#!/usr/bin/env python

import datetime
import logging
import cPickle
log = logging.getLogger('wrangler')

from wrangler import *
from wrangler.db.core import *
from wrangler.db.session import Session

__all__ = ['next_task',
           'update_job',
           'queue_job',
           'update_metrics',
           'create_task_log',
           'update_task_log']

def next_task():
    """Return the next task in the queue."""
    log.debug('Requesting next task from database.')
    db = Session()
    task = db.query(Task).filter(Task.status==Task.WAITING).order_by(desc(Task.priority)).first()
    if task:
        taskid = task.id
        task.status = Task.RUNNING
        db.commit()
        log.debug('Task %d was receieved from database.' % taskid)
    else:
        taskid = -1
        log.debug('No task found. The Queue is empty.')
    db.close()
    return taskid

def update_job(job):
    db = Session()
    db.add(job)
    status_list = []
    for task in job.tasks:
        status_list.append(task.status)
    if task.ERROR in status_list:
        job.status = job.ERROR
    elif all(map(lambda x: x==task.FINISHED, status_list)):
        job.status = job.FINISHED
    elif any(map(lambda x: x==task.RUNNING, status_list)):
        job.status = job.RUNNING
    status = job.status
    db.commit()
    db.close()
    return status

def queue_job(job):
    db = Session()
    db.add(job)
    log.debug('Adding job "%s" to queue.' % job.name)
    job.status = Job.WAITING
    for task in job.tasks:
        task.status = task.WAITING
    db.commit()
    jobid = job.id
    log.debug('Added job "%s" to queue. [%d]' % (job.name, job.id))
    db.close()
    return jobid

def create_task_log(task, cattle):
    db = Session()
    db.add(task)
    db.add(cattle)
    task_log = TaskLog(task, cattle)
    db.add(task_log)
    db.commit()
    log.debug('Create run log for task %d' % task.id)
    db.expunge(task_log)
    db.close()
    return task_log

def update_task_log(task_log, returncode, delta_time, stdout, stderr):
    db = Session()
    db.add(task_log)
    task_log.time = delta_time
    task_log.returncode = returncode
    task_log._log_stdout(stdout)
    task_log._log_stderr(stderr)
    task = task_log.task
    if task_log.returncode == 0:
        task.status = Task.FINISHED
        log.debug('Finished task %d' % task.id)
    else:
        task.status = Task.ERROR
        log.debug('Task %d errored out.' % task.id)
    job = task.job
    db.commit()
    db.expunge(task)
    db.expunge(job)
    db.close()
    update_job(job)

def update_metrics(hostname, data):
    db = Session()
    cattle = db.query(Cattle).filter(Cattle.hostname == hostname).first()
    time = datetime.datetime.now()
    load_avg = data['load_avg']
    cattle.running = data['running']
    metrics = CattleMetrics(cattle.id, time, load_avg)
    db.add(metrics)
    db.commit()
    db.close()
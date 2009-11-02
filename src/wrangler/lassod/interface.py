#!/usr/bin/env python

import logging
log = logging.getLogger('wrangler.lasso')

import wrangler.db.interface as db
import wrangler.generators as generator
from wrangler import *
from wrangler.db.session import Session
from wrangler.cattled.client import CattleClient

_api_ = ['cattle_sleep',
         'cattle_wake',
         'cattle_state',
         'job_stop',
         'job_pause',
         'job_queue',
         'task_kill',
         'task_stop',
         'task_queue',
         'task_pause',
         'lasso_submit_job']

def cattle_sleep(lassod, *hostnames):
    output = []
    for host in hostnames:
        client = CattleClient(host)
        output.append(client.sleep())
    return output


def cattle_wake(lassod, *hostnames):
    output = []
    for host in hostnames:
        client = CattleClient(host)
        output.append(client.wake_up())
    return output

def cattle_state(lassod, *hostnames):
    output = []
    for host in hostnames:
        client = CattleClient(host)
        output.append(client.state())
    return output

def cattle_dump(lassod, *hostnames):pass

def cattle_configure(lassod, *hostnames):pass

def _job_update(job):
    status_list = []
    for task in job.tasks:
        status_list.append(task.status)
    if task.ERROR in status_list:
        job.status = job.ERROR
    elif all(map(lambda x: x==task.FINISHED, status_list)):
        job.status = job.FINISHED
        if not job.finished:
            job.finished = datetime.datetime.now()
    elif any(map(lambda x: x==task.RUNNING, status_list)):
        job.status = job.RUNNING
        if not job.started:
            job.started = datetime.datetime.now()
    return job.status

def job_stop(lassod, *ids):
    db = Session()
    output = list()
    for job in db.query(Job).filter(Job.id.in_(ids)):
        for task in job.tasks:
            task.status = task.STOPPED
        _job_update(job)
    lassod.queue_dirty = True
    db.commit()
    db.close()
    return True

def job_pause(lassod, *ids):
    db = Session()
    output = list()
    for job in db.query(Job).filter(Job.id.in_(ids)):
        for task in job.tasks:
            task.status = task.PAUSED
        _job_update(job)
    lassod.queue_dirty = True
    db.commit()
    db.close()
    return True

def job_queue(lassod, *ids):
    db = Session()
    output = list()
    for job in db.query(Job).filter(Job.id.in_(ids)):
        for task in job.tasks:
            task.status = task.WAITING
        _job_update(job)
    lassod.queue_dirty = True
    db.commit()
    db.close()
    return True

def lasso_configure(lassod):
    pass

def lasso_submit_job(lassod, job_data):
    """Add job to the queue and return the job's id number."""
    gen = job_data.pop('generator')
    job = generator.__dict__[gen](**job_data)
    db = Session()
    db.add(job)
    log.debug('Adding job "%s" to queue.' % job.name)
    job.status = Job.WAITING
    for task in job.tasks:
        task.status = task.WAITING
    db.commit()
    jobid = job.id
    log.debug('Added job "%s" to queue. [%d]' % (job.name, job.id))
    lassod.queue_dirty = True
    db.close()
    return jobid

def task_kill(lassod, *ids):
    "Kill task by id number."
    db = Session()
    output = list()
    tasks = db.query(Task).filter(Task.id.in_(ids)).all()
    for task in tasks:
        if task.running:
            cattle = db.query(Cattle).filter(Cattle.id==task.running).first()
            client = CattleClient(cattle.hostname)
            client.kill_task(task.id)
            output.append(True)
        else:
            output.append(False)
    db.close()
    return True

def task_stop(lassod, *ids):
    db = Session()
    output = []
    tasks = db.query(Task).filter(Task.id.in_(ids)).all()
    for task in tasks:
        task.status = Task.STOPPED
        output.append(task.status)
        _job_update(task.job)
    lassod.queue_dirty = True
    db.commit()
    db.close()
    return output

def task_queue(lassod, *ids):
    db = Session()
    output = list()
    tasks = db.query(Task).filter(Task.id.in_(ids)).all()
    for task in tasks:
        task.status = Task.WAITING
        output.append(task.status)
        _job_update(task.job)
    lassod.queue_dirty = True
    db.commit()
    db.close()
    return output

def task_pause(lassod, *ids):
    db = Session()
    output = list()
    tasks = db.query(Task).filter(Task.id.in_(ids)).all()
    for task in tasks:
        task.status = Task.PAUSED
        output.append(task.status)
        _job_update(task.job)
    lassod.queue_dirty = True
    db.commit()
    db.close()
    return output

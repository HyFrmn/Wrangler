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
         'job_rename',
         'job_priority',
         'job_adjust_priority',
         'task_kill',
         'task_stop',
         'task_queue',
         'task_pause',
         'task_priority',
         'lasso_submit_job',
         'help',
         'help_task',
         'help_cattle',
         'help_job',
         'help_lasso']

def cattle_sleep(lassod, *hostnames):
    """Put specified cattle to sleep."""
    output = []
    for host in hostnames:
        client = CattleClient(host)
        output.append(client.sleep())
    return output


def cattle_wake(lassod, *hostnames):
    """Wake up specified cattle."""
    output = []
    for host in hostnames:
        client = CattleClient(host)
        output.append(client.wake_up())
    return output

def cattle_state(lassod, *hostnames):
    """Get the state of specified cattle."""
    output = []
    for host in hostnames:
        client = CattleClient(host)
        output.append(client.state())
    return output

def cattle_dump(lassod, *hostnames):
    """Kill ALL tasks currently running on specified cattle."""


def cattle_configure(lassod, *hostnames):
    """Reconfiugre specified cattle."""

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
    """Stop the specifed job, and currently running tasks of job. Mark all unfinished
    tasks as stopped."""
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
    """Pause all unfinished tasks associated with specifed jobs."""
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
    """Queue all unfinished tasks associated with specified jobs."""
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

def job_rename(lassod, id, name):
    """Rename specified job."""

def job_priority(lassod, id, priority):
    """Change the priority of all tasks associated with job."""

def job_adjust_priority(lassod, id, adjustment):
    """Adjust the priority of all task associated with job."""

def lasso_configure(lassod):
    """Reconfigure lasso daemon."""

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
    """Kill task by id number."""
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
    """Stop specified tasks. (Kill task if currently running)"""
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
    """Queue specifed tasks."""
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
    """Pause specified tasks."""
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

def task_priority(lassod, *ids):
    """Set the priority of the specified tasks."""

def help(item=None):
    output = ''
    if item:
        funcs = [globals()[func] for func in _api_ if not func.startswith(str(item))]
    else:
        funcs = _api_
    for func in funcs:
        output += str(func.__name__) + '\n'
        output += '=' * 32 + '\n'
        output += str(func.__doc__) + '\n'
        output += '\n' * 3
    return output

def help_task():
    return help('task')

def help_job():
    return help('job')

def help_cattle():
    return help('cattle')

def help_lasso():
    return help('lasso')
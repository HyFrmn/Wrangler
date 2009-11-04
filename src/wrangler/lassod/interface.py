#!/usr/bin/env python

import re
import datetime
import logging
log = logging.getLogger('wrangler.lasso')

import wrangler.db.interface as db
import wrangler.generators as generator
from wrangler import *
from wrangler.db.core import *
from wrangler.db.session import Session
from wrangler.cattled.client import CattleClient

_api_ = ['cattle_sleep',
         'cattle_wake',
         'cattle_state',
         'cattle_status',
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
    """Put the specified cattle to sleep. Return cattle state as a list."""
    output = []
    for host in hostnames:
        client = CattleClient(host)
        output.append(client.sleep())
    return output


def cattle_wake(lassod, *hostnames):
    """Wake up specified cattle. Return cattle state as a list."""
    output = []
    for host in hostnames:
        client = CattleClient(host)
        output.append(client.wake())
    return output

def cattle_state(lassod, *hostnames):
    """Get the state of specified cattle. Return cattle state as a list."""
    output = []
    for host in hostnames:
        client = CattleClient(host)
        output.append(client.state())
    return output

def cattle_status(lassod, *hostnames):
    """Get the status of the specified cattle. Return cattle state as a list of
    dictionaries containing a runtime report of cattle."""
    db = Session()
    output = []
    cattles = db.query(Cattle).filter(Cattle.hostname.in_(hostnames)).all()
    for cattle in cattles:
        metric = db.query(CattleMetrics).filter(CattleMetrics.cattle_id==cattle.id)
        metric = metric.order_by(desc(CattleMetrics.time)).first()
        report = dict()
        for key in CattleMetrics.keys:
            attr = getattr(metric, key)
            if attr is not None:
                if key == 'running':
                    report[key] = [int(task.id) for task in attr]
                else:
                    report[key] = str(attr)
        output.append(report)
    db.close()
    return output

def cattle_dump(lassod, *hostnames):
    """Kill ALL tasks currently running on specified cattle. Return a list of 
    lists containing task id of tasks that were killed."""


def cattle_configure(lassod, *hostnames):
    """Reconfigure specified cattle. Return a list of hostnames."""
    return hostnames

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
    """Stop the speciefed job, and currently running tasks of job. Mark all unfinished
    tasks as stopped. Return a list of killed tasks."""
    db = Session()
    tasks = list()
    output = []
    for job in db.query(Job).filter(Job.id.in_(ids)):
        for task in job.tasks:
            if task.status == task.WAITING or task.status == task.QUEUED:
                task.status = task.STOPPED
                print task.id, 'has been set to stop.'
            if task.status == task.RUNNING:
                cattle_id = task.running
                cattle = db.query(Cattle).filter(Cattle.id==cattle_id).first()
                client = CattleClient(cattle.hostname)
                if client.kill_task(task.id):
                    output.append(task.id)
                    print task.id, 'has been killed.'
        _job_update(job)
    lassod.queue_dirty = True
    db.commit()
    db.close()
    return output

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
    """Queue all unfinished tasks associated with specified jobs. Return a list 
    of tasks that are waiting."""
    lassod.normalize_queue()
    db = Session()
    output = list()
    for job in db.query(Job).filter(Job.id.in_(ids)):
        for task in job.tasks:
            if task.status == task.PAUSED and task.status == task.STOPPED:
                task.status = task.WAITING
                output.append(task.id)
        _job_update(job)
    lassod.queue_dirty = True
    lassod.update_queue()
    db.commit()
    db.close()
    return output

def job_rename(lassod, id, name):
    """Rename specified job."""
    db = Session()
    job = db.query(Job).filter(Job.id==id).first()
    if job:
        job.name = name
        db.commit()
        db.close()
        return True
    else:
        db.close()
        return False

def job_priority(lassod, id, priority):
    """Change the priority of all tasks associated with job."""
    db = Session()
    job = db.query(Job).filter(Job.id==id).first()
    if job:
        for task in job.tasks:
            task.priority = priority
        db.commit()
        db.close()
        return True
    else:
        db.close()
        return False

def job_adjust_priority(lassod, id, adjustment):
    """Adjust the priority of all task associated with job."""
    db = Session()
    job = db.query(Job).filter(Job.id==id).first()
    if job:
        for task in job.tasks:
            task.priority += adjustment
            if task.priority > 800:
                task.priority = 800
            elif task.priority < 200:
                task.priority = 200
        db.commit()
        db.close()
        return True
    else:
        db.close()
        return False

def lasso_configure(lassod):
    """Reconfigure lasso daemon."""
    return False

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
    return output

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
        if task.status == task.STOPPED or task.status == task.PAUSED:
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
        if task.status == task.WAITING or task.status == task.QUEUED:
            task.status = Task.PAUSED
        output.append(task.status)
        _job_update(task.job)
    lassod.queue_dirty = True
    db.commit()
    db.close()
    return output

def task_priority(lassod, *ids):
    """Set the priority of the specified tasks."""
    return False

def help(lassod, regex=None):
    output = ''
    if regex:
        regex = re.compile(regex)
        funcs = [globals()[func] for func in _api_ if regex.match(func)]
    else:
        funcs = [globals()[func] for func in _api_]
    for func in funcs:
        output += str(func.__name__) + '\n'
        output += '=' * 32 + '\n'
        output += str(func.__doc__) + '\n'
        output += '\n' * 3
    return output

def help_task(lassod):
    return help(lassod, 'task')

def help_job(lassod):
    return help(lassod, 'job')

def help_cattle(lassod):
    return help(lassod, 'cattle')

def help_lasso(lassod):
    return help(lassod, 'lasso')
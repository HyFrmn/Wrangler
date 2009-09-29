#!/usr/bin/env python

from wrangler.db.session import Session

__all__ = ['next_task',
           'update_job']

def next_task():pass

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
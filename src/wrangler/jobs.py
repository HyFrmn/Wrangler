#!/usr/bin/env python

import os
import simplejson

from wrangler.job import Job
from wrangler.task import Task

def RenderJob(name='No Name',
              command = 'printf "Frame: %4s %s\n" $WRANGLER_FRAME $WRANGLER_PADFRAME',
              start=1,
              end=100,
              step=1,
              padding=4,
              priority=500,
              env=None):
    if not env:
        env = {}
    env.update(os.environ)
    job = Job(name, env=env)
    for i in range(start, end + 1, step):
        task = Task(command)
        task.env.update(env)
        task.env['WRANGLER_PADFRAME'] = str(i).zfill(padding)
        task.env['WRANGLER_FRAME'] = i
        task.priority = priority
        job.tasks.append(task)
    job.status = job.WAITING
    return job

def main():
    job = RenderJob()
    json = job.dump()
    #print json
    obj = Job.Load(json)
    print type(obj)

if __name__ == '__main__':
    main()
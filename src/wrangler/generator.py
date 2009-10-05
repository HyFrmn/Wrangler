#!/usr/bin/env python

import os
import simplejson

from wrangler.job import Job
from wrangler.task import Task
from wrangler.config import config_base


def RenderJob(name='No Name',
              command = 'printf "Frame: %4s %s\n" $WRANGLER_FRAME $WRANGLER_PADFRAME',
              start=1,
              end=100,
              step=1,
              padding=4,
              priority=500,
              env=None,
              owner=None):

    config = config_base()

    if not env:
        env = {}
    if not owner:
        owner = os.environ['USER']
    env.update(os.environ)
    env_mask = config.get('jobs', 'env-mask').split(':')
    for mask in env_mask:
        try:
            del env[mask]
        except KeyError:
            pass
    job = Job(name, env=env)
    job.owner = owner
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
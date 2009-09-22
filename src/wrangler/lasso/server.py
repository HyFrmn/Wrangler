#!/usr/bin/env python

import sys
import cPickle
import thread
import traceback
from random import randint

from sqlalchemy import desc

from wrangler import *
from wrangler.db import Session
from wrangler.jobs import RenderJob
from wrangler.config import config_lasso
from wrangler.network import WranglerServer



config = config_lasso()

class LassoServer(WranglerServer):
    def _setup(self):
        WranglerServer._setup(self)

        #Populate Queue
#        for i in range(1, 20):
#            priority = randint(200, 800)
#            job = RenderJob('Job %d' % priority, priority=priority, command='echo $WRANGLER_FRAME; sleep 1')
#            self.queue_job(cPickle.dumps(job))

        #Initialize
        self.stable = dict()
        self.next_task_lock = thread.allocate_lock()

        #Register API Functions
        self.server.register_function(self.next_task, "next_task")
        self.server.register_function(self.queue_job, "queue_job")
        self.server.register_function(self.update_metrics, "update_metrics")
        self.server.register_function(self.connect_cattle, "connect_cattle")

    def connect_cattle(self, hostname):
        db = Session()
        found = db.query(Cattle).filter(Cattle.hostname==hostname).first()
        if found:
            cattle = found
        else:
            db.add(cattle)
        cattle.enabled = True
        db.commit()
        db.close()
        self.debug('%s was added to the heard.' % hostname)
        return hostname

    def disconnect_cattle(self, hostname):
        pass

    def next_task(self):
        """Return the next task in the queue."""
        self.debug('Requesting next task from database.')
        self.next_task_lock.acquire()
        db = Session()
        task = db.query(Task).filter(Task.status==Task.WAITING).order_by(desc(Task.priority)).first()
        if task:
            taskid = task.id
            task.status = Task.RUNNING
            db.commit()
            self.debug('Task %d was receieved from database.' % taskid)
        else:
            taskid = None
            self.debug('No task found. The Queue is empty.')
        db.close()
        self.next_task_lock.release()
        return cPickle.dumps(taskid)

    def queue_job(self, job):
        """ Add job to the queue and return the job's id number."""
        job = cPickle.loads(job)
        job.status = Job.WAITING
        for task in job.tasks:
            task.status = task.WAITING
        self.debug('Adding job "%s" to queue.' % job.name)
        db = Session()
        db.add(job)
        db.commit()
        jobid = job.id
        db.commit()
        self.debug('Added job %s to queue with priority %d. [%d]' % (job.name, job.priority, job.id))
        db.close()
        return jobid

    def update_metrics(self, hostname, data):
        db = Session()
        cattle = db.query(Cattle).filter(Cattle.hostname == hostname).first()
        time = data['time']
        load_avg = data['load_avg']
        metrics = CattleMetrics(cattle.id, time, load_avg)
        db.add(metrics)
        db.commit()
        db.close()
        return 0
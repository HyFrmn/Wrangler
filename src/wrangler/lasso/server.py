#!/usr/bin/env python

import sys
import cPickle
import thread
import traceback
from random import randint

from sqlalchemy import desc

import wrangler.db.interface as db
from wrangler import *
from wrangler.db.session import Session
from wrangler.jobs import RenderJob
from wrangler.config import config_lasso
from wrangler.network import WranglerServer



config = config_lasso()

class LassoServer(WranglerServer):
    def _setup(self):
        WranglerServer._setup(self)

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
        self.debug('Requesting next task from lasso.')
        self.next_task_lock.acquire()
        taskid = db.next_task()
        self.next_task_lock.release()
        return cPickle.dumps(taskid)

    def queue_job(self, job):
        """ Add job to the queue and return the job's id number."""
        job = cPickle.loads(job)
        jobid = db.queue_job(job)
        return jobid

    def update_metrics(self, hostname, data):
        db = Session()
        cattle = db.query(Cattle).filter(Cattle.hostname == hostname).first()
        time = data['time']
        load_avg = data['load_avg']
        cattle.running = data['running']
        metrics = CattleMetrics(cattle.id, time, load_avg)
        db.add(metrics)
        db.commit()
        db.close()
        return 0
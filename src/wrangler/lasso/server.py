#!/usr/bin/env python

import sys
import cPickle
import thread
import traceback
import datetime
import threading
from random import randint

from sqlalchemy import desc

import wrangler.db.interface as db
from wrangler import *
from wrangler.db.session import Session
from wrangler.jobs import RenderJob
from wrangler.config import config_lasso
from wrangler.network import WranglerServer
import wrangler.generator as generator 


config = config_lasso()

class CattleRuntime(object):
    """Holds runtime information about cattle."""
    def __init__(self):
        self.started = datetime.datetime.now()
        self.tasks = {}
        self.pulse()

    def pulse(self):
        self.last_pulse = datetime.datetime.now()
        return self.last_pulse

    def add_task(self, taskid, pid):
        self.tasks[taskid] = pid

    def rm_task(self, taskid):
        del self.tasks[taskid]

class LassoServer(WranglerServer):
    def __init__(self):
        config = config_lasso()
        hostname = config.get('lasso', 'hostname')
        port = config.getint('lasso', 'port')
        WranglerServer.__init__(self, hostname, port, 'wrangler.lasso')

        #Initialize
        self.heard = dict()
        self.queue_dirty = True
        self.next_task_lock = thread.allocate_lock()

    def configure(self):
        self.config = config_lasso()

    def _setup(self):
        WranglerServer._setup(self)
        self._register_timeout('update-queue', 20.0)
        self._register_timeout('thread-count', 5.0)

        #Register API Functions
        self.server.register_function(self.next_task, "next_task")
        self.server.register_function(self.queue_job, "queue_job")
        self.server.register_function(self.pulse, "pulse")


    def pulse(self, hostname):
        if hostname not in self.heard.keys():
            #Cattle is not connected.
            self.heard[hostname] = CattleRuntime()
        return self.heard[hostname].pulse()


    def next_task(self):
        """Return the next task in the queue."""
        self.debug('Requesting next task from lasso.')
        self.next_task_lock.acquire()
        taskid = db.next_task()
        self.next_task_lock.release()
        return taskid

    def queue_job(self, job_data):
        """Add job to the queue and return the job's id number."""
        gen = job_data.pop('generator')
        job = generator.__dict__[gen](**job_data)
        jobid = db.queue_job(job)
        self.queue_dirty = True
        return jobid

    def _handle_main(self):
        if self._timeout('update-queue'):
            self.queue_dirty = True
        if self.queue_dirty:
            db.update_queue()
            self.queue_dirty = False
        if self._timeout('thread-count'):
            print threading.activeCount()
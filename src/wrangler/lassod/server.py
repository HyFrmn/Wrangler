#!/usr/bin/env python

import sys
import cPickle
import thread
import traceback
import datetime
import threading
from random import randint

from sqlalchemy import desc

import wrangler.generators as generator
import wrangler.db.interface as db
import wrangler.lassod.interface
from wrangler import *
from wrangler.db.session import Session
from wrangler.queue import *
from wrangler.config import config_lasso
from wrangler.network import WranglerServer
from wrangler.cattled.client import CattleClient


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
        self.queue = PriorityQueue()

    def configure(self):
        self.config = config_lasso()

    def _setup(self):
        WranglerServer._setup(self)
        self._register_timeout('update-queue', 20.0)

        #Register API Functions
        self.server.register_function(self.next_task, "next_task")
        self.server.register_function(self.pulse, "pulse")

        #Register Interface Functions
        for func_name in wrangler.lassod.interface._api_:
            func = wrangler.lassod.interface.__dict__[func_name]
            if callable(func):
                self.server.register_function(self._decorate_interface(func), func_name)

        self.normalize_queue()

    def pulse(self, hostname):
        if hostname not in self.heard.keys():
            #Cattle is not connected.
            self.heard[hostname] = CattleRuntime()
        return self.heard[hostname].pulse()

    def next_task(self, hostname):
        """Return the next task (id) in the queue."""
        self.debug('Requesting next task from lasso.')
        self.next_task_lock.acquire()
        taskid = self.queue.next_task()
        self.next_task_lock.release()
        return taskid

    def normalize_queue(self):
        self.debug("Normalizing queue.")
        self.next_task_lock.acquire()
        db = Session()
        tasks = db.query(Task).filter(Task.status==Task.QUEUED).all()
        for task in tasks:
            task.status = Task.WAITING
        db.commit()
        db.close()
        self.next_task_lock.release()

    def update_queue(self):
        self.debug("Updating queue.")
        self.next_task_lock.acquire()
        db = Session()
        tasks = db.query(Task).filter(Task.status==Task.WAITING).order_by(desc(Task.priority)).limit(100)
        for task in tasks:
            if task.status == task.WAITING:
                if task.parent:
                    if task.parent.status != task.FINISHED:
                        return
                task.status = task.QUEUED
                self.queue.queue_task(task.id, task.priority + task.adjustment)
        db.commit()
        db.close()
        self.next_task_lock.release()

    def _decorate_interface(self, func):
        def decorated(*args):
            return func(self, *args)
        return decorated

    def _handle_main(self):
        if self._timeout('update-queue'):
            self.queue_dirty = True
        if self.queue_dirty:
            self.update_queue()
            self.queue_dirty = False
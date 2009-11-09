#!/usr/bin/env python

import sys
import cPickle
import thread
import logging
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
log = logging.getLogger('wrangler.lasso')

class CattleRuntime(object):
    """Holds runtime information about cattle."""
    def __init__(self, hostname):
        self.hostname = hostname
        self.started = datetime.datetime.now()
        self.tasks = {}
        self.pulse()

    def pulse(self):
        self.last_pulse = datetime.datetime.now()
        log.debug('Received pulse from %s.' % self.hostname)
        return self.last_pulse

    def add_task(self, taskid, pid):
        self.tasks[taskid] = pid

    def rm_task(self, taskid):
        del self.tasks[taskid]

class LassoServer(WranglerServer):
    def __init__(self):
        #Get configuration 
        config = config_lasso()
        hostname = config.get('lasso', 'hostname')
        port = config.getint('lasso', 'port')
        WranglerServer.__init__(self, hostname, port, 'wrangler.lasso')

        #Setup Code Objects
        self.decorate_task_object()

        #Clean Up Database
        db = Session()
        tasks = db.query(Task).filter(Task.status==Task.QUEUED).all()
        for task in tasks:
            task.status = task.WAITING
        db.commit()
        db.close()

        #Initialize
        self.heard = dict()
        self.next_task_lock = thread.allocate_lock()
        self.queue = PriorityQueue()

    def decorate_task_object(self):
        """Decorate task object to interface with lasso daemon."""
        
        def add_queue(task):
            self.next_task_lock.acquire()
            self.info("Adding %d to queue." % task.id)
            self.queue.add(task.id, task.priority + task.adjustment)
            task.status = task.QUEUED
            self.next_task_lock.release()
        Task._add_queue = add_queue

        def update_queue(task):
            self.next_task_lock.acquire()
            self.info("Updating %d priority in queue." % task.id)
            if self.queue.remove(task.id):
                self.queue.add(task.id, task.priority + task.adjustment)
            self.next_task_lock.release()
        Task._update_queue = update_queue
        
        def remove_queue(task):
            self.next_task_lock.acquire()
            self.info("Removing %d from queue." % task.id)
            self.queue.remove(task.id)
            self.next_task_lock.release()
        Task._remove_queue = remove_queue

        def kill_hook(task):
            self.info("Stopped task %d." % task.id)
            self.queue.remove(task.id)
            if task.status == task.RUNNING:
                cattle_id = task.running
                cattle = db.query(Cattle).filter(Cattle.id==cattle_id).first()
                client = CattleClient(cattle.hostname)
                if client.kill_task(task.id):
                    output.append(task.id)
                    print task.id, 'has been killed.'
        Task._kill_hook = kill_hook

        def pause_hook(task):
            self.info("Paused task %d." % task.id)
            self.queue.remove(task.id)
        Task._pause_hook = pause_hook

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


    def pulse(self, hostname):
        if hostname not in self.heard.keys():
            #Cattle is not connected.
            self.heard[hostname] = CattleRuntime(hostname)
        return self.heard[hostname].pulse()

    def next_task(self, hostname):
        """Return the next task (id) in the queue."""
        self.next_task_lock.acquire()
        task_id = self.queue.next()
        self.next_task_lock.release()
        self.info("Sending task %d to %s." % (task_id, hostname))
        return task_id

    def _decorate_interface(self, func):
        def decorated(*args):
            return func(self, *args)
        decorated.__doc__ = func.__doc__
        return decorated
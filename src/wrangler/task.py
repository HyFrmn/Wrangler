#!/usr/bin/env python

import os
import sys
import time
import subprocess

from sqlalchemy.types import TypeDecorator

from wrangler.db.core import *

class Task(Base):
    __tablename__ = 'tasks'

    # Status Constant 
    ERROR = -3
    STOPPED = -2
    PAUSED = -1
    WAITING = 0
    QUEUED = 1
    RUNNING = 2
    FINISHED = 3

    # Table Fields
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    priority = Column(Integer, default=500)
    adjustment = Column(Integer, default=0)
    command = Column(String(1024))
    env = Column(DictionaryDecorator(32768), default={})
    meta = Column(DictionaryDecorator(16384), default={})
    parent  = Column(Integer, ForeignKey('tasks.id'))
    status = Column(Integer, default=-1)
    run_count = Column(Integer)
    running = Column(Integer, ForeignKey('cattles.id'))

    # Relations 
    job = relation("Job", lazy=False)
    logs = relation('TaskLog', backref='task')

    def __init__(self, command='', priority=500):
        self.command = command
        self.priority = priority
        self.env = dict()
        self.meta = dict()
        self.run_count = 0
        self.running = 0
        
        self.add_probe('memory')
        self.add_probe('pcpu')

    def _add_queue(self):pass

    def _update_queue(self):pass
    
    def _remove_queue(self):pass

    def _stop_hook(self):pass

    def _kill_hook(self):pass

    def _pause_hook(self):pass

    def queue(self, force=False):
        change = False
        if self.status in [self.STOPPED, self.WAITING, self.PAUSED]:
            change = True
        elif (self.status == self.ERROR or self.status == self.FINISHED) and force:
            change = True
        if change:
            self.status = self.WAITING
            self._add_queue()
            return True
        return False

    def stop(self, force=False):
        change = False
        if self.status in [self.WAITING, self.QUEUED, self.PAUSED]:
            change = True
        elif force:
            change = True
        if change:
            if self.status == self.RUNNING:
                self.kill()
            self._remove_queue()
            self.status = self.STOPPED
            self._stop_hook()
            return True
        return False

    def pause(self, force=False):
        change = False
        if self.status in [self.WAITING, self.QUEUED, self.PAUSED]:
            change = True
        elif force:
            change = True
        if change:
            self.status = self.PAUSED
            self._remove_queue()
            self._pause_hook()
            return True
        return False

    def kill(self):
        self._kill_hook()

    def set_priority(self, priority):
        self.priority = int(priority)
        self._update_queue()

    def set_adjustment(self, adjustment):
        self.adjustment = int(adjustment)
        self._update_queue()

    def add_probe(self, probe):
        try:
            probe_list = self.meta['probes']
        except:
            probe_list = list()
        probe_list.append(probe)
        self.meta['probes'] = probe_list
        return probe_list

    def remove_probe(self, probe):
        try:
            probe_list = self.meta['probes']
        except:
            return False
        try:
            probe_list.remove(probe) 
        except ValueError:
            return False
        self.meta['probes'] = probe_list
        return True

class TaskProbe(Base):
    __tablename__ = 'task_probes'

    # Table Fields
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('jobs.id'))
    cattle_id = Column(Integer, ForeignKey('cattles.id'))
    task_log_id = Column(Integer, ForeignKey('task_logs.id'))
    memory = Column(Integer)
    pcpu = Column(Float)
    pid = Column(Integer)
    time = Column(DateTime)
    probes = Column(DictionaryDecorator(16384))

def main():
    task = Task('echo $HOSTNAME')
    task.run()

if __name__ == '__main__':
    main()
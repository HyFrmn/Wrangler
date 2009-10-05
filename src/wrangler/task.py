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

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    priority = Column(Integer, default=500)
    command = Column(String(1024))
    env = Column(DictionaryDecorator(32768))
    limits = Column(DictionaryDecorator(16384), default={})
    parent  = Column(Integer, ForeignKey('tasks.id'))
    logs = relation('TaskLog', backref='task')
    status = Column(Integer, default=-1)
    job = relation("Job", lazy=False)

    running = False

    def __init__(self, command='', priority=500):
        self.command = command
        self.priority = priority
        self.env = dict()

    def run(self):
        environ = os.environ.copy()
        for k, v in self.env.iteritems():
            environ[k] = str(v)
        try:
            start_time = time.time()
            self.popen = subprocess.Popen(self.command,
                                     env=environ,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        except OSError:
            return

        running = True
        returncode = self.popen.wait()
        end_time = time.time()
        delta_time = end_time - start_time
        output = self.popen.stdout.read()
        error = self.popen.stderr.read()
        return (returncode, delta_time, output, error)

    def kill(self):
        if self.running:
            self.popen.kill()

def main():
    task = Task('echo $HOSTNAME')
    task.run()

if __name__ == '__main__':
    main()
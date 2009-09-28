#!/usr/bin/env python

import os
import sys
import time
import subprocess
import cPickle

from sqlalchemy.types import TypeDecorator

from wrangler.db.core import *

class EnvironmentDecorator(TypeDecorator):
    impl = String
    def process_bind_param(self, value, engine):
        assert isinstance(value, dict)
        return cPickle.dumps(value)

    def process_result_value(self, value, engine):
        return cPickle.loads(str(value))

    def copy(self):
        return EnvironmentDecorator(self.impl.length)

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
    env = Column(EnvironmentDecorator(32768))
    parent  = Column(Integer, ForeignKey('tasks.id'))
    logs = relation('TaskLog', backref='task')
    status = Column(Integer, default=-1)

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
            popen = subprocess.Popen(self.command,
                                     env=environ,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        except OSError:
            return
        returncode = popen.wait()
        end_time = time.time()
        delta_time = end_time - start_time
        output = popen.stdout.read()
        error = popen.stderr.read()
        return (returncode, delta_time, output, error)


def main():
    task = Task('echo $HOSTNAME')
    task.run()

if __name__ == '__main__':
    main()
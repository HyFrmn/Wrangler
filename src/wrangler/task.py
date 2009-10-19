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

    # Relations 
    job = relation("Job", lazy=False)
    logs = relation('TaskLog', backref='task')

    def __init__(self, command='', priority=500):
        self.command = command
        self.priority = priority
        self.env = dict()
        self.meta = dict()

def main():
    task = Task('echo $HOSTNAME')
    task.run()

if __name__ == '__main__':
    main()
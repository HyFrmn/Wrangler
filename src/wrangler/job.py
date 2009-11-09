#!/usr/bin/env python

import os
import pickle

from wrangler.db.core import *

class Job(Base):
    __tablename__ = 'jobs'

    # Table Fields
    id = Column(Integer, primary_key=True)
    name = Column(String(1024))
    owner = Column(String(128))
    status = Column(Integer, default=-1)
    created = Column(DateTime)
    started = Column(DateTime)
    finished = Column(DateTime)
    description = Column(String(2048))
    meta = Column(DictionaryDecorator(16384), default={})

    # Relations 
    tasks = relation("Task", lazy=False)

    # Status Constant 
    ERROR = -3
    STOPPED = -2
    PAUSED = -1
    WAITING = 0
    QUEUED = 1
    RUNNING = 2
    FINISHED = 3

    def __init__(self,
                 name = 'No Name',
                 env=None):
        self.name = name
        self.tasks = []
        self.owner = os.environ['USER']
        if env:
            self.env = env
        else:
            self.env = {}

    def queue(self):
        for task in self.tasks:
            task.queue()

    def pause(self):
        for task in self.tasks:
            task.pause()

    def stop(self):
        for task in self.tasks:
            task.stop()


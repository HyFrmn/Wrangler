#!/usr/bin/env python

import os
import pickle

from wrangler.db.core import *

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    name = Column(String(1024))
    owner = Column(String(128))
    status = Column(Integer, default=-1)
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

    def dump(self):
        def encode_queueable(obj):
            try:
                return obj.serialize()
            except AttributeError:
                return obj
        #return simplejson.dumps(self, default=encode_queueable, indent=1)
        return pickle.dumps(self)

    @staticmethod
    def Load(string):
        def decode_queueable(dct):
            print dct
            if dct.get('type', None) == 'Job':
                print 'Job object found'
                return Job().decode(dct)
            else:
                return dct
        return pickle.loads(string)
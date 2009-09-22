#!/usr/bin/env python

import pickle

from wrangler.queueable import Queueable

class Job(Queueable):
    def __init__(self,
                 name = 'No Name',
                 env=None):
        Queueable.__init__(self)
        self.name = name
        self.tasks = []
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
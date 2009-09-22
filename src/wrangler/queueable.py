#!/usr/bin/env pythong

class Queueable(object):
    ERROR = -3
    STOPPED = -2
    PAUSED = -1
    WAITING = 0
    QUEUED = 1
    RUNNING = 2
    FINISHED = 3

    def __init__(self):
        self.id = None
        self.status = self.PAUSED
        self.priority = 500
        self.env = {}
        self.type = self.__class__.__name__

    def serialize(self):
        data = {}
        for item in self.__dict__.keys():
            if not item.startswith('_'):
                data[item] = self.__dict__[item]
        #data['__type__'] = self.type
        return data

    def decode(self, dct):
        for k, v in dct.iteritems():
            if k.startswith('__'):
                continue
            self.__dict__[k] = v
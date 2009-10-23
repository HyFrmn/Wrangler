#!/usr/bin/env python

class WranglerQueueInterface(object):
    def queue_task(self, task, priority=500):
        raise NotImplementedError

    def next_task(self):
        raise NotImplementedError
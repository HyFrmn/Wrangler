#!/usr/bin/env python

import math
import bisect
import logging

from wrangler.queue.interface import WranglerQueueInterface

log = logging.getLogger('wrangler.lasso')

class PriorityQueue(WranglerQueueInterface):
    def __init__(self):
        self.queue = []

    def add(self, task, priority=500):
        if task in self.queue:
            return
        priority = max(0, priority)
        priority = min(1000, priority)
        bisect.insort(self.queue,(1000 - priority,task))


    def next(self):
        try:
            priority, task = self.queue.pop(0)
        except IndexError:
            return -1
        return task

    def remove(self, task):
        try:
            task = int(task)
            ids = [int(id) for priority, id in self.queue]
            index = ids.index(task)
            priority, id = self.queue.pop(index)
            return True
        except ValueError, msg:
            log.warning(msg)
            return False

    def list(self):
        return [id for priority, id in self.queue]
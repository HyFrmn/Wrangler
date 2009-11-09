#!/usr/bin/env python

from wrangler.queue.lifo import WranglerQueueInterface

class LIFOQueue(WranglerQueueInterface):
    def __init__(self):
        self.queue = []
    
    def queue_task(self, task, priority=500):
        self.queue.append(task)

    def next_task(self):
        try:
            task = self.queue.pop(-1)
        except IndexError:
            task = -1
        return task

    def remove_task(self, task):
        try:
            self.queue.remove(task)
            return True
        except ValueError:
            return False


    def list(self):
        return self.queue
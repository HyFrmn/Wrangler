#!/usr/bin/env python

import math
import heapq

from wrangler.queue.interface import WranglerQueueInterface

class PriorityQueue(WranglerQueueInterface):
    def __init__(self):
        self.heap = []

    def queue_task(self, task, priority=500):
        priority = max(0, priority)
        priority = min(1000, priority)
        heapq.heappush(self.heap, (1000 - priority, task))

    def next_task(self):
        try:
            priority, task = heapq.heappop(self.heap)
        except IndexError:
            return -1
        return task
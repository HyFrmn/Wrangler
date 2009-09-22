#!/usr/bin/env python

from wrangler.hardware import info

class Cattle(object):
    def __init__(self):
        self.hostname = info.hostname()
        self.memory = info.memory()
        self.system = info.system()
        self.processor = info.processor()
        self.ncpus = info.ncpu()
        self.load_avg = info.load_avg()
        self.enabled = False


class CattleMetrics(object):
    def __init__(self, hostid, time, load_avg, running_tasks=-1):
        self.hostid = hostid
        self.time = time
        self.load_avg = load_avg
        self.running_tasks = running_tasks
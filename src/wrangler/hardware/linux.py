#!/usr/bin/env python

from subprocess import Popen, PIPE

from wrangler.hardware.infointerface import InfoInterface

class LinuxInfo(InfoInterface):
    def memory(self):
        o = Popen(["grep", "MemTotal", "/proc/meminfo"], stdout=PIPE).communicate()[0]
        line = o.split('\n')[0]
        return float(line.split()[1]) / pow(1000, 2)
    
    def load_avg(self):
        o = Popen(["cat", "/proc/loadavg"], stdout=PIPE).communicate()[0]
        return float(o.split()[0:3][0])

    def ncpu(self):
        o = Popen(["grep", "processor", "/proc/cpuinfo"], stdout=PIPE).communicate()[0]
        return int(len(o.split('\n')) - 1)
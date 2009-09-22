#!/usr/bin/env python

from subprocess import Popen, PIPE

from wrangler.hardware.infointerface import InfoInterface

class OSXInfo(InfoInterface):
    def memory(self):
        o = Popen(["sysctl", "hw.memsize"], stdout=PIPE).communicate()[0]
        return float(o.split()[1]) / pow(1024, 3)
    
    def load_avg(self):
        o = Popen(["sysctl", "vm.loadavg"], stdout=PIPE).communicate()[0]
        return float(o.split()[2:5][0])

    def ncpu(self):
        o = Popen(["sysctl", "hw.ncpu"], stdout=PIPE).communicate()[0]
        return int(o.split()[1])
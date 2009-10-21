#!/usr/bin/env python

import os
import sys
import pwd
import time
from subprocess import Popen, PIPE

print sys.path

from wrangler.hardware import info
from wrangler.cattle.client import CattleClient

_timeout = time.time()
def timeout():
    global _timeout
    now = time.time()
    delta = now - _timeout
    if delta > 1.0:
        _timeout = now
        return True
    return False

#Probes
def cpu_usage(pid):
    o = Popen(["ps", "-p %d" % pid, "-o pcpu="], stdout=PIPE).communicate()[0]
    return float(o.split()[0])

def memory(pid):
    o = Popen(["ps", "-p %d" % pid, "-o rss="], stdout=PIPE).communicate()[0]
    return float(o.split()[0])

def monitor(command, uid, gid, stdout, stderr, probes=None):
    print 'Init.  User Id:', os.getuid()
    print 'Init. Group Id:', os.getuid()

    try:
        os.setgid(gid)
    except OSError:
        print "ERROR: Could not set group id."
        sys.exit(1)

    try:
        os.setuid(uid)
    except OSError:
        print "ERROR: Could not set user id."
        sys.exit(1)

    try:
        os.environ['USER'] = pwd.getpwuid(uid)[0]
    except KeyError:
        print "ERROR: Could not find %d in /etc/passwd" % uid
        sys.exit(1)

    print 'Run  User Id:', os.getuid()
    print 'Run Group Id:', os.getuid()
    print 'Running User:', os.environ['USER']

    proc = Popen(command, shell=True)
    while proc.poll() is None:
        if timeout():
            print memory(proc.pid)
            print cpu_usage(proc.pid)
    print "Process %d is complete" % proc.pid

def main():
    client = CattleClient()

if __name__ == '__main__':
    main()
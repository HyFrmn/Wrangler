#!/usr/bin/env python

import os
import sys
import pwd
import subprocess


def monitor(command, uid, gid, stdout, stderr, probes=None):
    print 'Init.  User Id:', os.getuid()
    print 'Init. Group Id:', os.getuid()

    os.setgid(gid)
    os.setuid(uid)
    os.environ['USER'] = pwd.getpwuid(uid)[0]


    print 'Run  User Id:', os.getuid()
    print 'Run Group Id:', os.getuid()
    print 'Running User:', os.environ['USER']

    proc = subprocess.Popen(command)
    while proc.poll() is None:
        print "Process %d is still running" % proc.pid
    print "Process %d is complete" % proc.pid

if __name__ == '__main__':
    monitor('dumb.sh', 1047, 1100, '/tmp/stdout_test.txt', '/tmp/stderr_test.txt')
#!/usr/bin/env python

import os
import sys
import pwd
import time
from subprocess import Popen, PIPE

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
    o = Popen("ps -p %d -o pcpu=" % pid, shell=True, stdout=PIPE).communicate()[0]
    return float(o.split()[0])

def memory(pid):
    o = Popen("ps -p %d -o rss=" % pid, shell=True, stdout=PIPE).communicate()[0]
    return float(o.split()[0])

class ProcessMonitor(object):
    def __init__(self, task_id):
        self.task_id = task_id
        self.client = CattleClient()
        self.connect()
        self.monitor()
        self.disconnect()

    def connect(self):
        task_data = self.client.monitor_connect(self.task_id)
        self.command = task_data['command']
        self.uid = task_data['uid']
        self.gid = task_data['gid']
        self.stdout_file_path = task_data['stdout_file_path']
        self.stderr_file_path = task_data['stderr_file_path']

    def disconnect(self):
        self.client.monitor_disconnect(self.task_id)

    def monitor(self):
        #Set uid
        try:
            os.setgid(self.gid)
        except OSError:
            print "ERROR: Could not set group id."
            sys.exit(1)

        #Set gid
        try:
            os.setuid(self.uid)
        except OSError:
            print "ERROR: Could not set user id."
            sys.exit(1)

        try:
            os.environ['USER'] = pwd.getpwuid(self.uid)[0]
        except KeyError:
            print "ERROR: Could not find %d in /etc/passwd" % uid
            sys.exit(1)

        stdout_fd = open(self.stdout_file_path, 'w')
        stderr_fd = open(self.stderr_file_path, 'w')

        proc = Popen(self.command, shell=True, stdout=stdout_fd, stderr=stderr_fd)
        while proc.poll() is None:
            if timeout():
                client.info(memory(proc.pid))
                client.info(cpu_usage(proc.pid))
        print "Process %d is complete" % proc.pid
        stdout_fd.close()
        stderr_fd.close()


def main():
    task_id = int(sys.argv[1])
    ProcessMonitor(task_id)

if __name__ == '__main__':
    main()
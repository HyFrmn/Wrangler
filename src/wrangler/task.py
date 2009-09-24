#!/usr/bin/env python

import os
import sys
import time
import subprocess
import cPickle

from wrangler.queueable import Queueable

class Task(Queueable):
    def __init__(self, command='', priority=500):
        Queueable.__init__(self)
        self.command = command
        self.priority = priority

    def run(self):
        environ = os.environ.copy()
        for k, v in self.env.iteritems():
            environ[k] = str(v)
        try:
            start_time = time.time()
            popen = subprocess.Popen(self.command,
                                     env=environ,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        except OSError:
            return
        returncode = popen.wait()
        end_time = time.time()
        delta_time = end_time - start_time
        output = popen.stdout.read()
        error = popen.stderr.read()
        return (returncode, delta_time, output, error)


def main():
    task = Task('echo $HOSTNAME')
    task.run()

if __name__ == '__main__':
    main()
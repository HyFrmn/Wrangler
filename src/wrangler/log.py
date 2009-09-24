#!/usr/bin/env python

import os

from wrangler.config import config_base

config = config_base()

class TaskLog(object):
    logdir = os.path.expandvars(config.get('logging', 'directory'))

    def __init__(self, task, returncode, time, stdout, stderr, cattle_id):
        self.task_id = task.id
        self.task = task
        self.time = time
        self.returncode = returncode
        self.cattle_id = cattle_id
        self._log_stdout(stdout)
        self._log_stderr(stderr)

    def _log_stdout(self, output):
        filepath = self._stdout_file_path()
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        fd = open(filepath, 'w')
        fd.write(output)
        fd.close()

    def _log_stderr(self, output):
        filepath = self._stderr_file_path()
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        fd = open(filepath, 'w')
        fd.write(output)
        fd.close()

    def _stdout_file_path(self):
        return os.path.join(self.logdir, str(self.task.job_id), str(self.task.id) + '_out.log')

    def _stderr_file_path(self):
        return os.path.join(self.logdir, str(self.task.job_id), str(self.task.id) + '_err.log')
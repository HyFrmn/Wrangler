#!/usr/bin/env python

import os


from wrangler.config import config_base
from wrangler.db.core import *

config = config_base()

class TaskLog(Base):
    __tablename__ = 'task_logs'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    time = Column(Float, default=-1)
    returncode = Column(Integer, default=2)
    cattle_id = Column(Integer, ForeignKey('cattles.id'))
    cattle = relation('Cattle', backref=backref('logs'))
    stdout = Column(String(256))
    stderr = Column(String(256))

    logdir = os.path.expandvars(config.get('logging', 'task-dir'))

    def __init__(self, task, cattle):
        self.task_id = task.id
        self.cattle_id = cattle.id
        self.stdout = self._stdout_file_path()
        self.stderr = self._stderr_file_path()

    def _stdout_file_path(self):
        return os.path.join(self.logdir, str(self.task_id) + '_out.log')

    def _stderr_file_path(self):
        return os.path.join(self.logdir, str(self.task_id) + '_err.log')
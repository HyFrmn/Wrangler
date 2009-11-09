#!/usr/bin/env python
import sys
import logging

from wrangler.log import TaskLog
from wrangler.job import Job
from wrangler.task import Task, TaskProbe
from wrangler.generators import RenderJob
from wrangler.cattled.interface import Cattle, CattleMetrics
import wrangler.db.core

__all__ = ['Job',
           'TaskLog',
           'Task',
           'TaskProbe',
           'RenderJob',
           'Cattle',
           'CattleMetrics']

log = logging.getLogger('wrangler')
log.propagate = False
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)
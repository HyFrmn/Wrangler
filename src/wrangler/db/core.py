#!/usr/bin/env python
import os
import cPickle as pickle


import sqlalchemy
from sqlalchemy import Table, Column, Integer, Float, String, MetaData
from sqlalchemy import ForeignKey, Boolean, create_engine, and_, select, func
from sqlalchemy.orm import mapper, sessionmaker, relation, backref, synonym, column_property
from sqlalchemy.types import TypeDecorator

from wrangler import *
from wrangler.config import config_base

metadata = MetaData()


class EnvironmentDecorator(TypeDecorator):
    impl = String
    def process_bind_param(self, value, engine):
        assert isinstance(value, dict)
        return pickle.dumps(value)

    def process_result_value(self, value, engine):
        return pickle.loads(str(value))

    def copy(self):
        return EnvironmentDecorator(self.impl.length)


jobs_table = Table('jobs', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('name', String(1024)),
                   Column('status', Integer),
                   Column('owner', String(128)),
)

task_table = Table('tasks', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('jobid', Integer, ForeignKey('jobs.id')),
                   Column('priority', Integer, default=500),
                   Column('command', String(1024)),
                   Column('status', Integer),
                   Column('env', EnvironmentDecorator(32768)),
                   Column('parent', Integer, ForeignKey('tasks.id'))
)

task_log_table = Table('task_logs', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('taskid', Integer, ForeignKey('tasks.id')),
                       Column('time', Float),
                       Column('returncode', Integer),
)

cattle_table = Table('cattle', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('hostname', String(32), unique=True),
                     Column('memory', Float),
                     Column('system', String(64)),
                     Column('processor', String(64)),
                     Column('ncpus', Integer),
                     Column('enabled', Boolean)
)

cattle_metrics_table = Table('cattle_metrics', metadata,
                             Column('id', Integer, primary_key=True),
                             Column('hostid', Integer, ForeignKey('cattle.id')),
                             Column('load_avg', Float),
                             Column('running_tasks', Integer),
                             Column('time', Float),
                             )

mapper(Job, jobs_table, 
       properties = {'tasks' : relation(Task, lazy=False),
                     'running' : column_property(select([func.count(task_table.c.id)],
                                        and_(jobs_table.c.id==task_table.c.jobid,
                                             task_table.c.status==Task.RUNNING)).label('running')),
                     'waiting' : column_property(select([func.count(task_table.c.id)],
                                        and_(jobs_table.c.id==task_table.c.jobid,
                                             task_table.c.status==Task.WAITING)).label('waiting')),
                     'paused' : column_property(select([func.count(task_table.c.id)],
                                        and_(jobs_table.c.id==task_table.c.jobid,
                                             task_table.c.status==Task.PAUSED)).label('paused')),
                     'finished' : column_property(select([func.count(task_table.c.id)],
                                        and_(jobs_table.c.id==task_table.c.jobid,
                                             task_table.c.status==Task.FINISHED)).label('finished'))})

mapper(Task, task_table, properties={'logs' : relation(TaskLog)})

mapper(TaskLog, task_log_table)

mapper(Cattle, cattle_table, properties={'metrics' : relation(CattleMetrics)})

mapper(CattleMetrics, cattle_metrics_table)

config = config_base()
engine_url = config.get('database', 'url')
engine_url = os.path.expandvars(engine_url)
engine = create_engine(engine_url, echo=False)
metadata.create_all(engine)
Session = sessionmaker(bind=engine)

__all__ = ['Session', ]

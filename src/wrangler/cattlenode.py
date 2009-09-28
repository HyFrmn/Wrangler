#!/usr/bin/env python

from wrangler.db.core import *
from wrangler.hardware import info

class Cattle(Base):
    # table name is end's with 's' to help Ruby on Rails integration.
    __tablename__ = 'cattles'
    
    id = Column(Integer, primary_key=True)
    hostname = Column(String(64))
    memory = Column(Float)
    system = Column(String(128))
    processor = Column(String(128))
    ncpus = Column(Integer)
    enabled = Column(Boolean)
    running = Column(Integer, default=0)
    metrics = relation("CattleMetrics")

    def __init__(self):
        self.hostname = info.hostname()
        self.memory = info.memory()
        self.system = info.system()
        self.processor = info.processor()
        self.ncpus = info.ncpu()
        self.load_avg = info.load_avg()
        self.enabled = False


class CattleMetrics(Base):
    __tablename__ = 'metrics'
    id = Column(Integer, primary_key=True)
    cattle_id = Column(Integer, ForeignKey('cattles.id'))
    load_avg = Column(Float)
    running = Column(Integer)
    time = Column(Float)

    def __init__(self, hostid, time, load_avg, running_tasks=-1):
        self.cattle_id = hostid
        self.time = time
        self.load_avg = load_avg
        self.running_tasks = running_tasks
#!/usr/bin/env python
import os
import simplejson as json


import sqlalchemy
from sqlalchemy import Table, Column, Integer, Float, String, MetaData, desc, DateTime
from sqlalchemy import ForeignKey, Boolean, create_engine, and_, select, func
from sqlalchemy.orm import mapper, sessionmaker, relation, backref, synonym, column_property
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
from wrangler import *


metadata = Base.metadata

__all__ = ['metadata',
           'Base',
           'Column',
           'Integer',
           'Float',
           'String',
           'ForeignKey',
           'Boolean',
           'relation',
           'backref',
           'column_property',
           'desc',
           'DateTime',
           'DictionaryDecorator']

class DictionaryDecorator(TypeDecorator):
    impl = String
    def process_bind_param(self, value, engine):
        assert isinstance(value, dict)
        return json.dumps(value)

    def process_result_value(self, value, engine):
        return json.loads(str(value))

    def copy(self):
        return DictionaryDecorator(self.impl.length)
#!/usr/bin/env python

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wrangler.config import config_base
from wrangler.db.core import metadata

config = config_base()
engine_url = config.get('database', 'url')
engine_url = os.path.expandvars(engine_url)
engine = create_engine(engine_url, echo=False)
metadata.create_all(engine)
Session = sessionmaker(bind=engine)

__all__ = ['Session',]
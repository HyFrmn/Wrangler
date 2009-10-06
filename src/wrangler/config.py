#!/usr/bin/env python

import os
import logging
import logging.handlers
import logging.config
import ConfigParser

from hardware import info

class ConfigureError(Exception):pass

def check_environment():
    home = os.environ.get('WRANGLER_HOME', None)
    if not home:
        raise ConfigureError, '$WRANGLER_HOME variable is not set.'
    if not os.path.exists(home):
        raise ConfigureError, '$WRANGLER_HOME [%s] does not exist.' % home
    farm_cfg = os.path.join(home, 'farm.cfg')
    if not os.path.exists(farm_cfg):
        raise ConfigurationError, "'farm.cfg' was not found in [%s]" % farm_cfg
    return home

home = check_environment()

def config_logging(home=home):
    #logging.config.fileConfig(os.path.join(home, 'farm.cfg'))
    log = logging.getLogger('wrangler')
    log.setLevel(logging.ERROR)
    
    config = config_base()
    log_dir = config.get('logging', 'server-dir')
    file_path = os.path.join(log_dir, info.hostname() + '.log')
    file_path = os.path.expandvars(file_path)
    handler = logging.FileHandler(file_path)
    log.addHandler(handler)
    return log

def config_base(home=home):
    config = ConfigParser.SafeConfigParser()
    config.read(os.path.join(home, 'farm.cfg'))
    return config

def config_lasso(home=home):
    config.read(os.path.join(home, 'lasso.cfg'))
    return config

def config_cattle(home=home):
    config = config_base()
    config.read(os.path.join(home, 'cattle.cfg'))
    return config

log = config_logging(home)
config = config_base(home)
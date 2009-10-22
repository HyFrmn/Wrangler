#!/usr/bin/env python

import os
import sys
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
    log = logging.getLogger('wrangler')
    log.propagate = False
    log.setLevel(logging.FATAL)
    config = config_base()
    log_dir = os.path.expandvars(config.get('logging', 'server-dir'))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    handler = logging.StreamHandler(sys.stdout)
    log.addHandler(handler)
    
    #Setup Cattle Log
    cattle_log = logging.getLogger('wrangler.cattle')
    cattle_log.setLevel(logging.INFO)
    cattle_log.propagate = False
    file_path = os.path.join(log_dir, info.hostname() + '.log')
    file_path = os.path.expandvars(file_path)
    handler = logging.FileHandler(file_path)
    cattle_log.addHandler(handler)
    
    #Setup Lasso Log
    lasso_log = logging.getLogger('wrangler.lasso')
    lasso_log.setLevel(logging.INFO)
    lasso_log.propagate = False
    file_path = os.path.join(log_dir, 'lasso.log')
    file_path = os.path.expandvars(file_path)
    handler = logging.FileHandler(file_path)
    lasso_log.addHandler(handler)
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
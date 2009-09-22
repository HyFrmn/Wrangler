#!/usr/bin/env python

import os
import logging
import ConfigParser

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

def config_logging():
    log = logging.getLogger('wrangler')
    return log

def config_base():
    config = ConfigParser.SafeConfigParser()
    config.read(os.path.join(WRANGLER_HOME, 'farm.cfg'))
    return config

def config_lasso():
    config.read(os.path.join(WRANGLER_HOME, 'lasso.cfg'))
    return config

def config_cattle():
    config = config_base()
    config.read(os.path.join(WRANGLER_HOME, 'cattle.cfg'))
    return config

log = config_logging()
WRANGLER_HOME = check_environment()
config = config_base()
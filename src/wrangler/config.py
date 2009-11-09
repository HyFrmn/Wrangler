#!/usr/bin/env python

import os
import sys
import logging
import logging.handlers
import logging.config
import ConfigParser

from hardware import info

_base_dir = os.path.dirname(__file__) 

log = logging.getLogger('wrangler')

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

def _load_config_file(config, file_path):
    log.debug('Loading config file "%s"' % file_path)
    config.read(file_path)
    return config

def config_base(home=home):
    default_cfg = os.path.join(_base_dir, 'defaults.cfg')
    config = _load_config_file(ConfigParser.SafeConfigParser(), default_cfg)
    farm_cfg = os.path.join(home, 'farm.cfg')
    _load_config_file(config, farm_cfg)
    return config

def config_lasso(home=home):
    lasso_cfg = os.path.join(home, 'lasso.cfg')
    _load_config_file(config_base(), lasso_cfg)
    return config

def config_cattle(home=home):
    cattle_cfg = os.path.join(home, 'cattle.cfg')
    _load_config_file(config_base(), cattle_cfg)
    return config

config = config_base()
log_dir = os.path.expandvars(config.get('logging', 'server-dir'))
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

#Setup Cattle Log
cattle_log = logging.getLogger('wrangler.cattle')
cattle_log.setLevel(logging.DEBUG)
file_path = os.path.join(log_dir, info.hostname() + '.log')
file_path = os.path.expandvars(file_path)
handler = logging.FileHandler(file_path)
handler.setFormatter(formatter)
cattle_log.addHandler(handler)

#Setup Lasso Log
lasso_log = logging.getLogger('wrangler.lasso')
lasso_log.setLevel(logging.DEBUG)
file_path = os.path.join(log_dir, 'lasso.log')
file_path = os.path.expandvars(file_path)
handler = logging.FileHandler(file_path)
handler.setFormatter(formatter)
lasso_log.addHandler(handler)

client_log = logging.getLogger('wrangler.client')
client_log.setLevel(logging.INFO)

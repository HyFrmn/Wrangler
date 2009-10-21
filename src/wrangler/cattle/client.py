#!/usr/bin/env python


import pickle

from wrangler.config import config_base
from wrangler.network import WranglerClient
from wrangler.hardware import info

class CattleClient(WranglerClient):
    def __init__(self):
        config = config_base()
        port = config.getint('cattle', 'port')
        hostname = info.hostname()
        WranglerClient.__init__(self, hostname, port)
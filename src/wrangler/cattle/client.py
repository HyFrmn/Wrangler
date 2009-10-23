#!/usr/bin/env python

from wrangler.config import config_base
from wrangler.network import WranglerClient
from wrangler.hardware import info

class CattleClient(WranglerClient):
    def __init__(self, hostname=None, port=None):
        config = config_base()
        if not port:
            port = config.getint('cattle', 'port')
        if not hostname:
            hostname = info.hostname()
        WranglerClient.__init__(self, hostname, port)
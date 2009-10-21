#!/usr/bin/env python

from wrangler.config import config_base
from wrangler.network import WranglerClient
from wrangler.hardware import info

class CattleClient(WranglerClient):
    def __init__(self):
        config = config_base()
        port = config.getint('cattle', 'port')
        hostname = info.hostname()
        print 'Connecting to %s:%d' % (hostname, port)
        WranglerClient.__init__(self, hostname, port)
#!/usr/bin/env python

import logging

from xmlrpclib import ServerProxy

from wrangler.config import config_base

log = logging.getLogger('wrangler.client')

class WranglerClient(object):
    def __init__(self, hostname=None, port=None):
        self.config = config_base()
        if not hostname:
            hostname = self.config.get('master', 'hostname')
        if not port:
            port = self.config.getint('master', 'port')
        log.debug('Starting client to %s:%d' % (hostname, port))
        self.client = ServerProxy('http://%s:%s' % (hostname, port), allow_none=True)
        

    def __getattr__(self, attr):
        func = getattr(self.client, attr)
        return func
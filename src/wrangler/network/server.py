#!/usr/bin/env python

import time
import socket
import select
import logging
import xmlrpclib

from thread import start_new_thread as start

from wrangler.config import config_base
from wrangler.network.asyncxmlrpcserver import AsyncXMLRPCServer
log = logging.getLogger('wrangler.server')

class WranglerServer(object):
    def __init__(self, host, port):
        self.config = config_base()
        self.hostname = host
        self.port = port
        self.server = None
        self.client = None
        self._timeouts = dict()

    #Logging Messages
    def log(self, level, msg):
        log.log(level, msg)
        return True
    
    def debug(self, msg):
        log.debug(msg)
        return True

    def info(self, msg):
        log.info(msg)
        return True
    
    def warning(self, msg):
        log.warning(msg)
        return True
    
    def error(self, msg):
        log.error(msg)
        return True

    def critical(self, msg):
        log.critical(msg)
        return True

    def _setup(self):
        self.server = AsyncXMLRPCServer((self.hostname, self.port), logRequests=False)
        self.info('Server started on port: %d' % self.port)
        self.server.register_function(self.log, 'log')
        self.server.register_function(self.debug, 'debug')
        self.server.register_function(self.info, 'info')
        self.server.register_function(self.warning, 'warning')
        self.server.register_function(self.error, 'error')
        self.server.register_function(self.critical, 'critical')
        self._running = True
        self._handles = [self._handle_main]

    def _run(self):
        self._setup()
        start(self._serve, ())
        self._main()

    def _main(self):
        try:
            while self._running:
                try:
                    for handle in self._handles:
                        handle()
                    time.sleep(0.01)
                except socket.error, msg:
                    self.error('Socket Error: %s' % msg)
        except KeyboardInterrupt:
            pass
        log.info('Server stopped.')
        self.shutdown()

    def _handle_main(self):
        time.sleep(0.1)

    def _serve(self):
        self._connect()
        try:
            while self._running:
                try:
                    self._handle_server()
                except xmlrpclib.Fault, msg:
                    self.error('XML RPC Error: %s' % msg.faultString)
        except KeyboardInterrupt:
            pass
        log.info('Server stopped.')
        self.shutdown()
        self._disconnect()
        
    def _connect(self):
        pass
        
    def _disconnect(self):
        self.server.socket.close()
        self.server = None
    
    def _handle_server(self):
        self.log(5, 'Starting server handler.')
        ins = [self.server,]
        outs = []
        ers = []
        try:
            inputs, outputs, errs = select.select(ins,
                                                  outs,
                                                  ers)
        except Exception, msg:
            log.error(msg)
            return
        for sock in inputs:
            if sock == self.server:
                start(self.server.handle_request, ())
        self.log(5, 'Stopping server handler.')

    def _register_timeout(self, key, length):
        self._timeouts[key] = (length, 0)

    def _timeout(self, key):
        length, last_time = self._timeouts[key]
        now = time.time()
        delta = now - last_time
        if delta > length:
            self._timeouts[key] = (length, now)
            return True
        else:
            return False

    def shutdown(self):
        self._running = False
        return self._running
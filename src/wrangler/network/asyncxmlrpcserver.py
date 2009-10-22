#!/usr/bin/env python

import socket
import logging
import SocketServer
from threading import Thread
from SimpleXMLRPCServer import SimpleXMLRPCServer

log = logging.getLogger('wrangler')

class CustomThreadingMixIn:
    """Mix-in class to handle each request in a new thread."""
    # Decides how threads will act upon termination of the main process
    daemon_threads = True

    def process_request_thread(self, request, client_address):
        """Same as in BaseServer but as a thread.
        In addition, exception handling is done here.
        """
        try:
            self.finish_request(request, client_address)
            self.close_request(request)
        except (socket.error), why:
            print 'socket.error finishing request from "%s"; Error: %s' % (client_address, str(why))
            self.close_request(request)
        except:
            self.handle_error(request, client_address)
            self.close_request(request)

    def process_request(self, request, client_address):
        """Start a new thread to process the request."""
        log.debug('Spawning a new thread for %s:%d' % client_address)
        t = Thread(target = self.process_request_thread, args = (request, client_address))
        if self.daemon_threads:
            t.setDaemon(1)
        t.start()

#class AsyncXMLRPCServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer): pass
class AsyncXMLRPCServer(SimpleXMLRPCServer): pass
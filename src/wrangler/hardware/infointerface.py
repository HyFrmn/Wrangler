#!/usr/bin/env python

import socket
import platform

class InfoInterface(object):
    def __init__(self):
        pass

    def memory(self):
        """Return the amount of memory on the system in GB as a float."""
        raise NotImplementedError

    def ncpu(self):
        """Return the number of CPUs on the system as an integer."""
        raise NotImplementedError

    def load_avg(self):
        """Return the load average on the system as a float."""
        raise NotImplementedError

    def hostname(self):
        return platform.node()

    def system(self):
        return platform.system()

    def processor(self):
        return platform.processor()

    def ip(self):
        return socket.gethostbyname(socket.gethostname())
    
    def dict(self):
        output = {}
        attrs = [attr for attr in dir(self)]
        for attr in attrs:
            if attr == 'dict':
                continue
            if str(attr).startswith('_'):
                continue
            output[attr] = getattr(self, attr)()
        return output
#!/usr/bin/env python

import os
import sys

from wrangler.cattle.client import CattleClient
from wrangler.lasso.client import LassoClient

__all__ = ['sleep',
           'wake',
           'task_list',
           'queue_list']

def main():
    if len(sys.argv) < 2:
        help()
        sys.exit(1)

    args = sys.argv[1:]
    cmd = args.pop(0)

    if cmd in globals().keys():
        globals()[cmd](*args)

def sleep(*args):
    """Put target cattle to sleep. Usage: wrangler sleep [cattle1] [cattle2] ... [cattleN]"""
    for hostname in args:
        client = CattleClient(hostname)
        client.sleep()

def wake(*args):
    """Wake target cattle up. Usage: wrangler wake [cattle1] [cattle2] ... [cattleN]"""
    for hostname in args:
        client = CattleClient(hostname)
        client.wake_up()

def task_list(*args):
    """Print a list of tasks that a given cattle is currently chewing on."""
    hostname = args[0]
    client = CattleClient(hostname)
    for task in client.task_list():
        print task

def state(*args):
    for hostname in args:
        client = CattleClient(hostname)
        state = client.state()
        if state == 0:
            state_desc = 'Sleeping'
        elif state == 1:
            state_desc = 'Awake'
        else:
            state_desc = 'Unknown'
        print '%16s - %s' % (hostname, state_desc)

def queue_list(*args):
    """Print the list of tasks currently in the lasso's queue."""
    pass

def help():
    print 'Usage: wrangle [cmd] <options>'
    print '-' * 40
    # Two empty lines for formatting.
    print 
    print
    print 'Command List'
    print '-' * 40
    for func in __all__:
        print '%12s - %s' % (func, globals()[func].__doc__)
    
    # Two empty lines for formatting. 
    print 
    print

if __name__ == '__main__':
    main()
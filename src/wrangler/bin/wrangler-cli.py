#!/usr/bin/env python

import os
import sys

from wrangler.cattled.client import CattleClient
from wrangler.lassod.client import LassoClient

__all__ = ['sleep',
           'wake',
           'state',
           'task_list',
           'queue_list']

def lasso_call(item, cmd, args):
    func_name = item + '_' + cmd
    client = LassoClient()
    func = getattr(client, func_name)
    return func(*args)

def main():
    if len(sys.argv) < 3:
        help()
        sys.exit(1)

    args = sys.argv[1:]
    item = args.pop(0)
    cmd = args.pop(0)

    return_ = lasso_call(item, cmd, args)
    print return_

def help():
    print 'Usage: wrangle [item] [cmd] <options>'
#    print '-' * 40
#    # Two empty lines for formatting.
#    print 
#    print
#    print 'Command List'
#    print '-' * 40
#    for func in __all__:
#        print '%12s - %s' % (func, globals()[func].__doc__)
#    
#    # Two empty lines for formatting. 
#    print 
#    print

if __name__ == '__main__':
    main()
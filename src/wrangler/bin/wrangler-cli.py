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

def cmd_help():
    client = LassoClient()
    print client.help()

def main():
    try:
        args = sys.argv[1:]
        item = args.pop(0)
        if item == 'help' and len(args) == 0:
            cmd_help()
            sys.exit(1)
        cmd = args.pop(0)
    except IndexError:
        help()
        sys.exit(1)


    return_ = lasso_call(item, cmd, args)
    print return_

def help():
    print 'Usage: wrangle [item] [cmd] <options>'


if __name__ == '__main__':
    main()
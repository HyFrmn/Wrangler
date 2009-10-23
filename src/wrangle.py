#!/usr/bin/env python

import os
import sys

from wrangler.cattle.client import CattleClient
from wrangler.lasso.client import LassoClient

def main():
    if len(sys.argv) < 2:
        print 'Usage: wrangle [cmd] <options>'
        sys.exit(1)

    args = sys.argv[1:]
    cmd = args.pop(0)

    if cmd in globals().keys():
        globals()[cmd](*args)

def sleep(*args):
    for hostname in args:
        client = CattleClient(hostname)
        client.sleep()

if __name__ == '__main__':
    main()
#!/usr/bin/env python

import os
import sys

wrangler_module_dir = os.path.abspath(__file__)
wrangler_module_dir = os.path.dirname(wrangler_module_dir)
wrangler_module_dir = os.path.dirname(wrangler_module_dir)
wrangler_module_dir = os.path.dirname(wrangler_module_dir)

sys.path.append(wrangler_module_dir)

from wrangler.hardware import info
from wrangler.cattled.server import CattleServer

def main():
    server = CattleServer()
    server._run()

if __name__ == '__main__':
    main()
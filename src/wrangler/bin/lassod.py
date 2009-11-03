#!/usr/bin/env python

import os
import sys

wrangler_module_dir = os.path.abspath(__file__)
wrangler_module_dir = os.path.dirname(wrangler_module_dir)
wrangler_module_dir = os.path.dirname(wrangler_module_dir)
wrangler_module_dir = os.path.dirname(wrangler_module_dir)

sys.path.append(wrangler_module_dir)

from wrangler.lassod.server import LassoServer
from wrangler.hardware import info

def main():
    server = LassoServer()
    server._run()

if __name__ == '__main__':
    main()
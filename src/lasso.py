#!/usr/bin/env python

from wrangler.lasso.server import LassoServer
from wrangler.hardware import info

def main():
    server = LassoServer()
    server._run()

if __name__ == '__main__':
    main()
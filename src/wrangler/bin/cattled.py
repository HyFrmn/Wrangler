#!/usr/bin/env python

from wrangler.hardware import info
from wrangler.cattled.server import CattleServer

def main():
    server = CattleServer()
    server._run()

if __name__ == '__main__':
    main()
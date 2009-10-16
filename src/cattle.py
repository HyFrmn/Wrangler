#!/usr/bin/env python

from wrangler.cattle import CattleServer
from wrangler.hardware import info

def main():
    server = CattleServer(info.hostname(), 6789, 'wrangler.cattle')
    server._run()

if __name__ == '__main__':
    main()
#!/usr/bin/env python

from wrangler.hardware.infointerface import InfoInterface

__all__ = ['info']

_system = InfoInterface().system()

info = InfoInterface()
if _system == 'Darwin':
    from wrangler.hardware.osx import OSXInfo
    info = OSXInfo()

if _system == 'Linux':
    from wrangler.hardware.linux import LinuxInfo
    info = LinuxInfo()
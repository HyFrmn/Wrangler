#!/usr/bin/env python

class WranglerError(Exception):pass

class WranglerNetworkError(WranglerError):pass

class WranglerConnectionError(WranglerNetworkError):pass

class LassoError(WranglerError):pass

class CattleError(WranglerError):pass
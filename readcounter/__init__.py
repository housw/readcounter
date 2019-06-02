# -*- coding: utf-8 -*-

"""Top-level package for readcounter."""


__author__ = """Shengwei Hou"""
__email__ = 'housw2010@gmail.com'
def version():
    """Read program version from file."""
    import readcounter
    import os
    version_file = open(os.path.join(readcounter.__path__[0], 'VERSION'), "r")
    _version = version_file.readline().strip()
    version_file.close()
    return _version
__version__ = version()

from __future__ import absolute_import, print_function
import pkg_resources
import sys

try:
    __version__ = pkg_resources.get_distribution('pew').version
except pkg_resources.DistributionNotFound:
    __version__ = 'unknown'
    print('Setuptools has some issues here, failed to get our own package.', file=sys.stderr)

from . import pew
__all__ = ['pew']

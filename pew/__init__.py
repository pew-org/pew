from __future__ import absolute_import
import pkg_resources

__version__ = pkg_resources.get_distribution('pew').version

from . import pew, _utils
__all__ = ['pew']

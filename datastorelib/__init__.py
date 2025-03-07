import sys
from .influx2 import Influx2
from ._version import __version__


__version__ = __version__

if sys.version_info <= (3, 12):
    raise Exception('python >= 3.12 is required')

__all__ = ['Influx2']

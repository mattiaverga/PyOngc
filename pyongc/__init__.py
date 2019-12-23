"""Python interface to OpenNGC database data.

:license: MIT, see LICENSE for more details.
"""
__all__ = ['ongc', 'exceptions']

from .exceptions import InvalidCoordinates, ObjectNotFound, UnknownIdentifier
from .ongc import Dso, getNeighbors, getSeparation, listObjects, nearby, printDetails, stats

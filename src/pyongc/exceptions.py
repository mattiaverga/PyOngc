# -*- coding:utf-8 -*-
#
# MIT License
#
# Copyright (c) 2019 Mattia Verga <mattia.verga@tiscali.it>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""Exceptions for PyONGC."""

from typing import Optional


class InvalidCoordinates(Exception):
    """
    Raised when coordinates are not valid.

    Maybe you're passing an object without registered coordinates (typically an `Unknown` object)
    to some function; or you input coordinates as text in a wrong format: to be recognized
    the input text must be in the format `HH:MM:SS.ss +/-DD:MM:SS.s`.
    """
    def __init__(self, text: Optional[str] = None):
        if text is not None:
            super().__init__(text)
        else:  # pragma: no cover
            super().__init__('Coordinates not recognized.')


class ObjectNotFound(Exception):
    """
    Raised when a valid object identifier isn't found in the database.

    The identifier is recognized to be part of one of the supported catalogs,
    but the object isn't in the database (or doesn't exist at all).

    For example, `pyongc.Dso('NGC7000A')` is valid, but it doesn't exist.
    """
    def __init__(self, name: Optional[str] = None):
        if name is not None:
            super().__init__(f'Object named {name} not found in the database.')
        else:  # pragma: no cover
            super().__init__('Object not found in the database.')


class UnknownIdentifier(Exception):
    """
    Raised when input text can't be recognized as a valid object identifier.

    You're asking for an identifier using the wrong format, or using an identifier
    which refers to a catalog not supported by PyOngc.
    """
    def __init__(self, text: Optional[str] = None):
        if text is not None:
            super().__init__(f'The name "{text}" is not recognized.')
        else:  # pragma: no cover
            super().__init__('Unrecognized object name.')

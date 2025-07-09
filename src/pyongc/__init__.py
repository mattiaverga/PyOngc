# SPDX-FileCopyrightText: 2017 Mattia Verga <mattia.verga@tiscali.it>
#
# SPDX-License-Identifier: MIT

"""Python interface to OpenNGC database data."""

from importlib.metadata import version
from importlib.resources import files


__version__ = version('PyOngc')
DBDATE = 20231203  # Version of database data

DBPATH = str(files(__name__) / 'ongc.db')

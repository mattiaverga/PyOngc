# SPDX-FileCopyrightText: 2017 Mattia Verga <mattia.verga@tiscali.it>
#
# SPDX-License-Identifier: MIT

"""Python interface to OpenNGC database data."""

from pkg_resources import resource_filename


__version__ = '1.0.1'
DBDATE = 20221023  # Version of database data

DBPATH = resource_filename(__name__, 'ongc.db')

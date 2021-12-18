# -*- coding:utf-8 -*-
#
# MIT License
#
# Copyright (c) 2021 Mattia Verga <mattia.verga@tiscali.it>
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

"""Provides access to OpenNGC data through Pandas' DataFrames.

Methods provided:
    * all: Returns all data. Useful for subsequent custom data filtering.
    * clusters: Returns data for star clusters.
    * galaxies: Returns data for all galaxies in the database.
    * nebulae: Returns data for nebulae.
"""

from typing import Optional
import pandas as pd
import sqlite3

from pyongc import DBPATH

COMMON_COLS = ['name', 'type', 'ra', 'dec', 'const', 'majax', 'minax', 'pa',
               'messier', 'ngc', 'ic', 'bmag', 'vmag', 'jmag', 'hmag', 'kmag', 'notngc',
               'parallax', 'pmra', 'pmdec', 'radvel', 'redshift']


def _get_from_db(query: str) -> pd.core.frame.DataFrame:
    """Common code for retrieving data from database."""
    try:
        conn = sqlite3.connect(f'file:{DBPATH}?mode=ro', uri=True)
    except sqlite3.Error:
        raise OSError(f'There was a problem accessing database file at {DBPATH}')

    try:
        df = pd.read_sql_query(query, conn, dtype={"notngc": bool})
        return df
    except Exception as err:  # pragma: no cover
        raise err
    finally:
        conn.close()


def all() -> pd.core.frame.DataFrame:
    """Returns all data in the database.

    Useful for subsequent custom data filtering.

    """
    query = "SELECT * FROM objects;"
    return _get_from_db(query)


def clusters(globular: bool = True, open: bool = True, other: bool = False,
             extra_ids: bool = False, notngc: bool = False) -> Optional[pd.core.frame.DataFrame]:
    """Returns data for star clusters.

    Args:
        globular: fetch data for globular clusters
        open: fetch data for open clusters
        other: fetch data for star associations and Cl+N types
        extra_ids: adds extra identifiers and common names to the output
        notngc: if set to True return objects from the addendum catalog, otherwise
            return objects from the main NGC/IC catalog only

    """
    if not globular and not open and not other:
        return None
    types = []
    cols = COMMON_COLS.copy()
    if globular:
        types.append("'GCl'")
    if open:
        types.append("'OCl'")
    if other:
        types += ["'*Ass'", "'Cl+N'"]
    if extra_ids:
        cols += ['identifiers', 'commonnames']
    query = f"SELECT {','.join(cols)} FROM objects WHERE type IN ({','.join(types)});"
    objs = _get_from_db(query)
    return objs[objs['notngc'] == notngc]


def galaxies(extra_ids: bool = False, notngc: bool = False) -> pd.core.frame.DataFrame:
    """Returns data for all galaxies in the database.

    Args:
        extra_ids: adds extra identifiers and common names to the output
        notngc: if set to True return objects from the addendum catalog, otherwise
            return objects from the main NGC/IC catalog only

    """
    cols = COMMON_COLS + ['sbrightn', 'hubble']
    if extra_ids:
        cols += ['identifiers', 'commonnames']
    query = f"SELECT {','.join(cols)} FROM objects WHERE type = 'G';"
    objs = _get_from_db(query)
    return objs[objs['notngc'] == notngc]


def nebulae(extra_ids: bool = False, notngc: bool = False) -> pd.core.frame.DataFrame:
    """Returns data for all galaxies in the database.

    Args:
        extra_ids: adds extra identifiers and common names to the output
        notngc: if set to True return objects from the addendum catalog, otherwise
            return objects from the main NGC/IC catalog only

    """
    cols = COMMON_COLS + ['cstarumag', 'cstarbmag', 'cstarvmag', 'cstarnames']
    types = ["'Cl+N'", "'EmN'", "'HII'", "'Neb'", "'PN'", "'RfN'", "'SNR'"]
    if extra_ids:
        cols += ['identifiers', 'commonnames']
    query = f"SELECT {','.join(cols)} FROM objects WHERE type IN ({','.join(types)})"
    objs = _get_from_db(query)
    return objs[objs['notngc'] == notngc]

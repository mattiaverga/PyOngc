#!/usr/bin/python
# -*- coding:utf-8 -*-
#
#
# MIT License
#
# Copyright (c) 2017 Mattia Verga <mattia.verga@tiscali.it>
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

"""Creates sqlite3 database from csv OpenNGC file.
The first line of the csv file, which contains the headers, must be removed.

    Usage: createdb.py
"""

import os
import csv
import numpy as np
import re
import sqlite3

outputFile = os.path.join(os.path.dirname(__file__), os.pardir, 'src', 'pyongc', 'ongc.db')

# Dictionaries
objectTypes = {'*': 'Star',
               '**': 'Double star',
               '*Ass': 'Association of stars',
               'OCl': 'Open Cluster',
               'GCl': 'Globular Cluster',
               'Cl+N': 'Star cluster + Nebula',
               'G': 'Galaxy',
               'GPair': 'Galaxy Pair',
               'GTrpl': 'Galaxy Triplet',
               'GGroup': 'Group of galaxies',
               'PN': 'Planetary Nebula',
               'HII': 'HII Ionized region',
               'DrkN': 'Dark Nebula',
               'EmN': 'Emission Nebula',
               'Neb': 'Nebula',
               'RfN': 'Reflection Nebula',
               'SNR': 'Supernova remnant',
               'Nova': 'Nova star',
               'NonEx': 'Nonexistent object',
               'Other': 'Object of other/unknown type',
               'Dup': 'Duplicated record'}
PATTERNS = {'NGC|IC': r'^((?:NGC|IC)\s?)(\d{1,4})\s?((NED)(\d{1,2})|[A-Z]{1,2})?$',
            'Messier': r'^(M\s?)(\d{1,3})$',
            'Barnard': r'^(B\s?)(\d{1,3})$',
            'Caldwell': r'^(C\s?)(\d{1,3})$',
            'Collinder': r'^(CL\s?)(\d{1,3})$',
            'ESO': r'^(ESO\s?)(\d{1,3})-(\d{1,3})$',
            'Harvard': r'^(H\s?)(\d{1,2})$',
            'Hickson': r'^(HCG\s?)(\d{1,3})$',
            'LBN': r'^(LBN\s?)(\d{1,3})$',
            'Melotte': r'^(MEL\s?)(\d{1,3})$',
            'MWSC': r'^(MWSC\s?)(\d{1,4})$',
            'PGC': r'^((?:PGC|LEDA)\s?)(\d{1,6})$',
            'UGC': r'^(UGC\s?)(\d{1,5})$',
            }

# Create db
try:
    db = sqlite3.connect(outputFile)
    cursor = db.cursor()

    # Create objects types table
    cursor.execute('DROP TABLE IF EXISTS objTypes')
    cursor.execute('CREATE TABLE IF NOT EXISTS objTypes('
                   'type TEXT PRIMARY KEY NOT NULL, '
                   'typedesc TEXT NOT NULL)')
    listTypes = objectTypes.items()
    cursor.executemany('INSERT INTO objTypes VALUES(?,?)', listTypes)

    # Create main objects table
    cursor.execute('DROP TABLE IF EXISTS objects')
    cursor.execute('CREATE TABLE IF NOT EXISTS objects('
                   'id INTEGER PRIMARY KEY NOT NULL, '
                   'name TEXT NOT NULL UNIQUE, '
                   'type TEXT NOT NULL, '
                   'ra REAL, '
                   'dec REAL, '
                   'const TEXT, '
                   'majax REAL, '
                   'minax REAL, '
                   'pa INTEGER, '
                   'bmag REAL, '
                   'vmag REAL, '
                   'jmag REAL, '
                   'hmag REAL, '
                   'kmag REAL, '
                   'sbrightn REAL, '
                   'hubble TEXT, '
                   'cstarumag REAL, '
                   'cstarbmag REAL, '
                   'cstarvmag REAL, '
                   'messier TEXT, '
                   'ngc TEXT, '
                   'ic TEXT, '
                   'cstarnames TEXT, '
                   'identifiers TEXT, '
                   'commonnames TEXT, '
                   'nednotes TEXT, '
                   'ongcnotes TEXT, '
                   'notngc BOOL DEFAULT FALSE)')

    # Create object identifiers table
    cursor.execute('DROP TABLE IF EXISTS objIdentifiers')
    cursor.execute('CREATE TABLE IF NOT EXISTS objIdentifiers('
                   'id INTEGER PRIMARY KEY NOT NULL, '
                   'name TEXT NOT NULL, '
                   'identifier TEXT NOT NULL UNIQUE)')

    for filename in ('NGC.csv', 'addendum.csv'):
        notngc = True if filename != 'NGC.csv' else False
        with open(filename, 'r') as csvFile:
            reader = csv.reader(csvFile, delimiter=';')
            # List of columns that are not text and should be transformed in NULL if empty
            columns_maybe_null = [5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17]
            for line in reader:
                for column in columns_maybe_null:
                    if line[column] == '':
                        line[column] = None

                # Convert RA and Dec in radians
                if line[2] != '':
                    ra_array = np.array([float(x) for x in line[2].split(':')])
                    ra_rad = np.radians(np.sum(ra_array * [15, 1/4, 1/240]))
                else:
                    ra_rad = None
                if line[3] != '':
                    dec_array = np.array([float(x) for x in line[3].split(':')])
                    if np.signbit(dec_array[0]):
                        dec_rad = np.radians(np.sum(dec_array * [1, -1/60, -1/3600]))
                    else:
                        dec_rad = np.radians(np.sum(dec_array * [1, 1/60, 1/3600]))
                else:
                    dec_rad = None

                cursor.execute('INSERT INTO objects(name,type,ra,dec,const,majax,minax,pa,bmag,'
                               'vmag,jmag,hmag,kmag,sbrightn,hubble,cstarumag,cstarbmag,'
                               'cstarvmag,messier,ngc,ic,cstarnames,identifiers,commonnames,'
                               'nednotes,ongcnotes,notngc) '
                               'VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                               (line[0], line[1], ra_rad, dec_rad, line[4], line[5], line[6],
                                line[7], line[8], line[9], line[10], line[11], line[12], line[13],
                                line[14], line[15], line[16], line[17], line[18], line[19],
                                line[20], line[21], line[22], line[23], line[24], line[25], notngc)
                               )
                cursor.execute('INSERT INTO objIdentifiers(name,identifier) VALUES(?,?)',
                               (line[0], line[0].upper())
                               )
                for identifier in line[22].split(','):
                    for cat, pat in PATTERNS.items():
                        name_parts = re.match(pat, identifier)
                        if name_parts is not None:
                            if cat == 'NGC|IC' and name_parts.group(3) is not None:
                                if name_parts.group(4) is not None:
                                    objectname = f'{name_parts.group(1).strip()}' \
                                                 f'{name_parts.group(2):0>4}' \
                                                 f' {name_parts.group(4)}' \
                                                 f'{name_parts.group(5):0>2}'
                                else:
                                    objectname = f'{name_parts.group(1).strip()}' \
                                                 f'{name_parts.group(2):0>4}' \
                                                 f'{name_parts.group(3).strip()}'
                            elif cat in ('NGC|IC', 'MWSC'):
                                objectname = f'{name_parts.group(1).strip()}' \
                                             f'{name_parts.group(2):0>4}'
                            elif cat == 'ESO':
                                objectname = f'{name_parts.group(1).strip()}' \
                                             f'{name_parts.group(2):0>3}-' \
                                             f'{name_parts.group(3):0>3}'
                            elif cat == 'Harvard':
                                objectname = f'{name_parts.group(1).strip()}' \
                                             f'{name_parts.group(2):0>2}'
                            elif cat == 'UGC':
                                objectname = f'{name_parts.group(1).strip()}' \
                                             f'{name_parts.group(2):0>5}'
                            elif cat == 'PGC':
                                # Fixed catalog name to recognize also LEDA prefix
                                objectname = f'{cat}{name_parts.group(2):0>6}'
                            else:
                                objectname = f'{name_parts.group(1).strip()}' \
                                             f'{name_parts.group(2):0>3}'
                            cursor.execute('INSERT INTO objIdentifiers(name,identifier) '
                                           'VALUES(?,?)',
                                           (line[0], objectname)
                                           )

    cursor.execute('CREATE UNIQUE INDEX "idx_identifiers" ON "objIdentifiers" ("identifier");')
    db.commit()

except Exception as e:
    db.rollback()
    raise e

finally:
    db.close()

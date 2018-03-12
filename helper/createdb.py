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
import sqlite3
#
outputFile = os.path.join(os.path.dirname(__file__), os.pardir, 'pyongc', 'ongc.db')

# Dictionaries
objectTypes = {'*':'Star',
        '**':'Double star',
        '*Ass':'Association of stars',
        'OCl':'Open Cluster',
        'GCl':'Globular Cluster',
        'Cl+N':'Star cluster + Nebula',
        'G':'Galaxy',
        'GPair':'Galaxy Pair',
        'GTrpl':'Galaxy Triplet',
        'GGroup':'Group of galaxies',
        'PN':'Planetary Nebula',
        'HII':'HII Ionized region',
        'DrkN':'Dark Nebula',
        'EmN':'Emission Nebula',
        'Neb':'Nebula',
        'RfN':'Reflection Nebula',
        'SNR':'Supernova remnant',
        'Nova':'Nova star',
        'NonEx':'Nonexistent object',
        'Other':'Object of other/unknown type',
        'Dup':'Duplicated record'}

# Create db
try:
    db = sqlite3.connect(outputFile)
    cursor = db.cursor()

    # Create objects types table
    cursor.execute("DROP TABLE IF EXISTS objTypes")
    cursor.execute('''CREATE TABLE IF NOT EXISTS objTypes(
            type TEXT PRIMARY KEY NOT NULL,
            typedesc TEXT NOT NULL
            )''')
    listTypes = objectTypes.items()
    cursor.executemany("INSERT INTO objTypes VALUES(?,?)", listTypes)

    # Create main objects table
    cursor.execute("DROP TABLE IF EXISTS objects")
    cursor.execute('''CREATE TABLE IF NOT EXISTS objects(
            id INTEGER PRIMARY KEY NOT NULL,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            ra TEXT,
            dec TEXT,
            const TEXT,
            majax REAL,
            minax REAL,
            pa INTEGER,
            bmag REAL,
            vmag REAL,
            jmag REAL,
            hmag REAL,
            kmag REAL,
            sbrightn REAL,
            hubble TEXT,
            cstarumag REAL,
            cstarbmag REAL,
            cstarvmag REAL,
            messier INTEGER,
            ngc TEXT,
            ic TEXT,
            cstarnames TEXT,
            identifiers TEXT,
            commonnames TEXT,
            nednotes TEXT,
            ongcnotes TEXT
            )''')

    with open("NGC.csv", 'r') as csvFile:
        reader = csv.reader(csvFile, delimiter=";")
        for line in reader:
            cursor.execute('''INSERT INTO objects(name,type,ra,dec,const,majax,minax,pa,bmag,vmag,
                    jmag,hmag,kmag,sbrightn,hubble,cstarumag,cstarbmag,cstarvmag,messier,ngc,ic,
                    cstarnames,identifiers,commonnames,nednotes,ongcnotes)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ''', (line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line[8],
                    line[9],line[10],line[11],line[12],line[13],line[14],line[15],line[16],line[17],
                    line[18],line[19],line[20],line[21],line[22],line[23],line[24],line[25]))

    db.commit()

except Exception as e:
    db.rollback()
    raise e

finally:
    db.close()

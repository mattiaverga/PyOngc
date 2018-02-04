# -*- coding:utf-8 -*-
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

"""Provides classes and functions to access OpenNGC database.

Classes provided:
        * Dso: the main class which describe a single row (object) from OpenNGC database.

Methods provided:
        * getNeighbors: Find all neighbors of a object within a user selected range.
        * getSeparation: Calculate the apparent angular separation between two objects.
        * listObjects: Query DB for DSObjects with specific parameters.
        * printDetails: Prints a detailed description of the object in a formatted output.
        * searchAltId: Search a object in the database using an alternative identifier.
"""

from math import acos, cos, degrees, radians, sin
from pkg_resources import resource_filename
import os
import re
import sqlite3
import sys

__version__ = '0.1.1'
DBDATE = 20180203 #Version of database data
DBPATH = resource_filename(__name__, 'ongc.db')

class Dso(object):
        """Defines a single Deep Sky Object from ONGC database.
        
        A DSO object represents a single row from OpenNGC database, which corresponds to
        a Deep Sky Object from NGC or IC catalogs.
        
        The class provides the following methods to access object data:
                * __init__: Object constructor.
                * __str__: Returns basic data of the object as a formatted string.
                * getConstellation: Returns the constellation where the object is located.
                * getCoords: Returns the coordinates of the object in J2000 Epoch.
                * getCStarData: Returns data about central star of planetary nebulaes.
                * getDec: Returns the Declination in J2000 Epoch.
                * getDimensions: Returns object axes dimensions and position angle.
                * getHubble: Returns the Hubble classification of the galaxy.
                * getId: Returns the database Id of the object.
                * getIdentifiers: Returns the alternative identifiers of the object.
                * getMagnitudes: Returns the magnitudes of the object.
                * getName: Returns the main identifier of the object.
                * getNotes: Returns notes from NED and from ONGC author.
                * getSurfaceBrightness: Returns the surface brightness value of the galaxy.
                * getType: Returns the type of the object.
                * getRA: Returns the Right Ascension in J2000 Epoch.
                * xephemFormat: Returns object data in Xephem format.
        """
        
        def __init__(self, name, returnDup=False) :
                """Object constructor.
                
                :param string name: identifier of the NGC or IC object
                :optional param returnDup: if True don't resolve Dup objects
                """
                # Make sure user passed a string as parameter
                if not isinstance(name, str):
                        raise TypeError('Wrong type as parameter. A string type was expected.')
                
                # Make sure object name is written in correct form
                nameParts = re.match(r'((?:NGC|IC)\s?)(\d{1,4})(\s?(NED)(\d{1,2})|\s?[A-Z]+)?',name.upper())
                if nameParts is None :
                        raise ValueError('Wrong object name. Please insert a valid NGC or IC object name.')
                
                if nameParts.group(3) is not None :
                        # User searches for a sub-object
                        if nameParts.group(4) is not None :
                                # User searches for a NED suffixed component
                                objectname = (nameParts.group(1).strip()
                                + '{:0>4}'.format(nameParts.group(2))
                                + ' '
                                + nameParts.group(4)
                                + '{:0>2}'.format(nameParts.group(5))
                                )
                        else :
                                # User searches a single letter suffixed component
                                objectname = nameParts.group(1).strip() + '{:0>4}'.format(nameParts.group(2)) + nameParts.group(3).strip()
                else :
                        objectname = nameParts.group(1).strip() + '{:0>4}'.format(nameParts.group(2))
                
                cols = '''objects.id, objects.type, objTypes.typedesc, ra, dec, const, majax, minax, 
                                pa, bmag, vmag, jmag,hmag, kmag, sbrightn, hubble, cstarumag, cstarbmag, cstarvmag, messier, 
                                ngc, ic, cstarnames,identifiers, commonnames, nednotes, ongcnotes'''
                tables = 'objects JOIN objTypes ON objects.type = objTypes.type'
                params = 'name="' + objectname + '"'
                objectData = _queryFetchOne(cols, tables, params)
                
                if objectData is None:
                        raise ValueError('Object named ' + objectname +' not found in the database.')
                
                # If object is a duplicate then return the main object
                if objectData[1] == "Dup" and not returnDup:
                        if objectData[20] != "":
                                objectname = "NGC" + str(objectData[20])
                        else:
                                objectname = "IC" + str(objectData[21])
                        params = 'name="' + objectname + '"'
                        objectData = _queryFetchOne(cols, tables, params)
                
                # Assign object properties
                self._id = objectData[0]
                self._name = objectname
                self._type = str(objectData[2])
                self._ra = str(objectData[3])
                self._dec = str(objectData[4])
                self._const = str(objectData[5])
                
                # These properties may be empty
                self._majax = Dso._assignValue(objectData[6])
                self._minax = Dso._assignValue(objectData[7])
                self._pa = Dso._assignValue(objectData[8])
                self._bmag = Dso._assignValue(objectData[9])
                self._vmag = Dso._assignValue(objectData[10])
                self._jmag = Dso._assignValue(objectData[11])
                self._hmag = Dso._assignValue(objectData[12])
                self._kmag = Dso._assignValue(objectData[13])
                self._sbrightn = Dso._assignValue(objectData[14])
                self._hubble = str(objectData[15])
                self._cstarumag = Dso._assignValue(objectData[16])
                self._cstarbmag = Dso._assignValue(objectData[17])
                self._cstarvmag = Dso._assignValue(objectData[18])
                self._messier = str(objectData[19])
                self._ngc = str(objectData[20])
                self._ic = str(objectData[21])
                self._cstarnames = str(objectData[22])
                self._identifiers = str(objectData[23])
                self._commonnames = str(objectData[24])
                self._nednotes = str(objectData[25])
                self._ongcnotes = str(objectData[26])
        
        def __str__(self):
                """Returns basic data of the object.
                
                        >>> s = Dso("ngc1")
                        >>> print(s)
                        NGC0001, Galaxy in Peg
                
                """
                return (self._name + ", " + self._type + " in " + self._const)
        
        @staticmethod
        def _assignValue(value):
                """ Returns value or None type if value is an empty string."""
                if value == "":
                        return None
                else:
                        return value
        
        def getConstellation(self):
                """Returns the constellation where the object is located.
                
                :returns: 'constellation'
                
                        >>> s = Dso("ngc1")
                        >>> s.getConstellation()
                        'Peg'
                
                """
                return self._const
        
        def getCoords(self):
                """Returns the coordinates of the object in J2000 Epoch.
                
                :returns: ((HH,MM,SS.SS),(+/-,DD,MM,SS.SS))
                
                The value is espressed as a tuple of tuples 
                with numerical values espressed as int or float:
                
                        >>> s = Dso("ngc1")
                        >>> s.getCoords()
                        ((0, 7, 15.84), ('+', 27, 42, 29.1))
                
                """
                if self._ra == "" or self._dec == "":
                        raise ValueError('Object named ' + self._name +' has no coordinates in database.')
                ra = self._ra.split(":")
                dec = self._dec.split(":")
                raTuple = (int(ra[0]), int(ra[1]), float(ra[2]))
                decTuple = (dec[0][0], int(dec[0][1:]), int(dec[1]), float(dec[2]))
                return raTuple, decTuple
        
        def getCStarData(self):
                """Returns data about central star of planetary nebulaes.
                
                :returns: ([cstar identifiers], cstar UMag, cstar BMag, cstar VMag)
                
                If the DSO object is a Planetary Nebulae, this method will return a tuple with
                the central star identifiers and its magnitudes in U-B-V bands:
                
                        >>> s = Dso("ngc1535")
                        >>> s.getCStarData()
                        (['BD -13 842', 'HD 26847'], None, 12.19, 12.18)
                
                If the object is not a PN it returns all None values:
                
                        >>> s = Dso("ngc1")
                        >>> s.getCStarData()
                        (None, None, None, None)
                
                """
                if self._cstarnames != "":
                        identifiers = list(map(str.strip, self._cstarnames.split(",")))
                else:
                        identifiers = None
                        
                return identifiers, self._cstarumag, self._cstarbmag, self._cstarvmag
        
        def getDec(self):
                """Returns the Declination in J2000 Epoch.
                
                :returns: '+/-DD:MM:SS.SS'
                
                        >>> s = Dso("ngc1")
                        >>> s.getDec()
                        '+27:42:29.1'
                
                """
                return self._dec
        
        def getDimensions(self):
                """Returns a tuple with object axes dimensions (float) and position angle (int).
                
                :returns: (MajAx, MinAx, P.A.)
                
                Where values are not available a None type is returned.
                
                        >>> s = Dso("ngc1")
                        >>> s.getDimensions()
                        (1.57, 1.07, 112)
                
                """
                return self._majax, self._minax, self._pa
        
        def getHubble(self):
                """Returns the Hubble classification of the object.
                
                :returns: string
                
                        >>> s = Dso("ngc1")
                        >>> s.getHubble()
                        'Sb'
                
                """
                return self._hubble
        
        def getId(self):
                """Returns the database Id of the object.
                
                :returns: int
                
                        >>> s = Dso("ngc1")
                        >>> s.getId()
                        5612
                
                """
                return self._id
        
        def getIdentifiers(self):
                """Returns a tuple of alternative identifiers of the object.
                
                :returns: ('Messier', [NGC], [IC], [common names], [other])
                
                If a field is empty a None type is returned:
                
                        >>> s = Dso("ngc1")
                        >>> s.getIdentifiers()
                        (None, None, None, None, ['2MASX J00071582+2742291', 'IRAS 00047+2725', 'MCG +04-01-025', 'PGC 000564', 'UGC 00057'])
                
                """
                if self._messier == "":
                        messier = None
                else:
                        messier = "M" + self._messier
                        
                if self._ngc == "":
                        ngc = None
                else:
                        ngc = list(map(str.strip, self._ngc.split(",")))
                        ngc = list(map(lambda number: "NGC" + number, ngc))
                
                if self._ic == "":
                        ic = None
                else:
                        ic = list(map(str.strip, self._ic.split(",")))
                        ic = list(map(lambda number: "IC" + number, ic))
                
                if self._commonnames == "":
                        commonNames = None
                else:
                        commonNames = list(map(str.strip, self._commonnames.split(",")))
                
                if self._identifiers == "":
                        other = None
                else:
                        other = list(map(str.strip, self._identifiers.split(",")))
                
                return messier, ngc, ic, commonNames, other
        
        def getMagnitudes(self):
                """Returns the magnitudes of the object as a tuple of floats.
                
                :returns: (Bmag, Vmag, Jmag, Hmag, Kmag)
                
                Where values are not available a None type is returned:
                
                        >>> s = Dso("ngc1")
                        >>> s.getMagnitudes()
                        (13.4, None, 10.78, 10.02, 9.76)
                                
                """
                return self._bmag, self._vmag, self._jmag, self._hmag, self._kmag
        
        def getName(self):
                """Returns the main identifier of the object.
                
                :returns: string
                
                        >>> s = Dso("ngc1")
                        >>> s.getName()
                        'NGC0001'
                
                """
                return self._name
        
        def getNotes(self):
                """Returns notes from NED and from ONGC author.
                
                :returns: ('nednotes', 'ongcnotes')
                
                        >>> s = Dso("ngc6543")
                        >>> s.getNotes()
                        ('Additional radio sources may contribute to the WMAP flux.', 'Dimensions taken from LEDA')
                
                """
                return self._nednotes, self._ongcnotes
        
        def getSurfaceBrightness(self):
                """Returns the surface brightness value of the object.
                
                :returns: float or None
                
                        >>> s = Dso("ngc1")
                        >>> s.getSurfaceBrightness()
                        23.13
                
                """
                return self._sbrightn
        
        def getType(self):
                """Returns the type of the object.
                
                :returns: string
                
                        >>> s = Dso("ngc1")
                        >>> s.getType()
                        'Galaxy'
                
                """
                return self._type
        
        def getRA(self):
                """Returns the Right Ascension in J2000 Epoch.
                
                :returns: 'HH:MM:SS.SS'
                
                        >>> s = Dso("ngc1")
                        >>> s.getRA()
                        '00:07:15.84'
                
                """
                return self._ra
        
        def xephemFormat(self):
                """Returns object data in Xephem format.
                
                :returns: string
                
                This function will produce a string containing information about the object suitable to be imported
                in other software that accept Xephem format (for example: PyEphem).
                
                        >>> s = Dso("ngc1")
                        >>> s.xephemFormat()
                        'NGC0001,f|G,00:07:15.84,+27:42:29.1,13.4,,94.2|64.2|1.07'
                
                """
                line = []
                #Field 1: names
                names = [self.getName()]
                identifiers = self.getIdentifiers()
                if identifiers[0] is not None:
                        names.append(identifiers[0])
                for i in range(1,4):
                        if identifiers[i] is not None:
                                names.extend(identifiers[i])
                line.append("|".join(names))
                
                #Field 2: type designation
                objType = self.getType()
                if objType in ("Galaxy Pair", "Galaxy Triplet", "Group of galaxies"):
                        line.append("f|A")
                elif objType == "Globular Cluster":
                        line.append("f|C")
                elif objType == "Double star":
                        line.append("f|D")
                elif objType in ("HII Ionized region", "Nebula"):
                        line.append("f|F")
                elif objType == "Galaxy":
                        if self.getHubble().startswith("S"):
                                line.append("f|G")
                        else:
                                line.append("f|H")
                elif objType == "Dark Nebula":
                        line.append("f|K")
                elif objType in ("Emission Nebula", "Reflection Nebula"):
                        line.append("f|N")
                elif objType in ("Association of stars", "Open Cluster"):
                        line.append("f|O")
                elif objType == "Planetary Nebula":
                        line.append("f|P")
                elif objType == "Supernova remnant":
                        line.append("f|R")
                elif objType == "Star":
                        line.append("f|S")
                elif objType == "Star cluster + Nebula":
                        line.append("f|U")
                else:
                        line.append("f")
                
                #Field 3: Right Ascension
                line.append(self.getRA())
                
                #Field 4: Declination
                line.append(self.getDec())
                
                #Field 5: Magnitude
                #We use the first available magnitude in the sequence b,v,j,h,k
                for mag in self.getMagnitudes():
                        if mag is not None:
                                line.append(str(mag))
                                break
                
                #Field 6: optional Epoch, we let it empty
                line.append("")
                
                #Field 7: Dimensions
                dimensions = []
                #Xephem format wants axes espressed in arcsec, we have arcmin
                for value in (self.getDimensions()[0],self.getDimensions()[1]):
                        if value is not None:
                                dimensions.append(str(value*60))
                        else:
                                dimensions.append("")
                if self.getDimensions()[2] is not None:
                        dimensions.append(str(value))
                else:
                        dimensions.append("")
                line.append("|".join(dimensions))
                
                return ",".join(line)


def _queryFetchOne(cols, tables, params):
        """Search one row in database.
        
        :param string cols: the SELECT field of the query
        :param string tables: the FROM field of the query
        :param string params: the WHERE field of the query
        :returns: tuple with selected row data from database
        """
        try:
                db = sqlite3.connect(DBPATH)
                cursor = db.cursor()
                
                cursor.execute('SELECT ' + cols 
                        + ' FROM ' + tables 
                        + ' WHERE ' + params
                        )
                objectData = cursor.fetchone()
                
        except Exception as e:
                db.rollback()
                raise e
        
        finally:
                db.close()
        
        return objectData

def _queryFetchMany(cols, tables, params):
        """Search many rows in database.
        
        :param string cols: the SELECT field of the query
        :param string tables: the FROM field of the query
        :param string params: the WHERE field of the query
        :returns: generator object yielding a tuple with selected row data from database
        """
        try:
                db = sqlite3.connect(DBPATH)
                cursor = db.cursor()
                
                cursor.execute('SELECT ' + cols 
                        + ' FROM ' + tables 
                        + ' WHERE ' + params
                        )
                #print(params)
                while True:
                        objectList = cursor.fetchmany()
                        if objectList == []:
                                break
                        yield objectList[0]
                
        except Exception as e:
                db.rollback()
                raise e
        
        finally:
                db.close()

def getNeighbors(obj, separation, filter="all"):
        """Find all neighbors of a object within a user selected range.
        
        :param object: a Dso object or a string which identifies the object
        :param float separation: maximum distance from the object expressed in arcmin
        :param optional string filter: filter for "NGC" or "IC" objects - default is all
        :returns: list of Dso objects within limits ordered by distance [(Dso, separation),]
        
        This function is used to find all objects within a specified range from a given object.
        It requires an object as the starting point of the search (either a string containing the name or
        a Dso type) and a search radius expressed in arcmins.
        Be aware that this can be quite slow as it computes separation for nearly every object in the database!
        It returns a list of of tuples with the Dso objects found in range and its distance, or an empty list 
        if no object is found:
        
                >>> s1 = Dso("ngc521")
                >>> getNeighbors(s1, 15) #doctest: +ELLIPSIS
                [(<__main__.Dso object at 0x...>, 0.13726168561986588), (<__main__.Dso object at 0x...>, 0.2414024394257306)]
                
                >>> getNeighbors("ngc521", 1)
                []
        
        The optional "filter" parameter can be used to filter the search to only NGC or IC objects:
        
                >>> getNeighbors("ngc521", 15, filter="NGC") #doctest: +ELLIPSIS
                [(<__main__.Dso object at 0x...>, 0.2414024394257306)]
        
        """
        if not isinstance(obj, Dso):
                if isinstance(obj, str):
                        obj = Dso(obj)
                else:
                        raise TypeError('Wrong type obj. Either a Dso or string type was expected.')
        if not (isinstance(separation, int) or isinstance(separation, float)):
                raise TypeError('Wrong type separation. Either a int or float type was expected.')
        
        cols = 'objects.name'
        tables = 'objects'
        params = 'type != "Dup" AND ra != "" AND dec != "" AND name !="' + obj.getName() + '"'
        if filter.upper() == "NGC":
                params += " AND name LIKE 'NGC%'"
        elif filter.upper() == "IC":
                params += " AND name LIKE 'IC%'"
        
        neighbors = []
        for item in _queryFetchMany(cols, tables, params):
                possibleNeighbor = Dso(item[0])
                distance = getSeparation(obj, possibleNeighbor)[0]
                if distance <= (separation / 60):
                        neighbors.append((possibleNeighbor, distance))
        
        return sorted(neighbors, key=lambda neighbor: neighbor[1])

def getSeparation(obj1, obj2, style="raw"):
        """Finds the apparent angular separation between two objects.
        
        :param obj1: first Dso object or string identifier
        :param obj2: second Dso object or string identifier
        :param opt string style: use "text" to return a string with degrees, minutes and seconds
        :returns: if style="raw": (float: angular separation, float: difference in A.R, float: difference in Dec)
        :returns: if style="text": 'DD° MMm SS.SSs'
        
        This function will compute the apparent angular separation between two objects, either identified with
        their names as strings or directly as Dso type.
        By default it returns a tuple containing the angular separation and the differences in A.R. and Declination
        expressed in degrees:
        
                >>> s1 = Dso("ngc1")
                >>> s2 = Dso("ngc2")
                >>> getSeparation(s1, s2)
                (0.030089273732482536, 0.005291666666666788, -0.02972222222221896)
                
                >>> getSeparation("ngc1", "ngc2")
                (0.030089273732482536, 0.005291666666666788, -0.02972222222221896)
        
        With the optional parameter "style" set to "text", it returns a formatted string:
        
                >>> getSeparation("ngc1", "ngc2", style="text")
                '0° 1m 48.32s'
        
        If one of the objects is not found in the database it returns a ValueError:
        
                >>> getSeparation("ngc1a", "ngc2")
                Traceback (most recent call last):
                ...
                ValueError: Object named NGC0001A not found in the database.
        
        """
        if not isinstance(obj1, Dso):
                if isinstance(obj1, str):
                        obj1 = Dso(obj1)
                else:
                        raise TypeError('Wrong type obj1. Either a Dso or string type was expected.')
        if not isinstance(obj2, Dso):
                if isinstance(obj2, str):
                        obj2 = Dso(obj2)
                else:
                        raise TypeError('Wrong type obj2. Either a Dso or string type was expected.')
        
        coordsObj1 = obj1.getCoords()
        coordsObj2 = obj2.getCoords()
        
        a1 = radians(coordsObj1[0][0]*15 + coordsObj1[0][1]/4 + coordsObj1[0][2]/240)
        a2 = radians(coordsObj2[0][0]*15 + coordsObj2[0][1]/4 + coordsObj2[0][2]/240)
        d1 = radians(coordsObj1[1][1] + coordsObj1[1][2]/60 + coordsObj1[1][3]/3600)
        if coordsObj1[1][0] == "-":
                d1 = 0 - d1
        d2 = radians(coordsObj2[1][1] + coordsObj2[1][2]/60 + coordsObj2[1][3]/3600)
        if coordsObj2[1][0] == "-":
                d2 = 0 - d2
        
        separation = acos(sin(d1)*sin(d2) + cos(d1)*cos(d2)*cos(a1-a2))
        
        if style == "text":
                d = int(degrees(separation))
                md = abs(degrees(separation) - d) * 60
                m = int(md)
                s = (md - m) * 60
                return str(d) + "° " + str(m) + "m " + "{:.2f}".format(s) + "s"
        else:
                return degrees(separation), degrees(a2-a1), degrees(d2-d1)

def listObjects(**kwargs):
        """Query the database for DSObjects with specific parameters.
        
        :param optional string catalog: filter for catalog. [NGC|IC|M]
        :param optional string type: filter for object type. See OpenNGC types list.
        :param optional string constellation: filter for constellation (three letter latin form - e.g. "And")
        :param optional float minSize: filter for objects with MajAx >= minSize(arcmin)
        :param optional float maxSize: filter for objects with MajAx < maxSize(arcmin) OR MajAx not available
        :param optional float upToBMag: filter for objects with B-Mag brighter than value
        :param optional float upToVMag: filter for objects with V-Mag brighter than value
        :param optional bool withNames: filter for objects with common names
        :returns: [Dso,]
        
        This function returns a list of all DSObjects that match user defined parameters.
        If no argument is passed to the function, it returns all the objects from the database:
        
                >>> objectList = listObjects()
                >>> len(objectList)
                13954
        
        Filters are combined with "AND" in the query; only one value for filter is allowed:
        
                >>> objectList = listObjects(catalog="NGC", constellation="Boo")
                >>> len(objectList)
                281
        
        Duplicated objects are not resolved to main objects:
        
                >>> objectList = listObjects(type="Dup")
                >>> print(objectList[0])
                Name: IC0011        Type: Duplicated record               Constellation: Cas
        
        The maxSize filter will include objects with no size recorded in database:
        
                >>> objectList = listObjects(maxSize=0)
                >>> len(objectList)
                2015
        
        """
        cols = 'objects.name'
        tables = 'objects'
        
        if kwargs == {}:
                params = '1'
                return [Dso(str(item[0]), True) for item in _queryFetchMany(cols, tables, params)]
        
        paramslist = []
        if "catalog" in kwargs:
                if kwargs["catalog"].upper() == "NGC" or kwargs["catalog"].upper() == "IC":
                        paramslist.append('name LIKE "' + kwargs["catalog"].upper() + '%"')
                elif kwargs["catalog"].upper() == "M":
                        paramslist.append('messier != ""')
                else:
                        raise ValueError('Wrong value for catalog filter. [NGC|IC|M]')
        if "type" in kwargs:
                paramslist.append('type = "' + kwargs["type"] + '"')
        if "constellation" in kwargs:
                paramslist.append('const = "' + kwargs["constellation"].capitalize() + '"')
        if "minSize" in kwargs:
                paramslist.append('majax >= ' + str(kwargs["minSize"]))
        if "maxSize" in kwargs:
                paramslist.append('majax < ' + str(kwargs["maxSize"]) + ' OR majax = ""')
        if "upToBMag" in kwargs:
                paramslist.append('bmag <= ' + str(kwargs["upToBMag"]))
        if "upToVMag" in kwargs:
                paramslist.append('vmag <= ' + str(kwargs["upToVMag"]))
        if "withNames" in kwargs and kwargs["withNames"] == True:
                paramslist.append('commonnames != ""')
        
        if paramslist == []:
                raise ValueError("Wrong filter name.")
        
        params = " AND ".join(paramslist)
        return [Dso(item[0], True) for item in _queryFetchMany(cols, tables, params)]

def printDetails(dso):
        """Prints a detailed description of the object in a formatted output.
        
        :param dso: a Dso object or a string with the NGC/IC identifier
        :returns: string
        
        This function prints all the available details of the object, formatted in a way to fit 
        a 80cols display.
        The object can be identified by its name as a string or by a Dso type:
        
                >>> printDetails("ngc1")
                +-----------------------------------------------------------------------------+
                | Id: 5612      Name: NGC0001           Type: Galaxy                          |
                | R.A.: 00:07:15.84      Dec.: +27:42:29.1      Constellation: Peg            |
                +-----------------------------------------------------------------------------+
                | Major axis: 1.57'      Minor axis: 1.07'      Position angle: 112°          |
                | B-mag: 13.4    V-mag: N/A     J-mag: 10.78   H-mag: 10.02   K-mag: 9.76     |
                |                                                                             |
                | Surface brightness: 23.13     Hubble classification: Sb                     |
                +-----------------------------------------------------------------------------+
                | Other identifiers:                                                          |
                |    2MASX J00071582+2742291, IRAS 00047+2725, MCG +04-01-025, PGC 000564,    |
                |    UGC 00057                                                                |
                +-----------------------------------------------------------------------------+
        
        If the object is not found in the database it returns a ValueError:
        
                >>> printDetails("ngc1a")
                Traceback (most recent call last):
                ...
                ValueError: Object named NGC0001A not found in the database.
        
        """
        def _justifyText(text):
                """Prints the text on multiple lines if length is more than 73 chars.
                
                :param string text: text to be printed
                """
                chunks = text.split()
                line = []
                lineLength = 0
                for chunk in chunks:
                        lineLength += len(chunk) + 1
                        if lineLength <= 73:
                                line.append(chunk)
                                continue
                        else:
                                print('''{:5}{:73}{}'''.format("|", " ".join(line), "|"))
                                del line[:]
                                line.append(chunk)
                                lineLength = len(chunk) + 1
                print('''{:5}{:73}{}'''.format("|", " ".join(line), "|"))
        
        if not isinstance(dso, Dso):
                if isinstance(dso, str):
                        dso = Dso(dso)
                else:
                        raise TypeError('Wrong type as parameter. Either a Dso or string type was expected.')
        
        objType = dso.getType()
        print("+" + "-"*77 + "+")
        print('''{:2}{:14}{:24}{:38}{}'''.format("|", "Id: " + str(dso.getId()), "Name: " + dso.getName(),
                                                 "Type: " + objType, "|"))
        print('''{:2}{:23}{:23}{:30}{}'''.format("|", "R.A.: " + dso.getRA(), "Dec.: " + dso.getDec(),
                                                 "Constellation: " + dso.getConstellation(), "|"))
        
        identifiers = dso.getIdentifiers()
        if (identifiers[0] != None) or (identifiers[1] != None) or (identifiers[2] != None):
                print('''{:2}{:76}{}'''.format("|", "Also known as: ", "|"))
                knownAs = []
                if identifiers[0] != None:
                        knownAs.append(identifiers[0])
                if identifiers[1] != None:
                        knownAs.extend(identifiers[1])
                if identifiers[2] != None:
                        knownAs.extend(identifiers[2])
                _justifyText(", ".join(knownAs))
        
        if identifiers[3] != None:
                print('''{:2}{:76}{}'''.format("|", "Common names: ", "|"))
                _justifyText(", ".join(identifiers[3]))
        print("+" + "-"*77 + "+")
        
        dimensions = []
        for i in range(0,2):
                if dso.getDimensions()[i] is None:
                        dimensions.append("N/A")
                else:
                        dimensions.append(str(dso.getDimensions()[i]) + "'")
        if dso.getDimensions()[2] is None:
                dimensions.append("N/A")
        else:
                dimensions.append(str(dso.getDimensions()[2]) + "°")
        print('''{:2}{:23}{:23}{:30}{}'''.format("|", "Major axis: " + dimensions[0],
                                                 "Minor axis: " + dimensions[1],
                                                 "Position angle: " + dimensions[2], "|"))
        
        magnitudes = []
        for bandValue in dso.getMagnitudes():
                if bandValue is None:
                        magnitudes.append("N/A")
                else:
                        magnitudes.append(str(bandValue))
        print('''{:2}{:15}{:15}{:15}{:15}{:16}{}'''.format("|", "B-mag: " + magnitudes[0],
                                                           "V-mag: " + magnitudes[1], "J-mag: " + magnitudes[2],
                                                           "H-mag: " + magnitudes[3], "K-mag: " + magnitudes[4],
                                                           "|"))
        print("|" + " "*77 + "|")
        
        if objType == "Galaxy":
                print('''{:2}{:30}{:46}{}'''.format("|", "Surface brightness: " + str(dso.getSurfaceBrightness()),
                                                    "Hubble classification: " + dso.getHubble(), "|"))
        
        if objType == "Planetary Nebula":
                centralStar = dso.getCStarData()
                if centralStar[0] != None:
                        print('''{:2}{:76}{}'''.format("|", "Central star identifiers: ", "|"))
                        print('''{:5}{:73}{}'''.format("|", ", ".join(centralStar[0]), "|"))
                        print("|" + " "*77 + "|")
                cStarMagnitudes = []
                for i in range(1,4):
                        if centralStar[i] is None:
                                cStarMagnitudes.append("N/A")
                        else:
                                cStarMagnitudes.append(str(centralStar[i]))
                print('''{:2}{:76}{}'''.format("|", "Central star magnitudes: ", "|"))
                print('''{:5}{:24}{:24}{:25}{}'''.format("|", "U-mag: " + cStarMagnitudes[0],
                                           "B-mag: " + cStarMagnitudes[1],
                                           "V-mag: " + cStarMagnitudes[2], "|"))
        print("+" + "-"*77 + "+")
        
        if identifiers[4] != None:
                print('''{:2}{:76}{}'''.format("|", "Other identifiers: ", "|"))
                _justifyText(", ".join(identifiers[4]))
                print("+" + "-"*77 + "+")
        
        notes = dso.getNotes()
        if notes[0] != "":
                print('''{:2}{:76}{}'''.format("|", "NED notes: ", "|"))
                _justifyText(notes[0])
                print("+" + "-"*77 + "+")
        
        if notes[1] != "":
                print('''{:2}{:76}{}'''.format("|", "OpenNGC notes: ", "|"))
                _justifyText(notes[1])
                print("+" + "-"*77 + "+")

def searchAltId(name):
        """Search in the database using an alternative identifier.
        
        :param string name: alternative identifier to search for
        :returns: Dso object
        
        This function searches the name passed as parameter in the "alternative identifiers" field
        of the database.
        Currently it supports searching for identifiers from these catalogs: LBN, Messier, MWSC,
        PGC, UGC.
        The function return the founded Dso object.
        
                >>> searchAltId("pgc5") #doctest: +ELLIPSIS
                <__main__.Dso object at 0x...>
                
                >>> searchAltId("pc5")
                Traceback (most recent call last):
                ...
                ValueError: Wrong object name. Search can be performed for Messier, PGC, LBN, MWSC or UGC catalogs.
        
        If no object has been found, it returns a string:
        
                >>> searchAltId("pgc555")
                'Object not found.'
        
        """
        # Make sure user passed a string as parameter
        if not isinstance(name, str):
                raise TypeError('Wrong type as parameter. A string type was expected.')
        
        # Extract catalog name and object number to make sure we search the name in correct form
        nameParts = re.match(r'(LBN|M|MWSC|PGC|UGC)\s?(\d+)',name.upper())
        if nameParts is None :
                raise ValueError('Wrong object name. Search can be performed for Messier, PGC, LBN, MWSC or UGC catalogs.')
        
        selectWhat = 'objects.name'
        fromWhere = 'objects'
        if nameParts[1] == 'M':
                # M102 == M101
                if nameParts[2] == "102":
                        constraint = 'messier="101"'
                else:
                        constraint = 'messier="' + nameParts[2] + '"'
        elif nameParts[1] == 'PGC': # 6 digits format
                constraint = 'identifiers LIKE "%PGC ' + "{:0>6}".format(nameParts[2]) + '%"'
        elif nameParts[1] == 'UGC': # 5 digits format
                constraint = 'identifiers LIKE "%UGC ' + "{:0>5}".format(nameParts[2]) + '%"'
        elif nameParts[1] == 'MWSC': # 4 digits format
                constraint = 'identifiers LIKE "%MWSC ' + "{:0>4}".format(nameParts[2]) + '%"'
        elif nameParts[1] == 'LBN': # 3 digits format
                constraint = 'identifiers LIKE "%LBN ' + "{:0>3}".format(nameParts[2]) + '%"'
        objectData = _queryFetchOne(selectWhat, fromWhere, constraint)
        
        if objectData is not None:
                return Dso(objectData[0])
        else:
                return "Object not found."

def stats():
        try:
                db = sqlite3.connect(DBPATH)
                cursor = db.cursor()
                
                cursor.execute('''SELECT objTypes.typedesc, count(*)
                        FROM objects JOIN objTypes ON objects.type = objTypes.type
                        GROUP BY objects.type''')
                typesStats = cursor.fetchall()
                
        except Exception as e:
                db.rollback()
                raise e
        
        finally:
                db.close()
        
        totalObjects = sum(objType[1] for objType in typesStats)
        
        return __version__, DBDATE, totalObjects, typesStats

if __name__ == "__main__":
    import doctest
    doctest.testmod()

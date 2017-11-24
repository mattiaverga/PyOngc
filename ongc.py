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

"""Provides classes and functions to access OpenNGC database."""

from math import acos, cos, degrees, radians, sin
import re
import sqlite3
import sys


class Dso(object):
        """Defines a single Deep Sky Object from ONGC database."""
        
        def __init__(self, name):
                """Object constructor.
                
                :param string name: identifier of the NGC or IC object
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
                
                objectData = _queryObject(objectname)
                
                # If object is a duplicate then return the main object
                if objectData[1] == "Dup":
                        if objectData[20] != "":
                                objectname = "NGC" + str(objectData[20])
                        else:
                                objectname = "IC" + str(objectData[21])
                        objectData = _queryObject(objectname)
                
                # Assign object properties
                self._id = objectData[0]
                self._name = objectname
                self._type = str(objectData[2])
                self._ra = str(objectData[3])
                self._dec = str(objectData[4])
                self._const = str(objectData[5])
                
                # These properties may be empty
                self._majax = _assignValue(objectData[6])
                self._minax = _assignValue(objectData[7])
                self._pa = _assignValue(objectData[8])
                self._bmag = _assignValue(objectData[9])
                self._vmag = _assignValue(objectData[10])
                self._jmag = _assignValue(objectData[11])
                self._hmag = _assignValue(objectData[12])
                self._kmag = _assignValue(objectData[13])
                self._sbrightn = _assignValue(objectData[14])
                self._hubble = str(objectData[15])
                self._cstarumag = _assignValue(objectData[16])
                self._cstarbmag = _assignValue(objectData[17])
                self._cstarvmag = _assignValue(objectData[18])
                self._messier = str(objectData[19])
                self._ngc = str(objectData[20])
                self._ic = str(objectData[21])
                self._cstarnames = str(objectData[22])
                self._identifiers = str(objectData[23])
                self._commonnames = str(objectData[24])
                self._nednotes = str(objectData[25])
                self._ongcnotes = str(objectData[26])
        
        def __str__(self):
                """Returns basic data of the object as a formatted string."""
                
                return ('''{:20}{:38}{}'''
                        .format("Name: " + self._name, "Type: " + self._type, "Constellation: " + self._const)
                )
                
        def getConstellation(self):
                """Returns the constellation where the object is located (string)."""
                
                return self._const
        
        def getCoords(self):
                """Returns the coordinates of the object in J2000 Epoch.
                
                The value is espressed as a tuple of tuples 
                with numerical values espressed as int or float:
                ((HH,MM,SS.SS),(DD,MM,SS.SS))
                """
                
                ra = self._ra.split(":")
                dec = self._dec.split(":")
                raTuple = (int(ra[0]), int(ra[1]), float(ra[2]))
                decTuple = (int(dec[0]), int(dec[1]), float(dec[2]))
                return raTuple, decTuple
        
        def getCStarData(self):
                """Returns a tuple with data about central star of planetary nebulaes.
                
                (cstar identifiers, cstar UMag, cstar BMag, cstar VMag)
                cstar identifiers: list of names.
                cstar UMag, cstar BMag, cstar VMag: floats or None.
                """
                
                if self._cstarnames != "":
                        identifiers = list(map(str.strip, self._cstarnames.split(",")))
                else:
                        identifiers = None
                        
                return identifiers, self._cstarumag, self._cstarbmag, self._cstarvmag
        
        def getDec(self):
                """Returns the Declination in J2000 Epoch (string +/-DD:MM:SS.SS)."""
                
                return self._dec
        
        def getDimensions(self):
                """Returns a tuple with object axes dimensions (float) and position angle (int).
                
                Where values are not available a None type is returned.
                (MajAx, MinAx, P.A.)
                """
                
                return self._majax, self._minax, self._pa
        
        def getHubble(self):
                """Returns the Hubble classification of the object (string)."""
                
                return self._hubble
        
        def getId(self):
                """Returns the database Id of the object (int)."""
                
                return self._id
        
        def getIdentifiers(self):
                """Returns a tuple of alternative identifiers of the object.
                
                (Messier, NGC, IC, common names, other)
                Messier: string or None
                NGC, IC, common names, other: list of strings or None
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
                
                Where values are not available a None type is returned.
                (Bmag, Vmag, Jmag, Hmag, Kmag)
                """
                
                return self._bmag, self._vmag, self._jmag, self._hmag, self._kmag
        
        def getName(self):
                """Returns the main identifier of the object (string)."""
                
                return self._name
        
        def getNotes(self):
                """Returns notes from NED and from ONGC author (tuple of strings).
                
                (nednotes, ongcnotes)
                """
                
                return self._nednotes, self._ongcnotes
        
        def getSurfaceBrightness(self):
                """Returns the surface brightness value of the object (float or None)."""
                
                return self._sbrightn
        
        def getType(self):
                """Returns the type of the object (string)."""
                
                return self._type
        
        def getRA(self):
                """Returns the Right Ascension in J2000 Epoch (string HH:MM:SS.SS)."""
                
                return self._ra
        
        def xephemFormat(self):
                """Returns object data in Xephem format."""
                
                line = []
                #Field 1: names
                names = []
                names.append(self.getName())
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
                for value in (self.getDimensions()[0],self.getDimensions()[0]):
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


def _assignValue(value):
        """ Returns value or None type if value is an empty string."""
        
        if value == "":
                return None
        else:
                return value

def _queryObject(name):
        """Retrieve object data from database.
        
        :param string name: identifier of the NGC or IC object
        """
        
        # Make sure user passed a string as parameter
        if not isinstance(name, str):
                raise TypeError('Wrong type as parameter. A string type was expected.')
        
        try:
                db = sqlite3.connect('ongc.db')
                cursor = db.cursor()
                
                cursor.execute('''SELECT objects.id, objects.type, objTypes.typedesc, ra, dec, const, majax, minax, 
                        pa, bmag, vmag, jmag,hmag, kmag, sbrightn, hubble, cstarumag, cstarbmag, cstarvmag, messier, 
                        ngc, ic, cstarnames,identifiers, commonnames, nednotes, ongcnotes 
                        FROM objects JOIN objTypes ON objects.type = objTypes.type 
                        WHERE name=?
                        ''',(name,))
                objectData = cursor.fetchone()
                
        except Exception as e:
                db.rollback()
                raise e
        
        finally:
                db.close()
        
        return objectData

def getSeparation(obj1, obj2, style="raw"):
        """Finds the apparent angular separation between two objects.
        
        :param obj1, obj2: two NGC/IC objects or string identifiers
        :param opt string style: use "text" to return a string with degrees, minutes and seconds
        :returns: (int: angular separation, string: difference in A.R, string: difference in Dec)
        :returns: string DD° MMm SS.SSs
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
        d1 = radians(coordsObj1[1][0] + coordsObj1[1][1]/60 + coordsObj1[1][2]/3600)
        d2 = radians(coordsObj2[1][0] + coordsObj2[1][1]/60 + coordsObj2[1][2]/3600)
        
        separation = acos(sin(d1)*sin(d2) + cos(d1)*cos(d2)*cos(a1-a2))
        
        if style == "text":
                d = int(degrees(separation))
                md = abs(degrees(separation) - d) * 60
                m = int(md)
                s = (md - m) * 60
                return str(d) + "° " + str(m) + "m " + "{:.2f}".format(s) + "s"
        else:
                return degrees(separation), degrees(a2-a1), degrees(d2-d1)

def printDetails(dso):
        """Prints a detailed description of the object in a formatted output.
        
        :param dso: a Dso object or a string with the NGC/IC identifier
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

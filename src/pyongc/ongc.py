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
    * DsoEncoder: a custom json.dumps serializer for Dso class.

Methods provided:
    * getNeighbors: Find all neighbors of an object within a user selected range.
    * getSeparation: Calculate the apparent angular separation between two objects.
    * listObjects: Query DB for DSObjects with specific parameters.
    * nearby: Search for objects around given coordinates and range.
    * printDetails: Prints a detailed description of the object in a formatted output.
"""

from functools import cached_property
from typing import Generator, List, Tuple, Optional, Union
import json
import numpy as np
import re
import sqlite3

from pyongc import __version__ as version, DBDATE, DBPATH
from pyongc.exceptions import InvalidCoordinates, ObjectNotFound, UnknownIdentifier

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


class Dso(object):
    """Describes a Deep Sky Object from ONGC database.

    Each object of this class has the following read only properties:

    * cstar_data: The data about central star of planetary nebulaes.
    * constellation: The constellation where the object is located.
    * coords: Object coordinates in HMS and DMS as numpy array or None.
    * dec: Object Declination in a easy to read format as string.
    * dimensions: Object axes dimensions and position angle.
    * hubble: The Hubble classification of a galaxy.
    * id: The internal database Id of the object.
    * identifiers: All the alternative identifiers of the object.
    * magnitudes: Object magnitudes.
    * name: The main identifier of the object.
    * notes: Notes from NED and from ONGC.
    * notngc: A flag which marks objects not being in the NGC or IC catalog
    * parallax: Parallax, expressed in milliarcseconds.
    * pm_dec: Proper apparent motion in Dec, expressed in milliarcseconds/year.
    * pm_ra: Proper apparent motion in RA, expressed in milliarcseconds/year.
    * ra: Object Right Ascension in a easy to read format as string.
    * rad_coords: Object coordinates in radians as numpy array or None.
    * radvel: Radial velocity (heliocentric), expressed in km/s.
    * redshift: Redshift value (heliocentric).
    * surface_brightness: The surface brightness value of a galaxy or None.
    * type: Object type.

    The class also provides the following methods:

    * __init__: Object constructor.
    * __str__: Returns a basic description of the object.
    * xephemFormat: Returns object data in Xephem format.

    """

    def __init__(self, name: str, returndup: bool = False):
        """Object constructor.

        Args:
            name: Object identifier (ex.: 'NGC1', 'M15').
            returndup: If set to True, don't resolve Dup objects. Default is False.

        Raises:
            TypeError: If the object identifier is not a string.
            pyongc.ObjectNotFound: If the object identifier is not found in the database.
        """
        # Make sure user passed a string as parameter
        if not isinstance(name, str):
            raise TypeError('Wrong type as parameter. A string type was expected.')

        catalog, objectname = _recognize_name(name.upper())

        cols = ('objects.id, objects.name, objects.type, objTypes.typedesc, ra, dec, const, '
                'majax, minax, pa, bmag, vmag, jmag, hmag, kmag, sbrightn, hubble, parallax, '
                'pmra, pmdec, radvel, redshift, cstarumag, cstarbmag, cstarvmag, messier, '
                'ngc, ic, cstarnames, identifiers, commonnames, nednotes, ongcnotes, notngc')
        tables = ('objects JOIN objTypes ON objects.type = objTypes.type '
                  'JOIN objIdentifiers ON objects.name = objIdentifiers.name')
        if catalog == 'Messier':
            params = f'messier="{objectname}"'
        else:
            params = f'objIdentifiers.identifier="{objectname}"'
        objectData = _queryFetchOne(cols, tables, params)

        if objectData is None:
            raise ObjectNotFound(objectname)

        # If object is a duplicate then return the main object
        if objectData[2] == "Dup" and not returndup:
            if objectData[26] != "":
                objectname = f'NGC{objectData[26]}'
            else:
                objectname = f'IC{objectData[27]}'
            params = f'objIdentifiers.identifier="{objectname}"'
            objectData = _queryFetchOne(cols, tables, params)

        # Assign object properties
        self._id = objectData[0]
        self._name = objectData[1]
        self._type = objectData[3]
        self._ra = objectData[4]
        self._dec = objectData[5]
        self._const = objectData[6]
        self._notngc = objectData[33]

        # These properties may be empty
        self._majax = objectData[7]
        self._minax = objectData[8]
        self._pa = objectData[9]
        self._bmag = objectData[10]
        self._vmag = objectData[11]
        self._jmag = objectData[12]
        self._hmag = objectData[13]
        self._kmag = objectData[14]
        self._sbrightn = objectData[15]
        self._hubble = objectData[16]
        self._parallax = objectData[17]
        self._pmra = objectData[18]
        self._pmdec = objectData[19]
        self._radvel = objectData[20]
        self._redshift = objectData[21]
        self._cstarumag = objectData[22]
        self._cstarbmag = objectData[23]
        self._cstarvmag = objectData[24]
        self._messier = objectData[25]
        self._ngc = objectData[26]
        self._ic = objectData[27]
        self._cstarnames = objectData[28]
        self._identifiers = objectData[29]
        self._commonnames = objectData[30]
        self._nednotes = objectData[31]
        self._ongcnotes = objectData[32]

    def __str__(self) -> str:
        """Returns a basic description of the object.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1")
                >>> print(s)
                NGC0001, Galaxy in Peg

        """
        return f'{self._name}, {self._type} in {self._const}'

    @cached_property
    def cstar_data(self) -> Optional[Tuple[Optional[List[str]], Optional[float],
                                           Optional[float], Optional[float]]]:
        """Data about central star of planetary nebulaes.

        If the DSO object is a Planetary Nebulae, this method will return a tuple with
        the central star identifiers and its magnitudes in U-B-V bands:

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1535")
                >>> s.cstar_data
                (['BD -13 842', 'HD 26847'], None, 12.19, 12.18)

        If the object is not a PN it returns None:

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1")
                >>> s.cstar_data is None
                True

        Returns:
            `(['cstar identifiers'], cstar UMag, cstar BMag, cstar VMag)`

        """
        if self._type != 'Planetary Nebula':
            return None

        if self._cstarnames != "":
            identifiers = list(map(str.strip, self._cstarnames.split(",")))
        else:
            identifiers = None

        return identifiers, self._cstarumag, self._cstarbmag, self._cstarvmag

    @cached_property
    def constellation(self) -> str:
        """The constellation where the object is located.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1")
                >>> s.constellation
                'Peg'

        Returns:
            Name of the constellation in IAU 3-letter form.

        """
        return self._const

    @cached_property
    def coords(self) -> Optional[np.ndarray]:
        """Returns object coordinates in HMS and DMS as numpy array or None.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1")
                >>> s.coords
                array([[ 0.  ,  7.  , 15.84],
                       [27.  , 42.  , 29.1 ]])

        Returns:
            A numpy array of shape (2, 3) with R.A. and Declination
            values expressed in HMS and DMS.

        """
        if self._ra is None or self._dec is None:
            return None

        ra = np.empty(3)
        ra[0] = np.trunc(np.rad2deg(self._ra) / 15)
        ms = ((np.rad2deg(self._ra) / 15) - ra[0]) * 60
        ra[1] = np.trunc(ms)
        ra[2] = (ms - ra[1]) * 60

        dec = np.empty(3)
        dec[0] = np.trunc(np.rad2deg(np.abs(self._dec)))
        ms = (np.rad2deg(np.abs(self._dec)) - dec[0]) * 60
        dec[1] = np.trunc(ms)
        dec[2] = (ms - dec[1]) * 60
        dec[0] = dec[0] * -1 if np.signbit(self._dec) else dec[0]
        return np.array([ra, dec, ])

    @cached_property
    def dec(self) -> str:
        """Object Declination in a easy to read format as string.

        If you need the raw data to use in calculations use `coords` or `rad_coords` properties.

            >>> from pyongc.ongc import Dso
            >>> s = Dso("ngc1")
            >>> s.dec
            '+27:42:29.1'

            >>> from pyongc.ongc import Dso
            >>> s = Dso("ic1064")
            >>> s.dec
            'N/A'

        Returns:
            string: `'+/-DD:MM:SS.s'` or `'N/A'` if the object has no coordinates.

        """
        if self.coords is not None:
            return '{:+03.0f}:{:02.0f}:{:04.1f}'.format(*self.coords[1])
        else:
            return 'N/A'

    @cached_property
    def dimensions(self) -> Tuple[Optional[float], Optional[float], Optional[int]]:
        """Object axes dimensions and position angle.

        Where a value is not available a None type is returned.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1")
                >>> s.dimensions
                (1.57, 1.07, 112)

        Returns:
            (MajAx, MinAx, P.A.)

        """
        return self._majax, self._minax, self._pa

    @cached_property
    def hubble(self) -> str:
        """The Hubble classification of a galaxy.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1")
                >>> s.hubble
                'Sb'

        Returns:
            string: The Hubble classification code of a galaxy or empty string.

        """
        return self._hubble

    @cached_property
    def id(self) -> int:
        """The internal database Id of the object.

        Returns:
            The internal database id of the object.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1")
                >>> s.id
                5596

        """
        return self._id

    @cached_property
    def identifiers(self) -> Tuple[Optional[str], Optional[List[str]], Optional[List[str]],
                                   Optional[List[str]], Optional[List[str]]]:
        """All the alternative identifiers of the object.

        The tuple returned by this method will list all the alternative identifiers
        associated to the object.
        The first element of the tuple will be a string with the Messier name or None.
        The other fields will be lists of cross identifiers or None.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1976")
                >>> s.identifiers
                ('M042', None, None, ['Great Orion Nebula', 'Orion Nebula'], \
['LBN 974', 'MWSC 0582'])

                >>> from pyongc.ongc import Dso
                >>> s = Dso("mel22")
                >>> s.identifiers
                ('M045', None, None, ['Pleiades'], ['MWSC 0305'])

        Returns:
            `('Messier', ['NGC'], ['IC'], ['common names'], ['other'])`

        """
        if self._messier == "":
            messier = None
        else:
            messier = f'M{self._messier}'

        if self._ngc == "":
            ngc = None
        else:
            ngc = list(map(str.strip, self._ngc.split(",")))
            ngc = list(map(lambda number: f'NGC{number}', ngc))

        if self._ic == "":
            ic = None
        else:
            ic = list(map(str.strip, self._ic.split(",")))
            ic = list(map(lambda number: f'IC{number}', ic))

        if self._commonnames == "":
            commonNames = None
        else:
            commonNames = list(map(str.strip, self._commonnames.split(",")))

        if self._identifiers == "":
            other = None
        else:
            other = list(map(str.strip, self._identifiers.split(",")))

        return messier, ngc, ic, commonNames, other

    @cached_property
    def magnitudes(self) -> Tuple[Optional[float], Optional[float], Optional[float],
                                  Optional[float], Optional[float]]:
        """Returns object magnitudes.

        Where a value is not available a None type is returned

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1")
                >>> s.magnitudes
                (13.69, 12.93, 10.78, 10.02, 9.76)

        Returns:
            `(Bmag, Vmag, Jmag, Hmag, Kmag)`

        """
        return self._bmag, self._vmag, self._jmag, self._hmag, self._kmag

    @cached_property
    def name(self) -> str:
        """The main identifier of the object.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("m45")
                >>> s.name
                'Mel022'

        Returns:
            The main identifier of the object, as listed in ONGC database
            or its addendum.

        """
        return self._name

    @cached_property
    def notes(self) -> Tuple[str, str]:
        """Returns notes from NED and from ONGC.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc6543")
                >>> s.notes
                ('Additional radio sources may contribute to the WMAP flux.', \
'The fainter outer shell has a diameter of 5.5 arcmin ca.')

        Returns:
            `('nednotes', 'ongcnotes')`

        """
        return self._nednotes, self._ongcnotes

    @cached_property
    def notngc(self) -> bool:
        """A flag which marks objects not being in the NGC or IC catalog.

        The OpenNGC database also includes objects which aren't part of the NGC or IC catalog.
        For example, objects from the 'addendum' are objects which can interest amateur
        astronomers, thus we're including in our listings.
        The `notngc` property is a convenient flag to mark these extra objects.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("m45")
                >>> s.notngc
                True

        """
        return bool(self._notngc)

    @cached_property
    def parallax(self) -> Optional[float]:
        """Object's parallax.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("m13")
                >>> s.parallax
                0.0813

        Returns:
            Object's parallax expressed in milliarcseconds or None.

        """
        return self._parallax

    @cached_property
    def pm_dec(self) -> Optional[float]:
        """Proper apparent motion in Dec, expressed in milliarcseconds/year.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("m13")
                >>> s.pm_dec
                -2.56

        Returns:
            Object's apparent motion in Dec or None.

        """
        return self._pmdec

    @cached_property
    def pm_ra(self) -> Optional[float]:
        """Proper apparent motion in RA, expressed in milliarcseconds/year.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("m13")
                >>> s.pm_ra
                -3.18

        Returns:
            Object's apparent motion in RA or None.

        """
        return self._pmra

    @cached_property
    def ra(self) -> str:
        """Object Right Ascension in a easy to read format as string.

        If you need the raw data to use in calculations use `coords` or `rad_coords` properties.

            >>> from pyongc.ongc import Dso
            >>> s = Dso("ngc1")
            >>> s.ra
            '00:07:15.84'

            >>> from pyongc.ongc import Dso
            >>> s = Dso("ic1064")
            >>> s.ra
            'N/A'

        Returns:
            string: `'HH:MM:SS.ss'` or `'N/A'` if the object has no coordinates.

        """
        if self.coords is not None:
            return '{:02.0f}:{:02.0f}:{:05.2f}'.format(*self.coords[0])
        else:
            return 'N/A'

    @cached_property
    def rad_coords(self) -> Optional[np.ndarray]:
        """Returns object coordinates in radians as numpy array or None.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1")
                >>> s.rad_coords
                array([0.03169518, 0.48359728])

        Returns:
            A numpy array of shape (2,) with R.A. and Declination
            values expressed in radians.

        """
        if self._ra is None or self._dec is None:
            return None

        return np.array([self._ra, self._dec, ])

    @cached_property
    def radvel(self) -> Optional[float]:
        """Object's radial velocity.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("m13")
                >>> s.radvel
                -244

        Returns:
            Object's radial velocity (heliocentric) expressed in km/s or None.

        """
        return self._radvel

    @cached_property
    def redshift(self) -> Optional[float]:
        """Object's redshift value.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("m13")
                >>> s.redshift
                -0.000815

        Returns:
            Object's redshift value or None.

        """
        return self._redshift

    @cached_property
    def surface_brightness(self) -> Optional[float]:
        """The surface brightness value of a galaxy.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1")
                >>> s.surface_brightness
                23.13

        Returns:
            float: Object's surface brightness

        """
        return self._sbrightn

    @cached_property
    def type(self) -> str:
        """Object type.

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1")
                >>> s.type
                'Galaxy'

        Returns:
            string: Object type

        """
        return self._type

    def to_json(self) -> str:
        """Returns object data in JSON format."""
        return json.dumps(self, cls=DsoEncoder)

    def xephemFormat(self) -> str:
        """Returns object data in Xephem format.

        This function will produce a string containing information about the object
        suitable to be imported in other software that accept Xephem format
        (for example: PyEphem).

                >>> from pyongc.ongc import Dso
                >>> s = Dso("ngc1")
                >>> s.xephemFormat()
                'NGC0001,f|G,00:07:15.84,+27:42:29.1,13.69,,94.20|64.20|112'

        Returns:
            Xephem format object description

        """
        line = []
        # Field 1: names
        names = [self.name]
        identifiers = self.identifiers
        if identifiers[0] is not None:
            names.append(identifiers[0])
        for i in range(1, 4):
            if identifiers[i] is not None:
                names.extend(identifiers[i])
        line.append("|".join(names))

        # Field 2: type designation
        objType = self.type
        if objType in ("Galaxy Pair", "Galaxy Triplet", "Group of galaxies"):
            line.append("f|A")
        elif objType == "Globular Cluster":
            line.append("f|C")
        elif objType == "Double star":
            line.append("f|D")
        elif objType in ("HII Ionized region", "Nebula"):
            line.append("f|F")
        elif objType == "Galaxy":
            if self.hubble.startswith("S"):
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

        # Field 3: Right Ascension
        line.append(self.ra)

        # Field 4: Declination
        line.append(self.dec)

        # Field 5: Magnitude
        # We use the first available magnitude in the sequence b,v,j,h,k
        for mag in self.magnitudes:
            if mag is not None:
                line.append(str(mag))
                break

        # Field 6: optional Epoch, we let it empty
        line.append("")

        # Field 7: Dimensions
        dimensions = []
        # Xephem format wants axes espressed in arcsec, we have arcmin
        for value in (self._majax, self._minax):
            dimensions.append(f'{value*60:.2f}') if value is not None else dimensions.append("")
        for value in (self._pa, ):
            dimensions.append(str(value)) if value is not None else dimensions.append("")
        line.append("|".join(dimensions))

        return ",".join(line)


class DsoEncoder(json.JSONEncoder):
    """A custom json.dumps serializer for Dso class."""
    def default(self, obj: Dso) -> dict:
        """A custom json.dumps serializer for Dso class.

        Args:
            obj: the Dso object to encode.
        """
        if isinstance(obj, Dso):
            obj_description = {'id': obj.id,
                               'name': obj.name,
                               'type': obj.type,
                               'coordinates': {'right ascension': obj.ra,
                                               'declination': obj.dec,
                                               },
                               'constellation': obj.constellation,
                               'dimensions': {'major axis': obj.dimensions[0],
                                              'minor axis': obj.dimensions[1],
                                              'position angle': obj.dimensions[2],
                                              },
                               'magnitudes': {'B-band': obj.magnitudes[0],
                                              'V-band': obj.magnitudes[1],
                                              'J-band': obj.magnitudes[2],
                                              'H-band': obj.magnitudes[3],
                                              'K-band': obj.magnitudes[4],
                                              },
                               'other identifiers': {'messier': obj.identifiers[0],
                                                     'NGC': obj.identifiers[1],
                                                     'IC': obj.identifiers[2],
                                                     'common names': obj.identifiers[3],
                                                     'other catalogs': obj.identifiers[4],
                                                     },
                               'notes': {'NED notes': obj.notes[0],
                                         'OpenNGC notes': obj.notes[1]},
                               }

            if obj.rad_coords is not None:
                obj_description['coordinates']['radians coords'] = (obj.rad_coords[0],
                                                                    obj.rad_coords[1]
                                                                    )
            else:
                obj_description['coordinates']['radians coords'] = None

            if obj.type == 'Galaxy':
                obj_description['surface brightness'] = obj.surface_brightness
                obj_description['hubble classification'] = obj.hubble
            elif obj.type == 'Planetary Nebula':
                obj_description['central star data'] = {
                    'identifiers': obj.cstar_data[0],
                    'magnitudes': {'U-band': obj.cstar_data[1],
                                   'B-band': obj.cstar_data[1],
                                   'V-band': obj.cstar_data[1],
                                   },
                    }
            return obj_description
        else:
            return super().default(obj)


def _distance(coords1: np.ndarray, coords2: np.ndarray) -> Tuple[float, float, float]:
    """Calculate distance between two points in the sky.

    With p1 = '01:00:00 +15:30:00' and p2 = '01:30:00 +10:30:00':

            >>> import numpy as np
            >>> p1 = np.array([0.26179939, 0.27052603])
            >>> p2 = np.array([0.39269908, 0.18325957])
            >>> _distance(p1, p2)
            (8.852139937970884, 7.499999776570824, -4.999999851047216)

    Args:
        coords1: R.A. and Dec expressed in radians of the first point as
            numpy array with shape(2,)
        coords2: R.A. and Dec expressed in radians of the second point as
            numpy array with shape(2,)

    Returns:
        `(angular separation, difference in A.R, difference in Dec)`

        This function will return three float values, which are the apparent total
        angular separation between the two objects, the difference in Right Ascension and the
        difference in Declination.

        All values are expressed in degrees.

    """
    a1 = coords1[0]
    a2 = coords2[0]
    d1 = coords1[1]
    d2 = coords2[1]

    # separation = np.arccos(np.sin(d1)*np.sin(d2) + np.cos(d1)*np.cos(d2)*np.cos(a1-a2))
    # Better precision formula
    # see http://aa.quae.nl/en/reken/afstanden.html
    separation = 2*np.arcsin(np.sqrt(np.sin((d2-d1)/2)**2 +
                                     np.cos(d1)*np.cos(d2)*np.sin((a2-a1)/2)**2))

    return np.degrees(separation), np.degrees(a2-a1), np.degrees(d2-d1)


def _limiting_coords(coords: np.ndarray, radius: int) -> str:
    """Write query filters for limiting search to specific area of the sky.

    This is a quick method to exclude objects farther than a specified distance
    from the starting point, but it's not meant to be precise.

            >>> from pyongc.ongc import Dso, _limiting_coords
            >>> start = Dso('ngc1').coords
            >>> _limiting_coords(start, 2)
            ' AND (ra <= 0.06660176425610362 OR ra >= 6.279973901355917) AND \
(dec BETWEEN 0.44869069854374555 AND 0.5185038686235187)'

    Args:
        coords: R.A. and Dec of the starting point in the sky.

            It can be expressed as a numpy array of H:M:S/D:M:S

            `array([[HH., MM., SS.ss],[DD., MM., SS.ss]])`

            or as numpy array of radians

            `array([RA, Dec])`
        radius: radius of the search in degrees

    Returns:
        Parameters to be added to query

    """
    if coords.shape == (2, 3):
        rad_coords = np.empty(2)
        rad_coords[0] = np.radians(np.sum(coords[0] * [15, 1/4, 1/240]))
        if np.signbit(coords[1][0]):
            rad_coords[1] = np.radians(np.sum(coords[1] * [1, -1/60, -1/3600]))
        else:
            rad_coords[1] = np.radians(np.sum(coords[1] * [1, 1/60, 1/3600]))
    else:
        rad_coords = coords

    radius_rad = np.radians(radius)
    ra_lower_limit = rad_coords[0] - radius_rad
    ra_upper_limit = rad_coords[0] + radius_rad
    if ra_lower_limit < 0:
        ra_lower_limit += 2 * np.pi
        params = f' AND (ra <= {ra_upper_limit} OR ra >= {ra_lower_limit})'
    elif ra_upper_limit > 2 * np.pi:
        ra_upper_limit -= 2 * np.pi
        params = f' AND (ra <= {ra_upper_limit} OR ra >= {ra_lower_limit})'
    else:
        params = f' AND (ra BETWEEN {ra_lower_limit} AND {ra_upper_limit})'

    dec_lower_limit = rad_coords[1] - radius_rad
    if dec_lower_limit < -1/2 * np.pi:
        dec_lower_limit = -1/2 * np.pi
    dec_upper_limit = rad_coords[1] + radius_rad
    if dec_upper_limit > 1/2 * np.pi:
        dec_upper_limit = 1/2 * np.pi

    params += f' AND (dec BETWEEN {dec_lower_limit} AND {dec_upper_limit})'
    return params


def _queryFetchOne(cols: str, tables: str, params: str) -> tuple:
    """Search one row in database.

    Be sure to use a WHERE clause which is very specific, otherwise the query
    will return the first row that matches.

            >>> from pyongc.ongc import _queryFetchOne
            >>> cols = 'type'
            >>> tables = 'objects'
            >>> params = 'name="NGC0001"'
            >>> _queryFetchOne(cols, tables, params)
            ('G',)

    Args:
        cols: the `SELECT` field of the query
        tables: the `FROM` field of the query
        params: the `WHERE` field of the query

    Returns:
        Selected row data from database

    """
    try:
        db = sqlite3.connect(f'file:{DBPATH}?mode=ro', uri=True)
    except sqlite3.Error:
        raise OSError(f'There was a problem accessing database file at {DBPATH}')

    try:
        cursor = db.cursor()
        cursor.execute(f'SELECT {cols} '
                       f'FROM {tables} '
                       f'WHERE {params}'
                       )
        objectData = cursor.fetchone()
    except Exception as err:  # pragma: no cover
        raise err
    finally:
        db.close()

    return objectData


def _queryFetchMany(cols: str, tables: str, params: str,
                    order: str = '') -> Generator[tuple, None, None]:
    """Search many rows in database.

            >>> from pyongc.ongc import _queryFetchMany
            >>> cols = 'name'
            >>> tables = 'objects'
            >>> params = 'type="G"'
            >>> _queryFetchMany(cols, tables, params) #doctest: +ELLIPSIS
            <generator object _queryFetchMany at 0x...>

    Args:
        cols: the `SELECT` field of the query
        tables: the `FROM` field of the query
        params: the `WHERE` field of the query
        order: the `ORDER` clause of the query

    Yields:
        Selected row data from database

    """
    try:
        db = sqlite3.connect(f'file:{DBPATH}?mode=ro', uri=True)
    except sqlite3.Error:
        raise OSError(f'There was a problem accessing database file at {DBPATH}')

    try:
        cursor = db.cursor()

        cursor.execute(f'SELECT {cols} '
                       f'FROM {tables} '
                       f'WHERE {params}'
                       f'{" ORDER BY " + order if order != "" else ""}'
                       )
        while True:
            objectList = cursor.fetchmany()
            if objectList == []:
                break
            yield objectList[0]
    except Exception as err:  # pragma: no cover
        raise err
    finally:
        db.close()


def _recognize_name(text: str) -> Tuple[str, str]:
    """Recognize catalog and object id.

            >>> from pyongc.ongc import _recognize_name
            >>> _recognize_name('NGC1')
            ('NGC|IC', 'NGC0001')

    Args:
        text: the object name in input. Must be uppercase.

    Returns:
        `('catalog name', 'object name')`

    Raises:
        UnknownIdentifier: If the text cannot be recognized as a valid object name.

    """
    for cat, pat in PATTERNS.items():
        name_parts = re.match(pat, text)
        if name_parts is not None:
            if cat == 'NGC|IC' and name_parts.group(3) is not None:
                # User searches for a NGC/IC sub-object
                if name_parts.group(4) is not None:
                    # User searches for a NED suffixed component
                    objectname = f'{name_parts.group(1).strip()}' \
                                 f'{name_parts.group(2):0>4}' \
                                 f' {name_parts.group(4)}' \
                                 f'{name_parts.group(5):0>2}'
                else:
                    # User searches for a letter suffixed component
                    objectname = f'{name_parts.group(1).strip()}' \
                                 f'{name_parts.group(2):0>4}' \
                                 f'{name_parts.group(3).strip()}'
            elif cat in ('NGC|IC', 'MWSC'):
                objectname = f'{name_parts.group(1).strip()}{name_parts.group(2):0>4}'
            elif cat == 'ESO':
                objectname = f'{name_parts.group(1).strip()}{name_parts.group(2):0>3}-' \
                             f'{name_parts.group(3):0>3}'
            elif cat == 'Harvard':
                objectname = f'{name_parts.group(1).strip()}{name_parts.group(2):0>2}'
            elif cat == 'Messier':
                # We need to return only the numeric part of the name
                objectname = ('101' if name_parts.group(2) == '102'
                              else f'{name_parts.group(2):0>3}'
                              )
            elif cat == 'UGC':
                objectname = f'{name_parts.group(1).strip()}{name_parts.group(2):0>5}'
            elif cat == 'PGC':
                # Fixed catalog name to recognize also LEDA prefix
                objectname = f'{cat}{name_parts.group(2):0>6}'
            else:
                objectname = f'{name_parts.group(1).strip()}{name_parts.group(2):0>3}'
            return cat, objectname
    raise UnknownIdentifier(text)


def _str_to_coords(text: str) -> np.ndarray:
    """Recognize coordinates as string and return them as radians.

    Args:
        text (string): a string expressing coordinates in the form `HH:MM:SS.ss +/-DD:MM:SS.s`

    Returns:
        `array([RA, Dec])`

        A numpy array of shape (2,) with coordinates expressed in radians.

    Raises:
        InvalidCoordinates: If the text cannot be recognized as valid coordinates.

    """
    pattern = re.compile(r'^(?:(\d{1,2}):(\d{1,2}):(\d{1,2}(?:\.\d{1,2})?))\s'
                         r'(?:([+-]\d{1,2}):(\d{1,2}):(\d{1,2}(?:\.\d{1,2})?))$')
    result = pattern.match(text)

    if result:
        hms = np.array([float(x) for x in result.groups()[0:3]])
        ra = np.radians(np.sum(hms * [15, 1/4, 1/240]))
        dms = np.array([float(x) for x in result.groups()[3:6]])
        if np.signbit(dms[0]):
            dec = np.radians(np.sum(dms * [1, -1/60, -1/3600]))
        else:
            dec = np.radians(np.sum(dms * [1, 1/60, 1/3600]))

        return np.array([ra, dec])
    else:
        raise InvalidCoordinates(f'This text cannot be recognized as coordinates: {text}')


def get(name: str) -> Optional[Dso]:
    """Search and return an object from the database.

    If an object name isn't recognized, it will return None.

    Args:
        name: the name of the object

    Returns:
        Dso or None.

    """
    try:
        obj = Dso(name)
    except (ObjectNotFound, UnknownIdentifier):
        return None
    return obj


def getNeighbors(obj: Union[Dso, str], separation: Union[int, float],
                 catalog: str = "all") -> List[Tuple[Dso, float]]:
    """Find all neighbors of an object within a user selected range.

    It requires an object as the starting point of the search (either a string containing
    the name or a Dso type) and a search radius expressed in arcmins.

    The maximum allowed search radius is 600 arcmin (10 degrees).

    It returns a list of of tuples with the Dso objects found in range and its distance,
    or an empty list if no object is found:

            >>> from pyongc.ongc import Dso, getNeighbors
            >>> s1 = Dso("ngc521")
            >>> getNeighbors(s1, 15) #doctest: +ELLIPSIS
            [(<pyongc.ongc.Dso object at 0x...>, 0.13726168561780452), \
(<pyongc.ongc.Dso object at 0x...>, 0.24140243942744602)]

            >>> from pyongc.ongc import getNeighbors
            >>> getNeighbors("ngc521", 1)
            []

    The optional "catalog" parameter can be used to filter the search to only NGC or IC objects:

            >>> from pyongc.ongc import getNeighbors
            >>> getNeighbors("ngc521", 15, catalog="NGC") #doctest: +ELLIPSIS
            [(<pyongc.ongc.Dso object at 0x...>, 0.24140243942744602)]

    Args:
        object: a Dso object or a string which identifies the object
        separation: maximum distance from the object expressed in arcmin
        catalog: filter for "NGC" or "IC" objects - default is all

    Returns:
        A list of tuples with each element composed by the Dso object found and
        its distance from the starting point, ordered by distance.

    Raises:
        ValueError: If the search radius exceeds 10 degrees.
        InvalidCoordinates: If the starting object hasn't got registered cordinates.

    """
    if not isinstance(obj, Dso):
        obj = Dso(obj)
    if separation > 600:
        raise ValueError('The maximum search radius allowed is 10 degrees.')
    if obj.rad_coords is None:
        raise InvalidCoordinates('Starting object hasn\'t got registered coordinates.')

    cols = 'objects.name'
    tables = 'objects'
    params = f'type != "Dup" AND name !="{obj.name}"'
    if catalog.upper() in ["NGC", "IC"]:
        params += f' AND name LIKE "{catalog.upper()}%"'

    params += _limiting_coords(obj.rad_coords, np.ceil(separation / 60))

    neighbors = []
    for item in _queryFetchMany(cols, tables, params):
        possibleNeighbor = Dso(item[0])
        distance = getSeparation(obj, possibleNeighbor)[0]
        if distance <= (separation / 60):
            neighbors.append((possibleNeighbor, distance))

    return sorted(neighbors, key=lambda neighbor: neighbor[1])


def getSeparation(obj1: Union[Dso, str], obj2: Union[Dso, str],
                  style: str = "raw") -> Union[Tuple[float, float, float], str]:
    """Finds the apparent angular separation between two objects.

    This function will compute the apparent angular separation between two objects,
    either identified with their names as strings or directly as Dso type.

    By default it returns a tuple containing the angular separation and the differences in A.R.
    and Declination expressed in degrees:

            >>> from pyongc.ongc import Dso, getSeparation
            >>> s1 = Dso("ngc1")
            >>> s2 = Dso("ngc2")
            >>> getSeparation(s1, s2)
            (0.03008927371519897, 0.005291666666666788, -0.02972222222221896)

            >>> from pyongc.ongc import getSeparation
            >>> getSeparation("ngc1", "ngc2")
            (0.03008927371519897, 0.005291666666666788, -0.02972222222221896)

    With the optional parameter `style` set to `text`, it returns a formatted string:

            >>> from pyongc.ongc import getSeparation
            >>> getSeparation("ngc1", "ngc2", style="text")
            '0° 1m 48.32s'

    If one of the objects is not found in the database it returns an ObjectNotFound exception:

            >>> from pyongc.ongc import getSeparation
            >>> getSeparation("ngc1a", "ngc2")
            Traceback (most recent call last):
            ...
            pyongc.exceptions.ObjectNotFound: Object named NGC0001A not found in the database.

    Args:
        obj1: first Dso object or string identifier
        obj2: second Dso object or string identifier
        style: use "text" to return a string with degrees, minutes and seconds

    Returns:
        By default the return value is a tuple with values expressed in degrees

        (angular separation, difference in A.R, difference in Dec)

        With the `style` parameter set to `text` we get a more readable output in the form
        `'DD° MMm SS.SSs'`

    """
    if not isinstance(obj1, Dso):
        obj1 = Dso(obj1)
    if not isinstance(obj2, Dso):
        obj2 = Dso(obj2)
    if obj1.rad_coords is None or obj2.rad_coords is None:
        raise InvalidCoordinates('One object hasn\'t got registered coordinates.')

    separation = _distance(obj1.rad_coords, obj2.rad_coords)

    if style == "text":
        d = int(separation[0])
        md = abs(separation[0] - d) * 60
        m = int(md)
        s = (md - m) * 60
        return f'{d:d}° {m:d}m {s:.2f}s'
    else:
        return separation


def listObjects(**kwargs) -> List[Dso]:
    """Query the database for DSObjects with specific parameters.

    This function returns a list of all DSObjects that match user defined parameters.
    If no argument is passed to the function, it returns all the objects from the database:

            >>> from pyongc.ongc import listObjects
            >>> objectList = listObjects()
            >>> len(objectList)
            13992

    Filters are combined with "AND" in the query; only one value for filter is allowed:

            >>> from pyongc.ongc import listObjects
            >>> objectList = listObjects(catalog="NGC", constellation=["Boo", ])
            >>> len(objectList)
            281

    Duplicated objects are not resolved to main objects:

            >>> from pyongc.ongc import listObjects
            >>> objectList = listObjects(type=["Dup", ])
            >>> print(objectList[0])
            IC0011, Duplicated record in Cas

    The maxSize filter will include objects with no size recorded in database:

            >>> from pyongc.ongc import listObjects
            >>> objectList = listObjects(maxsize=0)
            >>> len(objectList)
            1967

    Args:
        catalog (string, optional): filter for catalog. [NGC|IC|M]
        type (list, optional): filter for object type. See OpenNGC types list.
        constellation (list, optional): filter for constellation
            (three letter latin form - e.g. "And")
        minsize (float, optional): filter for objects with MajAx >= minSize(arcmin)
        maxsize (float, optional): filter for objects with MajAx < maxSize(arcmin)
            OR MajAx not available
        uptobmag (float, optional): filter for objects with B-Mag brighter than value
        uptovmag (float, optional): filter for objects with V-Mag brighter than value
        minra (float, optional): filter for objects with RA degrees greater than value
        maxra (float, optional): filter for objects with RA degrees lower than value
        mindec (float, optional): filter for objects above specified Dec degrees
        maxdec (float, optional): filter for objects below specified Dec degrees
        cname (string, optional): filter for objects with common name like input value
        withname (bool, optional): filter for objects with common names

    Returns:
        A list of ongc.Dso objects.

    Raises:
        ValueError: If a filter name other than those expected is inserted.
        ValueError: If an unrecognized catalog name is entered. Only [NGC|IC|M] are permitted.

    """
    available_filters = ['catalog',
                         'type',
                         'constellation',
                         'minsize',
                         'maxsize',
                         'uptobmag',
                         'uptovmag',
                         'minra',
                         'maxra',
                         'mindec',
                         'maxdec',
                         'cname',
                         'withname']
    cols = 'objects.name'
    tables = 'objects'

    if kwargs == {}:
        params = '1'
        return [Dso(str(item[0]), True) for item in _queryFetchMany(cols, tables, params)]
    for element in kwargs:
        if element not in available_filters:
            raise ValueError("Wrong filter name.")

    paramslist = []
    order = ''
    if "catalog" in kwargs:
        if kwargs["catalog"].upper() == "NGC" or kwargs["catalog"].upper() == "IC":
            paramslist.append(f'name LIKE "{kwargs["catalog"].upper()}%"')
        elif kwargs["catalog"].upper() == "M":
            paramslist.append('messier != ""')
            order = 'messier ASC'
        else:
            raise ValueError('Wrong value for catalog filter. [NGC|IC|M]')
    if "type" in kwargs:
        types = [f'"{t}"' for t in kwargs["type"]]
        paramslist.append(f'type IN ({",".join(types)})')

    if "constellation" in kwargs:
        constellations = [f'"{c.capitalize()}"' for c in kwargs["constellation"]]
        paramslist.append(f'const IN ({",".join(constellations)})')

    if "minsize" in kwargs:
        paramslist.append(f'majax >= {kwargs["minsize"]}')

    if "maxsize" in kwargs:
        paramslist.append(f'(majax < {kwargs["maxsize"]} OR majax is NULL)')

    if "uptobmag" in kwargs:
        paramslist.append(f'bmag <= {kwargs["uptobmag"]}')

    if "uptovmag" in kwargs:
        paramslist.append(f'vmag <= {kwargs["uptovmag"]}')

    if "minra" in kwargs and "maxra" in kwargs:
        if kwargs["maxra"] > kwargs["minra"]:
            paramslist.append(f'ra BETWEEN '
                              f'{np.radians(kwargs["minra"])} '
                              f'AND {np.radians(kwargs["maxra"])}'
                              )
        else:
            paramslist.append(f'ra >= {np.radians(kwargs["minra"])} '
                              f'OR ra <= {np.radians(kwargs["maxra"])}'
                              )
    elif "minra" in kwargs:
        paramslist.append(f'ra >= {np.radians(kwargs["minra"])}')
    elif "maxra" in kwargs:
        paramslist.append(f'ra <= {np.radians(kwargs["maxra"])}')

    if "mindec" in kwargs and "maxdec" in kwargs:
        if kwargs["maxdec"] > kwargs["mindec"]:
            paramslist.append(f'dec BETWEEN '
                              f'{np.radians(kwargs["mindec"])} '
                              f'AND {np.radians(kwargs["maxdec"])}'
                              )
    elif "mindec" in kwargs:
        paramslist.append(f'dec >= {np.radians(kwargs["mindec"])}')
    elif "maxdec" in kwargs:
        paramslist.append(f'dec <= {np.radians(kwargs["maxdec"])}')

    if "cname" in kwargs:
        paramslist.append(f'commonnames LIKE "%{kwargs["cname"]}%"')

    if "withname" in kwargs and kwargs["withname"] is True:
        paramslist.append('commonnames != ""')
    elif "withname" in kwargs and kwargs["withname"] is False:
        paramslist.append('commonnames = ""')

    params = " AND ".join(paramslist)
    return [Dso(item[0], True) for item in _queryFetchMany(cols, tables, params, order)]


def nearby(coords_string: str, separation: float = 60,
           catalog: str = "all") -> List[Tuple[Dso, float]]:
    """Search for objects around given coordinates.

    Returns all objects around a point expressed by the coords parameter and within a search
    radius expressed by the separation parameter.
    Coordinates must be Right Ascension and Declination expressed as a string in the
    form "HH:MM:SS.ss +/-DD:MM:SS.s".

    The maximum allowed search radius is 600 arcmin (10 degrees) and default value is 60.

    It returns a list of of tuples with the Dso objects found in range and its distance,
    or an empty list if no object is found:

            >>> from pyongc.ongc import nearby
            >>> nearby('11:08:44 -00:09:01.3') #doctest: +ELLIPSIS +FLOAT_CMP
            [(<pyongc.ongc.Dso object at 0x...>, 0.1799936868460791), \
(<pyongc.ongc.Dso object at 0x...>, 0.7398295985600021), \
(<pyongc.ongc.Dso object at 0x...>, 0.9810037613087355)]

    The optional "catalog" parameter can be used to filter the search to only NGC or IC objects:

            >>> from pyongc.ongc import nearby
            >>> nearby('11:08:44 -00:09:01.3', separation=60, catalog='NGC') #doctest: +ELLIPSIS \
+FLOAT_CMP
            [(<pyongc.ongc.Dso object at 0x...>, 0.7398295985600021)]

    Args:
        coords: R.A. and Dec of search center
        separation: search radius expressed in arcmin - default 60
        catalog: filter for "NGC" or "IC" objects - default is all

    Returns:
        `[(Dso, separation),]`

        A list of tuples with the Dso object found and its distance from the starting point,
        ordered by distance.

    Raises:
        ValueError: If the search radius exceeds 10 degrees.

    """
    if separation > 600:
        raise ValueError('The maximum search radius allowed is 10 degrees.')

    coords = _str_to_coords(coords_string)

    cols = 'objects.name'
    tables = 'objects'
    params = 'type != "Dup"'
    if catalog.upper() in ["NGC", "IC"]:
        params += f' AND name LIKE "{catalog.upper()}%"'

    params += _limiting_coords(coords, np.ceil(separation / 60))

    neighbors = []
    for item in _queryFetchMany(cols, tables, params):
        possibleNeighbor = Dso(item[0])
        distance = _distance(coords, possibleNeighbor.rad_coords)[0]
        if distance <= (separation / 60):
            neighbors.append((possibleNeighbor, distance))

    return sorted(neighbors, key=lambda neighbor: neighbor[1])


def printDetails(dso: Union[Dso, str]) -> str:
    """Prints a detailed description of the object in a formatted output.

    This function returns a string with all the available details of the object,
    formatted in a way to fit a 80cols display.
    The object can be identified by its name as a string or by a Dso type:

            >>> from pyongc.ongc import printDetails
            >>> print(printDetails("ngc1"))
            +-----------------------------------------------------------------------------+
            | Id: 5596      Name: NGC0001           Type: Galaxy                          |
            | R.A.: 00:07:15.84      Dec.: +27:42:29.1      Constellation: Peg            |
            +-----------------------------------------------------------------------------+
            | Major axis: 1.57'      Minor axis: 1.07'      Position angle: 112°          |
            | B-mag: 13.69   V-mag: 12.93   J-mag: 10.78   H-mag: 10.02   K-mag: 9.76     |
            |                                                                             |
            | Parallax: N/A          Radial velocity: 4536km/s      Redshift: 0.015245    |
            |                                                                             |
            | Proper apparent motion in RA: N/A                                           |
            | Proper apparent motion in Dec: N/A                                          |
            |                                                                             |
            | Surface brightness: 23.13     Hubble classification: Sb                     |
            +-----------------------------------------------------------------------------+
            | Other identifiers:                                                          |
            |    2MASX J00071582+2742291, IRAS 00047+2725, MCG +04-01-025, PGC 000564,    |
            |    UGC 00057                                                                |
            +-----------------------------------------------------------------------------+
            <BLANKLINE>

    If the object is not found in the database it returns an ObjectNotFound exception:

            >>> from pyongc.ongc import printDetails
            >>> printDetails("ngc1a")
            Traceback (most recent call last):
            ...
            pyongc.exceptions.ObjectNotFound: Object named NGC0001A not found in the database.

    Args:
        dso: a Dso object or a string identifier

    Returns:
        All the object data ready to be printed on a 80cols terminal output.

    """
    def _justifyText(text: str) -> str:
        """Prints the text on multiple lines if length is more than 73 chars.

        Args:
            text: text to be sliced

        """
        text_returned = ''
        chunks = text.split()
        line = []
        lineLength = 0
        for chunk in chunks:
            lineLength += len(chunk) + 1
            if lineLength <= 73:
                line.append(chunk)
                continue
            else:
                text_returned += f'|    {" ".join(line):73}|\n'
                del line[:]
                line.append(chunk)
                lineLength = len(chunk) + 1
        text_returned += f'|    {" ".join(line):73}|\n'
        return text_returned

    def _add_units(value: Union[int, float, None], unit: str = '') -> str:
        """Returns a string with value + unit or N/A.

        Args:
            value: a int, float or None
            unit: the unit to append

        """
        if value is None:
            return 'N/A'
        else:
            return f'{value}{unit}'

    if not isinstance(dso, Dso):
        dso = Dso(dso)

    objType = dso.type
    separator = (f'+{"-" * 77}+\n')
    obj_string = separator
    obj_string += ('| '
                   f'Id: {str(dso.id):10}'
                   f'Name: {dso.name:18}'
                   f'Type: {objType:32}'
                   '|\n'
                   )
    obj_string += ('| '
                   f'R.A.: {dso.ra:17}'
                   f'Dec.: {dso.dec:17}'
                   f'Constellation: {dso.constellation:15}'
                   '|\n'
                   )

    if (dso.identifiers[0] is not None or
            dso.identifiers[1] is not None or
            dso.identifiers[2] is not None):
        obj_string += f'| {"Also known as:":76}|\n'
        knownAs = []
        if dso.identifiers[0] is not None:
            knownAs.append(dso.identifiers[0])
        if dso.identifiers[1] is not None:
            knownAs.extend(dso.identifiers[1])
        if dso.identifiers[2] is not None:
            knownAs.extend(dso.identifiers[2])
        obj_string += _justifyText(", ".join(knownAs))

    if dso.identifiers[3] is not None:
        obj_string += f'| {"Common names:":76}|\n'
        obj_string += _justifyText(", ".join(dso.identifiers[3]))
    obj_string += separator

    obj_string += ('| '
                   f'''Major axis: {_add_units(dso.dimensions[0], "'"):11}'''
                   f'''Minor axis: {_add_units(dso.dimensions[1], "'"):11}'''
                   f'''Position angle: {_add_units(dso.dimensions[2], "°"):14}'''
                   '|\n'
                   )

    obj_string += ('| '
                   f'B-mag: {_add_units(dso.magnitudes[0]):8}'
                   f'V-mag: {_add_units(dso.magnitudes[1]):8}'
                   f'J-mag: {_add_units(dso.magnitudes[2]):8}'
                   f'H-mag: {_add_units(dso.magnitudes[3]):8}'
                   f'K-mag: {_add_units(dso.magnitudes[4]):9}'
                   '|\n'
                   )

    obj_string += (f'|{" " * 77}|\n')

    redshift = f'{dso.redshift:.6f}'
    obj_string += ('| '
                   f'Parallax: {_add_units(dso.parallax, "mas"):13}'
                   f'Radial velocity: {_add_units(dso.radvel, "km/s"):14}'
                   f'Redshift: {_add_units(redshift):12}'
                   '|\n'
                   )

    obj_string += (f'|{" " * 77}|\n')

    obj_string += ('| '
                   f'Proper apparent motion in RA: {_add_units(dso.pm_ra, "mas/yr"):46}'
                   '|\n'
                   )

    obj_string += ('| '
                   f'Proper apparent motion in Dec: {_add_units(dso.pm_dec, "mas/yr"):45}'
                   '|\n'
                   )

    obj_string += (f'|{" " * 77}|\n')

    if objType == "Galaxy":
        obj_string += ('| '
                       f'Surface brightness: {str(dso.surface_brightness):10}'
                       f'Hubble classification: {dso.hubble:23}'
                       '|\n'
                       )

    if dso.cstar_data is not None:
        if dso.cstar_data[0] is not None:
            obj_string += f'| {"Central star identifiers:":76}|\n'
            obj_string += f'|    {", ".join(dso.cstar_data[0]):73}|\n'
            obj_string += f'|{" " * 77}|\n'
        obj_string += f'| {"Central star magnitudes:":76}|\n'
        obj_string += ('|    '
                       f'U-mag: {_add_units(dso.cstar_data[1]):17}'
                       f'B-mag: {_add_units(dso.cstar_data[2]):17}'
                       f'V-mag: {_add_units(dso.cstar_data[3]):18}'
                       '|\n'
                       )

    obj_string += separator

    if dso.identifiers[4] is not None:
        obj_string += f'| {"Other identifiers:":76}|\n'
        obj_string += _justifyText(", ".join(dso.identifiers[4]))
        obj_string += separator

    if dso.notes[0] != "":
        obj_string += f'| {"NED notes:":76}|\n'
        obj_string += _justifyText(dso.notes[0])
        obj_string += separator

    if dso.notes[1] != "":
        obj_string += f'| {"OpenNGC notes:":76}|\n'
        obj_string += _justifyText(dso.notes[1])
        obj_string += separator
    return obj_string


def stats() -> Tuple[str, str, int, tuple]:
    try:
        db = sqlite3.connect(f'file:{DBPATH}?mode=ro', uri=True)
    except sqlite3.Error:
        raise OSError(f'There was a problem accessing database file at {DBPATH}')

    try:
        cursor = db.cursor()

        cursor.execute('SELECT objTypes.typedesc, count(*) '
                       'FROM objects JOIN objTypes ON objects.type = objTypes.type '
                       'GROUP BY objects.type')
        typesStats = cursor.fetchall()
    except Exception as err:  # pragma: no cover
        raise err
    finally:
        db.close()

    totalObjects = sum(objType[1] for objType in typesStats)

    return version, DBDATE, totalObjects, typesStats

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

import unittest

import mock
import numpy as np

import pyongc
from pyongc.ongc import (
    _distance as distance, _limiting_coords as limiting_coords,
    _str_to_coords as str_to_coords)


class TestDsoClass(unittest.TestCase):
    """Test that Dso objects are created in the right way and that data
    is retrieved correctly.
    """
    @mock.patch('pyongc.ongc.DBPATH', 'badpath')
    def test_fail_database_connection(self):
        """Test a failed connection to database."""
        self.assertRaisesRegex(OSError, 'There was a problem accessing database file',
                               pyongc.Dso, 'NGC0001')
        self.assertRaisesRegex(OSError, 'There was a problem accessing database file',
                               pyongc.listObjects)
        self.assertRaisesRegex(OSError, 'There was a problem accessing database file',
                               pyongc.stats)

    def test_dso_creation_error(self):
        """Test we get a type error if user doesn't input a string."""
        self.assertRaisesRegex(TypeError, 'Wrong type as parameter', pyongc.Dso, 1234)

    def test_name_recognition_NGC(self):
        """Test the recognition of a NGC/IC identifier."""
        self.assertEqual(pyongc.Dso('ngc1')._name, 'NGC0001')
        self.assertEqual(pyongc.Dso('ic 1')._name, 'IC0001')
        self.assertEqual(pyongc.Dso('ic80 ned1')._name, 'IC0080 NED01')
        self.assertEqual(pyongc.Dso('ngc61a')._name, 'NGC0061A')
        self.assertRaisesRegex(ValueError, 'not recognized', pyongc.Dso, 'NGC77777')
        self.assertRaisesRegex(ValueError, 'not recognized', pyongc.Dso, 'NGC0001ABC')
        self.assertRaisesRegex(ValueError, 'not found in the database', pyongc.Dso, 'NGC0001A')

    def test_name_recognition_Barnard(self):
        """Test the recognition of a Barnard identifier."""
        self.assertEqual(pyongc.Dso('b33')._name, 'B033')

    def test_name_recognition_Caldwell(self):
        """Test the recognition of a Caldwell identifier."""
        self.assertEqual(pyongc.Dso('c9')._name, 'C009')

    def test_name_recognition_ESO(self):
        """Test the recognition of a ESO identifier."""
        self.assertEqual(pyongc.Dso('eso56-115')._name, 'ESO056-115')

    def test_name_recognition_Harvard(self):
        """Test the recognition of a Harvard identifier."""
        self.assertEqual(pyongc.Dso('H5')._name, 'H05')

    def test_name_recognition_Hickson(self):
        """Test the recognition of a HCG identifier."""
        self.assertEqual(pyongc.Dso('hcg79')._name, 'HCG079')

    def test_name_recognition_LBN(self):
        """Test the recognition of a LBN identifier."""
        self.assertEqual(pyongc.Dso('LBN741')._name, 'NGC1333')

    def test_name_recognition_Melotte(self):
        """Test the recognition of a Mel identifier."""
        self.assertEqual(pyongc.Dso('mel111')._name, 'Mel111')

    def test_name_recognition_Messier(self):
        """Test the recognition of a Messier identifier."""
        self.assertEqual(pyongc.Dso('M1')._name, 'NGC1952')
        self.assertRaisesRegex(ValueError, 'not recognized', pyongc.Dso, 'M15A')

    def test_name_recognition_M102(self):
        """Test M102 == M101."""
        self.assertEqual(pyongc.Dso('M102')._name, pyongc.Dso('M101')._name)

    def test_name_recognition_MWSC(self):
        """Test the recognition of a MWSC identifier."""
        self.assertEqual(pyongc.Dso('MWSC146')._name, 'IC0166')

    def test_name_recognition_PGC(self):
        """Test the recognition of a PGC identifier."""
        self.assertEqual(pyongc.Dso('PGC10540')._name, 'IC0255')
        self.assertEqual(pyongc.Dso('leda 10540')._name, 'IC0255')

    def test_name_recognition_UGC(self):
        """Test the recognition of a UGC identifier."""
        self.assertEqual(pyongc.Dso('UGC9965')._name, 'IC1132')

    def test_duplicate_resolving(self):
        """Test that a duplicated object is returned as himself when asked to do so."""
        self.assertEqual(pyongc.Dso('ngc20')._name, 'NGC0006')
        self.assertEqual(pyongc.Dso('ngc20', returndup=True)._name, 'NGC0020')
        self.assertEqual(pyongc.Dso('ic555')._name, 'IC0554')

    def test_object_print(self):
        """Test basic object data representation."""
        obj = pyongc.Dso('NGC1')

        expected = 'NGC0001, Galaxy in Peg'
        actual = str(obj)
        self.assertEqual(actual, expected)

    def test_getDec(self):
        """Test Declination as string is returned correctly."""
        obj = pyongc.Dso('IC15')
        expected = '-00:03:40.6'
        self.assertEqual(obj.getDec(), expected)
        # Nonexistent object
        obj = pyongc.Dso('NGC6991')
        expected = 'N/A'
        self.assertEqual(obj.getDec(), expected)

    def test_getRA(self):
        """Test Declination as string is returned correctly."""
        obj = pyongc.Dso('NGC475')
        expected = '01:20:02.00'
        self.assertEqual(obj.getRA(), expected)
        # Nonexistent object
        obj = pyongc.Dso('NGC6991')
        expected = 'N/A'
        self.assertEqual(obj.getRA(), expected)

    def test_get_coordinates_successful(self):
        """Test succesful getCoords() method."""
        obj = pyongc.Dso('NGC1')

        np.testing.assert_allclose(obj.getCoords(), ([[0., 7., 15.84], [27., 42., 29.1]]), 1e-12)

    def test_get_coordinates_nonexistent(self):
        """Test getCoords() on a Nonexistent object which doesn't have coords."""
        obj = pyongc.Dso('IC1064')

        expected = 'Object named IC1064 has no coordinates in database.'
        with self.assertRaisesRegex(ValueError, expected):
            obj.getCoords()

    def test_get_coordinates_radians_successful(self):
        """Test succesful getCoords() method."""
        obj = pyongc.Dso('NGC1')
        np.testing.assert_allclose(obj.getCoordsRad(),
                                   ([0.03169517921621703, 0.48359728358363213]),
                                   1e-12)

    def test_get_PN_central_star_data(self):
        """Test retrieving Planetary Nebulaes central star data."""
        # With central star identifiers
        obj = pyongc.Dso('NGC1535')
        expected = (['BD -13 842', 'HD 26847'], None, 12.19, 12.18)
        self.assertEqual(obj.getCStarData(), expected)
        # Without central star identifiers
        obj = pyongc.Dso('IC289')
        expected = (None, None, 15.1, 15.9)
        self.assertEqual(obj.getCStarData(), expected)

    def test_get_object_identifiers(self):
        """Test getIdentifiers() method."""
        obj = pyongc.Dso('NGC650')
        expected = ('M076', ['NGC0651'], None, ['Barbell Nebula', 'Cork Nebula',
                    'Little Dumbbell Nebula'], ['2MASX J01421808+5134243', 'IRAS 01391+5119',
                    'PN G130.9-10.5'])
        self.assertEqual(obj.getIdentifiers(), expected)

        obj = pyongc.Dso('IC5003')
        expected = (None,
                    None,
                    ['IC5029', 'IC5039', 'IC5046'],
                    None,
                    ['2MASX J20431434-2951122', 'ESO 463-020', 'ESO-LV 463-0200',
                     'IRAS 20401-3002', 'MCG -05-49-001', 'PGC 065249'])
        self.assertEqual(obj.getIdentifiers(), expected)

    def test_get_magnitudes(self):
        """Test getMagnitudes() method."""
        obj = pyongc.Dso('NGC1')

        expected = (13.4, None, 10.78, 10.02, 9.76)
        self.assertEqual(obj.getMagnitudes(), expected)

    def test_get_main_identifier(self):
        """Test getName() method."""
        obj = pyongc.Dso('NGC1')

        expected = 'NGC0001'
        self.assertEqual(obj.getName(), expected)

    def test_get_object_notes(self):
        """Test getNotes() method."""
        obj = pyongc.Dso('NGC6543')

        expected = ('Additional radio sources may contribute to the WMAP flux.',
                    'Dimensions taken from LEDA')
        self.assertEqual(obj.getNotes(), expected)

    def test_xephem_format(self):
        """Test object representation in XEphem format."""
        # Galaxy pair
        obj = pyongc.Dso('IC1008')
        expected = 'IC1008|IC4414,f|A,14:23:42.59,+28:20:52.3,,48.00||'
        self.assertEqual(obj.xephemFormat(), expected)

        # Globular cluster
        obj = pyongc.Dso('NGC1904')
        expected = 'NGC1904|M079,f|C,05:24:10.59,-24:31:27.2,9.21,,432.00||'
        self.assertEqual(obj.xephemFormat(), expected)

        # Double star
        obj = pyongc.Dso('IC470')
        expected = 'IC0470,f|D,07:23:31.50,+46:04:43.2,13.89,,||'
        self.assertEqual(obj.xephemFormat(), expected)

        # Nebula
        obj = pyongc.Dso('IC2087')
        expected = 'IC2087,f|F,04:39:59.97,+25:44:32.0,10.67,,240.00|240.00|'
        self.assertEqual(obj.xephemFormat(), expected)

        # Spiral galaxy
        obj = pyongc.Dso('NGC1')
        expected = 'NGC0001,f|G,00:07:15.84,+27:42:29.1,13.4,,94.20|64.20|112'
        self.assertEqual(obj.xephemFormat(), expected)

        # Elliptical galaxy
        obj = pyongc.Dso('IC3')
        expected = 'IC0003,f|H,00:12:06.09,-00:24:54.8,15.1,,55.80|40.20|53'
        self.assertEqual(obj.xephemFormat(), expected)

        # Dark nebula
        obj = pyongc.Dso('B33')
        expected = 'B033|Horsehead Nebula,f|K,05:40:59.00,-02:27:30.0,,360.00|240.00|90'
        self.assertEqual(obj.xephemFormat(), expected)

        # Emission nebula
        obj = pyongc.Dso('NGC1936')
        expected = 'NGC1936|IC2127,f|N,05:22:13.96,-67:58:41.9,11.6,,60.00|60.00|'
        self.assertEqual(obj.xephemFormat(), expected)

        # Open cluster
        obj = pyongc.Dso('IC4725')
        expected = 'IC4725|M025,f|O,18:31:46.77,-19:06:53.8,5.29,,846.00||'
        self.assertEqual(obj.xephemFormat(), expected)

        # Planetary nebula
        obj = pyongc.Dso('NGC650')
        expected = 'NGC0650|M076|NGC0651|Barbell Nebula|Cork Nebula|Little Dumbbell Nebula,f|P,' \
            '01:42:19.69,+51:34:31.7,12.2,,67.20||'
        self.assertEqual(obj.xephemFormat(), expected)

        # SNR
        obj = pyongc.Dso('NGC1952')
        expected = 'NGC1952|M001,f|R,05:34:31.97,+22:00:52.1,8.4,,480.00|240.00|'
        self.assertEqual(obj.xephemFormat(), expected)

        # Star
        obj = pyongc.Dso('IC117')
        expected = 'IC0117,f|S,01:27:25.41,-01:51:36.7,11.22,,||'
        self.assertEqual(obj.xephemFormat(), expected)

        # Star cluster + nebula
        obj = pyongc.Dso('NGC1976')
        expected = 'NGC1976|M042|Great Orion Nebula|Orion Nebula,f|U,' \
            '05:35:16.48,-05:23:22.8,4.0,,5400.00|3600.00|'
        self.assertEqual(obj.xephemFormat(), expected)

        # Unknown - other
        obj = pyongc.Dso('NGC405')
        expected = 'NGC0405,f,01:08:34.11,-46:40:06.6,7.17,,||'
        self.assertEqual(obj.xephemFormat(), expected)


class TestDsoMethods(unittest.TestCase):
    """Test functions about DS Objects."""
    def test_distance(self):
        """Test distance calculation."""
        np.testing.assert_allclose(distance(np.array([0., 0.]),
                                                  np.array([np.radians(15), 0.])),
                                   (15, 15, 0),
                                   1e-12
                                   )
        np.testing.assert_allclose(distance(np.array([0., 0.]),
                                                  np.array([np.radians(23*15), 0.])),
                                   (15, 345, 0),
                                   1e-12
                                   )
        np.testing.assert_allclose(distance(np.array([0., 0.]),
                                                  np.array([0., np.radians(15)])),
                                   (15, 0, 15),
                                   1e-12
                                   )
        np.testing.assert_allclose(distance(np.array([0., 0.]),
                                                  np.array([0., np.radians(-15)])),
                                   (15, 0, -15),
                                   1e-12
                                   )

    def test_limiting_coords_hms(self):
        """Test query filters for coordinates expressed in HMS."""
        # Positive dec
        coords = np.array([[0., 8., 27.05], [27., 43., 3.6]])
        expected = (' AND (ra BETWEEN 0.0019671315111019425 AND 0.07178030159087512)'
                    ' AND (dec BETWEEN 0.44885795926372835 AND 0.5186711293435016)')
        self.assertEqual(limiting_coords(coords, 2), expected)
        # Negative dec
        coords = np.array([[0., 11., 0.88], [-12., 49., 22.3]])
        expected = (' AND (ra BETWEEN 0.013153964795863934 AND 0.08296713487563712)'
                    ' AND (dec BETWEEN -0.25870773095471394 AND -0.18889456087494075)')
        self.assertEqual(limiting_coords(coords, 2), expected)

    def test_limiting_coords_rad(self):
        """Test query filters for coordinates expressed in radians."""
        # Crossing 0 RA
        coords = np.array([[0., 2., 0.], [27., 43., 3.6]])
        expected = (' AND (ra <= 0.04363323129985824 OR ra >= 6.257005368399671)'
                    ' AND (dec BETWEEN 0.44885795926372835 AND 0.5186711293435016)')
        self.assertEqual(limiting_coords(coords, 2), expected)
        coords = np.array([[23., 58., 0.], [27., 43., 3.6]])
        expected = (' AND (ra <= 0.02617993877991509 OR ra >= 6.239552075879729)'
                    ' AND (dec BETWEEN 0.44885795926372835 AND 0.5186711293435016)')
        self.assertEqual(limiting_coords(coords, 2), expected)
        # Max declination
        coords = np.array([[0., 11., 0.88], [89., 0., 0.]])
        expected = (' AND (ra BETWEEN 0.013153964795863934 AND 0.08296713487563712)'
                    ' AND (dec BETWEEN 1.5184364492350666 AND 1.5707963267948966)')
        self.assertEqual(limiting_coords(coords, 2), expected)
        # Min declination
        coords = np.array([[0., 11., 0.88], [-89., 0., 0.]])
        expected = (' AND (ra BETWEEN 0.013153964795863934 AND 0.08296713487563712)'
                    ' AND (dec BETWEEN -1.5707963267948966 AND -1.5184364492350666)')
        self.assertEqual(limiting_coords(coords, 2), expected)

    def test_str_to_coords(self):
        """Test conversion from string to coordinates."""
        np.testing.assert_allclose(str_to_coords('01:12:24.0 +22:6:18'),
                                   np.array([np.radians(18.1), np.radians(22.105)]),
                                   1e-12
                                   )
        np.testing.assert_allclose(str_to_coords('10:04:50.40 -8:42:36.9'),
                                   np.array([np.radians(151.21), np.radians(-8.71025)]),
                                   1e-12
                                   )

    def test_str_to_coords_not_recognized(self):
        """Test failed conversion from string to coordinates."""
        bad_coords = '11:11:11 1:2:3'
        self.assertRaisesRegex(ValueError,
                               'This text cannot be recognized as coordinates: ' + bad_coords,
                               str_to_coords, bad_coords)

    def test_calculate_separation_raw(self):
        """Test that the calculated apparent angular separation between two objects
        is correct and reports the raw data to user.
        """
        obj1 = pyongc.Dso('NGC6070')
        obj2 = pyongc.Dso('NGC6118')

        expected = (4.207483963913541, 2.9580416666666864, -2.9927499999999996)
        self.assertEqual(pyongc.getSeparation(obj1, obj2), expected)

    def test_calculate_separation_friendly(self):
        """Test that the calculated apparent angular separation between two objects
        is correct and returns a user friendly output.
        """
        expected = '4° 12m 26.94s'
        self.assertEqual(pyongc.getSeparation('NGC6118', 'NGC6070', style='text'), expected)

    def test_get_neighbors(self):
        """Test that neighbors are correctly found and returned."""
        obj1 = pyongc.Dso('NGC521')

        neighbors = pyongc.getNeighbors(obj1, 15)
        expectedListLength = 2
        expectedNearest = 'IC1694, Galaxy in Cet'
        expectedNearestSeparation = 0.13726168561780452

        self.assertIsInstance(neighbors, list)
        self.assertEqual(len(neighbors), expectedListLength)
        self.assertEqual(str(neighbors[0][0]), expectedNearest)
        self.assertEqual(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_negative_dec(self):
        """Test that neighbors are correctly found and returned - with negative Dec value."""
        obj1 = pyongc.Dso('IC60')

        neighbors = pyongc.getNeighbors(obj1, 30)
        expectedListLength = 1
        expectedNearest = 'IC0058, Galaxy in Cet'
        expectedNearestSeparation = 0.4064105387726472

        self.assertIsInstance(neighbors, list)
        self.assertEqual(len(neighbors), expectedListLength)
        self.assertEqual(str(neighbors[0][0]), expectedNearest)
        self.assertEqual(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_above0ra(self):
        """Test that neighbors are correctly found and returned - with RA just above 00h."""
        obj1 = pyongc.Dso('IC1')

        neighbors = pyongc.getNeighbors(obj1, 15)
        expectedListLength = 2
        expectedNearest = 'NGC0016, Galaxy in Peg'
        expectedNearestSeparation = 0.1378555838270968

        self.assertIsInstance(neighbors, list)
        self.assertEqual(len(neighbors), expectedListLength)
        self.assertEqual(str(neighbors[0][0]), expectedNearest)
        self.assertEqual(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_below0ra(self):
        """Test that neighbors are correctly found and returned - with RA just below 00h."""
        obj1 = pyongc.Dso('IC1523')

        neighbors = pyongc.getNeighbors(obj1, 60)
        expectedListLength = 1
        expectedNearest = 'NGC7802, Galaxy in Psc'
        expectedNearestSeparation = 0.7874886760327793

        self.assertIsInstance(neighbors, list)
        self.assertEqual(len(neighbors), expectedListLength)
        self.assertEqual(str(neighbors[0][0]), expectedNearest)
        self.assertEqual(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_with_filter(self):
        """Test that neighbors are correctly found and returned."""
        neighbors = pyongc.getNeighbors('NGC521', 15, catalog='NGC')
        expectedListLength = 1
        expectedNearest = 'NGC0533, Galaxy in Cet'
        expectedNearestSeparation = 0.24140243942744602

        self.assertIsInstance(neighbors, list)
        self.assertEqual(len(neighbors), expectedListLength)
        self.assertEqual(str(neighbors[0][0]), expectedNearest)
        self.assertEqual(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_bad_value(self):
        """Return the right message if search radius value is out of range."""
        self.assertRaisesRegex(ValueError,
                               'The maximum search radius allowed is 10 degrees.',
                               pyongc.getNeighbors, 'IC1', 601)

    def test_list_all_objects(self):
        """Test the listObjects() method without filters.
        It should return all objects from database.
        """
        objectList = pyongc.listObjects()

        self.assertEqual(len(objectList), 13978)
        self.assertIsInstance(objectList[0], pyongc.Dso)

    def test_list_objects_filter_catalog_NGC(self):
        """Test the listObjects() method with catalog filter applied."""
        objectList = pyongc.listObjects(catalog='NGC')

        self.assertEqual(len(objectList), 8343)

    def test_list_objects_filter_catalog_IC(self):
        """Test the listObjects() method with catalog filter applied."""
        objectList = pyongc.listObjects(catalog='IC')

        self.assertEqual(len(objectList), 5615)

    def test_list_objects_filter_catalog_M(self):
        """Test the listObjects() method with catalog filter applied."""
        objectList = pyongc.listObjects(catalog='M')

        self.assertEqual(len(objectList), 109)

    def test_list_objects_filter_type(self):
        """Test the listObjects() method with type filter applied.
        Duplicated objects are not resolved to the main object.
        """
        objectList = pyongc.listObjects(type=['Dup', ])

        self.assertEqual(len(objectList), 636)
        self.assertEqual(str(objectList[0]), 'IC0011, Duplicated record in Cas')

    def test_list_objects_filter_multiple_types(self):
        """Test the listObjects() method with multiple types filter."""
        objectList = pyongc.listObjects(type=['*', '**', ])

        self.assertEqual(len(objectList), 792)

    def test_list_objects_filter_constellation(self):
        """Test the listObjects() method with constellation filter applied."""
        objectList = pyongc.listObjects(constellation=['and', 'Boo', ])

        self.assertEqual(len(objectList), 738)

    def test_list_objects_filter_size(self):
        """Test the listObjects() method with size filters applied."""
        objectList = pyongc.listObjects(minsize=15, maxsize=20)

        self.assertEqual(len(objectList), 40)

    def test_list_objects_with_no_size(self):
        """Test the listObjects() method to list objects without size."""
        objectList = pyongc.listObjects(maxsize=0)

        self.assertEqual(len(objectList), 2020)

    def test_list_objects_filter_mag(self):
        """Test the listObjects() method with magnitudes filters applied."""
        objectList = pyongc.listObjects(uptobmag=8, uptovmag=10)

        self.assertEqual(len(objectList), 173)

    def test_list_objects_filter_minra(self):
        """List objects with RA greater than minra."""
        objectList = pyongc.listObjects(minra=358)

        self.assertEqual(len(objectList), 56)

    def test_list_objects_filter_maxra(self):
        """List objects with RA lower than maxra."""
        objectList = pyongc.listObjects(maxra=2)

        self.assertEqual(len(objectList), 68)

    def test_list_objects_filter_ra_between(self):
        """List objects with RA between minra and maxra."""
        objectList = pyongc.listObjects(minra=1, maxra=2)

        self.assertEqual(len(objectList), 33)

    def test_list_objects_filter_ra_between_crossing_zero(self):
        """List objects with RA between minra and maxra crossing 0h."""
        objectList = pyongc.listObjects(minra=359, maxra=1)

        self.assertEqual(len(objectList), 69)

    def test_list_objects_filter_mindec(self):
        """List objects with Dec above mindec."""
        objectList = pyongc.listObjects(mindec=85)

        self.assertEqual(len(objectList), 9)

    def test_list_objects_filter_maxdec(self):
        """List objects with RA below maxdec."""
        objectList = pyongc.listObjects(maxdec=-85)

        self.assertEqual(len(objectList), 4)

    def test_list_objects_filter_dec_between(self):
        """List objects with Dec between mindec and maxdec."""
        objectList = pyongc.listObjects(mindec=-1, maxdec=1)

        self.assertEqual(len(objectList), 264)

    def test_list_objects_by_name(self):
        """Test the listObjects() method to list objects with the provided common name."""
        objectList = pyongc.listObjects(cname='california')

        self.assertEqual(len(objectList), 1)
        self.assertEqual(str(objectList[0]), 'NGC1499, Nebula in Per')

    def test_list_objects_with_name(self):
        """Test the listObjects() method to list objects with common name."""
        objectList = pyongc.listObjects(withname=True)

        self.assertEqual(len(objectList), 132)

    def test_list_objects_without_name(self):
        """Test the listObjects() method to list objects without common name."""
        objectList = pyongc.listObjects(withname=False)

        self.assertEqual(len(objectList), 13846)

    def test_list_objects_wrong_filter(self):
        """Test the listObjects() method when an unsupported filter is used."""
        expected = 'Wrong filter name.'

        with self.assertRaisesRegex(ValueError, expected):
            pyongc.listObjects(catalog='NGC', name='NGC1')

    def test_list_objects_wrong_catalog(self):
        """Test the listObjects() method with a wrong catalog name."""
        expected = 'Wrong value for catalog filter.'

        with self.assertRaisesRegex(ValueError, expected):
            pyongc.listObjects(catalog='UGC')

    def test_nearby(self):
        """Test that searching neighbors by coords works properly."""
        obj = pyongc.Dso('NGC521')
        objCoords = ' '.join([obj.getRA(), obj.getDec()])

        neighbors = pyongc.getNeighbors(obj, 15)
        nearby_objects = pyongc.nearby(objCoords, separation=15)

        self.assertIsInstance(nearby_objects, list)
        self.assertEqual(len(nearby_objects), len(neighbors)+1)
        self.assertEqual(str(nearby_objects[0][0]), str(obj))
        self.assertEqual(nearby_objects[0][1], 0)
        self.assertEqual(str(nearby_objects[1][0]), str(neighbors[0][0]))
        self.assertEqual(nearby_objects[1][1], neighbors[0][1])

    def test_nearby_with_filter(self):
        """Test that neighbors are correctly filtered."""
        obj = pyongc.Dso('NGC521')
        objCoords = ' '.join([obj.getRA(), obj.getDec()])

        neighbors = pyongc.getNeighbors('NGC521', 15, catalog='IC')
        nearby_objects = pyongc.nearby(objCoords, separation=15, catalog='IC')

        self.assertIsInstance(nearby_objects, list)
        self.assertEqual(len(nearby_objects), len(neighbors))
        self.assertEqual(str(nearby_objects[0][0]), str(neighbors[0][0]))
        self.assertEqual(nearby_objects[0][1], neighbors[0][1])

    def test_nearby_bad_value(self):
        """Return the right message if search radius value is out of range."""
        self.assertRaisesRegex(ValueError,
                               'The maximum search radius allowed is 10 degrees.',
                               pyongc.nearby, '01:24:33.78 +01:43:53.0', separation=601)

    def test_print_details_obj_galaxy(self):
        """Test that printDetails() output is formatted in the right way for galaxies."""
        obj_details = pyongc.printDetails('NGC1')
        expected = (
            "+-----------------------------------------------------------------------------+\n"
            "| Id: 5616      Name: NGC0001           Type: Galaxy                          |\n"
            "| R.A.: 00:07:15.84      Dec.: +27:42:29.1      Constellation: Peg            |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Major axis: 1.57'      Minor axis: 1.07'      Position angle: 112°          |\n"
            "| B-mag: 13.4    V-mag: N/A     J-mag: 10.78   H-mag: 10.02   K-mag: 9.76     |\n"
            "|                                                                             |\n"
            "| Surface brightness: 23.13     Hubble classification: Sb                     |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Other identifiers:                                                          |\n"
            "|    2MASX J00071582+2742291, IRAS 00047+2725, MCG +04-01-025, PGC 000564,    |\n"
            "|    UGC 00057                                                                |\n"
            "+-----------------------------------------------------------------------------+\n"
            )

        self.assertEqual(obj_details, expected)

    def test_print_details_obj_PN(self):
        """Test that printDetails() output is formatted in the right way for PNs."""
        obj_details = pyongc.printDetails('NGC40')
        expected = (
            "+-----------------------------------------------------------------------------+\n"
            "| Id: 5655      Name: NGC0040           Type: Planetary Nebula                |\n"
            "| R.A.: 00:13:01.03      Dec.: +72:31:19.0      Constellation: Cep            |\n"
            "| Common names:                                                               |\n"
            "|    Bow-Tie nebula                                                           |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Major axis: 0.8'       Minor axis: N/A        Position angle: N/A           |\n"
            "| B-mag: 11.27   V-mag: 11.89   J-mag: 10.89   H-mag: 10.8    K-mag: 10.38    |\n"
            "|                                                                             |\n"
            "| Central star identifiers:                                                   |\n"
            "|    HD 000826, HIP 001041, TYC 4302-01297-1                                  |\n"
            "|                                                                             |\n"
            "| Central star magnitudes:                                                    |\n"
            "|    U-mag: 11.14            B-mag: 11.82            V-mag: 11.58             |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Other identifiers:                                                          |\n"
            "|    C 002, IRAS 00102+7214, PN G120.0+09.8                                   |\n"
            "+-----------------------------------------------------------------------------+\n"
            )

        self.assertEqual(obj_details, expected)

    def test_print_details_obj_nebula(self):
        """Test that printDetails() output is formatted in the right way for nebulae."""
        obj_details = pyongc.printDetails('NGC6523')
        expected = (
            "+-----------------------------------------------------------------------------+\n"
            "| Id: 12544     Name: NGC6523           Type: Nebula                          |\n"
            "| R.A.: 18:03:41.27      Dec.: -24:22:48.6      Constellation: Sgr            |\n"
            "| Also known as:                                                              |\n"
            "|    M008, NGC6533                                                            |\n"
            "| Common names:                                                               |\n"
            "|    Lagoon Nebula                                                            |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Major axis: 45.0'      Minor axis: 30.0'      Position angle: N/A           |\n"
            "| B-mag: 5.0     V-mag: 5.8     J-mag: N/A     H-mag: N/A     K-mag: N/A      |\n"
            "|                                                                             |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Other identifiers:                                                          |\n"
            "|    LBN 25                                                                   |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| NED notes:                                                                  |\n"
            "|    Nominal position for NGC 6533 is -30 arcmin in error.                    |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| OpenNGC notes:                                                              |\n"
            "|    B-Mag taken from LEDA, V-mag taken from HEASARC's messier table          |\n"
            "+-----------------------------------------------------------------------------+\n"
            )

        self.assertEqual(obj_details, expected)


class TestDatabaseIntegrity(unittest.TestCase):
    """Check data integrity."""
    def test_data_integrity(self):
        allObjects = pyongc.listObjects()
        for item in allObjects:
            self.assertIsInstance(item.getId(), int)
            self.assertNotEqual(item.getType(), '')
            if item.getType() != 'Nonexistent object':
                coords = item.getCoords()
                self.assertIsInstance(coords, np.ndarray)
                self.assertEqual(coords.shape, (2, 3))
                self.assertNotEqual(item.getDec(), '')
                self.assertNotEqual(item.getRA(), '')
                self.assertNotEqual(item.getConstellation(), '')
                self.assertIsInstance(item.getDimensions(), tuple)
                self.assertIsInstance(item.getMagnitudes(), tuple)


if __name__ == '__main__':
    unittest.main()

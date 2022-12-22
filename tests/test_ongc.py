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

import pytest

import json
import mock
import numpy as np

from pyongc import ongc, exceptions
from pyongc.ongc import (
    _distance as distance, _limiting_coords as limiting_coords,
    _str_to_coords as str_to_coords)


class TestDsoClass():
    """Test that Dso objects are created in the right way and that data
    is retrieved correctly.
    """
    @mock.patch('pyongc.ongc.DBPATH', 'badpath')
    def test_fail_database_connection(self):
        """Test a failed connection to database."""
        with pytest.raises(OSError) as excinfo:
            ongc.Dso('NGC0001')
        assert 'There was a problem accessing database file' in str(excinfo.value)

    def test_dso_creation_error(self):
        """Test we get a type error if user doesn't input a string."""
        with pytest.raises(TypeError) as excinfo:
            ongc.Dso(1234)
        assert 'Wrong type as parameter' in str(excinfo.value)

    def test_name_recognition_NGC(self):
        """Test the recognition of a NGC/IC identifier."""
        assert ongc.Dso('ngc1').name == 'NGC0001'
        assert ongc.Dso('ic 1').name == 'IC0001'
        assert ongc.Dso('ic80 ned1').name == 'IC0080 NED01'
        assert ongc.Dso('ngc61a').name == 'NGC0061A'
        with pytest.raises(exceptions.UnknownIdentifier) as excinfo:
            ongc.Dso('NGC77777')
        assert 'not recognized' in str(excinfo.value)
        with pytest.raises(exceptions.UnknownIdentifier) as excinfo:
            ongc.Dso('NGC0001ABC')
        assert 'not recognized' in str(excinfo.value)
        with pytest.raises(exceptions.ObjectNotFound) as excinfo:
            ongc.Dso('NGC0001A')
        assert 'not found in the database' in str(excinfo.value)

    def test_name_recognition_Barnard(self):
        """Test the recognition of a Barnard identifier."""
        assert ongc.Dso('b33').name == 'B033'

    def test_name_recognition_Caldwell(self):
        """Test the recognition of a Caldwell identifier."""
        assert ongc.Dso('c9').name == 'C009'

    def test_name_recognition_ESO(self):
        """Test the recognition of a ESO identifier."""
        assert ongc.Dso('eso56-115').name == 'ESO056-115'

    def test_name_recognition_Harvard(self):
        """Test the recognition of a Harvard identifier."""
        assert ongc.Dso('H5').name == 'H05'

    def test_name_recognition_Hickson(self):
        """Test the recognition of a HCG identifier."""
        assert ongc.Dso('hcg79').name == 'HCG079'

    def test_name_recognition_LBN(self):
        """Test the recognition of a LBN identifier."""
        assert ongc.Dso('LBN741').name == 'NGC1333'

    def test_name_recognition_Melotte(self):
        """Test the recognition of a Mel identifier."""
        assert ongc.Dso('mel111').name == 'Mel111'

    def test_name_recognition_Messier(self):
        """Test the recognition of a Messier identifier."""
        assert ongc.Dso('M1').name == 'NGC1952'
        with pytest.raises(exceptions.UnknownIdentifier) as excinfo:
            ongc.Dso('M15A')
        assert 'not recognized' in str(excinfo.value)

    def test_name_recognition_M102(self):
        """Test M102 == M101."""
        assert ongc.Dso('M102').name == ongc.Dso('M101').name

    def test_name_recognition_MWSC(self):
        """Test the recognition of a MWSC identifier."""
        assert ongc.Dso('MWSC146').name == 'IC0166'

    def test_name_recognition_PGC(self):
        """Test the recognition of a PGC identifier."""
        assert ongc.Dso('PGC10540').name == 'IC0255'
        assert ongc.Dso('leda 10540').name == 'IC0255'

    def test_name_recognition_UGC(self):
        """Test the recognition of a UGC identifier."""
        assert ongc.Dso('UGC9965').name == 'IC1132'

    def test_duplicate_resolving(self):
        """Test that a duplicated object is returned as himself when asked to do so."""
        assert ongc.Dso('ngc20').name == 'NGC0006'
        assert ongc.Dso('ngc20', returndup=True).name == 'NGC0020'
        assert ongc.Dso('ic555').name == 'IC0554'

    def test_object_print(self):
        """Test basic object data representation."""
        obj = ongc.Dso('NGC1')

        expected = 'NGC0001, Galaxy in Peg'
        actual = str(obj)
        assert actual == expected

    def test_dec(self):
        """Test Declination as string is returned correctly."""
        obj = ongc.Dso('IC15')
        expected = '-00:03:40.6'
        assert obj.dec == expected
        # Nonexistent object
        obj = ongc.Dso('IC1064')
        expected = 'N/A'
        assert obj.dec == expected

    def test_ra(self):
        """Test Right Ascension as string is returned correctly."""
        obj = ongc.Dso('NGC475')
        expected = '01:20:02.00'
        assert obj.ra == expected
        # Nonexistent object
        obj = ongc.Dso('IC1064')
        expected = 'N/A'
        assert obj.ra == expected

    def test_coords(self):
        """Test coords property."""
        obj = ongc.Dso('NGC1')
        np.testing.assert_allclose(obj.coords, ([[0., 7., 15.84], [27., 42., 29.1]]), 1e-12)

    def test_coords_nonexistent(self):
        """Test coords property on a Nonexistent object which doesn't have coords."""
        obj = ongc.Dso('IC1064')
        assert obj.coords is None

    def test_rad_coords(self):
        """Test rad_coords."""
        obj = ongc.Dso('NGC1')
        np.testing.assert_allclose(obj.rad_coords,
                                   ([0.03169517921621703, 0.48359728358363213]),
                                   1e-12)

    def test_rad_coords_nonexistent(self):
        """Test rad_coords property on a Nonexistent object which doesn't have coords."""
        obj = ongc.Dso('IC1064')
        assert obj.rad_coords is None

    def test_cstar_data(self):
        """Test retrieving Planetary Nebulae central star data."""
        # With central star identifiers
        obj = ongc.Dso('NGC1535')
        expected = (['BD -13 842', 'HD 26847'], None, 12.19, 12.18)
        assert obj.cstar_data == expected
        # Without central star identifiers
        obj = ongc.Dso('IC289')
        expected = (None, None, 15.1, 15.9)
        assert obj.cstar_data == expected

    def test_identifiers(self):
        """Test identifiers property."""
        obj = ongc.Dso('NGC650')
        expected = ('M076', ['NGC0651'], None, ['Barbell Nebula', 'Cork Nebula',
                    'Little Dumbbell Nebula'], ['2MASX J01421808+5134243', 'IRAS 01391+5119',
                    'PN G130.9-10.5'])
        assert obj.identifiers == expected

        obj = ongc.Dso('IC5003')
        expected = (None,
                    None,
                    ['IC5029', 'IC5039', 'IC5046'],
                    None,
                    ['2MASX J20431434-2951122', 'ESO 463-020', 'ESO-LV 463-0200',
                     'IRAS 20401-3002', 'MCG -05-49-001', 'PGC 065249'])
        assert obj.identifiers == expected

    def test_magnitudes(self):
        """Test magnitudes property."""
        obj = ongc.Dso('IC2')

        expected = (15.46, None, 12.26, 11.48, 11.17)
        assert obj.magnitudes == expected

    def test_notes(self):
        """Test notes property."""
        obj = ongc.Dso('NGC6543')

        expected = ('Additional radio sources may contribute to the WMAP flux.',
                    'The fainter outer shell has a diameter of 5.5 arcmin ca.')
        assert obj.notes == expected

    @pytest.mark.parametrize('obj,expected', [pytest.param('M45', True),
                                              pytest.param('IC1', False)])
    def test_notngc(self, obj, expected):
        """Test notngc property."""
        obj = ongc.get(obj)

        assert obj.notngc is expected

    @pytest.mark.parametrize('obj,expected', [pytest.param('M13', 0.0813),
                                              pytest.param('IC1', None)])
    def test_parallax(self, obj, expected):
        """Test parallax property."""
        obj = ongc.get(obj)

        assert obj.parallax == expected

    @pytest.mark.parametrize('obj,expected', [pytest.param('M13', -2.56),
                                              pytest.param('IC1', None)])
    def test_pmdec(self, obj, expected):
        """Test pm_dec property."""
        obj = ongc.get(obj)

        assert obj.pm_dec == expected

    @pytest.mark.parametrize('obj,expected', [pytest.param('M13', -3.18),
                                              pytest.param('IC1', None)])
    def test_pmra(self, obj, expected):
        """Test pm_ra property."""
        obj = ongc.get(obj)

        assert obj.pm_ra == expected

    @pytest.mark.parametrize('obj,expected', [pytest.param('M13', -244),
                                              pytest.param('IC1', None)])
    def test_radvel(self, obj, expected):
        """Test radvel property."""
        obj = ongc.get(obj)

        assert obj.radvel == expected

    @pytest.mark.parametrize('obj,expected', [pytest.param('M13', -0.000815),
                                              pytest.param('IC1', None)])
    def test_redshift(self, obj, expected):
        """Test redshift property."""
        obj = ongc.get(obj)

        assert obj.redshift == expected

    def test_to_json_galaxy(self):
        """Test galaxy data exported to JSON."""
        obj = ongc.Dso('NGC1')
        json_str = obj.to_json()
        assert json_str is not None

        obj_dict = json.loads(json_str)
        assert 'name' in obj_dict
        assert obj_dict['name'] == 'NGC0001'
        assert 'surface brightness' in obj_dict
        assert 'hubble classification' in obj_dict
        assert obj_dict['coordinates']['radians coords'] is not None

    def test_to_json_PN(self):
        """Test PN data exported to JSON."""
        obj = ongc.Dso('NGC650')
        json_str = obj.to_json()
        assert json_str is not None

        obj_dict = json.loads(json_str)
        assert 'name' in obj_dict
        assert obj_dict['name'] == 'NGC0650'
        assert 'central star data' in obj_dict
        assert obj_dict['coordinates']['radians coords'] is not None

    def test_to_json_no_coords(self):
        """Test object with no coords exported to JSON."""
        obj = ongc.Dso('IC1064')
        json_str = obj.to_json()
        assert json_str is not None

        obj_dict = json.loads(json_str)
        assert 'name' in obj_dict
        assert obj_dict['name'] == 'IC1064'
        assert obj_dict['coordinates']['radians coords'] is None

    def test_xephem_format(self):
        """Test object representation in XEphem format."""
        # Galaxy pair
        obj = ongc.Dso('IC1008')
        expected = 'IC1008|IC4414,f|A,14:23:42.59,+28:20:52.3,,48.00||'
        assert obj.xephemFormat() == expected

        # Globular cluster
        obj = ongc.Dso('NGC1904')
        expected = 'NGC1904|M079,f|C,05:24:10.59,-24:31:27.2,9.21,,432.00||'
        assert obj.xephemFormat() == expected

        # Double star
        obj = ongc.Dso('IC470')
        expected = 'IC0470,f|D,07:23:31.50,+46:04:43.2,13.89,,||'
        assert obj.xephemFormat() == expected

        # Nebula
        obj = ongc.Dso('IC2087')
        expected = 'IC2087,f|F,04:39:59.97,+25:44:32.0,10.67,,240.00|240.00|'
        assert obj.xephemFormat() == expected

        # Spiral galaxy
        obj = ongc.Dso('NGC1')
        expected = 'NGC0001,f|G,00:07:15.84,+27:42:29.1,13.69,,94.20|64.20|112'
        assert obj.xephemFormat() == expected

        # Elliptical galaxy
        obj = ongc.Dso('IC3')
        expected = 'IC0003,f|H,00:12:06.09,-00:24:54.8,14.78,,55.80|40.20|53'
        assert obj.xephemFormat() == expected

        # Dark nebula
        obj = ongc.Dso('B33')
        expected = 'B033|Horsehead Nebula,f|K,05:40:59.00,-02:27:30.0,,360.00|240.00|90'
        assert obj.xephemFormat() == expected

        # Emission nebula
        obj = ongc.Dso('NGC1936')
        expected = 'NGC1936|IC2127,f|N,05:22:13.96,-67:58:41.9,11.6,,60.00|60.00|'
        assert obj.xephemFormat() == expected

        # Open cluster
        obj = ongc.Dso('IC4725')
        expected = 'IC4725|M025,f|O,18:31:46.77,-19:06:53.8,5.29,,846.00||'
        assert obj.xephemFormat() == expected

        # Planetary nebula
        obj = ongc.Dso('NGC650')
        expected = 'NGC0650|M076|NGC0651|Barbell Nebula|Cork Nebula|Little Dumbbell Nebula,f|P,' \
            '01:42:19.69,+51:34:31.7,12.2,,67.20||'
        assert obj.xephemFormat() == expected

        # SNR
        obj = ongc.Dso('NGC1952')
        expected = 'NGC1952|M001|Crab Nebula,f|R,05:34:31.97,+22:00:52.1,8.4,,480.00|240.00|'
        assert obj.xephemFormat() == expected

        # Star
        obj = ongc.Dso('IC124')
        expected = 'IC0124,f|S,01:29:09.08,-01:56:13.3,14.4,,||'
        assert obj.xephemFormat() == expected

        # Star cluster + nebula
        obj = ongc.Dso('NGC1976')
        expected = 'NGC1976|M042|Great Orion Nebula|Orion Nebula,f|U,' \
            '05:35:16.48,-05:23:22.8,4.0,,5400.00|3600.00|'
        assert obj.xephemFormat() == expected

        # Unknown - other
        obj = ongc.Dso('NGC405')
        expected = 'NGC0405,f,01:08:34.11,-46:40:06.6,7.17,,||'
        assert obj.xephemFormat() == expected


class TestDsoMethods():
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
        assert limiting_coords(coords, 2) == expected
        # Negative dec
        coords = np.array([[0., 11., 0.88], [-12., 49., 22.3]])
        expected = (' AND (ra BETWEEN 0.013153964795863934 AND 0.08296713487563712)'
                    ' AND (dec BETWEEN -0.25870773095471394 AND -0.18889456087494075)')
        assert limiting_coords(coords, 2) == expected

    def test_limiting_coords_rad(self):
        """Test query filters for coordinates expressed in radians."""
        # Crossing 0 RA
        coords = np.array([[0., 2., 0.], [27., 43., 3.6]])
        expected = (' AND (ra <= 0.04363323129985824 OR ra >= 6.257005368399671)'
                    ' AND (dec BETWEEN 0.44885795926372835 AND 0.5186711293435016)')
        assert limiting_coords(coords, 2) == expected
        coords = np.array([[23., 58., 0.], [27., 43., 3.6]])
        expected = (' AND (ra <= 0.02617993877991509 OR ra >= 6.239552075879729)'
                    ' AND (dec BETWEEN 0.44885795926372835 AND 0.5186711293435016)')
        assert limiting_coords(coords, 2) == expected
        # Max declination
        coords = np.array([[0., 11., 0.88], [89., 0., 0.]])
        expected = (' AND (ra BETWEEN 0.013153964795863934 AND 0.08296713487563712)'
                    ' AND (dec BETWEEN 1.5184364492350666 AND 1.5707963267948966)')
        assert limiting_coords(coords, 2) == expected
        # Min declination
        coords = np.array([[0., 11., 0.88], [-89., 0., 0.]])
        expected = (' AND (ra BETWEEN 0.013153964795863934 AND 0.08296713487563712)'
                    ' AND (dec BETWEEN -1.5707963267948966 AND -1.5184364492350666)')
        assert limiting_coords(coords, 2) == expected

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
        with pytest.raises(exceptions.InvalidCoordinates) as excinfo:
            str_to_coords(bad_coords)
        assert f'This text cannot be recognized as coordinates: {bad_coords}' == str(excinfo.value)

    def test_get_return_obj(self):
        """The method should return the required object."""
        obj = ongc.get('NGC1')

        assert obj.name == 'NGC0001'

    def test_get_invalid_identifier(self):
        """An invalid identifier should return None."""
        obj = ongc.get('NGC100000')

        assert obj is None

    def test_get_not_found(self):
        """If the object is not found should return None."""
        obj = ongc.get('NGC1a')

        assert obj is None

    def test_get_separation_raw(self):
        """Test that the calculated apparent angular separation between two objects
        is correct and reports the raw data to user.
        """
        obj1 = ongc.Dso('NGC6070')
        obj2 = ongc.Dso('NGC6118')

        expected = (4.207483963913541, 2.9580416666666864, -2.9927499999999996)
        assert ongc.getSeparation(obj1, obj2) == expected

    def test_get_separation_friendly(self):
        """Test that the calculated apparent angular separation between two objects
        is correct and returns a user friendly output.
        """
        expected = '4° 12m 26.94s'
        assert ongc.getSeparation('NGC6118', 'NGC6070', style='text') == expected

    def test_get_separation_bad_object(self):
        """Raise exception if one object hasn't got registered coords."""
        obj1 = ongc.Dso('NGC6070')
        obj2 = ongc.Dso('IC1064')
        with pytest.raises(exceptions.InvalidCoordinates) as excinfo:
            ongc.getSeparation(obj1, obj2)
        assert 'One object hasn\'t got registered coordinates.' == str(excinfo.value)

    def test_get_neighbors(self):
        """Test that neighbors are correctly found and returned."""
        obj1 = ongc.Dso('NGC521')

        neighbors = ongc.getNeighbors(obj1, 15)
        expectedListLength = 2
        expectedNearest = 'IC1694, Galaxy in Cet'
        expectedNearestSeparation = 0.13726168561780452

        assert type(neighbors) is list
        assert len(neighbors) == expectedListLength
        assert str(neighbors[0][0]) == expectedNearest
        assert np.isclose(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_negative_dec(self):
        """Test that neighbors are correctly found and returned - with negative Dec value."""
        obj1 = ongc.Dso('IC60')

        neighbors = ongc.getNeighbors(obj1, 30)
        expectedListLength = 1
        expectedNearest = 'IC0058, Galaxy in Cet'
        expectedNearestSeparation = 0.4064105387726472

        assert type(neighbors) is list
        assert len(neighbors) == expectedListLength
        assert str(neighbors[0][0]) == expectedNearest
        assert np.isclose(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_above0ra(self):
        """Test that neighbors are correctly found and returned - with RA just above 00h."""
        obj1 = ongc.Dso('IC1')

        neighbors = ongc.getNeighbors(obj1, 15)
        expectedListLength = 2
        expectedNearest = 'NGC0016, Galaxy in Peg'
        expectedNearestSeparation = 0.1378555838270968

        assert type(neighbors) is list
        assert len(neighbors) == expectedListLength
        assert str(neighbors[0][0]) == expectedNearest
        assert np.isclose(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_below0ra(self):
        """Test that neighbors are correctly found and returned - with RA just below 00h."""
        obj1 = ongc.Dso('IC1523')

        neighbors = ongc.getNeighbors(obj1, 60)
        expectedListLength = 1
        expectedNearest = 'NGC7802, Galaxy in Psc'
        expectedNearestSeparation = 0.7874886760327793

        assert type(neighbors) is list
        assert len(neighbors) == expectedListLength
        assert str(neighbors[0][0]) == expectedNearest
        assert np.isclose(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_with_filter(self):
        """Test that neighbors are correctly found and returned."""
        neighbors = ongc.getNeighbors('NGC521', 15, catalog='NGC')
        expectedListLength = 1
        expectedNearest = 'NGC0533, Galaxy in Cet'
        expectedNearestSeparation = 0.24140243942744602

        assert type(neighbors) is list
        assert len(neighbors) == expectedListLength
        assert str(neighbors[0][0]) == expectedNearest
        assert np.isclose(neighbors[0][1], expectedNearestSeparation)

    def test_get_neighbors_bad_value(self):
        """Raise exception if search radius value is out of range."""
        with pytest.raises(ValueError) as excinfo:
            ongc.getNeighbors('IC1', 601)
        assert 'The maximum search radius allowed is 10 degrees.' == str(excinfo.value)

    def test_get_neighbors_bad_object(self):
        """Raise exception if starting object hasn't got registered coords."""
        with pytest.raises(exceptions.InvalidCoordinates) as excinfo:
            ongc.getNeighbors('IC1064', 15)
        assert 'Starting object hasn\'t got registered coordinates.' == str(excinfo.value)

    def test_list_all_objects(self):
        """Test the listObjects() method without filters.
        It should return all objects from database.
        """
        objectList = ongc.listObjects()

        assert len(objectList) == 13992
        assert type(objectList[0]) is ongc.Dso

    def test_list_objects_filter_catalog_NGC(self):
        """Test the listObjects() method with catalog filter applied."""
        objectList = ongc.listObjects(catalog='NGC')

        assert len(objectList) == 8373

    def test_list_objects_filter_catalog_IC(self):
        """Test the listObjects() method with catalog filter applied."""
        objectList = ongc.listObjects(catalog='IC')

        assert len(objectList) == 5595

    def test_list_objects_filter_catalog_M(self):
        """Test the listObjects() method with catalog filter applied."""
        objectList = ongc.listObjects(catalog='M')

        assert len(objectList) == 110

    def test_list_objects_filter_type(self):
        """Test the listObjects() method with type filter applied.
        Duplicated objects are not resolved to the main object.
        """
        objectList = ongc.listObjects(type=['Dup', ])

        assert len(objectList) == 652
        assert str(objectList[0]) == 'IC0011, Duplicated record in Cas'

    def test_list_objects_filter_multiple_types(self):
        """Test the listObjects() method with multiple types filter."""
        objectList = ongc.listObjects(type=['*', '**', ])

        assert len(objectList) == 790

    def test_list_objects_filter_constellation(self):
        """Test the listObjects() method with constellation filter applied."""
        objectList = ongc.listObjects(constellation=['and', 'Boo', ])

        assert len(objectList) == 737

    def test_list_objects_filter_size(self):
        """Test the listObjects() method with size filters applied."""
        objectList = ongc.listObjects(minsize=15, maxsize=20)

        assert len(objectList) == 41

    def test_list_objects_with_no_size(self):
        """Test the listObjects() method to list objects without size."""
        objectList = ongc.listObjects(maxsize=0)

        assert len(objectList) == 1967

    def test_list_objects_filter_mag(self):
        """Test the listObjects() method with magnitudes filters applied."""
        objectList = ongc.listObjects(uptobmag=8, uptovmag=10)

        assert len(objectList) == 175

    def test_list_objects_filter_minra(self):
        """List objects with RA greater than minra."""
        objectList = ongc.listObjects(minra=358)

        assert len(objectList) == 56

    def test_list_objects_filter_maxra(self):
        """List objects with RA lower than maxra."""
        objectList = ongc.listObjects(maxra=2)

        assert len(objectList) == 68

    def test_list_objects_filter_ra_between(self):
        """List objects with RA between minra and maxra."""
        objectList = ongc.listObjects(minra=1, maxra=2)

        assert len(objectList) == 33

    def test_list_objects_filter_ra_between_crossing_zero(self):
        """List objects with RA between minra and maxra crossing 0h."""
        objectList = ongc.listObjects(minra=359, maxra=1)

        assert len(objectList) == 69

    def test_list_objects_filter_mindec(self):
        """List objects with Dec above mindec."""
        objectList = ongc.listObjects(mindec=85)

        assert len(objectList) == 9

    def test_list_objects_filter_maxdec(self):
        """List objects with RA below maxdec."""
        objectList = ongc.listObjects(maxdec=-85)

        assert len(objectList) == 4

    def test_list_objects_filter_dec_between(self):
        """List objects with Dec between mindec and maxdec."""
        objectList = ongc.listObjects(mindec=-1, maxdec=1)

        assert len(objectList) == 264

    def test_list_objects_by_name(self):
        """Test the listObjects() method to list objects with the provided common name."""
        objectList = ongc.listObjects(cname='california')

        assert len(objectList) == 1
        assert str(objectList[0]) == 'NGC1499, Nebula in Per'

    def test_list_objects_with_name(self):
        """Test the listObjects() method to list objects with common name."""
        objectList = ongc.listObjects(withname=True)

        assert len(objectList) == 145

    def test_list_objects_without_name(self):
        """Test the listObjects() method to list objects without common name."""
        objectList = ongc.listObjects(withname=False)

        assert len(objectList) == 13847

    def test_list_objects_wrong_filter(self):
        """Test the listObjects() method when an unsupported filter is used."""
        with pytest.raises(ValueError) as excinfo:
            ongc.listObjects(catalog='NGC', name='NGC1')
        assert 'Wrong filter name.' == str(excinfo.value)

    def test_list_objects_wrong_catalog(self):
        """Test the listObjects() method with a wrong catalog name."""
        with pytest.raises(ValueError) as excinfo:
            ongc.listObjects(catalog='UGC')
        assert 'Wrong value for catalog filter.' in str(excinfo.value)

    def test_nearby(self):
        """Test that searching neighbors by coords works properly."""
        obj = ongc.Dso('NGC521')
        objCoords = ' '.join([obj.ra, obj.dec])

        neighbors = ongc.getNeighbors(obj, 15)
        nearby_objects = ongc.nearby(objCoords, separation=15)

        assert type(nearby_objects) is list
        assert len(nearby_objects) == len(neighbors)+1
        assert str(nearby_objects[0][0]) == str(obj)
        assert nearby_objects[0][1] == 0
        assert str(nearby_objects[1][0]) == str(neighbors[0][0])
        assert nearby_objects[1][1] == neighbors[0][1]

    def test_nearby_with_filter(self):
        """Test that neighbors are correctly filtered."""
        obj = ongc.Dso('NGC521')
        objCoords = ' '.join([obj.ra, obj.dec])

        neighbors = ongc.getNeighbors('NGC521', 15, catalog='IC')
        nearby_objects = ongc.nearby(objCoords, separation=15, catalog='IC')

        assert type(nearby_objects) is list
        assert len(nearby_objects) == len(neighbors)
        assert str(nearby_objects[0][0]) == str(neighbors[0][0])
        assert nearby_objects[0][1] == neighbors[0][1]

    def test_nearby_bad_value(self):
        """Return the right message if search radius value is out of range."""
        with pytest.raises(ValueError) as excinfo:
            ongc.nearby('01:24:33.78 +01:43:53.0', separation=601)
        assert 'The maximum search radius allowed is 10 degrees.' == str(excinfo.value)

    def test_print_details_obj_galaxy(self):
        """Test that printDetails() output is formatted in the right way for galaxies."""
        obj_details = ongc.printDetails('NGC1')
        expected = (
            "+-----------------------------------------------------------------------------+\n"
            "| Id: 5596      Name: NGC0001           Type: Galaxy                          |\n"
            "| R.A.: 00:07:15.84      Dec.: +27:42:29.1      Constellation: Peg            |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Major axis: 1.57'      Minor axis: 1.07'      Position angle: 112°          |\n"
            "| B-mag: 13.69   V-mag: 12.93   J-mag: 10.78   H-mag: 10.02   K-mag: 9.76     |\n"
            "|                                                                             |\n"
            "| Parallax: N/A          Radial velocity: 4536km/s      Redshift: 0.015245    |\n"
            "|                                                                             |\n"
            "| Proper apparent motion in RA: N/A                                           |\n"
            "| Proper apparent motion in Dec: N/A                                          |\n"
            "|                                                                             |\n"
            "| Surface brightness: 23.13     Hubble classification: Sb                     |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Other identifiers:                                                          |\n"
            "|    2MASX J00071582+2742291, IRAS 00047+2725, MCG +04-01-025, PGC 000564,    |\n"
            "|    UGC 00057                                                                |\n"
            "+-----------------------------------------------------------------------------+\n"
            )

        assert obj_details == expected

    def test_print_details_obj_PN(self):
        """Test that printDetails() output is formatted in the right way for PNs."""
        obj_details = ongc.printDetails('NGC40')
        expected = (
            "+-----------------------------------------------------------------------------+\n"
            "| Id: 5635      Name: NGC0040           Type: Planetary Nebula                |\n"
            "| R.A.: 00:13:01.03      Dec.: +72:31:19.0      Constellation: Cep            |\n"
            "| Common names:                                                               |\n"
            "|    Bow-Tie nebula                                                           |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Major axis: 0.8'       Minor axis: N/A        Position angle: N/A           |\n"
            "| B-mag: 11.27   V-mag: 11.89   J-mag: 10.89   H-mag: 10.8    K-mag: 10.38    |\n"
            "|                                                                             |\n"
            "| Parallax: 0.5041mas    Radial velocity: -20km/s       Redshift: -0.000068   |\n"
            "|                                                                             |\n"
            "| Proper apparent motion in RA: -7.249mas/yr                                  |\n"
            "| Proper apparent motion in Dec: -1.811mas/yr                                 |\n"
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

        assert obj_details == expected

    def test_print_details_obj_nebula(self):
        """Test that printDetails() output is formatted in the right way for nebulae."""
        obj_details = ongc.printDetails('NGC6523')
        expected = (
            "+-----------------------------------------------------------------------------+\n"
            "| Id: 12552     Name: NGC6523           Type: Nebula                          |\n"
            "| R.A.: 18:03:41.27      Dec.: -24:22:48.6      Constellation: Sgr            |\n"
            "| Also known as:                                                              |\n"
            "|    M008, NGC6533                                                            |\n"
            "| Common names:                                                               |\n"
            "|    Lagoon Nebula                                                            |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Major axis: 45.0'      Minor axis: 30.0'      Position angle: N/A           |\n"
            "| B-mag: 5.0     V-mag: 5.8     J-mag: N/A     H-mag: N/A     K-mag: N/A      |\n"
            "|                                                                             |\n"
            "| Parallax: N/A          Radial velocity: 4km/s         Redshift: 0.000013    |\n"
            "|                                                                             |\n"
            "| Proper apparent motion in RA: N/A                                           |\n"
            "| Proper apparent motion in Dec: N/A                                          |\n"
            "|                                                                             |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| Other identifiers:                                                          |\n"
            "|    LBN 25                                                                   |\n"
            "+-----------------------------------------------------------------------------+\n"
            "| NED notes:                                                                  |\n"
            "|    Nominal position for NGC 6533 is -30 arcmin in error.                    |\n"
            "+-----------------------------------------------------------------------------+\n"
            )

        assert obj_details == expected


class TestDatabaseIntegrity():
    """Check data integrity."""
    def test_data_integrity(self):
        allObjects = ongc.listObjects()
        for item in allObjects:
            assert type(item.id) is int
            assert item.type != ''
            if item.type != 'Nonexistent object':
                # Be sure all objects have registered coordinates
                assert item.coords is not None
                assert item.coords.shape == (2, 3)
                assert item.rad_coords is not None
                assert item.dec != ''
                assert item.ra != ''
                assert item.constellation != ''
            # These are always tuple even if all values are None
            assert type(item.dimensions) is tuple
            assert type(item.magnitudes) is tuple

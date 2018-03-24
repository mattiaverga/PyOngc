import unittest
from pyongc import ongc


class TestDsoClass(unittest.TestCase):
    """Test that Dso objects are created in the right way and that data
    is retrieved correctly.
    """
    def test_nameRecognition(self):
        """Test the regex used to convert the name of the object inputted by the user
        to the correct form.
        """
        self.assertEqual(ongc.Dso('ngc1')._name, 'NGC0001')
        self.assertEqual(ongc.Dso('ic 1')._name, 'IC0001')
        self.assertEqual(ongc.Dso('ic80 ned1')._name, 'IC0080 NED01')
        self.assertEqual(ongc.Dso('ngc61a')._name, 'NGC0061A')
        self.assertRaisesRegex(ValueError, 'Wrong object name', ongc.Dso, 'M15')
        self.assertRaisesRegex(ValueError, 'not found in the database', ongc.Dso, 'NGC0001A')

    def test_duplicateResolving(self):
        """Test that a duplicated object is returned as himself when asked to do so."""
        self.assertEqual(ongc.Dso('ngc20')._name, 'NGC0006')
        self.assertEqual(ongc.Dso('ngc20', returnDup=True)._name, 'NGC0020')

    def test_objectPrint(self):
        """Test basic object data representation."""
        obj = ongc.Dso('NGC1')

        expected = 'NGC0001, Galaxy in Peg'
        actual = str(obj)
        self.assertEqual(actual, expected)

    def test_successfulGetCoordinates(self):
        """Test succesful getCoords() method."""
        obj = ongc.Dso('NGC1')

        expected = ((0, 7, 15.84), ('+', 27, 42, 29.1))
        self.assertEqual(obj.getCoords(), expected)

    def test_nonexistentGetCoordinates(self):
        """Test getCoords() on a Nonexistent object which doesn't have coords."""
        obj = ongc.Dso('IC1064')

        expected = 'Object named IC1064 has no coordinates in database.'
        with self.assertRaisesRegex(ValueError, expected):
            obj.getCoords()

    def test_getPNcentralStarData(self):
        """Test retrieving Planetary Nebulaes central star data."""
        obj = ongc.Dso('NGC1535')

        expected = (['BD -13 842', 'HD 26847'], None, 12.19, 12.18)
        self.assertEqual(obj.getCStarData(), expected)

    def test_getObjectIdentifiers(self):
        """Test getIdentifiers() method."""
        obj = ongc.Dso('NGC650')

        expected = ('M76', ['NGC0651'], None, ['Barbell Nebula', 'Cork Nebula',
                    'Little Dumbbell Nebula'], ['2MASX J01421808+5134243', 'IRAS 01391+5119',
                    'PN G130.9-10.5'])
        self.assertEqual(obj.getIdentifiers(), expected)

    def test_getMagnitudes(self):
        """Test getMagnitudes() method."""
        obj = ongc.Dso('NGC1')

        expected = (13.4, None, 10.78, 10.02, 9.76)
        self.assertEqual(obj.getMagnitudes(), expected)

    def test_getMainIdentifier(self):
        """Test getName() method."""
        obj = ongc.Dso('NGC1')

        expected = 'NGC0001'
        self.assertEqual(obj.getName(), expected)

    def test_getObjectNotes(self):
        """Test getNotes() method."""
        obj = ongc.Dso('NGC6543')

        expected = ('Additional radio sources may contribute to the WMAP flux.',
                    'Dimensions taken from LEDA')
        self.assertEqual(obj.getNotes(), expected)

    def test_xephemFormat(self):
        """Test object representation in XEphem format."""
        obj = ongc.Dso('NGC1')

        expected = 'NGC0001,f|G,00:07:15.84,+27:42:29.1,13.4,,94.2|64.2|1.07'
        self.assertEqual(obj.xephemFormat(), expected)


class TestDsoMethods(unittest.TestCase):
    """Test functions about DS Objects."""
    def test_calculateSeparationRaw(self):
        """Test that the calculated apparent angular separation between two objects
        is correct and report the raw data to user.
        """
        obj1 = ongc.Dso('NGC1')
        obj2 = ongc.Dso('NGC2')

        expected = (0.030089273732482536, 0.005291666666666788, -0.02972222222221896)
        self.assertEqual(ongc.getSeparation(obj1, obj2), expected)

    def test_calculateSeparationFriendly(self):
        """Test that the calculated apparent angular separation between two objects
        is correct and give a user friendly output.
        """
        obj1 = ongc.Dso('NGC1')
        obj2 = ongc.Dso('NGC2')

        expected = '0° 1m 48.32s'
        self.assertEqual(ongc.getSeparation(obj1, obj2, style='text'), expected)


class TestDatabaseIntegrity(unittest.TestCase):
    """Check data integrity."""
    def test_dataIntegrity(self):
        allObjects = ongc.listObjects()
        for item in allObjects:
            self.assertIsInstance(item.getId(), int)
            self.assertNotEqual(item.getType(), '')
            if item.getType() != 'Nonexistent object':
                self.assertIsInstance(item.getCoords(), tuple)
                self.assertNotEqual(item.getDec(), '')
                self.assertNotEqual(item.getRA(), '')
                self.assertNotEqual(item.getConstellation(), '')
                self.assertIsInstance(item.getDimensions(), tuple)
                self.assertIsInstance(item.getMagnitudes(), tuple)


if __name__ == '__main__':
    unittest.main()

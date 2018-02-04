import unittest
from pyongc import ongc

class TestDsoClass(unittest.TestCase):
        """Test that Dso objects are created in the right way."""
        def test_nameRecognition(self):
                """Test the regex used to convert the name of the object inputted by the user to the
                correct form.
                """
                self.assertEqual(ongc.Dso("ngc1")._name, 'NGC0001')
                self.assertEqual(ongc.Dso("ic 1")._name, 'IC0001')
                self.assertEqual(ongc.Dso("ic80 ned1")._name, 'IC0080 NED01')
                self.assertEqual(ongc.Dso("ngc61a")._name, 'NGC0061A')
                self.assertRaisesRegexp(ValueError, "Wrong object name", ongc.Dso, "M15")
                self.assertRaisesRegexp(ValueError, "not found in the database", ongc.Dso, "NGC0001A")
                
        def test_duplicateResolving(self):
                """Test that a duplicated object is returned as himself when asked to do so."""
                self.assertEqual(ongc.Dso("ngc20")._name, 'NGC0006')
                self.assertEqual(ongc.Dso("ngc20", returnDup=True)._name, 'NGC0020')
        
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

from epyt import epanet, networks
import unittest
import os

DIRNAME = os.path.dirname(networks.__file__)

class update23(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        # Create EPANET object using the INP file
        inpname = os.path.join(DIRNAME, 'asce-tf-wdst', 'Net1.inp')
        self.epanetClass = epanet(inpname)


    def tearDown(self):
        """Call after every test case."""
        self.epanetClass.unload()

    """ ------------------------------------------------------------------------- """
    def test_setCurveType(self):
        #all 5 possible types
        self.epanetClass.setCurveType(1, 0)
        self.assertEqual( self.epanetClass.getCurveType(1),
                         ('VOLUME'), 'Wrong Curve Type comment output')
        self.epanetClass.setCurveType(1, 1)
        self.assertEqual(self.epanetClass.getCurveType(1),
                         ('PUMP'), 'Wrong Curve Type comment output')
        self.epanetClass.setCurveType(1, 2)
        self.assertEqual(self.epanetClass.getCurveType(1),
                         ('EFFICIENCY'), 'Wrong Curve Type comment output')
        self.epanetClass.setCurveType(1, 3)
        self.assertEqual(self.epanetClass.getCurveType(1),
                         ('HEADLOSS'), 'Wrong Curve Type comment output')
        self.epanetClass.setCurveType(1, 4)
        self.assertEqual(self.epanetClass.getCurveType(1),
                         ('GENERAL'), 'Wrong Curve Type comment output')

if __name__ == "__main__":
    unittest.main()

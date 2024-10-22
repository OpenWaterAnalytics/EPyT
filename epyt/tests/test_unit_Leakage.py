import unittest
import math
from epyt import epanet

class TestLeakage(unittest.TestCase):

    def test_leakage_model(self):
        error = 0
        Pipe21, Junc21, Junc22 = None, None, None
        pipe21Leak, junc21Leak, junc22Leak = 0.0, 0.0, 0.0
        ph = None

        # Create class and open network
        d = epanet("Net1.inp")



        # Single period analysis

        EN_LEAK_AREA = 26
        EN_LEAK_EXPAN = 27
        EN_LINK_LEAKAGE = 28
        EN_LEAKAGEFLOW = 30
        error = d.setTimeSimulationDuration(0)
        self.assertEqual(error, 0)

        # Get index of Pipe 21
        error = d.api.ENgetlinkindex("21")
        Pipe21 = error
        self.assertIsNotNone(Pipe21)

        # Set Pipe21 leak area to 1.0 sq mm per 100 ft of pipe
        # and its expansion rate to 0.1 sq mm per ft of head
        error = d.api.ENsetlinkvalue(Pipe21, EN_LEAK_AREA, 1.0)
        self.assertEqual(error, 0)
        error = d.api.ENsetlinkvalue(Pipe21, EN_LEAK_EXPAN, 0.1)
        self.assertEqual(error, 0)

        # Solve for hydraulics
        error = d.api.ENsolveH()
        self.assertEqual(error, 0)

        # Compute Pipe 21 leakage flow using the FAVAD formula EN_LINK_LEAKAGE
        pipe21Leak = d.getLinkLeakageRate(Pipe21)
        self.assertEqual(d.api.errcode, 0)

        # Retrieve leakage flow at end nodes
        Junc21 = d.api.ENgetnodeindex('21')
        self.assertEqual(d.api.errcode, 0)
        Junc22 = d.api.ENgetnodeindex('22')
        self.assertEqual(d.api.errcode, 0)

        junc21Leak = d.api.ENgetnodevalue(Junc21, EN_LEAKAGEFLOW)
        self.assertEqual(d.api.errcode, 0)
        junc22Leak = d.api.ENgetnodevalue(Junc22, EN_LEAKAGEFLOW)
        self.assertEqual(d.api.errcode, 0)


        #print(pipe21Leak)
        #print(junc21Leak)
        #print(junc22Leak)
        # Check that the sum of the node leakages equals the pipe leakage
        self.assertTrue(abs(pipe21Leak - (junc21Leak + junc22Leak)) < 0.01)

        # Clean up
        error = d.unload()
        self.assertEqual(d.api.errcode, 0)

if __name__ == '__main__':
    unittest.main()
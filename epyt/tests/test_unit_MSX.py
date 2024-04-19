from epyt import epanet, networks
import unittest
import os

DIRNAME = os.path.dirname(networks.__file__)


class MSXtest(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        # Create EPANET object using the INP file
        inpname = os.path.join(DIRNAME, 'msx-examples', 'Net3-NH2CL.inp')
        msxfile = os.path.join(DIRNAME, 'msx-examples', 'Net3-NH2CL.msx')
        self.epanetClass = epanet(inpname)
        self.msxClass = self.epanetClass.loadMSXFile(msxfile)

    def tearDown(self):
        """Call after every test case."""
        self.epanetClass.unloadMSX()
        self.epanetClass.unload()

    """ ------------------------------------------------------------------------- """

    def test_MSXgetsource(self):
        self.assertEqual(self.msxClass.MSXgetsource(1, 14),
                         ('SETPOINT', 2.0, 0), 'Wrong source comment output')
        self.assertEqual(self.msxClass.MSXgetsource(2, 1),
                         ('CONCEN', 0.8, 0), 'Wrong source comment output')
        self.assertEqual(self.msxClass.MSXgetsource(3, 2),
                         ('MASS', 0.5, 0), 'Wrong source comment output')
        self.assertEqual(self.msxClass.MSXgetsource(4, 3),
                         ('FLOWPACED', 4.5, 0), 'Wrong source comment output')

    def test_MSXsetsource(self):
        self.msxClass.MSXsetsource(1, 1, -1, 10.565, 1)
        self.assertEqual(self.msxClass.MSXgetsource(1, 1),
                         ('NOSOURCE', 10.565, 1), 'Wrong source comment output')
        self.msxClass.MSXsetsource(1, 1, 0, 10.565, 1)
        self.assertEqual(self.msxClass.MSXgetsource(1, 1),
                         ('CONCEN', 10.565, 1), 'Wrong source comment output')
        self.msxClass.MSXsetsource(1, 1, 1, 10.565, 1)
        self.assertEqual(self.msxClass.MSXgetsource(1, 1),
                         ('MASS', 10.565, 1), 'Wrong source comment output')
        self.msxClass.MSXsetsource(1, 1, 2, 10.565, 1)
        self.assertEqual(self.msxClass.MSXgetsource(1, 1),
                         ('SETPOINT', 10.565, 1), 'Wrong source comment output')
        self.msxClass.MSXsetsource(1, 1, 3, 10.565, 1)
        self.assertEqual(self.msxClass.MSXgetsource(1, 1),
                         ('FLOWPACED', 10.565, 1), 'Wrong source comment output')
        # set an integer value for level test_MSXsetsource
        self.msxClass.MSXsetsource(1, 1, 3, 10, 1)
        self.assertEqual(self.msxClass.MSXgetsource(1, 1),
                         ('FLOWPACED', 10, 1), 'Wrong source comment output')

    def test_MSXgetspecies(self):
        self.assertEqual(self.msxClass.MSXgetspecies(1), ('BULK', 'MMOL', 1.0e-8, 0.0001),
                         'Wrong species comment output')
        self.assertEqual(self.msxClass.MSXgetspecies(2), ('BULK', 'MMOL', 1.0e-8, 0.0001),
                         'Wrong species comment output')
        self.assertEqual(self.msxClass.MSXgetspecies(3), ('BULK', 'MMOL', 1.0e-8, 0.0001),
                         'Wrong species comment output')
        self.assertEqual(self.msxClass.MSXgetspecies(4), ('BULK', 'MMOL', 1.0e-8, 0.0001),
                         'Wrong species comment output')
        self.assertEqual(self.msxClass.MSXgetspecies(5), ('BULK', 'MMOL', 1.0e-8, 0.0001),
                         'Wrong species comment output')

    def test_MSXgetconstant(self):

        self.assertEqual(self.msxClass.MSXgetconstant(1), 0.02,
                         'Wrong constant comment output')
        self.assertEqual(self.msxClass.MSXgetconstant(2), 0.50,
                         'Wrong constant comment output')

    def test_MSXsetconstant(self):

        # set an integer value
        self.msxClass.MSXsetconstant(1, 69)
        self.assertEqual(self.msxClass.MSXgetconstant(1), 69,
                         'Wrong set/get constant comment output')
        # set a float value
        self.msxClass.MSXsetconstant(1, 69.420)
        self.assertEqual(self.msxClass.MSXgetconstant(1), 69.420,
                         'Wrong set/get constant comment output')

    def testMSXgetinitqual(self):
        self.assertEqual(self.msxClass.MSXgetinitqual(1, 1, 9), 2.818e-08,
                         'Wrong get init qual comment output')
        self.assertEqual(self.msxClass.MSXgetinitqual(1, 1, 10), 3.55e-7,
                         'Wrong get init qual comment output')
        self.assertEqual(self.msxClass.MSXgetinitqual(1, 1, 8), 0.004,
                         'Wrong get init qual comment output')
        self.assertEqual(self.msxClass.MSXgetinitqual(0, 1, 9), 2.818e-08,
                         'Wrong get init qual comment output')
        self.assertEqual(self.msxClass.MSXgetinitqual(0, 1, 10), 3.55e-7,
                         'Wrong get init qual comment output')
        self.assertEqual(self.msxClass.MSXgetinitqual(0, 1, 8), 0.004,
                         'Wrong get init qual comment output')

    def testMSXsetinitqual(self):
        # set value as integer testMSXsetinitqual
        self.msxClass.MSXsetinitqual(1, 1, 1, 69)
        self.assertEqual(self.msxClass.MSXgetinitqual(1, 1, 1), 69,
                         'Wrong set/get init qual comment output')
        # set value as float testMSXsetinitqual
        self.msxClass.MSXsetinitqual(1, 1, 1, 69.420)
        self.assertEqual(self.msxClass.MSXgetinitqual(1, 1, 1), 69.420,
                         'Wrong set/get init qual comment output')

    def test_MSXsetinitqual(self):
        # set value as integer test_MSXsetinitqual
        self.msxClass.MSXsetinitqual(1, 1, 1, 69)
        self.assertEqual(self.msxClass.MSXgetinitqual(1, 1, 1), 69,
                         'Wrong set/get init qual comment output')
        # set value as float test_MSXsetinitqual
        self.msxClass.MSXsetinitqual(1, 1, 1, 69.420)
        self.assertEqual(self.msxClass.MSXgetinitqual(1, 1, 1), 69.420,
                         'Wrong set/get init qual comment output')

    def test_MSXsetpatternvalue(self):

        # set value as integer test_MSXsetpatternvalue
        self.msxClass.MSXsetpatternvalue(1, 1, 69)
        self.assertEqual(self.msxClass.MSXgetpatternvalue(1, 1), 69,
                         'Wrong set/get patternvalue comment output')
        # set value as float test_MSXsetpatternvalue
        self.msxClass.MSXsetpatternvalue(1, 1, 69.420)
        self.assertEqual(self.msxClass.MSXgetpatternvalue(1, 1), 69.420,
                         'Wrong set/get init patternvalue comment output')

    def test_MSXgetIDlen(self):

        self.assertEqual(self.msxClass.MSXgetIDlen(3, 1), 4,
                         'Wrong get ID len comment output')
        self.assertEqual(self.msxClass.MSXgetIDlen(3, 2), 3,
                         'Wrong get ID len comment output')
        self.assertEqual(self.msxClass.MSXgetIDlen(3, 3), 5,
                         'Wrong get ID len comment output')

    def test_MSXgetID(self):

        self.assertEqual(self.msxClass.MSXgetID(3, 1, 4), 'HOCL',
                         'Wrong get ID  comment output')
        self.assertEqual(self.msxClass.MSXgetID(3, 2, 3), 'NH3',
                         'Wrong get ID  comment output')
        self.assertEqual(self.msxClass.MSXgetID(3, 3, 5), 'NH2CL',
                         'Wrong get ID  comment output')

    def test_MSXgeterror(self):

        self.assertEqual(self.msxClass.MSXgeterror(516), 'Error 516 - reference made to an illegal object index.',
                         'Wrong error comment output')
        self.assertEqual(self.msxClass.MSXgeterror(505), 'Error 505 - could not read hydraulic results file.',
                         'Wrong error comment output')
        self.assertEqual(self.msxClass.MSXgeterror(503), 'Error 503 - could not open MSX input file.',
                         'Wrong error comment output')

    def test_MSXgetparameter(self):
        self.assertEqual(self.msxClass.MSXgetparameter(1, 1, 2), 0.076,
                         'Wrong error comment output')
        self.assertEqual(self.msxClass.MSXgetparameter(1, 1, 4), 2.3e-3,
                         'Wrong error comment output')

    def test_MSXsetparameter(self):
        # set value as integer test_MSXsetparameter
        self.msxClass.MSXsetparameter(1, 1, 1, 69)
        self.assertEqual(self.msxClass.MSXgetparameter(1, 1, 1), 69,
                         'Wrong error comment output')
        # set value as float test_MSXsetparameter
        self.msxClass.MSXsetparameter(1, 1, 1, 69.420)
        self.assertEqual(self.msxClass.MSXgetparameter(1, 1, 1), 69.420,
                         'Wrong error comment output')

    def test_MSXgetcount(self):
        # for species
        self.assertEqual(self.msxClass.MSXgetcount(3), 16,
                         'Wrong error get count output')
        # for parameters
        self.assertEqual(self.msxClass.MSXgetcount(5), 11,
                         'Wrong error get count output')
        # for constants
        self.assertEqual(self.msxClass.MSXgetcount(6), 2,
                         'Wrong error get count output')
        # for patterns
        self.assertEqual(self.msxClass.MSXgetcount(7), 2,
                         'Wrong error get count output')

    def test_MSXgetindex(self):
        # testing 4 species (number 3) first , last, 1 char & more than 1 char and middle
        self.assertEqual(self.msxClass.MSXgetindex(3, "HOCL"), 1,
                         'Wrong error get count output')
        self.assertEqual(self.msxClass.MSXgetindex(3, "cNH2CL"), 16,
                         'Wrong error get count output')
        self.assertEqual(self.msxClass.MSXgetindex(3, "H"), 9,
                         'Wrong error get count output')
        self.assertEqual(self.msxClass.MSXgetindex(3, "OH"), 10,
                         'Wrong error get count output')
        # testing parameters (number 5) first , last and one middle case
        self.assertEqual(self.msxClass.MSXgetindex(5, "k1"), 1,
                         'Wrong error get count output')
        self.assertEqual(self.msxClass.MSXgetindex(5, "kDOC2"), 11,
                         'Wrong error get count output')
        self.assertEqual(self.msxClass.MSXgetindex(5, "k6"), 5,
                         'Wrong error get count output')
        # testing constants (number 6)
        self.assertEqual(self.msxClass.MSXgetindex(6, "S1"), 1,
                         'Wrong error get count output')
        self.assertEqual(self.msxClass.MSXgetindex(6, "S2"), 2,
                         'Wrong error get count output')
        # testing paterns (number 7)
        self.assertEqual(self.msxClass.MSXgetindex(7, "PAT1"), 1,
                         'Wrong error get count output')
        self.assertEqual(self.msxClass.MSXgetindex(7, "PAT2"), 2,
                         'Wrong error get count output')

    def test_MSXaddpattern(self):

        y = self.msxClass.MSXgetcount(7)
        self.msxClass.MSXaddpattern("pat-test-2")
        self.assertEqual(self.msxClass.MSXgetcount(7), y + 1,
                         'Wrong error add patter output')

    def test_MSXsetpatter(self):
        self.msxClass.MSXaddpattern("pat-test-1")
        x = self.msxClass.MSXgetindex(7, "pat-test-1")
        mult = [0.5, 0.8, 1.2, 1.0, 0.7, 0.3]
        self.msxClass.MSXsetpattern(x, mult, 6)

        self.assertEqual(self.msxClass.MSXgetpatternvalue(x, 1), 0.5,
                         'Wrong set/get patternvalue comment output')
        self.assertEqual(self.msxClass.MSXgetpatternvalue(x, 2), 0.8,
                         'Wrong set/get patternvalue comment output')
        self.assertEqual(self.msxClass.MSXgetpatternvalue(x, 3), 1.2,
                         'Wrong set/get patternvalue comment output')
        self.assertEqual(self.msxClass.MSXgetpatternvalue(x, 4), 1.0,
                         'Wrong set/get patternvalue comment output')
        self.assertEqual(self.msxClass.MSXgetpatternvalue(x, 5), 0.7,
                         'Wrong set/get patternvalue comment output')
        self.assertEqual(self.msxClass.MSXgetpatternvalue(x, 6), 0.3,
                         'Wrong set/get patternvalue comment output')

    def test_MSXsavesmsxfile(self):
        filename = "net-test-1.msx"
        self.msxClass.MSXsavemsxfile(filename)
        full_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(full_path):
            print(f"The file {filename} exists in the current directory.")
        else:
            print(f"The file {filename} does not exist in the current directory.")

    def test_MSXgetqual(self):

        self.msxClass.MSXclose()
        self.epanetClass.unload()
        inpname = os.path.join(DIRNAME, 'msx-examples', 'net2-cl2.inp')
        self.epanetClass = epanet(inpname)
        file_path = os.path.join(DIRNAME, 'msx-examples', 'net2-cl2.msx')
        self.msxClass = self.epanetClass.loadMSXFile(file_path)

        self.msxClass.MSXsolveH()
        self.msxClass.MSXsolveQ()
        t = 0
        tleft = 0
        self.msxClass.MSXinit(0)
        c = 0
        while True:
            t, tleft = self.msxClass.MSXstep()
            c = c + 1
            if c == 1:
                self.assertEqual(self.msxClass.MSXgetqual(0, 1, 1), 0.8,
                                 'Wrong get qual comment output')
            if c == 85:
                self.assertEqual(self.msxClass.MSXgetqual(0, 1, 1), 0.7991666666666667,
                                 'Wrong  get qual comment output')
            if c == 660:
                self.assertEqual(self.msxClass.MSXgetqual(0, 1, 1), 0.8,
                                 'Wrong  get qual comment output')
            if tleft <= 0:
                break


if __name__ == "__main__":
    unittest.main()

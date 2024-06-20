from epyt import epanet, networks
import unittest
import os

DIRNAME = os.path.dirname(networks.__file__)


class MSXtest(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        # Create EPANET object using the INP file
        inpname = os.path.join(DIRNAME, 'msx-examples', 'net2-cl2.inp')
        msxname = os.path.join(DIRNAME, 'msx-examples', 'net2-cl2.msx')
        self.epanetClass = epanet(inpname)
        self.msxClass = self.epanetClass.loadMSXFile(msxname)

    def tearDown(self):
        """Call after every test case."""
        self.epanetClass.unloadMSX()
        self.epanetClass.unload()

    """ ------------------------------------------------------------------------- """

    # new functions  - Read MSX file
    def test_MSXOptions(self):
        self.assertEqual(self.epanetClass.getMSXTimeStep(),
                         300, 'Wrong get timestep comment output')

        self.epanetClass.setMSXTimeStep(4200)
        self.assertEqual(self.epanetClass.getMSXTimeStep(),
                         4200, 'Wrong get timestep comment output')

        self.assertEqual(self.epanetClass.getMSXAreaUnits(),
                         "FT2", 'Wrong get Area Units comment output')

        self.epanetClass.setMSXAreaUnitsFT2()
        self.assertEqual(self.epanetClass.getMSXAreaUnits(),
                         "FT2", 'Wrong get Area Units comment output')
        self.epanetClass.setMSXAreaUnitsM2()
        self.assertEqual(self.epanetClass.getMSXAreaUnits(),
                         "M2", 'Wrong get Area Units comment output')
        self.epanetClass.setMSXAreaUnitsCM2()
        self.assertEqual(self.epanetClass.getMSXAreaUnits(),
                         "CM2", 'Wrong get Area Units comment output')

        self.epanetClass.setMSXRateUnitsSEC()
        self.assertEqual(self.epanetClass.getMSXRateUnits(),
                         "SEC", "Wrong get Rate Units comments output")
        self.epanetClass.setMSXRateUnitsMIN()
        self.assertEqual(self.epanetClass.getMSXRateUnits(),
                         "MIN", "Wrong get Rate Units comments output")
        self.epanetClass.setMSXRateUnitsDAY()
        self.assertEqual(self.epanetClass.getMSXRateUnits(),
                         "DAY", "Wrong get Rate Units comments output")

        self.epanetClass.setMSXSolverEUL()
        self.assertEqual(self.epanetClass.getMSXSolver(),
                         "EUL", "Wrong get Solver comments output")

        self.epanetClass.setMSXSolverRK5()
        self.assertEqual(self.epanetClass.getMSXSolver(),
                         "RK5", "Wrong get Solver comments output")
        self.epanetClass.setMSXSolverROS2()
        self.assertEqual(self.epanetClass.getMSXSolver(),
                         "ROS2", "Wrong get Solver comments output")

        self.epanetClass.setMSXCouplingFULL()
        self.assertEqual(self.epanetClass.getMSXCoupling(),
                         "FULL", "Wrong get Coupling comments output")
        self.epanetClass.setMSXCouplingNONE()
        self.assertEqual(self.epanetClass.getMSXCoupling(),
                         "NONE", "Wrong get Coupling comments output")

        #self.epanetClass.setMSXCompilerVC()
        #self.assertEqual(self.epanetClass.getMSXCompiler(),
        #                 "VC", "Wrong get Compiler comments output")
        #self.epanetClass.setMSXCompilerGC()
        #self.assertEqual(self.epanetClass.getMSXCompiler(),
        #                 "GC", "Wrong get Compiler comments output")
        #self.epanetClass.setMSXCompilerNONE()
        #self.assertEqual(self.epanetClass.getMSXCompiler(),
        #                 "NONE", "Wrong get Compiler comments output")

        self.epanetClass.setMSXAtol(0.2)
        self.assertEqual(self.epanetClass.getMSXAtol(),
                         0.2, "Wrong get ATOL comments output")
        self.epanetClass.setMSXRtol(0.2)
        self.assertEqual(self.epanetClass.getMSXRtol(),
                         0.2, "Wrong get RTOL comments output")

    def test_Parameters(self):
        self.assertEqual(self.epanetClass.getMSXEquationsTerms(),
                         (["Kf     1.5826e-4 * RE^0.88 / D"]), 'Wrong get Equations comment output')
        self.assertEqual(self.epanetClass.getMSXEquationsPipes(),
                         (["RATE        CL2    -Kb*CL2 - (4/D)*Kw*Kf/(Kw+Kf)*CL2"]),
                         'Wrong get Equations comment output')
        self.assertEqual(self.epanetClass.getMSXEquationsTanks(),
                         (["RATE        CL2    -Kb*CL2"]), 'Wrong get Equations comment output')


if __name__ == "__main__":
    unittest.main()

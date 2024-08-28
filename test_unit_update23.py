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

    def test_setControlEnabled(self):

        self.assertEqual( self.epanetClass.getControlEnabled(1),
                         (1), 'Wrong Control enabled comment output')

        self.epanetClass.setControlEnabled(1, 0)

        self.assertEqual(self.epanetClass.getControlEnabled(1),
                         (0), 'Wrong Control enabled comment output')

    def test_getLinkValuesFLOW(self):

        self.epanetClass.openHydraulicAnalysis()
        self.epanetClass.initializeHydraulicAnalysis()

        tstep = 1
        T_H, Ft, Fb =  [], [], []

        while tstep > 0:
            t = self.epanetClass.runHydraulicAnalysis()
            #flow test
            Ft.append(self.epanetClass.getLinkValues(self.epanetClass.ToolkitConstants.EN_FLOW))
            Fb.append(self.epanetClass.getLinkFlows())
            T_H.append(t)
            tstep = self.epanetClass.nextHydraulicAnalysisStep()

        self.epanetClass.closeHydraulicAnalysis()
        self.assertEqual(Fb[0].tolist(), Ft[0]) #Flow check

    def test_getLinkValuesHEADLOSS(self):

        self.epanetClass.openHydraulicAnalysis()
        self.epanetClass.initializeHydraulicAnalysis()

        tstep = 1
        T_H, Ht, Hb = [], [], []

        while tstep > 0:
            t = self.epanetClass.runHydraulicAnalysis()
            # headloss test
            Ht.append(self.epanetClass.getLinkValues(self.epanetClass.ToolkitConstants.EN_HEADLOSS))
            Hb.append(self.epanetClass.getLinkHeadloss())
            T_H.append(t)
            tstep = self.epanetClass.nextHydraulicAnalysisStep()

        self.epanetClass.closeHydraulicAnalysis()
        self.assertEqual(Hb[0].tolist(), Ht[0])  # Headloss check

    def test_getLinkValuesVELOCITY(self):

        self.epanetClass.openHydraulicAnalysis()
        self.epanetClass.initializeHydraulicAnalysis()

        tstep = 1
        T_H, Vt, Vb = [], [], []

        while tstep > 0:
            t = self.epanetClass.runHydraulicAnalysis()
            # Velocity test
            Vt.append(self.epanetClass.getLinkValues(self.epanetClass.ToolkitConstants.EN_VELOCITY))
            Vb.append(self.epanetClass.getLinkVelocity())
            T_H.append(t)
            tstep = self.epanetClass.nextHydraulicAnalysisStep()

        self.epanetClass.closeHydraulicAnalysis()
        self.assertEqual(Vb[0].tolist(), Vt[0])  # Velocity check

    def test_getLinkValuesDIAMETER(self):

        self.epanetClass.openHydraulicAnalysis()
        self.epanetClass.initializeHydraulicAnalysis()

        tstep = 1
        T_H, Dt, Db = [], [], []

        while tstep > 0:
            t = self.epanetClass.runHydraulicAnalysis()
            # Diameter test
            Dt.append(self.epanetClass.getLinkValues(self.epanetClass.ToolkitConstants.EN_DIAMETER))
            Db.append(self.epanetClass.getLinkDiameter())
            T_H.append(t)
            tstep = self.epanetClass.nextHydraulicAnalysisStep()

        self.epanetClass.closeHydraulicAnalysis()
        self.assertEqual(Db[0].tolist(), Dt[0])  # Diameter check

    def test_getLinkValuesLENGTH(self):

        self.epanetClass.openHydraulicAnalysis()
        self.epanetClass.initializeHydraulicAnalysis()

        tstep = 1
        T_H, Lt, Lb = [], [], []

        while tstep > 0:
            t = self.epanetClass.runHydraulicAnalysis()
            # LENGTH test
            Lt.append(self.epanetClass.getLinkValues(self.epanetClass.ToolkitConstants.EN_LENGTH))
            Lb.append(self.epanetClass.getLinkLength())
            T_H.append(t)
            tstep = self.epanetClass.nextHydraulicAnalysisStep()

        self.epanetClass.closeHydraulicAnalysis()
        self.assertEqual(Lb[0].tolist(), Lt[0])  # LENGTH check

    def test_getLinkValuesROUGHNESS(self):

        self.epanetClass.openHydraulicAnalysis()
        self.epanetClass.initializeHydraulicAnalysis()

        tstep = 1
        T_H, Rt, Rb = [], [], []

        while tstep > 0:
            t = self.epanetClass.runHydraulicAnalysis()
            # ROUGHNESS test
            Rt.append(self.epanetClass.getLinkValues(self.epanetClass.ToolkitConstants.EN_ROUGHNESS))
            Rb.append(self.epanetClass.getLinkRoughnessCoeff())
            T_H.append(t)
            tstep = self.epanetClass.nextHydraulicAnalysisStep()

        self.epanetClass.closeHydraulicAnalysis()
        self.assertEqual(Rb[0].tolist(), Rt[0])  # ROUGHNESS check

    def test_getLinkValuesMINORLOSS(self):

        self.epanetClass.openHydraulicAnalysis()
        self.epanetClass.initializeHydraulicAnalysis()

        tstep = 1
        T_H, Mt, Mb = [], [], []

        while tstep > 0:
            t = self.epanetClass.runHydraulicAnalysis()
            # MINORLOSS test
            Mt.append(self.epanetClass.getLinkValues(self.epanetClass.ToolkitConstants.EN_MINORLOSS))
            Mb.append(self.epanetClass.getLinkMinorLossCoeff())
            T_H.append(t)
            tstep = self.epanetClass.nextHydraulicAnalysisStep()

        self.epanetClass.closeHydraulicAnalysis()
        self.assertEqual(Mb[0].tolist(), Mt[0])  # MINORLOSS check

    def test_getLinkValuesINITSTATUS(self):

        self.epanetClass.openHydraulicAnalysis()
        self.epanetClass.initializeHydraulicAnalysis()

        tstep = 1
        T_H, It, Ib = [], [], []

        while tstep > 0:
            t = self.epanetClass.runHydraulicAnalysis()
            # INITSTATUS test
            It.append(self.epanetClass.getLinkValues(self.epanetClass.ToolkitConstants.EN_INITSTATUS))
            Ib.append(self.epanetClass.getLinkInitialStatus())
            T_H.append(t)
            tstep = self.epanetClass.nextHydraulicAnalysisStep()

        self.epanetClass.closeHydraulicAnalysis()
        self.assertEqual(Ib[0].tolist(), It[0])  # INITSTATUS check

    def test_getLinkValuesINITSETTING(self):

        self.epanetClass.openHydraulicAnalysis()
        self.epanetClass.initializeHydraulicAnalysis()

        tstep = 1
        T_H, It, Ib = [], [], []

        while tstep > 0:
            t = self.epanetClass.runHydraulicAnalysis()
            # INITSETTING test
            It.append(self.epanetClass.getLinkValues(self.epanetClass.ToolkitConstants.EN_INITSETTING))
            Ib.append(self.epanetClass.getLinkInitialSetting())
            T_H.append(t)
            tstep = self.epanetClass.nextHydraulicAnalysisStep()

        self.epanetClass.closeHydraulicAnalysis()
        self.assertEqual(Ib[0].tolist(), It[0])  # INITSETTING check

    def test_getLinkValuesSTATUS(self):

        self.epanetClass.openHydraulicAnalysis()
        self.epanetClass.initializeHydraulicAnalysis()

        tstep = 1
        T_H, St, Sb = [], [], []

        while tstep > 0:
            t = self.epanetClass.runHydraulicAnalysis()
            # STATUS test
            St.append(self.epanetClass.getLinkValues(self.epanetClass.ToolkitConstants.EN_STATUS))
            Sb.append(self.epanetClass.getLinkStatus())
            T_H.append(t)
            tstep = self.epanetClass.nextHydraulicAnalysisStep()

        self.epanetClass.closeHydraulicAnalysis()
        self.assertEqual(Sb[0].tolist(), St[0])  # STATUS check

    def test_getLinkValuesSETTING(self):

        self.epanetClass.openHydraulicAnalysis()
        self.epanetClass.initializeHydraulicAnalysis()

        tstep = 1
        T_H, St, Sb = [], [], []

        while tstep > 0:
            t = self.epanetClass.runHydraulicAnalysis()
            # STATUS test
            St.append(self.epanetClass.getLinkValues(self.epanetClass.ToolkitConstants.EN_SETTING))
            Sb.append(self.epanetClass.getLinkSettings())
            T_H.append(t)
            tstep = self.epanetClass.nextHydraulicAnalysisStep()

        self.epanetClass.closeHydraulicAnalysis()
        self.assertEqual(Sb[0].tolist(), St[0])  # SETTING check

    def test_getLinkValuesENERGY(self):

        self.epanetClass.openHydraulicAnalysis()
        self.epanetClass.initializeHydraulicAnalysis()

        tstep = 1
        T_H, Et, Eb = [], [], []

        while tstep > 0:
            t = self.epanetClass.runHydraulicAnalysis()
            # ENERGY test
            Et.append(self.epanetClass.getLinkValues(self.epanetClass.ToolkitConstants.EN_ENERGY))
            Eb.append(self.epanetClass.getLinkEnergy())
            T_H.append(t)
            tstep = self.epanetClass.nextHydraulicAnalysisStep()

        self.epanetClass.closeHydraulicAnalysis()
        self.assertEqual(Eb[0].tolist(), Et[0])  # ENERGY check


if __name__ == "__main__":
    unittest.main()


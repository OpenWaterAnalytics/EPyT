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

    def test_setControlEnabledandDissabled(self):

        self.assertEqual( self.epanetClass.getControlState(1),
                         (1), 'Wrong Control enabled comment output')

        self.epanetClass.setControlEnabled(1,0)

        self.assertEqual(self.epanetClass.getControlState(1),
                         (0), 'Wrong Control enabled comment output')

        self.epanetClass.setControlEnabled(1,1)

        self.assertEqual(self.epanetClass.getControlState(1),
                         (1), 'Wrong Control enabled comment output')

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

    def test_setVertex(self):
        linkID = '10'
        x = [22, 24, 28]
        y = [30, 68, 69]
        self.epanetClass.setLinkVertices(linkID, x, y)
        self.epanetClass.setVertex(1, 1, 1, 1)
        x = self.epanetClass.getLinkVertices()
        self.assertEqual(x['x'][1], [1, 24, 28], 'Wrong output for setVertex ')
        self.assertEqual(x['y'][1], [1, 68, 69], 'Wrong output for setVertex ')

    def test_getsetLinkValveCurvePCV(self):
        linkid =  self.epanetClass.getLinkPipeNameID(1)
        condition = 1
        index =  self.epanetClass.setLinkTypeValvePCV(linkid, condition)
        self.epanetClass.setLinkValveCurvePCV(index, 1)
        self.assertEqual(self.epanetClass.getLinkValveCurvePCV(index), 1,"Wrong output for set/get LinkValveCurvePCV")

    def test_getsetLinkValveCurveGPV(self):
        linkid =  self.epanetClass.getLinkPipeNameID(1)
        condition = 1
        index =  self.epanetClass.setLinkTypeValveGPV(linkid, condition)
        self.epanetClass.setLinkValveCurveGPV(index, 1)
        self.assertEqual(self.epanetClass.getLinkValveCurveGPV(index), 1,"Wrong output for set/get LinkValveCurveGPV")

    def test_getsetTimeClockStartTime(self):
        self.assertEqual(self.epanetClass.getTimeClockStartTime(), 0,"Wrong output for get getTimeClockStartTime")
        self.epanetClass.setTimeClockStartTime(3600)
        self.assertEqual(self.epanetClass.getTimeClockStartTime(), 3600,"Wrong output for get getTimeClockStartTime")

    def test_getsetOptionsDemandPattern(self):
        self.assertEqual(self.epanetClass.getOptionsDemandPattern(), 1,"Wrong output for get getOptionsDemandPattern")
        self.epanetClass.setOptionsDemandPattern(0)
        self.assertEqual(self.epanetClass.getOptionsDemandPattern(), 0,"Wrong output for get getsetOptionsDemandPattern")

    def test_setLinkTypeValvePCV(self):
        linkid = self.epanetClass.getLinkPipeNameID(1)  # Retrieves the ID of the 1t pipe
        index = self.epanetClass.setLinkTypeValvePCV(linkid)  # Changes the 1st pipe to valve PCV given it's ID
        self.assertEqual(self.epanetClass.getLinkType(index), "PCV","Wrong output for setLinkTypeValvePCV")

    def test_getsetEmiterBackFLow(self):
        self.assertEqual(self.epanetClass.getOptionsEmitterBackFlow(), 1, "Wrong output for getsetEmiterBackFLow")
        self.epanetClass.setOptionsEmitterBackFlowDisallowed()
        self.assertEqual(self.epanetClass.getOptionsEmitterBackFlow(), 0, "Wrong output for getsetEmiterBackFLow")
        self.epanetClass.setOptionsEmitterBackFlowAllowed()
        self.assertEqual(self.epanetClass.getOptionsEmitterBackFlow(), 1, "Wrong output for getsetEmiterBackFLow")

    def test_setLinkFlowUnitsCMS(self):
        self.epanetClass.setFlowUnitsCMS()  # kpa and meters
        self.assertEqual(self.epanetClass.getFlowUnits(), "CMS", "Wrong output for setLinkFlowUnitsCMS")

    def test_OptionsStatusReport(self):
        self.epanetClass.setOptionsStatusReportNo()
        self.assertEqual(self.epanetClass.getOptionsStatusReport(), "NO REPORT", "Wrong output for OptionsStatusReport")

        self.epanetClass.setOptionsStatusReportNormal()
        self.assertEqual(self.epanetClass.getOptionsStatusReport(), "NORMAL REPORT",
                         "Wrong output for OptionsStatusReport")

        self.epanetClass.setOptionsStatusReportFull()
        self.assertEqual(self.epanetClass.getOptionsStatusReport(), "FULL REPORT",
                         "Wrong output for OptionsStatusReport")


if __name__ == "__main__":
    unittest.main(),


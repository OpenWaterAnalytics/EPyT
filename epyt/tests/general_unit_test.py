from ftplib import error_perm
from math import isclose
from tkinter import E
from epyt import epanet
import numpy as np
import unittest

class GeneralTest(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        # Create EPANET object using the INP file
        inpname = 'Net1.inp'
        self.epanetClass = epanet(inpname)

    def tearDown(self):
        """Call after every test case."""
        self.epanetClass.unload()

    """ ------------------------------------------------------------------------- """
    def testaddControl(self):
        err_msg = "Wrong add Control output"
        # Test 1
        index = self.epanetClass.addControls('LINK 12 CLOSED IF NODE 2 ABOVE 20')
        assert self.epanetClass.getControls(index).Control == 'LINK 12 CLOSED IF NODE 2 ABOVE 20.0', err_msg
        # Test 2
        index = self.epanetClass.addControls('LINK 12 OPEN IF NODE 11 BELOW 30')
        np.testing.assert_approx_equal(self.epanetClass.getControls(index).Value, 30, err_msg=err_msg)
        # Test 3
        index = self.epanetClass.addControls('LINK 9 1.5 AT TIME 57600')
        assert self.epanetClass.getControls(index).Control == 'LINK 9 1.5 AT TIME 57600.0', err_msg
        # Test 4
        index = self.epanetClass.addControls(0, 13, 0, 11, 100)
        contorl_dict = {'Type': 'LOWLEVEL', 'LinkID': '9', 'Setting': 'CLOSED', 'NodeID': '2',
                        'Value': 100.0, 'Control': 'LINK 9 CLOSED IF NODE 2 BELOW 100.0'}
        self.assertDictEqual(self.epanetClass.getControls(index).to_dict(), contorl_dict, err_msg)
        
    def testaddCurve(self):
        err_msg = "Wrong add Curve output"
        # Test 1
        new_curve_ID = 'NewCurve'
        x_y_1 = [0, 730]
        x_y_2 = [1000, 500]
        x_y_3 = [1350, 260]
        values = [x_y_1, x_y_2, x_y_3] 
        curve_index = self.epanetClass.addCurve(new_curve_ID, values)
        curve_info = self.epanetClass.getCurvesInfo()
        np.testing.assert_equal(curve_info.CurveNameID, ['1', 'NewCurve'], err_msg=err_msg) 
        np.testing.assert_equal(curve_info.CurveNvalue, [1, 3], err_msg=err_msg)
        x_vals_desired = [[1500.0], [0.0, 1000.0, 1350.0]]
        x_vals_actual = curve_info.CurveXvalue
        for i in range(len(x_vals_actual)): np.testing.assert_equal(x_vals_actual[i], x_vals_desired[i], err_msg=err_msg)
        y_vals_desired = [[250.0], [730.0, 500.0, 260.0]]
        y_vals_actual = curve_info.CurveYvalue
        for i in range(len(y_vals_actual)): np.testing.assert_equal(y_vals_actual[i], y_vals_desired[i], err_msg=err_msg)

    def testaddLinkPipe(self):
        err_msg = "Wrong add Link Pipe output"
        # Test 1
        pipeID = 'newPipe_1'
        fromNode = '10'
        toNode = '21'
        pipeIndex = self.epanetClass.addLinkPipe(pipeID, fromNode, toNode)
        assert self.epanetClass.getLinkPipeCount() == 13, err_msg
        # Test 2
        pipeID = 'newPipe_2'
        fromNode = '11'
        toNode = '22'
        length = 600
        self.epanetClass.getLinkPipeCount()
        pipeIndex = self.epanetClass.addLinkPipe(pipeID, fromNode, toNode, length)
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkLength(pipeIndex), length)
        # Test 3
        pipeID = 'newPipe_3'
        fromNode = '31'
        toNode = '22'
        length = 500
        diameter = 15
        roughness = 120
        minorLossCoeff = 0.2
        self.epanetClass.getLinkPipeCount()
        pipeIndex = self.epanetClass.addLinkPipe(pipeID, fromNode, toNode, length, diameter, roughness, minorLossCoeff)
        assert self.epanetClass.getLinkPipeCount() == 15, err_msg
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkLength(pipeIndex), length)
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkDiameter(pipeIndex), diameter)
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkRoughnessCoeff(pipeIndex), roughness)
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkMinorLossCoeff(pipeIndex), minorLossCoeff)
       
    def testaddLinkPipeCV(self):
        err_msg = "Wrong add Link PipeCV output"
        # Test 1
        cvPipeID = 'newCVPipe_1'
        fromNode = '31'
        toNode = '22'
        length = 500
        diameter = 15
        roughness = 120
        minorLossCoeff = 0.2
        cvPipeIndex = self.epanetClass.addLinkPipeCV(cvPipeID, fromNode, toNode, length, diameter, roughness, minorLossCoeff)
        assert self.epanetClass.getLinkPipeCount() == 13, err_msg
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkLength(cvPipeIndex), length)
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkDiameter(cvPipeIndex), diameter)
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkRoughnessCoeff(cvPipeIndex), roughness)
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkMinorLossCoeff(cvPipeIndex), minorLossCoeff)

    def testaddLinkPump(self):
        err_msg = "Wrong add Link Pump output"
        pumpID = 'newPump_1'
        fromNode = '11'
        toNode = '22'
        initialStatus = 1    # (OPEN)
        initialSetting = 1.2
        power = 10
        patternIndex = 1
        pumpIndex = self.epanetClass.addLinkPump(pumpID, fromNode, toNode, initialStatus, initialSetting, power, patternIndex)
        assert self.epanetClass.getLinkPumpCount() == 2, err_msg
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkInitialStatus(pumpIndex), initialStatus)
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkInitialSetting(pumpIndex), initialSetting)
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkPumpPower(pumpIndex), power)
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getLinkPumpPatternIndex(pumpIndex), patternIndex)
        return
        
    def testLinkValves(self):
        # FCV
        valveID = 'newValveFCV'
        fromNode = '10'
        toNode = '21'
        valveIndex = self.epanetClass.addLinkValveFCV(valveID, fromNode, toNode)
        assert self.epanetClass.getLinkType(valveIndex) == 'FCV', 'error in FCV Valve'
        # GPV
        valveID = 'newValveGPV'
        valveIndex = self.epanetClass.addLinkValveGPV(valveID, fromNode, toNode)
        assert self.epanetClass.getLinkType(valveIndex) == 'GPV', 'error in GPV Valve'
        # PBV
        valveID = 'newValvePBV'
        valveIndex = self.epanetClass.addLinkValvePBV(valveID, fromNode, toNode)
        assert self.epanetClass.getLinkType(valveIndex) == 'PBV', 'error in PBV Valve'
        # PRV
        valveID = 'newValvePRV'
        valveIndex = self.epanetClass.addLinkValvePRV(valveID, fromNode, toNode)
        assert self.epanetClass.getLinkType(valveIndex) == 'PRV', 'error in PRV Valve'
        # PSV
        valveID = 'newValvePSV'
        valveIndex = self.epanetClass.addLinkValvePSV(valveID, fromNode, toNode)
        assert self.epanetClass.getLinkType(valveIndex) == 'PSV', 'error in PSV Valve'
        # TCV
        valveID = 'newValveTCV'
        valveIndex = self.epanetClass.addLinkValveTCV(valveID, fromNode, toNode)
        assert self.epanetClass.getLinkType(valveIndex) == 'TCV', 'error in TCV Valve'
        
    def testaddNodeJunction(self):
        err_msg = "Wrong add Node Junction output"
        junctionID = 'newJunction_5'
        junctionCoords = [10, 20]
        junctionElevation = 500
        demand = 50
        demandPatternID = self.epanetClass.getPatternNameID(1)
        junctionIndex = self.epanetClass.addNodeJunction(junctionID, junctionCoords, junctionElevation, demand, demandPatternID)
        assert self.epanetClass.getNodeJunctionCount() == 10, err_msg
        coords = self.epanetClass.getNodeCoordinates()
        x = coords['x'][junctionIndex]
        y = coords['y'][junctionIndex]
        assert [x, y] == junctionCoords, err_msg
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getNodeElevations(junctionIndex), junctionElevation)
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getNodeBaseDemands(junctionIndex)[1], demand)
        assert self.epanetClass.getNodeDemandPatternNameID()[1][junctionIndex-1] == demandPatternID, err_msg

    def testaddNodeJunctionDemand(self):
        self.epanetClass = epanet('ky10.inp')
        self.epanetClass.addNodeJunctionDemand([1, 2], [100, 110], ['1', '2'], ['new demand1', 'new demand2'])
        assert self.epanetClass.getNodeJunctionDemandName()[2][0:2]  == ['new demand1', 'new demand2'], 'Wrong node junction demand output'
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getNodeBaseDemands()[2][0:2], [100, 110])

    def testaddNodeReservoir(self):
        reservoirID = 'newReservoir_1'
        reservoirCoords = [20, 30]
        reservoirIndex = self.epanetClass.addNodeReservoir(reservoirID, reservoirCoords)
        assert self.epanetClass.getNodeCount() == 12, 'The Reservoir has not been added'
        x = self.epanetClass.getNodeCoordinates('x')[reservoirIndex]
        y = self.epanetClass.getNodeCoordinates('y')[reservoirIndex]
        assert [x,y] == reservoirCoords, 'Wrong Reservoir coordinates'

    def testaddNodeTank(self):
        tankID = 'newTank_1'
        tankCoords = [20, 30]
        elevation = 100
        initialLevel = 130
        minimumWaterLevel = 110
        maximumWaterLevel = 160
        diameter = 60
        minimumWaterVolume = 200000
        volumeCurveID = ''   # Empty for no curve
        tankIndex = self.epanetClass.addNodeTank(tankID, tankCoords, elevation, initialLevel, minimumWaterLevel,
                                                maximumWaterLevel, diameter, minimumWaterVolume, volumeCurveID)
        tank_data = self.epanetClass.getNodeTankData(tankIndex)
        x = self.epanetClass.getNodeCoordinates('x')[tankIndex]
        y = self.epanetClass.getNodeCoordinates('y')[tankIndex]
        assert [x,y] == tankCoords, 'Wrong Tank coordinates'
        assert isclose(tank_data.Elevation, elevation), 'Wrong Elevation output'
        assert isclose(tank_data.Initial_Level, initialLevel), 'Wrong Initial Level output'
        assert isclose(tank_data.Minimum_Water_Level, minimumWaterLevel), 'Wrong Minimum Water Level output'
        assert isclose(tank_data.Diameter, diameter), 'Wrong Diameter output'
        assert isclose(tank_data.Minimum_Water_Volume, minimumWaterVolume), 'Wrong Minimum Water Volume output'
        assert tank_data.Volume_Curve_Index is None, 'Wrong Volume Curve Index output'


    

if __name__ == "__main__":
    unittest.main()  # run all tests
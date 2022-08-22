from ftplib import error_perm
from math import isclose
from tkinter import E
from epyt import epanet
import numpy as np
import unittest

class AddTest(unittest.TestCase):
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
        assert tank_data.Volume_Curve_Index == [0], 'Wrong Volume Curve Index output'

    def testaddPattern(self):
        # Test 1
        patternID = 'new_pattern_1'
        patternIndex = self.epanetClass.addPattern(patternID)                 # Adds a new time pattern given it's ID
        assert self.epanetClass.getPatternNameID(patternIndex) == patternID, 'Wrong pattern Name ID'
        # Test 2
        patternID = 'new_pattern_2'
        patternMult = [1.56, 1.36, 1.17, 1.13, 1.08,
        1.04, 1.2, 0.64, 1.08, 0.53, 0.29, 0.9, 1.11,
        1.06, 1.00, 1.65, 0.55, 0.74, 0.64, 0.46,
        0.58, 0.64, 0.71, 0.66]
        patternIndex = self.epanetClass.addPattern(patternID, patternMult)    # Adds a new time pattern given it's ID and the multiplier
        assert self.epanetClass.getPatternNameID(patternIndex) == patternID, 'Wrong pattern Name ID'
        np.testing.assert_array_almost_equal_nulp(self.epanetClass.getPattern()[2], patternMult)

    def testaddRules(self):
        self.epanetClass.addRules('RULE RULE-1 \n IF TANK 2 LEVEL >= 140 \n THEN PUMP 9 STATUS IS CLOSED \n PRIORITY 1')
        assert self.epanetClass.getRuleCount() == 1, 'Wrong Rule Count Number'
        rule = self.epanetClass.getRules()[1]
        assert rule['Rule_ID'] == 'RULE-1', 'Wrong rule ID'
        self.assertEqual(rule['Premises'][0], 'IF NODE 2 LEVEL >= 140.0',  'Wrong Premises')
        self.assertEqual(rule['Then_Actions'][0], 'THEN PUMP 9 STATUS IS CLOSED','Wrong Then Actions')

class DeleteTest(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        # Create EPANET object using the INP file
        inpname = 'Net1.inp'
        self.epanetClass = epanet(inpname)

    def tearDown(self):
        """Call after every test case."""
        self.epanetClass.unload()

    def testdeleteControls(self):
        # Test 1
        self.epanetClass.deleteControls()
        assert self.epanetClass.getControls() == {}, 'The Controls have not been deleted'

    def testdeleteCurve(self):
        # Test 1
        d = epanet('BWSN_Network_1.inp')
        idCurve = d.getCurveNameID(1)    # Retrieves the ID of the 1st curve
        d.deleteCurve(idCurve)           #  Deletes a curve given it's ID
        self.assertEqual(d.getCurveNameID(), ['CURVE-1', 'CURVE-2'], 'Curve not deleted')
        # Test 2
        index = 1
        d.deleteCurve(index)             # Deletes a curve given it's index
        self.assertEqual(d.getCurveNameID(), ['CURVE-2'], 'Curve not deleted')

    def testdeleteLink(self):
        err_msg = 'Link not deleted'
        # Test 1
        idLink = self.epanetClass.getLinkNameID(1)          # Retrieves the ID label of the 1st link
        self.epanetClass.deleteLink(idLink)                 # Deletes the 1st link given it's ID
        self.assertNotEqual(self.epanetClass.getLinkNameID(1), idLink, err_msg)
        # Test 2
        indexLink = 1
        link_count = self.epanetClass.getLinkCount()
        self.epanetClass.deleteLink(indexLink)                             # Deletes the 1st link given it's index
        self.assertNotEqual(self.epanetClass.getLinkCount(), link_count, err_msg)

    def testdeleteNode(self):
        err_msg = 'Node not deleted'
        # Test 1
        idNode = self.epanetClass.getNodeNameID(1)        # Retrieves the ID label of the 1st node
        self.epanetClass.deleteNode(idNode)               # Deletes the 1st node given it's ID
        self.assertNotEqual(self.epanetClass.getNodeNameID(1), idNode, err_msg)
        # Test 2
        node_count = self.epanetClass.getNodeCount()
        index = 1
        self.epanetClass.deleteNode(index)                # Deletes the 1st node given it's index
        self.epanetClass.getNodeNameID()
        self.assertNotEqual(self.epanetClass.getNodeCount(), node_count, err_msg)
        # Test 3
        idNodes = self.epanetClass.getNodeNameID([1,2])
        self.epanetClass.deleteNode(idNodes)              # Deletes 2 nodes given their IDs
        self.assertNotEqual(self.epanetClass.getNodeNameID([1,2]), idNodes, err_msg)

    def testdeleteNodeJUnctionDemand(self):
        err_msg = 'Demand not deleted'
        # Test 1
        nodeIndex = 1
        baseDemand = 100
        patternId = '1'
        categoryIndex = 1
        categoryIndex = self.epanetClass.addNodeJunctionDemand(nodeIndex, baseDemand, patternId, 'new demand')    # Adds a new demand to the 1st node and returns the new demand index
        self.epanetClass.getNodeJunctionDemandIndex(nodeIndex)                                                    # Retrieves the indices of all demands for the 1st node
        self.epanetClass.deleteNodeJunctionDemand(1, 2)                                                           # Deletes the 2nd demand of the 1st node
        self.assertNotEqual(self.epanetClass.getNodeJunctionDemandIndex(nodeIndex), [1, 2], err_msg)
        # Test 2
        categoryIndex_2 = self.epanetClass.addNodeJunctionDemand(nodeIndex, baseDemand, patternId, 'new demand_2')   # Adds a new demand to the first node and returns the new demand index
        categoryIndex_3 = self.epanetClass.addNodeJunctionDemand(nodeIndex, baseDemand, patternId, 'new demand_3')   # Adds a new demand to the first node and returns the new demand index
        self.epanetClass.deleteNodeJunctionDemand(1)                                                                 # Deletes all the demands of the 1st node
        self.assertNotEqual(self.epanetClass.getNodeJunctionDemandName(1), {1: [''], 2: ['new demand_2'], 3: ['new demand_3']}, err_msg)
        # Test 3
        nodeIndex = [1, 2, 3]
        baseDemand = [100, 110, 150]
        patternId = ['1', '1', '']
        categoryIndex = self.epanetClass.addNodeJunctionDemand(nodeIndex, baseDemand, patternId, ['new demand_1', 'new demand_2', 'new demand_3'])     # Adds 3 new demands to the first 3 nodes
        demand_index_old = self.epanetClass.getNodeJunctionDemandIndex(nodeIndex)
        self.epanetClass.deleteNodeJunctionDemand([1,2,3])                                     # Deletes all the demands of the first 3 nodes
        self.assertNotEqual(self.epanetClass.getNodeJunctionDemandIndex(nodeIndex), demand_index_old, err_msg)

    def testsdeletePattern(self):
        err_msg = 'Pattern not deleted'
        # Test 1
        idPat = self.epanetClass.getPatternNameID(1)    # Retrieves the ID of the 1st pattern
        self.epanetClass.deletePattern(idPat)           # Deletes the 1st pattern given it's ID
        self.assertEqual(self.epanetClass.getPatternNameID(), [], err_msg)
        # Test 2
        self.epanetClass = epanet('Net1.inp')
        index = 1
        self.epanetClass.deletePattern(index)           # Deletes the 1st pattern given it's index
        self.assertEqual(self.epanetClass.getPatternNameID(), [], err_msg)

    def testdeletePatternsAll(self):
        err_msg = 'All Patterns not deleted'
        d = epanet('BWSN_Network_1.inp')
        d.deletePatternsAll()       # Deletes all the patterns
        self.assertEqual(d.getPatternNameID(), [], err_msg)

    def testdeleteRules(self):
        err_msg = 'Rule not deleted'
        # Test 1
        d = epanet('BWSN_Network_1.inp')
        rule_count = d.getRuleCount()        # Retrieves the number of rules
        d.deleteRules()                      # Deletes all the rule-based control
        self.assertEqual(d.getRuleCount(), 0, err_msg)
        # Test 2
        d = epanet('BWSN_Network_1.inp')
        rule_id_1 = d.getRuleID(1)
        d.deleteRules(1)        # Deletes the 1st rule-based control
        self.assertNotEqual(d.getRuleID(1), rule_id_1, err_msg)
        # Test 3
        d = epanet('BWSN_Network_1.inp')
        d.deleteRules([1,2,3])  # Deletes the 1st to 3rd rule-based control
        self.assertEqual(d.getRuleCount(), 1, err_msg)

class GetTest(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        # Create EPANET object using the INP file
        inpname = 'Net1.inp'
        self.epanetClass = epanet(inpname)

    def tearDown(self):
        """Call after every test case."""
        self.epanetClass.unload()

    def testgetComputedHydraulicTimeSeries(self):
        data = self.epanetClass.getComputedHydraulicTimeSeries(['Time','Pressure', 'Velocity'])
        self.assertEqual(
            data.Time.all(),
            np.array([    0,  3600,  7200, 10800, 14400, 18000, 21600, 25200, 28800,
                                32400, 36000, 39600, 43200, 45154, 46800, 50400, 54000, 57600,
                                61200, 64800, 68400, 72000, 75600, 79200, 81690, 82800, 86400]).all(),
            'Wrong Time output')
        self.assertEqual(
            data.Pressure.all(),
            np.matrix([[127.54072491, 119.25732074, 117.02125399, 118.66902368,
                        117.66115716, 118.75815405, 120.73696519, 115.86077993,
                        110.79018511,   0.        ,  51.996     ],
                        [128.58963612, 120.45028753, 118.34940585, 119.99139321,
                        118.94074548, 120.07340709, 122.05444889, 117.14855347,
                        112.0894993 ,   0.        ,  53.32542596],
                        [129.24743752, 121.19853401, 119.633948  , 120.91182173,
                        119.34717535, 120.82394882, 122.78398354, 117.00731724,
                        111.88895591,   0.        ,  54.6243226 ],
                        [129.95740184, 122.00620684, 120.53119195, 121.80401471,
                        120.21268816, 121.70906898, 123.67069653, 117.87722459,
                        112.76452393,   0.        ,  55.52219246],
                        [130.2807869 , 122.37412937, 121.39879063, 122.22626599,
                        120.12852018, 121.88262608, 123.82066328, 117.12817501,
                        111.89206413,   0.        ,  56.39910545],
                        [130.66581304, 122.81220852, 121.88417723, 122.70842025,
                        120.59761555, 122.35995953, 124.29888252, 117.59909621,
                        112.36522402,   0.        ,  56.88469473],
                        [130.67296063, 122.82034125, 122.35404163, 122.65949442,
                        120.05043713, 121.99713313, 123.90925151, 116.27646055,
                        110.86955714,   0.        ,  57.3588257 ],
                        [130.74630016, 122.90378911, 122.44621817, 122.75097749,
                        120.13971557, 122.0875427 , 123.99983233, 116.36598084,
                        110.95932278,   0.        ,  57.45101172],
                        [131.18618207, 123.40432512, 122.54022505, 123.36008274,
                        121.23167202, 123.00507407, 124.94519528, 118.23560812,
                        113.00477303,   0.        ,  57.54101105],
                        [131.54976976, 123.818075  , 122.99861945, 123.81539416,
                        121.67471938, 123.45577412, 125.39673394, 118.68034567,
                        113.4515494 ,   0.        ,  57.99958929],
                        [132.26981375, 124.63753647, 123.45427607, 124.71035299,
                        123.03261446, 124.59180141, 126.55864067, 120.71122109,
                        115.61661061,   0.        ,  58.44725465],
                        [132.9081991 , 125.36415115, 124.26141912, 125.51278568,
                        123.81133141, 125.3875497 , 127.35583525, 121.49373493,
                        116.40390485,   0.        ,  59.2549267 ],
                        [133.88680955, 126.47817303, 125.06096964, 126.67233084,
                        125.40691528, 126.71568902, 128.70816244, 123.65496369,
                        118.65176767,   0.        ,  60.04320918],
                        [120.59982887, 120.59982887, 125.59789324, 126.72157821,
                        123.67823733, 126.01248102, 128.12522042, 122.15478432,
                        117.43828897,   0.        ,  60.66200396],
                        [119.72714682, 119.72714682, 124.72521117, 125.84889613,
                        122.80555524, 125.13979893, 127.25253834, 121.28210222,
                        116.56560675,   0.        ,  59.78932188],
                        [118.06362697, 118.06362697, 122.83656011, 124.31324935,
                        121.56672857, 123.84418926, 125.97512722, 120.55898111,
                        115.97230307,   0.        ,  57.88066121],
                        [116.53669821, 116.53669821, 121.30963132, 122.78632057,
                        120.0397998 , 122.31726048, 124.44819844, 119.03205233,
                        114.4453743 ,   0.        ,  56.35373242],
                        [115.20762616, 115.20762616, 119.7988526 , 121.56045663,
                        119.05350362, 121.28513391, 123.43076018, 118.46198943,
                        113.98008889,   0.        ,  54.82680366],
                        [114.06242929, 114.06242929, 118.65365571, 120.41525973,
                        117.90830673, 120.13993702, 122.28556329, 117.31679255,
                        112.834892  ,   0.        ,  53.68160676],
                        [113.06571302, 113.06571302, 117.52057855, 119.49599534,
                        117.16882471, 119.36606181, 121.52271085, 116.88967053,
                        112.48639969,   0.        ,  52.53640989],
                        [112.30224802, 112.30224802, 116.75711353, 118.73253032,
                        116.4053597 , 118.6025968 , 120.75924583, 116.12620552,
                        111.72293467,   0.        ,  51.77294487],
                        [111.39030245, 111.39030245, 115.98152881, 117.74313285,
                        115.23617987, 117.46781014, 119.61343642, 114.64466568,
                        110.16276513,   0.        ,  51.00947987],
                        [110.24510565, 110.24510565, 114.83633199, 116.59793602,
                        114.09098305, 116.32261333, 118.4682396 , 113.49946886,
                        109.01756832,   0.        ,  49.86428304],
                        [108.90205223, 108.90205223, 113.67498514, 115.15167441,
                        112.40515372, 114.68261436, 116.81355232, 111.39740624,
                        106.81072819,   0.        ,  48.71908624],
                        [124.48318538, 115.78099067, 112.71091153, 114.63566434,
                        114.22834319, 114.80094526, 116.79751399, 112.82805364,
                        107.68452094,   0.        ,  47.66296061],
                        [124.92020828, 116.27777211, 113.2647933 , 115.18812071,
                        114.76197096, 115.35222877, 117.34954606, 113.36596566,
                        108.22952342,   0.        ,  48.2175138 ],
                        [125.96844576, 117.46948079, 115.03090241, 116.68717363,
                        115.74356881, 116.7866562 , 118.76214431, 113.93079598,
                        108.84261138,   0.        ,  50.00371454]]).all(),
            'Wrong Pressure output')

        self.assertEqual(
            data.Velocity.all(),
            np.matrix([[2.35286666e+00, 2.57230086e+00, 5.28331232e-01, 7.80876836e-01,
                        3.42300951e-01, 4.63083582e-01, 9.65991272e-01, 1.96883153e+00,
                        5.35291644e-01, 1.87239674e-01, 8.98762391e-01, 6.71632643e-01,
                        0.00000000e+00],
                        [2.33068336e+00, 2.54358132e+00, 5.31503118e-01, 7.66706780e-01,
                        3.40098253e-01, 4.59157105e-01, 9.43807974e-01, 1.95324794e+00,
                        5.43910881e-01, 1.92195745e-01, 8.96553748e-01, 6.75559120e-01,
                        0.00000000e+00],
                        [2.31666322e+00, 2.42681077e+00, 7.06538850e-01, 6.16194761e-01,
                        3.60385189e-01, 4.79042564e-01, 6.52412757e-01, 2.01414361e+00,
                        8.33956122e-01, 3.38033502e-01, 1.03539489e+00, 8.82616905e-01,
                        0.00000000e+00],
                        [2.30143547e+00, 2.40683910e+00, 7.08704481e-01, 6.06673617e-01,
                        3.58881279e-01, 4.77175094e-01, 6.37185006e-01, 2.00395017e+00,
                        8.39530985e-01, 3.41417300e-01, 1.03434444e+00, 8.84484375e-01,
                        0.00000000e+00],
                        [2.29446581e+00, 2.29272219e+00, 8.81628950e-01, 4.66778486e-01,
                        3.80634370e-01, 5.16575880e-01, 3.52840266e-01, 2.08248825e+00,
                        1.11879071e+00, 4.83956208e-01, 1.18416296e+00, 1.07202683e+00,
                        0.00000000e+00],
                        [2.28613994e+00, 2.28166679e+00, 8.82777453e-01, 4.61720309e-01,
                        3.79836799e-01, 5.15884056e-01, 3.44514395e-01, 2.07718101e+00,
                        1.12167872e+00, 4.85750744e-01, 1.18377381e+00, 1.07271866e+00,
                        0.00000000e+00],
                        [2.28598509e+00, 2.17126060e+00, 1.05313231e+00, 3.32329449e-01,
                        4.03374341e-01, 5.67236868e-01, 6.69844709e-02, 2.17052609e+00,
                        1.39244025e+00, 6.24274636e-01, 1.34031534e+00, 1.24830909e+00,
                        0.00000000e+00],
                        [2.28439619e+00, 2.16912714e+00, 1.05334394e+00, 3.31394073e-01,
                        4.03227377e-01, 5.67150521e-01, 6.53955686e-02, 2.16955962e+00,
                        1.39296444e+00, 6.24605306e-01, 1.34026677e+00, 1.24839544e+00,
                        0.00000000e+00],
                        [2.27483897e+00, 2.26665454e+00, 8.84333876e-01, 4.54863175e-01,
                        3.78755949e-01, 5.14956307e-01, 3.33213425e-01, 2.06998989e+00,
                        1.12559170e+00, 4.88182655e-01, 1.18325195e+00, 1.07364641e+00,
                        0.00000000e+00],
                        [2.26690942e+00, 2.25611915e+00, 8.85426211e-01, 4.50052565e-01,
                        3.77997383e-01, 5.14312510e-01, 3.25283877e-01, 2.06494751e+00,
                        1.12833479e+00, 4.89889428e-01, 1.18288981e+00, 1.07429020e+00,
                        0.00000000e+00],
                        [2.25112342e+00, 2.34078445e+00, 7.15844666e-01, 5.75283611e-01,
                        3.53922817e-01, 4.71191987e-01, 5.86872961e-01, 1.97040625e+00,
                        8.57866915e-01, 3.52573840e-01, 1.03097894e+00, 8.90467483e-01,
                        0.00000000e+00],
                        [2.23703453e+00, 2.32226979e+00, 7.17841800e-01, 5.66509789e-01,
                        3.52535919e-01, 4.69565723e-01, 5.72784064e-01, 1.96104697e+00,
                        8.62979515e-01, 3.55694360e-01, 1.03006417e+00, 8.92093747e-01,
                        0.00000000e+00],
                        [2.21526305e+00, 2.39387356e+00, 5.48041427e-01, 6.93165074e-01,
                        3.28613316e-01, 4.39732471e-01, 8.28387669e-01, 1.87271337e+00,
                        5.88352732e-01, 2.18036853e-01, 8.85627391e-01, 6.94983754e-01,
                        0.00000000e+00],
                        [1.06626930e-06, 7.46894277e-01, 7.70294218e-01, 2.87189089e-01,
                        1.74271100e-01, 3.25297366e-01, 1.38687645e+00, 8.51162565e-01,
                        1.14342079e+00, 5.65306840e-01, 8.21257645e-01, 8.09418859e-01,
                        0.00000000e+00],
                        [1.05667364e-06, 7.46894264e-01, 7.70294219e-01, 2.87189086e-01,
                        1.74271099e-01, 3.25297361e-01, 1.38687644e+00, 8.51162566e-01,
                        1.14342079e+00, 5.65306841e-01, 8.21257642e-01, 8.09418864e-01,
                        0.00000000e+00],
                        [1.03714862e-06, 5.97515677e-01, 6.16235394e-01, 2.29751348e-01,
                        1.39416867e-01, 2.60237879e-01, 1.10950134e+00, 6.80929970e-01,
                        9.14736679e-01, 4.52245502e-01, 6.57006108e-01, 6.47535101e-01,
                        0.00000000e+00],
                        [1.01552852e-06, 5.97515652e-01, 6.16235392e-01, 2.29751341e-01,
                        1.39416868e-01, 2.60237880e-01, 1.10950132e+00, 6.80929978e-01,
                        9.14736675e-01, 4.52245499e-01, 6.57006109e-01, 6.47535100e-01,
                        0.00000000e+00],
                        [9.97188290e-07, 4.48137076e-01, 4.62176568e-01, 1.72313606e-01,
                        1.04562635e-01, 1.95178398e-01, 8.32126229e-01, 5.10697378e-01,
                        6.86052563e-01, 3.39184161e-01, 4.92754575e-01, 4.85651337e-01,
                        0.00000000e+00],
                        [9.82963944e-07, 4.48137050e-01, 4.62176566e-01, 1.72313598e-01,
                        1.04562636e-01, 1.95178399e-01, 8.32126211e-01, 5.10697387e-01,
                        6.86052558e-01, 3.39184158e-01, 4.92754575e-01, 4.85651336e-01,
                        0.00000000e+00],
                        [9.70469226e-07, 2.98758484e-01, 3.08117742e-01, 1.14875867e-01,
                        6.97084020e-02, 1.30118916e-01, 5.54751123e-01, 3.40464784e-01,
                        4.57368448e-01, 2.26122821e-01, 3.28503041e-01, 3.23767574e-01,
                        0.00000000e+00],
                        [9.55911660e-07, 2.98758469e-01, 3.08117741e-01, 1.14875862e-01,
                        6.97084027e-02, 1.30118917e-01, 5.54751113e-01, 3.40464789e-01,
                        4.57368445e-01, 2.26122820e-01, 3.28503041e-01, 3.23767573e-01,
                        0.00000000e+00],
                        [9.45234760e-07, 4.48137001e-01, 4.62176562e-01, 1.72313584e-01,
                        1.04562638e-01, 1.95178400e-01, 8.32126177e-01, 5.10697402e-01,
                        6.86052550e-01, 3.39184153e-01, 4.92754576e-01, 4.85651334e-01,
                        0.00000000e+00],
                        [9.28221894e-07, 4.48136976e-01, 4.62176561e-01, 1.72313576e-01,
                        1.04562639e-01, 1.95178401e-01, 8.32126160e-01, 5.10697409e-01,
                        6.86052546e-01, 3.39184150e-01, 4.92754577e-01, 4.85651334e-01,
                        0.00000000e+00],
                        [9.08472163e-07, 5.97515505e-01, 6.16235382e-01, 2.29751297e-01,
                        1.39416875e-01, 2.60237885e-01, 1.10950122e+00, 6.80930023e-01,
                        9.14736650e-01, 4.52245483e-01, 6.57006112e-01, 6.47535094e-01,
                        0.00000000e+00],
                        [2.41636847e+00, 2.74378595e+00, 3.49838258e-01, 9.68602133e-01,
                        3.24414877e-01, 4.87272679e-01, 1.30686816e+00, 1.96101598e+00,
                        2.10786072e-01, 3.59999778e-02, 7.84713183e-01, 4.20500301e-01,
                        0.00000000e+00],
                        [2.40739457e+00, 2.73233851e+00, 3.50950539e-01, 9.62793939e-01,
                        3.23642460e-01, 4.84966403e-01, 1.29789426e+00, 1.95437753e+00,
                        2.14623692e-01, 3.77379168e-02, 7.83415903e-01, 4.22806577e-01,
                        0.00000000e+00],
                        [2.38573232e+00, 2.61481977e+00, 5.23638045e-01, 8.01889505e-01,
                        3.45560109e-01, 4.69014194e-01, 9.98856937e-01, 1.99197922e+00,
                        5.22476018e-01, 1.79906568e-01, 9.02098360e-01, 6.65702031e-01,
                        0.00000000e+00]]).all(),
            'Wrong velocity output')

    def testgetComputedQualityTimeSeries(self):
        self.assertEqual(
            self.epanetClass.getComputedQualityTimeSeries().NodeQuality[10].all(),
            np.matrix([[1., 0.45269294, 0.44701226, 0.43946804, 0.42596667,
                0.4392986 , 0.45068901, 0.41946084, 0.4033391 , 1.,
                0.97200717]]).all(),
            'Wrong NodeQuality output')
        self.assertEqual(self.epanetClass.getComputedQualityTimeSeries().LinkQuality.all(),
            np.matrix([[0.79051035, 0.44701226, 0.43946804, 0.43188486, 0.45136891,
                0.40885247, 0.4475449 , 0.440129  , 0.44680907, 0.44516552,
                0.41946084, 0.40761727, 1.]]).all(),
            'Wrong Link Quality output')

    def testgetConnectivityMatrix(self):
        self.assertEqual(self.epanetClass.getConnectivityMatrix().all(),
                         np.array([[0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                                [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
                                [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                                [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
                                [0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
                                [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
                                [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
                                [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
                                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]]).all(),
                         'Wrong connectivity matrix output'
                         )

    def testgetControls(self):
        self.assertDictEqual(self.epanetClass.getControls(1).to_dict(),
                                {'Type': 'LOWLEVEL', 'LinkID': '9', 'Setting': 'OPEN',
                                'NodeID': '2', 'Value': 110.0,
                                'Control': 'LINK 9 OPEN IF NODE 2 BELOW 110.0'})

    def testgetCurveComment(self):
        d = epanet('Net3.inp')
        self.assertEqual(d.getCurveComment([1,2]),
                         ['PUMP: Pump Curve for Pump 10 (Lake Source)',
                          'PUMP: Pump Curve for Pump 335 (River Source)'],
                         'Wrong curve comment output')

    def testgetCounts(self):
        self.maxDiff = None
        self.assertDictEqual(self.epanetClass.getCounts().to_dict(),
                            {'Nodes': 11, 'Links': 13, 'Junctions': 9, 'Reservoirs': 1, 'Tanks': 1,
                             'Pipes': 12, 'Pumps': 1, 'Valves': 0, 'Curves': 1, 'SimpleControls': 2,
                             'RuleBasedControls': 0, 'Patterns': 1},
                            'Wrong counts output')

    def testgetCurvesData(self):

        ''' ---getCurvesindex---    '''
        d = epanet('Net3.inp')
        err_msg = 'Wrong curve index'
        # Test 1
        curveID = d.getCurveNameID(1)
        self.assertEqual(d.getCurveIndex(curveID), 1, err_msg)
        # Test2
        curveID = d.getCurveNameID([1,2])
        self.assertEqual(d.getCurveIndex(curveID), [1,2], err_msg)

        ''' ---getCurveLengths---    '''
        d = epanet('Richmond_standard.inp')
        err_msg = 'Wrong curve lengths'
        # Test 3
        self.assertEqual(d.getCurveLengths(list(range(1,10))), [8, 6, 10, 9, 10, 10, 7, 9, 6], err_msg)
        # Test 4
        self.assertEqual(d.getCurveLengths('1006'), 8, err_msg)

        ''' ---getCurveNameID---    '''
        err_msg = 'Wrong curve IDs'
        # Test 5
        self.assertEqual(d.getCurveNameID(10), '2007', err_msg)
        # Test 6
        self.assertEqual(d.getCurveNameID([1,2]), ['1006', '1123'], err_msg)

        ''' ---getCurveNameID---    '''
        err_msg = 'Wrong curve info'
        curves_info = d.getCurvesInfo()
        # Test 7
        self.assertEqual(curves_info.CurveNvalue[0], 8, err_msg)
        # Test 8
        self.assertEqual(curves_info.CurveXvalue[1], [0.0, 2.78, 5.56, 8.53, 11.11, 13.89], err_msg)
        # Test 9
        self.assertEqual(curves_info.CurveYvalue[1], [88.0, 87.0, 84.0, 76.0, 63.0, 47.0], err_msg)

        ''' ---getCurveType---    '''
        err_msg = 'Wrong curve type'
        # Test 10
        self.assertEqual(d.getCurveType(10), 'PUMP', err_msg)
        # Test 11
        self.assertEqual(d.getCurveType([2,3]), ['PUMP', 'GENERAL'], err_msg)

        ''' ---getCurveType---    '''
        err_msg = 'Wrong curve type index'
        # Test 11
        self.assertEqual(d.getCurveTypeIndex(10), 1, err_msg)
        # Test 12
        self.assertEqual(d.getCurveTypeIndex([2,3]), [1, 4], err_msg)

        ''' ---getCurveValue---    '''
        err_msg = 'Wrong curve value'
        # Test 13
        self.assertEqual(d.getCurveValue()[2][0], [0.0, 88.0], err_msg)
        # Test 14
        curveIndex = 1
        pointIndex = 1
        self.assertEqual(d.getCurveValue(curveIndex, pointIndex).all() , np.array([ 0., 38.]).all(), err_msg)

    def testgetDemandModel(self):
        self.assertDictEqual(self.epanetClass.getDemandModel().to_dict(),
                             {'DemandModelCode': 0, 'DemandModelPmin': 0.0, 'DemandModelPreq': 0.1,
                              'DemandModelPexp': 0.5, 'DemandModelType': 'DDA'},
                             'Wrong demand model data')

    def testgetError(self):
        self.assertEqual(self.epanetClass.getError(250), 'Error 250: function call contains invalid format', 'Wrong error output')

    def testgetLinkQuality(self):
        err_msg = 'Wrong Quality output'
        self.assertEqual(self.epanetClass.getLinkQuality().all(),
                         np.array([100.0, 100.0, 100.0, 100.0, 100.0,
                                   100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 0.0]).all(),
                         err_msg)

    def testgetLinkType(self):

        ''' ---getLinkType---    '''
        err_msg = 'Wrong Link Type output'
        # Test 1
        self.assertEqual(self.epanetClass.getLinkType(),
                         ['PIPE', 'PIPE', 'PIPE', 'PIPE', 'PIPE', 'PIPE', 'PIPE',
                          'PIPE', 'PIPE', 'PIPE', 'PIPE', 'PIPE', 'PUMP'],
                         err_msg)
        # Test 2
        self.assertEqual(self.epanetClass.getLinkType(1), 'PIPE', err_msg)

        ''' ---getLinkTypeIndex---    '''
        err_msg = 'Wrong Link Type index output'
        # Test 3
        self.assertEqual(self.epanetClass.getLinkTypeIndex(),
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
                         err_msg)
        # Test 4
        self.assertEqual(self.epanetClass.getLinkTypeIndex([2,3]), [1, 1], err_msg)

    def testgetLink_Node_NameID(self):

        ''' ---getLinkNameID---    '''
        err_msg = 'Wrong Link IDs'
        self.assertEqual(self.epanetClass.getLinkNameID(),
                         ['10', '11', '12', '21', '22', '31', '110',
                          '111', '112', '113', '121', '122', '9'],
                         err_msg)
        self.assertEqual(self.epanetClass.getLinkNameID([1,2,3]), ['10', '11', '12'], err_msg)

        ''' ---getNodeNameID---    '''
        err_msg = 'Wrong Node IDs'
        self.assertEqual(self.epanetClass.getNodeNameID(),
                        ['10', '11', '12', '13', '21', '22', '23', '31', '32', '9', '2'],
                        err_msg)
        self.assertEqual(self.epanetClass.getNodeNameID([1,5,10]), ['10', '21', '9'], err_msg)



    def testgetLinkPumpData(self):

        ''' ---getLinkPumpEfficiency---    '''
        err_msg = 'Wrong Pump Efficiency'
        # Test 1
        self.epanetClass.getComputedQualityTimeSeries()
        self.assertEqual(self.epanetClass.getLinkPumpEfficiency(), np.array([0.75]), err_msg)
        # Test 2
        self.assertEqual(self.epanetClass.getLinkPumpEfficiency(1), 0.75, err_msg)

        ''' ---getLinkPumpECost---    '''
        err_msg = 'Wrong Pump ECost'
        # Test 3
        d = epanet('Richmond_standard.inp')
        self.assertEqual(list(d.getLinkPumpECost()), [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], err_msg)

        ''' ---getLinkPumpECurve---    '''
        err_msg = 'Wrong Pump ECurve'
        # Test 4
        self.assertEqual(list(d.getLinkPumpECurve()), [14, 13, 18, 16, 12, 15, 17], err_msg)

        ''' ---getLinkPumpEPat---    '''
        err_msg = 'Wrong Pump EPat'
        # Test 5
        self.assertEqual(list(d.getLinkPumpEPat()), [14, 14, 19, 17, 15, 16, 18], err_msg)

        ''' ---getLinkPumpHCurve---    '''
        err_msg = 'Wrong Pump HCurve'
        # Test 6
        self.assertEqual(list(d.getLinkPumpHCurve()), [10, 11,  1,  6,  8,  2,  7], err_msg)

        ''' ---getLinkPumpHeadCurveIndex---    '''
        err_msg = 'Wrong Pump Head Curve Index'
        # Test 7
        [curveIndex, pumpIndex] = d.getLinkPumpHeadCurveIndex()
        self.assertEqual(list(curveIndex), [10, 11, 1, 6, 8, 2, 7], err_msg)
        self.assertEqual(list(pumpIndex), [950, 951, 952, 953, 954, 955, 956], err_msg)

        ''' ---getLinkPumpPatternIndex---    '''
        pumpID = 'newPump_1'
        fromNode = '11'
        toNode = '22'
        initialStatus = 1
        initialSetting = 1.2
        power = 10
        patternIndex = 1
        pumpIndex = self.epanetClass.addLinkPump(pumpID, fromNode, toNode, initialStatus, initialSetting, power, patternIndex)
        err_msg = 'Wrong Pump Pattern Index'
        # Test 8
        self.assertEqual(list(self.epanetClass.getLinkPumpPatternIndex()), [0, 1],  err_msg)

        ''' ---getLinkPumpPatternNameID---    '''
        err_msg = 'Wrong Pump Pattern IDs'
        # Test 9
        self.assertEqual(list(self.epanetClass.getLinkPumpPatternNameID()), ['', '1'],  err_msg)

        ''' ---getLinkPumpPower---    '''
        err_msg = 'Wrong Pump Power'
        # Test 10
        self.assertEqual(self.epanetClass.getLinkPumpPower(pumpIndex),  10, err_msg)

        ''' ---getLinkPumpSwitches---    '''
        err_msg = 'Wrong Pump Switches'
        # Test 11
        d.unload()
        d = epanet('Richmond_standard.inp')
        self.assertEqual(d.getLinkPumpSwitches(),  [3, 2, 3, 6, 6, 4, 2], err_msg)

        ''' ---getLinkPumpType---    '''
        err_msg = 'Wrong Pump Type'
        # Test 12
        self.assertEqual(d.getLinkPumpType(),  ['CUSTOM', 'CUSTOM', 'CUSTOM', 'CUSTOM', 'CUSTOM', 'CUSTOM', 'CUSTOM'], err_msg)

        ''' ---getLinkPumpTypeCode---    '''
        err_msg = 'Wrong Pump Type Code'
        # Test 13
        self.assertEqual(d.getLinkPumpTypeCode(),  [2, 2, 2, 2, 2, 2, 2], err_msg)
        self.epanetClass.unload()
        self.epanetClass = epanet('Net1.inp')
        self.assertEqual(self.epanetClass.getLinkPumpTypeCode(),  [1], err_msg)

    def testgetLinksInfo(self):
        # Desired data
        LinkBulkReactionCoeff = [-0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, 0.0]
        LinkDiameter = [18.0, 14.0, 10.0, 10.0, 12.0, 6.0, 18.0, 10.0, 12.0, 8.0, 8.0, 6.0, 0.0]
        LinkInitialSetting = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 1.0]
        LinkInitialStatus = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        LinkLength = [10530.0, 5280.0, 5280.0, 5280.0, 5280.0, 5280.0, 200.0, 5280.0, 5280.0, 5280.0, 5280.0, 5280.0, 0.0]
        LinkMinorLossCoeff = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        LinkRoughnessCoeff = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 0.0]
        LinkTypeIndex = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2]
        LinkWallReactionCoeff = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 0.0]
        NodesConnectingLinksIndex = [[1, 2], [2, 3], [3, 4], [5, 6], [6, 7], [8, 9], [11, 3], [2, 5], [3, 6], [4, 7], [5, 8], [6, 9], [10, 1]]
        # Actual data
        l_info = self.epanetClass.getLinksInfo()
        # Test 1
        self.assertEqual(l_info.LinkBulkReactionCoeff,  LinkBulkReactionCoeff, 'Wrong LinkBulkReactionCoeff output')
        # Test 2
        self.assertEqual(l_info.LinkDiameter,  LinkDiameter, 'Wrong LinkDiameter output')
        # Test 3
        self.assertEqual(l_info.LinkInitialSetting,  LinkInitialSetting, 'Wrong LinkInitialSetting output')
        # Test 4
        self.assertEqual(l_info.LinkInitialStatus,  LinkInitialStatus, 'Wrong LinkInitialStatus output')
        # Test 5
        self.assertEqual(l_info.LinkLength,  LinkLength, 'Wrong LinkLength output')
        # Test 6
        self.assertEqual(l_info.LinkMinorLossCoeff,  LinkMinorLossCoeff, 'Wrong LinkMinorLossCoeff output')
        # Test 7
        self.assertEqual(l_info.LinkRoughnessCoeff,  LinkRoughnessCoeff, 'Wrong LinkRoughnessCoeff output')
        # Test 8
        self.assertEqual(l_info.LinkTypeIndex,  LinkTypeIndex, 'Wrong LinkTypeIndex output')
        # Test 9
        self.assertEqual(l_info.LinkWallReactionCoeff,  LinkWallReactionCoeff, 'Wrong LinkWallReactionCoeff output')
        # Test 10
        self.assertEqual(l_info.NodesConnectingLinksIndex,  NodesConnectingLinksIndex, 'Wrong NodesConnectingLinksIndex output')

    def testgetLinkVertices(self):
        d = epanet('ky10.inp')
        l_vertices = d.getLinkVertices()
        vert_link_2 = [5774062.57, 5774072.58, 5774084.86, 5774143.46, 5774181.97, 5774256.77, 5774331.86, 5774408.93, 5774481.77, 5774548.49, 5774714.61, 5774660.84, 5774565.26]
        self.assertEqual(l_vertices['x'][2], vert_link_2, 'Wrong vertices value')
        self.assertEqual(len(l_vertices['x']), d.getLinkCount(), 'Wrong vertices list length ')
        self.assertEqual(len(d.getLinkVerticesCount()), d.getLinkCount(), 'Wrong vertices count')
        self.assertEqual(d.getLinkVerticesCount([1,2,3]), [5, 13, 28], 'Wrong vertices for the first 3 links')

    def testgetLinkIndex_LinkNodesIndex(self):
        indices = self.epanetClass.getLinkIndex()
        self.assertEqual(indices, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], 'Wrong link indices')
        l_n_indices = self.epanetClass.getLinkNodesIndex([1,2,3])
        self.assertEqual(l_n_indices, [[1, 2], [2, 3], [3, 4]], 'Wrong link nodes indices')

    def testgetLinkPipe_Pump_Valve(self):
        d = epanet('Net3.inp')
        # Pipe
        pipe_indices = d.getLinkPipeIndex()
        self.assertEqual(pipe_indices, list(range(1,118)), 'Wrong pipe indices')
        pipe_IDs = d.getLinkPipeNameID([1,2,3])
        self.assertEqual(pipe_IDs, ['20', '40', '50'], 'Wrong pipe IDs')
        # Pump
        pump_indices = list(d.getLinkPumpIndex())
        self.assertEqual(pump_indices, [118, 119], 'Wrong pump indices')
        pump_IDs = d.getLinkPumpNameID([1,2])
        self.assertEqual(pump_IDs, ['10', '335'], 'Wrong pump IDs')
        # Valve
        d = epanet('ky10.inp')
        valve_indices = list(d.getLinkValveIndex())
        self.assertEqual(valve_indices, [1057, 1058, 1059, 1060, 1061], 'Wrong valve indices')
        valve_IDs = d.getLinkValveNameID([1,2,3])
        self.assertEqual(valve_IDs, ['~@RV-1', '~@RV-2', '~@RV-3'], 'Wrong valve IDs')

    def testgetNodeInfo(self):
        n_info = self.epanetClass.getNodesInfo()
        self.assertEqual(list(n_info.NodeElevations), [710.0, 710.0, 700.0, 695.0, 700.0, 695.0, 690.0, 700.0, 710.0, 800.0, 850.0], 'Wrong Node Elevation output')
        self.assertEqual(list(n_info.NodeEmitterCoeff), [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'Wrong Node Emitter Coeff output')
        self.assertEqual(list(n_info.NodeInitialQuality), [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 1.0], 'Wrong Node Initial Quality output')
        self.assertEqual(list(n_info.NodePatternIndex), [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0], 'Wrong Node Pattern Index output')
        self.assertEqual(list(n_info.NodeSourcePatternIndex), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Wrong Node Source Pattern Index output')
        self.assertEqual(list(n_info.NodeSourceQuality), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Wrong Node Source Quality output')
        self.assertEqual(list(n_info.NodeSourceTypeIndex), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Wrong Node Source Type Index output')
        self.assertEqual(list(n_info.NodeTypeIndex), [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2], 'Wrong Node Type Index output')

    def testgetNodeBaseDemands(self):
        b_dems = list(self.epanetClass.getNodeBaseDemands()[1])
        self.assertEqual(b_dems, [0.0, 150.0, 150.0, 100.0, 150.0, 200.0, 150.0, 100.0, 100.0, 0.0, 0.0], 'Wrong Node Base Demand output')

    def testgetNodeCoordinates(self):
        # Actual Values
        coords = self.epanetClass.getNodeCoordinates()
        # Desired Values
        x_desired = {1: 20.0, 2: 30.0, 3: 50.0, 4: 70.0, 5: 30.0, 6: 50.0, 7: 70.0, 8: 30.0, 9: 50.0, 10: 10.0, 11: 50.0}
        y_desired = {1: 70.0, 2: 70.0, 3: 70.0, 4: 70.0, 5: 40.0, 6: 40.0, 7: 40.0, 8: 10.0, 9: 10.0, 10: 70.0, 11: 90.0}
        x_vert_desired = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: [], 13: []}
        y_vert_desired = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: [], 13: []}
        # Test
        self.assertDictEqual(coords['x'], x_desired, 'Wrong x coordinate values')
        self.assertDictEqual(coords['y'], y_desired, 'Wrong y coordinate values')
        self.assertDictEqual(coords['x_vert'], x_vert_desired, 'Wrong x vertices coordinate values')
        self.assertDictEqual(coords['y_vert'], y_vert_desired, 'Wrong y vertices coordinate values')

    def testDemandsInfo(self):
        ''' ---getNodeDemandCategoriesNumber---    '''
        err_msg = 'Wrong Demand Categories Number Output'
        self.assertEqual(self.epanetClass.getNodeDemandCategoriesNumber(), [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0], err_msg)
        self.assertEqual(self.epanetClass.getNodeDemandCategoriesNumber(1), 1, err_msg)
        self.assertEqual(self.epanetClass.getNodeDemandCategoriesNumber([1,4,10]), [1, 1, 0], err_msg)

        ''' ---getNodeDemandDeficit---    ''' ###### Check again for inconsistent output, dynamic might be the case,  
                                                ###### getComputedHydraulicTimeSeries.DemandDeficit works fine ### 
        self.epanetClass.setDemandModel('PDA', 0, 0.1, 0.5) 
        actual_def = self.epanetClass.getComputedHydraulicTimeSeries().DemandDeficit[0].tolist()[0]
        desired_dem_def  = [0.0, -0.0012342832044413999, -0.0012111212332749546, -0.0012281893931302976, -0.0012177492556971789, 
                    -0.0012291126064630734, -0.0012496099800993576, -0.0011990998540248189, -0.0011465764024330798, 0.0, 0.0]
        self.assertEqual(actual_def, desired_dem_def, 'Wrong Demand Deficit Output')

        ''' ---getNodeDemandPatternIndex---    '''
        d = epanet('BWSN_Network_1.inp')
        self.assertEqual(len(d.getNodeDemandPatternIndex()), 2, 'Wrong Node Demand Pattern Dict length')
        self.assertEqual(d.getNodeDemandPatternIndex()[2][120:122],[2, 2], 'Wrong Node Demand Pattern Index Output')
                                                 
        ''' ---getNodeDemandPatternNameID---    '''
        self.assertEqual(len(d.getNodeDemandPatternNameID()), 2, 'Wrong Node Demand Pattern Dict length')
        self.assertEqual(d.getNodeDemandPatternNameID()[2][120:122], ['PATTERN-1', 'PATTERN-1'], 'Wrong Node Demand Pattern ID Output')
            
    def testgetNodeInitialQuality(self):
        desired_init_qual = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 1.0]
        self.assertEqual(list(self.epanetClass.getNodeInitialQuality()), desired_init_qual, 'Wrong Initial quality value')
      
    def testgetNodeJunctionData(self):
        ''' ---getNodeJunctionDemandIndex---    ''' 
        d = epanet('BWSN_Network_1.inp')
        err_msg = 'Wrong Junction Demand Index output'
        self.assertEqual(d.getNodeJunctionDemandIndex(1,''), 1, err_msg)
        self.assertEqual(d.getNodeJunctionDemandIndex([1,2,3]), [[0, 0, 0], [1, 1, 1]], err_msg)
        d.unload()
        
        ''' ---getNodeJunctionDemandName---    '''
        err_msg = 'Wrong Junction Demand Name ID output'
        self.assertDictEqual(self.epanetClass.getNodeJunctionDemandName(), {1: ['', '', '', '', '', '', '', '', '']}, err_msg)
        
        ''' ---getNodeJunctionIndex---    '''
        err_msg = 'Wrong Junction Index output'
        self.assertEqual(self.epanetClass.getNodeJunctionIndex(), [1, 2, 3, 4, 5, 6, 7, 8, 9], err_msg)
        
        ''' ---getNodeJunctionNameID---    '''
        err_msg = 'Wrong Junction Name ID output'
        self.assertEqual(self.epanetClass.getNodeJunctionNameID(), ['10', '11', '12', '13', '21', '22', '23', '31', '32'], err_msg)
        
    def testgetNodeReservoirIndex_ID(self):
        
        ''' ---getNodeReservoirIndex---    '''
        d = epanet('ky9.inp')
        self.assertEqual(d.getNodeReservoirIndex(),  [1243, 1244, 1245, 1246], 'Wrong Node Reservoir Index Output')        
        self.assertEqual(d.getNodeReservoirIndex([1,2,3]),  [1243, 1244, 1245], 'Wrong Node Reservoir Index Output')        
        
        ''' ---getNodeReservoirNameID---    '''
        self.assertEqual(d.getNodeReservoirNameID(),  ['R-1', 'R-2', 'R-3', 'R-4'], 'Wrong Node Reservoir ID Output')        
        self.assertEqual(d.getNodeReservoirNameID([1,2,3]),  ['R-1', 'R-2', 'R-3'], 'Wrong Node Reservoir ID Output')        
        d.unload()
          
    def testGetNodeConnectingLinksIndex_ID(self):
          
        ''' ---getNodesConnectingLinksID---    '''
        desired_n_conn_l_ID = [['10', '11'], ['11', '12'], ['12', '13'], ['21', '22'], ['22', '23'], ['31', '32'], ['2', '12'], ['11', '21'], 
                               ['12', '22'], ['13', '23'], ['21', '31'], ['22', '32'], ['9', '10']]
        self.assertEqual(self.epanetClass.getNodesConnectingLinksID(),  desired_n_conn_l_ID, 'Wrong Nodes Connecting Links ID Output')        
        self.assertEqual(self.epanetClass.getNodesConnectingLinksID([1,2,3]), [['10', '11'], ['11', '12'], ['12', '13']], 'Wrong Nodes Connecting Links ID Output')    
        
        ''' ---getNodesConnectingLinksIndex---    '''
        desired_n_conn_l_ind = [[1, 2], [2, 3], [3, 4], [5, 6], [6, 7], [8, 9], [11, 3], [2, 5], [3, 6], [4, 7], [5, 8], [6, 9], [10, 1]]
        self.assertEqual(self.epanetClass.getNodesConnectingLinksIndex(),  desired_n_conn_l_ind, 'Wrong Nodes Connecting Links index Output')        
        
    def testgetNodeTankData(self):
        # Net1
        tData = self.epanetClass.getNodeTankData().to_dict()
        desired_tData = {'Index': [11], 'Elevation': np.array([850.]), 'Initial_Level': np.array([120.]),
                        'Minimum_Water_Level': np.array([100.]), 'Maximum_Water_Level': np.array([150.]),
                        'Diameter': np.array([50.5]), 'Minimum_Water_Volume': np.array([200296.1666]), 
                        'Maximum_Water_Volume': np.array([50.5]),'Volume_Curve_Index': np.array([0])}  
        self.assertEqual(tData['Index'], desired_tData['Index'])
        np.testing.assert_array_almost_equal_nulp(tData['Elevation'], desired_tData['Elevation'])
        np.testing.assert_array_almost_equal_nulp(tData['Initial_Level'], desired_tData['Initial_Level'])
        np.testing.assert_array_almost_equal_nulp(tData['Minimum_Water_Level'], desired_tData['Minimum_Water_Level'])
        np.testing.assert_array_almost_equal_nulp(tData['Maximum_Water_Level'], desired_tData['Maximum_Water_Level'])
        np.testing.assert_array_almost_equal_nulp(tData['Diameter'], desired_tData['Diameter'])
        np.testing.assert_array_almost_equal_nulp(tData['Minimum_Water_Volume'], desired_tData['Minimum_Water_Volume'])
        np.testing.assert_array_almost_equal_nulp(tData['Volume_Curve_Index'], desired_tData['Volume_Curve_Index'])

        # ky10
        d = epanet('ky10.inp')
        tData = d.getNodeTankData().to_dict()
        desired_tData = {'Index': [923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935],
                         'Elevation': np.array([839.2236, 865.8419, 923.39  , 951.6379, 959.5179, 717.3331,
                                      942.2059, 975.39  , 735.6371, 742.2835, 757.7068, 823.2291,811.4059]), 
                         'Initial_Level': np.array([140.7764, 179.1581, 101.61, 158.3621,  70.4821,  82.6669,
                                        67.7941,  84.6101, 134.3629, 102.7165, 142.2932, 121.7709,148.5941]),
                         'Minimum_Water_Level': np.array([125.77639999999997, 159.1581, 81.61009999999999, 148.36210000000005, 
                                                    65.48209999999995, 72.66690000000006, 61.79409999999996, 74.61009999999999, 
                                                    124.36289999999997, 97.7165, 117.29319999999996, 106.77089999999998, 133.59410000000003]), 
                         'Maximum_Water_Level': np.array([145.7764, 181.6581, 106.61  , 173.3621,  95.4821,  97.6669,
                                                87.7941,  89.6101, 139.3629, 132.7165, 147.2932, 141.7709, 153.5941]),
                         'Diameter': np.array([30., 36., 26., 26., 25., 40., 20., 30., 58., 50., 52., 52., 40.]), 
                         'Minimum_Water_Volume': np.array([ 88906.0982, 162003.2134,  43329.1552,  78769.7649,  32143.4605,
                                                91315.882 ,  19413.1796,  52738.7366, 328576.659 , 191865.8795,
                                                249097.5199, 226751.1364, 167879.2973]), 
                         'Maximum_Water_Volume': np.array([103043.265143, 184905.42384766001, 56602.33107023415, 92042.99386315, 
                                                46869.676065625, 122731.80854, 27581.320500399997, 63341.611807249996, 368207.85033021, 
                                                260588.21880625002, 312809.01892312005, 301081.21859364, 193012.038532]), 
                         'Volume_Curve_Index': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])}  

        self.assertEqual(tData['Index'], desired_tData['Index'])
        self.assertEqual(d.getNodeTankNameID(), ['T-1', 'T-10', 'T-11', 'T-12', 'T-13', 'T-2', 'T-3', 'T-4', 'T-5', 'T-6', 'T-7', 'T-8', 'T-9'])
        np.testing.assert_array_almost_equal_nulp(tData['Elevation'], desired_tData['Elevation'])
        np.testing.assert_array_almost_equal_nulp(tData['Initial_Level'], desired_tData['Initial_Level'], nulp=5)
        np.testing.assert_array_almost_equal_nulp(tData['Minimum_Water_Level'], desired_tData['Minimum_Water_Level'])
        np.testing.assert_array_almost_equal_nulp(tData['Maximum_Water_Level'], desired_tData['Maximum_Water_Level'],nulp=5)
        np.testing.assert_array_almost_equal_nulp(tData['Diameter'], desired_tData['Diameter'], nulp=5)
        np.testing.assert_array_almost_equal_nulp(tData['Minimum_Water_Volume'], desired_tData['Minimum_Water_Volume'], nulp=5)
        np.testing.assert_array_almost_equal_nulp(tData['Volume_Curve_Index'], desired_tData['Volume_Curve_Index'], nulp=5)


    def testgetnodeTankMix(self):
        d = epanet('ky10.inp')

        ''' ---getNodeTankMixingFraction---    '''
        actual = list(d.getNodeTankMixingFraction())
        desired = [1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.]
        self.assertEqual(actual, desired, 'Wrong Node Tank Mixing Fraction Output')

        ''' ---getNodeTankMixingModelCode---    '''
        actual = list(d.getNodeTankMixingModelCode())
        desired = [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]
        self.assertEqual(actual, desired, 'Wrong Node Tank Mixing Model Code Output')

        ''' ---getNodeTankMixingModelType---    '''
        actual = list(d.getNodeTankMixingModelType())
        desired = ['MIX1', 'MIX1', 'MIX1', 'MIX1', 'MIX1', 'MIX1', 'MIX1', 'MIX1', 'MIX1', 'MIX1', 'MIX1', 'MIX1', 'MIX1']
        self.assertEqual(actual, desired, 'Wrong Node Tank Mixing Model Type Output')

        ''' ---getNodeTankMixZoneVolume---    '''
        actual = d.getNodeTankMixZoneVolume()
        desired = np.array([103043.265143  , 184905.42384766,  56602.33107023,  92042.99386315,
                    46869.67606562, 122731.80854   ,  27581.3205004 ,  63341.61180725,
                    368207.85033021, 260588.21880625, 312809.01892312, 301081.21859364,
                    193012.038532  ])
        self.assertEqual(actual.all(), desired.all(), 'Wrong Node Tank Mix Zone Volume Output')

    def testgetNodeType(self):

        ''' ---getNodeType---    '''
        desired_node_type = ['JUNCTION', 'JUNCTION', 'JUNCTION', 'JUNCTION', 'JUNCTION', 
                            'JUNCTION', 'JUNCTION', 'JUNCTION', 'JUNCTION', 'RESERVOIR', 'TANK']
        self.assertEqual(self.epanetClass.getNodeType(), desired_node_type, 'Wrong Node Type Output')
        self.assertEqual(self.epanetClass.getNodeType([10,11]), ['RESERVOIR', 'TANK'], 'Wrong Node Type Output')
        
        ''' ---getNodeTypeIndex---    '''
        desired_node_type_index = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2]
        self.assertEqual(self.epanetClass.getNodeTypeIndex(), desired_node_type_index, 'Wrong Node Type Index Output')
        self.assertEqual(self.epanetClass.getNodeTypeIndex([10,11]), [1, 2], 'Wrong Node Type Index Output')

    def testgetOptions(self):
        err_msg = 'Wrong options Output'
        d = epanet('BWSN_Network_1.inp')
        self.assertEqual(d.getOptionsAccuracyValue(), 0.005, 'Wrong Options Accuracy Value Output')
        self.assertEqual(d.getOptionsCheckFrequency(), 2.0, 'Wrong Options Check Frequency Output'), 
        self.assertEqual(d.getOptionsDampLimit(), 0.0, 'Wrong Options Damping Limit Output')
        self.assertEqual(d.getOptionsDemandCharge(), 0.0, 'Wrong Options Demand Charge Output')
        self.assertEqual(d.getOptionsEmitterExponent(), 0.5, 'Wrong Options Emitter Exponent Output')
        self.assertEqual(d.getOptionsExtraTrials(), -1.0, 'Wrong Options Extra Trials Output')
        self.assertEqual(d.getOptionsFlowChange(), 0.0, 'Wrong Options Flow Change Output')
        self.assertEqual(d.getOptionsGlobalEffic(), 75.0, 'Wrong Options Global Effic Output')
        self.assertEqual(d.getOptionsGlobalPrice(), 0.0, 'Wrong Options Global Price Output')
        self.assertEqual(d.getOptionsGlobalPattern(), 0.0, 'Wrong Options Global Pattern Output')
        self.assertEqual(d.getOptionsHeadError(), 0.0, 'Wrong Options Head Error Output')
        self.assertEqual(d.getOptionsHeadLossFormula(), 'HW', 'Wrong Options Head Loss Formula Output')
        self.assertEqual(d.getOptionsLimitingConcentration(), 0.0, 'Wrong Options Limiting Concentration Output')
        self.assertEqual(d.getOptionsMaximumCheck(), 10, 'Wrong Options Maximum CheckOutput')
        self.assertEqual(d.getOptionsMaxTrials(), 40, 'Wrong Options Max Trials Output')
        self.assertEqual(d.getOptionsPatternDemandMultiplier(), 1.0, 'Wrong Options Pattern Demand Multiplier Output')
        self.assertEqual(d.getOptionsPipeBulkReactionOrder(), 1, 'Wrong Options Pipe Bulk Reaction Order Output')
        self.assertEqual(d.getOptionsPipeWallReactionOrder(), 1, 'Wrong Options Pipe Wall Reaction Order Output')
        self.assertEqual(d.getOptionsQualityTolerance(), 0.01, 'Wrong Options Quality Tolerance Output')
        self.assertEqual(d.getOptionsSpecificDiffusivity(), 100.0, 'Wrong Options Specific Diffusivity Output')
        self.assertEqual(d.getOptionsSpecificGravity(), 1.0, 'Wrong Options Specific Gravity Output')
        self.assertEqual(d.getOptionsSpecificViscosity(), 1.0, 'Wrong Options Specific Viscosity Output')
        self.assertEqual(d.getOptionsTankBulkReactionOrder(), 1, 'Wrong Options Tank Bulk Reaction Order Output')

    def testgetPattern(self):
        d = epanet('BWSN_Network_1.inp')

        ''' ---getPattern---    '''
        desired_pattern = np.array([[1.560e+00, 1.360e+00, 1.170e+00, 1.130e+00, 1.080e+00, 1.040e+00,
                                    1.200e+00, 6.400e-01, 1.080e+00, 5.300e-01, 2.900e-01, 9.000e-01,
                                    1.110e+00, 1.060e+00, 1.000e+00, 1.650e+00, 5.500e-01, 7.400e-01,
                                    6.400e-01, 4.600e-01, 5.800e-01, 6.400e-01, 7.100e-01, 6.600e-01,
                                    6.800e-01, 4.300e-01, 3.700e-01, 3.300e-01, 2.300e-01, 2.100e-01,
                                    6.000e-02, 1.000e-01, 1.000e-01, 1.400e-01, 9.000e-02, 1.000e-01,
                                    9.000e-02, 9.000e-02, 3.000e-02, 2.300e-01, 2.700e-01, 7.200e-01,
                                    9.300e-01, 1.130e+00, 1.390e+00, 1.940e+00, 1.900e+00, 1.830e+00,
                                    2.730e+00, 1.740e+00, 1.290e+00, 1.410e+00, 1.390e+00, 1.350e+00,
                                    1.190e+00, 1.340e+00, 9.500e-01, 1.270e+00, 1.280e+00, 1.090e+00,
                                    1.010e+00, 1.130e+00, 1.000e+00, 7.700e-01, 6.700e-01, 7.600e-01,
                                    7.600e-01, 7.100e-01, 5.800e-01, 8.600e-01, 9.600e-01, 9.700e-01,
                                    8.200e-01, 7.100e-01, 6.500e-01, 6.200e-01, 4.400e-01, 4.800e-01,
                                    5.500e-01, 5.600e-01, 6.100e-01, 6.000e-01, 4.400e-01, 4.600e-01,
                                    4.400e-01, 4.000e-01, 4.400e-01, 6.900e-01, 7.600e-01, 1.190e+00,
                                    1.330e+00, 1.730e+00, 1.970e+00, 2.370e+00, 2.280e+00, 2.100e+00],
                                [8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01,
                                    8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01,
                                    8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01,
                                    0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00,
                                    0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00,
                                    0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00,
                                    0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00,
                                    0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 8.000e+01, 8.000e+01,
                                    8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01,
                                    8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01,
                                    8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01, 8.000e+01, 0.000e+00,
                                    0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00,
                                    0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00,
                                    0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00,
                                    0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00, 0.000e+00,
                                    0.000e+00, 0.000e+00, 0.000e+00, 8.000e+01, 8.000e+01, 8.000e+01],
                                [8.000e-01, 8.400e-01, 8.800e-01, 9.700e-01, 1.070e+00, 1.010e+00,
                                    9.600e-01, 9.700e-01, 9.900e-01, 1.080e+00, 1.180e+00, 1.190e+00,
                                    1.190e+00, 1.220e+00, 1.250e+00, 1.250e+00, 1.260e+00, 1.220e+00,
                                    1.190e+00, 1.160e+00, 1.140e+00, 1.120e+00, 1.110e+00, 1.100e+00,
                                    1.100e+00, 1.060e+00, 1.020e+00, 1.010e+00, 1.010e+00, 1.000e+00,
                                    1.000e+00, 8.500e-01, 7.100e-01, 7.000e-01, 6.900e-01, 7.400e-01,
                                    7.900e-01, 8.000e-01, 8.000e-01, 8.000e-01, 8.100e-01, 7.700e-01,
                                    7.400e-01, 7.400e-01, 7.500e-01, 7.800e-01, 8.100e-01, 8.000e-01,
                                    0.000e+00, 8.000e-01, 8.400e-01, 8.800e-01, 9.700e-01, 1.070e+00,
                                    1.010e+00, 9.600e-01, 9.700e-01, 9.900e-01, 1.080e+00, 1.180e+00,
                                    1.190e+00, 1.190e+00, 1.220e+00, 1.250e+00, 1.250e+00, 1.260e+00,
                                    1.220e+00, 1.190e+00, 1.160e+00, 1.140e+00, 1.120e+00, 1.110e+00,
                                    1.100e+00, 1.100e+00, 1.060e+00, 1.020e+00, 1.010e+00, 1.010e+00,
                                    1.000e+00, 1.000e+00, 8.500e-01, 7.100e-01, 7.000e-01, 6.900e-01,
                                    7.400e-01, 7.900e-01, 8.000e-01, 8.000e-01, 8.000e-01, 8.100e-01,
                                    7.700e-01, 7.400e-01, 7.400e-01, 7.500e-01, 7.800e-01, 8.100e-01],
                                [4.233e+02, 2.250e+02, 2.670e+01, 2.670e+01, 2.670e+01, 2.670e+01,
                                    2.670e+01, 2.670e+01, 2.670e+01, 2.021e+02, 3.775e+02, 2.021e+02,
                                    2.580e+01, 2.590e+01, 2.590e+01, 2.600e+01, 2.600e+01, 2.610e+01,
                                    2.610e+01, 2.610e+01, 2.620e+01, 2.630e+01, 2.630e+01, 2.630e+01,
                                    2.630e+01, 2.630e+01, 2.640e+01, 2.399e+02, 4.535e+02, 2.405e+02,
                                    2.740e+01, 2.678e+02, 5.081e+02, 4.621e+02, 4.160e+02, 3.275e+02,
                                    2.389e+02, 1.330e+02, 2.710e+01, 2.710e+01, 2.710e+01, 2.710e+01,
                                    2.710e+01, 2.480e+02, 4.689e+02, 3.607e+02, 2.524e+02, 4.495e+02,
                                    6.465e+02, 3.366e+02, 2.680e+01, 1.989e+02, 3.711e+02, 1.984e+02,
                                    2.580e+01, 2.580e+01, 2.580e+01, 2.580e+01, 2.580e+01, 2.590e+01,
                                    2.600e+01, 2.600e+01, 2.600e+01, 2.610e+01, 2.620e+01, 2.620e+01,
                                    2.620e+01, 2.620e+01, 2.630e+01, 2.630e+01, 2.630e+01, 2.630e+01,
                                    2.630e+01, 2.283e+02, 4.302e+02, 6.572e+02, 8.842e+02, 8.842e+02,
                                    8.843e+02, 8.844e+02, 8.845e+02, 8.845e+02, 8.845e+02, 6.633e+02,
                                    4.421e+02, 2.342e+02, 2.630e+01, 4.720e+01, 6.800e+01, 3.522e+02,
                                    6.364e+02, 3.312e+02, 2.600e+01, 2.610e+01, 2.610e+01, 2.247e+02]])
        actual_pattern = d.getPattern()
        self.assertEqual(actual_pattern.all(), desired_pattern.all(), 'Wrong Patterns Output')

        ''' ---getPatternAverageValue---    '''
        desired_pat_avg_val = [0.8856250000000001, 33.333333333333336, 0.967291666666667, 209.6072916666666]
        actual_pat_avg_val = d.getPatternAverageValue()
        self.assertEqual(desired_pat_avg_val, actual_pat_avg_val, 'Wrong Patterns Average Value Output') 

        ''' ---getPatternComment---    '''
        desired_comment = ['', '', '', '']
        actual_comment = d.getPatternComment()
        self.assertEqual(actual_comment, desired_comment, 'Wrong Pattern Comment Output')
        
        ''' ---getPatternIndex---    '''
        self.assertEqual(d.getPatternIndex(), [1, 2, 3, 4], 'Wrong Pattern Index Output')

        ''' ---getPatternLengths---    '''
        self.assertEqual(d.getPatternLengths() , [96, 96, 48, 96], 'Wrong Patterns Output')

        ''' ---getPatternNameID---    '''
        desired_pat_ID = ['PATTERN-0', 'PATTERN-1', 'PATTERN-2', 'PATTERN-3']
        actual_pat_ID = d.getPatternNameID() 
        self.assertEqual(actual_pat_ID, desired_pat_ID, 'Wrong Pattern ID Output')

        ''' ---getPatternValue---    '''
        self.assertEqual(d.getPatternValue(1, 5), 1.08, 'Wrong Pattern Value Output')

    def testgetQualityInfo(self):
        desired_qual_info_dict = {'QualityCode': 1, 'QualityChemName': 'Chlorine', 
                                'QualityChemUnits': 'mg/L', 'TraceNode': 0, 'QualityType': 'CHEM'}
        actual_qual_info_dict = self.epanetClass.getQualityInfo().to_dict()
        self.assertDictEqual(actual_qual_info_dict, desired_qual_info_dict, 'Wrong Quality Info Output')

    def testgetRuleInfo(self):
        d = epanet('BWSN_Network_1.inp')
        
        ''' ---getRuleID---    '''
        self.assertEqual(d.getRuleID() , ['RULE-0', 'RULE-1', 'RULE-3'], 'Wrong Rule ID Output')
        
        ''' ---getRuleInfo---    '''
        desired_rule_info = {'Index': [1, 2, 3, 4], 'Premises': [1, 1, 1, 1], 'ThenActions': [1, 1, 1, 1],
                             'ElseActions': [0, 0, 0, 0], 'Priority': [1.0, 1.0, 1.0, 1.0]}
        actual_rule_info = d.getRuleInfo().to_dict()
        self.assertDictEqual(actual_rule_info, desired_rule_info, 'Wrong Rule Info Output')

        ''' ---getRules---    '''
        desired_rule = {'Rule_ID': 'RULE-0', 
                        'Premises': ['IF NODE TANK-130 LEVEL >= 16.0'], 
                        'Then_Actions': ['THEN PUMP PUMP-172 STATUS IS CLOSED'], 
                        'Else_Actions': [], 
                        'Rule': ['RULE RULE-0', ['IF NODE TANK-130 LEVEL >= 16.0'], 
                        ['THEN PUMP PUMP-172 STATUS IS CLOSED'], [], 'PRIORITY 1.0']}
        actual_rule = d.getRules()[1]
        self.assertDictEqual(actual_rule, desired_rule, 'Wrong Rule Output')

    def testGetTime(self):
        self.assertEqual(self.epanetClass.getTimeSimulationDuration(), 86400, 'Wrong Simulation Duration Output')
        self.assertEqual(self.epanetClass.getTimeHydraulicStep(), 3600, 'Wrong Hydraulic StepOutput')
        self.assertEqual(self.epanetClass.getTimeQualityStep(), 300, 'Wrong Quality Step Output')
        self.assertEqual(self.epanetClass.getTimePatternStep(), 7200, 'Wrong Pattern Step Output')
        self.assertEqual(self.epanetClass.getTimePatternStart(), 0, 'Wrong Pattern Start Output')
        self.assertEqual(self.epanetClass.getTimeReportingStep(), 3600, 'Wrong Time Reporting Step Output')
        self.assertEqual(self.epanetClass.getTimeReportingStart(), 0, 'Wrong Time  Output')
        self.assertEqual(self.epanetClass.getTimeRuleControlStep(), 360, 'Wrong Time Reporting Start Output')
        self.assertEqual(self.epanetClass.getTimeStatisticsType(), 'NONE', 'Wrong Time Statistics Type Output')
        self.assertEqual(self.epanetClass.getTimeReportingPeriods(), 0, 'Wrong Time  Output')
        self.assertEqual(self.epanetClass.getTimeStartTime(), 0, 'Wrong Reporting Periods  Output')
        self.assertEqual(self.epanetClass.getTimeHTime(), 0, 'Wrong hydraulic solution Time Output')
        self.assertEqual(self.epanetClass.getTimeQTime(), 0, 'Wrong quality solution Time Output')
        self.assertEqual(self.epanetClass.getTimeHaltFlag(), 0, 'Wrong Halt Flag Time Output')
        self.assertEqual(self.epanetClass.getTimeNextEvent(), 3600, 'Wrong Time Next Event Output')
        self.assertEqual(self.epanetClass.getTimeNextEventTank(), 0, 'Wrong Time Next Event Tank Output')

class SetTest(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        # Create EPANET object using the INP file
        inpname = 'Net1.inp'
        self.epanetClass = epanet(inpname)

    def tearDown(self):
        """Call after every test case."""
        self.epanetClass.unload()

    def testsetControls(self):
        # Test 1
        controlIndex = 1
        control = 'LINK 9 CLOSED IF NODE 2 ABOVE 180'
        self.epanetClass.setControls(controlIndex, control)     
        control_data = self.epanetClass.getControls(controlIndex)
        self.assertEqual(control_data.Control, 'LINK 9 CLOSED IF NODE 2 ABOVE 180.0', 'Wrong Control Output')
        self.assertEqual(control_data.LinkID, '9', 'Wrong Control LinkID Output')
        self.assertEqual(control_data.NodeID, '2', 'Wrong Control NodeID Output')
        self.assertEqual(control_data.Setting, 'CLOSED', 'Wrong Control Setting Output')
        self.assertEqual(control_data.Type, 'HIGHLEVEL', 'Wrong Control Type Output')

        # Test 2
        control_1 = 'LINK 9 OPEN IF NODE 2 BELOW 110.0'
        control_2 = 'LINK 9 CLOSED IF NODE 2 ABOVE 200.0'
        controls = [control_1, control_2]
        self.epanetClass.setControls(controls)              
        self.assertEqual(self.epanetClass.getControls(1).Control, control_1, 'Wrong Control Output')
        self.assertEqual(self.epanetClass.getControls(2).Control, control_2, 'Wrong Control Output')

    def testsetCurve(self):
        
        ''' ---setCurve---    '''
        d = epanet('BWSN_Network_1.inp')
        curveIndex = 1
        d.getCurvesInfo().CurveXvalue[curveIndex-1]
        d.getCurvesInfo().CurveYvalue[curveIndex-1]
        x_y_1 = [0, 730]
        x_y_2 = [1000, 500]
        x_y_3 = [1350, 260]
        values = [x_y_1, x_y_2, x_y_3]
        d.setCurve(curveIndex, values)
        actual_x = d.getCurvesInfo().CurveXvalue[curveIndex-1]
        self.assertEqual(actual_x, [0.0, 1000.0, 1350.0], 'Wrong Curve X Value Output')
        actual_y = d.getCurvesInfo().CurveYvalue[curveIndex-1]
        self.assertEqual(actual_y, [730.0, 500.0, 260.0], 'Wrong Curve Y Value Output')
        
        ''' ---setCurveComment---    '''
        curveIndex = [1,2]
        comment = ['This is the 1st curve', 'This is the 2nd curve']
        d.setCurveComment(curveIndex, comment)
        desired_comment = ['This is the 1st curve', 'This is the 2nd curve']
        self.assertEqual(d.getCurveComment(curveIndex), desired_comment, 'Wrong Curve Comment Output')

        ''' ---setCurveNameID---    '''       
        d.setCurveNameID([1, 2], ['Curve1', 'Curve2'])
        self.assertEqual(d.getCurveNameID(), ['Curve1', 'Curve2', 'CURVE-2'], 'Wrong Curve ID')

        ''' ---setCurveValue---    '''  
        err_msg = 'Wrong Curve Value Output'     
        curveIndex = 1          
        curvePoint = 1                                         
        x_y_values = [10, 400]                                 
        d.setCurveValue(curveIndex, curvePoint, x_y_values)
        self.assertAlmostEqual(d.getCurvesInfo().CurveXvalue[curveIndex-1][0], x_y_values[0], err_msg)
        self.assertEqual(d.getCurvesInfo().CurveYvalue[curveIndex-1][0], x_y_values[1], err_msg) 
        
        d.unload()
        
    def testsetDemandModel(self):
        type = 'PDA'
        pmin = 0
        preq = 0.1
        pexp = 0.5
        self.epanetClass.setDemandModel(type, pmin, preq, pexp)
        desired = {'DemandModelCode': 1, 'DemandModelPmin': 0.0, 'DemandModelPreq': 0.1, 
                   'DemandModelPexp': 0.5, 'DemandModelType': 'PDA'}
        actual = self.epanetClass.getDemandModel().to_dict()
        self.assertDictEqual(actual,desired, 'Wrong Set Demand Model Output')

    def testsetFlowunits(self):
        self.epanetClass.setFlowUnitsAFD()
        self.assertEqual(self.epanetClass.getFlowUnits(), 'AFD', 'Error setting flow units to AFD') 
        self.epanetClass.setFlowUnitsCFS()
        self.assertEqual(self.epanetClass.getFlowUnits(), 'CFS', 'Error setting flow units to CFS') 
        self.epanetClass.setFlowUnitsCMD()
        self.assertEqual(self.epanetClass.getFlowUnits(), 'CMD', 'Error setting flow units to CMD') 
        self.epanetClass.setFlowUnitsCMH()
        self.assertEqual(self.epanetClass.getFlowUnits(), 'CMH', 'Error setting flow units to CMH') 
        self.epanetClass.setFlowUnitsGPM()
        self.assertEqual(self.epanetClass.getFlowUnits(), 'GPM', 'Error setting flow units to GPM') 
        self.epanetClass.setFlowUnitsIMGD()
        self.assertEqual(self.epanetClass.getFlowUnits(), 'IMGD', 'Error setting flow units to IMGD') 
        self.epanetClass.setFlowUnitsLPM()
        self.assertEqual(self.epanetClass.getFlowUnits(), 'LPM', 'Error setting flow units to LPM') 
        self.epanetClass.setFlowUnitsLPS()
        self.assertEqual(self.epanetClass.getFlowUnits(), 'LPS', 'Error setting flow units to LPS') 
        self.epanetClass.setFlowUnitsMGD()
        self.assertEqual(self.epanetClass.getFlowUnits(), 'MGD', 'Error setting flow units to MGD') 
        self.epanetClass.setFlowUnitsMLD()
        self.assertEqual(self.epanetClass.getFlowUnits(), 'MLD', 'Error setting flow units to MLD') 
        
    def testsetLinkBulkReactionCoeff(self):
        err_msg = 'Error setting Link Bulk Reaction Coeff'
        # Test 1
        index_pipe = 1
        coeff = 0
        self.epanetClass.setLinkBulkReactionCoeff(index_pipe, coeff)
        self.assertEqual(self.epanetClass.getLinkBulkReactionCoeff(index_pipe), 0, err_msg)

        # Test 2
        coeffs = self.epanetClass.getLinkBulkReactionCoeff()              
        coeffs_new = [0 for i in coeffs]
        self.epanetClass.setLinkBulkReactionCoeff(coeffs_new) 
        desired_value = [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]
        self.assertEqual(list(self.epanetClass.getLinkBulkReactionCoeff()), desired_value, err_msg) 

    def testsetLinkComment(self):
        err_msg = 'Error setting Link Comment'
        # Test 1
        linkIndex = 1
        comment = 'This is a link'
        self.epanetClass.setLinkComment(linkIndex, comment)
        self.assertEqual(self.epanetClass.getLinkComment(linkIndex)[0], comment, err_msg)   

        # Test 2
        linkIndex = [1, 2]
        comment = ['This is link 1', 'This is link 2']
        self.epanetClass.setLinkComment(linkIndex, comment)   
        self.assertEqual(self.epanetClass.getLinkComment(linkIndex), comment, err_msg)  

    def testsetLinkDiameter(self):
        err_msg = 'Error setting Link Diameter'
        # Test 1
        index_pipe = 1
        diameter = 20
        self.epanetClass.setLinkDiameter(index_pipe, diameter)       
        self.assertEqual(self.epanetClass.getLinkDiameter(index_pipe), 20, err_msg)

        # Test 2
        index_pipes = [1, 2]
        diameters = [20, 25]
        self.epanetClass.setLinkDiameter(index_pipes, diameters)     
        self.assertEqual(list(self.epanetClass.getLinkDiameter(index_pipes)), [20, 25], err_msg)  

    def testsetLinkInitial_Status_Setting(self):

        ''' ---setLinkInitialSetting---    ''' 
        err_msg = 'Error setting Link Initial Setting' 
        # Test 1
        index_pipe = 1
        setting = 80
        self.epanetClass.setLinkInitialSetting(index_pipe, setting) 
        self.assertEqual(self.epanetClass.getLinkInitialSetting(index_pipe), 80, err_msg)

        # Test 2
        settings = self.epanetClass.getLinkInitialSetting()                
        settings_new = settings + 140
        self.epanetClass.setLinkInitialSetting(settings_new)               
        self.assertEqual(list(self.epanetClass.getLinkInitialSetting()), list(settings_new), err_msg)
    
        ''' ---setLinkInitialStatus---    '''  
        err_msg = 'Error setting Link Initial Status'
        # Test 1
        index_pipe = 1
        status = 0
        self.epanetClass.setLinkInitialStatus(index_pipe, status)        
        self.assertEqual(self.epanetClass.getLinkInitialStatus(index_pipe), 0, err_msg) 

        # Test 2
        statuses = self.epanetClass.getLinkInitialStatus()                
        statuses_new = np.zeros(len(statuses))
        self.epanetClass.setLinkInitialStatus(statuses_new) 
        desired = [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]             
        self.assertEqual(list(self.epanetClass.getLinkInitialStatus()), desired, err_msg) 

    def testsetLinkLength(self):
        err_msg = 'Error setting Link Length'
        d = epanet('BWSN_Network_1.inp')
        # Test 1
        index_pipe = 1
        length_pipe = 100
        d.setLinkLength(index_pipe, length_pipe)      
        self.assertEqual(d.getLinkLength(index_pipe), 100, err_msg)

        # Test 2
        lengths = d.getLinkLength()                   
        lengths_new = [i * 1.5 for i in lengths]
        d.setLinkLength(lengths_new)                  
        self.assertEqual(list(d.getLinkLength()), lengths_new, err_msg)

    def testsetLinkMinorLossCoeff(self):
        err_msg = 'Error setting Link Minor Loss Coefficient'
        # Test 1
        index_pipe = 1
        coeff = 105
        self.epanetClass.setLinkMinorLossCoeff(index_pipe, coeff)        
        self.assertEqual(self.epanetClass.getLinkMinorLossCoeff(index_pipe), 105, err_msg)

        # Test 2
        coeffs = self.epanetClass.getLinkMinorLossCoeff()                
        coeffs_new = coeffs + 0.2
        self.epanetClass.setLinkMinorLossCoeff(coeffs_new)        
        desired = np.array([105.2,   0.2,   0.2,   0.2,   0.2,   0.2,   0.2,   0.2,   0.2,
         0.2,   0.2,   0.2,   0. ])      
        np.testing.assert_array_almost_equal(self.epanetClass.getLinkMinorLossCoeff(), desired, err_msg=err_msg)

    def testsetLinkNameID(self):
        err_msg = 'Error setting Link ID'
        d = epanet('BWSN_Network_1.inp')
        # Test 1
        index_pipe = 1
        linkID = 'New_ID'                   
        d.setLinkNameID(index_pipe, linkID) 
        self.assertEqual(d.getLinkNameID(index_pipe), linkID, err_msg)

        # Test 2
        IDs = ['1', '2', '3', '4']         
        d.setLinkNameID(IDs)                
        self.assertEqual(d.getLinkNameID([1,2,3,4]), ['1', '2', '3', '4'], err_msg)

    def testsetLinkNodesIndex(self):
        err_msg = 'Error setting Link ID'
        d = epanet('ky10.inp')
        # Test 1
        linkIndex = 1
        startNode = 2
        endNode   = 3
        d.setLinkNodesIndex(linkIndex, startNode, endNode)
        self.assertEqual(d.getLinkNodesIndex()[0], [2, 3], err_msg)

        # Test 2
        linkIndex = [1, 2]
        startNode = [2, 4]
        endNode   = [3, 5]
        d.setLinkNodesIndex(linkIndex, startNode, endNode)
        self.assertEqual(d.getLinkNodesIndex()[0:2], [[2, 3], [4, 5]], err_msg)

    def testsetLinkPipeData(self):
        pipeIndex = [1, 2]
        length = [1000, 1500]
        diameter = [20, 23]
        RoughnessCoeff = [110, 115]
        MinorLossCoeff = [0.2, 0.3]
        self.epanetClass.setLinkPipeData(pipeIndex, length, diameter, RoughnessCoeff, MinorLossCoeff)
        p_data = self.epanetClass.getLinksInfo()
        np.testing.assert_array_almost_equal(p_data.LinkLength[0:2], length, err_msg='Error setting link length')
        np.testing.assert_array_almost_equal(p_data.LinkDiameter[0:2], diameter, err_msg='Error setting link diameter')
        np.testing.assert_array_almost_equal(p_data.LinkRoughnessCoeff[0:2], RoughnessCoeff, err_msg='Error setting link Roughness Coefficient')
        np.testing.assert_array_almost_equal(p_data.LinkMinorLossCoeff[0:2], MinorLossCoeff, err_msg='Error setting link Minor Loss Coefficient')

    def testsetLinkPump(self):
        d = epanet('Net3_trace.inp')
        
        ''' ---setLinkPumpECost---    '''
        err_msg = 'Error setting pump average energy price (E cost)'
        # Test 1
        d.setLinkPumpECost(0.10)                       
        np.testing.assert_array_almost_equal(d.getLinkPumpECost(), np.array([0.1, 0.1]), err_msg=err_msg)

        # Test 2
        d.setLinkPumpECost([0.10, 0.12])               
        np.testing.assert_array_almost_equal(d.getLinkPumpECost(), np.array([0.1 , 0.12]), err_msg=err_msg)

        # Test 3
        d.setLinkPumpECost(1, 0.15)                    
        np.testing.assert_array_almost_equal(d.getLinkPumpECost(), np.array([0.15, 0.12]), err_msg=err_msg)

        # Test 4
        pumpIndex = d.getLinkPumpIndex()
        d.setLinkPumpECost(pumpIndex, 0.10)            
        np.testing.assert_array_almost_equal(d.getLinkPumpECost(), np.array([0.1, 0.1]), err_msg=err_msg)

        # Test 5
        pumpIndex = d.getLinkPumpIndex()
        d.setLinkPumpECost(pumpIndex, [0.10, 0.12])   
        np.testing.assert_array_almost_equal(d.getLinkPumpECost(), np.array([0.10, 0.12]), err_msg=err_msg)

        ''' ---setLinkPumpECost---    '''
        err_msg = 'Error setting pump efficiency flow curve index'
        # Test 1 
        d.setLinkPumpECurve(1, 2)                
        np.testing.assert_array_almost_equal(d.getLinkPumpECurve(), np.array([2, 0]), err_msg=err_msg)

        # Test 2
        pumpIndex = d.getLinkPumpIndex()
        d.setLinkPumpECurve(pumpIndex, 1)        
        np.testing.assert_array_almost_equal(d.getLinkPumpECurve(), np.array([1, 1]), err_msg=err_msg)

        # Test 3
        pumpIndex = d.getLinkPumpIndex()
        d.setLinkPumpECurve(pumpIndex,[1, 2])    
        np.testing.assert_array_almost_equal(d.getLinkPumpECurve(), np.array([1, 2]), err_msg=err_msg)

        ''' ---getLinkPumpEPat---    '''
        err_msg = 'Error setting pump energy price time pattern index'
        # Test 1 
        d.setLinkPumpEPat(1, 2)               
        np.testing.assert_array_almost_equal(d.getLinkPumpEPat(), np.array([2, 0]), err_msg=err_msg)

        # Test 2 
        pumpIndex = d.getLinkPumpIndex()
        d.setLinkPumpEPat(pumpIndex, 1)       
        np.testing.assert_array_almost_equal(d.getLinkPumpEPat(), np.array([1, 1]), err_msg=err_msg)

        # Test 3 
        pumpIndex = d.getLinkPumpIndex()
        d.setLinkPumpEPat(pumpIndex,[1, 2])    
        np.testing.assert_array_almost_equal(d.getLinkPumpEPat(), np.array([1, 2]), err_msg=err_msg)
        
        ''' ---setLinkPumpHeadCurveIndex---    '''
        err_msg = 'Error setting curves index for pumps index'
        pumpIndex = d.getLinkPumpIndex(1)  
        curveIndex = d.getCurveIndex()[1]
        d.setLinkPumpHeadCurveIndex(pumpIndex, curveIndex)
        np.testing.assert_array_almost_equal(d.getLinkPumpHeadCurveIndex()[0], np.array([2, 2]), err_msg=err_msg)

        ''' ---setLinkPumpPatternIndex---    '''
        err_msg = 'Error setting pump pattern index'
        pumpIndex = d.getLinkPumpIndex()
        d.setLinkPumpPatternIndex(pumpIndex, [3, 4])    
        np.testing.assert_array_almost_equal(d.getLinkPumpPatternIndex(), np.array([3, 4]), err_msg=err_msg)
        
        ''' ---setLinkPumpPower---    '''
        err_msg = 'Error setting pump power'
        pumpIndex = d.getLinkPumpIndex()
        d.setLinkPumpPower(pumpIndex, [10, 15])  
        np.testing.assert_array_almost_equal(d.getLinkPumpPower(), np.array([10., 15.]), err_msg=err_msg)

    def testsetLinkRoughnessCoeff(self):
        err_msg = 'Error setting Link Roughness Coefficient'
        # Test 1
        index_pipe = 1
        coeff = 105
        self.epanetClass.setLinkRoughnessCoeff(index_pipe, coeff)        
        self.assertEqual(self.epanetClass.getLinkRoughnessCoeff(index_pipe), 105, err_msg)

        # Test 2
        coeffs = self.epanetClass.getLinkRoughnessCoeff()                 
        coeffs_new = coeffs + 10
        self.epanetClass.setLinkRoughnessCoeff(coeffs_new)   
        desired =  np.array([115., 110., 110., 110., 110., 110., 110., 110., 110., 110., 110., 110., 0.])            
        np.testing.assert_array_almost_equal(self.epanetClass.getLinkRoughnessCoeff(), desired, err_msg=err_msg)

    def testsetLink_Settings_Status(self):
        ''' ---setLinkSettings---    '''
        err_msg = 'Error setting Link settings'
        settings = self.epanetClass.getLinkSettings()                
        settings_new = [i + 40 for i in settings]
        self.epanetClass.setLinkSettings(settings_new) 
        desired = np.array([140., 140., 140., 140., 140., 140., 140., 140., 140., 140., 140., 140.,  40.])   
        np.testing.assert_array_almost_equal(self.epanetClass.getLinkSettings(), desired, err_msg=err_msg)         
        
        ''' ---setLinkStatus---    '''
        err_msg = 'Error setting Link status'
        statuses = self.epanetClass.getLinkStatus()                 
        statuses_new = [0 for i in statuses]
        desired = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.epanetClass.setLinkStatus(statuses_new)   
        np.testing.assert_array_almost_equal(self.epanetClass.getLinkStatus(), desired, err_msg=err_msg)         
           
    def testsetLinkType(self):
        ''' ---setLinkTypePipe---    ''' 
        err_msg = 'Error setting Link type to pipe'
        linkid = self.epanetClass.getLinkPumpNameID(1)
        index = self.epanetClass.setLinkTypePipe(linkid)            
        self.assertEqual(self.epanetClass.getLinkType(index), 'PIPE', err_msg)
        
        ''' ---setLinkTypePipeCV---    ''' 
        err_msg = 'Error setting Link type to CV Pipe'                            
        linkid = self.epanetClass.getLinkPipeNameID(1)               
        index = self.epanetClass.setLinkTypePipeCV(linkid)     
        self.assertEqual(self.epanetClass.getLinkType(index), 'CVPIPE', err_msg)
      
        ''' ---setLinkTypePump---    ''' 
        err_msg = 'Error setting Link to Pump'
        linkid = self.epanetClass.getLinkPipeNameID(1)             
        index = self.epanetClass.setLinkTypePump(linkid)           
        self.assertEqual(self.epanetClass.getLinkType(index), 'PUMP', err_msg)

        ''' ---setLinkTypeValveFCV---    ''' 
        err_msg = 'Error setting Link to FCV valve'
        linkid = self.epanetClass.getLinkPipeNameID(1)                     
        index = self.epanetClass.setLinkTypeValveFCV(linkid)               
        self.assertEqual(self.epanetClass.getLinkType(index), 'FCV', err_msg)
        
        ''' ---setLinkTypeValveGPV---    ''' 
        err_msg = 'Error setting Link GPV valve'
        linkid = self.epanetClass.getLinkPipeNameID(1)                     
        index = self.epanetClass.setLinkTypeValveGPV(linkid)               
        self.assertEqual(self.epanetClass.getLinkType(index), 'GPV', err_msg)
        
        ''' ---setLinkTypeValvePBV---    ''' 
        err_msg = 'Error setting Link to PBV valve'
        linkid = self.epanetClass.getLinkPipeNameID(1)                     
        index = self.epanetClass.setLinkTypeValvePBV(linkid)               
        self.assertEqual(self.epanetClass.getLinkType(index), 'PBV', err_msg)
        
        ''' ---setLinkTypeValvePRV---    ''' 
        err_msg = 'Error setting Link to PRV valve'
        linkid = self.epanetClass.getLinkPipeNameID(1)                     
        index = self.epanetClass.setLinkTypeValvePRV(linkid)               
        self.assertEqual(self.epanetClass.getLinkType(index), 'PRV', err_msg)
        
        ''' ---setLinkTypeValvePSV---    ''' 
        err_msg = 'Error setting Link to PSV valve'
        linkid = self.epanetClass.getLinkPipeNameID(1)                     
        index = self.epanetClass.setLinkTypeValvePSV(linkid)               
        self.assertEqual(self.epanetClass.getLinkType(index), 'PSV', err_msg)
        
        ''' ---setLinkTypeValveTCV---    ''' 
        err_msg = 'Error setting Link to TCV valve'
        linkid = self.epanetClass.getLinkPipeNameID(1)                     
        index = self.epanetClass.setLinkTypeValveTCV(linkid)               
        self.assertEqual(self.epanetClass.getLinkType(index), 'TCV', err_msg)
        
    def testsetLinkVertices(self):
        linkID = '10'
        x = [22, 24, 28]
        y = [69, 68, 69]
        self.epanetClass.setLinkVertices(linkID, x, y)
        desired_x = [22.0, 24.0, 28.0]
        np.testing.assert_array_almost_equal(self.epanetClass.getLinkVertices(linkID)['x'][1], desired_x, err_msg='Error setting x vertices')
        desired_y = [69.0, 68.0, 69.0]
        np.testing.assert_array_almost_equal(self.epanetClass.getLinkVertices(linkID)['y'][1], desired_y, err_msg='Error setting y vertices')
        
    def testsetLinkWallReactionCoeff(self):
        err_msg = 'Error setting Link Wall reaction coefficient'
        coeffs = self.epanetClass.getLinkWallReactionCoeff()                
        coeffs_new = [0] * len(coeffs)
        self.epanetClass.setLinkWallReactionCoeff(coeffs_new) 
        desired_coeff = np.array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])             
        np.testing.assert_array_almost_equal(self.epanetClass.getLinkWallReactionCoeff(), desired_coeff, err_msg=err_msg)
    
    def testsetNodeBaseDemands(self):
        d=epanet('BWSN_Network_1.inp')   
        err_msg = 'Error setting Node Base Demands'
        
        # Test 1
        index_node = 1
        demand = 5
        d.setNodeBaseDemands(index_node, demand)                   
        self.assertAlmostEqual(d.getNodeBaseDemands()[1][index_node-1], demand, err_msg)

        # Test 2
        nodeIndex = list(range(1,6))
        BaseDems = d.getNodeBaseDemands()[1]
        baseDems = list(np.array(BaseDems)[0:5])                   
        demands = [10, 5, 15, 20, 5]
        d.setNodeBaseDemands(nodeIndex, demands) 
        desired = np.array([10.,  5., 15., 20.,  5.])                  
        np.testing.assert_array_almost_equal(d.getNodeBaseDemands()[1][0:5], desired, err_msg=err_msg)
        
        # Test 3
        nodeIndex = 121
        categoryIndex = 2
        demand = 25
        d.setNodeBaseDemands(nodeIndex, categoryIndex, demand)       
        self.assertAlmostEqual(d.getNodeBaseDemands()[categoryIndex][nodeIndex-1], demand, err_msg)
        
    def testsetNodeComment(self):
        self.epanetClass.setNodeComment([1,2], ['This is a node', 'Test comm'])  
        self.assertEqual(self.epanetClass.getNodeComment([1,2]) , ['This is a node', 'Test comm'], 'Erron setting node comments')
        
    def testsetNodeCoordinates(self):
        err_msg = 'Error setting Node Coordinates'
        
        # Test 1    
        nodeIndex = 1
        coords = [0,0]
        self.epanetClass.setNodeCoordinates(nodeIndex, coords)   
        desired = {'x': {1: 0.0}, 'y': {1: 0.0}}   
        self.assertDictEqual(self.epanetClass.getNodeCoordinates(nodeIndex), desired, err_msg)

        # Test 2 
        x_values = self.epanetClass.getNodeCoordinates('x')
        y_values = self.epanetClass.getNodeCoordinates('y')
        x_new = [x_values[i]+10 for i in x_values]
        y_new = [y_values[i]+10 for i in y_values]
        new_coords = [x_new, y_new]                    
        self.epanetClass.setNodeCoordinates(new_coords)
        desired_new_x = {1: 10.0, 2: 40.0, 3: 60.0, 4: 80.0, 5: 40.0, 6: 60.0, 7: 80.0, 8: 40.0, 9: 60.0, 10: 20.0, 11: 60.0}
        x_values_new = self.epanetClass.getNodeCoordinates('x')
        self.assertDictEqual(x_values_new, desired_new_x, err_msg)
        desired_new_y = {1: 10.0, 2: 80.0, 3: 80.0, 4: 80.0, 5: 50.0, 6: 50.0, 7: 50.0, 8: 20.0, 9: 20.0, 10: 80.0, 11: 100.0}
        y_values_new = self.epanetClass.getNodeCoordinates('y')
        self.assertDictEqual(y_values_new, desired_new_y, err_msg)
        
    def testsetNodeDemandPatternIndex(self):
        d = epanet('BWSN_Network_1.inp')
        err_msg = 'Error setting Node Demand Pattern Index'
        
        # Test 1
        nodeIndex = np.array(range(1,6))
        d.getNodeDemandPatternIndex()[1][0:5]
        patternIndices = [1, 3, 2, 4, 2]
        d.setNodeDemandPatternIndex(nodeIndex, patternIndices)                 
        self.assertEqual(d.getNodeDemandPatternIndex()[1][0:5], patternIndices, err_msg)
        
        # Test 2
        nodeIndex = 121
        categoryIndex = 2
        d.getNodeDemandPatternIndex()[categoryIndex][nodeIndex-1]                 
        patternIndex = 4
        d.setNodeDemandPatternIndex(nodeIndex, categoryIndex, patternIndex)       
        self.assertEqual(d.getNodeDemandPatternIndex()[categoryIndex][nodeIndex-1], 4, err_msg)
        
        # Test 3
        nodeIndex = np.array(range(1,6))
        categoryIndex = 1
        patDems = d.getNodeDemandPatternIndex()[categoryIndex]
        patDems = list(np.array(patDems)[0:5])
        patternIndices = [1, 3, 2, 4, 2]
        d.setNodeDemandPatternIndex(nodeIndex, categoryIndex, patternIndices)     
        self.assertEqual(d.getNodeDemandPatternIndex()[categoryIndex][0:5], patternIndices, err_msg)
    
    def testsetNodeElevations(self):
        err_msg = 'Error setting node elevations'
        elevs = self.epanetClass.getNodeElevations()               
        elevs_new = elevs + 100
        self.epanetClass.setNodeElevations(elevs_new)              
        np.testing.assert_array_almost_equal(self.epanetClass.getNodeElevations(), elevs_new, err_msg=err_msg)
        
    def testsetNodeEmitterCoeff(self):
        err_msg = 'Error setting node emitter coefficient'
        nodeset = self.epanetClass.getNodeEmitterCoeff()                
        nodeset[0] = 0.1                                 
        self.epanetClass.setNodeEmitterCoeff(nodeset) 
        desired = np.array([0.1, 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. ])                
        np.testing.assert_array_almost_equal(self.epanetClass.getNodeEmitterCoeff(), desired, err_msg=err_msg)
        
    def testsetNodeInitialQuality(self):
        err_msg = 'Error setting node initial quality'
        nodeIndex = 1
        initialQuality = 1
        self.epanetClass.setNodeInitialQuality(nodeIndex, initialQuality)   
        self.assertAlmostEqual(self.epanetClass.getNodeInitialQuality(nodeIndex), 1, err_msg)
        
    def testsetNodeJunctionData(self):
        err_msg = 'Error setting node junction data'
        junctionIndex = 1
        elev = 35
        dmnd = 100
        dmndpat = 'NEW_PATTERN'
        self.epanetClass.addPattern(dmndpat)                                         
        self.epanetClass.setNodeJunctionData(junctionIndex, elev, dmnd, dmndpat)     
        self.assertAlmostEqual(self.epanetClass.getNodeElevations(junctionIndex), elev, 'Error setting node junction data (elevation)')                           
        self.assertAlmostEqual(self.epanetClass.getNodeBaseDemands(junctionIndex)[1], dmnd, 'Error setting node junction data (demand)')                           
        self.assertEqual(self.epanetClass.getNodeDemandPatternNameID()[junctionIndex][0], dmndpat, 'Error setting node junction data (demand pattern)') 
        
    def testsetNodeNameID(self):
        err_msg = 'Error setting node ID'
        
        # Test 1
        nodeIndex = 1
        nameID = 'newID'
        self.epanetClass.setNodeNameID(nodeIndex, nameID) 
        self.assertEqual(self.epanetClass.getNodeNameID(nodeIndex), nameID, err_msg)

        # Test 2
        nameID = self.epanetClass.getNodeNameID()         
        nameID[0] = 'newID_1'
        nameID[4] = 'newID_5'
        self.epanetClass.setNodeNameID(nameID)             
        actual = [self.epanetClass.getNodeNameID()[0], self.epanetClass.getNodeNameID()[4]]
        desired =  [nameID[0], nameID[4]]  
        self.assertEqual(actual, desired, err_msg)
        
    def testsetNodesConnectingLinksID(self):
        err_msg = 'Error setting nodes connecting links IDs'
        
        # Test 1
        self.epanetClass.getNodesConnectingLinksID() 
        linkIndex = 2
        startNodeID = '11'
        endNodeID = '22'
        self.epanetClass.setNodesConnectingLinksID(linkIndex, startNodeID, endNodeID)
        self.assertEqual(self.epanetClass.getNodesConnectingLinksID(linkIndex)[0], [startNodeID, endNodeID], err_msg)

        # Test 2
        linkIndex   = [2, 3]
        startNodeID = ['12', '13']
        endNodeID   = ['21', '22']
        self.epanetClass.setNodesConnectingLinksID(linkIndex, startNodeID, endNodeID)
        self.assertEqual(self.epanetClass.getNodesConnectingLinksID(2)[0], ['12', '21'], err_msg)  
        self.assertEqual(self.epanetClass.getNodesConnectingLinksID(3)[0] , ['13', '22'], err_msg)
        
    def testsetNodeSourcePatternIndex(self):
        err_msg = 'Error setting nodes source Pattern Index'
        nodeIndex = [1,2,3]
        sourcePatternIndex = [1, 1, 1]
        self.epanetClass.setNodeSourcePatternIndex(nodeIndex, sourcePatternIndex)    
        self.assertEqual(list(self.epanetClass.getNodeSourcePatternIndex(nodeIndex)), sourcePatternIndex, err_msg)
     
    def testsetNodeSourceQuality(self):
        err_msg = 'Error setting nodes source Quality'
        nodeIndex = [1,2,3]
        sourceStrength = [10, 12, 8]
        self.epanetClass.setNodeSourceQuality(nodeIndex, sourceStrength)    
        self.assertEqual(list(self.epanetClass.getNodeSourceQuality(nodeIndex)), sourceStrength, err_msg)

    def testsetNodeSourceType(self):
        err_msg = 'Error setting nodes source Type'
        nodeIndex = 1
        sourceType = 'MASS'
        self.epanetClass.setNodeSourceType(nodeIndex, sourceType)     
        self.assertEqual(self.epanetClass.getNodeSourceType(nodeIndex)[0], sourceType, err_msg)

    def testsetNodeTankBulkReactionCoeff(self):
        err_msg = 'Error setting node Tank Bulk Reaction Coefficient'
        d = epanet('BWSN_Network_1.inp')
        
        # Test 1
        tankIndex = d.getNodeTankIndex()
        d.setNodeTankBulkReactionCoeff(tankIndex, 0)              
        self.assertEqual(d.getNodeTankBulkReactionCoeff(1), 0, err_msg)

        # Test 2
        tankIndex = d.getNodeTankIndex([1,2])
        d.setNodeTankBulkReactionCoeff(tankIndex, [-0.5, 0])      
        self.assertEqual(list(d.getNodeTankBulkReactionCoeff()), [-0.5, 0], err_msg)
    
    def testsetNodeTankCanOverFlow(self):
        err_msg = 'Error setting node Tank Can Overflow'
        d = epanet('BWSN_Network_1.inp')
    
        # Test 1
        d.setNodeTankCanOverFlow(1)              
        np.testing.assert_array_almost_equal(d.getNodeTankCanOverFlow(), np.array([1., 1.]), err_msg=err_msg)

        # Test 2
        d.setNodeTankCanOverFlow([1, 0])         
        np.testing.assert_array_almost_equal(d.getNodeTankCanOverFlow(), np.array([1., 0.]), err_msg=err_msg)

        # Test 3
        d.setNodeTankCanOverFlow(1, 0)           
        np.testing.assert_array_almost_equal(d.getNodeTankCanOverFlow(), np.array([0., 0.]), err_msg=err_msg)
        
    def testsetNodeTankData(self):
        d = epanet('Net3_trace.inp')
        tankIndex = [1, 2]    
        elev = [100, 105]
        intlvl = [13, 13.5]
        minlvl =  [0.2, 0.25]
        maxlvl = [30, 35]
        diam = [80, 85]
        minvol = [50000, 60000]
        volcurve = ['', '']   
        d.setNodeTankData(tankIndex, elev, intlvl, minlvl, maxlvl, diam, minvol, volcurve)
        t_Data = d.getNodeTankData(tankIndex)
        np.testing.assert_array_almost_equal(t_Data.Elevation, elev, err_msg='Error Setting Node Tank Elevation')
        np.testing.assert_array_almost_equal(t_Data.Initial_Level, intlvl, err_msg='Error Setting Node Tank Inititial Level') 
        np.testing.assert_array_almost_equal(t_Data.Minimum_Water_Level, minlvl, err_msg='Error Setting Node Tank Min Water Lever') 
        np.testing.assert_array_almost_equal(t_Data.Maximum_Water_Level, maxlvl, err_msg='Error Setting Node Tank Max Water Level') 
        np.testing.assert_array_almost_equal(t_Data.Diameter, diam, err_msg='Error Setting Node Tank Diameter') 
        np.testing.assert_array_almost_equal(t_Data.Minimum_Water_Volume, minvol, err_msg='Error Setting Node Tank Min Water Volume') 
        np.testing.assert_array_almost_equal(t_Data.Elevation, elev, err_msg='Error Setting Node Tank Elevation') 
        
    def testsetNodeTankDiameter(self):
        err_msg = 'Error setting Node Tank Diameter'
        d=epanet('BWSN_Network_1.inp')
        
        # Test 1
        d.setNodeTankDiameter(120)                      
        np.testing.assert_array_almost_equal(d.getNodeTankDiameter(), np.array([120., 120.]), err_msg=err_msg)

        # Test 2
        d.setNodeTankDiameter([110, 130])              
        self.assertEqual(list(d.getNodeTankDiameter()), [110, 130], err_msg)

        # Test 3
        d.setNodeTankDiameter(1, 120)                   
        self.assertEqual(d.getNodeTankDiameter(1), 120, err_msg)
    
    def testsetTankInitialLevel(self):
        err_msg = 'Error setting Node Tank Initial Level'
        d=epanet('BWSN_Network_1.inp')
        
        # Test 1
        tankIndex = d.getNodeTankIndex()
        d.setNodeTankInitialLevel(tankIndex, 10)          
        np.testing.assert_array_almost_equal(d.getNodeTankInitialLevel(), np.array([10., 10.]), err_msg=err_msg)

        # Test 2
        tankIndex = d.getNodeTankIndex()
        d.setNodeTankInitialLevel(tankIndex, [10, 15])    
        np.testing.assert_array_almost_equal(d.getNodeTankInitialLevel(), np.array([10., 15.]), err_msg=err_msg)
    
    def testsetNodeTankMaximumWaterLevel(self):
        err_msg = 'Error setting Node Tank Max Water Level'
        d=epanet('BWSN_Network_1.inp')
        tankIndex = d.getNodeTankIndex()
        d.setNodeTankMaximumWaterLevel(tankIndex, 30)          
        np.testing.assert_array_almost_equal(d.getNodeTankMaximumWaterLevel(), np.array([30., 30.]), err_msg=err_msg)
        
    def testsetNodeTankMinimumWaterLevel(self):
        err_msg = 'Error setting Node Tank Min Water Level'
        d=epanet('BWSN_Network_1.inp')
        tankIndex = d.getNodeTankIndex()
        d.setNodeTankMinimumWaterLevel(tankIndex, [5, 15])      
        d.getNodeTankMinimumWaterLevel(), 
        np.testing.assert_array_almost_equal(d.getNodeTankMinimumWaterLevel(), np.array([ 5., 15.]), err_msg=err_msg) 
        
    def testsetNodeTankMinimumWaterVolume(self):
        err_msg = 'Error setting Node Tank Min Water Volume'
        d=epanet('BWSN_Network_1.inp')
        d.setNodeTankMinimumWaterVolume([1500, 2000])              
        np.testing.assert_array_almost_equal(d.getNodeTankMinimumWaterVolume(), np.array([ 1500, 2000]), err_msg=err_msg) 
        
    def testsetNodeTankMixingFraction(self):
        err_msg = 'Error setting Node Tank Min Water Volume'
        d=epanet('BWSN_Network_1.inp')
        tankIndex = d.getNodeTankIndex()
        d.setNodeTankMixingFraction(tankIndex, [1, 0])    
        np.testing.assert_array_almost_equal(d.getNodeTankMixingFraction(), np.array([1, 0]), err_msg=err_msg) 
        
    def testgetNodeTankMixingModelType(self):
        err_msg = 'Error setting Node Tank Mixing Model Type'
        d=epanet('BWSN_Network_1.inp') 
        tankIndex = d.getNodeTankIndex()
        d.setNodeTankMixingModelType(tankIndex, ['MIX2', 'LIFO'])     
        self.assertEqual(d.getNodeTankMixingModelType(),  ['MIX2', 'LIFO'], err_msg)  
        
    def testsetNodeType(self):
        
        ''' ---setNodeTypeJunction---    '''
        index = self.epanetClass.setNodeTypeJunction('2')
        self.assertEqual(self.epanetClass.getNodeType(index), 'JUNCTION', 'Error setting node type to junction')
        
        ''' ---setNodeTypeReservoir---    '''
        index = self.epanetClass.setNodeTypeReservoir('13')
        self.assertEqual(self.epanetClass.getNodeType(index), 'RESERVOIR', 'Error setting node type to junction')
    
        ''' ---setNodeTypeTank---    '''
        self.epanetClass.unload()
        self.epanetClass = epanet('Net1.inp')
        index = self.epanetClass.setNodeTypeTank('13')
        self.assertEqual(self.epanetClass.getNodeType(index), 'TANK', 'Error setting node type to junction')
     
    def testsetoptions(self):
        err_msg = 'Error setting Options'
        self.epanetClass.setOptionsAccuracyValue(0.001)
        self.assertEqual(self.epanetClass.getOptionsAccuracyValue(), 0.001, err_msg)
        self.epanetClass.setOptionsCheckFrequency(2)
        self.assertEqual(self.epanetClass.getOptionsCheckFrequency(), 2, err_msg)
        self.epanetClass.setOptionsDampLimit(0)
        self.assertEqual(self.epanetClass.getOptionsDampLimit(), 0, err_msg)
        self.epanetClass.setOptionsDemandCharge(0)
        self.assertEqual(self.epanetClass.getOptionsDemandCharge(), 0, err_msg)
        self.epanetClass.setOptionsEmitterExponent(0.5)
        self.assertEqual(self.epanetClass.getOptionsEmitterExponent(), 0.5, err_msg)
        self.epanetClass.setOptionsExtraTrials(10)
        self.assertEqual(self.epanetClass.getOptionsExtraTrials(), 10, err_msg)
        self.epanetClass.setOptionsFlowChange(0)
        self.assertEqual(self.epanetClass.getOptionsFlowChange(), 0, err_msg)
        self.epanetClass.setOptionsGlobalEffic(75)
        self.assertEqual(self.epanetClass.getOptionsGlobalEffic(), 75, err_msg)
        self.epanetClass.setOptionsGlobalPrice(0)
        self.assertEqual(self.epanetClass.getOptionsGlobalPrice(), 0, err_msg)
        self.epanetClass.setOptionsGlobalPattern(1)
        self.assertEqual(self.epanetClass.getOptionsGlobalPattern(), 1, err_msg)
        self.epanetClass.setOptionsHeadError(0)
        self.assertEqual(self.epanetClass.getOptionsHeadError(), 0, err_msg)
        self.epanetClass.setOptionsHeadLossFormula('HW')  
        self.assertEqual(self.epanetClass.getOptionsHeadLossFormula(), 'HW' , err_msg) 
        self.epanetClass.setOptionsLimitingConcentration(0)
        self.assertEqual(self.epanetClass.getOptionsLimitingConcentration(), 0, err_msg)
        self.epanetClass.setOptionsMaximumCheck(10)
        self.assertEqual(self.epanetClass.getOptionsMaximumCheck(), 10, err_msg)
        self.epanetClass.setOptionsMaxTrials(40)
        self.assertEqual(self.epanetClass.getOptionsMaxTrials(), 40, err_msg)
        self.epanetClass.setOptionsPatternDemandMultiplier(1)
        self.assertEqual(self.epanetClass.getOptionsPatternDemandMultiplier(), 1, err_msg)
        self.epanetClass.setOptionsPipeBulkReactionOrder(1)
        self.assertEqual(self.epanetClass.getOptionsPipeBulkReactionOrder(), 1, err_msg)
        self.epanetClass.setOptionsPipeWallReactionOrder(1)
        self.assertEqual(self.epanetClass.getOptionsPipeWallReactionOrder(), 1, err_msg)
        self.epanetClass.setOptionsQualityTolerance(0.01)
        self.assertEqual(self.epanetClass.getOptionsQualityTolerance(), 0.01, err_msg)
        self.epanetClass.setOptionsSpecificDiffusivity(1)
        self.assertEqual(self.epanetClass.getOptionsSpecificDiffusivity(), 1, err_msg)
        self.epanetClass.setOptionsSpecificGravity(1)
        self.assertEqual(self.epanetClass.getOptionsSpecificGravity(), 1, err_msg)
        self.epanetClass.setOptionsSpecificViscosity(1)
        self.assertEqual(self.epanetClass.getOptionsSpecificViscosity(), 1, err_msg)
        self.epanetClass.setOptionsTankBulkReactionOrder(1)
        self.assertEqual(self.epanetClass.getOptionsTankBulkReactionOrder(), 1, err_msg)
        
    def testsetQualityType(self):
        err_msg = 'Error setting Quality type'
        
        # Test 1
        self.epanetClass.setQualityType('none')                         
        self.assertEqual(self.epanetClass.getQualityInfo().QualityType, 'NONE', err_msg)                     

        # Test 2
        self.epanetClass.setQualityType('age')                         
        self.assertEqual(self.epanetClass.getQualityInfo().QualityType, 'AGE', err_msg)                     

        # # Test 3
        self.epanetClass.setQualityType('chem', 'Chlorine')             
        self.assertEqual(self.epanetClass.getQualityInfo().QualityType, 'CHEM', err_msg)   
        self.assertEqual(self.epanetClass.getQualityInfo().QualityChemName, 'Chlorine', err_msg)   
        self.epanetClass.setQualityType('chem', 'Chlorine', 'mg/Kg')    
        self.assertEqual(self.epanetClass.getQualityInfo().QualityChemUnits, 'mg/Kg', err_msg)   

        # Test 4
        nodeID = self.epanetClass.getNodeNameID(1)
        self.epanetClass.setQualityType('trace', nodeID)                
        self.assertEqual(self.epanetClass.getQualityInfo().TraceNode, 1, err_msg)
        
    def testsetPattern(self):
        
        ''' ---setPattern---    '''
        err_msg = 'Error setting new pattern'
        patternID = 'new_pattern'
        patternIndex = self.epanetClass.addPattern(patternID)    
        patternMult = [1.56, 1.36, 1.17, 1.13, 1.08,
            1.04, 1.2, 0.64, 1.08, 0.53, 0.29, 0.9, 1.11,
            1.06, 1.00, 1.65, 0.55, 0.74, 0.64, 0.46,
            0.58, 0.64, 0.71, 0.66]
        self.epanetClass.setPattern(patternIndex, patternMult)    
        np.testing.assert_array_almost_equal(self.epanetClass.getPattern()[1], patternMult, err_msg=err_msg)     

        ''' ---setPatternComment---    '''
        err_msg = 'Error setting pattern comment'
        d = epanet('BWSN_Network_1.inp')
        patternComment = ['1st PAT', '2nd PAT', '3rd PAT', "4rth PAT"]
        d.setPatternComment(patternComment)                                                                         
        self.assertEqual(d.getPatternComment(), patternComment, err_msg)
        
        ''' ---setPatternMatrix---    '''
        err_msg = 'Error setting pattern Matrix'
        self.epanetClass.unload()
        self.epanetClass = epanet('Net1.inp')
        patternID_1 = 'new_pattern_1'
        patternIndex_1 = self.epanetClass.addPattern(patternID_1)    
        patternID_2 = 'new_pattern_2'
        patternIndex_2 = self.epanetClass.addPattern(patternID_2)    
        patternMult = self.epanetClass.getPattern()
        patternMult[patternIndex_1-1, 1] = 5            
        patternMult[patternIndex_2-1, 2] = 7            
        self.epanetClass.setPatternMatrix(patternMult)   
        desired = np.array([[1. , 1.2, 1.4, 1.6, 1.4, 1.2, 1. , 0.8, 0.6, 0.4, 0.6, 0.8],
                            [1. , 5. , 1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. ],
                            [1. , 1. , 7. , 1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. ]])            
        np.testing.assert_array_almost_equal(self.epanetClass.getPattern(), desired, err_msg=err_msg)
        
        
        ''' ---setPatternNameID---    '''
        err_msg = 'Error setting pattern ID'
        # Test 1
        self.epanetClass.setPatternNameID(1, 'Pattern1')                      
        self.assertEqual(self.epanetClass.getPatternNameID(1), 'Pattern1', err_msg) 

        # Test 2
        self.epanetClass.setPatternNameID([1, 2], ['Pattern1', 'Pattern2'])   
        self.assertEqual(self.epanetClass.getPatternNameID([1,2]), ['Pattern1', 'Pattern2'], err_msg)
        
        ''' ---setPatternValue---    '''
        err_msg = 'Error setting pattern Value'
        self.epanetClass.unload()
        self.epanetClass = epanet('Net1.inp')
        patternID = 'new_pattern'
        patternIndex = self.epanetClass.addPattern(patternID)                          
        patternTimeStep = 2
        patternFactor = 5
        self.epanetClass.setPatternValue(patternIndex, patternTimeStep, patternFactor) 
        self.assertEqual(self.epanetClass.getPattern()[1][patternTimeStep-1], patternFactor, err_msg)
        
    def testsetRule(self):
        d=epanet('BWSN_Network_1.inp')
        
        ''' ---setRulePremise---    '''
        err_msg = 'Error setting rule premise'
        # Test 1
        ruleIndex = 1
        premiseIndex = 1
        premise = 'IF SYSTEM CLOCKTIME >= 8 PM'
        d.setRulePremise(ruleIndex, premiseIndex, premise)   
        self.assertEqual(d.getRules()[1]['Premises'][0], 'IF SYSTEM CLOCKTIME >= 08:00 PM UTC', err_msg)

        # Test 2
        ruleIndex = 1
        premiseIndex = 1
        premise = 'IF NODE TANK-131 LEVEL > 20'
        d.setRulePremise(ruleIndex, premiseIndex, premise)                       
        self.assertEqual(d.getRules()[1]['Premises'][0], 'IF NODE TANK-131 LEVEL > 20.0', err_msg)

        ''' ---setRulePremiseObjectNameID---    '''
        err_msg = 'Error setting rule premise object ID'
        ruleIndex = 1
        premiseIndex = 1
        objNameID = 'TANK-131'
        d.setRulePremiseObjectNameID(ruleIndex, premiseIndex, objNameID)
        self.assertEqual(d.getRules()[1]['Premises'][0], 'IF NODE TANK-131 LEVEL > 20.0', err_msg)

        ''' ---setRulePremiseValue---    '''
        err_msg = 'Error setting rule premise value'
        ruleIndex = 1
        premiseIndex = 1
        value = 21
        d.setRulePremiseValue(ruleIndex, premiseIndex, value)
        self.assertEqual(d.getRules()[1]['Premises'][0], 'IF NODE TANK-131 LEVEL > 21.0', err_msg)
        
        ''' ---setRules---    '''
        err_msg = 'Error setting rules'
        rule = 'RULE RULE-1 \n IF NODE 2 LEVEL >= 140 \n THEN PIPE 10 STATUS IS CLOSED \n ELSE PIPE 10 STATUS IS OPEN \n PRIORITY 1'
        self.epanetClass.addRules(rule)              
        ruleIndex = 1
        rule_new = 'IF NODE 2 LEVEL > 150 \n THEN PIPE 10 STATUS IS OPEN \n ELSE PIPE 11 STATUS IS OPEN \n PRIORITY 2'
        self.epanetClass.setRules(ruleIndex, rule_new) 
        desired_rule =['RULE RULE-1', ['IF NODE 2 LEVEL > 150.0'], ['THEN PIPE 10 STATUS IS OPEN'], ['ELSE PIPE 11 STATUS IS OPEN'], 'PRIORITY 2.0']  
        self.assertEqual(self.epanetClass.getRules()[1]['Rule'], desired_rule, err_msg)
        
        ''' ---setRuleElseAction---    '''
        err_msg = 'Error setting rule else action'
        self.epanetClass.addRules("RULE RULE-1 \n IF TANK 2 LEVEL >= 140 \n THEN PIPE 10 STATUS IS CLOSED \n ELSE PIPE 10 STATUS IS OPEN \n PRIORITY 1")   # Adds a new rule - based control
        rule = self.epanetClass.getRules(1)   
        ruleIndex = 1
        actionIndex = 1
        else_action = 'ELSE PIPE 11 STATUS IS CLOSED'
        self.epanetClass.setRuleElseAction(ruleIndex, actionIndex, else_action)   
        self.assertEqual(self.epanetClass.getRules()[1]['Else_Actions'][0], else_action, err_msg)
        
        ''' ---setRulePremiseStatus---    '''
        err_msg = 'Error setting rule premise status'
        self.epanetClass.unload()
        self.epanetClass = epanet('Net1.inp')
        self.epanetClass.addRules('RULE RULE-1 \n IF LINK 110 STATUS = CLOSED \n THEN PUMP 9 STATUS IS CLOSED \n PRIORITY 1')
        self.epanetClass.getRules(1)
        ruleIndex = 1
        premiseIndex = 1
        status = 'OPEN'
        self.epanetClass.setRulePremiseStatus(ruleIndex, premiseIndex, status)   
        self.assertEqual(self.epanetClass.getRules()[1]['Premises'][0], 'IF LINK 110 STATUS = OPEN', err_msg)
        
        ''' ---setRulePriority---    '''
        self.epanetClass.unload()
        self.epanetClass = epanet('Net1.inp')
        err_msg = 'Error setting rule priority'
        ruleIndex = 1
        priority = 2
        d.setRulePriority(ruleIndex, priority)  
        self.assertEqual(d.getRules()[1]['Rule'][4], 'PRIORITY 2.0', err_msg)

        ''' ---setRuleThenAction---    '''
        err_msg = 'Error setting rule priority action'
        self.epanetClass.addRules('RULE RULE-1 \n IF TANK 2 LEVEL >= 140 \n THEN PIPE 10 STATUS IS CLOSED \n ELSE PIPE 10 STATUS IS OPEN \n PRIORITY 1')   # Adds a new rule - based control
        rule = self.epanetClass.getRules(1)  
        ruleIndex = 1
        actionIndex = 1
        then_action = 'THEN PIPE 11 STATUS IS OPEN'
        self.epanetClass.setRuleThenAction(ruleIndex, actionIndex, then_action)
        self.assertEqual(self.epanetClass.getRules()[1]['Then_Actions'], ['THEN PIPE 11 STATUS IS OPEN'], err_msg)

    def testsetTime(self):
        err_msg = 'Error setting time'
        Hstep = 1800
        self.epanetClass.setTimeHydraulicStep(Hstep)
        self.assertEqual(self.epanetClass.getTimeHydraulicStep(), Hstep, err_msg) 
        patternStart = 0
        self.epanetClass.setTimePatternStart(patternStart)
        self.assertEqual(self.epanetClass.getTimePatternStart(), patternStart, err_msg)
        patternStep = 3600
        self.epanetClass.setTimePatternStep(patternStep)
        self.assertEqual(self.epanetClass.getTimePatternStep(), patternStep, err_msg)
        Qstep = 1800
        self.epanetClass.setTimeQualityStep(Qstep)
        self.assertEqual(self.epanetClass.getTimeQualityStep(), Qstep, err_msg)
        reportingStart = 0
        self.epanetClass.setTimeReportingStart(reportingStart)
        self.assertEqual(self.epanetClass.getTimeReportingStart(), reportingStart, err_msg)
        reportingStep = 3600
        self.epanetClass.setTimeReportingStep(reportingStep)
        self.assertEqual(self.epanetClass.getTimeReportingStep(), reportingStep, err_msg)
        ruleControlStep = 360
        self.epanetClass.setTimeRuleControlStep(ruleControlStep)
        self.assertEqual(self.epanetClass.getTimeRuleControlStep(), ruleControlStep, err_msg)
        simulationDuration = 172800    
        self.epanetClass.setTimeSimulationDuration(simulationDuration)
        self.assertEqual(self.epanetClass.getTimeSimulationDuration(), simulationDuration, err_msg)
        statisticsType = 'AVERAGE'
        self.epanetClass.setTimeStatisticsType(statisticsType)
        self.assertEqual(self.epanetClass.getTimeStatisticsType(), statisticsType, err_msg)
        
class AddTest(unittest.TestCase):

    def testStepByStepHydraulic(self):
        d = epanet('Net1.inp')
        d.openHydraulicAnalysis()
        d.initializeHydraulicAnalysis()
        tstep,P , T_H, D, H, F, S, = 1, [], [], [], [] ,[], []
        while (tstep>0):
             t = d.runHydraulicAnalysis()
             P.append(d.getNodePressure())
             D.append(d.getNodeActualDemand())
             H.append(d.getNodeHydraulicHead())
             S.append(d.getLinkStatus())
             F.append(d.getLinkFlows())
             T_H.append(t)
             tstep = d.nextHydraulicAnalysisStep()
        d.closeHydraulicAnalysis()

        # Test Pressure
        err_msg = 'Error in Pressure Output'
        desired_p_1 = np.array([128.58963612, 120.45028753, 118.34940585, 119.99139321,
                                118.94074548, 120.07340709, 122.05444889, 117.14855347,
                                112.0894993 ,   0.        ,  53.32542596])
        np.testing.assert_array_almost_equal(P[1], desired_p_1, err_msg=err_msg) 
        
        desired_p_10 = np.array([132.26981375, 124.63753647, 123.45427607, 124.71035299,
                                123.03261446, 124.59180141, 126.55864067, 120.71122109,
                                115.61661061,   0.        ,  58.44725465])
        np.testing.assert_array_almost_equal(P[10], desired_p_10, err_msg=err_msg) 
    
        
        desired_p_25 = np.array([124.92020828, 116.27777211, 113.2647933 , 115.18812071,
                                114.76197096, 115.35222877, 117.34954606, 113.36596566,
                                108.22952342,   0.        ,  48.2175138 ])
        np.testing.assert_array_almost_equal(P[25], desired_p_25, err_msg=err_msg) 

        # Test Actual Demand
        err_msg = 'Error in Actual Demand'
        desired_act_dem_0 = np.array([    0.       ,   150.        ,   150.        ,   100.        ,
                                       150.        ,   200.        ,   150.        ,   100.        ,
                                       100.        , -1866.17582999,   766.17582999]) 
        np.testing.assert_array_almost_equal(D[0], desired_act_dem_0, err_msg=err_msg) 
        
        desired_act_dem_11 = np.array([    0.        ,   180.        ,   180.        ,   120.        ,
                                         180.        ,   240.        ,   180.        ,   120.        ,
                                         120.        , -1774.30359304,   454.30359304]) 
        np.testing.assert_array_almost_equal(D[11], desired_act_dem_11, err_msg=err_msg) 
        
        desired_act_dem_17 = np.array([   0.       ,   90.       ,   90.       ,   60.       ,
                                         90.       ,  120.       ,   90.       ,   60.       ,
                                         60.       ,    0.       , -660.0007914]) 
        np.testing.assert_array_almost_equal(D[17], desired_act_dem_17, err_msg=err_msg) 

        # Test Hydraulic Head
        err_msg = 'Error in Node Hydraulic Head'
        desired_head_3 = np.array([1009.9247677 ,  991.57444459,  978.17030221,  976.10781146,
                                   977.43523692,  975.88868908,  975.41587013,  972.04529101,
                                   970.24584336,  800.        ,  978.13799323])
        np.testing.assert_array_almost_equal(H[3], desired_head_3, err_msg=err_msg) 
        
        desired_head_14 = np.array([986.31467071, 986.31467071, 987.84955266, 985.4428713 ,
                                    983.41923666, 983.80636726, 983.68229481, 979.90330538,
                                    979.01824775, 800.        , 987.98597249])
        np.testing.assert_array_almost_equal(H[14], desired_head_14, err_msg=err_msg) 
        
        desired_head_25 = np.array([998.29958062, 978.35396286, 961.40039995, 960.83918927,
                                    964.85569112, 961.21792931, 960.82747764, 961.63389259,
                                    959.77965248, 800.        , 961.27974566])
        np.testing.assert_array_almost_equal(H[25], desired_head_25, err_msg=err_msg) 

        # Test Link Status
        err_msg = 'Error in Link Status'
        desired_status_0 = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        np.testing.assert_array_almost_equal(S[0], desired_status_0, err_msg=err_msg) 
        
        desired_status_15 = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0])
        np.testing.assert_array_almost_equal(S[15], desired_status_15, err_msg=err_msg) 
        
        desired_status_26 = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        np.testing.assert_array_almost_equal(S[26], desired_status_26, err_msg=err_msg) 

        # Test Link Flow
        err_msg = 'Error in Link Flow'
        desired_flow_1 = np.array([1825.38318977, 1154.81751895,  173.49038595,  148.51329828,
                                    126.50961405,   42.05237255, -505.38318977,  490.56567082,
                                    295.94394323,   53.49038595,  162.05237255,   77.94762745,
                                   1825.38318977])
        np.testing.assert_array_almost_equal(F[3], desired_flow_1, err_msg=err_msg) 
        
        desired_flow_14 = np.array([-8.38100537e-04, -3.58364870e+02,  1.88567513e+02, -7.03036975e+01,
                                     6.14324871e+01,  2.86677280e+01,  1.10000084e+03,  2.08364031e+02,
                                     4.03068457e+02,  8.85675129e+01,  1.28667728e+02,  7.13322720e+01,
                                    0.00000000e+00])
        np.testing.assert_array_almost_equal(F[14], desired_flow_14, err_msg=err_msg) 
        
        desired_flow_25 = np.array([ 1909.42463758,  1310.99431794,    85.91245886,   235.69131652,
                                      114.08754114,    42.73900313, -1029.42463758,   478.43031965,
                                       75.6572215 ,     5.91245886,   122.73900313,    37.26099687,
                                     1909.42463758])
        np.testing.assert_array_almost_equal(F[25], desired_flow_25, err_msg=err_msg) 


    def testStepByStepHydraulicQuality(self):
        d = epanet('Net2.inp')
        d.openHydraulicAnalysis()
        d.openQualityAnalysis()
        d.initializeHydraulicAnalysis(0)
        d.initializeQualityAnalysis(d.ToolkitConstants.EN_NOSAVE)
        tstep, P, T, F, QN, QL = 1, [], [], [], [], []
        # Extra dynamic variables
        Vel, HLoss, LSett, LEnrg, NDemSensN, MFR_, NActQual = [], [], [], [], [], [], []  
        while (tstep>0):
            t  = d.runHydraulicAnalysis()
            qt = d.runQualityAnalysis()
            P.append(d.getNodePressure())
            F.append(d.getLinkFlows())
            QN.append(d.getNodeActualQuality())
            QL.append(d.getLinkActualQuality())
            T.append(t)

            # Extra variables
            Vel.append(d.getLinkVelocity())
            HLoss.append(d.getLinkHeadloss())
            LSett.append(d.getLinkSettings())
            LEnrg.append(d.getLinkEnergy())
            NDemSensN.append(d.getNodeActualDemandSensingNodes())
            NActQual.append(d.getNodeActualQualitySensingNodes())
            MFR_.append(d.getNodeMassFlowRate())

            tstep = d.nextHydraulicAnalysisStep()
            qtstep = d.nextQualityAnalysisStep()
        d.closeQualityAnalysis()
        d.closeHydraulicAnalysis()

        # Test Pressure
        err_msg = 'Error in Pressure Output'
        desired_p_1 = np.array([113.44908691,  89.7622058 , 106.82691104, 106.6386474 ,
                                89.28836137,  77.5531041 ,  60.3874831 ,  82.05202764,
                                51.44147544,  73.38562132,  48.80664238,  36.8438231 ,
                                36.50653553,  40.6814559 ,  44.92037458,  62.27779634,
                                49.254625  ,  83.91787864,  62.25761494,  53.6728296 ,
                                62.33170387,  40.66680277,  27.32765269,  44.84070793,
                                27.24073401,  70.56470052,  79.22932155,  79.22939519,
                                70.56301264,  44.57029235,  79.58488909,  49.33250858,
                                44.99947598,  79.22930683,  79.22931001,  25.02817602])
        np.testing.assert_array_almost_equal(P[1], desired_p_1, err_msg=err_msg) 
        
        desired_p_10 = np.array([104.60396813,  82.93896813, 100.26187843, 100.27019131,
                                82.94214413,  72.13623112,  57.0459412 ,  78.70869778,
                                48.40123335,  70.04069639,  46.28936448,  35.75714786,
                                35.87914808,  40.33564453,  44.8229384 ,  61.72428425,
                                48.72501201,  83.37653805,  61.71117649,  53.29707981,
                                61.92798077,  40.2634679 ,  28.20018035,  45.02049294,
                                28.47009352,  71.7703745 ,  80.42958211,  80.42994484,
                                71.76206051,  45.79006666,  79.04235247,  48.9280188 ,
                                44.59485824,  80.42950961,  80.42952527,  26.5365387 ])
        np.testing.assert_array_almost_equal(P[10], desired_p_10, err_msg=err_msg) 
    
        
        desired_p_25 = np.array([112.30635933,  88.7727249 , 105.85553093, 105.68501784,
                                88.33680483,  76.68003911,  59.6914576 ,  81.35595229,
                                50.77187475,  72.68950149,  48.18348723,  36.34741436,
                                36.0501462 ,  40.24410062,  44.49704926,  61.84748716,
                                48.82889842,  83.49175121,  61.83044521,  53.2346395 ,
                                61.89273376,  40.22784348,  26.95657095,  44.43288199,
                                26.88784804,  70.2111541 ,  78.87562417,  78.87570587,
                                70.20928145,  44.2171391 ,  79.15874975,  48.89351709,
                                44.56048092,  78.87560784,  78.87561137,  24.6866985 ])
        np.testing.assert_array_almost_equal(P[25], desired_p_25, err_msg=err_msg)

        # Test Link Flow
        err_msg = 'Error in Link Flow'
        desired_flow_1 = np.array([666.624     , 552.03844658, 106.82555342,  93.24555342,
                                    85.48555342, 629.764     , 624.914     ,  13.58      ,
                                    607.454     ,   4.85      , 593.874     , 560.1374    ,
                                    544.6174    , 450.95264986, 402.45264986,  91.72475014,
                                    -12.18475015,  46.13203755,  14.54728741,  -4.85271259,
                                    26.19271259,  46.56      ,  14.11807025,  -1.40192975,
                                    14.01192975, 402.0274    , 412.6974    , 394.2674    ,
                                    353.5274    ,  34.92      ,  18.43      ,  10.67      ,
                                    1.67010192,   2.91      ,   1.455     , -21.34271259,
                                    2.20989809,   2.91      ,   0.70010191,   0.97      ])
        np.testing.assert_array_almost_equal(F[3], desired_flow_1, err_msg=err_msg) 
        
        desired_flow_14 = np.array([694.4       , 569.73469929, 113.22530071,  93.20530071,
                                    81.76530071, 640.06      , 632.91      ,  20.02      ,
                                    607.17      ,   7.15      , 587.15      , 537.4146    ,
                                    514.5346    , 421.13156631, 349.63156631,  90.54303369,
                                    26.71696631,  38.15675345,  36.27371976,   7.67371976,
                                    23.78628024,  68.64      ,  20.81323758,  -2.06676242,
                                    20.65676242, 304.3246    , 320.0546    , 292.8846    ,
                                    232.8246    ,  51.48      ,  27.17      ,  15.73      ,
                                    2.46210901,   4.29      ,   2.145     , -16.63628024,
                                    3.25789099,   4.29      ,   1.03210901,   1.43      ])
        np.testing.assert_array_almost_equal(F[14], desired_flow_14, err_msg=err_msg) 
        
        desired_flow_25 = np.array([638.848     , 526.87340214, 103.17459786,  87.77459786,
                                    78.97459786, 597.048     , 591.548     ,  15.4       ,
                                    571.748     ,   5.5       , 556.348     , 518.09      ,
                                    500.49      , 413.32924235, 358.32924235,  84.96075765,
                                    5.23924235,  39.67255841,  22.91180076,   0.91180076,
                                    23.28819924,  52.8       ,  16.01018276,  -1.58981724,
                                    15.88981725, 338.79      , 350.89      , 329.99      ,
                                    283.79      ,  39.6       ,  20.9       ,  12.1       ,
                                    1.89393001,   3.3       ,   1.65      , -17.78819924,
                                    2.50606999,   3.3       ,   0.79393001,   1.1       ])
        np.testing.assert_array_almost_equal(F[25], desired_flow_25, err_msg=err_msg)

        # Test Node Actual Quality 
        err_msg = 'Error in Node Actual Quality '
        desired_actual_qual_n_5 = np.array([0.64      , 0.64      , 0.67048332, 0.99039853, 0.69538444,
                                        0.69538444, 0.99479975, 0.9999543 , 0.99480261, 0.99998255,
                                        0.99485289, 0.99521299, 0.99531586, 0.99634925, 0.99711982,
                                        1.03729065, 1.03153143, 0.99968388, 0.98557096, 0.98550671,
                                        0.99965067, 0.99961999, 1.0319837 , 1.0083734 , 1.0326732 ,
                                        0.99234298, 0.99985533, 0.99699218, 0.99998949, 1.01354119,
                                        0.99904712, 0.99995205, 0.99999525, 0.9998032 , 0.9999915 ,
                                        1.00073598])
        np.testing.assert_array_almost_equal(QN[5], desired_actual_qual_n_5, err_msg=err_msg) 
        
        desired_actual_qual_n_25 = np.array([0.15      , 0.15      , 0.13021117, 0.13025352, 0.14729473,
                                        0.1471587 , 0.13169433, 0.13385677, 0.1317173 , 0.52638193,
                                        0.13180541, 0.9263402 , 0.92638118, 0.92645536, 0.92655419,
                                        0.92691066, 0.92710259, 0.90358968, 0.13692333, 0.92710674,
                                        0.93375845, 0.92718604, 0.92684628, 0.92664191, 0.92693835,
                                        0.92718994, 1.01683607, 0.92719291, 0.99951648, 0.92716929,
                                        0.19758304, 1.03599597, 0.99983082, 1.00030477, 0.99949038,
                                        0.92719247])
        np.testing.assert_array_almost_equal(QN[25], desired_actual_qual_n_25, err_msg=err_msg) 
        
        desired_actual_qual_n_50 = np.array([0.08      , 0.08134169, 0.08465141, 0.08746161, 0.08277441,
                                        0.08400952, 0.08591221, 0.08695709, 0.08618052, 0.0901129 ,
                                        0.0866383 , 0.24426994, 0.76375642, 0.76375658, 0.76375697,
                                        0.76375918, 0.76376117, 0.7433078 , 0.07708495, 0.76376101,
                                        0.78462961, 0.76376286, 0.76375982, 0.76375766, 0.76376087,
                                        0.763763  , 0.13845722, 0.76376313, 0.94441596, 0.76376264,
                                        0.4377526 , 0.0909339 , 0.14413847, 0.87968838, 0.41099686,
                                        0.76376316])
        np.testing.assert_array_almost_equal(QN[50], desired_actual_qual_n_50, err_msg=err_msg)

        # Test Link Actual Quality 
        err_msg = 'Error in Link Actual Quality '
        desired_actual_qual_l_5 = np.array([0.64      , 0.64      , 0.64      , 0.91723447, 1.01971497,
                                            0.69538444, 0.76623242, 1.00396346, 0.99480261, 0.99998255,
                                            0.99485289, 0.99521299, 0.99531586, 0.99634925, 0.99700032,
                                            1.02051568, 1.00264694, 1.03733108, 0.99971906, 0.99980064,
                                            1.01236519, 1.02101503, 0.99692542, 0.99998129, 0.9969474 ,
                                            1.0177895 , 0.99711982, 1.0326732 , 1.03327514, 1.02508339,
                                            0.99405897, 0.99699218, 0.99985533, 0.99995205, 0.99999525,
                                            0.99673462, 0.99974172, 0.99998949, 0.99999727, 0.9999915 ])
        np.testing.assert_array_almost_equal(QL[5], desired_actual_qual_l_5, err_msg=err_msg) 
        
        desired_actual_qual_l_25 = np.array([0.15      , 0.14982569, 0.14433033, 0.13025352, 0.13072138,
                                            0.1471587 , 0.13343018, 0.35084865, 0.1317173 , 0.57100102,
                                            0.13180541, 0.35477286, 0.92638118, 0.92645536, 0.9265464 ,
                                            0.92691066, 0.90087915, 0.92710259, 0.80950048, 0.87595265,
                                            0.71679381, 0.92710674, 0.92718601, 0.90544275, 0.92718604,
                                            0.92684628, 0.92664191, 0.92693835, 0.92699844, 0.92716929,
                                            0.92718994, 0.92719291, 0.8686534 , 0.74306268, 1.00226608,
                                            0.1455949 , 0.75839028, 0.99895694, 0.9997757 , 0.99955681])
        np.testing.assert_array_almost_equal(QL[25], desired_actual_qual_l_25, err_msg=err_msg) 
        
        desired_actual_qual_l_50 = np.array([0.08134169, 0.08216745, 0.08465141, 0.08746161, 0.08619748,
                                            0.08400952, 0.08591221, 0.24455678, 0.08618052, 0.23554602,
                                            0.0866383 , 0.08902147, 0.49475266, 0.76375658, 0.76375697,
                                            0.76375918, 0.76376131, 0.76376094, 0.63110369, 0.74330737,
                                            0.57669299, 0.76376101, 0.76376286, 0.6108296 , 0.76376286,
                                            0.76375982, 0.76375766, 0.76376087, 0.76376181, 0.76376264,
                                            0.763763  , 0.76376313, 0.60610794, 0.4847193 , 0.61113019,
                                            0.07690258, 0.61324601, 0.70567315, 0.88758939, 0.66363372])
        np.testing.assert_array_almost_equal(QL[50], desired_actual_qual_l_50, err_msg=err_msg) 

        # Test Link Velocity 
        err_msg = 'Error in Link Velocity '
        desired_vel_5 = np.array([1.89107267, 1.55810047, 0.6884234 , 0.58208631, 0.23169878,
                                    1.762793  , 1.7459141 , 0.04726093, 1.68515004, 0.03797753,
                                    1.63788911, 1.52047946, 1.46646697, 1.20995089, 1.04116185,
                                    0.56197017, 0.06086138, 0.25743011, 0.07394727, 0.00643166,
                                    0.15262992, 0.16203748, 0.11055041, 0.0109777 , 0.10971929,
                                    0.97022719, 1.00736078, 0.94322095, 0.80143815, 0.12152811,
                                    0.14431463, 0.08355057, 0.0130776 , 0.02278652, 0.01139326,
                                    0.11465239, 0.01730443, 0.02278652, 0.00548209, 0.00759551])
        np.testing.assert_array_almost_equal(Vel[5], desired_vel_5, err_msg=err_msg) 
        
        desired_vel_25 = np.array([1.81227798, 1.49462949, 0.65854063, 0.56024584, 0.22403439,
                                    1.69370013, 1.67809778, 0.04368657, 1.62192933, 0.03510528,
                                    1.57824276, 1.46971282, 1.41978531, 1.17252849, 1.01650501,
                                    0.54228572, 0.03344092, 0.25322116, 0.06499598, 0.00258659,
                                    0.14864342, 0.14978254, 0.10218945, 0.01014745, 0.10142119,
                                    0.96107627, 0.99540144, 0.93611252, 0.80505279, 0.11233691,
                                    0.13340008, 0.07723162, 0.01208854, 0.02106317, 0.01053158,
                                    0.11353814, 0.01599569, 0.02106317, 0.00506748, 0.00702106])
        np.testing.assert_array_almost_equal(Vel[25], desired_vel_25, err_msg=err_msg) 
        
        desired_vel_50 = np.array([1.81227798, 1.49714577, 0.65645338, 0.56441371, 0.22747538,
                                    1.70124599, 1.68663652, 0.04090652, 1.63404243, 0.03287131,
                                    1.59313591, 1.49151242, 1.44476211, 1.19393116, 1.04783645,
                                    0.55122112, 0.01213162, 0.26601754, 0.0544003 , 0.00403759,
                                    0.15371834, 0.14025093, 0.09568649, 0.0095017 , 0.09496711,
                                    1.01524366, 1.04738449, 0.9918685 , 0.86914894, 0.10518819,
                                    0.12491098, 0.07231688, 0.01131927, 0.01972279, 0.00986139,
                                    0.12084703, 0.01497778, 0.01972279, 0.004745  , 0.00657426])
        np.testing.assert_array_almost_equal(Vel[50], desired_vel_50, err_msg=err_msg) 

        # Test Link Head Loss 
        err_msg = 'Error in Link Head Loss '
        desired_hl_5 = np.array([4.66623842e+00, 1.08659784e+00, 6.24370723e-01, 4.22404407e-01,
                                    3.98227125e-02, 2.04851029e+00, 4.52774736e+00, 1.34903243e-03,
                                    6.28183749e-01, 1.20349695e-03, 1.04290558e+00, 2.46645761e+00,
                                    7.28416180e-01, 3.40124496e-01, 1.93133276e-01, 4.94710105e-01,
                                    8.06274218e-03, 4.66104101e-02, 3.36228028e-03, 1.82545289e-05,
                                    4.13065810e-02, 2.25887710e-02, 2.11060856e-02, 2.92927934e-04,
                                    2.08131577e-02, 3.38947886e-01, 1.51401704e-01, 1.60841236e-01,
                                    7.93029468e-02, 7.23210341e-03, 1.06388168e-02, 3.86634775e-03,
                                    2.18121485e-04, 8.71385305e-04, 9.65523106e-05, 8.68436388e-03,
                                    2.61714521e-04, 8.71385306e-04, 4.35930363e-05, 3.41745593e-05])
        np.testing.assert_array_almost_equal(HLoss[5], desired_hl_5, err_msg=err_msg) 
        
        desired_hl_23 = np.array([0.00000000e+00, 2.12312025e-03, 6.07622722e-03, 5.55697659e-03,
                                    2.64237088e-03, 1.77728998e-02, 5.02764696e-02, 1.49966988e-03,
                                    1.42333585e-02, 1.33788342e-03, 3.65197375e-02, 2.00732742e-01,
                                    8.15543943e-02, 8.25545387e-02, 1.03141866e-01, 1.02185677e-01,
                                    2.88064062e-01, 1.81979589e-04, 8.33854390e-03, 7.92533017e-04,
                                    8.76221936e-03, 2.51111082e-02, 2.34628613e-02, 3.25637240e-04,
                                    2.31372240e-02, 3.42051062e-01, 1.32060597e-01, 1.80430638e-01,
                                    1.55718379e-01, 8.03966410e-03, 1.18267824e-02, 4.29807698e-03,
                                    2.42477654e-04, 9.68687084e-04, 1.07333662e-04, 5.50837145e-04,
                                    2.90938434e-04, 9.68687084e-04, 4.84607797e-05, 3.79906041e-05])
        np.testing.assert_array_almost_equal(HLoss[23], desired_hl_23, err_msg=err_msg) 
        
        desired_hl_51 = np.array([4.31256504e+00, 1.01913328e+00, 5.61048713e-01, 4.16152148e-01,
                                    4.19324206e-02, 1.96783554e+00, 4.37316956e+00, 6.61642927e-04,
                                    6.19212311e-01, 5.90263973e-04, 1.04532883e+00, 2.58657778e+00,
                                    7.81521938e-01, 3.70236769e-01, 2.32843368e-01, 5.02954094e-01,
                                    3.92572822e-02, 6.08687614e-02, 3.74567793e-04, 1.98752685e-04,
                                    4.84029147e-02, 1.10788296e-02, 1.03516357e-02, 1.43668670e-04,
                                    1.02079670e-02, 4.91244998e-01, 2.12841090e-01, 2.38615449e-01,
                                    1.35577363e-01, 3.54703856e-03, 5.21788629e-03, 1.89627882e-03,
                                    1.06979294e-04, 4.27377362e-04, 4.73547942e-05, 1.26416617e-02,
                                    1.28359821e-04, 4.27377362e-04, 2.13805269e-05, 1.67611652e-05])
        np.testing.assert_array_almost_equal(HLoss[51], desired_hl_51, err_msg=err_msg)

        # Test Link Settings 
        err_msg = 'Error in Link Settings'
        desired_sett_0 = np.array([100., 100., 100., 100., 100., 100., 100., 140., 100., 140., 100.,
                                   100., 100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
                                   100., 100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
                                   100., 100., 100., 100., 100., 100., 100.])
        np.testing.assert_array_almost_equal(LSett[0], desired_sett_0, err_msg=err_msg) 

        # Test Link Energy 
        err_msg = 'Error in Link Energy'
        desired_enrg_5 = np.array([5.86348910e-01, 1.12498123e-01, 1.26939451e-02, 7.26129840e-03,
                                    6.13105994e-04, 2.39949829e-01, 5.25274159e-01, 4.23648468e-06,
                                    7.03406297e-02, 1.34980245e-06, 1.13503817e-01, 2.49192629e-01,
                                    7.09794855e-02, 2.73455481e-02, 1.33615343e-02, 8.21036573e-03,
                                    1.44918241e-05, 3.54356768e-04, 1.65210273e-05, 7.80143452e-09,
                                    1.86190444e-04, 2.43214270e-04, 6.89075030e-05, 9.49665191e-08,
                                    6.74402862e-05, 2.18518067e-02, 1.01343706e-02, 1.00807262e-02,
                                    4.22318706e-03, 5.84012767e-05, 4.53421535e-05, 9.54000958e-06,
                                    8.42412685e-08, 5.86390195e-07, 3.24869652e-08, 2.94048909e-05,
                                    1.33746844e-07, 5.86390195e-07, 7.05767837e-09, 7.66581151e-09])
        np.testing.assert_array_almost_equal(LEnrg[5], desired_enrg_5, err_msg=err_msg) 
        
        desired_enrg_23 = np.array([0.00000000e+00, 7.57281174e-06, 1.01274099e-05, 9.21563204e-06,
                                    9.40276051e-06, 1.60406707e-04, 5.13468317e-04, 4.98657667e-06,
                                    2.06213534e-04, 1.58879210e-06, 6.50531961e-04, 5.23384524e-03,
                                    2.43634232e-03, 3.09009534e-03, 5.08555118e-03, 7.23689933e-04,
                                    3.57014313e-03, 6.92653436e-08, 6.69087179e-05, 2.59464445e-06,
                                    1.70978917e-05, 2.86276641e-04, 8.11079405e-05, 1.11780843e-07,
                                    7.93809451e-05, 2.21606514e-02, 8.21086255e-03, 1.20324897e-02,
                                    1.19378331e-02, 6.87415312e-05, 5.33702213e-05, 1.12291187e-05,
                                    9.91566299e-08, 6.90213677e-07, 3.82389540e-08, 4.20717423e-07,
                                    1.57427429e-07, 6.90213677e-07, 8.30727765e-09, 9.02308390e-09])
        np.testing.assert_array_almost_equal(LEnrg[23], desired_enrg_23, err_msg=err_msg) 
        
        desired_enrg_51 = np.array([5.19327654e-01, 1.01923935e-01, 1.07665857e-02, 7.09644859e-03,
                                    6.63834774e-04, 2.25553307e-01, 4.97914128e-01, 1.41431120e-06,
                                    6.87996081e-02, 4.50619054e-07, 1.13910209e-01, 2.68125554e-01,
                                    7.91036229e-02, 3.11617013e-02, 1.78201454e-02, 8.42200819e-03,
                                    1.65862125e-04, 5.34489931e-04, 5.62728564e-07, 3.08332424e-07,
                                    2.37676857e-04, 8.11948329e-05, 2.30041321e-05, 3.17036934e-08,
                                    2.25143153e-05, 3.86967788e-02, 1.71235752e-02, 1.85049621e-02,
                                    9.64479399e-03, 1.94967257e-05, 1.51370583e-05, 3.18484390e-06,
                                    2.81231677e-08, 1.95760939e-07, 1.08454726e-08, 5.24245111e-05,
                                    4.46501460e-08, 1.95760939e-07, 2.35614062e-09, 2.55916022e-09])
        np.testing.assert_array_almost_equal(LEnrg[51], desired_enrg_51, err_msg=err_msg)

        # Test Node Actual Demand Sensing Nodes 
        err_msg = 'Error in Node Actual Demand Sensing Nodes'
        desired_act_dem_sen_2 = np.array([-666.624 ,    7.76  ,   13.58  ,    7.76  ,    7.76  ,    4.85  ,
                                            3.88  ,    8.73  ,   13.58  ,    4.85  ,   33.7366,   15.52  ,
                                            1.94  ,    1.94  ,    1.94  ,   19.4   ,   19.4   ,   19.4   ,
                                            4.85  ,   18.43  ,   15.52  ,    9.7   ,    7.76  ,   10.67  ,
                                            5.82  ,    7.76  ,    0.    ,    6.79  ,    2.91  ,   16.49  ,
                                            16.49  ,    1.455 ,    1.455 ,    0.    ,    0.97  ,  353.5274])
        np.testing.assert_array_almost_equal(NDemSensN[2], desired_act_dem_sen_2, err_msg=err_msg) 
        
        desired_act_dem_sen_20 = np.array([   0.        ,   10.08      ,   17.64      ,   10.08      ,
                                            10.08      ,    6.3       ,    5.04      ,   11.34      ,
                                            17.64      ,    6.3       ,   43.8228    ,   20.16      ,
                                            2.52      ,    2.52      ,    2.52      ,   25.2       ,
                                            25.2       ,   25.2       ,    6.3       ,   23.94      ,
                                            20.16      ,   12.6       ,   10.08      ,   13.86      ,
                                            7.56      ,   10.08      ,    0.        ,    8.82      ,
                                            3.78      ,   21.42      ,   21.42      ,    1.89      ,
                                            1.89      ,    0.        ,    1.26      , -406.70253781])
        np.testing.assert_array_almost_equal(NDemSensN[20], desired_act_dem_sen_20, err_msg=err_msg) 
        
        desired_act_dem_sen_50 = np.array([-638.848     ,    8.24      ,   14.42      ,    8.24      ,
                                            8.24      ,    5.15      ,    4.12      ,    9.27      ,
                                            14.42      ,    5.15      ,   35.8234    ,   16.48      ,
                                            2.06      ,    2.06      ,    2.06      ,   20.6       ,
                                            20.6       ,   20.6       ,    5.15      ,   19.57      ,
                                            16.48      ,   10.3       ,    8.24      ,   11.33      ,
                                            6.18      ,    8.24      ,    0.        ,    7.21      ,
                                            3.09      ,   17.51      ,   17.51      ,    1.545     ,
                                            1.545     ,    0.        ,    1.03      ,  306.38459999])
        np.testing.assert_array_almost_equal(NDemSensN[50], desired_act_dem_sen_50, err_msg=err_msg)

        # Test Node Actual Quality Sensing Nodes 
        err_msg = 'Error in Node Actual Quality Sensing Nodes'
        desired_act_qual_sens_2 = np.array([1.02      , 1.02      , 1.01886289, 0.98075828, 1.01706526,
                                            1.01649625, 0.984237  , 0.9999543 , 0.98423092, 0.99999335,
                                            0.98419022, 0.98407613, 0.98413583, 0.98653162, 0.98921752,
                                            0.99881135, 0.99929102, 0.99993587, 0.99974241, 0.99933008,
                                            0.99993153, 0.99992532, 0.99456018, 0.99121529, 0.99586472,
                                            0.99985462, 0.99999968, 0.99997815, 0.99999999, 0.99939214,
                                            0.99992752, 0.99999825, 0.99999996, 0.99999955, 0.99999999,
                                            0.99997897])
        np.testing.assert_array_almost_equal(NActQual[2], desired_act_qual_sens_2, err_msg=err_msg) 
        
        desired_act_qual_sens_20 = np.array([0.15      , 0.13007754, 0.13002584, 0.1301467 , 0.13063834,
                                            0.13190425, 0.13328394, 0.69315762, 0.13400906, 1.00316403,
                                            0.13481013, 0.91011792, 0.92718207, 0.92719201, 0.92719315,
                                            0.13607246, 0.15150492, 0.88631925, 0.23492208, 0.15904258,
                                            1.00047636, 1.00052995, 0.92719315, 0.92719315, 0.92719315,
                                            0.221263  , 0.99932869, 0.42258208, 0.99951648, 0.92719315,
                                            0.88435288, 0.99986736, 0.99990912, 0.99581539, 0.99956727,
                                            0.92719315])
        np.testing.assert_array_almost_equal(NActQual[20], desired_act_qual_sens_20, err_msg=err_msg) 
        
        desired_act_qual_sens_50 = np.array([0.08      , 0.08134169, 0.08465141, 0.08746161, 0.08277441,
                                            0.08400952, 0.08591221, 0.08695709, 0.08618052, 0.0901129 ,
                                            0.0866383 , 0.24426994, 0.76375642, 0.76375658, 0.76375697,
                                            0.76375918, 0.76376117, 0.7433078 , 0.07708495, 0.76376101,
                                            0.78462961, 0.76376286, 0.76375982, 0.76375766, 0.76376087,
                                            0.763763  , 0.13845722, 0.76376313, 0.94441596, 0.76376264,
                                            0.4377526 , 0.0909339 , 0.14413847, 0.87968838, 0.41099686,
                                            0.76376316])
        np.testing.assert_array_almost_equal(NActQual[50], desired_act_qual_sens_50, err_msg=err_msg)

        # Test Node Mass Flow Rate
        err_msg = 'Error in Node Mass Flow Rate'
        desired_act_dem_MFR__2 = [18168918.949573442, None, None, None, None, None, None, None, None,
                                    None, None, None, None, None, None, None, None, None, None, None,
                                    None, None, None, None, None, None, None, None, None, None, None,
                                    None, None, None, None, None]
        self.assertEqual(list(MFR_[2]), desired_act_dem_MFR__2, err_msg) 
        






if __name__ == "__main__":
    unittest.main()  # run all tests
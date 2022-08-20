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

if __name__ == "__main__":
    unittest.main()  # run all tests
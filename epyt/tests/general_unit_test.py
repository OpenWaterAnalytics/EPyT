from math import isclose
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
        self.epanetClass.addCurve(new_curve_ID, values)
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
        d.unload()

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

    def testdeleteNodeJunctionDemand(self):
        err_msg = 'Demand not deleted'
        # Test 1
        nodeIndex = 1
        baseDemand = 100
        patternId = '1'
        self.epanetClass.addNodeJunctionDemand(nodeIndex, baseDemand, patternId, 'new demand')    # Adds a new demand to the 1st node and returns the new demand index
        self.epanetClass.getNodeJunctionDemandIndex(nodeIndex)                                                    # Retrieves the indices of all demands for the 1st node
        self.epanetClass.deleteNodeJunctionDemand(1, 2)    
        self.assertNotEqual(self.epanetClass.getNodeJunctionDemandIndex(nodeIndex), [[1, 2]], err_msg)
        # Test 2
        self.epanetClass.addNodeJunctionDemand(nodeIndex, baseDemand, patternId, 'new demand_2')   # Adds a new demand to the first node and returns the new demand index
        self.epanetClass.addNodeJunctionDemand(nodeIndex, baseDemand, patternId, 'new demand_3')   # Adds a new demand to the first node and returns the new demand index
        self.epanetClass.deleteNodeJunctionDemand(1) 
        print('UserWarning expected since the Demand is deleted')                                                                # Deletes all the demands of the 1st node
        self.assertNotEqual(self.epanetClass.getNodeJunctionDemandName(1), {1: [''], 2: ['new demand_2'], 3: ['new demand_3']}, err_msg)
        # Test 3
        nodeIndex = [1, 2, 3]
        baseDemand = [100, 110, 150]
        patternId = ['1', '1', '']
        self.epanetClass.addNodeJunctionDemand(nodeIndex, baseDemand, patternId, ['new demand_1', 'new demand_2', 'new demand_3'])     # Adds 3 new demands to the first 3 nodes
        demand_index_old = self.epanetClass.getNodeJunctionDemandIndex(nodeIndex)
        self.epanetClass.deleteNodeJunctionDemand([1,2,3])  
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
        d.unload()

    def testdeleteRules(self):
        err_msg = 'Rule not deleted'
        # Test 1
        d = epanet('BWSN_Network_1.inp')
        d.deleteRules()                      # Deletes all the rule-based control
        self.assertEqual(d.getRuleCount(), 0, err_msg)
        d.unload()
        # Test 2
        d = epanet('BWSN_Network_1.inp')
        rule_id_1 = d.getRuleID(1)
        d.deleteRules(1)        # Deletes the 1st rule-based control
        self.assertNotEqual(d.getRuleID(1), rule_id_1, err_msg)
        d.unload()
        # Test 3
        d = epanet('BWSN_Network_1.inp')
        d.deleteRules([1,2,3])  # Deletes the 1st to 3rd rule-based control
        self.assertEqual(d.getRuleCount(), 1, err_msg)
        d.unload()

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
            np.array([[127.54072491, 119.25732074, 117.02125399, 118.66902368,
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
            np.array([[2.35286666e+00, 2.57230086e+00, 5.28331232e-01, 7.80876836e-01,
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
            np.array([[1., 0.45269294, 0.44701226, 0.43946804, 0.42596667,
                0.4392986 , 0.45068901, 0.41946084, 0.4033391 , 1.,
                0.97200717]]).all(),
            'Wrong NodeQuality output')
        self.assertEqual(self.epanetClass.getComputedQualityTimeSeries().LinkQuality.all(),
            np.array([[0.79051035, 0.44701226, 0.43946804, 0.43188486, 0.45136891,
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
        d.unload()

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
        d.unload()

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
        d.unload()

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

        # ''' ---getLinkPumpSwitches---    '''
        # err_msg = 'Wrong Pump Switches'
        # # Test 11
        # self.assertEqual(d.getLinkPumpSwitches(),  [5, 2, 5, 7, 6, 6, 4], err_msg)

        ''' ---getLinkPumpType---    '''
        err_msg = 'Wrong Pump Type'
        # Test 12
        self.assertEqual(d.getLinkPumpType(),  ['CUSTOM', 'CUSTOM', 'CUSTOM', 'CUSTOM', 'CUSTOM', 'CUSTOM', 'CUSTOM'], err_msg)

        ''' ---getLinkPumpTypeCode---    '''
        err_msg = 'Wrong Pump Type Code'
        d.unload()
        # Test 13
        d = epanet('Richmond_skeleton.inp')
        self.assertEqual(d.getLinkPumpTypeCode(),  [2, 2, 2, 2, 2, 2, 2], err_msg)
        self.epanetClass.unload()
        self.epanetClass = epanet('Net1.inp')
        self.assertEqual(self.epanetClass.getLinkPumpTypeCode(),  [1], err_msg)
        d.unload()

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
        d.unload()

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
        d.unload()
        # Valve
        d = epanet('ky10.inp')
        valve_indices = list(d.getLinkValveIndex())
        self.assertEqual(valve_indices, [1057, 1058, 1059, 1060, 1061], 'Wrong valve indices')
        valve_IDs = d.getLinkValveNameID([1,2,3])
        self.assertEqual(valve_IDs, ['~@RV-1', '~@RV-2', '~@RV-3'], 'Wrong valve IDs')
        d.unload()

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
        actual_def = self.epanetClass.getComputedHydraulicTimeSeries().DemandDeficit[0]
        desired_dem_def  = [0.0, -0.0012342832044413999, -0.0012111212332749546, -0.0012281893931302976, -0.0012177492556971789, 
                    -0.0012291126064630734, -0.0012496099800993576, -0.0011990998540248189, -0.0011465764024330798, 0.0, 0.0]
        self.assertEqual(list(actual_def), desired_dem_def, 'Wrong Demand Deficit Output')

        ''' ---getNodeDemandPatternIndex---    '''
        d = epanet('BWSN_Network_1.inp')
        self.assertEqual(len(d.getNodeDemandPatternIndex()), 2, 'Wrong Node Demand Pattern Dict length')
        self.assertEqual(d.getNodeDemandPatternIndex()[2][120:122],[2, 2], 'Wrong Node Demand Pattern Index Output')
                                                 
        ''' ---getNodeDemandPatternNameID---    '''
        self.assertEqual(len(d.getNodeDemandPatternNameID()), 2, 'Wrong Node Demand Pattern Dict length')
        self.assertEqual(d.getNodeDemandPatternNameID()[2][120:122], ['PATTERN-1', 'PATTERN-1'], 'Wrong Node Demand Pattern ID Output')
        d.unload()
        
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
        err_msg = 'Error in Tank Data'
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
                         'Minimum_Water_Volume' : np.array([ 88906.0982, 162003.2134,  43329.1552,  78769.7649,  32143.4605,
                                                91315.882 ,  19413.1796,  52738.7366, 328576.659 , 191865.8795,
                                                249097.5199, 226751.1364, 167879.2973]), 
                         'Maximum_Water_Volume' : np.array([103043.265143, 184905.42384766001, 56602.33107023415, 92042.99386315, 
                                                46869.676065625, 122731.80854, 27581.320500399997, 63341.611807249996, 368207.85033021, 
                                                260588.21880625002, 312809.01892312005, 301081.21859364, 193012.038532]), 
                         'Volume_Curve_Index': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])}  

        self.assertEqual(tData['Index'], desired_tData['Index'], err_msg)
        self.assertEqual(d.getNodeTankNameID(), ['T-1', 'T-10', 'T-11', 'T-12', 'T-13', 'T-2', 'T-3', 'T-4', 'T-5', 'T-6', 'T-7', 'T-8', 'T-9'], err_msg)
        np.testing.assert_array_almost_equal(tData['Elevation'], desired_tData['Elevation'], err_msg=err_msg)
        np.testing.assert_array_almost_equal(tData['Initial_Level'], desired_tData['Initial_Level'], err_msg=err_msg)
        np.testing.assert_array_almost_equal(tData['Minimum_Water_Level'], desired_tData['Minimum_Water_Level'], err_msg=err_msg)
        np.testing.assert_array_almost_equal(tData['Maximum_Water_Level'], desired_tData['Maximum_Water_Level'], err_msg=err_msg)
        np.testing.assert_array_almost_equal(tData['Diameter'], desired_tData['Diameter'], err_msg=err_msg)
        np.testing.assert_array_almost_equal(tData['Minimum_Water_Volume']/1000, desired_tData['Minimum_Water_Volume']/1000, err_msg=err_msg)
        np.testing.assert_array_almost_equal(tData['Volume_Curve_Index'], desired_tData['Volume_Curve_Index'], err_msg=err_msg)
        d.unload()

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
        d.unload()

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
        d = epanet('BWSN_Network_1.inp')
        self.assertEqual(d.getOptionsAccuracyValue(), 0.005, 'Wrong Options Accuracy Value Output')
        self.assertEqual(d.getOptionsCheckFrequency(), 2.0, 'Wrong Options Check Frequency Output') 
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
        d.unload()
    
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
        d.unload()

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
        d.unload()

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
        d.unload()

        ''' ---setCurveValue---    '''  
        d = epanet('BWSN_Network_1.inp')
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
        d.unload()

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
        d.unload()
        
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
        d.unload()

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
        d.unload()

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
        d.unload()
    
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
        d.unload()
        
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
        d.unload()
        
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
        d.unload()
        
    def testsetNodeTankDiameter(self):
        err_msg = 'Error setting Node Tank Diameter'
        d=epanet('BWSN_Network_1.inp')
        
        # Test 1
        d.setNodeTankDiameter(120)                      
        np.testing.assert_array_almost_equal(d.getNodeTankDiameter(), np.array([120., 120.]), err_msg=err_msg)

        # Test 2
        d.setNodeTankDiameter([110, 130])              
        np.testing.assert_almost_equal(list(d.getNodeTankDiameter()), [110, 130], err_msg=err_msg)

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
        d.unload()
        
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
        
class AnalysisTest(unittest.TestCase):

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
        d.unload()

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
        
        desired_act_dem_20 = np.array([   0.        ,   60.        ,   60.        ,   40.        ,
                                          60.        ,   80.        ,   60.        ,   40.        ,
                                          40.        ,    0.        , -440.00076023])
        np.testing.assert_array_almost_equal(D[20]/1000, desired_act_dem_20/1000, err_msg=err_msg) 

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
            d.runQualityAnalysis()
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
            d.nextQualityAnalysisStep()
        d.closeQualityAnalysis()
        d.closeHydraulicAnalysis()
        d.unload()

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
        
        desired_flow_10 = np.array([-3.19163104e-07, -3.69432046e+01,  1.72632041e+01, -1.71767959e+01,
                                  -3.68567959e+01, -9.34800005e+01, -1.05780001e+02,  3.44400000e+01,
                                  -1.50060001e+02,  1.23000000e+01, -1.84500001e+02, -2.70058801e+02,
                                  -3.09418801e+02, -3.87691998e+02, -5.10691998e+02,  7.33531976e+01,
                                    1.28366802e+02,  3.94233686e+00,  8.31091392e+01,  3.39091392e+01,
                                    2.02108608e+01,  1.18080000e+02,  3.58045905e+01, -3.55540947e+00,
                                    3.55354095e+01, -6.71038801e+02, -6.43978801e+02, -6.90718801e+02,
                                  -7.94038801e+02,  8.85600000e+01,  4.67400000e+01,  2.70600000e+01,
                                    4.23551620e+00,  7.38000000e+00,  3.69000000e+00, -7.91086075e+00,
                                    5.60448380e+00,  7.38000000e+00,  1.77551620e+00,  2.46000000e+00])
        np.testing.assert_array_almost_equal(F[10], desired_flow_10, err_msg=err_msg) 
        
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
        
        desired_actual_qual_n_45 = np.array([0.09      , 0.08927529, 0.08979756, 0.08926078, 0.08747952,
                                            0.08717831, 0.08676482, 0.09010864, 0.08659873, 0.12272579,
                                            0.0864319 , 0.76375766, 0.76376316, 0.76376316, 0.76376316,
                                            0.0820711 , 0.7432995 , 0.15814202, 0.07636707, 0.0854724 ,
                                            0.85594054, 0.84164127, 0.76376316, 0.76376316, 0.76376316,
                                            0.08161471, 0.92705355, 0.12725728, 0.40659917, 0.76376316,
                                            0.69914026, 0.9270073 , 1.00053611, 0.32030924, 1.00047879,
                                            0.76376316])
        np.testing.assert_array_almost_equal(QN[45]/1000, desired_actual_qual_n_45/1000, err_msg=err_msg)

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
        np.testing.assert_array_almost_equal(NDemSensN[20]/100, desired_act_dem_sen_20/100, err_msg=err_msg) 
        
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
        np.testing.assert_array_almost_equal(NActQual[50]/1000, desired_act_qual_sens_50/1000, err_msg=err_msg)

        # Test Node Mass Flow Rate
        err_msg = 'Error in Node Mass Flow Rate'
        desired_act_dem_MFR__2 = [18168918.949573442, None, None, None, None, None, None, None, None,
                                    None, None, None, None, None, None, None, None, None, None, None,
                                    None, None, None, None, None, None, None, None, None, None, None,
                                    None, None, None, None, None]
        self.assertEqual(list(MFR_[2]), desired_act_dem_MFR__2, err_msg) 
        
    def testgetComputedHydraulicTimeSeries(self):
        d = epanet('Net1.inp')
        comp_vals = d.getComputedHydraulicTimeSeries()
        err_msg = 'Error in getComputedHydraulicTimeSeries output'
        d.unload()
        
        # Test Demand 
        desired = np.array([[    0.        ,   150.        ,   150.        ,   100.        ,
           150.        ,   200.        ,   150.        ,   100.        ,
           100.        , -1866.17582999,   766.17582999],
        [    0.        ,   150.        ,   150.        ,   100.        ,
           150.        ,   200.        ,   150.        ,   100.        ,
           100.        , -1848.5811499 ,   748.5811499 ],
        [    0.        ,   180.        ,   180.        ,   120.        ,
           180.        ,   240.        ,   180.        ,   120.        ,
           120.        , -1837.46107838,   517.46107838],
        [    0.        ,   180.        ,   180.        ,   120.        ,
           180.        ,   240.        ,   180.        ,   120.        ,
           120.        , -1825.38318977,   505.38318977],
        [    0.        ,   210.        ,   210.        ,   140.        ,
           210.        ,   280.        ,   210.        ,   140.        ,
           140.        , -1819.85520335,   279.85520335],
        [    0.        ,   210.        ,   210.        ,   140.        ,
           210.        ,   280.        ,   210.        ,   140.        ,
           140.        , -1813.25153977,   273.25153977],
        [    0.        ,   240.        ,   240.        ,   160.        ,
           240.        ,   320.        ,   240.        ,   160.        ,
           160.        , -1813.12872281,    53.12872281],
        [    0.        ,   240.        ,   240.        ,   160.        ,
           240.        ,   320.        ,   240.        ,   160.        ,
           160.        , -1811.8684852 ,    51.86848521],
        [    0.        ,   210.        ,   210.        ,   140.        ,
           210.        ,   280.        ,   210.        ,   140.        ,
           140.        , -1804.28817716,   264.28817716],
        [    0.        ,   210.        ,   210.        ,   140.        ,
           210.        ,   280.        ,   210.        ,   140.        ,
           140.        , -1797.99885729,   257.99885729],
        [    0.        ,   180.        ,   180.        ,   120.        ,
           180.        ,   240.        ,   180.        ,   120.        ,
           120.        , -1785.47819904,   465.47819904],
        [    0.        ,   180.        ,   180.        ,   120.        ,
           180.        ,   240.        ,   180.        ,   120.        ,
           120.        , -1774.30359304,   454.30359304],
        [    0.        ,   150.        ,   150.        ,   100.        ,
           150.        ,   200.        ,   150.        ,   100.        ,
           100.        , -1757.03555296,   657.03555296],
        [    0.        ,   150.        ,   150.        ,   100.        ,
           150.        ,   200.        ,   150.        ,   100.        ,
           100.        ,     0.        , -1100.00084621],
        [    0.        ,   150.        ,   150.        ,   100.        ,
           150.        ,   200.        ,   150.        ,   100.        ,
           100.        ,     0.        , -1100.00083973],
        [    0.        ,   120.        ,   120.        ,    80.        ,
           120.        ,   160.        ,   120.        ,    80.        ,
            80.        ,     0.        ,  -880.00081984],
        [    0.        ,   120.        ,   120.        ,    80.        ,
           120.        ,   160.        ,   120.        ,    80.        ,
            80.        ,     0.        ,  -880.00080573],
        [    0.        ,    90.        ,    90.        ,    60.        ,
            90.        ,   120.        ,    90.        ,    60.        ,
            60.        ,     0.        ,  -660.0007914 ],
        [    0.        ,    90.        ,    90.        ,    60.        ,
            90.        ,   120.        ,    90.        ,    60.        ,
            60.        ,     0.        ,  -660.00077694],
        [    0.        ,    60.        ,    60.        ,    40.        ,
            60.        ,    80.        ,    60.        ,    40.        ,
            40.        ,     0.        ,  -440.00076867],
        [    0.        ,    60.        ,    60.        ,    40.        ,
            60.        ,    80.        ,    60.        ,    40.        ,
            40.        ,     0.        ,  -440.00076023],
        [    0.        ,    90.        ,    90.        ,    60.        ,
            90.        ,   120.        ,    90.        ,    60.        ,
            60.        ,     0.        ,  -660.00075021],
        [    0.        ,    90.        ,    90.        ,    60.        ,
            90.        ,   120.        ,    90.        ,    60.        ,
            60.        ,     0.        ,  -660.0007362 ],
        [    0.        ,   120.        ,   120.        ,    80.        ,
           120.        ,   160.        ,   120.        ,    80.        ,
            80.        ,     0.        ,  -880.00072421],
        [    0.        ,   120.        ,   120.        ,    80.        ,
           120.        ,   160.        ,   120.        ,    80.        ,
            80.        , -1916.54228315,  1036.54228315],
        [    0.        ,   120.        ,   120.        ,    80.        ,
           120.        ,   160.        ,   120.        ,    80.        ,
            80.        , -1909.42463758,  1029.42463758],
        [    0.        ,   150.        ,   150.        ,   100.        ,
           150.        ,   200.        ,   150.        ,   100.        ,
           100.        , -1892.24322665,   792.24322665]])
        actual = comp_vals.Demand
        self.assertEqual(actual.all(), desired.all(), err_msg)
    
        # Test Energy
        desired = np.array([[6.72482481e+00, 3.52704749e+00, 2.91862104e-02, 8.89394398e-02,
         9.85232843e-03, 1.30951217e-02, 1.00839487e-02, 1.24317362e+00,
         3.52652499e-02, 1.25777125e-03, 1.10285438e-01, 3.78119311e-02,
         9.58448204e+01],
        [6.54557392e+00, 3.41589541e+00, 2.96887268e-02, 8.44134710e-02,
         9.67258858e-03, 1.27809351e-02, 9.43746163e-03, 1.21531545e+00,
         3.69089846e-02, 1.35506512e-03, 1.09514251e-01, 3.84457983e-02,
         9.60658732e+01],
        [6.43390186e+00, 2.98741850e+00, 6.68628666e-02, 4.52610606e-02,
         1.14105417e-02, 1.44236747e-02, 3.29234295e-03, 1.32652335e+00,
         1.24884165e-01, 6.78134962e-03, 1.65122141e-01, 8.24121815e-02,
         9.61890784e+01],
        [6.31402088e+00, 2.91783445e+00, 6.74490248e-02, 4.32949213e-02,
         1.12752624e-02, 1.42638897e-02, 3.07788504e-03, 1.30746622e+00,
         1.27279868e-01, 6.97675152e-03, 1.64644813e-01, 8.29104608e-02,
         9.63085216e+01],
        [6.25963955e+00, 2.54036390e+00, 1.25719953e-01, 2.04999630e-02,
         1.33356989e-02, 1.78857641e-02, 5.70400522e-04, 1.45897027e+00,
         2.88694618e-01, 1.88707796e-02, 2.42154455e-01, 1.43481368e-01,
         9.63582230e+01],
        [6.19507610e+00, 2.50558405e+00, 1.26187606e-01, 1.98727436e-02,
         1.32561592e-02, 1.78175335e-02, 5.32846948e-04, 1.44839099e+00,
         2.90825087e-01, 1.90710310e-02, 2.41927565e-01, 1.43745606e-01,
         9.64135251e+01],
        [6.19387944e+00, 2.17508225e+00, 2.08722912e-01, 7.77918714e-03,
         1.57357081e-02, 2.33540374e-02, 4.99074298e-06, 1.64183972e+00,
         5.38835774e-01, 3.90061443e-02, 3.44759276e-01, 2.21490403e-01,
         9.64145118e+01],
        [6.18160675e+00, 2.16899301e+00, 2.08842646e-01, 7.71737223e-03,
         1.57193849e-02, 2.33451475e-02, 4.65831687e-06, 1.63976153e+00,
         5.39416072e-01, 3.90652149e-02, 3.44724690e-01, 2.21536542e-01,
         9.64245744e+01],
        [6.10813615e+00, 2.45885139e+00, 1.26823085e-01, 1.90419473e-02,
         1.31488416e-02, 1.77255310e-02, 4.84497561e-04, 1.43413133e+00,
         2.93726859e-01, 1.93445121e-02, 2.41622889e-01, 1.44099012e-01,
         9.64815261e+01],
        [6.04760857e+00, 2.42639864e+00, 1.27270443e-01, 1.84737793e-02,
         1.30738953e-02, 1.76631693e-02, 4.52334603e-04, 1.42419515e+00,
         2.95774056e-01, 1.95381137e-02, 2.41412673e-01, 1.44347021e-01,
         9.65244044e+01],
        [5.92827381e+00, 2.69520654e+00, 6.94051747e-02, 3.72069793e-02,
         1.08366120e-02, 1.37582471e-02, 2.43430410e-03, 1.24600579e+00,
         1.35368273e-01, 7.64674909e-03, 1.63120411e-01, 8.45175240e-02,
         9.65979543e+01],
        [5.82306898e+00, 2.63485415e+00, 6.99588984e-02, 3.56120145e-02,
         1.07159575e-02, 1.36247039e-02, 2.27131399e-03, 1.22920622e+00,
         1.37683010e-01, 7.84141592e-03, 1.62709112e-01, 8.49610184e-02,
         9.66503914e+01],
        [5.66289357e+00, 2.87322928e+00, 3.23999820e-02, 6.33162483e-02,
         8.76986755e-03, 1.12985492e-02, 6.50562994e-03, 1.07779747e+00,
         4.61757435e-02, 1.94182565e-03, 1.05750617e-01, 4.16831648e-02,
         9.67071141e+01],
        [5.43703141e-18, 1.03683269e-01, 8.55448201e-02, 5.13031381e-03,
         1.43675171e-03, 4.78269786e-03, 2.82864723e-02, 1.13722047e-01,
         3.07192578e-01, 2.93925724e-02, 8.52743186e-02, 6.43812284e-02,
         0.00000000e+00],
        [5.29830034e-18, 1.03683264e-01, 8.55448204e-02, 5.13031377e-03,
         1.43675171e-03, 4.78269930e-03, 2.82864718e-02, 1.13722050e-01,
         3.07192579e-01, 2.93925726e-02, 8.52743193e-02, 6.43812331e-02,
         0.00000000e+00],
        [5.02411460e-18, 5.48683444e-02, 4.52695731e-02, 2.71491976e-03,
         7.60316211e-04, 2.53096228e-03, 1.49689602e-02, 6.01806911e-02,
         1.62563643e-01, 1.55542947e-02, 4.51264213e-02, 3.40699857e-02,
         0.00000000e+00],
        [4.72951243e-18, 5.48683378e-02, 4.52695727e-02, 2.71491950e-03,
         7.60316230e-04, 2.53096231e-03, 1.49689595e-02, 6.01806931e-02,
         1.62563641e-01, 1.55542944e-02, 4.51264214e-02, 3.40699856e-02,
         0.00000000e+00],
        [4.49155505e-18, 2.41544669e-02, 1.99288015e-02, 1.19517748e-03,
         3.34710079e-04, 1.11419274e-03, 6.58971583e-03, 2.64930314e-02,
         7.15645991e-02, 6.84739170e-03, 1.98657790e-02, 1.49984612e-02,
         0.00000000e+00],
        [4.31053302e-18, 2.41544629e-02, 1.99288013e-02, 1.19517733e-03,
         3.34710091e-04, 1.11419275e-03, 6.58971542e-03, 2.64930326e-02,
         7.15645978e-02, 6.84739154e-03, 1.98657791e-02, 1.49984611e-02,
         0.00000000e+00],
        [4.15676997e-18, 7.59953437e-03, 6.27002154e-03, 3.76029161e-04,
         1.05306735e-04, 3.50548330e-04, 2.07326633e-03, 8.33525502e-03,
         2.25157371e-02, 2.15433462e-03, 6.25019110e-03, 4.71883176e-03,
         0.00000000e+00],
        [3.98068238e-18, 7.59953327e-03, 6.27002148e-03, 3.76029119e-04,
         1.05306738e-04, 3.50548334e-04, 2.07326622e-03, 8.33525535e-03,
         2.25157367e-02, 2.15433458e-03, 6.25019112e-03, 4.71883174e-03,
         0.00000000e+00],
        [3.85588976e-18, 2.41544555e-02, 1.99288009e-02, 1.19517705e-03,
         3.34710112e-04, 1.11419278e-03, 6.58971466e-03, 2.64930348e-02,
         7.15645954e-02, 6.84739123e-03, 1.98657792e-02, 1.49984610e-02,
         0.00000000e+00],
        [3.66027298e-18, 2.41544516e-02, 1.99288007e-02, 1.19517690e-03,
         3.34710123e-04, 1.11419280e-03, 6.58971426e-03, 2.64930360e-02,
         7.15645941e-02, 6.84739108e-03, 1.98657793e-02, 1.49984609e-02,
         0.00000000e+00],
        [3.44342137e-18, 5.48682994e-02, 4.52695706e-02, 2.71491803e-03,
         7.60316341e-04, 2.53096246e-03, 1.49689555e-02, 6.01807046e-02,
         1.62563628e-01, 1.55542928e-02, 4.51264220e-02, 3.40699848e-02,
         0.00000000e+00],
        [7.25549028e+00, 4.23983044e+00, 9.00655140e-03, 1.64412838e-01,
         8.45407969e-03, 1.51417090e-02, 2.38770180e-02, 1.22915082e+00,
         2.47174744e-03, 1.14102961e-05, 7.48925418e-02, 9.94558872e-03,
         9.50326068e+01],
        [7.17890598e+00, 4.18957571e+00, 9.08846069e-03, 1.61616647e-01,
         8.39679888e-03, 1.49382117e-02, 2.34123807e-02, 1.21732100e+00,
         2.60226579e-03, 1.30524959e-05, 7.45399713e-02, 1.01019497e-02,
         9.51636971e+01],
        [6.99620555e+00, 3.69587724e+00, 2.84528612e-02, 9.59364455e-02,
         1.01222318e-02, 1.35791132e-02, 1.10935473e-02, 1.28531402e+00,
         3.29103289e-02, 1.12232080e-03, 1.11456923e-01, 3.68674584e-02,
         9.54579159e+01]])
        actual = comp_vals.Energy
        self.assertEqual(actual.all(), desired.all(), err_msg)
        
        # Test Energy
        desired = np.array([[ 1.86617583e+03,  1.23420718e+03,  1.29335135e+02,
          1.91158131e+02,  1.20664865e+02,  4.08105191e+01,
         -7.66175830e+02,  4.81968650e+02,  1.88696216e+02,
          2.93351346e+01,  1.40810519e+02,  5.91894809e+01,
          1.86617583e+03],
        [ 1.84858115e+03,  1.22042735e+03,  1.30111610e+02,
          1.87689310e+02,  1.19888390e+02,  4.04644875e+01,
         -7.48581150e+02,  4.78153798e+02,  1.91734592e+02,
          3.01116100e+01,  1.40464488e+02,  5.95355125e+01,
          1.84858115e+03],
        [ 1.83746108e+03,  1.16440006e+03,  1.72960241e+02,
          1.50844068e+02,  1.27039759e+02,  4.22169485e+01,
         -5.17461078e+02,  4.93061017e+02,  2.93978742e+02,
          5.29602410e+01,  1.62216948e+02,  7.77830515e+01,
          1.83746108e+03],
        [ 1.82538319e+03,  1.15481752e+03,  1.73490386e+02,
          1.48513298e+02,  1.26509614e+02,  4.20523725e+01,
         -5.05383190e+02,  4.90565671e+02,  2.95943943e+02,
          5.34903860e+01,  1.62052373e+02,  7.79476275e+01,
          1.82538319e+03],
        [ 1.81985520e+03,  1.10006346e+03,  2.15822181e+02,
          1.14267063e+02,  1.34177819e+02,  4.55246756e+01,
         -2.79855203e+02,  5.09791739e+02,  3.94386080e+02,
          7.58221812e+01,  1.85524676e+02,  9.44753244e+01,
          1.81985520e+03],
        [ 1.81325154e+03,  1.09475901e+03,  2.16103334e+02,
          1.13028825e+02,  1.33896666e+02,  4.54637067e+01,
         -2.73251540e+02,  5.08492532e+02,  3.95404135e+02,
          7.61033339e+01,  1.85463707e+02,  9.45362933e+01,
          1.81325154e+03],
        [ 1.81312872e+03,  1.04178538e+03,  2.57806090e+02,
          8.13540284e+01,  1.42193910e+02,  4.99893150e+01,
         -5.31287228e+01,  5.31343343e+02,  4.90850566e+02,
          9.78060902e+01,  2.09989315e+02,  1.10010685e+02,
          1.81312872e+03],
        [ 1.81186849e+03,  1.04076173e+03,  2.57857897e+02,
          8.11250490e+01,  1.42142103e+02,  4.99817055e+01,
         -5.18684852e+01,  5.31106754e+02,  4.91035349e+02,
          9.78578969e+01,  2.09981705e+02,  1.10018295e+02,
          1.81186849e+03],
        [ 1.80428818e+03,  1.08755603e+03,  2.16484345e+02,
          1.11350203e+02,  1.33515655e+02,  4.53819462e+01,
         -2.64288177e+02,  5.06732149e+02,  3.96783506e+02,
          7.64843453e+01,  1.85381946e+02,  9.46180538e+01,
          1.80428818e+03],
        [ 1.79799886e+03,  1.08250108e+03,  2.16751748e+02,
          1.10172569e+02,  1.33248252e+02,  4.53252098e+01,
         -2.57998857e+02,  5.05497779e+02,  3.97750473e+02,
          7.67517481e+01,  1.85325210e+02,  9.46747902e+01,
          1.79799886e+03],
        [ 1.78547820e+03,  1.12312406e+03,  1.75238299e+02,
          1.40829046e+02,  1.24761701e+02,  4.15250947e+01,
         -4.65478199e+02,  4.82354140e+02,  3.02407561e+02,
          5.52382987e+01,  1.61525095e+02,  7.84749053e+01,
          1.78547820e+03],
        [ 1.77430359e+03,  1.11424060e+03,  1.75727196e+02,
          1.38681220e+02,  1.24272804e+02,  4.13817757e+01,
         -4.54303593e+02,  4.80062995e+02,  3.04209809e+02,
          5.57271956e+01,  1.61381776e+02,  7.86182243e+01,
          1.77430359e+03],
        [ 1.75703555e+03,  1.14859657e+03,  1.34160177e+02,
          1.69686349e+02,  1.15839823e+02,  3.87526380e+01,
         -6.57035553e+02,  4.58438987e+02,  2.07400835e+02,
          3.41601771e+01,  1.38752638e+02,  6.12473620e+01,
          1.75703555e+03],
        [-8.45711330e-04, -3.58364876e+02,  1.88567513e+02,
         -7.03036982e+01,  6.14324872e+01,  2.86677284e+01,
          1.10000085e+03,  2.08364030e+02,  4.03068457e+02,
          8.85675128e+01,  1.28667728e+02,  7.13322716e+01,
          0.00000000e+00],
        [-8.38100537e-04, -3.58364870e+02,  1.88567513e+02,
         -7.03036975e+01,  6.14324871e+01,  2.86677280e+01,
          1.10000084e+03,  2.08364031e+02,  4.03068457e+02,
          8.85675129e+01,  1.28667728e+02,  7.13322720e+01,
          0.00000000e+00],
        [-8.22614269e-04, -2.86692024e+02,  1.50854015e+02,
         -5.62429774e+01,  4.91459851e+01,  2.29341815e+01,
          8.80000820e+02,  1.66691204e+02,  3.22454781e+02,
          7.08540149e+01,  1.02934182e+02,  5.70658185e+01,
          0.00000000e+00],
        [-8.05466293e-04, -2.86692012e+02,  1.50854014e+02,
         -5.62429756e+01,  4.91459855e+01,  2.29341816e+01,
          8.80000806e+02,  1.66691206e+02,  3.22454779e+02,
          7.08540145e+01,  1.02934182e+02,  5.70658184e+01,
          0.00000000e+00],
        [-7.90919740e-04, -2.15019170e+02,  1.13140517e+02,
         -4.21822563e+01,  3.68594834e+01,  1.72006351e+01,
          6.60000791e+02,  1.25018379e+02,  2.41841105e+02,
          5.31405166e+01,  7.72006351e+01,  4.27993649e+01,
          0.00000000e+00],
        [-7.79637702e-04, -2.15019158e+02,  1.13140516e+02,
         -4.21822544e+01,  3.68594838e+01,  1.72006352e+01,
          6.60000777e+02,  1.25018381e+02,  2.41841103e+02,
          5.31405162e+01,  7.72006352e+01,  4.27993648e+01,
          0.00000000e+00],
        [-7.69727518e-04, -1.43346322e+02,  7.54270185e+01,
         -2.81215358e+01,  2.45729815e+01,  1.14670887e+01,
          4.40000769e+02,  8.33455529e+01,  1.61227429e+02,
          3.54270185e+01,  5.14670887e+01,  2.85329113e+01,
          0.00000000e+00],
        [-7.58181187e-04, -1.43346314e+02,  7.54270182e+01,
         -2.81215347e+01,  2.45729818e+01,  1.14670887e+01,
          4.40000760e+02,  8.33455540e+01,  1.61227428e+02,
          3.54270182e+01,  5.14670887e+01,  2.85329113e+01,
          0.00000000e+00],
        [-7.49712805e-04, -2.15019135e+02,  1.13140515e+02,
         -4.21822508e+01,  3.68594847e+01,  1.72006354e+01,
          6.60000750e+02,  1.25018385e+02,  2.41841100e+02,
          5.31405153e+01,  7.72006354e+01,  4.27993646e+01,
          0.00000000e+00],
        [-7.36219053e-04, -2.15019123e+02,  1.13140515e+02,
         -4.21822490e+01,  3.68594851e+01,  1.72006355e+01,
          6.60000736e+02,  1.25018386e+02,  2.41841099e+02,
          5.31405149e+01,  7.72006355e+01,  4.27993645e+01,
          0.00000000e+00],
        [-7.20554557e-04, -2.86691941e+02,  1.50854012e+02,
         -5.62429649e+01,  4.91459880e+01,  2.29341821e+01,
          8.80000724e+02,  1.66691217e+02,  3.22454771e+02,
          7.08540120e+01,  1.02934182e+02,  5.70658179e+01,
          0.00000000e+00],
        [ 1.91654228e+03,  1.31648687e+03,  8.56401732e+01,
          2.37113159e+02,  1.14359827e+02,  4.29422501e+01,
         -1.03654228e+03,  4.80055409e+02,  7.43044181e+01,
          5.64017321e+00,  1.22942250e+02,  3.70577499e+01,
          1.91654228e+03],
        [ 1.90942464e+03,  1.31099432e+03,  8.59124589e+01,
          2.35691317e+02,  1.14087541e+02,  4.27390031e+01,
         -1.02942464e+03,  4.78430320e+02,  7.56572215e+01,
          5.91245886e+00,  1.22739003e+02,  3.72609969e+01,
          1.90942464e+03],
        [ 1.89224323e+03,  1.25460804e+03,  1.28186245e+02,
          1.96302018e+02,  1.21813755e+02,  4.13331707e+01,
         -7.92243227e+02,  4.87635189e+02,  1.84178566e+02,
          2.81862454e+01,  1.41333171e+02,  5.86668293e+01,
          1.89224323e+03]])
        actual = comp_vals.Flow
        self.assertEqual(actual.all(), desired.all(), err_msg)

        # Test Pressure
        desired = np.array([[127.54072491, 119.25732074, 117.02125399, 118.66902368,
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
         108.84261138,   0.        ,  50.00371454]])
        actual = comp_vals.Pressure
        self.assertEqual(actual.all(), desired.all(), err_msg)

        # Test Setting 
        desired = np.array([[100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   0.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   0.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   0.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   0.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   0.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   0.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   0.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   0.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   0.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   0.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   0.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.],
        [100., 100., 100., 100., 100., 100., 100., 100., 100., 100.,
         100., 100.,   1.]])
        actual = comp_vals.Setting
        self.assertEqual(actual.all(), desired.all(), err_msg)

        # Test Head 
        desired = np.array([[1004.34739189,  985.23037329,  970.06982226,  968.87266023,
          971.54663549,  969.07836152,  968.64520007,  967.39159919,
          965.68932635,  800.        ,  970.        ],
        [1006.76814245,  987.98358534,  973.13502388,  971.92451698,
          974.49975878,  972.11379434,  971.68578097,  970.3636129 ,
          968.68797438,  800.        ,  973.06814207],
        [1008.28626246,  989.71044083,  976.09957997,  974.04874621,
          975.43774601,  973.84594697,  973.36945197,  970.03765808,
          968.22514633,  800.        ,  976.06582645],
        [1009.9247677 ,  991.57444459,  978.17030221,  976.10781146,
          977.43523692,  975.88868908,  975.41587013,  972.04529101,
          970.24584336,  800.        ,  978.13799323],
        [1010.67109832,  992.4235619 ,  980.17260705,  977.08231247,
          977.24098819,  976.28923627,  975.76197387,  970.31658208,
          968.23231971,  800.        ,  980.16179424],
        [1011.55968853,  993.43459156,  981.29281613,  978.19506173,
          978.32359925,  977.39085976,  976.86564164,  971.40340689,
          969.32431114,  800.        ,  981.2824711 ],
        [1011.57618423,  993.45336083,  982.37720201,  978.0821473 ,
          977.06078267,  976.55350364,  975.96642397,  968.35093595,
          965.87250666,  800.        ,  982.37670367],
        [1011.74544232,  993.64594763,  982.58993346,  978.29327831,
          977.26682569,  976.76215716,  976.17547273,  968.55753714,
          966.07967409,  800.        ,  982.58945701],
        [1012.76063251,  994.80111958,  982.80688911,  979.69901395,
          979.78691905,  978.87970014,  978.35724735,  972.87239354,
          970.80030702,  800.        ,  982.79716375],
        [1013.59974558,  995.75600046,  983.86480372,  980.74981344,
          980.80941469,  979.91985719,  979.39933982,  973.89878991,
          971.83140873,  800.        ,  983.85550263],
        [1015.26151339,  997.64721086,  984.91639989,  982.81526192,
          983.94325978,  982.54166031,  982.08086932,  978.58578604,
          976.82808819,  800.        ,  984.88865601],
        [1016.73482368,  999.32414297,  986.77918097,  984.66717213,
          985.74043714,  984.37814379,  983.92069063,  980.39172613,
          978.64506081,  800.        ,  986.75265797],
        [1018.99332921, 1001.89516048,  988.62443951,  987.34325141,
          989.42283701,  987.44331646,  987.04168576,  985.3795608 ,
          983.83283561,  800.        ,  988.57191134],
        [ 988.3287073 ,  988.3287073 ,  989.8635893 ,  987.45690794,
          985.43327331,  985.82040392,  985.69633146,  981.91734208,
          981.03228473,  800.        ,  990.00000913],
        [ 986.31467071,  986.31467071,  987.84955266,  985.4428713 ,
          983.41923666,  983.80636726,  983.68229481,  979.90330538,
          979.01824775,  800.        ,  987.98597249],
        [ 982.47548342,  982.47548342,  983.49079186,  981.89879842,
          980.56018595,  980.81626877,  980.73419622,  978.23443597,
          977.64898009,  800.        ,  983.58103211],
        [ 978.95153061,  978.95153061,  979.96683897,  978.37484553,
          977.0362331 ,  977.2923159 ,  977.21024335,  974.71048311,
          974.12502722,  800.        ,  980.05707922],
        [ 975.88420531,  975.88420531,  976.48015833,  975.54571112,
          974.75998989,  974.91030213,  974.86212828,  973.39485214,
          973.05120907,  800.        ,  976.53312638],
        [ 973.24124   ,  973.24124   ,  973.83719295,  972.90274575,
          972.11702454,  972.26733677,  972.21916292,  970.75188679,
          970.40824372,  800.        ,  973.890161  ],
        [ 970.94094859,  970.94094859,  971.22219836,  970.78120318,
          970.41039628,  970.48133351,  970.45859877,  969.76614477,
          969.60396881,  800.        ,  971.24719568],
        [ 969.17897073,  969.17897073,  969.46022048,  969.0192253 ,
          968.64841841,  968.71935564,  968.69662089,  968.0041669 ,
          967.84199094,  800.        ,  969.48521779],
        [ 967.07431906,  967.07431906,  967.6702719 ,  966.73582471,
          965.95010355,  966.10041575,  966.0522419 ,  964.58496579,
          964.24132271,  800.        ,  967.72323994],
        [ 964.43135392,  964.43135392,  965.02730669,  964.0928595 ,
          963.30713837,  963.45745056,  963.40927671,  961.94200061,
          961.59835753,  800.        ,  965.08027473],
        [ 961.33176144,  961.33176144,  962.34706934,  960.75507595,
          959.41646369,  959.67254641,  959.59047384,  957.09071369,
          956.50525778,  800.        ,  962.43730957],
        [ 997.29098865,  977.20745596,  960.12211291,  959.56419187,
          963.62414769,  959.94563872,  959.55345948,  960.39246166,
          958.5218577 ,  800.        ,  959.99990908],
        [ 998.29958062,  978.35396286,  961.40039995,  960.83918927,
          964.85569112,  961.21792931,  960.82747764,  961.63389259,
          959.77965248,  800.        ,  961.27974566],
        [1000.71877627,  981.10427139,  965.47634991,  964.29880829,
          967.12109119,  964.5284011 ,  964.08757054,  962.93744745,
          961.1945797 ,  800.        ,  965.40206447]])
        actual = comp_vals.Head
        self.assertEqual(actual.all(), desired.all(), err_msg)

        # Test HeadLoss 
        desired = np.array([[ 1.91170186e+01,  1.51605510e+01,  1.19716204e+00,
          2.46827397e+00,  4.33161447e-01,  1.70227284e+00,
          6.98222646e-02,  1.36837378e+01,  9.91460745e-01,
          2.27460153e-01,  4.15503630e+00,  3.38903517e+00,
         -2.04347392e+02],
        [ 1.87845571e+01,  1.48485615e+01,  1.21050690e+00,
          2.38596445e+00,  4.28013370e-01,  1.67563852e+00,
          6.68818165e-02,  1.34838266e+01,  1.02122955e+00,
          2.38736014e-01,  4.13614589e+00,  3.42581995e+00,
         -2.06768142e+02],
        [ 1.85758216e+01,  1.36108609e+01,  2.05083376e+00,
          1.59179904e+00,  4.76495000e-01,  1.81251174e+00,
          3.37535244e-02,  1.42726948e+01,  2.25363300e+00,
          6.79294238e-01,  5.40008793e+00,  5.62080064e+00,
         -2.08286262e+02],
        [ 1.83503231e+01,  1.34041424e+01,  2.06249075e+00,
          1.54654784e+00,  4.72818950e-01,  1.79944765e+00,
          3.23089877e-02,  1.41392077e+01,  2.28161313e+00,
          6.91941331e-01,  5.38994592e+00,  5.64284572e+00,
         -2.09924768e+02],
        [ 1.82475364e+01,  1.22509549e+01,  3.09029458e+00,
          9.51751915e-01,  5.27262401e-01,  2.08426237e+00,
          1.08128027e-02,  1.51825737e+01,  3.88337077e+00,
          1.32033859e+00,  6.92440611e+00,  8.05691657e+00,
         -2.10671098e+02],
        [ 1.81250970e+01,  1.21417754e+01,  3.09775439e+00,
          9.32739493e-01,  5.25218116e-01,  2.07909575e+00,
          1.03450266e-02,  1.51109923e+01,  3.90195637e+00,
          1.32942009e+00,  6.92019236e+00,  8.06654862e+00,
         -2.11559689e+02],
        [ 1.81228234e+01,  1.10761588e+01,  4.29505471e+00,
          5.07279025e-01,  5.87079671e-01,  2.47842929e+00,
          4.98342099e-04,  1.63925782e+01,  5.82369837e+00,
          2.11572332e+00,  8.70984672e+00,  1.06809970e+01,
         -2.11576184e+02],
        [ 1.80994947e+01,  1.10560142e+01,  4.29665515e+00,
          5.04668530e-01,  5.86684425e-01,  2.47786305e+00,
          4.76449867e-04,  1.63791219e+01,  5.82777631e+00,
          2.11780558e+00,  8.70928855e+00,  1.06824831e+01,
         -2.11745442e+02],
        [ 1.79595129e+01,  1.19942305e+01,  3.10787516e+00,
          9.07218909e-01,  5.22452788e-01,  2.07208652e+00,
          9.72535823e-03,  1.50142005e+01,  3.92718897e+00,
          1.34176660e+00,  6.91452551e+00,  8.07939311e+00,
         -2.12760633e+02],
        [ 1.78437451e+01,  1.18911967e+01,  3.11499028e+00,
          8.89557493e-01,  5.20517375e-01,  2.06738117e+00,
          9.30108853e-03,  1.49465858e+01,  3.94494653e+00,
          1.35047362e+00,  6.91062478e+00,  8.08844846e+00,
         -2.13599746e+02],
        [ 1.76143025e+01,  1.27308110e+01,  2.10113798e+00,
          1.40159947e+00,  4.60790997e-01,  1.75769785e+00,
          2.77438823e-02,  1.37039511e+01,  2.37473958e+00,
          7.34392604e-01,  5.35747374e+00,  5.71357212e+00,
         -2.15261513e+02],
        [ 1.74106807e+01,  1.25449620e+01,  2.11200884e+00,
          1.36229335e+00,  4.57453159e-01,  1.74666532e+00,
          2.65230066e-02,  1.35837058e+01,  2.40103719e+00,
          7.46481502e-01,  5.34871100e+00,  5.73308297e+00,
         -2.16734824e+02],
        [ 1.70981687e+01,  1.32707210e+01,  1.28118810e+00,
          1.97952055e+00,  4.01630696e-01,  1.54672519e+00,
          5.25281655e-02,  1.24723235e+01,  1.18112305e+00,
          3.01565648e-01,  4.04327622e+00,  3.61048085e+00,
         -2.18993329e+02],
        [ 3.41060513e-11,  1.53488199e+00,  2.40668135e+00,
          3.87130607e-01,  1.24072454e-01,  8.85057349e-01,
          1.36419834e-01,  2.89543399e+00,  4.04318538e+00,
          1.76057648e+00,  3.51593124e+00,  4.78811919e+00,
          0.00000000e+00],
        [ 3.35376171e-11,  1.53488195e+00,  2.40668136e+00,
          3.87130608e-01,  1.24072454e-01,  8.85057629e-01,
          1.36419833e-01,  2.89543405e+00,  4.04318540e+00,
          1.76057649e+00,  3.51593127e+00,  4.78811951e+00,
          0.00000000e+00],
        [ 3.24007488e-11,  1.01530843e+00,  1.59199344e+00,
          2.56082820e-01,  8.20725551e-02,  5.85455885e-01,
          9.02402529e-02,  1.91529747e+00,  2.67452309e+00,
          1.16460220e+00,  2.32574998e+00,  3.16728869e+00,
          0.00000000e+00],
        [ 3.11501935e-11,  1.01530835e+00,  1.59199343e+00,
          2.56082804e-01,  8.20725564e-02,  5.85455889e-01,
          9.02402502e-02,  1.91529751e+00,  2.67452306e+00,
          1.16460219e+00,  2.32574999e+00,  3.16728868e+00,
          0.00000000e+00],
        [ 3.01270120e-11,  5.95953018e-01,  9.34447212e-01,
          1.50312239e-01,  4.81738433e-02,  3.43643068e-01,
          5.29680493e-02,  1.12421542e+00,  1.56985620e+00,
          6.83582834e-01,  1.36513775e+00,  1.85909306e+00,
          0.00000000e+00],
        [ 2.93312041e-11,  5.95952954e-01,  9.34447205e-01,
          1.50312227e-01,  4.81738443e-02,  3.43643071e-01,
          5.29680471e-02,  1.12421546e+00,  1.56985618e+00,
          6.83582823e-01,  1.36513775e+00,  1.85909305e+00,
          0.00000000e+00],
        [ 2.86490831e-11,  2.81249772e-01,  4.40995177e-01,
          7.09372321e-02,  2.27347425e-02,  1.62175960e-01,
          2.49973176e-02,  5.30552309e-01,  7.40864848e-01,
          3.22604414e-01,  6.44251506e-01,  8.77364698e-01,
          0.00000000e+00],
        [ 2.78532752e-11,  2.81249745e-01,  4.40995174e-01,
          7.09372270e-02,  2.27347430e-02,  1.62175962e-01,
          2.49973167e-02,  5.30552322e-01,  7.40864841e-01,
          3.22604409e-01,  6.44251507e-01,  8.77364695e-01,
          0.00000000e+00],
        [ 2.72848411e-11,  5.95952836e-01,  9.34447192e-01,
          1.50312204e-01,  4.81738463e-02,  3.43643077e-01,
          5.29680431e-02,  1.12421552e+00,  1.56985615e+00,
          6.83582804e-01,  1.36513776e+00,  1.85909304e+00,
          0.00000000e+00],
        [ 2.63753464e-11,  5.95952774e-01,  9.34447186e-01,
          1.50312192e-01,  4.81738474e-02,  3.43643080e-01,
          5.29680411e-02,  1.12421555e+00,  1.56985613e+00,
          6.83582794e-01,  1.36513776e+00,  1.85909303e+00,
          0.00000000e+00],
        [ 2.53521648e-11,  1.01530789e+00,  1.59199338e+00,
          2.56082714e-01,  8.20725642e-02,  5.85455911e-01,
          9.02402347e-02,  1.91529775e+00,  2.67452293e+00,
          1.16460211e+00,  2.32575001e+00,  3.16728863e+00,
          0.00000000e+00],
        [ 2.00835327e+01,  1.70853430e+01,  5.57921045e-01,
          3.67850897e+00,  3.92179237e-01,  1.87060395e+00,
          1.22203828e-01,  1.35833083e+01,  1.76474193e-01,
          1.07323844e-02,  3.23168603e+00,  1.42378102e+00,
         -1.97290989e+02],
        [ 1.99456178e+01,  1.69535629e+01,  5.61210687e-01,
          3.63776181e+00,  3.90451665e-01,  1.85424011e+00,
          1.20654290e-01,  1.34982717e+01,  1.82470648e-01,
          1.17116256e-02,  3.22179852e+00,  1.43827682e+00,
         -1.98299581e+02],
        [ 1.96145049e+01,  1.56279215e+01,  1.17754162e+00,
          2.59269009e+00,  4.40830562e-01,  1.74286775e+00,
          7.42854318e-02,  1.39831802e+01,  9.47948807e-01,
          2.11237749e-01,  4.18364374e+00,  3.33382140e+00,
         -2.00718776e+02]])
        actual = comp_vals.HeadLoss
        self.assertEqual(actual.all(), desired.all(), err_msg)

        # Test State 
        desired = np.array([[3],
        [3],
        [3],
        [3],
        [3],
        [3],
        [3],
        [3],
        [3],
        [3],
        [3],
        [3],
        [3],
        [2],
        [2],
        [2],
        [2],
        [2],
        [2],
        [2],
        [2],
        [2],
        [2],
        [2],
        [3],
        [3],
        [3]])
        actual = comp_vals.State
        self.assertEqual(actual.all(), desired.all(), err_msg)
        
        # Test Tank Volume 
        desired = np.array([[     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 240355.39992932],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 246500.77087736],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 252505.01777571],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 256655.48840308],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 260709.08426249],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 262953.75705037],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 265145.46293336],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 265571.59972454],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 265987.62835619],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 268107.44057455],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 270176.8071875 ],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 273910.33164666],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 277554.22641986],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 280414.65154756],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 276380.61336201],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 267557.68664122],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 260499.344077  ],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 253441.00162603],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 248147.24328703],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 242853.48506405],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 239324.31090452],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 235795.13681264],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 230501.37880408],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 225207.62090786],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 220325.60116484],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 222889.06477206],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 231145.91132522]])
        actual = comp_vals.TankVolume
        self.assertEqual(actual.all(), desired.all(), err_msg)
        
        # Test Tank Velocity 
        desired = np.array([[     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 240355.39992932],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 246500.77087736],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 252505.01777571],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 256655.48840308],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 260709.08426249],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 262953.75705037],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 265145.46293336],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 265571.59972454],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 265987.62835619],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 268107.44057455],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 270176.8071875 ],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 273910.33164666],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 277554.22641986],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 280414.65154756],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 276380.61336201],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 267557.68664122],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 260499.344077  ],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 253441.00162603],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 248147.24328703],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 242853.48506405],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 239324.31090452],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 235795.13681264],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 230501.37880408],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 225207.62090786],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 220325.60116484],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 222889.06477206],
        [     0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        ,      0.        ,      0.        ,
              0.        , 231145.91132522]])
        actual = comp_vals.Velocity
        self.assertEqual(actual.all(), desired.all(), err_msg) 

    def testgetComputedQualityTimeSeries(self):   
        d = epanet('Net1.inp')
        comp_vals = d.getComputedQualityTimeSeries()
        d.unload()
        err_msg = 'Error in getComputedQualityTimeSeries output'
        
        # Test LinkQuality 
        desired_0 = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.75]
        actual_0 = comp_vals.LinkQuality[0]
        np.testing.assert_array_almost_equal(actual_0, desired_0, err_msg=err_msg) 
        
        desired_10 = [0.7905103495922685, 0.447012255612685, 0.43946804267267675, 0.431884859944181, 0.45136890741421926,
                      0.4088524671378628, 0.447544901915228, 0.4401289976946857, 0.4468090703914463, 0.44516552149692806, 
                      0.4194608434894798, 0.4076172688259915, 1.0]
        actual_10 = comp_vals.LinkQuality[10]
        np.testing.assert_array_almost_equal(actual_10, desired_10, err_msg=err_msg) 
        
        desired_25 = [0.9333667984087247, 0.8295918634854789, 0.4082678891873164, 0.36767918327870297, 0.38345550994086436, 
                      0.30650249668366, 0.7946174028666654, 0.8072304802850477, 0.42333201775777995, 0.3714267801242186, 
                      0.3639229545688321, 0.3229344218709133, 1.0]
        actual_25 = comp_vals.LinkQuality[25]
        np.testing.assert_array_almost_equal(actual_25, desired_25, err_msg=err_msg) 

        # Test NodeQuality 
        desired_0 = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0, 1.0]
        actual_0 = comp_vals.NodeQuality[0]
        np.testing.assert_array_almost_equal(actual_0, desired_0, err_msg=err_msg) 
        
        desired_10 = [1.0000000000000002, 0.4526929432239758, 0.447012255612685, 0.4394680426726767, 0.4259666672523444, 
                      0.4392986016631863, 0.45068900627310676, 0.4194608434894798, 0.40333910007431323, 1.0, 0.9720071725424413]
        actual_10 = comp_vals.NodeQuality[10]
        np.testing.assert_array_almost_equal(actual_10, desired_10, err_msg=err_msg) 
        
        desired_25 = [1.0, 0.85732665454064, 0.7949196620043768, 0.36078517810580646, 0.746055505507391, 0.3677236352776429, 
                      0.3843648409713966, 0.32025873566692853, 0.29049233545152015, 1.0, 0.9329052016714082]
        actual_25 = comp_vals.NodeQuality[25]
        np.testing.assert_array_almost_equal(actual_25, desired_25, err_msg=err_msg) 
        
    def testgetComputedTimeSeries(self):
        d = epanet('Net1.inp')
        comp_vals = d.getComputedTimeSeries()
        d.unload()
        err_msg = 'Error in getComputedTimeSeries output'

        # Test LinkQuality 
        desired_0 = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.75]
        actual_0 = comp_vals.LinkQuality[0]
        np.testing.assert_array_almost_equal(actual_0, desired_0, err_msg=err_msg) 
        
        desired_5 = [0.9321969747543335, 0.8248310685157776, 0.6822988986968994, 0.6069462895393372, 
                    0.3435664772987366, 0.3247292637825012, 0.7769863605499268, 0.8085265159606934, 
                    0.7127845287322998, 0.321151465177536, 0.6564596891403198, 0.45066702365875244, 1.0]
        actual_5 = comp_vals.LinkQuality[5]
        np.testing.assert_array_almost_equal(actual_5, desired_5, err_msg=err_msg) 
        
        desired_20 = [0.7951614856719971, 0.5341360569000244, 0.4999150037765503, 0.3575170338153839, 
                      0.3587680757045746, 0.19799287617206573, 0.6330206394195557, 0.3800353407859802, 
                      0.5404495596885681, 0.3071078956127167, 0.24770621955394745, 0.33150285482406616, 0.9240829944610596]
        actual_20 = comp_vals.LinkQuality[20]
        np.testing.assert_array_almost_equal(actual_20, desired_20, err_msg=err_msg)

      # Test Flow 
        desired_0 = [1866.17578125, 1234.2071533203125, 129.33514404296875, 191.1581268310547, 120.66487121582031, 
                    40.81052017211914, -766.1758422851562, 481.9686279296875, 188.6962127685547, 29.335134506225586, 
                    140.81051635742188, 59.18947982788086, 1866.17578125]
        actual_0 = comp_vals.Flow[0]
        np.testing.assert_array_almost_equal(actual_0, desired_0, err_msg=err_msg) 
        
        desired_5 = [1813.2515869140625, 1094.759033203125, 216.10333251953125, 113.02882385253906, 133.89666748046875, 
                    45.463706970214844, -273.2515563964844, 508.4925231933594, 395.4041442871094, 76.10334014892578, 
                    185.4636993408203, 94.53629302978516, 1813.2515869140625]
        actual_5 = comp_vals.Flow[5]
        np.testing.assert_array_almost_equal(actual_5, desired_5, err_msg=err_msg) 
        
        desired_20 = [-0.000749712809920311, -215.01913452148438, 113.14051055908203, -42.1822509765625, 36.8594856262207, 
                    17.20063591003418, 660.000732421875, 125.01838684082031, 241.8411102294922, 53.14051818847656, 77.20063018798828, 
                    42.79936599731445, 0.0]
        actual_20 = comp_vals.Flow[20]
        np.testing.assert_array_almost_equal(actual_20, desired_20, err_msg=err_msg)
       
    def testgetComputedTimeSeries_ENepanet(self):
        d = epanet('Net1.inp')
        comp_vals = d.getComputedTimeSeries_ENepanet()
        err_msg = 'Error in getComputedTimeSeries_ENepanet output'
        d.unload()

        # Test LinkQuality 
        desired_0 = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.75]
        actual_0 = comp_vals.LinkQuality[0]
        np.testing.assert_array_almost_equal(actual_0, desired_0, err_msg=err_msg) 
        
        desired_5 = [0.9321969747543335, 0.8248310685157776, 0.6822988986968994, 0.6069462895393372, 
                    0.3435664772987366, 0.3247292637825012, 0.7769863605499268, 0.8085265159606934, 
                    0.7127845287322998, 0.321151465177536, 0.6564596891403198, 0.45066702365875244, 1.0]
        actual_5 = comp_vals.LinkQuality[5]
        np.testing.assert_array_almost_equal(actual_5, desired_5, err_msg=err_msg) 
        
        desired_20 = [0.7951614856719971, 0.5341360569000244, 0.4999150037765503, 0.3575170338153839, 
                      0.3587680757045746, 0.19799287617206573, 0.6330206394195557, 0.3800353407859802, 
                      0.5404495596885681, 0.3071078956127167, 0.24770621955394745, 0.33150285482406616, 0.9240829944610596]
        actual_20 = comp_vals.LinkQuality[20]
        np.testing.assert_array_almost_equal(actual_20, desired_20, err_msg=err_msg)

      # Test Flow 
        desired_0 = [1866.17578125, 1234.2071533203125, 129.33514404296875, 191.1581268310547, 120.66487121582031, 
                    40.81052017211914, -766.1758422851562, 481.9686279296875, 188.6962127685547, 29.335134506225586, 
                    140.81051635742188, 59.18947982788086, 1866.17578125]
        actual_0 = comp_vals.Flow[0]
        np.testing.assert_array_almost_equal(actual_0, desired_0, err_msg=err_msg) 
        
        desired_5 = [1813.2515869140625, 1094.759033203125, 216.10333251953125, 113.02882385253906, 133.89666748046875, 
                    45.463706970214844, -273.2515563964844, 508.4925231933594, 395.4041442871094, 76.10334014892578, 
                    185.4636993408203, 94.53629302978516, 1813.2515869140625]
        actual_5 = comp_vals.Flow[5]
        np.testing.assert_array_almost_equal(actual_5, desired_5, err_msg=err_msg) 
        
        desired_20 = [-0.000749712809920311, -215.01913452148438, 113.14051055908203, -42.1822509765625, 36.8594856262207, 
                    17.20063591003418, 660.000732421875, 125.01838684082031, 241.8411102294922, 53.14051818847656, 77.20063018798828, 
                    42.79936599731445, 0.0]
        actual_20 = comp_vals.Flow[20]
        np.testing.assert_array_almost_equal(actual_20, desired_20, err_msg=err_msg)
       
        
if __name__ == "__main__":
    unittest.main()  # run all tests
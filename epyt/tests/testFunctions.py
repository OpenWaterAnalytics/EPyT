"""
EPANET Python Toolkit (EPyT) Test Part 1
This file is provided to ensure that all functions can be executed correctly.
Step-by-step execution. You may also use breakpoints.
"""
from epyt import epanet

# Create EPANET object using the INP file
inpname = "Net1.inp"
d = epanet(inpname)  # Net1 Net2 Net3 BWSN_Network_1 ky1 -10

# %% Get/Set Functions
d.printv(d.getConnectivityMatrix())
d.printv(d.getLibFunctions())

d.printv(d.getLinkPumpTypeCode())  # returns type index of all pumps
d.printv(d.getLinkPumpType())  # returns type name of all pumps: CONSTANT_HORSEPOWER, POWER_FUNCTION, CUSTOM
d.printv(d.getLinkPumpHeadCurveIndex())  # returns index of all pump head curve
d.printv(d.getCurveNameID())  # returns all curve IDs
d.printv(d.getCurveNameID(1))  # returns specific curve ID
d.printv(d.addCurve('NewCur1'))  # add new curve with ID
indexCurve = d.addCurve('NewCur2', [[1500, 400], [1800, 200]])  # add new curve with points
d.printv(d.getCurveNameID())
d.printv(d.getCurveValue(indexCurve))  # returns all points for specific curve index
d.printv(d.getCurveValue(indexCurve, 2))  # returns specific point for specific curve index

d.setCurve(3, [[1400, 200], [1900, 300]])  # Change an existing curve
d.printv(d.getCurveValue(indexCurve))

d.printv(d.getCurvesInfo().to_dict())

d.printv(d.getCurveLengths())
d.printv(d.getCurveLengths(3))
d.printv(d.getCurveLengths('NewCur2'))

d.printv(d.getCurveIndex())
d.printv(d.getCurveIndex('NewCur1'))

pointindex = 2
tmppoints = d.getCurveValue(indexCurve, pointindex)
d.setCurveValue(indexCurve, pointindex, tmppoints + 100)
d.printv(d.getCurveValue(indexCurve, pointindex))

bd1 = d.getNodeBaseDemands()  # get an array of the base demands (some nodes may have multiple base demands for
# different patterns)
demandindex = 1
print(bd1[demandindex])
node_index = 5 - 1  # -1 (node_index = 5 / python index)
bd1[demandindex][node_index] = bd1[demandindex][node_index] + 100
d.setNodeBaseDemands(bd1[demandindex])
d.printv(d.getNodeBaseDemands())

d.printv(d.getNodeDemandCategoriesNumber())
d.printv(d.getNodeDemandCategoriesNumber(d.getNodeCount()))
d.printv(d.getNodeDemandCategoriesNumber(list(range(5, d.getNodeCount()))))

# ENgetdemandpattern - Retrieves the index of a demand pattern for a specific demand category of a node
d.printv(d.getNodeDemandPatternNameID()[1])
d.printv(d.getNodeDemandPatternIndex()[1])

# ENgetaveragepatternvalue - Retrieves the average value of a pattern
d.printv(d.getPatternAverageValue())

# ENgetstatistic - Retrieves hydraulic simulation statistic
Statistic = d.getStatistic()
d.printv(Statistic.RelativeError)

d.plot()
nodeCoords = d.getNodeCoordinates()
indexNode = 1
nodeCoords['x'][indexNode] = nodeCoords['x'][indexNode] + 10  # X
nodeCoords['y'][indexNode] = nodeCoords['y'][indexNode] + 20  # Y
newNodeCoords = [list(nodeCoords['x'].values()),
                 list(nodeCoords['y'].values())]
d.setNodeCoordinates(newNodeCoords)
d.plot()

# Quality Info
QualityInfo = d.getQualityInfo()
d.printv(QualityInfo.QualityChemName)

# Others
n = d.getComputedHydraulicTimeSeries()  # EN_TANKVOLUME - ENgetnodevalue
tank_index = d.NodeTankIndex[0] - 1
d.printv(n.TankVolume[:, tank_index])

# EN_STARTTIME  - ENgettimeparam
d.printv(d.getTimeStartTime())

# EN_HTIME - ENgettimeparam
d.printv(d.getTimeHTime())

# EN_HALTFLAG - ENgettimeparam
d.printv(d.getTimeHaltFlag())

# find the lesser of the hydraulic time step length, or the time to next fill/empty
d.printv(d.getTimeNextEvent())

# EN_MAXVOLUME - ENgetnodevalue
d.printv(d.getNodeTankMaximumWaterVolume())

# Curves Info
d.getCurvesInfo().disp()

# Pump pattern
d.printv(d.getLinkPumpPatternNameID())  # EN_LINKPATTERN - ENgetlinkvalue
d.printv(d.getLinkPumpPatternIndex())

## Controls
d = epanet(inpname)
Controls = d.getControls()

## Counts
NodeCount = d.getNodeCount()
NodeTankReservoirCount = d.getNodeTankReservoirCount()
LinkCount = d.getLinkCount()
PatternCount = d.getPatternCount()
CurveCount = d.getCurveCount()
ControlRulesCount = d.getControlRulesCount()
NodeTankCount = d.getNodeTankCount()
NodeReservoirCount = d.getNodeReservoirCount()
NodeJunctionsCount = d.getNodeJunctionCount()
LinkPipeCount = d.getLinkPipeCount()
LinkPumpCount = d.getLinkPumpCount()
LinkValveCount = d.getLinkValveCount()

## Errors
error_list = list(range(6 + 1))
error_list.extend(list(range(101, 106 + 1)))
error_list.extend([110, 120, 200])
error_list.extend(list(range(202, 207 + 1)))
error_list.extend(list(range(223, 224 + 1)))
error_list.extend(list(range(250, 251 + 1)))
error_list.extend(list(range(301, 309 + 1)))
for e in error_list:
    d.printv(d.getError(e))

d.printv(d.getFlowUnits())
d.printv(d.getLinkNameID())
d.printv(d.getLinkPipeNameID())
d.printv(d.getLinkPumpNameID())
d.printv(d.getLinkValveNameID())
d.printv(d.getLinkIndex())
d.printv(d.getLinkPipeIndex())
d.printv(d.getLinkPumpIndex())
d.printv(d.getLinkValveIndex())
d.printv(d.getLinkNodesIndex())
d.printv(d.getNodesConnectingLinksID())
d.printv(d.getLinkType())
d.printv(d.getLinkTypeIndex())
d.printv(d.getLinkDiameter())
d.printv(d.getLinkLength())
d.printv(d.getLinkRoughnessCoeff())
d.printv(d.getLinkMinorLossCoeff())
d.printv(d.getLinkInitialStatus())
d.printv(d.getLinkInitialSetting())
d.printv(d.getLinkBulkReactionCoeff())
d.printv(d.getLinkWallReactionCoeff())
d.printv(d.getLinkFlows())  # This is called dynamically in a loop
d.printv(d.getLinkVelocity())
d.printv(d.getLinkHeadloss())
d.printv(d.getLinkStatus())
d.printv(d.getLinkSettings())
d.printv(d.getLinkEnergy())

d.printv(d.getNodeNameID())
d.printv(d.getNodeReservoirNameID())
d.printv(d.getNodeJunctionNameID())
d.printv(d.getNodeIndex())
d.printv(d.getNodeReservoirIndex())
d.printv(d.getNodeJunctionIndex())
d.printv(d.getNodeType())
d.printv(d.getNodeTypeIndex())
d.printv(d.getNodeElevations())
d.printv(d.getNodeBaseDemands())
d.printv(d.getNodePatternIndex())
d.printv(d.getNodeEmitterCoeff())
d.printv(d.getNodeInitialQuality())
d.printv(d.getNodeSourceQuality())
d.printv(d.getNodeSourcePatternIndex())
d.printv(d.getNodeSourceType())
d.printv(d.getNodeTankInitialLevel())

d.printv(d.getNodeActualDemand())  # This is called dynamically in a loop
d.printv(d.getNodeActualDemandSensingNodes([1, 2, 34, 25, 5]))
d.printv(d.getNodeHydraulicHead())
d.printv(d.getNodePressure())
d.printv(d.getNodeActualQuality())
d.printv(d.getNodeMassFlowRate())
# getNodeActualQualitySensingNodes Works without adding input values in list
d.printv(d.getNodeActualQualitySensingNodes([1, 2, 34, 25, 5]))

d.printv(d.getNodeTankMixingModelCode())
d.printv(d.getNodeTankMixingModelType())

d.printv(d.getNodeTankMinimumWaterVolume())
d.printv(d.getNodeTankVolumeCurveIndex())
d.printv(d.getNodeTankMinimumWaterLevel())
d.printv(d.getNodeTankMaximumWaterLevel())
d.printv(d.getNodeTankMixingFraction())
d.printv(d.getNodeTankBulkReactionCoeff())
d.printv(d.getNodeTankIndex())
d.printv(d.getNodeTankNameID())
d.printv(d.getOptionsMaxTrials())
d.printv(d.getOptionsAccuracyValue())
d.printv(d.getOptionsQualityTolerance())
d.printv(d.getOptionsEmitterExponent())
d.printv(d.getOptionsPatternDemandMultiplier())
d.printv(d.getPatternNameID())
d.printv(d.getPatternIndex())
d.printv(d.getPatternLengths())
d.printv(d.getPattern())
d.printv(d.getPatternValue(1, 12))
d.printv(d.getQualityType())
d.printv(d.getQualityCode())
d.printv(d.getQualityTraceNodeIndex())
d.printv(d.getTimeSimulationDuration())
d.printv(d.getTimeHydraulicStep())
d.printv(d.getTimeQualityStep())
d.printv(d.getTimePatternStep())
d.printv(d.getTimePatternStart())
d.printv(d.getTimeReportingStep())
d.printv(d.getTimeReportingStart())

d.printv(d.getTimeStatisticsType())
d.printv(d.getTimeStatisticsIndex())
d.printv(d.getVersion())

d.printv(d.getTimeReportingPeriods())
d.printv(d.getNodeTankMixZoneVolume())
d.printv(d.getNodeTankDiameter())
d.printv(d.getNodeTankInitialWaterVolume())

## Simulate all
d.setTimeSimulationDuration(86400)
d.getComputedHydraulicTimeSeries().disp()  # Also are included:
# obj.openHydraulicAnalysis, obj.initializeHydraulicAnalysis, obj.runHydraulicAnalysis, obj.nextHydraulicAnalysisStep,
# obj.closeHydraulicAnalysis
d.getComputedQualityTimeSeries().disp()  # Also are included: obj.openQualityAnalysis, obj.initializeQualityAnalysis,
# obj.runQualityAnalysis, obj.stepQualityAnalysisTimeLeft, obj.closeQualityAnalysis

d.addPattern('NewPat1')
d.addPattern('NewPat2', [0.8, 1.1, 1.4, 1.1, 0.8, 0.7])
d.printv(d.getPattern())

try:
    d.printv(d.getControls(1).to_dict())
    d.setControls(1, 'Link 12 OPEN AT TIME 2')
    d.printv(d.getControls(1).to_dict())
except Exception as e:
    print(e)

d.getLinkDiameter()
d.setLinkDiameter(2 * d.getLinkDiameter())
d.getLinkDiameter()

d.printv(d.getLinkLength())
d.setLinkLength(2 * d.getLinkLength())
d.printv(d.getLinkLength())

d.printv(d.getLinkRoughnessCoeff())
d.setLinkRoughnessCoeff(2 * d.getLinkRoughnessCoeff())
d.printv(d.getLinkRoughnessCoeff())

d.printv(d.getLinkMinorLossCoeff())
d.setLinkMinorLossCoeff(d.getLinkMinorLossCoeff() + 1.1)
d.printv(d.getLinkMinorLossCoeff())

d.printv(d.getLinkInitialStatus())
d.setLinkInitialStatus(0 * d.getLinkInitialStatus())
d.printv(d.getLinkInitialStatus())

linkset = d.getLinkInitialSetting()
linkset[-1] = 108
if d.LinkValveCount:
    linkset[d.LinkValveIndex - 2] = 0
d.setLinkInitialSetting(linkset)
d.printv(d.getLinkInitialSetting())

d.printv(d.getLinkBulkReactionCoeff())
d.setLinkBulkReactionCoeff(d.getLinkBulkReactionCoeff() - 0.055)
d.printv(d.getLinkBulkReactionCoeff())

d.printv(d.getLinkWallReactionCoeff())
d.setLinkWallReactionCoeff(-1.1 * d.getLinkWallReactionCoeff())
d.printv(d.getLinkWallReactionCoeff())

d.printv(d.getLinkStatus())  # dynamic
d.setLinkStatus(0 * d.getLinkStatus())
d.printv(d.getLinkStatus())

values = d.getLinkSettings()  # dynamic
values[-1] = 111
d.setLinkSettings(values)
d.printv(d.getLinkSettings())

values = d.getNodeElevations()
d.printv(values)
values[-1] = 720
d.setNodeElevations(values)
d.printv(d.getNodeElevations())

values = d.getNodeBaseDemands()
d.printv(values)
values[1][2] = 160
d.setNodeBaseDemands(values[1])  # Add the first demand category values
d.printv(d.getNodeBaseDemands()[1])

values = d.getNodeDemandPatternIndex()
d.printv(values)
values[1][1] = 2
d.setNodeDemandPatternIndex(values[1])  # Add the first pattern category values
d.printv(d.getNodePatternIndex())

values = d.getNodeBaseDemands()[1]
d.printv(values)
values[2] = 160
d.setNodeBaseDemands(values)
d.printv(d.getNodeBaseDemands())

values = d.getNodePatternIndex()
d.printv(values)
values[1] = 0
d.setNodeDemandPatternIndex(values)
d.printv(d.getNodePatternIndex())

d.unload()
d = epanet(inpname)

hyd_res_1 = d.getComputedTimeSeries()
d.printv(hyd_res_1.Pressure)

values = d.getNodeEmitterCoeff()
d.printv(values)
values[2] = 0.5
d.setNodeEmitterCoeff(values)
d.printv(d.getNodeEmitterCoeff())

values = d.getNodeInitialQuality()
d.printv(values)
values[2] = 0.6
d.setNodeInitialQuality(values)
d.printv(d.getNodeInitialQuality())

if d.getNodeTankCount():
    values = d.getNodeTankInitialLevel()
    d.printv(values)
    values[-1] = values[-1] + 10
    d.setNodeTankInitialLevel(values)
    d.printv(d.getNodeTankInitialLevel())

    values = d.getNodeTankMixingModelType()
    d.printv(values)
    d.printv(d.getNodeTankMixingModelCode())
    values[-1] = 'MIX2'
    d.setNodeTankMixingModelType(values)
    d.printv(d.getNodeTankMixingModelType())
    d.printv(d.getNodeTankMixingModelCode())
    values = d.getNodeTankMixingModelType()
    d.printv(values)
    values[-1] = 'FIFO'
    d.setNodeTankMixingModelType(values)
    d.printv(d.getNodeTankMixingModelType())
    d.printv(d.getNodeTankMixingModelCode())
    values = d.getNodeTankMixingModelType()
    d.printv(values)
    values[-1] = 'LIFO'
    d.setNodeTankMixingModelType(values)
    d.printv(d.getNodeTankMixingModelType())
    d.printv(d.getNodeTankMixingModelCode())

    values = d.getNodeTankDiameter()
    d.printv(values)
    values[-1] = 60
    d.setNodeTankDiameter(values)
    d.printv(d.getNodeTankDiameter())

    values = d.getNodeTankMinimumWaterLevel()
    d.printv(values)
    values[-1] = 10
    d.setNodeTankMinimumWaterLevel(values)
    d.printv(d.getNodeTankMinimumWaterLevel())

    values = d.getNodeTankMinimumWaterVolume()
    d.printv(values)
    values[-1] = 10
    d.setNodeTankMinimumWaterVolume(values)
    d.printv(d.getNodeTankMinimumWaterVolume())

    values = d.getNodeTankMaximumWaterLevel()
    d.printv(values)
    values[-1] = 210
    d.setNodeTankMaximumWaterLevel(values)
    d.printv(d.getNodeTankMaximumWaterLevel())

    values = d.getNodeTankMixingFraction()
    d.printv(values)
    values[-1] = 0.5  # takes values 0-1
    d.setNodeTankMixingFraction(values)
    d.printv(d.getNodeTankMixingFraction())

    values = d.getNodeTankBulkReactionCoeff()
    d.printv(values)
    values[-1] = 1
    d.setNodeTankBulkReactionCoeff(values)
    d.printv(d.getNodeTankBulkReactionCoeff())

d.printv(d.getNodeSourceType())
d.setNodeSourceType(2, 'MASS')
d.printv(d.getNodeSourceType())
d.setNodeSourceType(2, 'CONCEN')
d.printv(d.getNodeSourceType())
d.setNodeSourceType(2, 'SETPOINT')
d.printv(d.getNodeSourceType())
d.setNodeSourceType(2, 'FLOWPACED')
d.printv(d.getNodeSourceType())

values = d.getNodeSourceQuality()
d.printv(values)
values[2] = 0.5
d.setNodeSourceQuality(values)
d.printv(d.getNodeSourceQuality())

values = d.getNodeSourcePatternIndex()
d.printv(values)
values[6] = 1
d.setNodeSourcePatternIndex(values)
d.printv(d.getNodeSourcePatternIndex())

d.printv(d.getOptionsMaxTrials())
d.setOptionsMaxTrials(45)
d.printv(d.getOptionsMaxTrials())

d.printv(d.getOptionsAccuracyValue())
d.setOptionsAccuracyValue(0.015)
d.printv(d.getOptionsAccuracyValue())

d.printv(d.getOptionsQualityTolerance())
d.setOptionsQualityTolerance(0.02)
d.printv(d.getOptionsQualityTolerance())

d.printv(d.getOptionsEmitterExponent())
d.setOptionsEmitterExponent(0.55)
d.printv(d.getOptionsEmitterExponent())

d.printv(d.getOptionsPatternDemandMultiplier())
d.setOptionsPatternDemandMultiplier(1.1)
d.printv(d.getOptionsPatternDemandMultiplier())

d.printv(d.getTimeSimulationDuration())
d.setTimeSimulationDuration(86500)
d.printv(d.getTimeSimulationDuration())

d.printv(d.getTimeHydraulicStep())
d.setTimeHydraulicStep(3500)
d.printv(d.getTimeHydraulicStep())

d.printv(d.getTimeQualityStep())
d.setTimeQualityStep(250)
d.printv(d.getTimeQualityStep())

d.printv(d.getTimePatternStep())
d.setTimePatternStep(7000)
d.printv(d.getTimePatternStep())

d.printv(d.getTimePatternStart())
d.setTimePatternStart(100)
d.printv(d.getTimePatternStart())

d.printv(d.getTimeReportingStep())
d.setTimeReportingStep(3500)
d.printv(d.getTimeReportingStep())

d.printv(d.getTimeReportingStart())
d.setTimeReportingStart(200)
d.printv(d.getTimeReportingStart())

d.printv(d.getTimeStatisticsType())
d.printv(d.getTimeStatisticsIndex())
d.setTimeStatisticsType('MINIMUM')
d.printv(d.getTimeStatisticsType())
d.printv(d.getTimeStatisticsIndex())
d.setTimeStatisticsType('MAXIMUM')
d.printv(d.getTimeStatisticsType())
d.printv(d.getTimeStatisticsIndex())
d.setTimeStatisticsType('RANGE')
d.printv(d.getTimeStatisticsType())
d.printv(d.getTimeStatisticsIndex())
d.setTimeStatisticsType('AVERAGE')
d.printv(d.getTimeStatisticsType())
d.printv(d.getTimeStatisticsIndex())
d.setTimeStatisticsType('NONE')
d.printv(d.getTimeStatisticsType())
d.printv(d.getTimeStatisticsIndex())

d.printv(d.getTimeRuleControlStep())
d.setTimeRuleControlStep(100)
d.printv(d.getTimeRuleControlStep())

d.printv(d.getPattern())


d.setPattern(1, d.arange(1, 2, 0.1))

d.printv(d.getPattern())

values = d.getPattern()
d.printv(values)
values[0, :] = 3
d.setPatternMatrix(values)
d.printv(d.getPattern())

d.printv(d.getPatternValue(1, 10))
d.setPatternValue(1, 10, 1.2)
d.printv(d.getPatternValue(1, 10))

d.printv(d.getQualityType())
d.printv(d.getQualityCode())
d.setQualityType('none')
d.printv(d.getQualityCode())
d.printv(d.getQualityType())
d.setQualityType('age')
d.printv(d.getQualityType())
d.printv(d.getQualityCode())
d.setQualityType('chem', 'mg/L')
d.printv(d.getQualityType())
d.printv(d.getQualityCode())
d.setQualityType('trace', d.NodeNameID[1])
d.printv(d.getQualityType())
d.printv(d.getQualityCode())
d.saveInputFile('TEST_INP_TEMP.inp')

# Unload net
d.unload()

# %% Report files

d = epanet(inpname)
# write line in report file
# Solve hydraulics 
d.solveCompleteHydraulics()  # solves internally the hydraulics (does not return something)
# Solve quality
d.solveCompleteQuality()
d.writeLineInReportFile('Line-writting testing!!')  # Check this! at the second time is work
d.writeReport()

# Unload net
d.unload()

# Report Preparation
d = epanet(inpname)
# Compute ranges (max - min) 
d.setTimeStatisticsType('RANGE')
d.printv(d.getTimeStatisticsType())
d.setTimeStatisticsType('MINIMUM')
d.printv(d.getTimeStatisticsType())
# StatisticsType('AVERAGE')
d.setTimeStatisticsType('NONE')
d.printv(d.getTimeStatisticsType())
d.setTimeStatisticsType('MAXIMUM')
d.printv(d.getTimeStatisticsType())

d.solveCompleteHydraulics()
d.solveCompleteQuality()

# Define contents of the report
d.setReportFormatReset()
d.setReport('FILE TestReport1.txt')
d.setReport('PAGESIZE 0')
d.setReport('NODES ALL')  # /ALL/node1 node2
d.setReport('LINKS ALL')  # /ALL/link1 link2
d.setReport('PRESSURE PRECISION 1')
d.setReport('PRESSURE ABOVE 20')
d.setReport('STATUS YES')  # YES/NO/FULL
d.setReport('SUMMARY YES')  # YES/NO
d.setReport('MESSAGES YES')  # YES/NO
d.setReport('ENERGY YES')  # YES/NO
# Nodes parameters
# YES/NO/BELOW/ABOVE/PRECISION
d.setReport('ELEVATION YES')
d.setReport('DEMAND YES')
d.setReport('HEAD YES')
d.setReport('PRESSURE YES')
d.setReport('QUALITY YES')
# Links parameters
# BELOW/ABOVE/PRECISION
d.setReport('LENGTH YES')
d.setReport('DIAMETER YES')
d.setReport('FLOW YES')
d.setReport('LENGTH YES')
d.setReport('VELOCITY YES')
d.setReport('HEADLOSS YES')
d.setReport('QUALITY PRECISION 1')
d.setReport('STATUS YES')
d.setReport('SETTING YES')
d.setReport('REACTION YES')
d.setReport('F-FACTOR YES')

# Write the report to file 
d.writeReport()
report_file_string_1 = open('TestReport1.txt').read()  # create str varible

d.setReportFormatReset()
d.setReport('FILE TestReport2.txt')
d.setTimeStatisticsType('AVERAGE')
d.setReport('NODES 10')
d.setReport('HEAD YES')
d.setReport('DEMAND NO')
d.setReport('PRESSURE NO')
d.setReport('QUALITY NO')
d.writeReport()
report_file_string_2 = open('TestReport2.txt').read()  # create str varible

d.setReportFormatReset()
d.setReport('FILE TestReport3.txt')
d.setReport('NODES ALL')
d.setReport('LINKS ALL')
d.writeReport()
report_file_string_3 = open('TestReport3.txt').read()  # create str varible

d.setReportFormatReset()
d.setReport('FILE TestReport4.txt')
d.setReport('STATUS YES')  # is not appear - check
d.writeReport()
report_file_string_4 = open('TestReport4.txt').read()  # create str varible

d.setReportFormatReset()
d.setReport('FILE TestReport5.txt')
d.setTimeStatisticsType('NONE')
d.setReport('LINKS 10')
d.setReport('LINKS 11')
d.setReport('LINKS 12')
d.setReport('FLOW YES')
d.setReport('HEADLOSS NO')
d.setReport('VELOCITY NO')
d.writeReport()
report_file_string_5 = open('TestReport5.txt').read()  # create str varible

d.setReportFormatReset()
d.setReport('FILE TestReport6.txt')
d.setTimeStatisticsType('MINIMUM')
d.setReport('NODES ALL')
d.writeReport()
report_file_string_6 = open('TestReport6.txt').read()  # create str varible

# CHECK
d.setReportFormatReset()
d.setReport('FILE TestReport7.txt')
d.setTimeStatisticsType('NONE')
d.setReport('LINKS ALL')
d.writeReport()
report_file_string_7 = open('TestReport7.txt').read()  # create str varible

# unload net
d.unload()

# %% Hydraulic/Quality analysis

## Create Hydraulics file
d = epanet(inpname)
d.solveCompleteHydraulics()  # Only call this ONLY once (see ENsolveH for more details)
d.saveHydraulicFile('hydraulics.hyd')
d.useHydraulicFile('hydraulics.hyd')
d.saveHydraulicsOutputReportingFile()

# unload net
d.unload()

## Simulation Quality
d = epanet(inpname)
d.setQualityType('chem', 'mg/L')

# Solve Hydraulics (outside the loop)
# d.solveCompleteHydraulics()

# # or open hydraulics files
d.useHydraulicFile('hydraulics.hyd')

# Runs Quality Step-by-step
d.openQualityAnalysis()
d.initializeQualityAnalysis()
tleft, P, T, Q = 1, [], [], []
while tleft > 0:
    # Add code which changes something related to quality
    t = d.runQualityAnalysis()
    P.append(d.getNodePressure())
    Q.append(d.getNodeActualQuality())
    T.append(t)
    tleft = d.stepQualityAnalysisTimeLeft()
d.closeQualityAnalysis()

tstep = d.nextQualityAnalysisStep()  # 0, if analysis has finished. 

# WITH SETTIMEQUALITYSTEP
d.unload()

## Simulation Hydraulics
d = epanet(inpname)
d.setQualityType('chem', 'mg/L')

# Runs hydraulics Step-by-step
d.openHydraulicAnalysis()
d.initializeHydraulicAnalysis()
tstep, P, T, D, H, F = 1, [], [], [], [], []
while tstep > 0:
    t = d.runHydraulicAnalysis
    P.append(d.getNodePressure())
    D.append(d.getNodeActualDemand())
    H.append(d.getNodeHydraulicHead())
    F.append(d.getLinkFlows())
    T.append(t())
    tstep = d.nextHydraulicAnalysisStep()
d.closeHydraulicAnalysis()

# Unload library
d.unload()  # delete txt and temp files
d.deleteAllTemps()  # delete all temp files

print('Test finished.\n')

# Close all figures

d.plot_close()

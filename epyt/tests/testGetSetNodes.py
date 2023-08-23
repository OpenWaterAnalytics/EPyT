"""
EPANET Python Toolkit (EPyT) Test Part 3
This file is provided to ensure that all functions can be executed correctly.
Step-by-step execution. You may also use the breakpoints,
indicated with a short dash (-) on the left of each line number.
"""
from epyt import epanet

# Create EPANET object using the INP file
inpname = 'Net1.inp'  # Net1 Net2 Net3 BWSN_Network_1 L-TOWN ky1 -10
d = epanet(inpname)

# *Get Nodes Data (EXAMPLES)*
all_elevations = d.getNodeElevations()
d.printv(all_elevations)

elevationForIndex10 = d.getNodeElevations(10)
d.printv(elevationForIndex10)

elevationsSp = d.getNodeElevations([1, 5, 10])
d.printv(elevationsSp)

d.printv(d.getNodeDemandCategoriesNumber())
d.printv(d.getNodeDemandCategoriesNumber(2))

numCategories = 1
nodeindex = 2
d.printv(d.getNodeDemandPatternIndex()[numCategories])
d.printv(d.getNodeDemandPatternIndex()[numCategories][nodeindex])
d.printv(d.getNodeDemandPatternNameID()[numCategories])
d.printv(d.getNodeDemandPatternNameID()[numCategories][nodeindex])

d.printv(d.getNodeBaseDemands()[numCategories])
d.printv(d.getNodeBaseDemands()[numCategories][nodeindex])

d.printv(d.getNodePatternIndex())
d.printv(d.getNodePatternIndex(2))

d.printv(d.getNodeEmitterCoeff())
d.printv(d.getNodeEmitterCoeff(3))

d.printv(d.getNodeInitialQuality())
d.printv(d.getNodeInitialQuality(1))

d.printv(d.getNodeSourceQuality())
d.printv(d.getNodeSourceQuality(1))

d.printv(d.getNodeSourcePatternIndex())
d.printv(d.getNodeSourcePatternIndex(1))

d.printv(d.getNodeSourceTypeIndex())
d.printv(d.getNodeSourceTypeIndex(1))

d.printv(d.getNodeSourceType())
d.printv(d.getNodeSourceType(1))

# Tanks
tankInd = d.getNodeTankIndex(1)

d.printv(d.getNodeTankInitialLevel())
d.printv(d.getNodeTankInitialLevel(tankInd))

d.printv(d.getNodeTankInitialWaterVolume())
d.printv(d.getNodeTankInitialWaterVolume(tankInd))

d.printv(d.getNodeTankMixZoneVolume())
d.printv(d.getNodeTankMixZoneVolume(tankInd))

d.printv(d.getNodeTankDiameter())
d.printv(d.getNodeTankDiameter(tankInd))

d.printv(d.getNodeTankMinimumWaterVolume())
d.printv(d.getNodeTankMinimumWaterVolume(tankInd))

d.printv(d.getNodeTankVolumeCurveIndex())
d.printv(d.getNodeTankVolumeCurveIndex(tankInd))

d.printv(d.getNodeTankMinimumWaterLevel())
d.printv(d.getNodeTankMinimumWaterLevel(tankInd))

d.printv(d.getNodeTankMaximumWaterLevel())
d.printv(d.getNodeTankMaximumWaterLevel(tankInd))

d.printv(d.getNodeTankMixingFraction())
d.printv(d.getNodeTankMixingFraction(tankInd))

d.printv(d.getNodeTankBulkReactionCoeff())
d.printv(d.getNodeTankBulkReactionCoeff(tankInd))

d.printv(d.getNodeTankVolume())
d.printv(d.getNodeTankVolume(tankInd))

d.printv(d.getNodeTankMaximumWaterVolume())
d.printv(d.getNodeTankMaximumWaterVolume(tankInd))

d.printv(d.getNodeTankVolumeCurveIndex())

d.printv(d.getNodeType())
d.printv(d.getNodeType(tankInd))

d.printv(d.getNodeNameID())
d.printv(d.getNodeNameID(tankInd))

d.printv(d.getNodeCoordinates())
d.printv(d.getNodeCoordinates()['x'])
d.printv(d.getNodeCoordinates()['y'])
d.printv(d.getNodeCoordinates(2))

# Run hydraulics Step-by-step
d.openHydraulicAnalysis()
d.initializeHydraulicAnalysis()
tstep, P, T, D, H, Q = 1, [], [], [], [], []
index = 2
while (tstep > 0):
    t = d.runHydraulicAnalysis()
    D.append(d.getNodeActualDemand(index))
    H.append(d.getNodeHydraulicHead(index))
    P.append(d.getNodePressure(index))
    Q.append(d.getNodeActualQuality(index))
    T.append(t)
    tstep = d.nextHydraulicAnalysisStep()
d.closeHydraulicAnalysis()
print("Actual Demand\n")
d.printv(D)
print("Hudraulic Head\n")
d.printv(H)
print("Pressure\n")
d.printv(P)
print("Actual Quality\n")
d.printv(Q)

# Set nodes info
d.printv(d.getNodeElevations())
d.printv(d.setNodeElevations(2*d.getNodeElevations()))
d.printv(d.getNodeElevations())
d.printv(d.getNodeElevations(2))
d.setNodeElevations(2, 300)  # index,  value
d.printv(d.getNodeElevations(2))

d.printv(d.getNodeEmitterCoeff())
d.setNodeEmitterCoeff([2] * d.getNodeCount())
d.printv(d.getNodeEmitterCoeff())
d.printv(d.getNodeEmitterCoeff(2))
d.setNodeEmitterCoeff(2, 1.5)  # index,  value
d.printv(d.getNodeEmitterCoeff(2))

d.printv(d.getNodeInitialQuality())
d.setNodeInitialQuality(2*d.getNodeInitialQuality())
d.printv(d.getNodeInitialQuality())
d.printv(d.getNodeInitialQuality(2))
d.setNodeInitialQuality(2, 1.5)  # index,  value
d.printv(d.getNodeInitialQuality(2))

d.printv(d.getNodeCoordinates(2))
d.setNodeCoordinates(2, [10, 10])
d.printv(d.getNodeCoordinates(2))

d.printv(d.getNodeBaseDemands(1))
d.setNodeBaseDemands(1, 20)
d.printv(d.getNodeBaseDemands(1))

d.printv(d.getNodeDemandPatternIndex()[1])
d.setNodeDemandPatternIndex(1, 0)  # remove pattern..
d.printv(d.getNodeDemandPatternIndex()[1])

d.printv(d.getNodeSourceType())
d.setNodeSourceType(1, 'MASS')
d.setNodeSourceType(2, 'CONCEN')
d.setNodeSourceType(3, 'SETPOINT')
d.setNodeSourceType(4, 'FLOWPACED')
d.printv(d.getNodeSourceType())

d.printv(d.getNodeSourcePatternIndex())
d.setNodeSourcePatternIndex(1, 1)
d.printv(d.getNodeSourcePatternIndex())

d.printv(d.getNodeSourceQuality())
d.setNodeSourceQuality(2*d.getNodeSourceQuality())
d.printv(d.getNodeSourceQuality())
d.setNodeSourceQuality(3, 20)
d.printv(d.getNodeSourceQuality())

# Set tanks info
d.printv(d.getNodeTankInitialLevel())
d.setNodeTankInitialLevel(d.getNodeTankInitialLevel()+20)
v = d.getNodeTankInitialLevel()
d.setNodeTankInitialLevel(tankInd, v+10)
d.printv(d.getNodeTankInitialLevel())

d.printv(d.getNodeTankDiameter())
d.setNodeTankDiameter(d.getNodeTankDiameter() + 20)
d.printv(d.getNodeTankDiameter())
d.setNodeTankDiameter(tankInd, 100)
d.printv(d.getNodeTankDiameter())

d.printv(d.getNodeTankBulkReactionCoeff())
d.setNodeTankBulkReactionCoeff(d.getNodeTankBulkReactionCoeff() + 1)
d.printv(d.getNodeTankBulkReactionCoeff())
d.setNodeTankBulkReactionCoeff(tankInd, -1)
d.printv(d.getNodeTankBulkReactionCoeff())

d.printv(d.getNodeTankMaximumWaterLevel())
d.setNodeTankMaximumWaterLevel(d.getNodeTankMaximumWaterLevel() + 21)
d.printv(d.getNodeTankMaximumWaterLevel())
d.setNodeTankMaximumWaterLevel(tankInd, 200)
d.printv(d.getNodeTankMaximumWaterLevel())

d.printv(d.getNodeTankMinimumWaterLevel())
d.setNodeTankMinimumWaterLevel(d.getNodeTankMinimumWaterLevel() - 21)
n = d.getNodeTankMinimumWaterLevel(1)
d.setNodeTankMinimumWaterLevel(tankInd, n + 20)
d.printv(d.getNodeTankMinimumWaterLevel())

d.printv(d.getNodeTankMixingFraction())
d.setNodeTankMixingFraction(d.getNodeTankMixingFraction() - 0.1)
d.printv(d.getNodeTankMixingFraction())
d.setNodeTankMixingFraction(tankInd, 0.2)
d.printv(d.getNodeTankMixingFraction())

d.printv(d.getNodeTankMinimumWaterVolume())
d.setNodeTankMinimumWaterVolume(d.getNodeTankMinimumWaterVolume() + 10000)
d.printv(d.getNodeTankMinimumWaterVolume())
d.setNodeTankMinimumWaterVolume(tankInd, 20000)
d.printv(d.getNodeTankMinimumWaterVolume())

values = d.getNodeTankMixingModelType()
d.printv(d.getNodeTankMixingModelCode())
values = 'MIX2'
d.setNodeTankMixingModelType(values)
d.printv(d.getNodeTankMixingModelType())
d.printv(d.getNodeTankMixingModelCode())
d.setNodeTankMixingModelType(tankInd, 'FIFO')
d.printv(d.getNodeTankMixingModelType())
d.printv(d.getNodeTankMixingModelCode())

d.unload()

print('Test finished.\n')

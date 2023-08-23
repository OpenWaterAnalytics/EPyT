"""
EPANET Python Toolkit (EPyT) Test Part 2
This file is provided to ensure that all functions can be executed correctly.
Step-by-step execution. You may also use the breakpoints,
indicated with a short dash (-) on the left of each line number.
"""
from epyt import epanet

# Create EPANET object using the INP file
inpname = 'Net1.inp'  # Net1 Net2 Net3 BWSN_Network_1 L-TOWN ky1 -10
d = epanet(inpname)

# *Get Links Data (EXAMPLES)*
all_diameters = d.getLinkDiameter()
d.printv(all_diameters)

diameterForIndex10 = d.getLinkDiameter(10)
d.printv(diameterForIndex10)

all_diameters2 = d.getLinkDiameter()
d.printv(all_diameters2)

diametersSp = d.getLinkDiameter([1, 5, 10])
d.printv(diametersSp)

# similar..
d.printv(d.getLinkLength())
d.printv(d.getLinkLength(5))

d.printv(d.getLinkRoughnessCoeff())
d.printv(d.getLinkRoughnessCoeff(3))

d.printv(d.getLinkMinorLossCoeff())
d.printv(d.getLinkMinorLossCoeff(2))

d.printv(d.getLinkInitialStatus())
d.printv(d.getLinkInitialStatus(2))

d.printv(d.getLinkInitialSetting())
d.printv(d.getLinkInitialSetting(2))

d.printv(d.getLinkBulkReactionCoeff())
d.printv(d.getLinkBulkReactionCoeff(2))

d.printv(d.getLinkWallReactionCoeff())
d.printv(d.getLinkWallReactionCoeff(2))

d.printv(d.getLinkType())
d.printv(d.getLinkType(13))

d.printv(d.getLinkTypeIndex())
d.printv(d.getLinkTypeIndex(list(range(5, d.getLinkCount()))))

# Runs hydraulics Step-by-step
d.openHydraulicAnalysis()
d.initializeHydraulicAnalysis()
tstep, T, V, H, F, Q = 1, [], [], [], [], []
index = 1
while tstep > 0:
    t = d.runHydraulicAnalysis()
    V.append(d.getLinkVelocity(index))
    H.append(d.getLinkHeadloss(index))
    F.append(d.getLinkFlows(index))
    Q.append(d.getLinkQuality())
    T.append(t)
    tstep = d.nextHydraulicAnalysisStep()
d.closeHydraulicAnalysis()

d.printv(F)
d.printv(V)
d.printv(H)
d.printv(Q)

d.printv(d.getLinkStatus())
d.printv(d.getLinkStatus(2))

d.printv(d.getLinkSettings())
d.printv(d.getLinkSettings(2))

# Set links info
d.printv(d.getLinkDiameter())
d.setLinkDiameter(2 * d.getLinkDiameter())
d.printv(d.getLinkDiameter())
d.printv(d.getLinkDiameter(2))
d.setLinkDiameter(2, 200)  # index,  value
d.printv(d.getLinkDiameter(2))

d.printv(d.getLinkLength())
d.setLinkLength(2 * d.getLinkLength())
d.printv(d.getLinkLength())
d.printv(d.getLinkLength(2))
d.setLinkLength(2, 500)  # index,  value
d.printv(d.getLinkLength(2))

d.printv(d.getLinkRoughnessCoeff())
d.setLinkRoughnessCoeff(2 * d.getLinkRoughnessCoeff())
d.printv(d.getLinkRoughnessCoeff())
d.printv(d.getLinkRoughnessCoeff(2))
d.setLinkRoughnessCoeff(2, 150)  # index,  value
d.printv(d.getLinkRoughnessCoeff(2))

d.printv(d.getLinkMinorLossCoeff())
d.setLinkMinorLossCoeff(d.getLinkMinorLossCoeff() + 1.1)
d.printv(d.getLinkMinorLossCoeff())
d.printv(d.getLinkMinorLossCoeff(2))
d.setLinkMinorLossCoeff(2, 1.01)  # index,  value
d.printv(d.getLinkMinorLossCoeff(2))

d.printv(d.getLinkInitialStatus())
d.setLinkInitialStatus(0 * d.getLinkInitialStatus())
d.printv(d.getLinkInitialStatus())
d.printv(d.getLinkInitialStatus(2))
d.setLinkInitialStatus(2, 1)
d.printv(d.getLinkInitialStatus(2))

d.printv(d.getLinkBulkReactionCoeff())
d.setLinkBulkReactionCoeff(d.getLinkBulkReactionCoeff() - 0.055)
d.printv(d.getLinkBulkReactionCoeff())
d.printv(d.getLinkBulkReactionCoeff(1))
d.setLinkBulkReactionCoeff(1, 0.2)
d.printv(d.getLinkBulkReactionCoeff(1))

d.printv(d.getLinkWallReactionCoeff())
d.setLinkWallReactionCoeff(-1.1 * d.getLinkWallReactionCoeff())
d.printv(d.getLinkWallReactionCoeff())
d.printv(d.getLinkWallReactionCoeff(2))
d.setLinkWallReactionCoeff(2, -2)
d.printv(d.getLinkWallReactionCoeff(2))

linkset = d.getLinkInitialSetting()
if d.getLinkValveCount():
    linkset[d.getLinkValveIndex()-1] = 0
d.setLinkInitialSetting(linkset * 10)
d.printv(d.getLinkInitialSetting())
d.printv(d.getLinkInitialSetting(2))
d.setLinkInitialSetting(2, 10)
d.printv(d.getLinkInitialSetting(2))

d.printv(d.getLinkStatus())  # dynamic
d.setLinkStatus(0 * d.getLinkStatus())
d.printv(d.getLinkStatus())
d.printv(d.getLinkStatus(2))
d.setLinkStatus(2, 1)
d.printv(d.getLinkStatus(2))

d.printv(d.getLinkSettings())  # dynamic
d.setLinkSettings(d.getLinkSettings() + 10)
d.printv(d.getLinkSettings())
d.printv(d.getLinkSettings(2))
d.setLinkSettings(2, 121)
d.printv(d.getLinkSettings(2))

# Unload library
d.unload()

print('Test finished.\n')

"""
EPANET Python Toolkit (EPyT) Test Part 4
This file is provided to ensure that all functions can be executed correctly.
Step-by-step execution. You may also use the breakpoints.
"""

import matplotlib.pyplot as plt
from epyt import epanet

# Create EPANET object using the INP file
d = epanet('Net1.inp')  # Net1 Net2 Net3 BWSN_Network_1

if d.getLinkPumpCount():
    d.printv(d.getLinkPumpHeadCurveIndex())
    indexCurve = d.addCurve('NewCur2', [[1500, 400], [1800, 200]])
    fromNode = d.getNodeNameID(2)
    toNode = d.getNodeNameID(6)
    index = d.addLinkPump('Pump', fromNode, toNode)
    d.setLinkPumpHeadCurveIndex(index, indexCurve)
    [HeadCurveIndex, PumpIndex] = d.getLinkPumpHeadCurveIndex()
    d.deleteLink(index)

# %% Add/delete Node -
# Select the position of the node to be added/deleted 
# by clicking on the plot
d.plot(nodesID=True)
print('\nAdd a junction')
d.printv(d.getNodeNameID())
d.printv(d.getNodeJunctionCount())
xy = plt.ginput(1)[0]
index = d.addNodeJunction('Junction')
d.setNodeCoordinates(index, [xy[0], xy[1]])
d.printv(d.getNodeNameID())
d.printv(d.getNodeJunctionCount())
d.plot(nodesID=True)

# %%
print('\nAdd a reservoir')
d.getNodeReservoirCount()
xy = plt.ginput(1)[0]
index = d.addNodeReservoir('Reservoir')
d.setNodeCoordinates(index, [xy[0], xy[1]])
d.printv(d.getNodeNameID())
d.printv(d.getNodeReservoirCount())
d.plot(nodesID=True)

# %%
print('\nAdd a tank')
d.getNodeTankCount()
xy = plt.ginput(1)[0]
index = d.addNodeTank('Tank')
d.setNodeCoordinates(index, [xy[0], xy[1]])
d.printv(d.getNodeNameID())
d.printv(d.getNodeTankCount())
d.plot(nodesID=True)

# %%
print('\nDelete a node')
d.getNodeCount()
d.deleteNode('Junction')
d.printv(d.getNodeNameID())
d.printv(d.getNodeCount())
d.plot(nodesID=True)

# %% Add/delete Link
print('\nAdd a cv pipe')
d.printv(d.getLinkNameID())
d.printv(d.getLinkPipeCount())
fromNode = d.getNodeNameID(2)
toNode = d.getNodeNameID(6)
index = d.addLinkPipeCV('CVPipe', fromNode, toNode)
d.printv(d.getLinkNameID())
d.printv(d.getLinkPipeCount())
d.printv(d.getLinkType())
d.plot(linksID=True)
d.deleteLink(index)
d.plot(linksID=True)

# %%
print('\nAdd a pipe')
d.printv(d.getLinkNameID())
d.printv(d.getLinkPipeCount())
fromNode = d.getNodeNameID(2)
toNode = d.getNodeNameID(6)
index = d.addLinkPipe('Pipe', fromNode, toNode)
d.printv(d.getLinkNameID())
d.printv(d.getLinkPipeCount())
d.deleteLink(index)

# %%
print('\nAdd a pump')
d.printv(d.getLinkPumpCount())
fromNode = d.getNodeNameID(2)
toNode = d.getNodeNameID(6)
index = d.addLinkPump('Pump', fromNode, toNode)
d.printv(d.getLinkNameID())
d.printv(d.getLinkPumpCount())
d.printv(d.getLinkType())
d.deleteLink(index)

# %%
# similar
print('\nAdd a valve')
index = d.addLinkValvePRV('PRV-V', fromNode, toNode)
index1 = d.addLinkValveFCV('FCV', fromNode, toNode)
index2 = d.addLinkValveGPV('GPV', fromNode, toNode)
index3 = d.addLinkValvePBV('PBV', fromNode, toNode)
index4 = d.addLinkValvePSV('PSV', fromNode, toNode)
index5 = d.addLinkValveTCV('TCV', fromNode, toNode)
d.printv(d.getLinkType())

# %%
# Unload library
d.unload()

# Close all figures
# plt.close("all")

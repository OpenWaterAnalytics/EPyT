"""
EPANET Python Toolkit (EPyT) Test Part 4
This file is provided to ensure that all functions can be executed correctly.
Step-by-step execution. You may also use breakpoints.
"""
from epyt import epanet

# Create EPANET object using the INP file
d = epanet('Net1.inp')  # Net1 Net2 Net3 BWSN_Network_1 L-TOWN ky1 -10

# Print properties
d.printv(dir(d))

# Counts
counts = d.getCounts()  # Retrieves the number of all network components
d.printv(counts.Curves)
d.printv(counts.Junctions)
d.printv(counts.Links)
d.printv(counts.Nodes)  # Retrieves the number of nodes
d.printv(counts.Patterns)
d.printv(counts.Pipes)
d.printv(counts.Pumps)
d.printv(counts.Reservoirs)
d.printv(counts.RuleBasedControls)
d.printv(counts.SimpleControls)  # Retrieves the number of simple controls
d.printv(counts.Tanks)
d.printv(counts.Valves)

d.printv(d.getNodeCount())
d.printv(d.getNodeTankReservoirCount())
d.printv(d.getLinkCount())  # Retrieves the number of links.
d.printv(d.getPatternCount())
d.printv(d.getCurveCount())  # Retrieves the number of curves.
d.printv(d.getControlRulesCount())  # Retrieves the number of control rules
d.printv(d.getNodeTankCount())
d.printv(d.getNodeReservoirCount())
d.printv(d.getNodeJunctionCount())
d.printv(d.getLinkPipeCount())  # Retrieves the number of pipes.
d.printv(d.getLinkPumpCount())  # Retrieves the number of pumps.
d.printv(d.getLinkValveCount())

# Return error message
error = 250
d.printv(d.getError(error))  # Retrieves the text of the message associated with a particular error or warning code.

# Get link quality (dynamic - check example EX2_Hydraulic_analysis)
d.printv(d.getLinkQuality())  # Retrieves the value of all link quality
d.printv(d.getLinkQuality(1))  # Retrieves the value of the first link quality

# Get link type / type index
d.printv(d.getLinkType())  # Retrieves the link-type code for all links
d.printv(d.getLinkType(1))  # Retrieves the link-type code for the first link

d.printv(d.getLinkTypeIndex())  # Retrieves the link-type code for all links
d.printv(d.getLinkTypeIndex(1))  # Retrieves the link-type code for the first link
d.printv(d.getLinkTypeIndex([2, 3]))  # Retrieves the link-type code for the second and third links

# Get link diameter
d.printv(d.getLinkDiameter())  # Retrieves the value of all link diameters
d.printv(d.getLinkDiameter(1))  # Retrieves the value of the first link diameter
d.printv(d.getLinkDiameter([1, 2]))  # Retrieves the value of the second and third link diameter

# Get link length
d.printv(d.getLinkLength())  # Retrieves the value of all link lengths
d.printv(d.getLinkLength(1))  # Retrieves the value of the first link length

# Get link roughness coeff.
d.printv(d.getLinkRoughnessCoeff())  # Retrieves the value of all link roughness coefficients
d.printv(d.getLinkRoughnessCoeff(5))  # Retrieves the value of the first link roughness coefficient

# Get minor loss coeff.
d.printv(d.getLinkMinorLossCoeff())  # Retrieves the value of all link minor loss coefficients
d.printv(d.getLinkMinorLossCoeff(1))  # Retrieves the value of the first link minor loss coefficient

# Get initial status
d.printv(d.getLinkInitialStatus())  # Retrieves the value of all link initial status
d.printv(d.getLinkInitialStatus(1))  # Retrieves the value of the first link initial status

# Get initial setting
d.printv(d.getLinkInitialSetting())  # Retrieves the value of all link initial settings
d.printv(d.getLinkInitialSetting(1))  # Retrieves the value of the first link initial setting

# Get link bulk and wall reaction coeff.
d.printv(d.getLinkBulkReactionCoeff())  # Retrieves the value of all link bulk chemical reaction coefficient
d.printv(d.getLinkBulkReactionCoeff(1))  # Retrieves the value of the first link bulk chemical reaction coefficient
d.printv(d.getLinkWallReactionCoeff())  # Retrieves the value of all pipe wall chemical reaction coefficient
d.printv(d.getLinkWallReactionCoeff(1))  # Retrieves the value of the first pipe wall chemical reaction coefficient

# Get link pump pattern index
d.printv(d.getLinkPumpPatternIndex())  # Retrieves the speed time pattern index of all pumps
d.printv(d.getLinkPumpPatternIndex(1))  # Retrieves the speed time pattern index of the 1st pump
d = epanet('Richmond_standard.inp')
d.printv(d.getLinkPumpPatternIndex([1, 2]))  # Retrieves the speed time pattern index of the first 2 pumps
pumpIndex = d.getLinkPumpIndex()
d.printv(d.getLinkPumpPatternIndex(pumpIndex))  # Retrieves the speed time pattern index of the pumps given their
# indices

# Get link pump state
d.printv(d.getLinkPumpState())  # Retrieves the current computed pump state for all links
d.printv(d.getLinkPumpState(1))  # Retrieves the current computed pump state for the first link

# Get link pump type (CONSTANT_HORSEPOWER, POWER_FUNCTION, CUSTOM)
d.printv(d.getLinkPumpType())  # Retrieves the type of a pump.
d.printv(d.getLinkPumpTypeCode())  # Retrieves all the pump type codes
d.printv(d.getLinkPumpTypeCode()[0])  # Retrieves the first pump type code

# Get link flows/velocity/headloss/status/setting/energy/quality (dynamic - check example EX2_Hydraulic_analysis)
d.printv(d.getLinkFlows())  # Retrieves the current computed flow rate for all links
d.printv(d.getLinkFlows(1))  # Retrieves the current computed flow rate for the first link
d.printv(d.getLinkVelocity())  # Retrieves the current computed flow velocity for all links
d.printv(d.getLinkVelocity(1))  # Retrieves the current computed flow velocity for the first link
d.printv(d.getLinkHeadloss())  # Retrieves the current computed head loss for all links
d.printv(d.getLinkHeadloss(1))  # Retrieves the current computed head loss for the first link
d.printv(d.getLinkStatus())  # Retrieves the current link status for all links
d.printv(d.getLinkStatus(1))  # Retrieves the current link status for the first link
d.printv(d.getLinkSettings())  # Retrieves the current values of settings for all links
d.printv(d.getLinkSettings(1))  # Retrieves the current value of setting for the first link
d.printv(d.getLinkEnergy())  # Retrieves the current computed pump energy usage for all links
d.printv(d.getLinkEnergy(1))  # Retrieves the current computed pump energy usage for the first link
d.printv(d.getLinkActualQuality())  # Retrieves the current computed link quality for all links
d.printv(d.getLinkActualQuality(1))  # Retrieves the current computed link quality for the first link

# Get link name ID & index
d.printv(d.getLinkNameID())  # Retrieves the ID's of all links

linkIndex = 1
d.printv(d.getLinkNameID(linkIndex))  # Retrieves the ID of the link with index = 1

linkIndices = [1, 2, 3]
d.printv(d.getLinkNameID(linkIndices))  # Retrieves the IDs of the links with indices = 1, 2, 3

d.printv(d.getLinkIndex())  # Retrieves the indices of all links

linkID = d.getLinkNameID()[0]
d.printv(d.getLinkIndex(linkID))  # Retrieves the index of the 1st link given it's ID

linkID = d.getLinkNameID()[0:3]
d.printv(d.getLinkIndex(linkID))  # Retrieves the indices of the first 3 links given their ID

# Get link pipe name ID & index
d.printv(d.getLinkPipeIndex())

d.printv(d.getLinkPipeNameID())  # Retrieves the ID's of all pipes
d.printv(d.getLinkPipeNameID()[0])  # Retrieves the ID of the 1st pipe
d.printv(d.getLinkPipeNameID()[0:3])  # Retrieves the ID of the first 3 pipes

# Get link pump info
d.printv(d.getLinkPumpEfficiency())  # Retrieves the current computed pump efficiency for all links
d.printv(d.getLinkPumpEfficiency(1))  # Retrieves the current computed pump efficiency for the first link
d.printv(d.getLinkPumpECost())  # Retrieves the average energy price of all pumps
d.printv(d.getLinkPumpECost(1))  # Retrieves the average energy price of the 1st pump

pIndex = 950
pIndices = d.getLinkPumpIndex()
d.printv(d.getLinkPumpECost(pIndex))  # Retrieves the average energy price of the pump with link index 950

d.printv(d.getLinkPumpECurve())  # Retrieves the efficiency v. flow curve index of all pumps
d.printv(d.getLinkPumpECurve(1))  # Retrieves the efficiency v. flow curve index of the 1st pump
d.printv(d.getLinkPumpECurve([1, 2]))  # Retrieves the efficiency v. flow curve index of the first 2 pumps

pIndex = 950
pIndices = d.getLinkPumpIndex()
d.printv(d.getLinkPumpECurve(pIndex))

d.printv(d.getLinkPumpEPat())  # Retrieves the energy price time pattern index of all pumps
d.printv(d.getLinkPumpEPat(1))  # Retrieves the energy price time pattern index of the 1st pump
d.printv(d.getLinkPumpEPat([1, 2]))  # Retrieves the energy price time pattern index of the first 2 pumps

pIndices = d.getLinkPumpIndex()
d.printv(d.getLinkPumpEPat(pIndex))  # Retrieves the energy price time pattern index of pump with link index 950

d.printv(d.getLinkPumpHCurve())  # Retrieves the head v. flow curve index of all pumps
d.printv(d.getLinkPumpHCurve(1))  # Retrieves the head v. flow curve index of the 1st pump
d.printv(d.getLinkPumpHCurve([1, 2]))  # Retrieves the head v. flow curve index of the first 2 pumps

pIndex = 950
pIndices = d.getLinkPumpIndex()
d.printv(d.getLinkPumpHCurve(pIndex))

d.printv(d.getLinkPumpIndex())  # Retrieves the indices of all pumps
d.printv(d.getLinkPumpIndex(1))  # Retrieves the index of the 1st pump
d.printv(d.getLinkPumpIndex([1, 2]))  # Retrieves the indices of the first 2 pumps

d.printv(d.getLinkPumpNameID())  # Retrieves the ID's of all pumps
d.printv(d.getLinkPumpNameID()[0])  # Retrieves the ID of the 1st pump

# Unload library      
d.unload()

d = epanet('Net3_trace.inp')

# Get pump patterns
d.printv(d.getLinkPumpNameID()[0:2])  # Retrieves the ID of the first 2 pumps
d.printv(d.getLinkPumpPatternNameID())  # Retrieves the pattern name ID of all pumps
d.printv(d.getLinkPumpPatternNameID(1))  # Retrieves the pattern name ID of the 1st pump
d.printv(d.getLinkPumpPatternNameID([1, 2]))  # Retrieves the pattern name ID of the first 2 pumps

# Unload library
d.unload()

d = epanet('Richmond_standard.inp')

# Get Link pump power
d.printv(d.getLinkPumpPower())  # Retrieves the constant power rating of all pumps
d.printv(d.getLinkPumpPower(1))  # Retrieves the constant power rating of the 1st pump
d.printv(d.getLinkPumpPower([1, 2]))  # Retrieves the constant power rating of the first 2 pumps

pumpIndex = d.getLinkPumpIndex()
d.printv(d.getLinkPumpPower(pumpIndex))  # Retrieves the constant power rating of the pumps given their indices

# Get link valve name ID & index
d.printv(d.getLinkValveNameID())  # Retrieves the ID's of all valves
d.printv(d.getLinkValveNameID()[0])  # Retrieves the ID of the 1st valve
d.printv(d.getLinkValveNameID()[0:3])  # Retrieves the ID of the first 3 valves

# Unload library     
d.unload()

d = epanet('Anytown.inp')

# Get link vertices
d.printv(d.getLinkVertices())  # Retrieves the vertices coordinates (x,y) of all links
d.printv(d.getLinkVertices(31))  # Retrieves the vertices coordinates (x,y) of  link with index 31
xVert = d.getLinkVertices(31)['x']  # Retrieves the first vertex coordinate x of link with index 31
d.printv(xVert[31])

# Get Link Vertices Count
d.printv(d.getLinkVerticesCount())  # Retrieves the number of vertices per link

link_id = '2'
d.printv(d.getLinkVerticesCount(link_id))  # Retrieves the number of vertices number of link '2'

link_index = 31
d.printv(d.getLinkVerticesCount(link_index))  # Retrieves the number of vertices of link 31

# Unload library
d.unload()

d = epanet('Richmond_standard.inp')

# Get Node Elevations
d.printv(d.getNodeElevations())  # Retrieves the value of all node elevations
d.printv(d.getNodeElevations(1))  # Retrieves the value of the first node elevation
d.printv(d.getNodeElevations([4, 5, 6]))  # Retrieves the value of the 5th to 7th node elevations

# Unload library      
d.unload()

d = epanet('Net1.inp')

# Get node name ID
d.printv(d.getNodeNameID())  # Retrieves the ID label of all nodes
d.printv(d.getNodeNameID(1))  # Retrieves the ID label of the first node
junctionIndex = d.getNodeJunctionIndex()
d.printv(d.getNodeNameID(junctionIndex))  # Retrieves the ID labels of all junctions give their indices

# Get node pattern index
d.printv(d.getNodePatternIndex())  # Retrieves the value of all node demand pattern indices
d.printv(d.getNodePatternIndex(1))  # Retrieves the value of the first node demand pattern index
d.printv(d.getNodePatternIndex([1, 2, 3]))  # Retrieves the value of the 1,2,3 nodes demand pattern index


# Get node type (junction, reservoir, tank)/ index type
d.printv(d.getNodeType())  # Retrieves the node-type code for all nodes
d.printv(d.getNodeType(1))  # Retrieves the node-type code for the first node
d.printv(d.getNodeType([10, 11]))  # Retrieves the node-type code for the tenth and eleventh nodes

d.printv(d.getNodeTypeIndex())  # Retrieves the node-type code for all nodes
d.printv(d.getNodeTypeIndex(1))  # Retrieves the node-type code for the first node

# Unload library
d.unload()

d = epanet('Net2.inp')

# Get pattern name ID
d.printv(d.getPatternNameID())  # Retrieves the IDs of all the patterns
d.printv(d.getPatternNameID(1))  # Retrieves the ID of the 1st pattern
d.printv(d.getPatternNameID([1, 2]))  # Retrieves the IDs of the first 2 patterns/ error for Net1

# Get / Set link diameters
d.printv(d.getLinkDiameter())  # Retrieves the diameters of all links
index_pipe = 1
diameter = 20
d.setLinkDiameter(index_pipe, diameter)  # Sets the diameter of the 1st pipe
d.printv(d.getLinkDiameter())

index_pipes = [1, 2]
diameters = [20, 25]
d.setLinkDiameter(index_pipes, diameters)  # Sets the diameters of the first 2 pipes
d.printv(d.getLinkDiameter(index_pipes))

diameters = d.getLinkDiameter()
diameters = diameters * 1.5
d.setLinkDiameter(diameters)  # Sets the diameters of all the links
d.printv(d.getLinkDiameter())

# Get / Set link lengths
index_pipe = 1
d.printv(d.getLinkLength(index_pipe))  # Retrieves the length of the 1st link

length_pipe = 100
d.setLinkLength(index_pipe, length_pipe)  # Sets the length of the 1st link
d.printv(d.getLinkLength(index_pipe))

lengths = d.getLinkLength()  # Retrieves the lengths of all the links
d.printv(lengths)
lengths_new = lengths * 1.5
d.setLinkLength(lengths_new)  # Sets the new lengths of all links
d.printv(d.getLinkLength())

# Get / Set elevations
index_node = 1
d.printv(d.getNodeElevations(index_node))  # Retrieves the elevation of the 1st node
elev = 500
d.setNodeElevations(index_node, elev)  # Sets the elevation of the 1st node
d.printv(d.getNodeElevations(index_node))

elevs = d.getNodeElevations()  # Retrieves the elevations of all the nodes
d.printv(elevs)
elevs_new = elevs + 100
d.setNodeElevations(elevs_new)  # Sets the elevations of all nodes
d.printv(d.getNodeElevations())

# Unload library
d.unload()

print('Test finished.\n')

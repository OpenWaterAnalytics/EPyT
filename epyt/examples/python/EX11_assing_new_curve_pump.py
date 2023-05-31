""" Assings a new curve to a specific pump.

    This example contains:
      Load a network.
      Add new curve in the network.
      Get pump index.
      Get head curve index.
      Assing new curve index on the specific pump.
      Unload library.

"""
from epyt import epanet

# Load a network.
d = epanet('L-TOWN.inp')

# Add new curve in the network.
indexCurve = d.addCurve('NewCurve', [1800, 300], [1500, 500])

# Get pump index.
pumpIndex = d.getLinkPumpIndex(1)

# Get head curve index.
[HeadCurveIndex, PumpIndex] = d.getLinkPumpHeadCurveIndex()

print('Head Curve Index: ' + str(HeadCurveIndex))
print('On pump index: ' + str(PumpIndex))

# Assing new curve index on the specific pump.
d.setLinkPumpHeadCurveIndex(pumpIndex, indexCurve)
print('\nAssign new curve to pump: ' + str(PumpIndex) + '\n\n')
[HeadCurveIndex, PumpIndex] = d.getLinkPumpHeadCurveIndex()
print('New Head Curve Index: ' + str(HeadCurveIndex))
print('On pump index: ' + str(PumpIndex))

print('\n')

# Unload library.
d.unload()

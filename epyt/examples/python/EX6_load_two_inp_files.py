"""  Loads 2 different networks.
 
    This example contains:
       Load networks.
       Print elevations for the two networks.
       Plot networks.
       Unload libraries.
"""
from epyt import epanet

# Load networks
d1 = epanet('Net1.inp', ph=True)
d2 = epanet('Net2.inp', ph=True)

# Close any open figures
d1.plot_close()

# Print elevations for the two networks.
print('Net1 - Elevations:')
print('------------------')
print(d1.getNodeElevations())
print('Net2 - Elevations:')
print('------------------')
print(d2.getNodeElevations())

d1.setNodeElevations(1, 750.22)
d2.setNodeElevations(2, 200.33)

print('Net1 - Elevations:')
print('------------------')
print(d1.getNodeElevations())
print('Net2 - Elevations:')
print('------------------')
print(d2.getNodeElevations())

# Plot networks.
d1.plot()
d2.plot()

d1.plot_show()

# Unload libraries.
d1.unload()
d2.unload()

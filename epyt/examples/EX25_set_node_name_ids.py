""" Set node name IDs
    This example contains:
        Load a network.
        Get node name ids.
        Set new node name ids.
        Get new node name ids.
        Unload library.
"""
from epyt import epanet

# Load network
d = epanet('Net1.inp')

print(f'\n Node name ids: \n {d.getNodeNameID()}')

# Set your prefix 
junction_prefix = 'J'
reservoir_prefix = 'R'
tank_prefix = 'T'

# Update node names 
for i in d.getNodeJunctionIndex():
    d.setNodeNameID(i, junction_prefix + '-' + str(i))

for i in d.getNodeReservoirIndex():
    d.setNodeNameID(i, reservoir_prefix + '-' + str(i))

for i in d.getNodeTankIndex():
    d.setNodeNameID(i, tank_prefix + '-' + str(i))

print(f'\n New Node name ids: \n {d.getNodeNameID()} \n')

d.unload()

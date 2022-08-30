""" Visualises/plots time series for node pressures, water velocity and water flow.
 
    This example contains:
        Load a network.
        Hydraulic analysis using ENepanet binary file.
        Change time-stamps from seconds to hours.
        Plot node pressures for specific nodes.
        Plot water velocity for specific links.
        Plot water flow for specific links.
        Unload library.
"""
# Run hydraulic analysis of a network
from epyt import epanet

# Load a network
d = epanet('Net1.inp')

# Close any open figures
d.plot_close()

# Hydraulic analysis using binary file
# (This function ignore events)
hyd_res = d.getComputedTimeSeries()

# Change time-stamps from seconds to hours
hrs_time = hyd_res.Time / 3600

# Plot node pressures for specific nodes 
node_indices = [1, 3, 5]
node_names = d.getNodeNameID(node_indices)
for index in node_indices:
    d.plot_ts(X=hrs_time, Y=hyd_res.Pressure[:, index - 1],
              title=f'Pressure for the node id {d.getNodeNameID(index)}',
              xlabel='Time (hrs)', ylabel=f'Pressure ({d.units.NodePressureUnits})',
              marker=None)

# Plot water velocity for specific links
link_indices = [4, 8, 10]
link_names = d.getNodeNameID(link_indices)
for index in link_indices:
    d.plot_ts(X=hrs_time, Y=hyd_res.Velocity[:, index - 1],
              title=f'Velocity for the link id {d.getLinkNameID(index)}',
              xlabel='Time (hrs)', ylabel=f'Velocity ({d.units.LinkVelocityUnits})',
              marker=None)

# Plot water flow for specific links
link_indices = [2, 3, 9]
for index in link_indices:
    d.plot_ts(X=hrs_time, Y=hyd_res.Flow[:, index - 1],
              title=f'Flow for the link id {d.getLinkNameID(index)}',
              xlabel='Time (hrs)', ylabel=f'Flow ({d.units.LinkFlowUnits})',
              marker=None)

d.plot_show()

# Unload library
d.unload()

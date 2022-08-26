""" Plot net attributes.
    
    This example contains:
        Load a network.
        Plot node elevations.
        Run complete analysis.
        Plot Pressure at hour 10.
        Plot Flow at hour 10.
        Plot Pressure at hour 10 with printed values.
        Plot Flow at hour 10 with printed values.
        Unload library.

"""
from epyt import epanet

# Load Network Net1
d = epanet('Net1.inp')

# Close any open figures
d.plot_close()

# Plot Node Elevations
Elevations = d.getNodeElevations()
d.plot(elevation=True, colorbar='Oranges')

# Plot Pressure at hour 10
res = d.getComputedTimeSeries()
d.plot(pressure=res.Pressure[10, :], title='Pressure at hour 10')

# Plot Flow at hour 10
d.plot(flow=res.Flow[10, :])

# Plot Pressure at hour 10 with printed values
d.plot(pressure=res.Pressure[10, :], pressure_text=True)

# Plot Flow at hour 10 with printed values
d.plot(flow=res.Flow[11, :], flow_text=True)

# Unload library
d.unload()
d.plot_show()

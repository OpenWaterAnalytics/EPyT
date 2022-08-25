""" Plots the network topology.

    This example contains:
      Load a network.
      Plot network topology.
      Plot node IDs.
      Plot links IDs.
      Plot node indices.
      Plot link indices.
      Plot specific nodes ID
      Plot specific nodes index
      Plot specific links ID
      Plot specific links index
      Highlight specific links.
      Highlight specific nodes.
      Plot only links.
      Plot only nodes.
      Hide legend.
      Unload library.
      
"""
from epyt import epanet

# Load a network
d = epanet('Net1.inp')

# Close any open figures
d.plot_close()

# Plot network topology
d.plot()

# Plot nodes IDs
d.plot(nodesID=True)

# Plot links IDs
d.plot(linksID=True)

# Plot node indices
d.plot(nodesindex=True)

# Plot link indices
d.plot(linksindex=True)

# Plot specific nodes ID
d.plot(nodesID=['10', '11', '9'])

# Plot specific nodes index
d.plot(nodesindex=[1, 2, 10])

# Plot specific links ID
d.plot(linksID=['111', '122', '9'])

# Plot specific links index
d.plot(linksindex=[1, 2, 10])

# Highlight specific links
d.plot(highlightlink='10')

# Highlight specific nodes 
d.plot(highlightnode=['10', '32'])

# Plot only nodes
d.plot(point=True)

# Plot only links
d.plot(line=True)

# Hide legend
d.plot(legend=False)

# Unload library
d.plot_show()
d.unload()
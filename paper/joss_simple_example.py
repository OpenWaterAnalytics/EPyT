from epyt import epanet

# Load EPANET Input File
G = epanet('Net1.inp')

# Lists all available functions and properties
dir(G)

# Retrieve some examples for the function
help(G.getNodeElevations)

# Retrieve Link diameters
diameters = G.getLinkDiameter()

# Retrieve Node elevations
elevations = G.getNodeElevations()

# Link diameter for links 2 & 10
diameters = G.getLinkDiameter([2, 10])
# Update the link 10 diameter from 100 to 90
G.setLinkDiameter(10, 90)
# Retrieve the diameter of link 10
G.getLinkDiameter(10)

# Solve hydraulics in library
H = G.getComputedHydraulicTimeSeries()
# Solve quality dynamics in library
Q = G.getComputedQualityTimeSeries()
# Solve all dynamics in library, create a binary file to store the computed values
R = G.getComputedTimeSeries()

# Plot link flows and quality
hrs_time = R.Time / 3600
link_indices = [1, 3, 5, 10]
link_names = G.getLinkNameID(link_indices)
G.plot_ts(X=hrs_time, Y=R.Flow[:, link_indices],
          title=f'Flow, Link IDs: {link_names}', figure_size=[4, 3], legend_location='best',
          xlabel='Time (hrs)', ylabel=f'Flow ({G.units.LinkFlowUnits})',
          marker=None, labels=link_names, save_fig=True, filename='figures/paper_flows')
G.plot_ts(X=hrs_time, Y=R.LinkQuality[:, link_indices],
          title=f'Quality, Link IDs: {link_names}', legend_location='best',
          xlabel='Time (hrs)', ylabel=f'Quality', figure_size=[4, 3],
          marker=None, labels=link_names, save_fig=True, filename='figures/paper_link_quality')

# Plot node pressures and quality
node_indices = [2, 4, 6, 10]
node_names = G.getNodeNameID(node_indices)
G.plot_ts(X=hrs_time, Y=R.Pressure[:, node_indices], legend_location='best',
          title=f'Pressure, Node IDs: {node_names}', figure_size=[4, 3],
          xlabel='Time (hrs)', ylabel=f'Pressure ({G.units.NodePressureUnits})',
          marker=None, labels=node_names, save_fig=True, filename='figures/paper_pressures')

G.plot_ts(X=hrs_time, Y=R.NodeQuality[:, node_indices],
          title=f'Quality, Node IDs: {node_names}', legend_location='best',
          xlabel='Time (hrs)', ylabel=f'Quality', figure_size=[4, 3],
          marker=None, labels=node_names, save_fig=True, filename='figures/paper_node_quality')

from epyt import epanet  # Import the module "epanet" from the package "epyt"

G = epanet('L-TOWN.inp')  # Load the L-Town epanet input file and create the object G
dir(G)  # Lists all available functions and properties in G
help(G.getNodeElevations)  # Retrieve some examples for the function getNodeElevations

diameters = G.getLinkDiameter()  # retrieve Link diameters
elevations = G.getNodeElevations()  # retrieve Node elevations

G.getLinkDiameter([2, 10])  # Link diameter for link indices 2 & 10
G.setLinkDiameter(10, 90)  # Change the link with index 10 diameter to 90mm
G.getLinkDiameter([2, 10])  # Retrieve the diameter of link index 10

# H = G.getComputedHydraulicTimeSeries()  # Solve hydraulics in library
# Q = G.getComputedQualityTimeSeries()  # Solve quality dynamics in library

R = G.getComputedTimeSeries_ENepanet()  # Solve all dynamics in library, create a binary file to store the computed
# values

# Plot link flows and quality
G.plot()
hrs_time = R.Time / 3600  # transform seconds into hours
link_indices = [1, 5]  # select indices to plot
link_names = G.getLinkNameID(link_indices)  # get the ID of the link indices

G.plot_ts(X=hrs_time, Y=R.Flow[:, link_indices], title=f'Flow of links with ID: {link_names}', figure_size=[4, 3],
          legend_location='best', xlabel='Time (hours)', ylabel=f'Flow ($m^3$/hour)', marker=None, color=['r', 'g'],
          fontsize=8, fontsize_title=8, labels=link_names, save_fig=True, filename='figures/paper_flows')

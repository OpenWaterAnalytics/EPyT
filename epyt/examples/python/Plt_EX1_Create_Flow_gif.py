""" Create a gif with the flows of Net1.
    Requirements:
        pip install imageio
        pip install Pillow

    This example contains:
        Load a network.
        Run analysis with getComputedTimeSeries.
        Set colorbar values based on the min/max of all the Flow values.
        Create pngs for every timepoint.
        Create gif from all the pngs.
        Unload library.
"""
import matplotlib.pyplot as plt
from epyt import epanet
from PIL import Image
import imageio
import os

# Close all figures
plt.close('all')

# Load network Net1
d = epanet('Net1.inp')

# Set gif name 
new_gif_name = f'{d.netName[:-4]}_flows.gif'

# Run analysis
comp_analysis_vals = d.getComputedTimeSeries()
flows = comp_analysis_vals.Flow
Time = comp_analysis_vals.Time / 3600

print("\nCreating flow gif...")

# Set the colorbar values based on the min/max of all the Flow values
minFlow = d.min(flows)
maxFlow = d.max(flows)

# iterate through flow times
figToPngNames = []
for i, values in enumerate(flows):
    hr = str(int(Time[i - 1]))

    d.plot(link_values=values, min_colorbar=minFlow, max_colorbar=maxFlow, figure=False, link_text=True,
           title=f'Flows at time {hr} hrs', colorbar_label=f'Flow ({d.units.LinkFlowUnits})')

    PngName = f'{i}.png'
    figToPngNames.append(PngName)
    plt.savefig(PngName)
    plt.close()

# create gif
with imageio.get_writer(new_gif_name, mode='I') as writer:
    for fig in figToPngNames:
        image = imageio.imread(fig)
        writer.append_data(image)

# Remove files
for fig in set(figToPngNames):
    os.remove(fig)

flow_gif = Image.open(new_gif_name)

print(f"{new_gif_name} has created.")

# Unload library
d.unload()

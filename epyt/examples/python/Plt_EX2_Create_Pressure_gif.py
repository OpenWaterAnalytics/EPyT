""" Create a gif with the pressure of net2-cl2.

    Requirements:
        pip install imageio
        pip install Pillow

    This example contains:
        Load a network.
        Run hydraulic analysis with getComputedHydraulicTimeSeries.
        Set colorbar values based on the min/max of all the Pressure values.
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

# Load network net2-cl2
d = epanet('Net1.inp')

# Set gif name 
new_gif_name = f'{d.netName[:-4]}_pressures.gif'

# Run Hydraulic analysis
comp_analysis_vals = d.getComputedTimeSeries()
pressures = comp_analysis_vals.Pressure
Time = comp_analysis_vals.Time/3600

# Set the colorbar values based on the min/max of all the Pressure values
minPressure = d.min(pressures)
maxPressure = d.max(pressures)

# iterate through flow times
figToPngNames = []
for i, values in enumerate(pressures):

    hr = str(int(Time[i - 1]))

    d.plot(node_values=values, figure=False, min_colorbar=minPressure, max_colorbar=maxPressure,
           title=f'Pressures at time {hr} hrs', colorbar_label=f'Pressure ({d.units.NodePressureUnits})')

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

pressure_gif = Image.open(new_gif_name)

print(f"{new_gif_name} has created.")

# Unload library
d.unload()

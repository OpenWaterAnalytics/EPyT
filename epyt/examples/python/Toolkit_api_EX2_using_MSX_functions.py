from epyt.epanet import epanet, epanetmsxapi
from epyt import networks
import numpy as np
import os

# Create EPANET object using INP file and MSX object using MSX file
dirname = os.path.dirname(networks.__file__)
inpname = os.path.join(dirname, 'msx-examples', 'net2-cl2.inp')
msxname = os.path.join(dirname, 'msx-examples', 'net2-cl2.msx')

d = epanet(inpname)
msx = epanetmsxapi(msxname)
MSX_SPECIES = 3
ss = list(range(1, d.LinkCount + 1))
uu = list(range(1, msx.MSXgetcount(MSX_SPECIES) + 1))

# Initialized quality and time
link_count = d.getLinkCount()
msx_time_step = 300
time_steps = int(d.getTimeSimulationDuration()/msx_time_step)
quality = [np.zeros((time_steps, 1)) for _ in range(link_count)]
time = np.zeros((time_steps, 1))
data = {
    'Quality': quality,
    'Time': time
}

# Obtain a hydraulic solution
msx.MSXsolveH()

# Run a step-wise water quality analysis without saving results to file
msx.MSXinit(0)

# Retrieve species concentration at node
for i, nl in enumerate(ss, start=1):
    for j_idx, j in enumerate(uu, start=1):
        data['Quality'][i - 1][j_idx - 1] = msx.MSXgetinitqual(1, i, j)

k = 0
tleft = 1
# Initialized data time with 0
data['Time'][k] = [0]
while tleft > 0:
    t, tleft = msx.MSXstep()
    if t > msx_time_step:
        for i, nl in enumerate(ss, start=1):
            for g, j in enumerate(uu, start=1):
                x = msx.MSXgetqual(1, nl, j)
                data['Quality'][i - 1][k, g - 1] = x
    data['Time'][k] = t
    k += 1

# Plot quality over time (in hrs) for link 1
hrs_time = data['Time'] / 3600
d.plot_ts(X=hrs_time, Y=data['Quality'][0],
          title=f'Quality vs Time Link 1', legend_location='best', marker=None,
          xlabel='Time (hrs)', ylabel=f'CL2 Concentration (ppm)', figure_size=[4, 3])

# Plot quality over time (in hrs) for link 36
d.plot_ts(X=hrs_time, Y=data['Quality'][35],
          title=f'Quality vs Time Link 36', legend_location='best', marker=None,
          xlabel='Time (hrs)', ylabel=f'CL2 Concentration (ppm)', figure_size=[4, 3])

# Unload MSX library and EN library.
msx.MSXclose()
d.unload()

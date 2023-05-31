"""  Changes status randomly at pipes during simulation.

   This example contains:
    Load a network.
    Get pipe count.
    Get pipe indices.
    Run step by step hydraulic analysis.
    Set status random 0/1 for pipes.
    Plot flows.
    Unload library.
    
"""
from epyt import epanet
import random

# Load a network.
d = epanet('Net1.inp')

# Close any open figures
d.plot_close()

# Get pipe count.
pipe_count = d.getLinkPipeCount()
# Get pipe indices.
pipe_indices = d.getLinkPipeIndex()

# Run step by step hydraulic analysis.
d.openHydraulicAnalysis()
d.initializeHydraulicAnalysis()
tstep = 1
F = []
while tstep > 0:
    # Set status random 0/1 for pipes.
    Status = [random.randint(0, 1) for i in range(pipe_count)]
    t = d.runHydraulicAnalysis()
    d.setLinkStatus(pipe_indices, Status)
    F.append(d.getLinkFlows())
    tstep = d.nextHydraulicAnalysisStep()
d.closeHydraulicAnalysis()

# Plot flows.
d.plot_ts(Y=F, marker=None, color=None, title='Flows')

d.plot_show()
# Unload library.
d.unload()

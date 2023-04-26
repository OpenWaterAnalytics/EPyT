""" Closes pipes during simulation.
    This example contains:
      Load a network.
      Link index for change the status.
      Run step by step hydraulic analysis.
      Get flows for the specific link index.
      Unload library.
"""
from epyt import epanet
import pandas as pd

# Load a network.
d = epanet('Net1.inp')

# Link index for change the status.
link_index = 2

Status = [0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, ]

# Run step by step hydraulic analysis.
d.openHydraulicAnalysis()
d.initializeHydraulicAnalysis()
i, tstep, F = 0, 1, {}
while tstep > 0:
    t = d.runHydraulicAnalysis()
    d.setLinkStatus(link_index, Status[i])
    i += 1
    F[i] = d.getLinkFlows()
    tstep = d.nextHydraulicAnalysisStep()
d.closeHydraulicAnalysis()

# Get flows for the specific link index.
Flows = pd.DataFrame(F).iloc[link_index - 1]
T = pd.DataFrame({"Flows": Flows, "Status": Status}, dtype="category")

print(f'\nFlows and status for node index 2:\n {T}\n')

# Unload library.
d.unload()

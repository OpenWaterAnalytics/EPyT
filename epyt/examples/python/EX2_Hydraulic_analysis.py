""" Runs the hydraulic analysis of a network.

    This example contains:
      Load a network.
      Set simulation time duration.
      Hydraulic analysis using ENepanet binary file.
      Hydraulic analysis using EN functions.
      Hydraulic analysis step-by-step.
      Unload library.
"""
# Run hydraulic analysis of a network
from epyt import epanet
import time

# Load a network.
d = epanet('ky10.inp')

# Set simulation time duration.
hrs = 50
d.setTimeSimulationDuration(hrs * 3600)

# Hydraulic analysis using epanet2.exe binary file.
start_1 = time.time()
hyd_res_1 = d.getComputedTimeSeries_ENepanet()
stop_1 = time.time()
hyd_res_1.disp()

# Hydraulic analysis using epanet2.exe binary file.
start_2 = time.time()
hyd_res_2 = d.getComputedTimeSeries()
stop_2 = time.time()
hyd_res_2.disp()

# Hydraulic analysis using the functions ENopenH, ENinit, ENrunH, ENgetnodevalue/&ENgetlinkvalue, ENnextH, ENcloseH.
# (This function contains events)
start_3 = time.time()
hyd_res_3 = d.getComputedHydraulicTimeSeries()
stop_3 = time.time()
hyd_res_3.disp()

# Hydraulic analysis step-by-step using the functions ENopenH, ENinit, ENrunH, ENgetnodevalue/&ENgetlinkvalue,
# ENnextH, ENcloseH. (This function contains events)
etstep = 3600
d.setTimeReportingStep(etstep)
d.setTimeHydraulicStep(etstep)
d.setTimeQualityStep(etstep)

start_4 = time.time()
d.openHydraulicAnalysis()
d.initializeHydraulicAnalysis()
tstep, P, T_H, D, H, F = 1, [], [], [], [], []
while tstep > 0:
    t = d.runHydraulicAnalysis()
    P.append(d.getNodePressure())
    D.append(d.getNodeActualDemand())
    H.append(d.getNodeHydraulicHead())
    F.append(d.getLinkFlows())
    T_H.append(t)
    tstep = d.nextHydraulicAnalysisStep()
d.closeHydraulicAnalysis()
stop_4 = time.time()

print(f'Pressure: {P}')
print(f'Demand: {D}')
print(f'Hydraulic Head {H}')
print(f'Flow {F}')

# Unload library.
d.unload()

print(f'Elapsed time for the function `getComputedTimeSeries_ENepanet` is: {stop_1 - start_1:.8f}')
print(f'Elapsed time for the function `getComputedTimeSeries` is: {stop_2 - start_2:.8f}')
print(f'Elapsed time for the function `getComputedHydraulicTimeSeries` is: {stop_3 - start_3:.8f}')
print(f'Elapsed time for `step-by-step` analysis is: {stop_4 - start_4:.8f}')

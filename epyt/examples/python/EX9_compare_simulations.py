""" Compares hydraulics and quality analysis functions.

    This example contains:
        Load a network.
        Set simulation duration.
        Test hydraulics and quality analysis functions.
        Step by step hydraulic analysis.
        Step by step quality analysis.
        Unload library.
        Run time d.getComputedTimeSeries.
        
"""
from epyt import epanet
import time

# Load a network.
d = epanet('Net1.inp')

# Close any open figures
d.plot_close()

# Set simulation duration.
hours = 100
d.setTimeSimulationDuration(hours * 3600)

# Test hydraulics and quality analysis functions.
# Using ENepanet, create and read binary file.
start_results = time.time()
Results = d.getComputedTimeSeries()
stop_results = time.time()

# Using the functions(ENopenH, ENinit, ENrunH, ENgetnodevalue/&ENgetlinkvalue, ENnextH, ENcloseH).
start_hydraulic = time.time()
Hydraulics = d.getComputedHydraulicTimeSeries()
stop_hydraulic = time.time()

# ENopenQ, ENinitQ, ENrunQ, ENgetnodevalue/&ENgetlinkvalue, ENstepQ, ENcloseQ
start_quality = time.time()
Quality = d.getComputedQualityTimeSeries()
stop_quality = time.time()

# Pipeindex 4 and nodeindex 6 # start from 0
pipeindex = 4 - 1
nodeindex = 6 - 1

# Step by step hydraulic analysis.
d.openHydraulicAnalysis()
d.initializeHydraulicAnalysis()
tstep, P, T_H, D, H, F = 1, [], [], [], [], []
while tstep > 0:
    t = d.runHydraulicAnalysis()
    P.append(d.getNodePressure())
    D.append(d.getNodeActualDemand())
    H.append(d.getNodeHydraulicHead())
    F.append(d.getLinkFlows())
    T_H.append(t/3600)
    tstep = d.nextHydraulicAnalysisStep()
d.closeHydraulicAnalysis()

# Step by step quality analysis.
d.setTimeSimulationDuration(86400)
d.setTimeQualityStep(3600)
d.solveCompleteHydraulics() 
d.openQualityAnalysis()
d.initializeQualityAnalysis()
tleft, P, T_Q, Q = 1, [], [], []
sim_duration = d.getTimeSimulationDuration()
while tleft > 0 or t < sim_duration:
    t = d.runQualityAnalysis()
    Q.append(d.getNodeActualQuality())
    T_Q.append(t/3600)
    tleft = d.stepQualityAnalysisTimeLeft()
d.closeQualityAnalysis()

# Unload library.
d.unload()

# Run time d.getComputedTimeSeries.
print(f'\nSimulation duration: {hours} hours\n')
print(f'Run Time of function d.getComputedTimeSeries: {stop_results - start_results:.5}  (sec)')
print(f'Run Time of function d.getComputedHydraulicTimeSeries: {stop_hydraulic - start_hydraulic:.5} (sec)')
print(f'Run Time of function d.getComputedQualityTimeSeries: {stop_quality - start_quality:.5} (sec)')


d.plot_ts(X=Results.Time/3600, Y=Results.Flow[:, pipeindex], title='d.getComputedTimeSeries (Ignore events)',
          xlabel='Time (hrs)', ylabel='Flow (' + d.LinkFlowUnits + ') - Link ID "' + d.LinkNameID[pipeindex] + '"',
          marker=None, fontsize=8)


d.plot_ts(X=Hydraulics.Time/3600, Y=d.to_array(F)[:, pipeindex], title='d.getComputedHydraulicTimeSeries',
          xlabel='Time (hrs)', ylabel='Flow (' + d.LinkFlowUnits + ') - Link ID "' + d.LinkNameID[pipeindex] + '"',
          marker=None, fontsize=8)


d.plot_ts(X=T_H, Y=d.to_array(F)[:, pipeindex], title='step by step Hydraulic Analysis',
          xlabel='Time (hrs)', ylabel='Flow (' + d.LinkFlowUnits + ') - Link ID "' + d.LinkNameID[pipeindex] + '"',
          marker=None, fontsize=8)


d.plot_ts(X=Results.Time/3600, Y=Results.NodeQuality[:, nodeindex], title='d.getComputedTimeSeries (Ignore events)',
          xlabel='Time (hrs)', ylabel='Node Quality (' + d.QualityChemUnits + ') - Node ID "' + d.NodeNameID[nodeindex] + '"',
          marker=None, fontsize=8)


d.plot_ts(X=Quality.Time/3600, Y=Quality.NodeQuality[:, nodeindex], title='d.getComputedQualityTimeSeries',
          xlabel='Time (hrs)', ylabel='Node Quality (' + d.QualityChemUnits + ') - Link ID "' + d.NodeNameID[nodeindex] + '"',
          marker=None, fontsize=8)


d.plot_ts(X=T_Q, Y=d.to_array(Q)[:, pipeindex], title='step by step Quality Analysis',
          xlabel='Time (hrs)', ylabel='Node Quality (' + d.QualityChemUnits + ') - Link ID "' + d.NodeNameID[nodeindex] + '"',
          marker=None, fontsize=8)

# Show the plots (plt.show())
d.plot_show()
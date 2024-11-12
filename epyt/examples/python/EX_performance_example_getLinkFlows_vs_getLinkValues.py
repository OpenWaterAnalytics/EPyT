from epyt import epanet
import time

"""
        Performance Example Summary:

Objective:

    To compare the execution speed of two functions, getLinkFlows vs. getLinkValues.

Criteria:

    The main criterion for comparison was speed.
    Both functions were tested under the same simulation conditions.

Test Setup:

    The simulation was designed to extract link flow values:
        getLinkFlows: Extracts flows for all links - 1.
        getLinkValues: Extracts the flow values for all links.

Results:

    getLinkFlows: Extracted fewer values (flows set to -1).
    getLinkValues: Extracted all actual flow values for each link,
    processing more data than getLinkFlows.
    Despite extracting more data, getLinkValues performed faster than getLinkFlows.

Conclusion: 

    The function getLinkValues was more efficient in terms of speed, 
    even though it processed and returned more values compared to getLinkFlows. 
"""



inp= "Net1.inp"
d = epanet(inp)

d.setTimeSimulationDuration(1000*3600*24)
start_time = time.time()
d.openHydraulicAnalysis()
d.initializeHydraulicAnalysis()
numbers = [i for i in range(1, 13)]
tstep = 1
T_H, Ft, Fb =  [], [], []
while tstep > 0:
    t = d.runHydraulicAnalysis()
    #flow test
    Fb.append(d.getLinkFlows(numbers))
    T_H.append(t)
    tstep = d.nextHydraulicAnalysisStep()

d.closeHydraulicAnalysis()
print(Fb)
end_time = time.time()
timeforold = end_time - start_time
print(f"Time taken by old function: {timeforold} seconds")
d.unload()

d = epanet(inp)
start_time = time.time()

d.openHydraulicAnalysis()
d.initializeHydraulicAnalysis()

tstep = 1
T_H, Ft, Fb =  [], [], []
while tstep > 0:
    t = d.runHydraulicAnalysis()
    #flow test
    Ft.append(d.getLinkValues(d.ToolkitConstants.EN_FLOW))
    T_H.append(t)
    tstep = d.nextHydraulicAnalysisStep()

d.closeHydraulicAnalysis()
print(Ft)
end_time = time.time()
timefornew = end_time - start_time
print(f"Time taken by newfunction: {timefornew} seconds")
print(f"The new function is faster by {timeforold-timefornew} seconds")
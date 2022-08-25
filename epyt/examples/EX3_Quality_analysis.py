""" This examples runs the quality analysis of a network.

    The example contains: 
        Load a network.
        Run Water Quality analysis of a network.
        Compute Quality step by step.   
        Unload library.
   
    Based on EX3_Quality_analysis.m of EPANET-Matlab-Toolkit:
        https://github.com/MariosDem/EPANET-Matlab-Toolkit/blob/master/examples/EX3_Quality_analysis.m

"""
from epyt import epanet

# Load a network.
d = epanet('Net2.inp')

# Run Water Quality analysis of a network (This function contains events)
qual_res = d.getComputedQualityTimeSeries()  # Value x Node, Value x Link
qual_res.disp()

# Compute Quality step by step.
d.solveCompleteHydraulics()
d.openQualityAnalysis()
d.initializeQualityAnalysis()
tleft, P, T, QsN, QsL = 1, [], [], [], []
while tleft > 0:
    t = d.runQualityAnalysis()
    P.append(d.getNodePressure())
    QsN.append(d.getNodeActualQuality())
    QsL.append(d.getLinkQuality())
    T.append(t)
    tleft = d.stepQualityAnalysisTimeLeft()

d.closeQualityAnalysis()

d.printv(QsN)

# Unload library
d.unload()

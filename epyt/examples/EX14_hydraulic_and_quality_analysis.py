""" Runs the Hydraulic and Quality analysis of a network.

    This example contains:
      Load a network.
      Hydraulic and Quality analysis STEP-BY-STEP.
      Display nodes pressures, links flows, nodes actual qualities, links actual qualities.
      Unload library.
"""
from epyt import epanet

# Load a network.
d = epanet('Net1.inp')
d.setQualityType('Chlorine', 'mg/L')
initialQuality = 0.6
nodeIndex = d.getNodeReservoirIndex()
nodeIndex = [nodeIndex[0], d.getNodeTankIndex()[0]]
d.setNodeInitialQuality(nodeIndex, [initialQuality] * len(nodeIndex))

# Set time hydraulic and quality steps
etstep = 3600
d.setTimeReportingStep(etstep)
d.setTimeHydraulicStep(etstep)
d.setTimeQualityStep(etstep)
# step = min(Pstep,Hstep)
# Hstep = min(Rstep,Hstep)
# Hstep = min(Qstep,Hstep)

# Hydraulic and Quality analysis STEP-BY-STEP.
d.openHydraulicAnalysis()
d.openQualityAnalysis()
d.initializeHydraulicAnalysis(0)
d.initializeQualityAnalysis(d.ToolkitConstants.EN_NOSAVE)

tstep = 1
T, P, F, QN, QL = [], [], [], [], []
while tstep > 0:
    t = d.runHydraulicAnalysis()
    qt = d.runQualityAnalysis()

    P.append(d.getNodePressure())
    F.append(d.getLinkFlows())

    QN.append(d.getNodeActualQuality())
    QL.append(d.getLinkActualQuality())
    T.append(t)

    tstep = d.nextHydraulicAnalysisStep()
    qtstep = d.nextQualityAnalysisStep()

d.closeQualityAnalysis()
d.closeHydraulicAnalysis()

# Display nodes pressures, links flows, nodes actual qualities, links actual qualities.
print(f'Pressure:\n {P} \n')
print(f'Flow:\n {F} \n')
print(f'Node Quality:\n {QN} \n')
print(f'Link Quality:\n {QL} \n')

# Unload library.
d.unload()

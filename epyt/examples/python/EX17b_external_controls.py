""" b) External Controls, Adds controls in hydraulic analysis STEP-BY-STEP.
    This example contains:
        Load network.
        Delete Controls.
        Hydraulic analysis STEP-BY-STEP.
        CONTROLS.
        Add new controls in live.
        Delete controls.
        Unload library.
"""
from epyt import epanet

# Second way
# Load network.
d = epanet('Net1.inp')

# Close any open figures
d.plot_close()

# Delete Controls.
d.deleteControls()
tankID = '2'
pumpID = '9'

tankIndex = d.getNodeIndex(tankID)
pumpIndex = d.getLinkIndex(pumpID)
tankElevation = d.getNodeElevations(tankIndex)

# Hydraulic analysis STEP-BY-STEP.
d.openHydraulicAnalysis()
d.initializeHydraulicAnalysis(0)

tstep = 1
i = 0
T, P, F, S = [], [], [], []
tankHead = []

# CONTROLS
while tstep > 0:
    H = d.getNodeHydraulicHead()
    tankHead.append(H[tankIndex - 1] - tankElevation)

    # Add new controls in live.
    Below = 110
    Above = 140
    status = ['OPEN', 'CLOSED']

    # LINK 9 OPEN IF NODE 2 BELOW 110
    d.addControls('LINK ' + pumpID + ' ' + status[0] + ' IF NODE ' + tankID +
                  ' BELOW ' + str(Below))

    # LINK 9 CLOSED IF NODE 2 ABOVE 140
    d.addControls('LINK ' + pumpID + ' ' + status[1] + ' IF NODE ' + tankID +
                  ' ABOVE ' + str(Above))

    t = d.runHydraulicAnalysis()

    S.append(d.getLinkStatus(pumpIndex))
    F.append(d.getLinkFlows())
    P.append(d.getNodePressure(1))
    T.append(t)

    tstep = d.nextHydraulicAnalysisStep()

    # Delete controls.
    d.deleteControls()
d.closeHydraulicAnalysis()

# Unload library.
d.unload()

d.plot_ts(Y=tankHead, title='Tank Head', marker=False)
d.plot_ts(Y=S, title='Link Status', marker=False)

d.plot_show()

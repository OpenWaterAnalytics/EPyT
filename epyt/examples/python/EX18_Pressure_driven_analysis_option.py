""" Test the Pressure Driven Analysis option.

   This example contains:
    Set Demand Multiplier to 10 to cause negative pressures.
    Run single period analysis.
    Solve hydraulics with default DDA option which will return with neg. pressure warning code.
    Check that 4 demand nodes have negative pressures.
    Switch to PDA with pressure limits of 20 - 100 psi.
    Solve hydraulics again.
    Check that 6 nodes had demand reductions totaling 32.66.
    Check that Junction 12 had full demand.
    Check that Junction 21 had a demand deficit of 413.67.
    Unload library.

 https://github.com/OpenWaterAnalytics/EPANET/blob/a184a3a39a7bf3663943c0504c6c1c2f632f44dd/tests/test_pda.cpp

"""
from epyt import epanet

d = epanet('Net1.inp')

# Set Demand Multiplier to 10 to cause negative pressures.
d.setOptionsPatternDemandMultiplier(10)

# Run single period analysis.
d.setTimeSimulationDuration(0)

# Solve hydraulics with default DDA option which will return with neg. pressure warning code.
d.solveCompleteHydraulics()

# Check that 4 demand nodes have negative pressures.
deficient_nodes = d.getStatistic().DeficientNodes
print(True) if abs(deficient_nodes) == 4 else print(False)

# Switch to PDA with pressure limits of 20 - 100 psi.
Type = 'PDA'
pmin = 0
preq = 0.1
pexp = 0.5
d.setDemandModel(Type, pmin, preq, pexp)

# Solve hydraulics again.
d.solveCompleteHydraulics()

# Check that 6 nodes had demand reductions totaling 32.66.
deficient_nodes = d.getStatistic().DeficientNodes
demand_reduction = d.getStatistic().DemandReduction
print(True) if abs(deficient_nodes) == 6 else print(False)
print(True) if abs(demand_reduction - 32.66) < 0.01 else print(False)

# Check that Junction 12 had full demand.
junctionIndex_12 = d.getNodeIndex('12')
demand_deficit_12 = d.getNodeDemandDeficit(junctionIndex_12)
print(True) if abs(demand_deficit_12) < 0.01 else print(False)

# Check that Junction 21 had a demand deficit of 413.67.
junctionIndex_21 = d.getNodeIndex('21')
demand_deficit_21 = d.getNodeDemandDeficit(junctionIndex_21)
print(True) if abs(demand_deficit_21 - 413.67) < 0.01 else print(False)

# Unload library.
d.unload()

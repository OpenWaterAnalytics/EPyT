from epyt import epanet, networks
import os

d = epanet('example.inp')
d.loadMSXFile('example.msx')

a = d.getMSXOptions()
# AREA_UNITS FT2/M2/CM2
# RATE_UNITS SEC/MIN/HR/DAY
# SOLVER EUL/RK5/ROS2
# COUPLING FULL/NONE
# TIMESTEP seconds
# ATOL value
# RTOL value
# COMPILER NONE/VC/GC
# SEGMENTS value
# PECLET value
d.printv(d.getMSXTimeStep())
d.printv(d.getMSXRateUnits())
d.printv(d.getMSXAreaUnits())
d.printv(d.getMSXCompiler())
d.printv(d.getMSXCoupling())
d.printv(d.getMSXSolver())
d.printv(d.getMSXAtol())
d.printv(d.getMSXRtol())
# d.printv(d.getMSXSegments())
# d.printv(d.getMSXPeclet())

print('after set')
d.setMSXAreaUnitsCM2()
d.printv(d.getMSXAreaUnits())

d.setMSXAreaUnitsFT2()
d.printv(d.getMSXAreaUnits())

d.setMSXAreaUnitsM2()
d.printv(d.getMSXAreaUnits())

d.setMSXAtol(0.1)
d.printv(d.getMSXAtol())

d.setMSXRtol(0.2)
d.printv(d.getMSXRtol())

d.setMSXCompilerGC()
d.printv(d.getMSXCompiler())

d.setMSXCompilerVC()
d.printv(d.getMSXCompiler())

d.setMSXCompilerNONE()
d.printv(d.getMSXCompiler())

d.setMSXCouplingFULL()
d.printv(d.getMSXCoupling())

d.setMSXCouplingNONE()
d.printv(d.getMSXCoupling())

d.setMSXTimeStep(100)
d.printv(d.getMSXTimeStep())

d.setMSXRateUnitsSEC()
d.printv(d.getMSXRateUnits())

d.setMSXRateUnitsMIN()
d.printv(d.getMSXRateUnits())

d.setMSXRateUnitsHR()
d.printv(d.getMSXRateUnits())

d.setMSXRateUnitsDAY()
d.printv(d.getMSXRateUnits())
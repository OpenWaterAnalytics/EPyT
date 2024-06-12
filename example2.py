import struct

from epyt import epanet
import os
import numpy as np
from epyt.epanet import epanetmsxapi

import warnings



inpname = os.path.join(os.getcwd(), 'epyt', 'networks','msx-examples', 'net2-cl2.inp')
msxname = os.path.join(os.getcwd(), 'epyt', 'networks','msx-examples', 'net2-cl2.msx')
#inpname = os.path.join(os.getcwd(), 'epyt', 'networks','msx-examples', 'Net3-NH2CL.inp')
#msxname = os.path.join(os.getcwd(), 'epyt','networks','msx-examples', 'Net3-NH2CL.msx')

epanetlib=r"C:\Users\ichry\OneDrive\Desktop\Water\epanet2.dll"
msxlib=r"C:\Users\ichry\OneDrive\Desktop\Water\epanetmsx.dll"
#inpname = os.path.join(os.getcwd(), 'epyt', 'networks','msx-examples', 'Net1.inp')
d = epanet(inpname)
d.loadMSXFile(msxname, customMSXlib=msxlib)


"""
x=d.getMSXConstantsCount()
print(x)
x=d.getMSXParametersCount()
print(x)
x=d.getMSXPatternsCount()
print(x)
x = d.getMSXConstantsIndex(['S1','S2'])
print(x)
#x = d.getMSXSources()
#print(x)
options = d.get_MSX_Options(msxname, 'TIMESTEP')
options = d.get_MSX_Options(msxname, getall=True)

print(options)

x= d.getMSXTimeStep()
print(x)
x = d.getMSXAreaUnits()
print(x)
x = d.getMSXRateUnits()
print(x)
x = d.getMSXCompiler()
print(x)
x = d.getMSXCoupling()
print(x)
x = d.getMSXSolver()
print(x)
x = d.getMSXRtol()
print(x)
x = d.getMSXAtol()
print(x)
x=d.getMSXConstantsNameID()
print(x)
x=d.getMSXConstantsNameID({1})
print(x)
x=d.getMSXConstantsNameID([1,2])
print(x)

x=d.getMSXParametersNameID()
print(x)
x=d.getMSXParametersNameID({1, 3, 4})
print(x)
x=d.getMSXParametersNameID([1,5,6])
print(x)
x=d.getMSXPatternsNameID()
print(x)
x=d.getMSXPatternsNameID({1})
print(x)
x=d.getMSXPatternsNameID([1,2])
print(x)

x=d.getMSXSpeciesNameID()
print(x)
x=d.getMSXSpeciesNameID([1,5,8])
print(x)
x=d.getMSXSpeciesNameID({7})
print(x)



x = d.getMSXParametersIndex()
print(x)

x = d.getMSXParametersIndex({'k2','k3'})
print(x)
x = d.getMSXParametersIndex({"k1","k2","k3","k10","kDOC2"})
print(x)

x = d.getMSXSpeciesIndex()
print(x)
x = d.getMSXSpeciesIndex({"HOCL","I"})
print(x)
x = d.getMSXSpeciesIndex({"HOCL","I","TOC","ALK","cNH2CL"})
print(x)

x=d.getMSXPatternsIndex()
print(x)
x=d.getMSXPatternsIndex({"PAT1","PAT2"})
print(x)
x=d.getMSXPatternsIndex({"PAT2"})
print(x)
x=d.getMSXConstantsIndex()
print(x)
x=d.getMSXConstantsIndex(({"S2"}))
print(x)
x=d.getMSXConstantsValue()
print(x)
x=d.getMSXConstantsValue([1,2])
print(x)
x=d.getMSXConstantsValue([2])
print(x)
x=d.getMSXParametersPipesValue()
print(x)
x=d.getMSXParametersTanksValue()
print(x)
x=d.getMSXPatternsLengths()
print(x)
x=d.getMSXPatternsLengths([1])
print(x)
x=d.getMSXPatternsLengths()
print(x)
x=d.getMSXPattern()
print(x)

x=d.getMSXSpeciesType()
print(x)
x=d.getMSXSpeciesType([1,2,3,5])
print(x)

x=d.getMSXSpeciesUnits()
print(x)
x=d.getMSXSpeciesUnits([1,2,14])
print(x)
x,y,z=d.getEquations()
print(x)
print(y)
print(z)
x=d.getMSXEquationsTerms()
print(x)
x=d.getMSXEquationsPipes()
print(x)
x=d.getMSXEquationsTanks()
print(x)

x=d.getMSXSourceLevel()
print(x)
x=d.getMSXSourceLevel([1])
print(x)
x=d.getMSXSourcePatternIndex()
print(x)
x=d.getMSXSourcePatternIndex([1])
print(x)
x=d.getMSXSourceNodeNameID
print(x)
x=d.getMSXLinkInitqualValue()
print(x)
x=d.getMSXLinkInitqualValue([1,2,3])
print(x)
x=d.getMSXNodeInitqualValue()
print(x)
x=d.getMSXLinkInitqualValue([1,2,3])
print(x)
x=d.getMSXSpeciesATOL()
print(x)
x=d.getMSXSpeciesRTOL()
print(x)
d.solveMSXCompleteHydraulics()
d.solveMSXCompleteQuality()
x=d.getMSXSpeciesConcentration(0,1,1)
print(x)
x=d.getMSXSources()
print(x)
#print(d.getMSXSourceNodeNameID())
x=d.getMSXSourceType()
print(x)
x=d.getMSXSourceType([97])
print(x)

x=d.getMSXSourceNodeNameID()
print(x)
x=d.getMSXSourcePatternIndex()
print(x)
x=d.getMSXSourceType([1])
print(x)
x=d.getMSXSourceNodeNameID()
print(x)
z = len(x)
print(z)

d.setMSXAreaUnitsCM2()
x=d.getMSXOptions()
print(x)
d.setMSXAreaUnitsFT2()
x=d.getMSXOptions()
print(x)
d.setMSXAreaUnitsM2()
x=d.getMSXOptions()
print(x)
d.setMSXAtol(420)
x=d.getMSXOptions()
print(x)
d.setMSXRtol(360)
x=d.getMSXOptions()
print(x)
d.setMSXCompilerNONE()
x=d.getMSXOptions()
print(x)
d.setMSXCompilerVC()
x=d.getMSXOptions()
print(x)
d.setMSXCompilerGC()
x=d.getMSXOptions()
print(x)
d.setMSXCompilerNONE()
x=d.getMSXOptions()
print(x)
d.setMSXCouplingFULL()
x=d.getMSXOptions()
print(x)
d.setMSXRateUnitsDAY()
x=d.getMSXOptions()
print(x)
d.setMSXRateUnitsHR()
x=d.getMSXOptions()
print(x)
d.setMSXRateUnitsMIN()
x=d.getMSXOptions()
print(x)
d.setMSXRateUnitsSEC()
x=d.getMSXOptions()
print(x)
d.setMSXSolverEUL()
x=d.getMSXOptions()
print(x)
d.setMSXSolverROS2()
x=d.getMSXOptions()
print(x)
d.setMSXSolverRK5()
x=d.getMSXOptions()
print(x)
d.setMSXTimeStep(650)
x=d.getMSXOptions()
print(x)
d.setMSXParametersPipesValue(1, [10,15,12,54])
MSX_comp = d.getMSXComputedQualitySpecie(['CL2'])
a=MSX_comp.NodeQuality
ae=MSX_comp.LinkQuality
#print(len(a))
#print(len(a[0]))
x=[0,1,2]
for i in x:
    print(i)
ax=d.getMSXComputedNodeQualitySpecie(x,'CL2')
#print(ax.NodeQuality)
ax=d.getMSXComputedLinkQualitySpecie(x,'CL2')
print(ax.LinkQuality[0][0])

linkIndex=0
speciesIndex=0
n=0
m=0
values = [[0] * n for _ in range(m)]
values=d.getMSXNodeInitqualValue()
values[linkIndex][speciesIndex]=1500
d.setMSXNodeInitqualValue(values)
x=d.getMSXNodeInitqualValue()
print(x)



srcs = d.getMSXSources()
print(srcs)
d.addMSXPattern('PatAsIII',[2, .3, .4, 6, 5, 2, 4])
x=d.getMSXPatternsNameID()

z=d.getMSXSpeciesNameID()
x=[0]
for i in x:
    print(i)
ax=d.getMSXComputedNodeQualitySpecie(x,'CL2')
print(ax.NodeQuality)
y=d.getNodeNameID(2)

print(ax.NodeQuality)
d.setMSXSources(d.getNodeNameID(2), d.getMSXSpeciesNameID([1]),'FLOWPACED', 0.5, 'PatAsIII')
kek = d.getMSXSources()
print(kek)
#example with msxwrite



x=d.getMSXComputedQualitySpecie(['CL2'],1,None)

print(x.NodeQuality)

x=[0,1,2]
for i in x:
    print(i)
ax=d.getMSXComputedLinkQualitySpecie(x,['CL2',"H"])
print(ax["CL2"].LinkQuality)
print(ax["H"].LinkQuality)
d.addMSXPattern('1',[])
d.setMSXPatternMatrix([.1,.2,.5,.2,1,.9])
print(d.getMSXPattern())

#SX_comp = d.getMSXComputedTimeSeries()
speciesindex = 1
MSX_comp = d.getMSXComputedTimeSeries('species', speciesindex)
#print(MSX_comp.LinkQuality)
#print(MSX_comp.Time)
nodeidnex = d.getNodeIndex()
MSX_comp = d.getMSXComputedTimeSeries('nodes', nodeidnex, 'species', speciesindex)
#print(MSX_comp.NodeQuality)
#print(MSX_comp.Time)
linkidnex = d.getLinkIndex()
MSX_comp = d.getMSXComputedTimeSeries('links', linkidnex, 'species', speciesindex)
print(MSX_comp.LinkQuality)
#print(MSX_comp.Time)
#print(MSX_comp.LinkQuality)"""
#MSX_comp = d.getMSXComputedQualityNode()
#print(MSX_comp.Quality)
#print(MSX_comp.Time)
#d.getMSXComputedQualityNode(1).Quality
#d.getMSXComputedQualityNode(1:3).Quality
"""
x=[0,1,2]

ax=d.getMSXComputedLinkQualitySpecie(x,['CL2'])
print(ax["CL2"].LinkQuality)
ax2[0].LinkQuality
ax2.LinkQuality[0]
ax2=d.getMSXComputedTimeSeries()
idx=9
d32=100
d.setNodeBaseDemands(idx, d32)
p32 = d.getComputedHydraulicTimeSeries().Pressure[idx-1,:]
print(p32)

x=[0,1,2]


ax=d.getMSXComputedNodeQualitySpecie(x,['CL2'])

print(ax.NodeQuality)
msx = d.initializeMSXWrite()

msx.FILENAME="cl34.msx"
msx.TITLE = "CL2 Full msx"
msx.AREA_UNITS = 'FT2'
msx.RATE_UNITS = 'DAY'
msx.SOLVER = 'EUL'
msx.COUPLING = 'NONE'
msx.COMPILER = 'NONE'
msx.TIMESTEP = 300
msx.ATOL = 0.001
msx.RTOL = 0.001

msx.SPECIES={'BULK CL2 MG 0.01 0.001'}
msx.COEFFICIENTS = {'PARAMETER Kb 0.3', 'PARAMETER Kw 1'}
msx.TERMS = {'Kf 1.5826e-4 * RE^0.88 / D'}
msx.PIPES = {'RATE CL2 -Kb*CL2-(4/D)*Kw*Kf/(Kw+Kf)*CL2'}
msx.TANKS = {'RATE CL2 -Kb*CL2'}
msx.SOURCES = {'CONC 1 CL2 0.8 '}
msx.GLOBAL = {'Global CL2 0.5'}
msx.QUALITY = {'NODE 26 CL2 0.1'}
msx.PARAMETERS = {''}
msx.PATERNS = {''}
d.writeMSXFile(msx)
d.unloadMSX()
d.loadMSXFile(msx.FILENAME)
d.unloadMSX()
d.unload()"""
#MSX_comp = d.getMSXComputedQualityNode()
#x=MSX_comp.Quality
# Assuming MSX_comp is the result from getMSXComputedQualityNode
MSX_comp = d.getMSXComputedQualityLink()
x = MSX_comp.Quality

d.addMSXPattern('1',[])
d.addMSXPattern('2',[])
d.setMSXPatternMatrix([[.1,.2,.5,.2,1,.9],[1, 2, 3,4,5]])
print(d.getMSXPattern())
d.unloadMSX()
d.unload()
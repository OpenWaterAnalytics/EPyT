from epyt import epanet
import logging

#inpfile = "Richmond_standard.inp"

#Warning that a link is missing and the network is not fully connected
inpfile = "BrokenNetwork.inp"
d = epanet(inpfile)
d.unload()

inpfile = "Net1.inp"
d = epanet(inpfile)

#setcurvetype functions
d.setCurveTypePump(1)
d.printv(d.getCurveType(1))
d.setCurveTypeVolume(1)
d.printv(d.getCurveType())
d.setCurveTypeGeneral(1)
d.printv(d.getCurveType())
d.setCurveTypeHeadloss(1)
d.printv(d.getCurveType())
d.setCurveTypeEfficiency(1)
d.printv(d.getCurveType())
d.setCurveTypeValveCurve(1)
d.printv(d.getCurveType())

# Setvertex
linkID = '10'
x = [ 22,24, 28]
y = [ 30,68, 69]
d.setLinkVertices(linkID, x, y)
x = d.getLinkVertices()
d.setVertex(1,1,1,1)
d.printv(d.getLinkVertices())

#set and get linkvalvecurvegpv
linkid = d.getLinkPipeNameID(1)
condition = 1
index = d.setLinkTypeValveGPV(linkid, condition)
d.setLinkValveCurveGPV(index,1)
d.printv(d.getLinkValveCurveGPV())

#set and get linkvalvecurvepcv
linkid = d.getLinkPipeNameID(1)
condition = 1
index = d.setLinkTypeValvePCV(linkid, condition)
d.setLinkValveCurvePCV(index,1)
d.printv(d.getLinkValveCurvePCV(index))

#setTimeClockStartTime & getTimeClockStartTime
d.printv(d.getTimeClockStartTime())
d.setTimeClockStartTime(3600)
d.printv(d.getTimeClockStartTime())

# getOptionsDemandPattern())
d.printv(d.getOptionsDemandPattern())
d.setOptionsDemandPattern(0)
d.printv(d.getOptionsDemandPattern())


# getLinkType / d.setLinkTypeValvePCV / d.addLinkValvePCV
d.getLinkType(1)  # Retrieves the type of the 1st link
linkid = d.getLinkPipeNameID(1)  # Retrieves the ID of the 1t pipe
index = d.setLinkTypeValvePCV(linkid)  # Changes the 1st pipe to valve PCV given it's ID
print(d.getLinkType(index))

#addLinkValvePCV
#d.plot()
valveID = 'newValvePCV'
fromNode = '10'
toNode = '21'
valveIndex = d.addLinkValvePCV(valveID, fromNode, toNode)
#d.plot()

#getset OptionsEmiterBackFlow
d.printv(d.getOptionsEmitterBackFlow())
d.setOptionsEmitterBackFlowDisallowed()
d.printv(d.getOptionsEmitterBackFlow())
d.setOptionsEmitterBackFlowAllowed()
d.printv(d.getOptionsEmitterBackFlow())

#getNodeInControl & getLinkInControl
d.printv(d.getLinkInControl())
d.printv(d.getLinkInControl(10))
d.printv(d.getNodeInControl())
d.printv(d.getNodeInControl(11))

#setLinkFlowUnitsCMS
d.setFlowUnitsCMS() #kpa and meters
d.printv(d.getFlowUnits())


#example with change from kpa to psi without changing metric first
d.setOptionsPressureUnitsPSI()
d.printv(d.getOptionsPressureUnits())

#how to do it right
d.setFlowUnitsIMGD()
d.setOptionsPressureUnitsPSI()
d.printv(d.getOptionsPressureUnits())


#example with change from psi to KPA without changing the metric
d.setOptionsPressureUnitsKPA()
d.printv(d.getOptionsPressureUnits())

#reseting
d.setFlowUnitsGPM()
d.setOptionsPressureUnitsPSI()

#setNodeEmitterCoeff
d.setNodeEmitterCoeff([2,3],[0.5,0.6])
d.printv(d.getNodeEmitterCoeff())

#getset Optionsstatusreport
d.setOptionsStatusReportNo()
d.printv(d.getOptionsStatusReport())
d.setOptionsStatusReportNormal()
d.printv(d.getOptionsStatusReport())
d.setOptionsStatusReportFull()
d.printv(d.getOptionsStatusReport())

#Leakage section
d.solveCompleteHydraulics()

d.setLinkLeakArea(2,10.5)
d.printv(d.getLinkLeakArea())

d.setLinkExpansionProperties(5,2)
d.printv(d.getLinkExpansionProperties())

d.printv(d.getLinkLeakageRate())

d.printv(d.getConsumerDemandRequested(5))

d.printv(d.getConsumerDemandDelivered(5))

d.printv(d.getNodeEmitterFlow())

d.unload()

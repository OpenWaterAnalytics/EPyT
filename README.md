<a href="http://www.kios.ucy.ac.cy"><img src="https://www.kios.ucy.ac.cy/wp-content/uploads/2021/07/Logotype-KIOS.svg" width="200" height="100"/><a>

# EPANET Python Toolkit (EPyT)

The `EPANET-Python Toolkit` is an open-source software, originally developed by the [KIOS Research and Innovation Center of Excellence, University of Cyprus](http://www.kios.ucy.ac.cy/) which operates within the Python environment, for providing a programming interface for the latest version of [EPANET](https://github.com/OpenWaterAnalytics/epanet), a hydraulic and quality modeling software created by the US EPA, with Python, a  high-level technical computing software. The goal of the EPANET Python Toolkit is to serve as a common programming framework for research and development in the growing field of smart water networks.

The `EPANET-Python Toolkit` features easy to use commands/wrappers for viewing, modifying, simulating and plotting results produced by the EPANET libraries.  

For support, please use the OWA community forum : http://community.wateranalytics.org/

## Table of Contents

- [How to cite](#how-to-cite)
- [Requirements](#requirements)
- [How to install necessary compilers](#How-to-install)
- [How to use the Toolkit](#How-to-use-the-Toolkit)
- [How to fix/report bugs](#How-to-fixreport-bugs)
- [Licenses](#Licenses)
- [Contributors](#Contributors)
- [List of Python Class Functions](#List-of-Python-Class-Functions)
- [List of EPANET 2.2 Functions](#List-of-EPANET-2.2-Functions)
  
## How to cite 

D.G. Eliades, M. Kyriakou, S. Vrachimis and M.M. Polycarpou, "EPANET-MATLAB Toolkit: An Open-Source Software for Interfacing EPANET with MATLAB", in *Proc. 14th International Conference on Computing and Control for the Water Industry (CCWI)*, The Netherlands, Nov 2016, p.8. (doi:10.5281/zenodo.831493)

```
@INPROCEEDINGS{Eliades2016, 
author={Eliades, Demetrios G. and Kyriakou, Marios and Vrachimis, Stelios and Polycarpou, Marios M.}, 
title={EPANET-MATLAB Toolkit: An Open-Source Software for Interfacing EPANET with MATLAB}, 
booktitle={Proc. 14th International Conference on Computing and Control for the Water Industry (CCWI)}, 
year={2016},
pages={8},
address = {The Netherlands},
month={Nov},
DOI={10.5281/zenodo.831493}}
```

&uparrow; [Back to top](#table-of-contents)

## Requirements

* Python 3.7
* Windows, OSX or Linux
* [EPANET 2.2](https://github.com/OpenWaterAnalytics/epanet)

&uparrow; [Back to top](#table-of-contents)

## How to install

* PyPI: <b>pip install epyt</b>
* Anaconda: <b>conda install -c conda-forge epyt</b>

&uparrow; [Back to top](#table-of-contents)

## How to use the Toolkit

Minimum Example:

d = epanet('Net1.inp')

d.getNodeCount()

d.getNodeElevations()

&uparrow; [Back to top](#table-of-contents)

## How to fix/report bugs

To fix a bug `Fork` the `EPyT`, `Edit` the code and make the appropriate change, and then `Pull` it so that we evaluate it. 

Keep in mind that some bugs may exist in the `EPANET` libraries, in case you are not receiving the expected results.

&uparrow; [Back to top](#table-of-contents)

## Licenses

* `EPANET`: Public Domain
* `EPANET-Python Toolkit (EPyT)`: EUPL

&uparrow; [Back to top](#table-of-contents)

## Contributors

* Marios Kyriakou, [KIOS Research and Innovation Center of Excellence, University of Cyprus](http://www.kios.ucy.ac.cy/)
* Marios Demetriades, [KIOS Research and Innovation Center of Excellence, University of Cyprus](http://www.kios.ucy.ac.cy/)
* Stelios Vrachimis, [KIOS Research and Innovation Center of Excellence, University of Cyprus](http://www.kios.ucy.ac.cy/)
* Demetrios Eliades, [KIOS Research and Innovation Center of Excellence, University of Cyprus](http://www.kios.ucy.ac.cy/)

The `EPyT` is based/inspired on the [EPANET-Matlab Toolkit](https://github.com/OpenWaterAnalytics/EPANET-Matlab-Toolkit).

## Recommendation

* Install Anaconda<br>
* Run `EPyT` with [Spyder IDE](https://www.spyder-ide.org/)
* Run `EPyT` with [PyCharm](https://www.jetbrains.com/pycharm/)

*Settings on Spyder IDE*

* Tools -> Preferrences
![image](https://user-images.githubusercontent.com/2945956/154067349-3aed266f-3a23-4573-8b93-db0b4f224964.png)
* View -> Window layouts -> Matlab layout
* Enable interactive plot on matlibplot
  : Tools -> Preferences -> IPython console -> Graphics -> Graphics backend -> Backend: Automatic

&uparrow; [Back to top](#table-of-contents)

## List of Python Class Functions

|Function|Description|
|---------|----------|
|addControls|Adds a new simple control|
|addCurve|Adds a new curve appended to the end of the existing curves|
|addLinkPipe|Adds a new pipe|
|addLinkPipeCV|Adds a new control valve pipe|
|addLinkPump|Adds a new pump|
|addLinkValveFCV|Adds a new FCV valve|
|addLinkValveGPV|Adds a new GPV valve|
|addLinkValvePBV|Adds a new PBV valve|
|addLinkValvePRV|Adds a new PRV valve|
|addLinkValvePSV|Adds a new PSV valve|
|addLinkValveTCV|Adds a new TCV valve|
|addNodeJunction|Adds a new junction|
|addNodeJunctionDemand|Adds a new demand to a junction given the junction index, base demand, demand time pattern and demand category name|
|addNodeReservoir|Adds a new reservoir|
|addNodeTank|Adds a new tank|
|addPattern|Adds a new time pattern to the network|
|addRules|Adds a new rule-based control to a project|
|appRotateNetwork|Rotates the network by theta degrees counter-clockwise|
|appShiftNetwork|Shifts the network|
|clearReport|Clears the contents of a project's report file|
|closeHydraulicAnalysis|Closes the hydraulic analysis system, freeing all allocated memory|
|closeNetwork|Closes down the Toolkit system|
|closeQualityAnalysis|Closes the water quality analysis system, freeing all allocated memory|
|copyReport|Copies the current contents of a project's report file to another file|
|createProject|Creates a new epanet projec|
|deleteAllTemps|Delete all temporary files (.inp, .bin) created in networks folder|
|deleteControls|Deletes an existing simple control|
|deleteCurve|Deletes a data curve from a project|
|deleteLink|Deletes a link|
|deleteNode|Deletes nodes|
|deletePattern|Deletes a time pattern from a project
|deleteProject|Deletes the epanet projec
|deleteRules|Deletes an existing rule-based control given it's index
|getCMDCODE|Retrieves the CMC code|
|getComputedHydraulicTimeSeries|Computes hydraulic simulation and retrieves all time-series
|getComputedQualityTimeSeries|Computes Quality simulation and retrieves all or some time-series
|getComputedTimeSeries|Run analysis with binary fil
|getConnectivityMatrix|Retrieve the Connectivity Matrix of the networ
|getControlRulesCount|Retrieves the number of controls
|getControls|Retrieves the parameters of all control statements
|getCounts|Retrieves the number of network components
|getCurveComment|Retrieves the comment string of a curve
|getCurveCount|Retrieves the number of curves
|getCurveIndex|Retrieves the index of a curve with specific ID
|getCurveLengths|Retrieves number of points in a curve
|getCurveNameID|Retrieves the IDs of curves
|getCurveType|Retrieves the curve-type for all curves
|getCurveTypeIndex|Retrieves the curve-type index for all curves
|getCurveValue|Retrieves the X, Y values of points of curves
|getCurvesInfo|Retrieves all the info of curves
|getDemandModel|Retrieves the type of demand model in use and its parameters
|getENfunctionsImpemented|Retrieves the epanet functions that have been developed
|getError|Retrieves the text of the message associated with a particular error or warning code
|getFlowUnits|Retrieves flow units used to express all flow rates
|getLibFunctions|Retrieves the functions of DLL
|getLinkActualQuality|Retrieves the current computed link quality (read only)
|getLinkBulkReactionCoeff|Retrieves the value of all link bulk chemical reaction coefficient
|getLinkComment|Retrieves the comment string assigned to the link object
|getLinkCount|Retrieves the number of links
|getLinkDiameter|Retrieves the value of link diameters
|getLinkEnergy|Retrieves the current computed pump energy usage (read only)
|getLinkFlows|Retrieves the current computed flow rate (read only)
|getLinkHeadloss|Retrieves the current computed head loss (read only)
|getLinkIndex|Retrieves the indices of all links, or the indices of an ID set of links
|getLinkInitialSetting|Retrieves the value of all link roughness for pipes or initial speed for pumps or initial setting for valves
|getLinkInitialStatus|Retrieves the value of all link initial status
|getLinkLength|Retrieves the value of link lengths
|getLinkMinorLossCoeff|Retrieves the value of link minor loss coefficients
|getLinkNameID|Retrieves the ID label(s) of all links, or the IDs of an index set of links
|getLinkNodesIndex|Retrieves the indexes of the from/to nodes of all links
|getLinkPipeCount|Retrieves the number of pipes
|getLinkPipeIndex|Retrieves the pipe indices
|getLinkPipeNameID|Retrieves the pipe ID
|getLinkPumpCount|Retrieves the number of pumps
|getLinkPumpECost|Retrieves the pump average energy price
|getLinkPumpECurve|Retrieves the pump efficiency v
|getLinkPumpEPat|Retrieves the pump energy price time pattern index
|getLinkPumpEfficiency|Retrieves the current computed pump efficiency (read only)
|getLinkPumpHCurve|Retrieves the pump head v
|getLinkPumpHeadCurveIndex|Retrieves the index of a head curve for all pumps
|getLinkPumpIndex|Retrieves the pump indices
|getLinkPumpNameID|Retrieves the pump ID
|getLinkPumpPatternIndex|Retrieves the pump speed time pattern index
|getLinkPumpPatternNameID|Retrieves pump pattern name ID
|getLinkPumpPower|Retrieves the pump constant power rating (read only)
|getLinkPumpState|Retrieves the current computed pump state (read only) (see @ref EN_PumpStateType)
|getLinkPumpSwitches|Retrieves the number of pump switches
|getLinkPumpType|Retrieves the type of a pump
|getLinkPumpTypeCode|Retrieves the code of type of a pump
|getLinkQuality|Retrieves the value of link quality
|getLinkResultIndex|Retrieves the order in which a link's results were saved to an output file
|getLinkRoughnessCoeff|Retrieves the value of link roughness coefficient
|getLinkSettings|Retrieves the current computed value of all link roughness for pipes or actual speed for pumps or actual setting for valves
|getLinkStatus|Retrieves the current link status (see @ref EN_LinkStatusType) (0 = closed, 1 = open)
|getLinkType|Retrieves the link-type code for all links
|getLinkTypeIndex|Retrieves the link-type code for all links
|getLinkValveCount|Retrieves the number of valves
|getLinkValveIndex|Retrieves the valve indices
|getLinkValveNameID|Retrieves the valve ID
|getLinkVelocity|Retrieves the current computed flow velocity (read only)
|getLinkVertices|Retrieves the coordinate's of a vertex point assigned to a link
|getLinkVerticesCount|Retrieves the number of internal vertex points assigned to a link
|getLinkWallReactionCoeff|Retrieves the value of all pipe wall chemical reaction coefficient
|getLinksInfo|Retrieves all link info
|getNodeActualDemand|Retrieves the computed value of all node actual demands
|getNodeActualDemandSensingNodes|Retrieves the computed demand values at some sensing nodes
|getNodeActualQuality|Retrieves the computed values of the actual quality for all nodes
|getNodeActualQualitySensingNodes|Retrieves the computed quality values at some sensing node
|getNodeBaseDemands|Retrieves the value of all node base demands
|getNodeComment|Retrieves the comment string assigned to the node object
|getNodeCoordinates
|getNodeCount|Retrieves the number of nodes
|getNodeDemandCategoriesNumber|Retrieves the value of all node base demands categorie number
|getNodeDemandDeficit|Retrieves the amount that full demand is reduced under PDA
|getNodeDemandPatternIndex|Retrieves the value of all node base demands pattern index
|getNodeDemandPatternNameID|Retrieves the value of all node base demands pattern name ID
|getNodeElevations|Retrieves the value of all node elevations
|getNodeEmitterCoeff|Retrieves the value of all node emmitter coefficients
|getNodeHydraulicHead|Retrieves the computed values of all node hydraulic heads
|getNodeIndex|Retrieves the indices of all nodes or some nodes with a specified ID
|getNodeInitialQuality|Retrieves the value of all node initial quality
|getNodeJunctionCount|Retrieves the number of junction nodes
|getNodeJunctionDemandIndex|Retrieves the demand index of the junctions
|getNodeJunctionDemandName|Gets the name of a node's demand category
|getNodeJunctionIndex|Retrieves the indices of junctions
|getNodeJunctionNameID|Retrieves the junction ID label
|getNodeMassFlowRate|Retrieves the computed mass flow rates per minute of chemical sources for all nodes
|getNodeNameID|Retrieves the ID label of all nodes or some nodes with a specified index
|getNodePatternIndex|Retrieves the value of all node demand pattern indices
|getNodePressure|Retrieves the computed values of all node pressures
|getNodeReservoirCount|Retrieves the number of Reservoirs
|getNodeReservoirIndex|Retrieves the indices of reservoirs
|getNodeReservoirNameID|Retrieves the reservoir ID label
|getNodeResultIndex|Retrieves the order in which a node's results were saved to an output file
|getNodeSourcePatternIndex|Retrieves the value of all node source pattern index
|getNodeSourceQuality|Retrieves the value of all node source quality
|getNodeSourceType|Retrieves the value of all node source type
|getNodeSourceTypeIndex|Retrieves the value of all node source type index
|getNodeTankBulkReactionCoeff|Retrieves the tank bulk rate coefficient
|getNodeTankCanOverFlow|Retrieves the tank can overflow (= 1) or not (= 0)
|getNodeTankCount|Retrieves the number of Tanks
|getNodeTankData|Retrieves a group of properties for a tank
|getNodeTankDiameter|Retrieves the tank diameters
|getNodeTankIndex|Retrieves the tank indices
|getNodeTankInitialLevel|Retrieves the value of all tank initial water levels
|getNodeTankInitialWaterVolume|Retrieves the tank initial water volume
|getNodeTankMaximumWaterLevel|Retrieves the tank maximum water level
|getNodeTankMaximumWaterVolume|Retrieves the tank maximum water volume
|getNodeTankMinimumWaterLevel|Retrieves the tank minimum water level
|getNodeTankMinimumWaterVolume|Retrieves the tank minimum water volume
|getNodeTankMixZoneVolume|Retrieves the tank mixing zone volume
|getNodeTankMixingFraction|Retrieves the tank Fraction of total volume occupied by the inlet/outlet zone in a 2-compartment tank
|getNodeTankMixingModelCode|Retrieves the tank mixing model code
|getNodeTankMixingModelType|Retrieves the tank mixing model type
|getNodeTankNameID|Retrieves the tank IDs
|getNodeTankReservoirCount|Retrieves the number of tanks
|getNodeTankVolume|Retrieves the tank volume
|getNodeTankVolumeCurveIndex|Retrieves the tank volume curve index
|getNodeType|Retrieves the node-type code for all nodes
|getNodeTypeIndex|Retrieves the node-type code for all nodes
|getNodesConnectingLinksID|Retrieves the id of the from/to nodes of all links
|getNodesConnectingLinksIndex|Retrieves the indexes of the from/to nodes of all links
|getNodesInfo|Retrieves nodes info (elevations, demand patterns, emmitter coeff, initial quality, source quality, source pattern index, source type index, node type index)
|getOptionsAccuracyValue|Retrieves the total normalized flow change for hydraulic convergence
|getOptionsCheckFrequency|Retrieves the frequency of hydraulic status checks
|getOptionsDampLimit|Retrieves the accuracy level where solution damping begins
|getOptionsDemandCharge|Retrieves the energy charge per maximum KW usage
|getOptionsEmitterExponent|Retrieves the power exponent for the emmitters
|getOptionsExtraTrials|Retrieves the extra trials allowed if hydraulics don't converge
|getOptionsFlowChange|Retrieves the maximum flow change for hydraulic convergence
|getOptionsGlobalEffic|Retrieves the global efficiency for pumps(percent)
|getOptionsGlobalPattern|Retrieves the index of the global energy price pattern
|getOptionsGlobalPrice|Retrieves the global average energy price per kW-Hour
|getOptionsHeadError|Retrieves the maximum head loss error for hydraulic convergence
|getOptionsHeadLossFormula|Retrieves the headloss formula
|getOptionsLimitingConcentration|Retrieves the limiting concentration for growth reactions
|getOptionsMaxTrials|Retrieves the maximum hydraulic trials allowed for hydraulic convergence
|getOptionsMaximumCheck|Retrieves the maximum trials for status checking
|getOptionsPatternDemandMultiplier|Retrieves the global pattern demand multiplier
|getOptionsPipeBulkReactionOrder|Retrieves the bulk water reaction order for pipes
|getOptionsPipeWallReactionOrder|Retrieves the wall reaction order for pipes (either 0 or 1)
|getOptionsQualityTolerance|Retrieves the water quality analysis tolerance
|getOptionsSpecificDiffusivity|Retrieves the specific diffusivity (relative to chlorine at 20 deg C)
|getOptionsSpecificGravity|Retrieves the specific gravity
|getOptionsSpecificViscosity|Retrieves the specific viscosity
|getOptionsTankBulkReactionOrder|Retrieves the bulk water reaction order for tanks
|getPattern|Retrieves the multiplier factor for all patterns and all times
|getPatternAverageValue|Retrieves the average values of all the time patterns
|getPatternComment|Retrieves the comment string assigned to the pattern object
|getPatternCount|Retrieves the number of patterns
|getPatternIndex|Retrieves the index of all or some time patterns given their IDs
|getPatternLengths|Retrieves the number of time periods in all or some time patterns
|getPatternNameID|Retrieves the ID label of all or some time patterns indices
|getPatternValue|Retrieves the multiplier factor for a certain pattern and time
|getQualityCode|Retrieves the code of water quality analysis type
|getQualityInfo|Retrieves quality analysis information (type, chemical name, units, trace node ID)
|getQualityTraceNodeIndex|Retrieves the trace node index of water quality analysis type
|getQualityType|Retrieves the type of water quality analysis type
|getRuleCount|Retrieves the number of rules
|getRuleID|Retrieves the ID name of a rule-based control given its index
|getRuleInfo|Retrieves summary information about a rule-based control given it's index
|getRules|Retrieves the rule - based control statements
|getStatistic|Returns error code
|getTimeHTime|Retrieves the elapsed time of current hydraulic solution
|getTimeHaltFlag|Retrieves the number of halt flag indicating if the simulation was halted
|getTimeHydraulicStep|Retrieves the value of the hydraulic time step
|getTimeNextEvent|Retrieves the shortest time until a tank becomes empty or full
|getTimeNextEventTank|Retrieves the index of tank with shortest time to become empty or full
|getTimePatternStart|Retrieves the value of pattern start time
|getTimePatternStep|Retrieves the value of the pattern time step
|getTimeQTime|Retrieves the elapsed time of current quality solution
|getTimeQualityStep|Retrieves the value of the water quality time step
|getTimeReportingPeriods|Retrieves the number of reporting periods saved to the binary
|getTimeReportingStart|Retrieves the value of the reporting start time
|getTimeReportingStep|Retrieves the value of the reporting time step
|getTimeRuleControlStep|Retrieves the time step for evaluating rule-based controls
|getTimeSimulationDuration|Retrieves the value of simulation duration
|getTimeStartTime|Retrieves the simulation starting time of day
|getTimeStatisticsIndex|Retrieves the index of the type of time series post-processing
|getTimeStatisticsType|Retrieves the type of time series post-processing
|getTitle|Retrieves the title lines of the project
|getUnits|Retrieves the Units of Measurement
|getVersion|Retrieves the current EPANET version of DLL
|initializeEPANET|Initializes an EPANET project that isn't opened with an input fil
|initializeHydraulicAnalysis|Initializes storage tank levels, link status and settings, and the simulation clock time prior to running a hydraulic analysis
|initializeQualityAnalysis|Initializes water quality and the simulation clock time prior to running a water quality analysis
|loadEPANETFile|Load epanet file when use bin functions
|nextHydraulicAnalysisStep|Determines the length of time until the next hydraulic event occurs in an extended period simulation
|nextQualityAnalysisStep|Advances the water quality simulation to the start of the next hydraulic time period
|openAnyInp|Open as on matlab editor any EPANET input file using built function open
|openCurrentInp|Opens EPANET input file who is loade
|openHydraulicAnalysis|Opens the hydraulics analysis system
|openQualityAnalysis|Opens the water quality analysis system
|plot|Plot Network, show all components, plot pressure/flow/elevation|
|reloadNetwork|Reloads the Network (ENopen)
|runEPANETexe|Runs epanet .exe file|
|runHydraulicAnalysis|Runs a single period hydraulic analysis, retrieving the current simulation clock time t
|runQualityAnalysis|Makes available the hydraulic and water quality results that occur at the start of the next time period of a water quality analysis, where the start of the period is returned in t
|runsCompleteSimulation|Runs a complete hydraulic and water simulation to create binary & report files with name: [NETWORK_temp.txt], [NETWORK_temp.bin] OR you can use argument to runs a complete simulation via self.api.en_epane
|saveHydraulicFile|Saves the current contents of the binary hydraulics file to a file
|saveHydraulicsOutputReportingFile|Transfers results of a hydraulic simulation from the binary Hydraulics file to the binary Output file, where results are only reported at uniform reporting intervals
|saveInputFile|Writes all current network input data to a file using the format of an EPANET input file
|setCMDCODE|Sets the CMC code|
|setControls|Sets the parameters of a simple control statement
|setCurve|Sets x, y values for a specific curve
|setCurveComment|Sets the comment string of a curve
|setCurveNameID|Sets the name ID of a curve given it's index and the new ID
|setCurveValue|Sets x, y point for a specific point number and curve
|setDemandModel|Sets the type of demand model to use and its parameters
|setFlowUnitsAFD|Sets flow units to AFD(Acre-Feet per Day)
|setFlowUnitsCFS|Sets flow units to CFS(Cubic Feet per Second)
|setFlowUnitsCMD|Sets flow units to CMD(Cubic Meters per Day)
|setFlowUnitsCMH|Sets flow units to CMH(Cubic Meters per Hour)
|setFlowUnitsGPM|Sets flow units to GPM(Gallons Per Minute)
|setFlowUnitsIMGD|Sets flow units to IMGD(Imperial Million Gallons per Day)
|setFlowUnitsLPM|Sets flow units to LPM(Liters Per Minute)
|setFlowUnitsLPS|Sets flow units to LPS(Liters Per Second)
|setFlowUnitsMGD|Sets flow units to MGD(Million Gallons per Day)
|setFlowUnitsMLD|Sets flow units to MLD(Million Liters per Day)
|setLinkBulkReactionCoeff|Sets the value of bulk chemical reaction coefficient
|setLinkComment|Sets the comment string assigned to the link object
|setLinkDiameter|Sets the values of diameters
|setLinkInitialSetting|Sets the values of initial settings, roughness for pipes or initial speed for pumps or initial setting for valves
|setLinkInitialStatus|Sets the values of initial status
|setLinkLength|Sets the values of lengths
|setLinkMinorLossCoeff|Sets the values of minor loss coefficient
|setLinkNameID|Sets the ID name for links
|setLinkNodesIndex|Sets the indexes of a link's start- and end-nodes
|setLinkPipeData|Sets a group of properties for a pipe
|setLinkPumpECost|Sets the pump average energy price
|setLinkPumpECurve|Sets the pump efficiency v
|setLinkPumpEPat|Sets the pump energy price time pattern index
|setLinkPumpHCurve|Sets the pump head v
|setLinkPumpHeadCurveIndex|Sets the curves index for pumps index|
|setLinkPumpPatternIndex|Sets the pump speed time pattern index
|setLinkPumpPower|Sets the power for pumps
|setLinkRoughnessCoeff|Sets the values of roughness coefficient
|setLinkSettings|Sets the values of current settings, roughness for pipes or initial speed for pumps or initial setting for valves
|setLinkStatus|Sets the values of current status for links
|setLinkTypePipe|Sets the link type pipe for a specified link
|setLinkTypePipeCV|Sets the link type cvpipe(pipe with check valve) for a specified link
|setLinkTypePump|Sets the link type pump for a specified link
|setLinkTypeValveFCV|Sets the link type valve FCV(flow control valve) for a specified link
|setLinkTypeValveGPV|Sets the link type valve GPV(general purpose valve) for a specified link
|setLinkTypeValvePBV|Sets the link type valve PBV(pressure breaker valve) for a specified link
|setLinkTypeValvePRV|Sets the link type valve PRV(pressure reducing valve) for a specified link
|setLinkTypeValvePSV|Sets the link type valve PSV(pressure sustaining valve) for a specified link
|setLinkTypeValveTCV|Sets the link type valve TCV(throttle control valve) for a specified link
|setLinkVertices|Assigns a set of internal vertex points to a link
|setLinkWallReactionCoeff|Sets the value of wall chemical reaction coefficient
|setNodeBaseDemands|Sets the values of demand for nodes
|setNodeComment|Sets the comment string assigned to the node object
|setNodeCoordinates|Sets node coordinates
|setNodeDemandPatternIndex|Sets the values of demand time pattern indices
|setNodeElevations|Sets the values of elevation for nodes
|setNodeEmitterCoeff|Sets the values of emitter coefficient for nodes
|setNodeInitialQuality|Sets the values of initial quality for nodes
|setNodeJunctionData|Sets a group of properties for a junction node
|setNodeJunctionDemandName|Assigns a name to a node's demand category
|setNodeNameID|Sets the ID name for nodes
|setNodeSourcePatternIndex|Sets the values of quality source pattern index
|setNodeSourceQuality|Sets the values of quality source strength
|setNodeSourceType|Sets the values of quality source type
|setNodeTankBulkReactionCoeff|Sets the tank bulk reaction coefficient
|setNodeTankCanOverFlow|Sets the tank can-overflow (= 1) or not (= 0)
|setNodeTankData|Sets a group of properties for a tank
|setNodeTankDiameter|Sets the diameter value for tanks
|setNodeTankInitialLevel|Sets the values of initial level for tanks
|setNodeTankMaximumWaterLevel|Sets the maximum water level value for tanks
|setNodeTankMinimumWaterLevel|Sets the minimum water level value for tanks
|setNodeTankMinimumWaterVolume|Sets the minimum water volume value for tanks
|setNodeTankMixingFraction|Sets the tank mixing fraction of total volume occupied by the inlet/outlet zone in a 2-compartment tank
|setNodeTankMixingModelType|Sets the mixing model type value for tanks
|setNodeTypeJunction|Transforms a node to JUNCTION The new node keeps the id,coordinates and elevation of the deleted on
|setNodeTypeReservoir|Transforms a node to RESERVOIR The new node keeps the id,coordinates and elevation of the deleted on
|setNodeTypeTank|Transforms a node to TANK The new node keeps the id,coordinates and elevation of the deleted on
|setNodesConnectingLinksID|Sets the IDs of a link's start- and end-nodes
|setOptionsAccuracyValue|Sets the total normalized flow change for hydraulic convergence
|setOptionsCheckFrequency|Sets the frequency of hydraulic status checks
|setOptionsDampLimit|Sets the accuracy level where solution damping begins
|setOptionsDemandCharge|Sets the energy charge per maximum KW usage
|setOptionsEmitterExponent|Sets the power exponent for the emmitters
|setOptionsExtraTrials|Sets the extra trials allowed if hydraulics don't converge
|setOptionsFlowChange|Sets the maximum flow change for hydraulic convergence
|setOptionsGlobalEffic|Sets the global efficiency for pumps(percent)
|setOptionsGlobalPattern|Sets the global energy price pattern
|setOptionsGlobalPrice|Sets the global average energy price per kW-Hour
|setOptionsHeadError|Sets the maximum head loss error for hydraulic convergence
|setOptionsHeadLossFormula|Sets the headloss formula
|setOptionsLimitingConcentration|Sets the limiting concentration for growth reactions
|setOptionsMaxTrials|Sets the maximum hydraulic trials allowed for hydraulic convergence
|setOptionsMaximumCheck|Sets the maximum trials for status checking
|setOptionsPatternDemandMultiplier|Sets the global pattern demand multiplier
|setOptionsPipeBulkReactionOrder|Sets the bulk water reaction order for pipes
|setOptionsPipeWallReactionOrder|Sets the wall reaction order for pipes (either 0 or 1)
|setOptionsQualityTolerance|Sets the water quality analysis tolerance
|setOptionsSpecificDiffusivity|Sets the specific diffusivity (relative to chlorine at 20 deg C)
|setOptionsSpecificGravity|Sets the specific gravity
|setOptionsSpecificViscosity|Sets the specific viscosity
|setOptionsTankBulkReactionOrder|Sets the bulk water reaction order for tanks
|setPattern|Sets all of the multiplier factors for a specific time pattern
|setPatternComment|Sets the comment string assigned to the pattern object
|setPatternMatrix|Sets all of the multiplier factors for all time patterns
|setPatternNameID|Sets the name ID of a time pattern given it's index and the new ID
|setPatternValue|Sets the multiplier factor for a specific period within a time pattern
|setQualityType|Sets the type of water quality analysis called for
|setReport|Issues a report formatting command
|setReportFormatReset|Resets a project's report options to their default values
|setReportStatus|Sets the level of hydraulic status reporting
|setRuleElseAction|Sets rule - based control else actions
|setRulePremise|Sets the premise of a rule - based control
|setRulePremiseObejctNameID|Sets the ID of an object in a premise of a rule-based control
|setRulePremiseStatus|Sets the status being compared to in a premise of a rule-based control
|setRulePremiseValue|Sets the value being compared to in a premise of a rule-based control
|setRulePriority|Sets rule - based control priority
|setRuleThenAction|Sets rule - based control then actions
|setRules|Sets a rule - based control
|setTimeHydraulicStep|Sets the hydraulic time step
|setTimePatternStart|Sets the time when time patterns begin
|setTimePatternStep|Sets the time pattern step
|setTimeQualityStep|Sets the quality time step
|setTimeReportingStart|Sets the time when reporting starts
|setTimeReportingStep|Sets the reporting time step
|setTimeRuleControlStep|Sets the rule-based control evaluation time step
|setTimeSimulationDuration|Sets the simulation duration (in seconds)
|setTimeStatisticsType|Sets the statistic type
|setTitle|Sets the title lines of the project
|solveCompleteHydraulics|Runs a complete hydraulic simulation with results for all time periods written to the binary Hydraulics file
|solveCompleteQuality|Runs a complete water quality simulation with results at uniform reporting intervals written to EPANET's binary Output file
|splitPipe|Splits a pipe, creating two new pipes and adds a junction/node in between
|stepQualityAnalysisTimeLeft|Advances the water quality simulation one water quality time step
|unload|unload library and close the EPANET Toolkit system
|useHydraulicFile|Uses the contents of the specified file as the current binary hydraulics file
|writeLineInReportFile|Writes a line of text to the EPANET report file
|writeReport|Writes a formatted text report on simulation results to the Report file

## List of EPANET 2.2 Functions 

|Function|Description|
|---------|----------|
|ENepanet|Runs a complete EPANET simulation
|ENaddcontrol|Adds a new simple control to a project
|ENaddcurve|Adds a new data curve to a project
|ENadddemand|Appends a new demand to a junction node demands list
|ENaddlink|Adds a new link to a project
|ENaddnode|Adds a new node to a project
|ENaddpattern|Adds a new time pattern to a project
|ENaddrule|Adds a new rule-based control to a project
|ENclearreport|Clears the contents of a project's report file
|ENclose|Closes a project and frees all of its memory
|ENcloseH|Closes the hydraulic solver freeing all of its allocated memory
|ENcloseQ|Closes the water quality solver, freeing all of its allocated memory
|ENcopyreport|Copies the current contents of a project's report file to another file
|ENcreateproject|Copies the current contents of a project's report file to another file
|ENdeletecontrol|Deletes an existing simple control
|ENdeletecurve|Deletes a data curve from a project
|ENdeletedemand|Deletes a demand from a junction node
|ENdeletelink|Deletes a link from the project
|ENdeletenode|Deletes a node from a project
|ENdeletepattern|Deletes a time pattern from a project
|ENdeleteproject|Deletes an EPANET project
|ENdeleterule|Deletes an existing rule-based control
|ENgetaveragepatternvalue|Retrieves the average of all pattern factors in a time pattern
|ENgetbasedemand|Gets the base demand for one of a node's demand categories
|ENgetcomment|Sets a comment to a specific index
|ENgetcontrol|Retrieves the comment of a specific index of a type object
|ENgetcoord|Gets the (x,y) coordinates of a node
|ENgetcount|Retrieves the number of objects of a given type in a project
|ENgetcurve|Retrieves all of a curve's data
|ENgetcurveid|Retrieves the ID name of a curve given its index
|ENgetcurveindex|Retrieves the index of a curve given its ID name
|ENgetcurvelen|Retrieves the number of points in a curve
|ENgetcurvetype|Retrieves a curve's type
|ENgetcurvevalue|Retrieves the value of a single data point for a curve
|ENgetdemandindex|Retrieves the index of a node's named demand category
|ENgetdemandmodel|Retrieves the type of demand model in use and its parameters
|ENgetdemandname|Retrieves the name of a node's demand category
|ENgetdemandpattern|Retrieves the index of a time pattern assigned to one of a node's demand categories
|ENgetelseaction|Gets the properties of an ELSE action in a rule-based control
|ENgeterror|Returns the text of an error message generated by an error code, as warning
|ENgetflowunits|Retrieves a project's flow units
|ENgetheadcurveindex|Retrieves the curve assigned to a pump's head curve
|ENgetlinkid|Gets the ID name of a link given its index
|ENgetlinkindex|Gets the index of a link given its ID name
|ENgetlinknodes|Gets the indexes of a link's start- and end-nodes
|ENgetlinktype|Retrieves a link's type
|ENgetlinkvalue|Retrieves a property value for a link
|ENgetnodeid|Gets the ID name of a node given its index
|ENgetnodeindex|Gets the index of a node given its ID name
|ENgetnodetype|Retrieves a node's type given its index
|ENgetnodevalue|Retrieves a property value for a node
|ENgetnumdemands|Retrieves the number of demand categories for a junction node
|ENgetoption|Retrieves the value of an analysis option
|ENgetpatternid|Retrieves the ID name of a time pattern given its index
|ENgetpatternindex|Retrieves the index of a time pattern given its ID name
|ENgetpatternlen|Retrieves the number of time periods in a time pattern
|ENgetpatternvalue|Retrieves a time pattern's factor for a given time period
|ENgetpremise|Gets the properties of a premise in a rule-based control
|ENgetpumptype|Retrieves the type of head curve used by a pump
|ENgetqualinfo|Gets information about the type of water quality analysis requested
|ENgetqualtype|Retrieves the type of water quality analysis to be run
|ENgetresultindex|Retrieves the order in which a node or link appears in an output file
|ENgetrule|Retrieves summary information about a rule-based control
|ENgetruleID|Gets the ID name of a rule-based control given its index
|ENgetstatistic|Retrieves a particular simulation statistic
|ENgetthenaction|Gets the properties of a THEN action in a rule-based control
|ENgettimeparam|Retrieves the value of a time parameter
|ENgettitle|Retrieves the title lines of the project
|ENgetversion|Retrieves the toolkit API version number
|ENgetvertex|Retrieves the coordinate's of a vertex point assigned to a link
|ENgetvertexcount|Retrieves the number of internal vertex points assigned to a link
|ENinit|Initializes an EPANET project
|ENinitH|Initializes a network prior to running a hydraulic analysis
|ENinitQ|Initializes a network prior to running a water quality analysis
|ENnextH| Determines the length of time until the next hydraulic event occurs in an extended period simulation
|ENnextQ|Advances a water quality simulation over the time until the next hydraulic event
|ENopen|Opens an EPANET input file & reads in network data
|ENopenH|Opens a project's hydraulic solver
|ENopenQ|Opens a project's water quality solver
|ENreport|Writes simulation results in a tabular format to a project's report file
|ENresetreport|Resets a project's report options to their default values
|ENrunH|Computes a hydraulic solution for the current point in time
|ENrunQ|Makes hydraulic and water quality results at the start of the current time period available to a project's water quality solver
|ENsaveH|Transfers a project's hydraulics results from its temporary hydraulics file to its binary output file, where results are only reported at uniform reporting intervals
|ENsavehydfile|Saves a project's temporary hydraulics file to disk
|ENsaveinpfile|Saves a project's data to an EPANET-formatted text file
|ENsetbasedemand|Sets the base demand for one of a node's demand categories
|ENsetcomment|Sets a comment to a specific index
|ENsetcontrol|Sets the properties of an existing simple control
|ENsetcoord|Sets the (x,y) coordinates of a node
|ENsetcurve|Assigns a set of data points to a curve
|ENsetcurveid|Changes the ID name of a data curve given its index
|ENsetcurvevalue|Sets the value of a single data point for a curve
|ENsetdemandmodel|Sets the Type of demand model to use and its parameters
|ENsetdemandname|Assigns a name to a node's demand category
|ENsetdemandpattern|Sets the index of a time pattern used for one of a node's demand categories
|ENsetelseaction|Sets the properties of an ELSE action in a rule-based control
|ENsetflowunits|Sets a project's flow units
|ENsetheadcurveindex|Assigns a curve to a pump's head curve
|ENsetjuncdata|Sets a group of properties for a junction node
|ENsetlinkid|Changes the ID name of a link
|ENsetlinknodes|Sets the indexes of a link's start- and end-nodes
|ENsetlinktype|Changes a link's type
|ENsetlinkvalue|Sets a property value for a link
|ENsetnodeid|Changes the ID name of a node
|ENsetnodevalue|Sets a property value for a node
|ENsetoption|Sets the value for an anlysis option
|ENsetpattern|Sets the pattern factors for a given time pattern
|ENsetpatternid|Changes the ID name of a time pattern given its index
|ENsetpatternvalue|Sets a time pattern's factor for a given time period
|ENsetpipedata|Sets a group of properties for a pipe link
|ENsetpremise|Sets the properties of a premise in a rule-based control
|ENsetpremiseindex|Sets the index of an object in a premise of a rule-based control
|ENsetpremisestatus|Sets the status being compared to in a premise of a rule-based control
|ENsetpremisevalue|Sets the value in a premise of a rule-based control
|ENsetqualtype|Sets the type of water quality analysis to run
|ENsetreport|Processes a reporting format command
|ENsetrulepriority|Sets the priority of a rule-based control
|ENsetstatusreport|Sets the level of hydraulic status reporting
|ENsettankdata|Sets a group of properties for a tank node
|ENsetthenaction|Sets the properties of a THEN action in a rule-based control
|ENsettimeparam|Sets the value of a time parameter
|ENsettitle|Sets the title lines of the project
|ENsetvertices|Assigns a set of internal vertex points to a link
|ENsolveH|Runs a complete hydraulic simulation with results for all time periods written to a temporary hydraulics file
|ENsolveQ| Runs a complete water quality simulation with results at uniform reporting intervals written to the project's binary output file
|ENstepQ|Advances a water quality simulation by a single water quality time step
|ENusehydfile|Uses a previously saved binary hydraulics file to supply a project's hydraulics
|ENwriteline|Writes a line of text to a project's report file

&uparrow; [Back to top](#table-of-contents)

"""
   EPANET-Python Toolkit (EPyT): A Python toolkit for EPANET libraries

   How to run:
   from epyt import epanet
   d = epanet('Net1.inp')

   EPANET is software that models water distribution piping systems
   developed by the US EPA and provided under a public domain licence.
   This python toolkit serves as an interface between Python and
   EPANET, to assist researchers and the industry when
   solving problems related with water distribution systems.

   EPANET was developed by the Water Supply and Water
   Resources Division of the U.S. Environmental Protection Agency's
   National Risk Management Research Laboratory. EPANET is under the
   Public Domain.

   The latest EPANET files can downloaded at:
   https://github.com/OpenWaterAnalytics/EPANET

   Inspired by:
   EPANET-MATLAB Toolkit
   D.G. Eliades, M. Kyriakou, S. Vrachimis and M.M. Polycarpou, "EPANET-MATLAB Toolkit:
   An Open-Source Software for Interfacing EPANET with MATLAB", in Proc. 14th International
   Conference on Computing and Control for the Water Industry (CCWI),
   The Netherlands, Nov 2016, p.8. (doi:10.5281/zenodo.831493)

   wntr
   Klise, K.A., Murray, R., Haxton, T. (2018). An overview of the Water Network Tool for Resilience (WNTR),
   In Proceedings of the 1st International WDSA/CCWI Joint Conference, Kingston, Ontario, Canada, July 23-25, 075, 8p.

   epanet-python
   The home for Python packages related to the EPANET engine.
   https://github.com/OpenWaterAnalytics/epanet-python

   EPANET-Python Toolkit Licence:

   Copyright 2022 KIOS Research and Innovation Center of Excellence (KIOS CoE),
   University of Cyprus (www.kios.org.cy)

   Licensed under the EUPL, Version 1.2 or - as soon they will be
   approved by the European Commission - subsequent libepanets of the
   EUPL (the "Licence") You may not use this work except in
   compliance with the Licence. You may obtain a copy of the Licence
   at:

   https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12

   Unless required by applicable law or agreed to in writing, software
   distributed under the Licence is distributed on an "AS IS" basis,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied. See the Licence for the specific language governing
   permissions and limitations under the Licence.
"""
from pkg_resources import resource_filename
from inspect import getmembers, isfunction, currentframe, getframeinfo
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib import cm
import matplotlib as mpl
from pathlib import Path
import pandas as pd
import numpy as np
import subprocess
import platform
import warnings
import random
import string
import struct
import ctypes
import math
import json
import sys
import os
import re


class ToolkitConstants:
    # Limits on the size of character arrays used to store ID names
    # and text messages.
    EN_MAXID = 31 + 1  # characters in ID name
    EN_MAXMSG = 255  # characters in message text

    # Node parameters
    EN_ELEVATION = 0
    EN_BASEDEMAND = 1
    EN_PATTERN = 2
    EN_EMITTER = 3
    EN_INITQUAL = 4
    EN_SOURCEQUAL = 5
    EN_SOURCEPAT = 6
    EN_SOURCETYPE = 7
    EN_TANKLEVEL = 8
    EN_DEMAND = 9
    EN_HEAD = 10
    EN_PRESSURE = 11
    EN_QUALITY = 12
    EN_SOURCEMASS = 13
    EN_INITVOLUME = 14
    EN_MIXMODEL = 15
    EN_MIXZONEVOL = 16
    EN_TANKDIAM = 17
    EN_MINVOLUME = 18
    EN_VOLCURVE = 19
    EN_MINLEVEL = 20
    EN_MAXLEVEL = 21
    EN_MIXFRACTION = 22
    EN_TANK_KBULK = 23
    EN_TANKVOLUME = 24
    EN_MAXVOLUME = 25
    EN_CANOVERFLOW = 26
    EN_DEMANDDEFICIT = 27

    # Link parameters
    EN_DIAMETER = 0
    EN_LENGTH = 1
    EN_ROUGHNESS = 2
    EN_MINORLOSS = 3
    EN_INITSTATUS = 4
    EN_INITSETTING = 5
    EN_KBULK = 6
    EN_KWALL = 7
    EN_FLOW = 8
    EN_VELOCITY = 9
    EN_HEADLOSS = 10
    EN_STATUS = 11
    EN_SETTING = 12
    EN_ENERGY = 13
    EN_LINKQUAL = 14
    EN_LINKPATTERN = 15
    EN_PUMP_STATE = 16
    EN_PUMP_EFFIC = 17
    EN_PUMP_POWER = 18
    EN_PUMP_HCURVE = 19
    EN_PUMP_ECURVE = 20
    EN_PUMP_ECOST = 21
    EN_PUMP_EPAT = 22

    # Time parameters
    EN_DURATION = 0
    EN_HYDSTEP = 1
    EN_QUALSTEP = 2
    EN_PATTERNSTEP = 3
    EN_PATTERNSTART = 4
    EN_REPORTSTEP = 5
    EN_REPORTSTART = 6
    EN_RULESTEP = 7
    EN_STATISTIC = 8
    EN_PERIODS = 9
    EN_STARTTIME = 10
    EN_HTIME = 11
    EN_QTIME = 12
    EN_HALTFLAG = 13
    EN_NEXTEVENT = 14
    EN_NEXTEVENTTANK = 15

    # Component counts
    EN_NODECOUNT = 0
    EN_TANKCOUNT = 1
    EN_LINKCOUNT = 2
    EN_PATCOUNT = 3
    EN_CURVECOUNT = 4
    EN_CONTROLCOUNT = 5
    EN_RULECOUNT = 6

    # Node types
    EN_JUNCTION = 0
    EN_RESERVOIR = 1
    EN_TANK = 2

    # Link types
    EN_CVPIPE = 0
    EN_PIPE = 1
    EN_PUMP = 2
    EN_PRV = 3
    EN_PSV = 4
    EN_PBV = 5
    EN_FCV = 6
    EN_TCV = 7
    EN_GPV = 8

    # Quality analysis types
    EN_NONE = 0
    EN_CHEM = 1
    EN_AGE = 2
    EN_TRACE = 3

    # Source quality types
    EN_CONCEN = 0
    EN_MASS = 1
    EN_SETPOINT = 2
    EN_FLOWPACED = 3

    # Flow units types
    EN_CFS = 0
    EN_GPM = 1
    EN_MGD = 2
    EN_IMGD = 3
    EN_AFD = 4
    EN_LPS = 5
    EN_LPM = 6
    EN_MLD = 7
    EN_CMH = 8
    EN_CMD = 9

    # Option types
    EN_TRIALS = 0
    EN_ACCURACY = 1
    EN_TOLERANCE = 2
    EN_EMITEXPON = 3
    EN_DEMANDMULT = 4
    EN_HEADERROR = 5
    EN_FLOWCHANGE = 6
    EN_HEADLOSSFORM = 7
    EN_GLOBALEFFIC = 8
    EN_GLOBALPRICE = 9
    EN_GLOBALPATTERN = 10
    EN_DEMANDCHARGE = 11
    EN_SP_GRAVITY = 12
    EN_SP_VISCOS = 13
    EN_UNBALANCED = 14
    EN_CHECKFREQ = 15
    EN_MAXCHECK = 16
    EN_DAMPLIMIT = 17
    EN_SP_DIFFUS = 18
    EN_BULKORDER = 19
    EN_WALLORDER = 20
    EN_TANKORDER = 21
    EN_CONCENLIMIT = 22

    # Control types
    EN_LOWLEVEL = 0
    EN_HILEVEL = 1
    EN_TIMER = 2
    EN_TIMEOFDAY = 3

    # Time statistic types
    EN_AVERAGE = 1
    EN_MINIMUM = 2
    EN_MAXIMUM = 3
    EN_RANGE = 4

    # Tank mixing models
    EN_MIX1 = 0
    EN_MIX2 = 1
    EN_FIFO = 2
    EN_LIFO = 3

    # Save-results-to-file flag
    EN_NOSAVE = 0
    EN_SAVE = 1
    EN_INITFLOW = 10
    EN_SAVE_AND_INIT = 11

    # ObjectType
    EN_NODE = 0
    EN_LINK = 1
    EN_TIMEPAT = 2
    EN_CURVE = 3
    EN_CONTROL = 4
    EN_RULE = 5

    # Head Loss Type
    EN_HW = 0
    EN_DW = 1
    EN_CM = 2

    # Network objects used in rule-based controls
    EN_R_NODE = 6
    EN_R_LINK = 7
    EN_R_SYSTEM = 8

    # Object variables used in rule-based controls.
    EN_R_DEMAND = 0
    EN_R_HEAD = 1
    EN_R_GRADE = 2
    EN_R_LEVEL = 3
    EN_R_PRESSURE = 4
    EN_R_FLOW = 5
    EN_R_STATUS = 6
    EN_R_SETTING = 7
    EN_R_POWER = 8
    EN_R_TIME = 9
    EN_R_CLOCKTIME = 10
    EN_R_FILLTIME = 11
    EN_R_DRAINTIME = 12

    # Analysis convergence statistics.
    EN_ITERATIONS = 0
    EN_RELATIVEERROR = 1
    EN_MAXHEADERROR = 2
    EN_MAXFLOWCHANGE = 3
    EN_MASSBALANCE = 4
    EN_DEFICIENTNODES = 5
    EN_DEMANDREDUCTION = 6

    # Link status codes used in rule-based controls
    EN_R_IS_OPEN = 1
    EN_R_IS_CLOSED = 2
    EN_R_IS_ACTIVE = 3


class val:

    def __init__(self):
        pass
        # self.RelativeError = None

    def disp(Vals):
        """ Displays the values on the command window

        :param Vals: Values to be printed on the command window
        :type Vals: val class
        :return: None

        """
        values = vars(Vals)
        print('\n')
        for i in values:
            print(f'{i}: {values[str(i)]}', end='\n')

    def to_dict(Vals):
        """ Transform val class values to dict format

        :param Vals: Values to add in the dictionary
        :type Vals: val class
        :return: dictionary with the values
        :rtype: dict

        """
        values = vars(Vals)
        return values

    def to_excel(Vals, filename=None, attributes=None, allValues=False):
        """ Save to an excel file the values of val clas

        :param Vals: Values to add to the excel file
        :type Vals: val class
        :param filename: excel filename, defaults to None
        :type filename: str, optional
        :param attributes: attributes to add to the file, defaults to None
        :type attributes: str or list of str, optional
        :param allValues: 'True' if all the values will be included in a
            seperate sheet, defaults to False
        :type allValues: bool, optional
        :return: None

        """
        if not filename:
            rand_id = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            filename = 'ToExcelfile_' + rand_id + '.xlsx'
        if '.xlsx' not in filename: filename = filename + '.xlsx'
        dictVals = val.to_dict(Vals)
        dictValss = {}
        for i in dictVals:
            if isinstance(dictVals[i], (np.ndarray, np.matrix)):
                dictValss[i] = dictVals[i].transpose().tolist()
            else:
                dictValss[i] = dictVals[i]
        dictVals = dictValss
        with pd.ExcelWriter(filename, mode="w") as writer:
            for key in dictVals:
                if key != 'Time':
                    if not attributes:
                        df = pd.DataFrame(dictVals[key])
                        df.insert(0, "Index", list(range(1, len(dictVals[key]) + 1)), True)
                        df.set_index("Index", inplace=True)
                        df.to_excel(writer, sheet_name=key, header=dictVals['Time'])
                    else:
                        if not isList(attributes):
                            attributes = [attributes]
                        if key in attributes:
                            df = pd.DataFrame(dictVals[key])
                            df.insert(0, "Index", list(range(1, len(dictVals[key]) + 1)), True)
                            df.set_index("Index", inplace=True)
                            df.to_excel(writer, sheet_name=key, header=dictVals['Time'])
            if allValues:
                first_iter = True
                titleFormat = writer.book.add_format(
                    {'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 16})
                for key in dictVals:
                    if key != 'Time' and not attributes:
                        df = pd.DataFrame(dictVals[key])
                        df.insert(0, "Index", list(range(1, len(dictVals[key]) + 1)), True)
                        df.set_index("Index", inplace=True)
                        if first_iter:
                            df.to_excel(
                                writer,
                                sheet_name='All values',
                                header=dictVals['Time'],
                                startrow=1
                            )
                            writer.book.worksheets()[-1].write(0, 1, key, titleFormat)
                            first_iter = False
                        else:
                            startrow = writer.book.worksheets()[-1].dim_rowmax + 3
                            writer.book.worksheets()[-1].write(startrow - 1, 1, key, titleFormat)
                            df.to_excel(
                                writer,
                                sheet_name='All values',
                                header=dictVals['Time'],
                                startrow=startrow
                            )

    def to_json(Vals, filename=None):
        """ Transforms val class values to json object and saves them
        to a json file if filename is provided

        :param Vals: Values to add in the json file
        :type Vals: val class
        :param filename: json filename, defaults to None
        :type filename: str, optional
        :return: the json object with the values
        :rtype: json object

        """
        dictVals = val.to_dict(Vals)
        dictValss = {}
        for i in dictVals:
            if isinstance(dictVals[i], (np.ndarray, np.matrix)):
                dictValss[i] = dictVals[i].tolist()
            else:
                dictValss[i] = dictVals[i]
        json_object = json.dumps(dictValss, indent=2)
        if filename:
            if '.json' not in filename:
                filename = filename + '.json'
            f = open(filename, "w")
            f.write(json_object)
        return json_object


def isList(var):
    if isinstance(var, (list, np.ndarray, np.matrix)):
        return True
    else:
        return False


class epanet:
    """ EPyt main functions class """

    def __init__(self, *argv, version=2.2, loadfile=False):


        # Initial attributes
        self.classversion = '0.0.3'
        self.api = epanetapi(version)
        print(f'EPANET version {self.getVersion()} loaded (EPyT version {self.classversion}).')
        self.ToolkitConstants = ToolkitConstants()
        self.api.solve = 0

        if len(argv) > 0:
            self.InputFile = argv[0]

            self.__exist_inp_file = False
            if len(argv) == 1:
                for root, dirs, files in os.walk(resource_filename("epyt", "")):
                    for name in files:
                        if name == self.InputFile:
                            self.InputFile = os.path.join(root, self.InputFile)
                            break
                    else:
                        continue
                    break
                self.__exist_inp_file = True
                self.api.ENopen(self.InputFile)
                # Save the temporary input file
                self.TempInpFile = self.InputFile[0:-4] + '_temp.inp'
                # Create a new INP file (Working Copy) using the SAVE command of EPANET
                self.saveInputFile(self.TempInpFile)
                # Close input file
                self.closeNetwork()
                # Load temporary file
                rptfile = self.InputFile[0:-4] + '_temp.txt'
                binfile = self.InputFile[0:-4] + '_temp.bin'
                self.RptTempfile = rptfile
                self.BinTempfile = binfile
                self.api.ENopen(self.TempInpFile, rptfile, binfile)
                # Parameters
                if not loadfile: self.__getInitParams()

            elif (len(argv) == 2) and (argv[1].upper() == 'CREATE'):
                self.InputFile = argv[0]
                # if the file exists it is overwritten
                f = open(self.InputFile, "w")
                f.close()
                self.createProject()
                # Save the temporary input file
                self.BinTempfile = f'{self.InputFile[0:-4]}_temp.inp'
                self.__exist_inp_file = True

            if not self.__exist_inp_file:
                msg = f'File "{self.InputFile}" does not exist.'
                warnings.warn(msg)
                sys.exit(-1)

            self.netName = os.path.basename(self.InputFile)
            self.LibEPANETpath = self.api.LibEPANETpath
            self.LibEPANET = self.api.LibEPANET

            # Hide messages at command window from bin computed
            self.CMDCODE = 1
            print(f'Input File {self.netName} loaded successfully.\n')
        else:
            self.createProject()

        # Global plot settings
        plt.rcParams["figure.figsize"] = [3, 2]
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['figure.constrained_layout.use'] = True
        plt.rcParams['figure.max_open_warning'] = 30

    # Constants
    # Demand model types. DDA #0 Demand driven analysis, PDA #1 Pressure driven analysis.
    DEMANDMODEL = ['DDA', 'PDA']
    # Link types
    TYPELINK = ['CVPIPE', 'PIPE', 'PUMP', 'PRV', 'PSV', 'PBV', 'FCV', 'TCV', 'GPV']
    # Constants for mixing models
    TYPEMIXMODEL = ['MIX1', 'MIX2', 'FIFO', 'LIFO']
    # Node types
    TYPENODE = ['JUNCTION', 'RESERVOIR', 'TANK']
    # Constants for pumps
    TYPEPUMP = ['CONSTANT_HORSEPOWER', 'POWER_FUNCTION', 'CUSTOM']
    # Link PUMP status
    TYPEPUMPSTATE = ['XHEAD', '', 'CLOSED', 'OPEN', '', 'XFLOW']
    # Constants for quality
    TYPEQUALITY = ['NONE', 'CHEM', 'AGE', 'TRACE', 'MULTIS']
    # Constants for sources
    TYPESOURCE = ['CONCEN', 'MASS', 'SETPOINT', 'FLOWPACED']
    # Constants for statistics
    TYPESTATS = ['NONE', 'AVERAGE', 'MINIMUM', 'MAXIMUM', 'RANGE']
    # Constants for control: 'LOWLEVEL', 'HILEVEL', 'TIMER', 'TIMEOFDAY'
    TYPECONTROL = ['LOWLEVEL', 'HIGHLEVEL', 'TIMER', 'TIMEOFDAY']
    # Constants for report: 'YES', 'NO', 'FULL'
    TYPEREPORT = ['YES', 'NO', 'FULL']
    # Link Status
    TYPESTATUS = ['CLOSED', 'OPEN']
    # Constants for pump curves: 'PUMP', 'EFFICIENCY', 'VOLUME', 'HEADLOSS'
    TYPECURVE = ['VOLUME', 'PUMP', 'EFFICIENCY', 'HEADLOSS', 'GENERAL']
    # Constants of headloss types: HW: Hazen-Williams, DW: Darcy-Weisbach, CM: Chezy-Manning
    TYPEHEADLOSS = ['HW', 'DW', 'CM']
    # Constants for units
    TYPEUNITS = ['CFS', 'GPM', 'MGD', 'IMGD', 'AFD', 'LPS', 'LPM', 'MLD', 'CMH', 'CMD']
    # 0 = closed (max. head exceeded), 1 = temporarily closed, 2 = closed, 3 = open, 4 = active (partially open)
    # 5 = open (max. flow exceeded), 6 = open (flow setting not met), 7 = open (pressure setting not met)
    TYPEBINSTATUS = ['CLOSED (MAX. HEAD EXCEEDED)', 'TEMPORARILY CLOSED', 'CLOSED', 'OPEN',
                     'ACTIVE(PARTIALY OPEN)', 'OPEN (MAX. FLOW EXCEEDED', 'OPEN (PRESSURE SETTING NOT MET)']
    # Constants for rule-based controls: 'OPEN', 'CLOSED', 'ACTIVE'
    RULESTATUS = ['OPEN', 'CLOSED', 'ACTIVE']
    # Constants for rule-based controls: 'IF', 'AND', 'OR'
    LOGOP = ['IF', 'AND', 'OR']
    # Constants for rule-based controls: 'NODE','LINK','SYSTEM'  EPANET Version 2.2
    RULEOBJECT = ['NODE', 'LINK', 'SYSTEM']
    # Constants for rule-based controls: 'DEMAND', 'HEAD', 'GRADE' etc.  EPANET Version 2.2
    RULEVARIABLE = ['DEMAND', 'HEAD', 'GRADE', 'LEVEL', 'PRESSURE', 'FLOW', 'STATUS', 'SETTING', 'POWER', 'TIME',
                    'CLOCKTIME', 'FILLTIME', 'DRAINTIME']
    # Constants for rule-based controls: '=', '~=', '<=' etc.  EPANET Version 2.2
    RULEOPERATOR = ['=', '~=', '<=', '>=', '<', '>', 'IS', 'NOT', 'BELOW', 'ABOVE']

    # Initial Properties
    ControlLevelValues = None  # The control level values
    ControlLinkIndex = None,  # Set of control links index
    ControlNodeIndex = None,  # Set of control nodes index
    ControlRules = None,  # Retrieves the parameters of all control statements
    ControlRulesCount = None,  # Number of controls
    Controls = None,  # Controls info
    ControlSettings = None,  # Settings for the controls
    ControlTypes = None,  # Set of control types
    ControlTypesIndex = None,  # Index of the control types
    CurveCount = None,  # Number of curves
    CurveIndex = None,  # Index of curves
    CurvesInfo = None,  # Curves info
    DemandModelCode = None,  # Demand model code DDA - 0, PDA - 1
    DemandModelPmin = None,  # Demand model Pmin - Pressure below which there is no demand
    DemandModelPreq = None,  # Demand model Preq - Pressure required to deliver full demand
    DemandModelPexp = None,  # Demand model Pexp - Pressure exponent in demand function
    DemandModelType = None,  # Demand model type DDA, PDA
    EnergyEfficiencyUnits = None,  # Units for efficiency
    EnergyUnits = None,  # Units for energy
    Errcode = None,  # Code for the EPANET error message
    InputFile = None,  # Name of the input file
    Iterations = None,  # Iterations to reach solution
    LibEPANET = None,  # EPANET library dll
    LibEPANETpath = None,  # EPANET library dll path
    libFunctions = None,  # EPANET functions in dll
    LinkBulkReactionCoeff = None,  # Bulk reaction coefficient of each link
    LinkCount = None,  # Number of links
    LinkDiameter = None,  # Diameter of each link
    LinkFlowUnits = None,  # Units of flow
    LinkFrictionFactorUnits = None,  # Units for friction factor
    LinkIndex = None,  # Index of links
    LinkInitialSetting = None,  # Initial settings of links
    LinkInitialStatus = None,  # Initial status of links
    LinkLength = None,  # Length of links
    LinkLengthsUnits = None,  # Units of length
    LinkMinorLossCoeff = None,  # Minor loss coefficient of links
    LinkMinorLossCoeffUnits = None,  # Minor loss coefficient units
    LinkNameID = None,  # Name ID of links
    LinkPipeCount = None,  # Number of pipes
    LinkPipeDiameterUnits = None,  # Units for pipe diameters
    LinkPipeIndex = None,  # Index of pipe links
    LinkPipeNameID = None,  # Name ID of pipe links
    LinkPipeRoughnessCoeffUnits = None,  # Pipe roughness coefficient units
    LinkPumpCount = None,  # Number of pumps
    LinkPumpHeadCurveIndex = None,  # Head curve indices
    LinkPumpIndex = None,  # Index of pumps
    LinkPumpNameID = None,  # Name ID of pumps
    LinkPumpPatternIndex = None,  # Index of pump pattern
    LinkPumpPatternNameID = None,  # ID of pump pattern
    LinkPumpPower = None,  # Power value
    LinkPumpPowerUnits = None,  # Units of power
    LinkPumpType = None,  # Pump type e.g constant horsepower, power function, user-defined custom curv
    LinkPumpTypeCode = None,  # Pump index/code
    LinkRoughnessCoeff = None,  # Roughness coefficient of links
    LinkType = None,  # ID of link type
    LinkTypeIndex = None,  # Index of link type
    LinkValveCount = None,  # Number of valves
    LinkValveIndex = None,  # Index of valves
    LinkValveNameID = None,  # ID name of valves
    LinkVelocityUnits = None,  # Units for velocity
    LinkWallReactionCoeff = None,  # Wall reaction coefficient of links
    NodeBaseDemands = None,  # Base demands of nodes
    NodeCoordinates = None,  # Coordinates for each node (long/lat & intermediate pipe coordinates)
    NodeCount = None,  # Number of nodes
    NodeDemandPatternIndex = None,  # Index of demand patterns
    NodeDemandPatternNameID = None,  # ID of demand patterns
    NodeDemandUnits = None,  # Units for demand
    NodeElevations = None,  # Elevation of nodes
    NodeElevationUnits = None,  # Units for elevation
    NodeEmitterCoeff = None,  # Emmitter Coefficient of nodes
    NodeEmitterCoefficientUnits = None,  # Units for emitter coefficient
    NodeHeadUnits = None,  # Nodal head units
    NodeIndex = None,  # Index of nodes
    NodeInitialQuality = None,  # Initial quality of nodes
    NodeJunctionCount = None,  # Number of junctions
    NodeJunctionIndex = None,  # Index of node junctions
    NodeJunctionNameID = None,  # Name ID of node junctions
    NodeNameID = None,  # Name ID of all nodes
    NodeDemandCategoriesNumber = None,  # Number of demand categories for nodes
    NodePatternIndex = None,  # Node demand pattern indices
    NodePressureUnits = None,  # Units for Pressure
    NodeReservoirCount = None,  # Number of reservoirs
    NodeReservoirIndex = None,  # Index of reservoirs
    NodeReservoirNameID = None,  # Name ID of reservoirs
    NodesConnectingLinksID = None,  # Name IDs of nodes which connect links
    NodesConnectingLinksIndex = None,  # Indices of nodes which connect links
    NodeSourcePatternIndex = None,  # Index of pattern for node sources
    NodeSourceQuality = None,  # Quality of node sources
    NodeSourceTypeIndex = None,  # Index of source type
    NodeTankBulkReactionCoeff = None,  # Bulk reaction coefficients in tanks
    NodeTankCount = None,  # Number of tanks
    NodeTankDiameter = None,  # Diameters of tanks
    NodeTankDiameterUnits = None,  # Units for tank diameters
    NodeTankIndex = None,  # Indices of Tanks
    NodeTankInitialLevel = None,  # Initial water level in tanks
    NodeTankInitialWaterVolume = None,  # Initial water volume in tanks
    NodeTankMaximumWaterLevel = None,  # Maximum water level in tanks
    NodeTankMaximumWaterVolume = None,  # Maximum water volume
    NodeTankMinimumFraction = None,  # Fraction of the total tank volume devoted to the inlet/outlet compartment
    NodeTankMinimumWaterLevel = None,  # Minimum water level
    NodeTankMinimumWaterVolume = None,  # Minimum water volume
    NodeTankMixingModelCode = None,  # Code of mixing model (MIXED:0, 2COMP:1, FIFO:2, LIFO:3)
    NodeTankMixingModelType = None,  # Type of mixing model (MIXED, 2COMP, FIFO, or LIFO)
    NodeTankMixZoneVolume = None,  # Mixing zone volume
    NodeTankNameID = None,  # Name ID of Tanks
    NodeTankReservoirCount = None,  # Number of tanks and reservoirs
    NodeTankVolumeCurveIndex = None,  # Index of curve for tank volumes
    NodeTankVolumeUnits = None,  # Units for volume
    NodeType = None,  # ID of node type
    NodeTypeIndex = None,  # Index of nodetype
    OptionsAccuracyValue = None,  # Convergence value (0.001 is default)
    OptionsEmitterExponent = None,  # Exponent of pressure at an emmiter node (0.5 is default)
    OptionsHeadLossFormula = None,  # Headloss formula (Hazen-Williams, Darcy-Weisbach or Chezy-Manning)
    OptionsHydraulics = None,  # Save or Use hydraulic soltion. *** Not implemented ***
    OptionsMaxTrials = None,  # Maximum number of trials (40 is default)
    OptionsPattern = None,  # *** Not implemented *** # but get with BinOptionsPattern
    OptionsPatternDemandMultiplier = None,  # Multiply demand values (1 is default)
    OptionsQualityTolerance = None,  # Tolerance for water  (0.01 is default)
    OptionsSpecificGravity = None,  # *** Not implemented *** # but get with BinOptionsSpecificGravity
    OptionsUnbalanced = None,  # *** Not implemented *** # but get with BinOptionsUnbalanced
    OptionsViscosity = None,  # *** Not implemented *** # but get with BinOptionsViscosity
    OptionsHeadError = None,
    OptionsFlowChange = None,
    Pattern = None,  # Get all patterns - matrix
    PatternAverageValue = None,  # Average value of patterns
    PatternCount = None,  # Number of patterns
    PatternDemandsUnits = None,  # Units for demands
    PatternIndex = None,  # Indices of the patterns
    PatternLengths = None,  # Length of the patterns
    PatternNameID = None,  # ID of the patterns
    QualityChemName = None,  # Quality Chem Name
    QualityChemUnits = None,  # Quality Chem Units
    QualityCode = None,  # Water quality analysis code (None:0/Chemical:1/Age:2/Trace:3)
    QualityReactionCoeffBulkUnits = None,  # Bulk reaction coefficient units
    QualityReactionCoeffWallUnits = None,  # Wall reaction coefficient units
    QualitySourceMassInjectionUnits = None,  # Units for source mass injection
    QualityTraceNodeIndex = None,  # Index of trace node (0 if QualityCode<3)
    QualityType = None,  # Water quality analysis type (None/Chemical/Age/Trace)
    QualityUnits = None,  # Units for quality concentration.
    QualityWaterAgeUnits = None,  # Units for water age
    RelativeError = None,  # Relative error - hydraulic simulation statistic
    #         RulePremises=None,
    #         RuleTrueActions=None,
    #         RuleFalseActions=None,
    #         RulePriority=None,
    TempInpFile = None,  # Name of the temporary input file
    TimeHaltFlag = None,  # Number of halt flag
    TimeHTime = None,  # Number of htime
    TimeHydraulicStep = None,  # Hydraulic time step
    TimeNextEvent = None,  # Find the lesser of the hydraulic time step length, or the time to next fill/empty
    TimePatternStart = None,  # Pattern start time
    TimePatternStep = None,  # Pattern Step
    TimeQualityStep = None,  # Quality Step
    TimeReportingPeriods = None,  # Reporting periods
    TimeReportingStart = None,  # Start time for reporting
    TimeReportingStep = None,  # Reporting time step
    TimeRuleControlStep = None,  # Time step for evaluating rule-based controls
    TimeSimulationDuration = None,  # Simulation duration
    TimeStartTime = None,  # Number of start time
    TimeStatisticsIndex = None,  # Index of time series post-processing type ('NONE':0, 'AVERAGE':1, 'MINIMUM':2, 'MAXIMUM':3, 'RANGE':4)
    TimeStatisticsType = None,  # Type of time series post-processing ('NONE', 'AVERAGE', 'MINIMUM', 'MAXIMUM', 'RANGE')
    ToolkitConstants = None,  # Contains all parameters from epanet2.h
    Units_SI_Metric = None,  # Equal with 1 if is SI-Metric
    Units_US_Customary = None,  # Equal with 1 if is US-Customary
    Version = None  # EPANET version

    def addControls(self, control, *argv):
        """ Adds a new simple control. (EPANET Version 2.2)

        :param control: New Control
        :type control: float or list
        :return: Control index
        :rtype: int

        The examples are based on d = epanet('Net1.inp')

        Example 1: Close Link 12 if the level in Tank 2 exceeds 20 ft.

        >>> index = d.addControls('LINK 12 CLOSED IF NODE 2 ABOVE 20')
        >>> d.getControls(index).disp()

        Example 2: Open Link 12 if the pressure at Node 11 is under 30 psi.

        >>> index = d.addControls('LINK 12 OPEN IF NODE 11 BELOW 30')
        >>> d.getControls(index).disp()

        Example 3: Pump 9 speed is set to 1.5 at 16 hours or 57600 seconds into the simulation.

        >>> index = d.addControls('LINK 9 1.5 AT TIME 16:00')
        >>> d.getControls(index).disp()
        >>> index = d.addControls('LINK 9 1.5 AT TIME 57600') #in seconds
        >>> d.getControls(index).disp()

        Example 4: Link 12 is closed at 10 am and opened at 8 pm throughout the simulation.

        >>> index_3 = d.addControls('LINK 12 CLOSED AT CLOCKTIME 10:00')
        >>> d.getControls(index_3).disp()
        >>> index_4 = d.addControls('LINK 12 OPEN AT CLOCKTIME 20:00')
        >>> d.getControls(index_4).disp()

        Example 5: Adds multiple controls given as cell.

        >>> d = epanet("Net1.inp")
        >>> control_1 = 'LINK 9 OPEN IF NODE 2 BELOW 110'
        >>> control_2 = 'LINK 9 CLOSED IF NODE 2 ABOVE 200'
        >>> controls = [control_1, control_2]
        >>> index = d.addControls(controls)
        >>> d.getControls(index)[0].Control
        >>> d.getControls(index)[1].Control

        Example 6:

        Notes:
            * index:	  return index of the new control.
            * Type:  	  the type of control to add (see EN_ControlType).
            * linkIndex:  the index of a link to control (starting from 1).
            * setting:	  control setting applied to the link.
            * nodeIndex:  index of the node used to control the link (0 for EN_TIMER and EN_TIMEOFDAY controls).
            * level:	  action level (tank level, junction pressure, or time in seconds) that triggers the control.

        Control type codes consist of the following:
            * EN_LOWLEVEL      0   Control applied when tank level or node pressure drops below specified level
            * EN_HILEVEL       1   Control applied when tank level or node pressure rises above specified level
            * EN_TIMER         2   Control applied at specific time into simulation
            * EN_TIMEOFDAY     3   Control applied at specific time of day

        Code example:
        index = d.addControls(type, linkIndex, setting, nodeIndex, level)

        >>> index = d.addControls(0, 13, 0, 11, 100)
        >>> d.getControls(index).to_dict() # retrieve controls of index in dict format

        See also deleteControls, getControls, setControls, getControlRulesCount.
        """
        if type(control) is dict:
            index = []
            for key in control:
                index.append(self.__addControlFunction(control[key]))
        else:
            if len(argv) == 0:
                index = self.__addControlFunction(control)
            else:
                linkIndex = argv[0]
                controlSettingValue = argv[1]
                nodeIndex = argv[2]
                controlLevel = argv[3]
                index = self.api.ENaddcontrol(control, linkIndex, controlSettingValue, nodeIndex, controlLevel)
        return index

    def addCurve(self, *argv):
        """ Adds a new curve appended to the end of the existing curves. (EPANET Version 2.1)
        Returns the new curve's index.

        :param *argv: value index or value
        :type *argv: int or float
        :raises: No curve ID or curve values exist
        :return: new curve valueIndex
        :rtype: int

        Example:

        >>> new_curve_ID = 'NewCurve'                          # ID selected without a space in between the letters
        >>> x_y_1 = [0, 730]
        >>> x_y_2 = [1000, 500]
        >>> x_y_3 = [1350, 260]
        >>> values = [x_y_1, x_y_2, x_y_3]                     # X and Y values selected
        >>> curve_index = d.addCurve(new_curve_ID, values)     # New curve added
        >>> d.getCurvesInfo().disp()                           # Retrieves all the info of curves

        See also getCurvesInfo, getCurveType, setCurve,setCurveValue, setCurveNameID, setCurveComment.
        """
        valueIndex = 0
        if len(argv) > 0:
            self.api.ENaddcurve(argv[0])
            valueIndex = self.getCurveIndex(argv[0])
            if len(argv) == 2:
                self.setCurve(valueIndex, argv[1])
        else:
            raise Exception('No curve ID or curve values exist.')
        return valueIndex

    def addLinkPipe(self, pipeID, fromNode, toNode, *argv):
        """ Adds a new pipe.
        Returns the index of the new pipe.

        Properties that can be set(optional):
            1. Length
            2. Diameter
            3. Roughness Coefficient
            4. Minor Loss Coefficient

        If no properties are given, the default values are:
            * length = 330 feet (~100.5 m)
            * diameter = 10 inches (25.4 cm)
            * roughness coefficient = 130 (Hazen-Williams formula) or
                0.15 mm (Darcy-Weisbach formula) or
                0.01 (Chezy-Manning formula)
            * minor Loss Coefficient = 0

        The examples are based on d = epanet("Net1.inp")

        Example 1: Adds a new pipe given no properties.

        >>> pipeID = 'newPipe_1'
        >>> fromNode = '10'
        >>> toNode = '21'
        >>> d.getLinkPipeCount()                   # Retrieves the number of links
        >>> pipeIndex = d.addLinkPipe(pipeID, fromNode, toNode)
        >>> d.getLinkPipeCount()
        >>> d.plot()

        Example 2: Adds a new pipe given it's length.

        >>> pipeID = 'newPipe_2'
        >>> fromNode = '11'
        >>> toNode = '22'
        >>> length = 600
        >>> d.getLinkPipeCount()
        >>> pipeIndex = d.addLinkPipe(pipeID, fromNode, toNode, length)
        >>> d.getLinkPipeCount()
        >>> d.getLinkLength(pipeIndex)           # Retrieves the new link's length
        >>> d.plot()

        Example 3: Adds a new pipe given it's length, diameter, roughness coefficient and minor loss coefficient.

        >>> pipeID = 'newPipe_3'
        >>> fromNode = '31'
        >>> toNode = '22'
        >>> length = 500
        >>> diameter = 15
        >>> roughness = 120
        >>> minorLossCoeff = 0.2
        >>> d.getLinkPipeCount()
        >>> pipeIndex = d.addLinkPipe(pipeID, fromNode, toNode, length, diameter, roughness, minorLossCoeff)
        >>> d.getLinkPipeCount()
        >>> d.getLinkLength(pipeIndex)
        >>> d.getLinkDiameter(pipeIndex)          # Retrieves the new link's diameter
        >>> d.getLinkRoughnessCoeff(pipeIndex)    # Retrieves the new link's roughness coefficient
        >>> d.getLinkMinorLossCoeff(pipeIndex)    # Retrieves the new link's minor loss coefficient
        >>> d.plot()

        See also plot, setLinkNodesIndex, addLinkPipeCV, addNodeJunction, deleteLink, setLinkDiameter.
        """
        index = self.api.ENaddlink(pipeID, self.ToolkitConstants.EN_PIPE, fromNode, toNode)
        if len(argv) > 0:
            self.setLinkLength(index, argv[0])
        if len(argv) > 1:
            self.setLinkDiameter(index, argv[1])
        if len(argv) > 2:
            self.setLinkRoughnessCoeff(index, argv[2])
        if len(argv) > 3:
            self.setLinkMinorLossCoeff(index, argv[3])
        return index

    def addLinkPipeCV(self, cvpipeID, fromNode, toNode, *argv):
        """ Adds a new control valve pipe.
        Returns the index of the new control valve pipe.

        Properties that can be set(optional):
            1. Length
            2. Diameter
            3. Roughness Coefficient
            4. Minor Loss Coefficient

        If no properties are given, the default values are:
            * length = 330 feet (~100.5 m)
            * diameter = 10 inches (25.4 cm)
            * roughness coefficient = 130 (Hazen-Williams formula) or
                0.15 mm (Darcy-Weisbach formula) or
                0.01 (Chezy-Manning formula)
            * minor Loss Coefficient = 0

        The examples are based on d = epanet('Net1.inp')

        Example 1: Adds a new control valve pipe given no properties.

        >>> cvPipeID = 'newCVPipe_1'
        >>> fromNode = '10'
        >>> toNode = '21'
        >>> d.getLinkPipeCount()                       # Retrieves the number of pipes
        >>> cvPipeIndex = d.addLinkPipeCV(cvPipeID, fromNode, toNode)
        >>> d.getLinkPipeCount()
        >>> d.plot()                                   # Plots the network in a new figure

        Example 2: Adds a new control valve pipe given it's length.

        >>> cvPipeID = 'newCVPipe_2'
        >>> fromNode = '11'
        >>> toNode = '22'
        >>> length = 600
        >>> d.getLinkPipeCount()
        >>> cvPipeIndex = d.addLinkPipeCV(cvPipeID, fromNode, toNode, length)
        >>> d.getLinkPipeCount()
        >>> d.getLinkLength(cvPipeIndex)            # Retrieves the new link's length
        >>> d.plot()

        Example 3: Adds a new control valve pipe given it's length, diameter, roughness coefficient and minor loss coefficient.

        >>> cvPipeID = 'newCVPipe_3'
        >>> fromNode = '31'
        >>> toNode = '22'
        >>> length = 500
        >>> diameter = 15
        >>> roughness = 120
        >>> minorLossCoeff = 0.2
        >>> d.getLinkPipeCount()
        >>> cvPipeIndex = d.addLinkPipeCV(cvPipeID, fromNode, toNode, length, diameter, roughness, minorLossCoeff)
        >>> d.getLinkPipeCount()
        >>> d.getLinkLength(cvPipeIndex)
        >>> d.getLinkDiameter(cvPipeIndex)          # Retrieves the new link's diameter
        >>> d.getLinkRoughnessCoeff(cvPipeIndex)    # Retrieves the new link's roughness coefficient
        >>> d.getLinkMinorLossCoeff(cvPipeIndex)    # Retrieves the new link's minor loss coefficient
        >>> d.plot()

        See also plot, setLinkNodesIndex, addLinkPipe, addNodeJunction, deleteLink, setLinkDiameter.
        """
        index = self.api.ENaddlink(cvpipeID, self.ToolkitConstants.EN_CVPIPE, fromNode, toNode)
        if len(argv) > 0:
            self.setLinkLength(index, argv[0])
        if len(argv) > 1:
            self.setLinkDiameter(index, argv[1])
        if len(argv) > 2:
            self.setLinkRoughnessCoeff(index, argv[2])
        if len(argv) > 3:
            self.setLinkMinorLossCoeff(index, argv[3])
        return index

    def addLinkPump(self, pumpID, fromNode, toNode, *argv):
        """ Adds a new pump.
        Returns the index of the new pump.

        Parameters
        ----------
        pumpID : string
            Pump ID.
        fromNode : numeric
            Starting node.
        toNode : numeric
            End node.

        Returns
        -------
        index : numeric
            new Pumps index

        Properties that can be set(optional):
            1) Initial Status
            2) Initial Speed setting
            3) Power
            4) Pattern index

        If no properties are given, the default values are:
            * initial status = 1 (OPEN)
            * initial speed setting = 1
            * power = 0
            * pattern index = 0

        Examples
        --------
        The examples are based on d = epanet('Net1.inp')

        Example 1: Adds a new pump given no properties.

        >>> pumpID = 'newPump_1'
        >>> fromNode = '10'
        >>> toNode = '21'
        >>> d.getLinkPumpCount()                     # Retrieves the number of pumps
        >>> pumpIndex = d.addLinkPump(pumpID, fromNode, toNode)
        >>> d.getLinkPumpCount()
        >>> d.plot()                                 # Plots the network in a new MATLAB figure

        Example 2: Adds a new pump given it's initial status.::

        >>> pumpID = 'newPump_2'
        >>> fromNode = '31'
        >>> toNode = '22'
        >>> initialStatus = 0    # (CLOSED)
        >>> d.getLinkPumpCount()
        >>> pumpIndex = d.addLinkPump(pumpID, fromNode, toNode, initialStatus)
        >>> d.getLinkPumpCount()
        >>> d.getLinkInitialStatus(pumpIndex)       # Retrieves the new pump's initial status
        >>> d.plot()

        Example 3: Adds a new pump given it's initial status, initial speed setting, power and pattern index.

        >>> pumpID = 'newPump_3'
        >>> fromNode = '11'
        >>> toNode = '22'
        >>> initialStatus = 1    # (OPEN)
        >>> initialSetting = 1.2
        >>> power = 10
        >>> patternIndex = 1
        >>> d.getLinkPumpCount()
        >>> pumpIndex = d.addLinkPump(pumpID, fromNode, toNode, initialStatus, initialSetting, power, patternIndex)
        >>> d.getLinkPumpCount()
        >>> d.getLinkInitialStatus(pumpIndex)
        >>> d.getLinkInitialSetting(pumpIndex)      # Retrieves the new pump's initial setting
        >>> d.getLinkPumpPower(pumpIndex)           # Retrieves the new pump's power
        >>> d.getLinkPumpPatternIndex(pumpIndex)    # Retrieves the new pump's pattern index
        >>> d.plot()

        See also: plot, setLinkNodesIndex, addLinkPipe, addNodeJunction, deleteLink, setLinkInitialStatus.
        """
        index = self.api.ENaddlink(pumpID, self.ToolkitConstants.EN_PUMP, fromNode, toNode)
        if len(argv) > 0:
            self.setLinkInitialStatus(index, argv[0])
        if len(argv) > 1:
            self.setLinkInitialSetting(index, argv[1])
        if len(argv) > 2:
            self.setLinkPumpPower(index, argv[2])
        if len(argv) > 3:
            self.setLinkPumpPatternIndex(index, argv[3])
        return index

    def addLinkValveFCV(self, vID, fromNode, toNode):
        """ Adds a new FCV valve.
        Returns the index of the new FCV valve.

         The example is based on d = epanet('Net1.inp')

        Example:
        >>> valveID = 'newValveFCV'
        >>> fromNode = '10'
        >>> toNode = '21'
        >>> valveIndex = d.addLinkValveFCV(valveID, fromNode, toNode)
        >>> d.plot()

        See also plot, setLinkNodesIndex, addLinkPipe,
              addLinkValvePRV, deleteLink, setLinkTypeValveTCV.
        """
        return self.api.ENaddlink(vID, self.ToolkitConstants.EN_FCV, fromNode, toNode)

    def addLinkValveGPV(self, vID, fromNode, toNode):
        """ Adds a new GPV valve.
        Returns the index of the new GPV valve.

         The example is based on d = epanet('Net1.inp')

        Example:
        >>> valveID = 'newValveGPV'
        >>> fromNode = '10'
        >>> toNode = '21'
        >>> valveIndex = d.addLinkValveGPV(valveID, fromNode, toNode)
        >>> d.plot()

        See also plot, setLinkNodesIndex, addLinkPipe,
                 addLinkValvePRV, deleteLink, setLinkTypeValveFCV.
        """
        return self.api.ENaddlink(vID, self.ToolkitConstants.EN_GPV, fromNode, toNode)

    def addLinkValvePBV(self, vID, fromNode, toNode):
        """ Adds a new PBV valve.
        Returns the index of the new PBV valve.

         The example is based on d = epanet('Net1.inp')

        Example:
        >>> valveID = 'newValvePBV'
        >>> fromNode = '10'
        >>> toNode = '21'
        >>> valveIndex = d.addLinkValvePBV(valveID, fromNode, toNode)
        >>> d.plot()

         See also plot, setLinkNodesIndex, addLinkPipe,
                  addLinkValvePRV, deleteLink, setLinkTypeValvePRV.
         """
        return self.api.ENaddlink(vID, self.ToolkitConstants.EN_PBV, fromNode, toNode)

    def addLinkValvePRV(self, vID, fromNode, toNode):
        """ Adds a new PRV valve.
        Returns the index of the new PRV valve.

        # The example is based on d = epanet('Net1.inp')

        Example:
        >>> valveID = 'newValvePRV'
        >>> fromNode = '10'
        >>> toNode = '21'
        >>> valveIndex = d.addLinkValvePRV(valveID, fromNode, toNode)
        >>> d.plot()

        See also plot, setLinkNodesIndex, addLinkPipe,
                 addLinkValvePSV, deleteLink, setLinkTypeValveFCV.
        """
        return self.api.ENaddlink(vID, self.ToolkitConstants.EN_PRV, fromNode, toNode)

    def addLinkValvePSV(self, vID, fromNode, toNode):
        """Adds a new PSV valve.
        Returns the index of the new PSV valve.

        The example is based on d = epanet('Net1.inp')

        Example:
        >>> valveID = 'newValvePSV'
        >>> fromNode = '10'
        >>> toNode = '21'
        >>> valveIndex = d.addLinkValvePSV(valveID, fromNode, toNode)
        >>> d.plot()

        See also plot, setLinkNodesIndex, addLinkPipe,
                 addLinkValvePRV, deleteLink, setLinkTypeValveGPV.
        """
        return self.api.ENaddlink(vID, self.ToolkitConstants.EN_PSV, fromNode, toNode)

    def addLinkValveTCV(self, vID, fromNode, toNode):
        """ Adds a new TCV valve.
        Returns the index of the new TCV valve.

        The example is based on d = epanet('Net1.inp')

        Example:
        >>> valveID = 'newValveTCV'
        >>> fromNode = '10'
        >>> toNode = '21'
        >>> valveIndex = d.addLinkValveTCV(valveID, fromNode, toNode)
        >>> d.plot()

        See also plot, setLinkNodesIndex, addLinkPipe,
                  addLinkValvePRV, deleteLink, setLinkTypeValveFCV.
        """
        return self.api.ENaddlink(vID, self.ToolkitConstants.EN_TCV, fromNode, toNode)

    def addNodeJunction(self, juncID, *argv):
        """ Adds new junction

        Returns the index of the new junction.

        The following data can be set(optional):
          1. Coordinates
          2. Elevation
          3. Primary base demand
          4. ID name of the demand's time pattern

        Example 1: Adds a new junction with the default coordinates (i.e. [0, 0]).

        >>> junctionID = 'newJunction_1'
        >>> junctionIndex = d.addNodeJunction(junctionID)
        >>> d.plot()

        Example 2: Adds a new junction with coordinates [X, Y] = [20, 10].

        >>> junctionID = 'newJunction_2'
        >>> junctionCoords = [20, 10]
        >>> junctionIndex = d.addNodeJunction(junctionID, junctionCoords)
        >>> d.plot(highlightnode=junctionIndex)

        Example 3: Adds a new junction with coordinates [X, Y] = [20, 20] and elevation = 500.

        >>> junctionID = 'newJunction_3'
        >>> junctionCoords = [20, 20]
        >>> junctionElevation = 500
        >>> junctionIndex = d.addNodeJunction(junctionID, junctionCoords, junctionElevation)
        >>> d.getNodeElevations(junctionIndex)
        >>> d.plot()

        Example 4: Adds a new junction with coordinates [X, Y] = [10, 40],
        elevation = 500 and demand = 50.

        >>> junctionID = 'newJunction_4'
        >>> junctionCoords = [10, 40]
        >>> junctionElevation = 500
        >>> demand = 50
        >>> junctionIndex = d.addNodeJunction(junctionID, junctionCoords, junctionElevation, demand)
        >>> d.getNodeBaseDemands(junctionIndex)
        >>> d.plot()

        Example 5: Adds a new junction with coordinates [X, Y] = [10, 20], elevation = 500,
        demand = 50 and pattern ID = the 1st time pattern ID(if exists).

        >>> junctionID = 'newJunction_5'
        >>> junctionCoords = [10, 20]
        >>> junctionElevation = 500
        >>> demand = 50
        >>> demandPatternID = d.getPatternNameID(1)
        >>> junctionIndex = d.addNodeJunction(junctionID, junctionCoords, junctionElevation, demand, demandPatternID)
        >>> d.getNodeDemandPatternNameID()[1][junctionIndex-1]
        >>> d.plot()

        See also plot, setLinkNodesIndex, addNodeReservoir, setNodeComment, deleteNode, setNodeBaseDemands.
        """
        xy = [0, 0]
        elev = 0
        dmnd = 0
        dmndpat = ''
        if len(argv) > 0:
            xy = argv[0]
        if len(argv) > 1:
            elev = argv[1]
        if len(argv) > 2:
            dmnd = argv[2]
        if len(argv) > 3:
            dmndpat = argv[3]
        index = self.api.ENaddnode(juncID, self.ToolkitConstants.EN_JUNCTION)
        self.setNodeCoordinates(index, [xy[0], xy[1]])
        self.setNodeJunctionData(index, elev, dmnd, dmndpat)
        return index

    def addNodeJunctionDemand(self, *argv):
        """ Adds a new demand to a junction given the junction index, base demand, demand time pattern and demand category name. (EPANET Version 2.2)
        Returns the values of the new demand category index.
        A blank string can be used for demand time pattern and demand name category to indicate
        that no time pattern or category name is associated with the demand.

        Example 1: New demand added with the name 'new demand' to the 1st node, with 100 base demand, using the 1st time pattern.

        >>> d.addNodeJunctionDemand(1, 100, '1', 'new demand')
        >>> d.getNodeJunctionDemandIndex()       # Retrieves the indices of all demands for all nodes.
        >>> d.getNodeJunctionDemandName()[2]     # Retrieves the demand category names of the 2nd demand index for all nodes.

        Example 2: New demands added with the name 'new demand' to the 1st and 2nd node, with 100 base demand, using the 1st time pattern.

        >>> d.addNodeJunctionDemand([1, 2], 100, '1', 'new demand')
        >>> d.getNodeJunctionDemandIndex()       # Retrieves the indices of all demands for all nodes.
        >>> d.getNodeJunctionDemandName()[2]     # Retrieves the demand category names of the 2nd demand index for all nodes.

        Example 3: New demands added with the name 'new demand' to the 1st and 2nd node, with 100 and 110 base demand respectively, using the 1st time pattern.

        >>> d.addNodeJunctionDemand([1, 2], [100, 110], '1', 'new demand')
        >>> d.getNodeJunctionDemandIndex()       # Retrieves the indices of all demands for all nodes.
        >>> d.getNodeJunctionDemandName()[2]     # Retrieves the demand category names of the 2nd demand index for all nodes.

        Example 4: New demands added with the name 'new demand' to the 1st and 2nd node, with 100 and 110 base demand respectively, using the 1st time pattern.

        >>> d.addNodeJunctionDemand([1, 2], [100, 110], ['1', '1'], 'new demand')
        >>> d.getNodeJunctionDemandIndex()       # Retrieves the indices of all demands for all nodes.
        >>> d.getNodeJunctionDemandName()[2]     # Retrieves the demand category names of the 2nd demand index for all nodes.

        Example 5: New demands added with the names 'new demand1' and 'new demand2' to the 1st and 2nd node, with 100 and 110 base demand
        respectively, using the 1st and 2nd(if exists) time pattern respectively.

        >>> d.addNodeJunctionDemand([1, 2], [100, 110], ['1', '2'], ['new demand1', 'new demand2'])
        >>> d.getNodeJunctionDemandIndex()       # Retrieves the indices of all demands for all nodes.
        >>> d.getNodeJunctionDemandName()[2]     # Retrieves the demand category names of the 2nd demand index for all nodes.

        See also deleteNodeJunctionDemand, getNodeJunctionDemandIndex, getNodeJunctionDemandName,
                 setNodeJunctionDemandName, getNodeBaseDemands.
        """
        nodeIndex = argv[0]
        baseDemand = argv[1]
        if len(argv) == 2:
            demandPattern = ''
            demandName = ''
        elif len(argv) == 3:
            demandPattern = argv[2]
            demandName = ''
        elif len(argv) == 4:
            demandPattern = argv[2]
            demandName = argv[3]
        if not isList(nodeIndex):
            self.api.ENadddemand(nodeIndex, baseDemand, demandPattern, demandName)
        elif isList(nodeIndex) and not isList(baseDemand) and not isList(demandPattern) and not isList(demandName):
            for i in nodeIndex:
                self.api.ENadddemand(i, baseDemand, demandPattern, demandName)
        elif isList(nodeIndex) and isList(baseDemand) and not isList(demandPattern) and not isList(demandName):
            for i in range(len(nodeIndex)):
                self.api.ENadddemand(nodeIndex[i], baseDemand[i], demandPattern, demandName)
        elif isList(nodeIndex) and isList(baseDemand) and isList(demandPattern) and not isList(demandName):
            for i in range(len(nodeIndex)):
                self.api.ENadddemand(nodeIndex[i], baseDemand[i], demandPattern[i], demandName)
        elif isList(nodeIndex) and isList(baseDemand) and isList(demandPattern) and isList(demandName):
            for i in range(len(nodeIndex)):
                self.api.ENadddemand(nodeIndex[i], baseDemand[i], demandPattern[i], demandName[i])

        if isList(nodeIndex) and not isList(demandName):
            demandName = [demandName for i in nodeIndex]
        return self.getNodeJunctionDemandIndex(nodeIndex, demandName)

    def addNodeReservoir(self, resID, *argv):
        """
        Adds a new reservoir.
        Returns the index of the new reservoir.

        Example 1: Adds a new reservoir with the default coordinates (i.e. [0, 0])

        >>> reservoirID = 'newReservoir_1'
        >>> reservoirIndex = d.addNodeReservoir(reservoirID)
        >>> d.plot()

        Example 2: Adds a new reservoir with coordinates [X, Y] = [20, 30].

        >>> reservoirID = 'newReservoir_2'
        >>> reservoirCoords = [20, 30]
        >>> reservoirIndex = d.addNodeReservoir(reservoirID, reservoirCoords)
        >>> d.plot()

        See also plot, setLinkNodesIndex, addNodeJunction, self.addLinkPipe, deleteNode, setNodeBaseDemands.
        """
        xy = [0, 0]
        elev = 0
        if len(argv) > 0:
            xy = argv[0]
        if len(argv) > 1:
            elev = argv[1]
        index = self.api.ENaddnode(resID, self.ToolkitConstants.EN_RESERVOIR)
        self.setNodeCoordinates(index, [xy[0], xy[1]])
        self.setNodeElevations(index, elev)
        return index

    def addNodeTank(self, tankID, *argv):
        """ Adds a new tank.
        Returns the index of the new tank.

        Example 1: Adds a new tank with the default coordinates (i.e. [0, 0])

        >>> tankID = 'newTank_1'
        >>> tankIndex = d.addNodeTank(tankID)
        >>> d.plot()

        Example 2: Adds a new tank with coordinates [X, Y] = [10, 10].
        >>> tankID = 'newTank_2'
        >>> tankCoords = [10, 10]
        >>> tankIndex = d.addNodeTank(tankID, tankCoords)
        >>> d.plot()

        Example 3: Adds a new tank with coordinates [X, Y] = [20, 20] and elevation = 100.

        >>> tankID = 'newTank_3'
        >>> tankCoords = [20, 20]
        >>> elevation = 100
        >>> tankIndex = d.addNodeTank(tankID, tankCoords, elevation)
        >>> d.plot()

        Example 4: Adds a new tank with coordinates [X, Y] = [20, 30], elevation = 100, initial level = 130, minimum water level = 110,
        maximum water level = 160, diameter = 60, minimum water volume = 200000, volume curve ID = ''.

        >>> tankID = 'newTank_4'
        >>> tankCoords = [20, 30]
        >>> elevation = 100
        >>> initialLevel = 130
        >>> minimumWaterLevel = 110
        >>> maximumWaterLevel = 160
        >>> diameter = 60
        >>> minimumWaterVolume = 200000
        >>> volumeCurveID = ''   # Empty for no curve
        >>> tankIndex = d.addNodeTank(tankID, tankCoords, elevation, initialLevel, minimumWaterLevel,
        >>> maximumWaterLevel, diameter, minimumWaterVolume, volumeCurveID)
        >>> t_data = d.getNodeTankData(tankIndex)
        >>> d.plot()

        See also plot, setLinkNodesIndex, addNodeJunction, addLinkPipe, deleteNode, setNodeBaseDemands.
        """
        xy = [0, 0]
        elev = 0
        intlvl = 0
        minlvl = 0
        maxlvl = 0
        diam = 0
        minvol = 0
        volcurve = ''
        if len(argv) > 0:
            xy = argv[0]
        if len(argv) > 1:
            elev = argv[1]
        if len(argv) > 2:
            intlvl = argv[2]
        if len(argv) > 3:
            minlvl = argv[3]
        if len(argv) > 4:
            maxlvl = argv[4]
        if len(argv) > 5:
            diam = argv[5]
        if len(argv) > 6:
            minvol = argv[6]
        if len(argv) > 7:
            volcurve = argv[7]
        index = self.api.ENaddnode(tankID, self.ToolkitConstants.EN_TANK)
        self.setNodeCoordinates(index, [xy[0], xy[1]])
        if diam == 0 and self.getNodeType(index) == 'TANK':
            minvol = (np.pi * np.power((diam / 2), 2)) * minlvl
            if minvol == 0:
                return index
        self.setNodeTankData(index, elev, intlvl, minlvl, maxlvl, diam, minvol, volcurve)
        return index

    def addPattern(self, *argv):
        """ Adds a new time pattern to the network.

        Example 1:

        >>> d.getPatternNameID()                                   # Retrieves the ID labels of time patterns
        >>> patternID = 'new_pattern'
        >>> patternIndex = d.addPattern(patternID)                 # Adds a new time pattern given it's ID
        >>> d.getPatternNameID()

        Example 2:

        >>> patternID = 'new_pattern'
        >>> patternMult = [1.56, 1.36, 1.17, 1.13, 1.08,
        ... 1.04, 1.2, 0.64, 1.08, 0.53, 0.29, 0.9, 1.11,
        ... 1.06, 1.00, 1.65, 0.55, 0.74, 0.64, 0.46,
        ... 0.58, 0.64, 0.71, 0.66]
        >>> patternIndex = d.addPattern(patternID, patternMult)    # Adds a new time pattern given it's ID and the multiplier
        >>> d.getPatternNameID()
        >>> d.getPattern()

        See also getPattern, setPattern, setPatternNameID, setPatternValue, setPatternComment.
        """
        self.api.ENaddpattern(argv[0])
        index = self.getPatternIndex(argv[0])
        if len(argv) == 1:
            self.setPattern(index, [1] * max(self.getPatternLengths()))
        else:
            self.setPattern(index, argv[1])
        return index

    def addRules(self, rule):
        """ Adds a new rule-based control to a project. (EPANET Version 2.2)

        .. note:: Rule format: Following the format used in an EPANET input file.
                     'RULE ruleid \n IF object objectid attribute relation attributevalue \n THEN object objectid STATUS/SETTING IS value \n PRIORITY value'

        See more: 'https://nepis.epa.gov/Adobe/PDF/P1007WWU.pdf' (Page 164)

        The example is based on d = epanet('Net1.inp')

        Example:
        >>> d.getRuleCount()
        >>> d.addRules('RULE RULE-1 \n IF TANK 2 LEVEL >= 140 \n THEN PUMP 9 STATUS IS CLOSED \n PRIORITY 1')
        >>> d.getRuleCount()
        >>> d.getRules()[1]['Rule']

        See also deleteRules, setRules, getRules, getRuleInfo,
        setRuleThenAction, setRuleElseAction, setRulePriority.
        """
        self.api.ENaddrule(rule)

    def appRotateNetwork(self, theta, indexRot=0):
        """ Rotates the network by theta degrees counter-clockwise,
        using as pivot the indexRot
        theta: angle in degrees to rotate the network counter-clockwise
        indexRot: index of the node/point to be rotated. If  it's not
        provided then the first index node is used as pivot.

        Example 1: Rotate the network by 60 degrees counter-clockwise around the index 1 node.
        >>> d = epanet('Net1.inp')
        >>> d.plot()
        >>> d.appRotateNetwork(60)
        >>> d.plot()

        Example 2: Rotate the network by 150 degrees counter-clockwise around the reservoir with index 921.
        >>> d = epanet('ky10.inp')
        >>> d.plot()
        >>> d.appRotateNetwork(150,921)
        >>> d.plot()
        """
        # Access the x and y coordinates
        xCoord = self.getNodeCoordinates('x')
        yCoord = self.getNodeCoordinates('y')
        # Pick center of rotation point
        # If IndexRot is not provided, pick the first x,y coordinate
        if not indexRot:
            x_center = xCoord[1]
            y_center = yCoord[1]
        else:
            x_center = xCoord[indexRot]
            y_center = yCoord[indexRot]
        # Create a matrix which will be used later in calculations.
        # center = repmat([x_center  y_center], 1, length(xCoord))
        # Define the rotation matrix.
        R = np.array([[np.cos(theta * 2 * np.pi / 360), -np.sin(theta * 2 * np.pi / 360)],
                    [np.sin(theta * 2 * np.pi / 360), np.cos(theta * 2 * np.pi / 360)]], dtype=float)
        # Do the rotation:
        xCoord_new = [xCoord[i] - x_center for i in xCoord]
        yCoord_new = [yCoord[i] - y_center for i in yCoord]
        # v = [xCoord, yCoord]
        # s = v - center   # Shift points in the plane so that the center of rotation is at the origin.
        s = np.array([xCoord_new, yCoord_new], dtype=float)
        so = R * s  # Apply the rotation about the origin.
        newxCoord = so[0, :] + x_center  # Shift again so the origin goes back to the desired center of rotation.
        newyCoord = so[1, :] + y_center
        # Set the new coordinates
        for i in range(1, self.getNodeCount() + 1):
            self.setNodeCoordinates(i, [newxCoord[0, i - 1], newyCoord[0, i - 1]])
        if sum(self.getLinkVerticesCount()) != 0:
            xVertCoord = self.getNodeCoordinates()['x_vert']
            yVertCoord = self.getNodeCoordinates()['y_vert']
            for i in range(1, self.getLinkCount() + 1):
                if self.getLinkVerticesCount(i) != 0:
                    vertX_temp = xVertCoord[i]
                    vertY_temp = yVertCoord[i]
                    # Shift points in the plane so that the center of rotation is at the origin.
                    vertX_temp = [j - x_center for j in vertX_temp]
                    vertY_temp = [j - y_center for j in vertY_temp]
                    # Apply the rotation about the origin.
                    s = np.array([vertX_temp, vertY_temp], dtype=float)
                    so = R * s
                    # Shift again so the origin goes back to the desired center of rotation.
                    newxVertCoord = so[0,
                                    :] + x_center  # Shift again so the origin goes back to the desired center of rotation.
                    newvyVertCoord = so[1, :] + y_center
                    LinkID = self.getLinkNameID(i)
                    self.setLinkVertices(LinkID, newxVertCoord.tolist()[0], newvyVertCoord.tolist()[0])

    def appShiftNetwork(self, xDisp, yDisp):
        """ Shifts the network by xDisp in the x-direction and
        by yDisp in the y-direction

        Example 1: Shift the network by 1000 feet in the x-axis and -1000 feet in the y-axis

        >>> d = epanet('Net1.inp')
        >>> d.getNodeCoordinates(1) # old x coordinates
        >>> d.getNodeCoordinates(2) # old y coordinates
        >>> d.appShiftNetwork(1000,-1000)
        >>> d.getNodeCoordinates(1) # new x coordinates
        >>> d.getNodeCoordinates(2) # new y coordinates

        Example 2: Shift the network,along with the vertices by 1000 feet in
        the x-axis and -1000 feet in the y-axis

        >>> d = epanet('ky10.inp')
        >>> d.appShiftNetwork(1000,-1000)
        >>> d.plot()
        """
        # Access the x and y coordinates
        xCoord = self.getNodeCoordinates('x')
        yCoord = self.getNodeCoordinates('y')
        # Update coordinates
        newxCoord = [(xCoord[i] + xDisp) for i in xCoord]
        newyCoord = [(yCoord[i] + yDisp) for i in yCoord]
        # Set the new coordinates
        for i in range(1, self.getNodeCount() + 1):
            self.setNodeCoordinates(i, [newxCoord[i - 1], newyCoord[i - 1]])
        if sum(self.getLinkVerticesCount()) != 0:
            xVertCoord = self.getNodeCoordinates()['x_vert']
            yVertCoord = self.getNodeCoordinates()['y_vert']
            for i in range(self.getLinkCount()):
                if self.getLinkVerticesCount(i + 1) != 0:
                    newX = [(i + xDisp) for i in xVertCoord[i + 1]]
                    newY = [(i + yDisp) for i in yVertCoord[i + 1]]
                    LinkID = self.getLinkNameID(i + 1)
                    self.setLinkVertices(LinkID, newX, newY)

    def arange(self, begin, end, step=1):
        """ Create float number sequence """
        return np.arange(begin, end, step)

    def clearReport(self):
        """ Clears the contents of a project's report file. (EPANET Version 2.2)

        Example:

        >>> d.clearReport()

        See also writeReport, writeLineInReportFile, copyReport.
        """
        self.api.ENclearreport()

    def closeHydraulicAnalysis(self):
        """ Closes the hydraulic analysis system, freeing all allocated memory.

        Example:

        >>> d.closeHydraulicAnalysis()

        For more, you can type `help getNodePressure` and check examples 3 & 4.

        See also openHydraulicAnalysis(), saveHydraulicFile, closeQualityAnalysis().
        """
        self.api.ENcloseH()

    def closeNetwork(self):
        """ Closes down the Toolkit system.

        Example:

        >>> d.closeNetwork()

        See also loadEPANETFile, closeHydraulicAnalysis(), closeQualityAnalysis().
        """
        self.api.ENclose()

    def closeQualityAnalysis(self):
        """ Closes the water quality analysis system, freeing all allocated memory.

        Example:

        >>> d.closeQualityAnalysis()

        For more, you can type help (d.epanet.getNodePressure) and check examples 3 & 4.

        See also openQualityAnalysis(), initializeQualityAnalysis, closeHydraulicAnalysis().
        """
        self.api.ENcloseQ()

    def copyReport(self, fileName):
        """ Copies the current contents of a project's report file to another file. (EPANET Version 2.2)

        Example:

        >>> fileName = 'Report_copy'
        >>> d.copyReport(fileName)

        See also writeReport, writeLineInReportFile, clearReport.
        """
        self.api.ENcopyreport(fileName)

    def createProject(self):
        """ Creates a new epanet project
        """
        self.api.ENcreateproject()

    def deleteAllTemps(self):
        """ Delete all temporary files (.inp, .bin) created in networks folder
        """
        net_dir = os.path.dirname(self.TempInpFile)
        for filename in os.listdir(net_dir):
            if 'temp' in filename:
                try:
                    os.remove(os.path.join(net_dir, filename))
                except:
                    pass

    def deleteControls(self, *argv):
        """ Deletes an existing simple control. (EPANET Version 2.2)

        Example 1: 

        >>> d.getControls()                                                # Retrieves the parameters of all control statements
        >>> d.deleteControls()                                             # Deletes the existing simple controls
        >>> d.getControls()

        Example 2:

        >>> index = d.addControls('LINK 9 43.2392 AT TIME 4:00:00')        # Adds a new simple control(index = 3)
        >>> d.getControls(index)
        >>> d.deleteControls(index)                                        # Deletes the 3rd simple control
        >>> d.getControls()

        Example 3:

        >>> index_3 = d.addControls('LINK 9 43.2392 AT TIME 4:00:00')     # Adds a new simple control(index = 3)
        >>> index_4 = d.addControls('LINK 10 43.2392 AT TIME 4:00:00')    # Adds a new simple control(index = 4)
        >>> d.getControls(index_3)
        >>> d.getControls(index_4)
        >>> d.deleteControls([index_3, index_4])                          # Deletes the 3rd and 4th simple controls
        >>> d.getControls()

        See also addControls, setControls, getControls, getControlRulesCount.
        """
        if len(argv) == 0:
            index = list(range(1, self.getControlRulesCount() + 1))
        else:
            index = argv[0]
        if not isList(index): index = [index]
        for i in reversed(index):
            self.api.ENdeletecontrol(i)

    def deleteCurve(self, idCurve):
        """ Deletes a data curve from a project.

        Example 1:

        >>> d = epanet('BWSN_Network_1.inp')
        >>> idCurve = d.getCurveNameID(1)    # Retrieves the ID of the 1st curve
        >>> d.deleteCurve(idCurve)           #  Deletes a curve given it's ID
        >>> d.getCurveNameID()

        Example 2:

        >>> index = 1
        >>> d.deleteCurve(index)             # Deletes a curve given it's index
        >>> d.getCurveNameID()

        See also addCurve, setCurve, setCurveNameID, setCurveValue, setCurveComment.
        """
        if type(idCurve) is str:
            indexCurve = self.getCurveIndex(idCurve)
        else:
            indexCurve = idCurve
        self.api.ENdeletecurve(indexCurve)

    def deleteLink(self, idLink, *argv):
        """ Deletes a link.

        condition = 0 | if is EN_UNCONDITIONAL: Deletes all controls and rules related to the object
        condition = 1 | if is EN_CONDITIONAL: Cancel object deletion if contained in controls and rules
        Default condition is 0.

        Example 1:

        >>> d.getLinkNameID()                    # Retrieves the ID label of all links
        >>> idLink = d.getLinkNameID(1)          # Retrieves the ID label of the 1st link
        >>> d.deleteLink(idLink)                 # Deletes the 1st link given it's ID
        >>> d.getLinkNameID()

        Example 2:

        >>> idLink = d.getLinkPumpNameID(1)
        >>> condition = 1
        >>> d.deleteLink(idLink, condition)      # Attempts to delete a link contained in controls (error occurs)

        Example 3:

        >>> indexLink = 1
        >>> d.deleteLink(indexLink)              # Deletes the 1st link given it's index
        >>> d.getLinkNameID()

        See also addLinkPipe, deleteNode, deleteRules, setNodeCoordinates, setLinkPipeData.
        """
        condition = 0
        if len(argv) == 1:
            condition = argv[0]
        if type(idLink) is str:
            indexLink = self.getLinkIndex(idLink)
        else:
            indexLink = idLink
        self.api.ENdeletelink(indexLink, condition)

    def deleteNode(self, idNode, *argv):
        """ Deletes nodes. (EPANET Version 2.2)

        condition = 0 | if is EN_UNCONDITIONAL: Deletes all controls, rules and links related to the object
        condition = 1 | if is EN_CONDITIONAL: Cancel object deletion if contained in controls, rules and links
        Default condition is 0.

        Example 1:

        >>> d.getNodeCount()                   # Retrieves the total number of all nodes
        >>> idNode = d.getNodeNameID(1)        # Retrieves the ID label of the 1st node
        >>> d.deleteNode(idNode)               # Deletes the 1st node given it's ID
        >>> d.getNodeCount()

        Example 2:

        >>> idNode = d.getNodeNameID(1)
        >>> condition = 1
        >>> d.deleteNode(idNode, condition)    # Attempts to delete a node connected to links (error occurs)

        Example 3:

        >>> index = 1
        >>> d.deleteNode(index)                # Deletes the 1st node given it's index
        >>> d.getNodeNameID()

        Example 4:

        >>> idNodes = d.getNodeNameID([1,2])
        >>> d.getNodeCount()
        >>> d.deleteNode(idNodes)              # Deletes 2 nodes given their IDs
        >>> d.getNodeCount()

        See also addNodeJunction, deleteLink, deleteRules, setNodeCoordinates, setNodeJunctionData.
        """
        condition = 0
        if len(argv) == 1:
            condition = argv[0]
        if type(idNode) is str:
            idNode = [idNode]
        if isList(idNode):
            for j in idNode:
                indexNode = self.getNodeIndex(j)
                self.api.ENdeletenode(indexNode, condition)
        else:
            self.api.ENdeletenode(idNode, condition)

    def deleteNodeJunctionDemand(self, *argv):
        """ Deletes a demand from a junction given the junction index and demand index. (EPANET Version 2.2)
        Returns the remaining(if exist) node demand indices.

        Example 1:
        >>> nodeIndex = 1
        >>> baseDemand = 100
        >>> patternId = '1'
        >>> categoryIndex = 1
        >>> d.getNodeJunctionDemandIndex(nodeIndex)                                                    # Retrieves the indices of all demands for the 1st node
        >>> d.getNodeJunctionDemandName()                                                              # Retrieves the names of all nodes demand category
        >>> d.getNodeJunctionDemandName()[categoryIndex][nodeIndex-1]                                  # Retrieves the name of the 1st demand category of the 1st node
        >>> categoryIndex = d.addNodeJunctionDemand(nodeIndex, baseDemand, patternId, 'new demand')    # Adds a new demand to the 1st node and returns the new demand index
        >>> d.getNodeJunctionDemandIndex(nodeIndex)                                                    # Retrieves the indices of all demands for the 1st node
        >>> d.getNodeJunctionDemandName()                                                              # Retrieves the names of all nodes demand category
        >>> d.getNodeJunctionDemandName()[categoryIndex][nodeIndex-1]                                  # Retrieves the name of the 2nd demand category of the 1st node
        >>> d.deleteNodeJunctionDemand(1, 2)                                                           # Deletes the 2nd demand of the 1st node
        >>> d.getNodeJunctionDemandIndex(nodeIndex)

        Example 2:
        >>> nodeIndex = 1
        >>> baseDemand = 100
        >>> patternId = '1'
        >>> categoryIndex_2 = d.addNodeJunctionDemand(nodeIndex, baseDemand, patternId, 'new demand_2')   # Adds a new demand to the first node and returns the new demand index
        >>> categoryIndex_3 = d.addNodeJunctionDemand(nodeIndex, baseDemand, patternId, 'new demand_3')   # Adds a new demand to the first node and returns the new demand index
        >>> d.getNodeJunctionDemandName()[categoryIndex_2][nodeIndex-1]                                   # Retrieves the name of the 2nd demand category of the 1st node
        >>> d.deleteNodeJunctionDemand(1)                                                                 # Deletes all the demands of the 1st node
        >>> d.getNodeJunctionDemandIndex(nodeIndex)                                                       # Retrieves the indices of all demands for the 1st node

        Example 3:
        >>> nodeIndex = [1, 2, 3]
        >>> baseDemand = [100, 110, 150]
        >>> patternId = ['1', '1', '']
        >>> categoryIndex = d.addNodeJunctionDemand(nodeIndex, baseDemand, patternId,
        ...                                        ['new demand_1', 'new demand_2', 'new demand_3'])     # Adds 3 new demands to the first 3 nodes
        >>> d.getNodeJunctionDemandName()[2]
        >>> d.getNodeJunctionDemandIndex(nodeIndex)
        >>> d.deleteNodeJunctionDemand([1,2,3])                                     # Deletes all the demands of the first 3 nodes
        >>> d.getNodeJunctionDemandIndex(nodeIndex)


        See also addNodeJunctionDemand, getNodeJunctionDemandIndex, getNodeJunctionDemandName,
                 setNodeJunctionDemandName, getNodeBaseDemands.
        """
        nodeIndex = argv[0]
        if len(argv) == 1:
            numDemand = len(self.getNodeJunctionDemandIndex())
            if not isList(nodeIndex):
                for i in range(1,numDemand+1):
                    self.api.ENdeletedemand(nodeIndex, 1)
            else:
                for j in nodeIndex:
                    for i in range(1,numDemand+1):
                        self.api.ENdeletedemand(j, 1)

        elif len(argv) == 2:
            self.api.ENdeletedemand(nodeIndex, argv[1])

    def deletePattern(self, idPat):
        """ Deletes a time pattern from a project.

        Example 1:

        >>> idPat = d.getPatternNameID(1)    # Retrieves the ID of the 1st pattern
        >>> d.deletePattern(idPat)           # Deletes the 1st pattern given it's ID
        >>> d.getPatternNameID()

        Example 2:

        >>> index = 1
        >>> d.deletePattern(index)           # Deletes the 1st pattern given it's index
        >>> d.getPatternNameID()

        See also deletePatternsAll, addPattern, setPattern, setPatternNameID, 
        setPatternValue, setPatternComment.
        """
        if type(idPat) is str:
            indexPat = self.getPatternIndex(idPat)
        else:
            indexPat = idPat
        self.api.ENdeletepattern(indexPat)

    def deletePatternsAll(self):
        """ Deletes all time patterns from a project.

        Example 1:

        >>> d.getPatternNameID()        # Retrieves the IDs of all the patterns
        >>> d.deletePatternsAll()       # Deletes all the patterns
        >>> d.getPatternNameID()

        See also deletePattern, addPattern, setPattern, setPatternNameID, 
        setPatternValue, setPadtternComment.
        """
        idPat = self.getPatternIndex()
        for i in range(len(idPat),0,-1):
            self.api.ENdeletepattern(i)

    def deleteProject(self):
        """ Deletes the epanet project
        """
        self.api.ENdeleteproject()

    def deleteRules(self, *argv):
        """ Deletes an existing rule-based control given it's index. (EPANET Version 2.2)
        Returns error code.

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> d.getRuleCount()        # Retrieves the number of rules
        >>> d.deleteRules()         # Deletes all the rule-based control
        >>> d.getRuleCount()

        Example 2:

        >>> d.deleteRules(1)        # Deletes the 1st rule-based control
        >>> d.getRuleCount()

        Example 3:

        >>> d.deleteRules([1,2,3])  # Deletes the 1st to 3rd rule-based control
        >>> d.getRuleCount()

        See also addRules, getRules, setRules, getRuleCount().
        """
        if len(argv) == 0:
            index = list(range(1, self.getRuleCount() + 1))
        elif isList(argv[0]):
            index = argv[0]
        else:
            index = [argv[0]]
        for i in range(len(index), 0, -1):
            self.api.ENdeleterule(index[i-1])

    def getENfunctionsImpemented(self):
        """ Retrieves the epanet functions that have been developed.

        Example:

        >>> d.getENfunctionsImpemented()

        See also getLibFunctions, getVersion.
        """
        en_funcs = getmembers(epanetapi, isfunction)
        en_functions = []
        for i in en_funcs:
            en_functions.append(i[0])
        en_functions.remove('__init__')
        return en_functions

    def getNodeActualQualitySensingNodes(self, *argv):
        """ Retrieves the computed quality values at some sensing nodes

        Example:

        >>> d.getNodeActualQualitySensingNodes(1)      # Retrieves the computed quality value at the first node
        >>> d.getNodeActualQualitySensingNodes(1,2,3)  # Retrieves the computed quality value at the first three nodes

        For more, you can check examples 3 & 4 of getNodePressure.

        See also getNodeActualDemand, getNodeActualDemandSensingNodes, getNodePressure,
        getNodeHydraulicHead, getNodeActualQuality, getNodeMassFlowRate.
        """
        value = []
        if len(argv) > 0:
            indices = argv[0]
        else:
            indices = self.getNodeIndex()
        for i in indices:
            value.append(self.api.ENgetnodevalue(i, self.ToolkitConstants.EN_QUALITY))
        return np.array(value)

    def getCMDCODE(self):
        """ Retrieves the CMC code """
        return self.CMDCODE

    def getComputedHydraulicTimeSeries(self, matrix=True, *argv):
        """ Computes hydraulic simulation and retrieves all time-series.

        Data that is computed:
          1) Time              8)  Velocity
          2) Pressure          9)  HeadLoss
          3) Demand            10) Status
          4) DemandDeficit     11) Setting
          5) Head              12) Energy
          6) TankVolume        13) Efficiency
          7) Flow

        Example 1:

        >>> d.getComputedHydraulicTimeSeries()               # Retrieves all the time-series data

        Example 2:

        >>> d.getComputedHydraulicTimeSeries().Demand        # Retrieves all the time-series demands
        >>> d.getComputedHydraulicTimeSeries().Flow          # Retrieves all the time-series flows

        Example 3:
        >>> data = d.getComputedHydraulicTimeSeries(['Time',
        ...  'Pressure', 'Velocity'])                        # Retrieves all the time-series Time, Pressure, Velocity
        >>> time = data.Time
        >>> pressure = data.Pressure
        >>> velocity = data.Velocity

        See also getComputedQualityTimeSeries, getComputedTimeSeries.
        """
        value = val()
        self.openHydraulicAnalysis()
        self.api.solve = 1
        self.initializeHydraulicAnalysis()
        if len(argv) == 0:
            attrs = ['time', 'pressure', 'demand', 'demanddeficit', 'head', 'tankvolume', 'flow', 'velocity',
                     'headloss', 'status', 'setting', 'energy', 'efficiency', 'state']
        else:
            attrs = argv[0]
            for i in attrs:
                if type(i) is int:
                    sensingnodes = i
        if 'time' in attrs:
            value.Time = []
        if 'pressure' in attrs:
            value.Pressure = {}
        if 'demand' in attrs:
            value.Demand = {}
        if 'demanddeficit' in attrs:
            value.DemandDeficit = {}
        if 'demandSensingNodes' in attrs:
            value.DemandSensingNodes = {}  # zeros(totalsteps, length(attrs{sensingnodes}:
            value.SensingNodesIndices = attrs[sensingnodes - 1]
        if 'head' in attrs:
            value.Head = {}
        if 'tankvolume' in attrs:
            value.TankVolume = {}
        if 'flow' in attrs:
            value.Flow = {}
        if 'velocity' in attrs:
            value.Velocity = {}
        if 'headloss' in attrs:
            value.HeadLoss = {}
        if 'status' in attrs:
            value.Status = {}
            value.StatusStr = {}
        if 'setting' in attrs:
            value.Setting = {}
        if 'energy' in attrs:
            value.Energy = {}
        if 'efficiency' in attrs:
            value.Efficiency = {}
        if 'state' in attrs:
            value.State = {}
            value.StateStr = {}
        k, tstep = 1, 1
        while tstep > 0:
            t = self.runHydraulicAnalysis()
            if 'time' in attrs:
                value.Time.append(t)
            if 'pressure' in attrs:
                value.Pressure[k] = self.getNodePressure()
            if 'demand' in attrs:
                value.Demand[k] = self.getNodeActualDemand()
            if 'demanddeficit' in attrs:
                value.DemandDeficit[k] = self.getNodeDemandDeficit()
            if 'demandSensingNodes' in attrs:
                value.DemandSensingNodes[k] = self.getNodeActualDemandSensingNodes(attrs[sensingnodes - 1])
            if 'head' in attrs:
                value.Head[k] = self.getNodeHydraulicHead()
            if 'tankvolume' in attrs:
                value.TankVolume[k] = np.zeros(self.getNodeJunctionCount() + self.getNodeReservoirCount())
                value.TankVolume[k] = np.concatenate((value.TankVolume[k], self.getNodeTankVolume()))
            if 'flow' in attrs:
                value.Flow[k] = self.getLinkFlows()
            if 'velocity' in attrs:
                value.Velocity[k] = self.getLinkVelocity()
            if 'headloss' in attrs:
                value.HeadLoss[k] = self.getLinkHeadloss()
            if 'status' in attrs:
                value.Status[k] = self.getLinkStatus()
                value.StatusStr[k] = []
                for i in value.Status[k]:
                    value.StatusStr[k].append(self.TYPESTATUS[i])
                value.StatusStr[k] = np.array(value.StatusStr[k])
            if 'setting' in attrs:
                value.Setting[k] = self.getLinkSettings()
            if 'energy' in attrs:
                value.Energy[k] = self.getLinkEnergy()
            if 'efficiency' in attrs:
                value.Efficiency[k] = np.zeros(self.getLinkPipeCount())
                value.Efficiency[k] = np.concatenate((value.Efficiency[k], self.getLinkPumpEfficiency()))
                value.Efficiency[k] = np.concatenate((value.Efficiency[k], np.zeros(self.getLinkValveCount())))
            if 'state' in attrs:
                value.State[k] = self.getLinkPumpState()
                value.StateStr[k] = []
                for i in value.State[k]:
                    value.StateStr[k].append(self.TYPEPUMPSTATE[int(i)])
                value.StateStr[k] = np.array(value.StateStr[k])
            tstep = self.nextHydraulicAnalysisStep()
            k += 1
        self.closeHydraulicAnalysis()
        value.Time = np.array(value.Time)

        value_final = val()
        val_dict = value.__dict__
        for i in val_dict:
            if type(val_dict[i]) is dict:
                exec(f"value_final.{i} = np.array(list(val_dict[i].values()))")
            else:
                exec(f"value_final.{i} = val_dict[i]")
        return value_final

    def getComputedQualityTimeSeries(self, *argv):
        """ Computes Quality simulation and retrieves all or some time-series.

        Data that is computed:
          1) Time
          2) NodeQuality
          3) LinkQuality
          4) MassFlowRate

        Example 1:

        >>> d.getComputedQualityTimeSeries()               # Retrieves all the time-series data

        Example 2:

        >>> d.getComputedQualityTimeSeries().NodeQuality   # Retrieves all the time-series node quality
        >>> d.getComputedQualityTimeSeries().LinkQuality   # Retrieves all the time-series link quality

        Example 3:

        >>> data = d.getComputedQualityTimeSeries(['time',
        ... 'nodequality', 'linkquality'])                # Retrieves all the time-series Time, NodeQuality, LinkQuality
        >>> time = data.Time
        >>> node_quality = data.NodeQuality
        >>> link_quality = data.LinkQuality

        See also getComputedHydraulicTimeSeries, getComputedTimeSeries.
        """
        value = val()
        if not self.api.solve:
            self.solveCompleteHydraulics()
            self.api.solve = 1
        self.openQualityAnalysis()
        self.initializeQualityAnalysis()
        # tleft = self.nextQualityAnalysisStep()
        if len(argv) == 0:
            attrs = ['time', 'nodequality', 'linkquality', 'mass']
        else:
            attrs = argv[0]
            for i in attrs:
                if type(i) is int:
                    sensingnodes = i
        if 'time' in attrs:
            value.Time = []
        if 'nodequality' in attrs:
            value.NodeQuality = {}
        if 'linkquality' in attrs:
            value.LinkQuality = {}
        if 'qualitySensingNodes' in attrs:
            value.QualitySensingNodes = {}
            value.SensingNodesIndices = attrs[sensingnodes - 1]
        if 'demandSensingNodes' in attrs:
            value.DemandSensingNodes = {}
            value.SensingNodesIndices = attrs[sensingnodes - 1]
        if 'mass' in attrs:
            value.MassFlowRate = {}
        if 'demand' in attrs:
            value.Demand = {}
        k, t, tleft = 1, 1, 1
        sim_duration = self.getTimeSimulationDuration()
        while tleft > 0 or t < sim_duration:
            t = self.runQualityAnalysis()
            if 'time' in attrs:
                value.Time.append(t)
            if 'nodequality' in attrs:
                value.NodeQuality[k] = self.getNodeActualQuality()
            if 'linkquality' in attrs:
                value.LinkQuality[k] = self.getLinkActualQuality()
            if 'mass' in attrs:
                value.MassFlowRate[k] = self.getNodeMassFlowRate()
            if 'demand' in attrs:
                value.Demand[k] = self.getNodeActualDemand()
            if 'qualitySensingNodes' in attrs:
                value.QualitySensingNodes[k] = self.getNodeActualQualitySensingNodes(argv[1])
            if 'demandSensingNodes' in attrs:
                value.DemandSensingNodes[k] = self.getNodeActualDemandSensingNodes(attrs[sensingnodes - 1])
            if t < sim_duration:
                tleft = self.stepQualityAnalysisTimeLeft()
            k += 1
        self.closeQualityAnalysis()
        value.Time = np.array(value.Time)
        value_final = val()
        val_dict = value.__dict__
        for i in val_dict:
            if type(val_dict[i]) is dict:
                exec(f"value_final.{i} = np.array(list(val_dict[i].values()))")
            else:
                exec(f"value_final.{i} = val_dict[i]")
        return value_final

    def getComputedTimeSeries(self):
        """ Run analysis using .exe file """
        self.saveInputFile(self.TempInpFile)
        [fid, binfile, _] = self.runEPANETexe()
        if fid is False:  # temporary.
            value_final = self.getComputedTimeSeries_ENepanet()
            return value_final
        value = self.__readEpanetBin(fid, binfile, 0)
        value.StatusStr = {}
        for i in range(1, len(value.Status) + 1):
            value.StatusStr[i] = []
            for j in value.Status[i]:
                value.StatusStr[i].append(self.TYPEBINSTATUS[int(j)])
            value.StatusStr[i] = np.array(value.StatusStr[i])

        # Remove report bin txt , files @#
        for file in Path(".").glob("@#*.txt"):
            file.unlink()
        value.Time = np.array(value.Time)
        value_final = val()
        val_dict = value.__dict__
        for i in val_dict:
            if type(val_dict[i]) is dict:
                exec(f"value_final.{i} = np.array(list(val_dict[i].values()))")
            else:
                exec(f"value_final.{i} = val_dict[i]")
        value_final.Status = value_final.Status.astype(int)
        return value_final

    def getComputedTimeSeries_ENepanet(self):
        """ Run analysis using ENepanet function """
        self.saveInputFile(self.TempInpFile)
        uuID = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        rptfile = self.TempInpFile[0:-4] + '.txt'
        binfile = '@#' + uuID + '.bin'
        self.api.ENepanet(self.TempInpFile, rptfile, binfile)
        fid = open(binfile, "rb")
        value = self.__readEpanetBin(fid, binfile, 0)
        value.StatusStr = {}
        for i in range(1, len(value.Status) + 1):
            value.StatusStr[i] = []
            for j in value.Status[i]:
                value.StatusStr[i].append(self.TYPEBINSTATUS[int(j)])
        # Remove report bin txt , files @#
        for file in Path(".").glob("@#*.txt"):
            file.unlink()
        value.Time = np.array(value.Time)
        value_final = val()
        val_dict = value.__dict__
        for i in val_dict:
            if type(val_dict[i]) is dict:
                exec(f"value_final.{i} = np.array(list(val_dict[i].values()))")
            else:
                exec(f"value_final.{i} = val_dict[i]")
        value_final.Status = value_final.Status.astype(int)
        return value_final

    def getConnectivityMatrix(self):
        """ Retrieve the Connectivity Matrix of the network """
        conn_ind = self.getNodesConnectingLinksIndex()
        cnt = self.getNodeCount()
        value = np.zeros((cnt, cnt), dtype=int)
        for i in conn_ind:
            value[i[0] - 1][i[1] - 1] += 1
            value[i[1] - 1][i[0] - 1] += 1
        return value

    def getControls(self, *argv):
        """ Retrieves the parameters of all control statements.

        The example is based on d = epanet('Net1.inp')

        Example :

        >>> d.getControls()             # Retrieves the parameters of all control statements
        >>> d.getControls(1).Type       # Retrieves the type of the 1st control
        >>> d.getControls(1).LinkID     # Retrieves the ID of the link associated with the 1st control
        >>> d.getControls(1).Setting    # Retrieves the setting of the link associated with the 1st control
        >>> d.getControls(1).NodeID     # Retrieves the ID of the node associated with the 1st control
        >>> d.getControls(1).Value      # Retrieves the value of the node associated with the 1st control
        >>> d.getControls(1).Control    # Retrieves the 1st control statement
        >>> d.getControls(1).to_dict()  # Retrieves all the parameters of the first control statement in a dict
        >>> d.getControls([1,2])        # Retrieves the parameters of the first two control statements

        See also setControls, addControls, deleteControls,
                      getRules, setRules, addRules, deleteRules.
        """
        indices = self.__getControlIndices(*argv)
        value = {}
        self.ControlTypes = []
        self.ControlTypesIndex, self.ControlLinkIndex, self.ControlSettings, self.ControlTypes, \
        self.ControlNodeIndex, self.ControlLevelValues = [], [], [], [], [], []
        if not isList(indices):
            indices = [indices]
        for i in indices:
            [v1, v2, v3, v4, v5] = self.api.ENgetcontrol(i)
            self.ControlTypesIndex.append(v1)
            self.ControlLinkIndex.append(v2)
            self.ControlSettings.append(float(v3))
            self.ControlNodeIndex.append(v4)
            self.ControlLevelValues.append(v5)
            self.ControlTypes.append(self.TYPECONTROL[self.ControlTypesIndex[-1]])
            value[i] = val()
            value[i].Type = self.ControlTypes[-1]
            # value[i].TypeIndex = self.ControlTypesIndex[i-1]
            value[i].LinkID = self.getLinkNameID(self.ControlLinkIndex[-1])
            if self.ControlSettings[-1] not in [0, 1]:
                value[i].Setting = self.ControlSettings[-1]
            else:
                value[i].Setting = self.TYPESTATUS[int(self.ControlSettings[-1])]
            if self.ControlNodeIndex[-1]:
                value[i].NodeID = self.getNodeNameID(self.ControlNodeIndex[-1])
            else:
                value[i].NodeID = None
            value[i].Value = self.ControlLevelValues[-1]
            if self.ControlTypes[-1] == 'LOWLEVEL':
                value[i].Control = 'LINK ' + value[i].LinkID + ' ' + value[i].Setting + ' IF NODE ' + \
                                   value[i].NodeID + ' BELOW ' + str(value[i].Value)
            elif self.ControlTypes[-1] == 'HIGHLEVEL':
                value[i].Control = 'LINK ' + value[i].LinkID + ' ' + value[i].Setting + ' IF NODE ' + \
                                   value[i].NodeID + ' ABOVE ' + str(value[i].Value)
            elif self.ControlTypes[-1] == 'TIMER':
                value[i].Control = 'LINK ' + value[i].LinkID + ' ' + str(value[i].Setting) + \
                                   ' AT TIME ' + str(value[i].Value)
            elif self.ControlTypes[-1] == 'TIMEOFDAY':
                value[i].Control = 'LINK ' + value[i].LinkID + ' ' + str(value[i].Setting) + \
                                   ' AT CLOCKTIME ' + str(value[i].Value)
        if len(argv) == 0:
            return value
        elif isList(argv[0]):
            return [value.get(ruleIndex) for ruleIndex in argv[0]]
        else:
            return value[argv[0]]

    def getControlRulesCount(self):
        """ Retrieves the number of controls.

        Example:

        >>> d.getControlRulesCount()

        See also getControls, getRuleCount.
        """
        return self.api.ENgetcount(self.ToolkitConstants.EN_CONTROLCOUNT)

    def getCurveComment(self, *argv):
        """ Retrieves the comment string of a curve.

        Example 1:

        >>> d.getCurveComment()       # Retrieves the comment string assigned to all the curves

        Example 2:

        >>> d.getCurveComment(1)      # Retrieves the comment string assigned to the 1st curve

        Example 3:

        >>> d.getCurveComment([1,2])  # Retrieves the comment string assigned to the first 2 curves

        See also getCurveNameID, getCurveType, getCurvesInfo
        """
        if len(argv) == 0:
            value = []
            for i in range(1, self.getCurveCount() + 1):
                value.append(self.api.ENgetcomment(self.ToolkitConstants.EN_CURVE, i))
        elif isList(argv[0]):
            value = []
            for i in argv[0]:
                value.append(self.api.ENgetcomment(self.ToolkitConstants.EN_CURVE, i))
        else:
            value = self.api.ENgetcomment(self.ToolkitConstants.EN_CURVE, argv[0])
        return value

    def getCounts(self):
        """ Retrieves the number of network components.
        Nodes, Links, Junctions, Reservoirs, Tanks, Pipes, Pumps,
        Valves, Curves, SimpleControls, RuleBasedControls, Patterns.

        Example:

        >>> counts = d.getCounts().to_dict()    # Retrieves the number of all network components
        >>> d.getCounts().Nodes                # Retrieves the number of nodes
        >>> d.getCounts().SimpleControls       # Retrieves the number of simple controls

        See also getNodeCount(), getNodeJunctionCount(), getLinkCount(), getControlRulesCount().
        """
        value = val()
        value.Nodes = self.getNodeCount()
        value.Links = self.getLinkCount()
        value.Junctions = self.getNodeJunctionCount()
        value.Reservoirs = self.getNodeReservoirCount()
        value.Tanks = self.getNodeTankCount()
        value.Pipes = self.getLinkPipeCount()
        value.Pumps = self.getLinkPumpCount()
        value.Valves = self.getLinkValveCount()
        value.Curves = self.getCurveCount()
        value.SimpleControls = self.getControlRulesCount()
        value.RuleBasedControls = self.getRuleCount()
        value.Patterns = self.getPatternCount()
        return value

    def getCurveCount(self):
        """ Retrieves the number of curves.

        Example:

        >>> d.getCurveCount()

        See also getCurveIndex, getCurvesInfo.
        """
        return self.api.ENgetcount(self.ToolkitConstants.EN_CURVECOUNT)

    def getCurveIndex(self, *argv):
        """ Retrieves the index of a curve with specific ID. (EPANET Version 2.1)

        Example 1:

        >>> d.getCurveIndex()              # Retrieves the indices of all the curves

        Example 2:

        >>> curveID = d.getCurveNameID(1)
        >>> d.getCurveIndex(curveID)       # Retrieves the index of the 1st curve given it's ID

        Example 3:

        >>> curveID = d.getCurveNameID([1,2])
        >>> d.getCurveIndex(curveID)       # Retrieves the indices of the first 2 curves given their ID

        See also getCurveNameID, getCurvesInfo.
        """
        if len(argv) == 0:
            value = list(range(1, self.getCurveCount() + 1))
        elif isList(argv[0]):
            value = []
            for j in range(len(argv[0])):
                value.append(self.api.ENgetcurveindex(argv[0][j]))
        else:
            return self.api.ENgetcurveindex(argv[0])
        return value

    def getCurveLengths(self, *argv):
        """ Retrieves number of points in a curve. (EPANET Version 2.1)

        The examples are based on: d = epanet('Richmond_standard.inp')

        Example:

        >>> d.getCurveLengths()         # Retrieves the number of points in all the curves
        >>> d.getCurveLengths(1)        # Retrieves the number of points in the 1st curve
        >>> d.getCurveLengths([1,2])    # Retrieves the number of points in the first 2 curves
        >>> d.getCurveLengths('1006')   # Retrieves the number of points for curve with id = '1'

        See also getCurvesInfo, setCurve.
        """
        value = []
        if len(argv) == 0:
            for i in range(1, self.getCurveCount() + 1):
                value.append(self.api.ENgetcurvelen(i))
        else:
            curves = argv[0]
            if not isList(curves):
                if type(curves) is int:
                    return self.api.ENgetcurvelen(curves)
                elif type(curves) is str:
                    return self.api.ENgetcurvelen(self.getCurveIndex(curves))
                else:
                    curves = [curves]
            if type(curves[0]) is str:
                for i in range(len(curves)):
                    value.append(self.api.ENgetcurvelen(self.getCurveIndex(curves[i])))
            else:
                for i in range(1, len(curves) + 1):
                    value.append(self.api.ENgetcurvelen(i))
        return value

    def getCurveNameID(self, *argv):
        """Retrieves the IDs of curves. (EPANET Version 2.1)

        Example:

        >>> d.getCurveNameID()         # Retrieves the IDs of all the curves
        >>> d.getCurveNameID(1)        # Retrieves the ID of the 1st curve
        >>> d.getCurveNameID([1,2])    # Retrieves the IDs of the first 2 curves

        See also setCurveNameID, getCurvesInfo.
        """
        curCnt = self.getCurveCount()
        value = []
        if curCnt:
            if len(argv) == 0:
                for i in range(1, curCnt + 1):
                    value.append(self.api.ENgetcurveid(i))
            elif isList(argv[0]):
                for i in argv[0]:
                    value.append(self.api.ENgetcurveid(i))
            else:
                value = self.api.ENgetcurveid(argv[0])
        return value

    def getCurvesInfo(self):
        """
        Retrieves all the info of curves. (EPANET Version 2.1)

        Returns the following informations:
          1) Curve Name ID
          2) Number of points on curve
          3) X values of points
          4) Y values of points

        Example:

        >>> d.getCurvesInfo().disp()
        >>> d.getCurvesInfo().CurveNameID       # Retrieves the IDs of curves
        >>> d.getCurvesInfo().CurveNvalue       # Retrieves the number of points on curve
        >>> d.getCurvesInfo().CurveXvalue       # Retrieves the X values of points of all curves
        >>> d.getCurvesInfo().CurveXvalue[0]    # Retrieves the X values of points of the 1st curve
        >>> d.getCurvesInfo().CurveYvalue       # Retrieves the Y values of points of all curves
        >>> d.getCurvesInfo().CurveYvalue[0]    # Retrieves the Y values of points of the 1st curve

        See also setCurve, getCurveType, getCurveLengths, getCurveValue, getCurveNameID, getCurveComment.
        """
        value = val()
        value.CurveNameID = []
        value.CurveNvalue = []
        value.CurveXvalue = []
        value.CurveYvalue = []
        for i in range(1, self.getCurveCount() + 1):
            tempVal = self.api.ENgetcurve(i)
            value.CurveNameID.append(tempVal['id'])
            value.CurveNvalue.append(tempVal['nPoints'])
            value.CurveXvalue.append(tempVal['x'])
            value.CurveYvalue.append(tempVal['y'])
        return value

    def getCurveType(self, *argv):
        """ Retrieves the curve-type for all curves.

        Example:

        >>> d.getCurveType()        # Retrieves the curve-type for all curves
        >>> d.getCurveType(1)       # Retrieves the curve-type for the 1st curve
        >>> d.getCurveType([1,2])   # Retrieves the curve-type for the first 2 curves

        See also getCurveTypeIndex, getCurvesInfo.
        """
        indices = self.__getCurveIndices(*argv)
        return [self.TYPECURVE[self.getCurveTypeIndex(i)] for i in indices] if isList(indices) \
            else self.TYPECURVE[self.getCurveTypeIndex(indices)]

    def getCurveTypeIndex(self, *argv):
        """ Retrieves the curve-type index for all curves.

        Example:

        >>> d.getCurveTypeIndex()        # Retrieves the curve-type index for all curves
        >>> d.getCurveTypeIndex(1)       # Retrieves the curve-type index for the 1st curve
        >>> d.getCurveTypeIndex([1,2])   # Retrieves the curve-type index for the first 2 curves

        See also getCurveType, getCurvesInfo.
        """
        indices = self.__getCurveIndices(*argv)
        return [self.api.ENgetcurvetype(i) for i in indices] if isList(indices) else self.api.ENgetcurvetype(indices)

    def getCurveValue(self, *argv):
        """ Retrieves the X, Y values of points of curves. (EPANET Version 2.1)

        Example:

        >>> d.getCurveValue()                          # Retrieves all the X and Y values of all curves
        >>> curveIndex = 1
        >>> d.getCurveValue(curveIndex)                # Retrieves all the X and Y values of the 1st curve
        >>> pointIndex = 1
        >>> d.getCurveValue(curveIndex, pointIndex)    # Retrieves the X and Y values of the 1st point of the 1st curve

        See also setCurveValue, setCurve, getCurvesInfo.
        """
        tmplen = self.getCurveLengths()
        pnt = 0
        if len(argv) == 2:
            pnt = argv[1]
        if len(argv) > 0:
            index = argv[0]
        else:
            index = self.getCurveIndex()
        if not isList(index):
            index = [index]
        val = {}
        for i in index:
            value = []
            try:
                for j in range(1, tmplen[i - 1] + 1):
                    if pnt:
                        return np.array(self.api.ENgetcurvevalue(i, pnt))
                    else:
                        value.append(self.api.ENgetcurvevalue(i, j))
            except:
                self.errcode = 206
                errmssg = self.getError(self.errcode)
                raise Exception(errmssg)
            val[i] = value
        return val

    def getDemandModel(self):
        """ Retrieves the type of demand model in use and its parameters.

        Example:

        >>> model = d.getDemandModel()

        See also setDemandModel, getNodeBaseDemands, getNodeDemandCategoriesNumber
        getNodeDemandPatternIndex, getNodeDemandPatternNameID.
        """
        value = val()
        [value.DemandModelCode, value.DemandModelPmin, value.DemandModelPreq,
         value.DemandModelPexp] = self.api.ENgetdemandmodel()
        value.DemandModelType = self.DEMANDMODEL[value.DemandModelCode]
        return value

    def getError(self, Errcode):
        """ Retrieves the text of the message associated with a particular error or warning code.

        Example:

        >>> error = 250
        >>> d.getError(error)
        """
        errmssg = ctypes.create_string_buffer(150)
        self.api._lib.ENgeterror(Errcode, ctypes.byref(errmssg), 150)
        return errmssg.value.decode()

    def getFlowUnits(self):
        """ Retrieves flow units used to express all flow rates.

        Example:

        >>> d.getFlowUnits()
        """
        flowunitsindex = self.api.ENgetflowunits()
        return self.TYPEUNITS[flowunitsindex]

    def getLibFunctions(self):
        """ Retrieves the functions of DLL.

        Example:

        >>> d.getLibFunctions()

        See also getENfunctionsImpemented, getVersion.
        """
        funcs = getmembers(epanetapi, isfunction)
        lib_functions = []
        for i in funcs:
            if not i[0].startswith('_api'):
                lib_functions.append(i[0])
        lib_functions.remove('__init__')
        return lib_functions

    def getLinkComment(self, *argv):
        """Retrieves the comment string assigned to the link object.

        Example 1:

        >>> d.getLinkComment()            # Retrieves the comments of all links

        Example 2:

        >>> linkIndex = 1
        >>> d.getLinkComment(linkIndex)   # Retrieves the comment of the 1st link

        Example 3:

        >>> linkIndex = [1,2,3,4,5]
        >>> d.getLinkComment(linkIndex)   # Retrieves the comments of the first 5 links

        See also setLinkComment, getLinkNameID, getLinksInfo.
        """
        value = []
        indices = self.__getNodeIndices(*argv)
        for i in indices:
            value.append(self.api.ENgetcomment(self.ToolkitConstants.EN_LINK, i))
        return value

    def getLinkCount(self):
        """ Retrieves the number of links.

        Example:

        >>> d.getLinkCount()

        See also getLinkIndex, getNodeCount.
        """
        return self.api.ENgetcount(self.ToolkitConstants.EN_LINKCOUNT)

    def getLinkQuality(self, *argv):
        """ Retrieves the value of link quality. Pipe quality

        Example 1:

        >>> d.getLinkQuality()       # Retrieves the value of all link quality

        Example 2:

        >>> d.getLinkQuality(1)      # Retrieves the value of the first link quality

        See also getLinkType, getLinksInfo, getLinkDiameter,
        getLinkRoughnessCoeff, getLinkMinorLossCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_QUALITY, *argv)

    def getLinkType(self, *argv):
        """ Retrieves the link-type code for all links.

        Example 1:

        >>> d.getLinkType()      # Retrieves the link-type code for all links

        Example 2:

        >>> d.getLinkType(1)     # Retrieves the link-type code for the first link

        See also getLinkTypeIndex, getLinksInfo, getLinkDiameter,
        getLinkLength, getLinkRoughnessCoeff, getLinkMinorLossCoeff.
        """
        lTypes = []
        if len(argv) > 0:
            index = argv[0]
            if type(index) is list:
                for i in index:
                    lTypes.append(self.TYPELINK[self.api.ENgetlinktype(i)])
            else:
                lTypes = self.TYPELINK[self.api.ENgetlinktype(index)]
        else:
            for i in range(self.getLinkCount()):
                lTypes.append(self.TYPELINK[self.api.ENgetlinktype(i + 1)])
        return lTypes

    def getLinkTypeIndex(self, *argv):
        """ Retrieves the link-type code for all links.

        Example:

        >>> d.getLinkTypeIndex()          # Retrieves the link-type code for all links
        >>> d.getLinkTypeIndex(1)         # Retrieves the link-type code for the first link
        >>> d.getLinkTypeIndex([2,3])     # Retrieves the link-type code for the second and third links

        See also getLinkType, getLinksInfo, getLinkDiameter,
        getLinkLength, getLinkRoughnessCoeff, getLinkMinorLossCoeff.
        """
        lTypes = []
        if len(argv) > 0:
            index = argv[0]
            if type(index) is list:
                for i in index:
                    lTypes.append(self.api.ENgetlinktype(i))
            else:
                lTypes = self.api.ENgetlinktype(index)
        else:
            for i in range(self.getLinkCount()):
                lTypes.append(self.api.ENgetlinktype(i + 1))
        return lTypes

    def getLinkDiameter(self, *argv):
        """ Retrieves the value of link diameters.
        Pipe/valve diameter

        Example 1:

        >>> d.getLinkDiameter()      # Retrieves the value of all link diameters
        >>> d.getLinkDiameter(1)     # Retrieves the value of the first link diameter
        >>> d.getLinkDiameter([1,2]) # Retrieves the value of the second and third link diameter

        See also getLinkType, getLinksInfo, getLinkLength,
        getLinkRoughnessCoeff, getLinkMinorLossCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_DIAMETER, *argv)

    def getLinkLength(self, *argv):
        """ Retrieves the value of link lengths.
        Pipe length

        Example:

        >>> d.getLinkLength()        # Retrieves the value of all link lengths
        >>> d.getLinkLength(1)       # Retrieves the value of the first link length

        See also getLinkType, getLinksInfo, getLinkDiameter,
        getLinkRoughnessCoeff, getLinkMinorLossCoeff.ughnessCoeff, getLinkMinorLossCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_LENGTH, *argv)

    def getLinkRoughnessCoeff(self, *argv):
        """ Retrieves the value of link roughness coefficient.
        Pipe roughness coefficient

        Example:

        >>> d.getLinkRoughnessCoeff()        # Retrieves the value of all link roughness coefficients
        >>> d.getLinkRoughnessCoeff(1)       # Retrieves the value of the first link roughness coefficient

        See also getLinkType, getLinksInfo, getLinkDiameter,
        getLinkLength, getLinkMinorLossCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_ROUGHNESS, *argv)

    def getLinkMinorLossCoeff(self, *argv):
        """ Retrieves the value of link minor loss coefficients.
        Pipe/valve minor loss coefficient

        Example:

        >>> d.getLinkMinorLossCoeff()        # Retrieves the value of all link minor loss coefficients
        >>> d.getLinkMinorLossCoeff(1)       # Retrieves the value of the first link minor loss coefficient

        See also getLinkType, getLinksInfo, getLinkDiameter,
        getLinkLength, getLinkRoughnessCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_MINORLOSS, *argv)

    def getLinkNameID(self, *argv):
        """ Retrieves the ID label(s) of all links, or the IDs of an index set of links.

        Example 1:

        >>> d.getLinkNameID()                # Retrieves the ID's of all links

        Example 2:

        >>> linkIndex = 1
        >>> d.getLinkNameID(linkIndex)       # Retrieves the ID of the link with index = 1

        Example 3:

        >>> linkIndices = [1,2,3]
        >>> d.getLinkNameID(linkIndices)     # Retrieves the IDs of the links with indices = 1, 2, 3

        See also getNodeNameID, getLinkPipeNameID, getLinkIndex.
        """
        values = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, (list, np.ndarray)):
                for i in index:
                    values.append(self.api.ENgetlinkid(i))
            else:
                values = self.api.ENgetlinkid(index)
        else:
            for i in range(self.getLinkCount()):
                values.append(self.api.ENgetlinkid(i + 1))
        return values

    def getLinkInitialStatus(self, *argv):
        """ Retrieves the value of all link initial status.
        Initial status (see @ref EN_LinkStatusType)

        Example :

        >>> d.getLinkInitialStatus()        # Retrieves the value of all link initial status
        >>> d.getLinkInitialStatus(1)       # Retrieves the value of the first link initial status

        See also getLinkType, getLinksInfo, getLinkInitialSetting,
        getLinkBulkReactionCoeff, getLinkWallReactionCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_INITSTATUS, *argv)

    def getLinkInitialSetting(self, *argv):
        """ Retrieves the value of all link roughness for pipes or initial speed for pumps or initial setting for valves.

        Example:

        >>> d.getLinkInitialSetting()       # Retrieves the value of all link initial settings
        >>> d.getLinkInitialSetting(1)      # Retrieves the value of the first link initial setting

        See also getLinkType, getLinksInfo, getLinkInitialStatus,
        getLinkBulkReactionCoeff, getLinkWallReactionCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_INITSETTING, *argv)

    def getLinkBulkReactionCoeff(self, *argv):
        """ Retrieves the value of all link bulk chemical reaction coefficient.

        Example:

        >>> d.getLinkBulkReactionCoeff()      # Retrieves the value of all link bulk chemical reaction coefficient
        >>> d.getLinkBulkReactionCoeff(1)     # Retrieves the value of the first link bulk chemical reaction coefficient

        See also getLinkType, getLinksInfo, getLinkRoughnessCoeff, getLinkMinorLossCoeff, getLinkInitialStatus,
        getLinkInitialSetting, getLinkWallReactionCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_KBULK, *argv)

    def getLinkWallReactionCoeff(self, *argv):
        """ Retrieves the value of all pipe wall chemical reaction coefficient.

        Example :

        >>> d.getLinkWallReactionCoeff()      # Retrieves the value of all pipe wall chemical reaction coefficient
        >>> d.getLinkWallReactionCoeff(1)     # Retrieves the value of the first pipe wall chemical reaction coefficient

        See also getLinkType, getLinksInfo, getLinkRoughnessCoeff, getLinkMinorLossCoeff, getLinkInitialStatus,
        getLinkInitialSetting, getLinkBulkReactionCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_KWALL, *argv)

    def getLinkPipeCount(self):
        """ Retrieves the number of pipes.

        Example:

        >>> d.getLinkPipeCount()

        See also getLinkPumpCount, getLinkCount.
        """
        linkTypes = self.getLinkTypeIndex()
        return linkTypes.count(self.ToolkitConstants.EN_CVPIPE) + linkTypes.count(self.ToolkitConstants.EN_PIPE)

    def getLinkPumpEfficiency(self, *argv):
        """ Retrieves the current computed pump efficiency (read only). (EPANET Version 2.2)

        Example :

        >>> d.getLinkPumpEfficiency()        # Retrieves the current computed pump efficiency for all links
        >>> d.getLinkPumpEfficiency(1)       # Retrieves the current computed pump efficiency for the first link

        See also getLinkFlows, getLinkStatus, getLinkPumpState, getLinkSettings, getLinkEnergy, getLinkActualQuality.
        """
        return self.__getPumpLinkInfo(self.ToolkitConstants.EN_PUMP_EFFIC, *argv)

    def getLinkPumpCount(self):
        """ Retrieves the number of pumps.

        Example:

        >>> d.getLinkPumpCount()

        See also getLinkPipeCount, getLinkCount.
        """
        linkTypes = self.getLinkTypeIndex()
        return linkTypes.count(self.ToolkitConstants.EN_PUMP)

    def getLinkPumpECost(self, *argv):
        """ Retrieves the pump average energy price. (EPANET Version 2.2)

        Example 1:

        >>> d.getLinkPumpECost()                # Retrieves the average energy price of all pumps

        Example 2:

        >>> d.getLinkPumpECost(1)               # Retrieves the average energy price of the 1st pump

        Example 3:

        >>> d = epanet('Richmond_standard.inp')
        >>> pIndex = 950
        >>> pIndices = d.getLinkPumpIndex()
        >>> d.getLinkPumpECost(pIndex)           # Retrieves the average energy price of the pump with link index 950

        See also setLinkPumpECost, getLinkPumpPower, getLinkPumpHCurve,
        getLinkPumpEPat, getLinkPumpPatternIndex, getLinkPumpPatternNameID.
        """
        return self.__getPumpLinkInfo(self.ToolkitConstants.EN_PUMP_ECOST, *argv)

    def getLinkPumpECurve(self, *argv):
        """ Retrieves the pump efficiency v. flow curve index. (EPANET Version 2.2)

        Example 1:

        >>> d.getLinkPumpECurve()                # Retrieves the efficiency v. flow curve index of all pumps

        Example 2:

        >>> d.getLinkPumpECurve(1)               # Retrieves the efficiency v. flow curve index of the 1st pump

        Example 3:

        >>> d.getLinkPumpECurve([1,2])           # Retrieves the efficiency v. flow curve index of the first 2 pumps

        Example 4:

        >>> d = epanet('Richmond_standard.inp')  # Retrieves the efficiency v. flow curve index of the pumps with lin index 950
        >>> pIndex = 950
        >>> pIndices = d.getLinkPumpIndex()
        >>> d.getLinkPumpECurve(pIndex)

        See also setLinkPumpECurve, getLinkPumpHCurve, getLinkPumpECost,
        getLinkPumpEPat, getLinkPumpPatternIndex, getLinkPumpPatternNameID.
        """
        value = self.__getPumpLinkInfo(self.ToolkitConstants.EN_PUMP_ECURVE, *argv)
        return self.__returnValue(value)

    def getLinkPumpEPat(self, *argv):
        """ Retrieves the pump energy price time pattern index. (EPANET Version 2.2)

        Example 1:

        >>> d.getLinkPumpEPat()                # Retrieves the energy price time pattern index of all pumps

        Example 2:

        >>> d.getLinkPumpEPat(1)               # Retrieves the energy price time pattern index of the 1st pump

        Example 3:

        >>> d.getLinkPumpEPat([1,2])           # Retrieves the energy price time pattern index of the first 2 pumps

        Example 4:

        >>> d = epanet('Richmond_standard.inp')
        >>> pIndex = 950
        >>> pIndices = d.getLinkPumpIndex()
        >>> d.getLinkPumpEPat(pIndex)           # Retrieves the energy price time pattern index of pump with link index 950

        See also setLinkPumpEPat, getLinkPumpHCurve, getLinkPumpECurve,
        getLinkPumpECost, getLinkPumpPatternIndex, getLinkPumpPatternNameID.
        """
        value = self.__getPumpLinkInfo(self.ToolkitConstants.EN_PUMP_EPAT, *argv)
        return self.__returnValue(value)

    def getLinkPumpHCurve(self, *argv):
        """ Retrieves the pump head v. flow curve index. (EPANET Version 2.2)

        Example 1:

        >>> d.getLinkPumpHCurve()                # Retrieves the head v. flow curve index of all pumps

        Example 2:

        >>> d.getLinkPumpHCurve(1)               # Retrieves the head v. flow curve index of the 1st pump

        Example 3:

        >>> d.getLinkPumpHCurve([1,2])           # Retrieves the head v. flow curve index of the first 2 pumps

        Example 4:

        >>> d = epanet('Richmond_standard.inp')  # Retrieves the head v. flow curve index of pump with link index 950
        >>> pIndex = 950
        >>> pIndices = d.getLinkPumpIndex()
        >>> d.getLinkPumpHCurve(pIndex)

        See also setLinkPumpHCurve, getLinkPumpECurve, getLinkPumpECost,
        getLinkPumpEPat, getLinkPumpPatternIndex, getLinkPumpPatternNameID.
        """
        value = self.__getPumpLinkInfo(self.ToolkitConstants.EN_PUMP_HCURVE, *argv)
        return self.__returnValue(value)

    def getLinkPumpHeadCurveIndex(self):
        """ Retrieves the index of a head curve for all pumps. (EPANET Version 2.1)

        Example:

        >>> [curveIndex, pumpIndex] = d.getLinkPumpHeadCurveIndex()

        See also getLinkPumpHCurve, getLinkPumpECurve.
        """
        pumpIndex = self.getLinkPumpIndex()
        curveIndex = []
        for i in pumpIndex:
            curveIndex.append(self.api.ENgetheadcurveindex(i))
        curveIndex = np.array(curveIndex)
        if len(curveIndex) > 1:
            return [curveIndex, pumpIndex]
        elif len(curveIndex) > 0:
            return [curveIndex[0], pumpIndex[0]]
        else:
            return [None, None]

    def getLinkPumpPatternIndex(self, *argv):
        """ Retrieves the pump speed time pattern index. (EPANET Version 2.1)

        Example 1:

        >>> d.getLinkPumpPatternIndex()                # Retrieves the speed time pattern index of all pumps

        Example 2:

        >>> d.getLinkPumpPatternIndex(1)               # Retrieves the speed time pattern index of the 1st pump

        Example 3:

        >>> d.getLinkPumpPatternIndex([1,2])           # Retrieves the speed time pattern index of the first 2 pumps

        Example 4:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.getLinkPumpPatternIndex(pumpIndex)       # Retrieves the speed time pattern index of the pumps given their indices

        See also setLinkPumpPatternIndex, getLinkPumpPower, getLinkPumpHCurve,
        getLinkPumpECost, getLinkPumpEPat,  getLinkPumpPatternNameID.
        """
        value = self.__getPumpLinkInfo(self.ToolkitConstants.EN_LINKPATTERN, *argv)
        return self.__returnValue(value)

    def getLinkPumpPatternNameID(self, *argv):
        """ Retrieves pump pattern name ID. (EPANET Version 2.1)
        A value of 0 means empty


        Example 1:

        >>> d = epanet('ky10.inp')
        >>> d.getLinkPumpPatternNameID()              # Retrieves the pattern name ID of all pumps

        Example 2:

        >>> d.getLinkPumpPatternNameID(1)             # Retrieves the pattern name ID of the 1st pump

        Example 3:

        >>> d.getLinkPumpPatternNameID([1,2])         # Retrieves the pattern name ID of the first 2 pumps

        Example 4:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.getLinkPumpPatternNameID(pumpIndex)     # Retrieves the pattern name ID of the pumps given their indices

        See also getLinkPumpPower, getLinkPumpHCurve, getLinkPumpECurve,
        getLinkPumpECost, getLinkPumpEPat, getLinkPumpPatternIndex.
        """
        if len(argv) == 0:
            patindices = self.getLinkPumpPatternIndex()
        else:
            patindices = self.getLinkPumpPatternIndex(argv[0])
        if not isinstance(patindices, (list, np.ndarray)):
            patindices = [patindices]
        value = []
        for i in patindices:
            if i == 0:
                value.append('')
            else:
                value.append(self.getPatternNameID(i))
        return value

    def getLinkPumpPower(self, *argv):
        """ Retrieves the pump constant power rating (read only). (EPANET Version 2.2)

        Example 1:

        >>> d.getLinkPumpPower()                # Retrieves the constant power rating of all pumps

        Example 2:

        >>> d.getLinkPumpPower(1)               # Retrieves the constant power rating of the 1st pump

        Example 3:

        >>> d.getLinkPumpPower([1,2])           # Retrieves the constant power rating of the first 2 pumps

        Example 4:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.getLinkPumpPower(pumpIndex)     # Retrieves the constant power rating of the pumps given their indices

        See also getLinkPumpHCurve, getLinkPumpECurve, getLinkPumpECost,
        getLinkPumpEPat, getLinkPumpPatternIndex, getLinkPumpPatternNameID.
        """
        return self.__getPumpLinkInfo(self.ToolkitConstants.EN_PUMP_POWER, *argv)

    def getLinkPumpState(self, *argv):
        """ Retrieves the current computed pump state (read only) (see @ref EN_PumpStateType). (EPANET Version 2.2)
        same as status: open, active, closed
        Using step-by-step hydraulic analysis,

        Example:

        >>> d.getLinkPumpState()        # Retrieves the current computed pump state for all links
        >>> d.getLinkPumpState(1)       # Retrieves the current computed pump state for the first link

        For more, you can check examples 3 & 4 of getLinkFlows function

        See also getLinkFlows, getLinkHeadloss, getLinkStatus,
        getLinkSettings, getLinkEnergy, getLinkPumpEfficiency.
        """
        value = self.__getPumpLinkInfo(self.ToolkitConstants.EN_PUMP_STATE, *argv)
        return self.__returnValue(value)

    def getLinkPumpSwitches(self):
        """ Retrieves the number of pump switches.

        Example:

        >>> d.getLinkPumpSwitches()
        """
        value = []
        status = self.getComputedTimeSeries().Status
        link_indices = self.getLinkPumpIndex()
        if not isList(link_indices):
            link_indices = [link_indices]

        pump_status_arr = np.zeros((len(link_indices), len(status)), dtype=int)
        count = 0
        for key_values in status:
            for j in range(len(link_indices)):
                pump_status_arr[j][count] = int(key_values[:, link_indices[j] - 1])
            count += 1
        for pump_index_status in pump_status_arr:
            value.append(len(np.argwhere(np.diff(pump_index_status))))
        return value

    def getLinkPumpType(self):
        """ Retrieves the type of a pump. (EPANET Version 2.1)

        Example:

        >>> d.getLinkPumpType()

        See also getLinkPumpTypeCode(), getLinkPumpPower.
        """
        v = self.getLinkPumpTypeCode()
        pType = []
        for i in v:
            pType.append(self.TYPEPUMP[i])
        return pType

    def getLinkPumpTypeCode(self):
        """ Retrieves the code of type of a pump. (EPANET Version 2.1)

        Type of pump codes:
          0 = Constant horsepower
          1 = Power function
          2 = User-defined custom curve

        Example:

        >>> d.getLinkPumpTypeCode()         #  Retrieves the all the  pumps type code
        >>> d.getLinkPumpTypeCode()[0]      #  Retrieves the first pump type code

        See also getLinkPumpType, getLinkPumpPower.
        """
        pumpCnt = self.getLinkPumpCount()
        j = 0
        value = [1] * pumpCnt
        if pumpCnt != 0:
            for i in self.getLinkPumpIndex():
                value[j] = self.api.ENgetpumptype(i)
                j += 1
        return value

    def getLinksInfo(self):
        """ Retrieves all link info.

        Example:

        >>> linkInfo =  d.getLinksInfo().to_dict()        # get links info as a dict
        >>> linkInf  =  d.getLinksInfo()                  # get links info as object
        >>> linDiam  =  d.getLinksInfo().LinkDiameter     # get link diameters

        See also getLinkType, getLinkTypeIndex, getLinkDiameter,
        getLinkLength, getLinkRoughnessCoeff, getLinkMinorLossCoeff.
        """
        value = val()
        value.LinkDiameter = []
        value.LinkLength = []
        value.LinkRoughnessCoeff = []
        value.LinkMinorLossCoeff = []
        value.LinkInitialStatus = []
        value.LinkInitialSetting = []
        value.LinkBulkReactionCoeff = []
        value.LinkWallReactionCoeff = []
        value.LinkTypeIndex = []
        value.NodesConnectingLinksIndex = [[0, 0] for i in range(self.getLinkCount())]
        for i in range(1, self.getLinkCount() + 1):
            value.LinkDiameter.append(self.api.ENgetlinkvalue(i, self.ToolkitConstants.EN_DIAMETER))
            value.LinkLength.append(self.api.ENgetlinkvalue(i, self.ToolkitConstants.EN_LENGTH))
            value.LinkRoughnessCoeff.append(self.api.ENgetlinkvalue(i, self.ToolkitConstants.EN_ROUGHNESS))
            value.LinkMinorLossCoeff.append(self.api.ENgetlinkvalue(i, self.ToolkitConstants.EN_MINORLOSS))
            value.LinkInitialStatus.append(self.api.ENgetlinkvalue(i, self.ToolkitConstants.EN_INITSTATUS))
            value.LinkInitialSetting.append(self.api.ENgetlinkvalue(i, self.ToolkitConstants.EN_INITSETTING))
            value.LinkBulkReactionCoeff.append(self.api.ENgetlinkvalue(i, self.ToolkitConstants.EN_KBULK))
            value.LinkWallReactionCoeff.append(self.api.ENgetlinkvalue(i, self.ToolkitConstants.EN_KWALL))
            value.LinkTypeIndex.append(self.api.ENgetlinktype(i))
            xy = self.api.ENgetlinknodes(i)
            value.NodesConnectingLinksIndex[i - 1][0] = xy[0]
            value.NodesConnectingLinksIndex[i - 1][1] = xy[1]
        return value

    def getLinkValveCount(self):
        """ Retrieves the number of valves.

        Example:
        >>> d = epanet('BWSN_Network_1.inp')
        >>> d.getLinkValveCount()

        See also getLinkPumpCount, getLinkCount.
        """
        linkTypes = self.getLinkTypeIndex()
        pipepump = linkTypes.count(self.ToolkitConstants.EN_CVPIPE) + linkTypes.count(
            self.ToolkitConstants.EN_PIPE) + linkTypes.count(self.ToolkitConstants.EN_PUMP)
        value = self.getLinkCount() - pipepump
        return value

    def getLinkFlows(self, *argv):
        """ Retrieves the current computed flow rate (read only).
        Using step-by-step hydraulic analysis

        Example 1:

        >>> d.getLinkFlows()        # Retrieves the current computed flow rate for all links

        Example 2:

        >>> d.getLinkFlows(1)       # Retrieves the current computed flow rate for the first link

        Example 3: Hydraulic analysis step-by-step.

        >>> d.openHydraulicAnalysis()
        >>> d.initializeHydraulicAnalysis()
        >>> tstep, P, T_H, D, H, F, S =1, [], [], [], [], [], []
        >>> while tstep>0:
        ...     t = d.runHydraulicAnalysis()
        ...     P.append(d.getNodePressure())
        ...     D.append(d.getNodeActualDemand())
        ...     H.append(d.getNodeHydraulicHead())
        ...     S.append(d.getLinkStatus())
        ...     F.append(d.getLinkFlows())
        ...     T_H.append(t)
        ...     tstep=d.nextHydraulicAnalysisStep()
        >>> d.closeHydraulicAnalysis()

        Example 4: Hydraulic and Quality analysis step-by-step

        >>> d.openHydraulicAnalysis()
        >>> d.openQualityAnalysis()
        >>> d.initializeHydraulicAnalysis(0)
        >>> d.initializeQualityAnalysis(d.ToolkitConstants.EN_NOSAVE)
        >>> tstep, T, P, F, QN, QL = 1, [], [], [], [], []
        >>> while (tstep>0):
        ...     t  = d.runHydraulicAnalysis()
        ...     qt = d.runQualityAnalysis()
        ...     P.append(d.getNodePressure())
        ...     F.append(d.getLinkFlows())
        ...     QN.append(d.getNodeActualQuality())
        ...     QL.append(d.getLinkActualQuality())
        ...     T.append(t)
        ...     tstep = d.nextHydraulicAnalysisStep()
        ...     qtstep = d.nextQualityAnalysisStep()
        >>> d.closeQualityAnalysis()
        >>> d.closeHydraulicAnalysis()

        See also getLinkVelocity, getLinkHeadloss, getLinkStatus,
        getLinkPumpState, getLinkSettings, getLinkEnergy,
        getLinkActualQuality, getLinkPumpEfficiency.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_FLOW, *argv)

    def getLinkVelocity(self, *argv):
        """ Retrieves the current computed flow velocity (read only).

        Using step-by-step hydraulic analysis

        Example 1:

        >>> d.getLinkVelocity()        # Retrieves the current computed flow velocity for all links

        Example 2:

        >>> d.getLinkVelocity(1)       # Retrieves the current computed flow velocity for the first link

        For more, you can check examples 3 & 4 of getLinkFlows function

        See also getLinkFlows, getLinkHeadloss, getLinkStatus,
        getLinkPumpState, getLinkSettings, getLinkActualQuality.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_VELOCITY, *argv)

    def getLinkVertices(self, *argv):
        """ Retrieves the coordinate's of a vertex point assigned to a link.

        The example is based on d = epanet('Net1.inp')

        Example:

        >>> linkID = '10'
        >>> x = [22, 24, 28]
        >>> y = [69, 68, 69]
        >>> d.setLinkVertices(linkID, x, y)
        >>> linkID = '112'
        >>> x = [10, 24, 18]
        >>> y = [49, 58, 60]
        >>> d.setLinkVertices(linkID, x, y)
        >>> d.getLinkVertices(1)
        >>> d.getLinkVertices(d.getLinkIndex('112'))

        See also setLinkVertices, getLinkVerticesCount.
        """
        if len(argv) > 0:
            if type(argv[0]) == str:
                indices = self.getLinkIndex(argv[0])
            else:
                indices = argv[0]
        else:
            indices = self.getLinkIndex()
        if type(indices) == int:
            indices = [indices]
        x_data = {}
        y_data = {}
        xy = []
        for i in indices:
            if self.getLinkVerticesCount(i) == [0]:
                x_data[i] = []
                y_data[i] = []
                continue
            x_mat = []
            y_mat = []
            for j in range(1, self.getLinkVerticesCount(i) + 1):
                xy = self.api.ENgetvertex(i, j)
                x_mat.append(xy[0])
                y_mat.append(xy[1])
            x_data[i] = x_mat
            y_data[i] = y_mat
        return {'x': x_data, 'y': y_data}

    def getLinkVerticesCount(self, *argv):
        """ Retrieves the number of internal vertex points assigned to a link.

        Example 1:

        >>> d = epanet('Anytown.inp')
        >>> d.getLinkVerticesCount()          # Retrieves the vertices per link

        Example 2:

        >>> d = epanet('ky10.inp')
        >>> link_id = 'P-10'
        >>> d.getLinkVerticesCount(link_id)   # Retrieves the vertices of link 'P-10'

        Example 3:

        >>> link_index = 31
        >>> d.getLinkVerticesCount(link_index)    # Retrieves the vertices of link 31

        See also getLinkVertices, setLinkVertices.
        """
        if len(argv) > 0:
            if type(argv[0]) == str:
                indices = self.getLinkIndex(argv[0])
            else:
                indices = argv[0]
        else:
            indices = self.getLinkIndex()
        value = []
        if not isList(indices):
            return self.api.ENgetvertexcount(indices)
        else:
            for i in indices:
                value.append(self.api.ENgetvertexcount(i))
        return value

    def getLinkHeadloss(self, *argv):
        """ Retrieves the current computed head loss (read only).

        Using step-by-step hydraulic analysis,

        Example :

        >>> d.getLinkHeadloss()      # Retrieves the current computed head loss for all links
        >>> d.getLinkHeadloss(1)     # Retrieves the current computed head loss for the first link

        For more, you can check examples 3 & 4 of getLinkFlows function

        See also getLinkFlows, getLinkVelocity, getLinkStatus,
        getLinkPumpState, getLinkSettings, getLinkActualQuality.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_HEADLOSS, *argv)

    def getLinkStatus(self, *argv):
        """ Retrieves the current link status (see @ref EN_LinkStatusType) (0 = closed, 1 = open).

        Using step-by-step hydraulic analysis,

        Example:

        >>> d.getLinkStatus()        # Retrieves the current link status for all links
        >>> d.getLinkStatus(1)       # Retrieves the current link status for the first link

        For more, you can check examples 3 & 4 of getLinkFlows function

        See also getLinkFlows, getLinkVelocity, getLinkHeadloss,
        getLinkPumpState, getLinkSettings.
        """
        value = self.__getLinkInfo(self.ToolkitConstants.EN_STATUS, *argv)
        return self.__returnValue(value)

    def getLinkSettings(self, *argv):
        """ Retrieves the current computed value of all link roughness for pipes
        or actual speed for pumps or actual setting for valves.

        Using step-by-step hydraulic analysis,

        Example:

        >>> d.getLinkSettings()      # Retrieves the current values of settings for all links
        >>> d.getLinkSettings(1)     # Retrieves the current value of setting for the first link

        For more, you can check examples 3 & 4 of getLinkFlows function

        See also getLinkFlows, getLinkVelocity, getLinkHeadloss,
        getLinkStatus, getLinkPumpState, getLinkEnergy.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_SETTING, *argv)

    def getLinkEnergy(self, *argv):
        """ Retrieves the current computed pump energy usage (read only).

        Using step-by-step hydraulic analysis,

        Example:

        >>> d.getLinkEnergy()        # Retrieves the current computed pump energy usage for all links
        >>> d.getLinkEnergy(1)       # Retrieves the current computed pump energy usage for the first link

        For more, you can check examples 3 & 4 of getLinkFlows function

        See also getLinkFlows, getLinkVelocity, getLinkHeadloss,
        getLinkStatus, getLinkPumpState, getLinkPumpEfficiency.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_ENERGY, *argv)

    def getLinkActualQuality(self, *argv):
        """ Retrieves the current computed link quality (read only). (EPANET Version 2.2)

        Example:

        >>> d.getLinkActualQuality()        # Retrieves the current computed link quality for all links
        >>> d.getLinkActualQuality(1)       # Retrieves the current computed link quality for the first link

        .. note::
            check epyt/examples/EX14_hydraulic_and_quality_analysis.py

        See also getLinkFlows, getLinkStatus, getLinkPumpState, getLinkSettings, getLinkPumpEfficiency.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_LINKQUAL, *argv)

    def getLinkIndex(self, *argv):
        """ Retrieves the indices of all links, or the indices of an ID set of links.

        Example 1:

        >>> d.getLinkIndex()                # Retrieves the indices of all links

        Example 2:

        >>> linkID = d.getLinkNameID()
        >>> d.getLinkIndex(linkID)          # Retrieves the index of the 1st link given it's ID

        Example 3:

        >>> linkID = d.getLinkNameID([1,2,3])
        >>> d.getLinkIndex(linkID)          # Retrieves the indices of the first 3 links given their ID

        See also getLinkNameID, getLinkPipeIndex, getNodeIndex.
        """
        values = []
        if len(argv) > 0:
            index = argv[0]
            if type(index) is list:
                for i in index:
                    values.append(self.api.ENgetlinkindex(i))
            else:
                values = self.api.ENgetlinkindex(index)
        else:
            for i in range(self.getLinkCount()):
                values.append(i + 1)
        return values

    def getLinkNodesIndex(self, *argv):
        """ Retrieves the indexes of the from/to nodes of all links.

        Example:

        d.getLinkNodesIndex()
        d.getLinkNodesIndex(2)    # Link index

        See also getNodesConnectingLinksID.
        """
        indices = self.__getlinkIndices(*argv)
        value = []
        for i in indices:
            value.append(self.api.ENgetlinknodes(i))
        if len(argv) == 1 and not isList(argv[0]):
            return value[0]
        else:
            return value

    def getLinkPipeIndex(self):
        """ Retrieves the pipe indices.

        Example:

        >>> d.getLinkPipeIndex()

        See also getLinkIndex, getLinkPumpIndex.
        """
        tmpLinkTypes = self.getLinkType()
        value = []
        for i in range(len(tmpLinkTypes)):
            if tmpLinkTypes[i] == 'PIPE' or tmpLinkTypes[i] == 'CVPIPE':
                value.append(i + 1)
        return value

    def getLinkPipeNameID(self, *argv):
        """ Retrieves the pipe ID.

        Example:

        >>> d.getLinkPipeNameID()         # Retrieves the ID's of all pipes
        >>> d.getLinkPipeNameID(1)        # Retrieves the ID of the 1st pipe
        >>> d.getLinkPipeNameID([1,2,3])  # Retrieves the ID of the first 3 pipes

        See also getLinkNameID, getLinkPumpNameID, getNodeNameID.
        """
        pIndices = self.getLinkPipeIndex()
        if len(argv) == 0:
            return self.getLinkNameID(self.getLinkPipeIndex())
        elif isList(argv[0]):
            value = []
            for i in argv[0]:
                if i in pIndices:
                    value.append(self.getLinkNameID(i))
                else:
                    try:
                        value.append(self.getLinkNameID(pIndices[i - 1]))
                    except:
                        raise Exception('The input values contain non-pipe indices.')
            return value
        else:
            if argv[0] in pIndices:
                return self.getLinkNameID(argv[0])
            else:
                try:
                    return self.getLinkNameID(pIndices[argv[0] - 1])
                except:
                    raise Exception('The input value contains non-pipe index.')

    def getLinkPumpIndex(self, *argv):
        """ Retrieves the pump indices.

        Example 1:

        >>> d.getLinkPumpIndex()          # Retrieves the indices of all pumps

        Example 2:

        >>> d.getLinkPumpIndex(1)         # Retrieves the index of the 1st pump

        Example 3:

        >>> d = epanet('Richmond_standard.inp')
        >>> d.getLinkPumpIndex([1,2])     # Retrieves the indices of the first 2 pumps

        See also getLinkIndex, getLinkPipeIndex, getLinkValveIndex.
        """
        tmpLinkTypes = self.getLinkTypeIndex()
        value = np.array([i for i, x in enumerate(tmpLinkTypes) if x == self.ToolkitConstants.EN_PUMP]) + 1
        if value.size == 0:
            return value
        if argv:
            index = np.array(argv[0])
            try:
                return value[index - 1]
            except:
                raise Exception('Some PUMP indices do not exist.')
        else:
            return value

    def getLinkPumpNameID(self, *argv):
        """ Retrieves the pump ID.

        Example 1:

        >>> d.getLinkPumpNameID()          # Retrieves the ID's of all pumps

        Example 2:

        >>> d.getLinkPumpNameID(1)         # Retrieves the ID of the 1st pump

        Example 3:

        >>> d = epanet('Net3_trace.inp')
        >>> d.getLinkPumpNameID([1,2])     # Retrieves the ID of the first 2 pumps

        See also getLinkNameID, getLinkPipeNameID, getNodeNameID.
        """
        return self.getLinkNameID(self.getLinkPumpIndex(*argv))

    def getLinkValveIndex(self):
        """ Retrieves the valve indices.

        Example:

        >>> d = epanet('ky10.inp')
        >>> d.getLinkValveIndex()

        See also getLinkIndex, getLinkPipeIndex(), getLinkPumpIndex.
        """
        tmpLinkTypes = self.getLinkType()
        value = []
        for i in range(len(tmpLinkTypes)):
            if tmpLinkTypes[i].endswith('V'):
                value.append(i + 1)
        return np.array(value)

    def getLinkValveNameID(self, *argv):
        """ Retrieves the valve ID.

        Example:

        >>> d = epanet('BWSN_Network_1.inp')
        >>> d.getLinkValveNameID()          # Retrieves the ID's of all valves
        >>> d.getLinkValveNameID(1)         # Retrieves the ID of the 1st valve
        >>> d.getLinkValveNameID([1,2,3])   # Retrieves the ID of the first 3 valves

        See also getLinkNameID, getLinkPumpNameID, getNodeNameID.
        """
        vIndices = self.getLinkValveIndex()
        if len(argv) == 0:
            return self.getLinkNameID(self.getLinkValveIndex())
        elif isList(argv[0]):
            value = []
            for i in argv[0]:
                if i in vIndices:
                    value.append(self.getLinkNameID(i))
                else:
                    value.append(self.getLinkNameID(vIndices[i - 1]))
            return value
        else:
            if argv[0] in vIndices:
                return self.getLinkNameID(argv[0])
            else:
                return self.getLinkNameID(vIndices[argv[0] - 1])

    def getNodeActualDemandSensingNodes(self, *argv):
        """ Retrieves the computed demand values at some sensing nodes.

        Example: Retrieves the computed demand value of the first sensing node.

        >>> d.getNodeActualDemandSensingNodes(1)

        For more, you can type help (d.getNodePressure) and check examples 3 & 4.

        See also getNodeActualDemand, getNodeHydraulicHead, getNodePressure,
        getNodeActualQuality, getNodeMassFlowRate, getNodeActualQualitySensingNodes.
        """
        value = []
        if len(argv) > 0:
            indices = argv[0]
        else:
            indices = self.getNodeIndex()
        for i in indices:
            value.append(self.api.ENgetnodevalue(i, self.ToolkitConstants.EN_DEMAND))
        return np.array(value)

    def getNodeCount(self):
        """ Retrieves the number of nodes.

        Example:

        >>> d.getNodeCount()

        See also getNodeIndex, getLinkCount().
        """
        return self.api.ENgetcount(self.ToolkitConstants.EN_NODECOUNT)

    def getNodeActualDemand(self, *argv):
        """ Retrieves the computed value of all node actual demands.

        Example:

        >>> d.getNodeActualDemand()           # Retrieves the computed value of all node actual demands
        >>> d.getNodeActualDemand(1)          # Retrieves the computed value of the first node actual demand
        >>> d.getNodeActualDemand([1,2,3])    # Retrieves the computed value of the first 3 nodes actual demand

        See also getNodeActualDemandSensingNodes, getNode HydraulicHead, getNodePressure,
        getNodeActualQuality, getNodeMassFlowRate, getNodeActualQualitySensingNodes.
        """
        return self.__getNodeInfo(self.ToolkitConstants.EN_DEMAND, *argv)

    def getNodeActualQuality(self, *argv):
        """ Retrieves the computed values of the actual quality for all nodes.

        Example:

        >>> d.getNodeActualQuality()        # Retrieves the computed values of the actual quality for all nodes
        >>> d.getNodeActualQuality(1)       # Retrieves the computed value of the actual quality for the first node

        See also getNodeActualDemand, getNodeActualDemandSensingNodes, getNodePressure,
        getNodeHydraulicHead, getNodeMassFlowRate, getNodeActualQualitySensingNodes.
        """
        return self.__getNodeInfo(self.ToolkitConstants.EN_QUALITY, *argv)

    def getNodeBaseDemands(self, *argv):
        """ Retrieves the value of all node base demands.

        Example 1:

        >>> d.getNodeBaseDemands()
        >>> d.getNodeBaseDemands()[1]      #  Get categories 1

        Example 2:

        >>> d.getNodeBaseDemands(2)        # Get node base demand with categories for specific node index

        See also setNodeBaseDemands, getNodeDemandCategoriesNumber,
        getNodeDemandPatternIndex, getNodeDemandPatternNameID.
        """
        indices = self.__getNodeIndices(*argv)
        numdemands = self.getNodeDemandCategoriesNumber(indices)
        value = {}
        val = np.zeros((max(numdemands), len(indices)))
        j = 1
        for i in indices:
            v = 0
            for u in range(numdemands[j - 1]):
                val[v][j - 1] = self.api.ENgetbasedemand(i, u + 1)
                v += 1
            j += 1
        for i in range(max(numdemands)):
            value[i + 1] = np.array(val[i])
        return value

    def getNodeComment(self, *argv):
        """ Retrieves the comment string assigned to the node object.

        Example:

        >>> d.getNodeComment()              # Retrieves the comment string assigned to all node objects
        >>> d.getNodeComment(4)             # Retrieves the comment string assigned to the 4th node object
        >>> d.getNodeComment([1,2,3,4,5])   # Retrieves the comment string assigned to the 1st to 5th node object

        See also setNodeComment, getNodesInfo, getNodeNameID, getNodeType.
        """
        value = []
        indices = self.__getNodeIndices(*argv)
        for i in indices:
            value.append(self.api.ENgetcomment(self.ToolkitConstants.EN_NODE, i))
        return value

    def getNodeCoordinates(self, *argv):
        # GET VERTICES
        vertices = self.getLinkVertices()
        # SET X Y node coordinates
        if len(argv) > 0 and type(argv[0]) is not str:
            indices = self.__getNodeIndices(*argv)
        else:
            indices = self.__getNodeIndices()
        vx, vy = [], []
        for i in indices:
            vx.append(self.api.ENgetcoord(i)[0])
            vy.append(self.api.ENgetcoord(i)[1])
        if len(argv) == 0:
            vxx, vyy = {}, {}
            for i in indices:
                vxx[i] = vx[i - 1]
                vyy[i] = vy[i - 1]
            return {'x': vxx, 'y': vyy, 'x_vert': vertices['x'], 'y_vert': vertices['y']}
        else:
            xVal, yVal = {}, {}
            j = 1
            for i in indices:
                xVal[i] = vx[j - 1]
                yVal[i] = vy[j - 1]
                j += 1
            if argv[0] == 'x':
                return xVal
            elif argv[0] == 'y':
                return yVal
            else:
                return {'x': xVal, 'y': yVal}

    def getNodeDemandCategoriesNumber(self, *argv):
        """ Retrieves the value of all node base demands categorie number. (EPANET Version 2.1)

        Example 1:

       	>>> d.getNodeDemandCategoriesNumber()               # Retrieves the value of all node base demands categorie number

        Example 2:

       	>>> d.getNodeDemandCategoriesNumber(1)              # Retrieves the value of the first node base demand categorie number

        Example 3:

       	>>> d.getNodeDemandCategoriesNumber([1,2,3,4])      # Retrieves the value of the first 4 nodes base demand categorie number

        See also getNodeBaseDemands, getNodeDemandPatternIndex, getNodeDemandPatternNameID.
        """
        value = []
        if len(argv) > 0:
            index = argv[0]
            if type(index) is list:
                for i in index:
                    value.append(self.api.ENgetnumdemands(i))
            else:
                value = self.api.ENgetnumdemands(index)
        else:
            for i in range(self.getNodeCount()):
                value.append(self.api.ENgetnumdemands(i + 1))
        return value

    def getNodeDemandDeficit(self, *argv):
        """  Retrieves the amount that full demand is reduced under PDA. (EPANET Version 2.2)

        The example is based on d = epanet('Net1.inp')

        Example:

        >>> d.setDemandModel('PDA', 0, 0.1, 0.5)      # Sets a type of demand model and its parameters
        >>> d.getComputedHydraulicTimeSeries()        # Computes hydraulic simulation and retrieve all time-series
        >>> d.getNodeDemandDeficit()                  # Retrieves the amount that full demand is reduced under PDA

        See also setDemandModel, getComputedHydraulicTimeSeries,
        getNodeActualDemand, getNodeActualDemandSensingNodes.
        """
        return self.__getNodeInfo(self.ToolkitConstants.EN_DEMANDDEFICIT, *argv)

    def getNodeDemandPatternIndex(self):
        """ Retrieves the value of all node base demands pattern index. (EPANET Version 2.1)

        Example:

        >>> d.getNodeDemandPatternIndex()
        >>> d.getNodeDemandPatternIndex()[1]

        See also getNodeBaseDemands, getNodeDemandCategoriesNumber, getNodeDemandPatternNameID,
        setNodeDemandPatternIndex.
        """
        numdemands = self.getNodeDemandCategoriesNumber()
        value = {}
        val = np.zeros((max(numdemands), self.getNodeCount()), dtype=int)
        for i in self.getNodeIndex():
            v = 0
            for u in range(numdemands[i - 1]):
                val[v][i - 1] = self.api.ENgetdemandpattern(i, u + 1)
                v += 1
        for i in self.getNodeReservoirIndex():
            val[v][i - 1] = self.api.ENgetnodevalue(i, self.ToolkitConstants.EN_PATTERN)
        for i in range(max(numdemands)):
            value[i + 1] = list(val[i])
        return value

    def getNodeDemandPatternNameID(self):
        """ Retrieves the value of all node base demands pattern name ID. (EPANET Version 2.1)

        Example:

        >>> d.getNodeDemandPatternNameID()
        >>> d.getNodeDemandPatternNameID()[1]

        See also getNodeBaseDemands, getNodeDemandCategoriesNumber,
        getNodeDemandPatternIndex.
        """
        v = self.getNodeDemandPatternIndex()
        m = self.getPatternNameID()
        if m:
            numdemands = self.getNodeDemandCategoriesNumber()
            indices = self.__getNodeIndices()
            value = {}
            val = [['' for i in range(self.getNodeCount())] for j in range(max(numdemands))]
            for i in indices:
                for u in range(numdemands[i - 1]):
                    if v[u + 1][i - 1] != np.array(0):
                        val[u][i - 1] = m[v[u + 1][i - 1] - 1]
                    else:
                        val[u][i - 1] = ''
                if numdemands[i - 1] == 0:
                    val[0][i - 1] = ''
            for i in range(len(val)):
                value[i + 1] = list(val[i])
            return value
        else:
            return None

    def getNodeElevations(self, *argv):
        """ Retrieves the value of all node elevations.
        Example:

        >>> d.getNodeElevations()             # Retrieves the value of all node elevations
        >>> d.getNodeElevations(1)            # Retrieves the value of the first node elevation
        >>> d.getNodeElevations([4, 5, 6])    # Retrieves the value of the 5th to 7th node elevations

        See also setNodeElevations, getNodesInfo, getNodeNameID,
        getNodeType, getNodeEmitterCoeff, getNodeInitialQuality.
        """
        return self.__getNodeInfo(self.ToolkitConstants.EN_ELEVATION, *argv)

    def getNodeEmitterCoeff(self, *argv):
        """ Retrieves the value of all node emmitter coefficients.

        Example:

        >>> d.getNodeEmitterCoeff()         # Retrieves the value of all node emmitter coefficients
        >>> d.getNodeEmitterCoeff(1)        # Retrieves the value of the first node emmitter coefficient

        See also setNodeEmitterCoeff, getNodesInfo, getNodeElevations.
        """
        return self.__getNodeInfo(self.ToolkitConstants.EN_EMITTER, *argv)

    def getNodeHydraulicHead(self, *argv):
        """ Retrieves the computed values of all node hydraulic heads.

        Example 1:

        >>> d.getNodeHydraulicHead()        # Retrieves the computed value of all node hydraulic heads

        Example 2:

        >>> d.getNodeHydraulicHead(1)       # Retrieves the computed value of the first node hydraulic head

        For more, you can type `help getNodePressure` and check examples 3 & 4.

        See also getNodeActualDemand, getNodeActualDemandSensingNodes, getNodePressure,
        getNodeActualQuality, getNodeMassFlowRate, getNodeActualQualitySensingNodes.
        """
        return self.__getNodeInfo(self.ToolkitConstants.EN_HEAD, *argv)

    def getNodeIndex(self, *argv):
        """ Retrieves the indices of all nodes or some nodes with a specified ID.

        Example 1:

        >>> d.getNodeIndex()              # Retrieves the indices of all nodes

        Example 2:

        >>> nameID = d.getNodeNameID(1)
        >>> d.getNodeIndex(nameID)        # Retrieves the node index given the ID label of the 1st node

        See also getNodeNameID, getNodeReservoirIndex, getNodeJunctionIndex,
        getNodeType, getNodeTypeIndex, getNodesInfo.
        """
        values = []
        if len(argv) > 0:
            index = argv[0]
            if type(index) is list:
                for i in index:
                    values.append(self.api.ENgetnodeindex(i))
            else:
                values = self.api.ENgetnodeindex(index)
        else:
            for i in range(self.getNodeCount()):
                values.append(i + 1)
        return values

    def getNodeInitialQuality(self, *argv):
        """ Retrieves the value of all node initial quality.

        Example 1:

        >>> d.getNodeInitialQuality()          # Retrieves the value of all node initial quality

        Example 2:

        >>> d.getNodeInitialQuality(1)         # Retrieves the value of the first node initial quality

        See also setNodeInitialQuality, getNodesInfo, getNodeSourceQuality.
        """
        return self.__getNodeInfo(self.ToolkitConstants.EN_INITQUAL, *argv)

    def getNodeJunctionCount(self):
        """ Retrieves the number of junction nodes.

        Example:

        >>> d.getNodeJunctionCount()

        See also getNodeTankCount, getNodeCount.
        """
        return self.getNodeTypeIndex().count(self.ToolkitConstants.EN_JUNCTION)

    def getNodeJunctionDemandIndex(self, *argv):
        """ Retrieves the demand index of the junctions. (EPANET Version 2.2)

        Example 1:

        >>> d.getNodeJunctionDemandIndex()         # Retrieves the demand index of all junctions

        Example 2:

        >>> d.getNodeJunctionDemandIndex(1,'')     # Retrieves the demand index of the 1st junction given it's name (i.e. '')

        Example 3:

        >>> d.getNodeJunctionDemandIndex([1,2,3])  # Retrieves the demand index of the first 3 junctions

        Example 4: Adds two new demands and retrieves the two new demand indices.

        >>> d.addNodeJunctionDemand([1, 2], [100, 110], ['1', '1'], ['new demand1', 'new demand2'])
        >>> d.getNodeJunctionDemandIndex([1,2],['new demand1','new demand2'])

        See also getNodeJunctionDemandName, getNodeJunctionIndex, getNodeJunctionNameID,
        addNodeJunctionDemand, deleteNodeJunctionDemand, getNodeJunctionCount.
        """
        if len(argv) == 2:
            nodeIndex = argv[0]
            demandName = argv[1]
            if not isList(nodeIndex) and not isList(demandName):
                value = self.api.ENgetdemandindex(nodeIndex, demandName)
            elif isList(nodeIndex) and isList(demandName):
                value = []
                for i in range(len(nodeIndex)):
                    value.append(self.api.ENgetdemandindex(nodeIndex[i], demandName[i]))
        elif len(argv) == 1:
            nodeIndex = argv[0]
            demandName = self.getNodeJunctionDemandName()
            if not isList(nodeIndex):
                value = []
                for i in range(len(demandName)):
                    demandNameIn = demandName[i + 1]
                    value.append(self.api.ENgetdemandindex(nodeIndex, demandNameIn[nodeIndex-1]))
            else:
                for i in range(len(demandName)):
                    demandNameIn = demandName[i + 1]
                    value = [[0 for i in range(len(nodeIndex))] for j in range(len(demandName))]
                    for j in range(len(nodeIndex)):
                        value[i][j] = self.api.ENgetdemandindex(nodeIndex[j], demandNameIn[nodeIndex[j]])
        elif len(argv) == 0:
            demandName = self.getNodeJunctionDemandName()
            indices = self.__getNodeJunctionIndices(*argv)
            value = [[0 for i in range(len(indices))] for j in range(len(demandName))]
            for i in range(len(demandName)):
                for j in range(len(demandName[i + 1])):
                    demandNameIn = demandName[i + 1][j]
                    value[i][j] = self.api.ENgetdemandindex(j + 1, demandNameIn)
        else:
            self.api.errcode = 250
            self.api.ENgeterror()
        return value

    def getNodeJunctionDemandName(self, *argv):
        """ Gets the name of a node's demand category.

        Example:

        >>> model = d.getNodeJunctionDemandName()

        See also setNodeJunctionDemandName, getNodeBaseDemands,
        getNodeDemandCategoriesNumber, getNodeDemandPatternNameID.
        """
        indices = self.__getNodeJunctionIndices(*argv)
        numdemands = self.getNodeDemandCategoriesNumber(indices)
        value = {}
        if not isList(indices): indices = [indices]
        if not isList(numdemands) : numdemands = [numdemands]
        val = [['' for i in range(len(indices))] for j in range(max(numdemands))]
        for i in indices:
            for u in range(numdemands[indices.index(i)]):
                val[u][indices.index(i)] = self.api.ENgetdemandname(i, u + 1)
        for i in range(len(val)):
            value[i + 1] = val[i]
        return value

    def getNodeJunctionIndex(self, *argv):
        """Retrieves the indices of junctions.

        Example:

        >>> d.getNodeJunctionIndex()          # Retrieves the indices of all junctions
        >>> d.getNodeJunctionIndex([1,2])     # Retrieves the indices of the first 2 junctions

        See also getNodeNameID, getNodeIndex, getNodeReservoirIndex,
        getNodeType, getNodeTypeIndex, getNodesInfo.
        """
        tmpNodeTypes = self.getNodeTypeIndex()
        value = [i for i, x in enumerate(tmpNodeTypes) if x == self.ToolkitConstants.EN_JUNCTION]
        if (len(value) > 0) and (len(argv) > 0):
            index = argv[0]
            try:
                if type(index) is list:
                    jIndices = []
                    for i in index:
                        jIndices.append(value[i - 1] + 1)
                    return jIndices
                else:
                    return value[index - 1] + 1
            except:
                raise Exception('Some JUNCTION indices do not exist.')
        else:
            jIndices = value
            return [i + 1 for i in jIndices]

    def getNodeJunctionNameID(self, *argv):
        """ Retrieves the junction ID label.

        Example:

        >>> d.getNodeJunctionNameID()       # Retrieves the ID of all junctions
        >>> d.getNodeJunctionNameID(1)      # Retrieves the ID of the 1st junction
        >>> d.getNodeJunctionNameID([1,2])  # Retrieves the ID of the first 2 junction

        See also getNodeNameID, getNodeReservoirNameID, getNodeIndex,
        getNodeJunctionIndex, getNodeType, getNodesInfo.
        """
        if len(argv) == 0:
            return self.getNodeNameID(self.getNodeJunctionIndex())
        else:
            indices = self.__getNodeJunctionIndices(*argv)
            if isList(indices):
                return [self.getNodeNameID(i) for i in indices]
            else:
                return self.getNodeNameID(indices)

    def getNodeMassFlowRate(self, *argv):
        """ Retrieves the computed mass flow rates per minute of chemical sources for all nodes.

        Example:

        >>> d.getNodeMassFlowRate()     # Retrieves the computed mass flow rates per minute of chemical sources for all nodes
        >>> d.getNodeMassFlowRate(1)    # Retrieves the computed mass flow rates per minute of chemical sources for the first node

        For more, you can type `help getNodePressure` and check examples 3 & 4.

        See also getNodeActualDemand, getNodeActualDemandSensingNodes, getNodePressure,
        getNodeHydraulicHead, getNodeActualQuality, getNodeActualQualitySensingNodes.
        """
        indices = self.__getNodeIndices(*argv)
        if not isList(indices):
            indices = [indices]
        value = []
        for i in indices:
            temp_val = self.api.ENgetnodevalue(i, self.ToolkitConstants.EN_SOURCEMASS)
            if temp_val!=240:
                value.append(temp_val)
            else:
                value.append(None)
        return np.array(value)

    def getNodePatternIndex(self, *argv):
        """  Retrieves the value of all node demand pattern indices.

        Example 1:

        >>> d.getNodePatternIndex()        #  Retrieves the value of all node demand pattern indices

        Example 2:

        >>> d.getNodePatternIndex(1)       #  Retrieves the value of the first node demand pattern index

        See also getNodeBaseDemands, getNodeDemandCategoriesNumber,
        getNodeDemandPatternIndex, getNodeDemandPatternNameID.
        """
        value = self.__getNodeInfo(self.ToolkitConstants.EN_PATTERN, *argv)
        return self.__returnValue(value)

    def getNodePressure(self, *argv):
        """ Retrieves the computed values of all node pressures.

        Example 1:

        >>> d.getNodePressure()          # Retrieves the computed values of all node pressures

        Example 2:

        >>> d.getNodePressure(1)         # Retrieves the computed value of the first node pressure

        Example 3: Hydraulic analysis step-by-step.

        >>> d.openHydraulicAnalysis()
        >>> d.initializeHydraulicAnalysis()
        >>> tstep,P , T_H, D, H, F, S, = 1, [], [], [], [] ,[], []
        >>> while (tstep>0):
        ...     t = d.runHydraulicAnalysis()
        ...     P.append(d.getNodePressure())
        ...     D.append(d.getNodeActualDemand())
        ...     H.append(d.getNodeHydraulicHead())
        ...     S.append(d.getLinkStatus())
        ...     F.append(d.getLinkFlows())
        ...     T_H.append(t)
        ...     tstep=d.nextHydraulicAnalysisStep()
        >>> d.closeHydraulicAnalysis()

        Example 4: Hydraulic and Quality analysis step-by-step.

        >>> d.openHydraulicAnalysis()
        >>> d.openQualityAnalysis()
        >>> d.initializeHydraulicAnalysis(0)
        >>> d.initializeQualityAnalysis(d.ToolkitConstants.EN_NOSAVE)
        >>> tstep, P, T, F, QN, QL = 1, [], [], [], [], []
        >>> while (tstep>0):
        ...     t  = d.runHydraulicAnalysis()
        ...     qt = d.runQualityAnalysis()
        ...     P.append(d.getNodePressure())
        ...     F.append(d.getLinkFlows())
        ...     QN.append(d.getNodeActualQuality())
        ...     QL.append(d.getLinkActualQuality())
        ...     T.append(t)
        ...     tstep = d.nextHydraulicAnalysisStep()
        ...     qtstep = d.nextQualityAnalysisStep()
        >>> d.closeQualityAnalysis()
        >>> d.closeHydraulicAnalysis()

        See also getNodeActualDemand, getNodeActualDemandSensingNodes, getNodeHydraulicHead
        getNodeActualQuality, getNodeMassFlowRate, getNodeActualQualitySensingNodes.
        """
        return self.__getNodeInfo(self.ToolkitConstants.EN_PRESSURE, *argv)

    def getNodeReservoirIndex(self, *argv):
        """ Retrieves the indices of reservoirs.

        Example 1:

        >>> d.getNodeReservoirIndex()           # Retrieves the indices of all reservoirs.

        Example 2:

        >>> d.getNodeReservoirIndex([1,2,3])    # Retrieves the indices of the first 3 reservoirs, if they exist.

        See also getNodeNameID, getNodeIndex, getNodeJunctionIndex,
        getNodeType, getNodeTypeIndex, getNodesInfo.
        """
        tmpNodeTypes = self.getNodeTypeIndex()
        value = [i for i, x in enumerate(tmpNodeTypes) if x == self.ToolkitConstants.EN_RESERVOIR]
        if (len(value) > 0) and (len(argv) > 0):
            index = argv[0]
            try:
                if type(index) is list:
                    rIndices = []
                    for i in index:
                        rIndices.append(value[i - 1] + 1)
                    return rIndices
                else:
                    return value[index - 1] + 1
            except:
                raise Exception('Some RESERVOIR indices do not exist.')
        else:
            rIndices = value
            return [i + 1 for i in rIndices]

    def getNodeReservoirNameID(self, *argv):
        """ Retrieves the reservoir ID label.

        Example :

        >>> d.getNodeReservoirNameID()       # Retrieves the ID of all reservoirs
        >>> d.getNodeReservoirNameID(1)      # Retrieves the ID of the 1st reservoir
        >>> d.getNodeReservoirNameID([1,2])  # Retrieves the ID of the first 2 reservoirs (if they exist!)

        See also getNodeNameID, getNodeJunctionNameID, getNodeIndex,
        getNodeReservoirIndex, getNodeType, getNodesInfo.
        """
        if len(argv) == 0:
            return self.getNodeNameID(self.getNodeReservoirIndex())
        else:
            indices = self.getNodeReservoirIndex(*argv)
            if isList(indices):
                return [self.getNodeNameID(i) for i in indices]
            else:
                return self.getNodeNameID(indices)

    def getNodesConnectingLinksID(self, *argv):
        """ Retrieves the id of the from/to nodes of all links.

        Example:

        >>> d.getNodesConnectingLinksID()            # Retrieves the id of the from/to nodes of all links
        >>> linkIndex = 1
        >>> d.getNodesConnectingLinksID(1)           # Retrieves the id of the from/to nodes of the 1st link

        See also getLinkNodesIndex.
        """
        indices = self.__getlinkIndices(*argv)
        values = self.getLinkNodesIndex(indices)
        connVals = []
        for i in range(len(values)):
            connVals.append(self.getNodeNameID((values[i])))
        return connVals

    def getNodesConnectingLinksIndex(self):
        """ Retrieves the indexes of the from/to nodes of all links.
        Duplicate function with getLinkNodesIndex for new version.

        Example:

        >>> d.getNodesConnectingLinksIndex()

        See also getLinkNodesIndex, getNodesConnectingLinksID.
        """
        return self.getLinkNodesIndex()

    def getNodesInfo(self):
        """ Retrieves nodes info (elevations, demand patterns, emmitter coeff, initial quality,
        source quality, source pattern index, source type index, node type index).

        Example:

        >>> d.getNodesInfo()

        See also getNodeElevations, getNodeDemandPatternIndex, getNodeEmitterCoeff,
        getNodeInitialQuality, NodeTypeIndex.
        """
        value = val()
        value.NodeElevations = self.getNodeElevations()
        value.NodePatternIndex = self.getNodePatternIndex()
        value.NodeEmitterCoeff = self.getNodeEmitterCoeff()
        value.NodeInitialQuality = self.getNodeInitialQuality()
        value.NodeSourceQuality = self.getNodeSourceQuality()
        value.NodeSourcePatternIndex = self.getNodeSourcePatternIndex()
        value.NodeSourceTypeIndex = self.getNodeSourceTypeIndex()
        value.NodeTypeIndex = self.getNodeTypeIndex()
        return value

    def getNodeNameID(self, *argv):
        """ Retrieves the ID label of all nodes or some nodes with a specified index.

        Example 1:

        >>> d.getNodeNameID()                   # Retrieves the ID label of all nodes

        Example 2:

        >>> d.getNodeNameID(1)                  # Retrieves the ID label of the first node

        Example 3:

        >>> junctionIndex = d.getNodeJunctionIndex()
        >>> d.getNodeNameID(junctionIndex)       # Retrieves the ID labels of all junctions give their indices

        See also getNodeReservoirNameID, getNodeJunctionNameID,
        getNodeIndex, getNodeType, getNodesInfo.
        """
        values = []
        if len(argv) > 0:
            index = argv[0]
            if type(index) is list:
                for i in index:
                    values.append(self.api.ENgetnodeid(i))
            else:
                values = self.api.ENgetnodeid(index)
        else:
            for i in range(self.getNodeCount()):
                values.append(self.api.ENgetnodeid(i + 1))
        return values

    def getNodeReservoirCount(self):
        """ Retrieves the number of Reservoirs.

        Example:

        >>> d.getNodeReservoirCount()

        See also getNodeTankCount, getNodeCount.
        """
        return self.getNodeTypeIndex().count(self.ToolkitConstants.EN_RESERVOIR)

    def getNodeResultIndex(self, node_index):
        """ Retrieves the order in which a node's results
        were saved to an output file. (EPANET Version 2.2)

        Example:

        >>> node_index = 3
        >>> result_index = d.getNodeResultIndex(node_index)

        See also getComputedHydraulicTimeSeries, deleteNode, getLinkResultIndex
        """
        return self.api.ENgetresultindex(self.ToolkitConstants.EN_NODE, node_index)

    def getNodeSourcePatternIndex(self, *argv):
        """ Retrieves the value of all node source pattern index.

        Example 1:

        d.getNodeSourcePatternIndex()       #  Retrieves the value of all node source pattern index
        d.getNodeSourcePatternIndex(1)      #  Retrieves the value of the first node source pattern index

        See also setNodeSourcePatternIndex, getNodeSourceQuality,
        getNodeSourceTypeIndex, getNodeSourceType.
        """
        indices = self.__getNodeIndices(*argv)
        value = []
        for i in indices:
            e = self.api.ENgetnodevalue(i, self.ToolkitConstants.EN_SOURCEPAT)
            if e != 240:
                value.append(e)
            else:
                value.append(0)
        if len(argv) > 0 and not isList(argv[0]):
            return value[0]
        return self.to_array(value)

    def getNodeSourceQuality(self, *argv):
        """ Retrieves the value of all node source quality.

        Example 1:

        >>> d.getNodeSourceQuality()         # Retrieves the value of all node source quality
        >>> d.getNodeSourceQuality(1)        # Retrieves the value of the first node source quality

        See also setNodeSourceQuality, getNodeInitialQuality, getNodeSourcePatternIndex,
        getNodeSourceTypeIndex, getNodeSourceType.
        """
        indices = self.__getNodeIndices(*argv)
        value = []
        j = 1
        for i in indices:
            try:
                e = self.api.ENgetnodevalue(i, self.ToolkitConstants.EN_SOURCEQUAL)
                if e != 240:
                    value.append(e)
                else:
                    value.append(0)
            except Exception as Errcode:
                if Errcode.args[0][13:16] == '203':
                    return self.getError(Errcode)
            j = j + 1
        return np.array(value)

    def getNodeSourceType(self, *argv):
        """ Retrieves the value of all node source type.

        Example:

        >>> d.getNodeSourceType()        # Retrieves the value of all node source type
        >>> d.getNodeSourceType(1)       # Retrieves the value of the first node source type

        See also setNodeSourceType, getNodeSourceQuality,
        getNodeSourcePatternIndex, getNodeSourceTypeIndex.
        """
        indices = self.__getNodeIndices(*argv)
        value = []
        j = 1
        for i in indices:
            try:
                e = int(self.api.ENgetnodevalue(i, self.ToolkitConstants.EN_SOURCETYPE))
                if e != 240:
                    value.append(self.TYPESOURCE[e])
                else:
                    value.append(0)
            except Exception as Errcode:
                if Errcode.args[0][13:16] == '203':
                    return self.getError(Errcode)
            j = j + 1
        return value

    def getNodeSourceTypeIndex(self, *argv):
        """ Retrieves the value of all node source type index.

        Example:

        >>> d.getNodeSourceTypeIndex()        # Retrieves the value of all node source type index
        >>> d.getNodeSourceTypeIndex(1)       # Retrieves the value of the first node source type index

        See also getNodeSourceQuality, getNodeSourcePatternIndex, getNodeSourceType.
        """
        indices = self.__getNodeIndices(*argv)
        value = []
        j = 1
        for i in indices:
            try:
                e = self.api.ENgetnodevalue(i, self.ToolkitConstants.EN_SOURCETYPE)
                if e != 240:
                    value.append(e)
                else:
                    value.append(0)
            except Exception as Errcode:
                if Errcode.args[0][13:16] == '203':
                    return self.getError(Errcode)
            j = j + 1
        if len(argv) == 0:
            return np.array(value)
        else:
            return value[0]

    def getNodeTankBulkReactionCoeff(self, *argv):
        """ Retrieves the tank bulk rate coefficient.

        Example 1:

        >>> d.getNodeTankBulkReactionCoeff()                 # Retrieves the bulk rate coefficient of all tanks

        Example 2:

        >>> d.getNodeTankBulkReactionCoeff(1)                # Retrieves the bulk rate coefficient of the 1st tank

        Example 3:

        >>> d.getNodeTankBulkReactionCoeff([1,2])            # Retrieves the bulk rate coefficient of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankBulkReactionCoeff(tankIndex)        # Retrieves the bulk rate coefficient of the tanks given their indices

        See also setNodeTankBulkReactionCoeff, getNodeTankData.
        """
        return self.__getTankNodeInfo(self.ToolkitConstants.EN_TANK_KBULK, *argv)
    
    def getNodeTankCanOverFlow(self, *argv):
        """ Retrieves the tank can overflow (= 1) or not (= 0). (EPANET Version 2.2)

        Example 1:

        >>> d.getNodeTankCanOverFlow()             # Retrieves the can overflow of all tanks

        Example 2:

        >>> d.getNodeTankCanOverFlow(1)            # Retrieves the can overflow of the 1st tank

        Example 3:

        >>> d = epanet('BWSN_Network_1.inp')
        >>> d.getNodeTankCanOverFlow([1,2])        # Retrieves the can overflow of the first 2 tanks

        Example 4:

        >>> d = epanet('BWSN_Network_1.inp')
        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankCanOverFlow(tankIndex)    # Retrieves the can overflow of the tanks given their indices

        See also setNodeTankCanOverFlow, getNodeTankData.
        """
        if len(argv) == 1:
            indices = argv[0] if argv[0] == self.getNodeTankIndex() else self.getNodeTankIndex(*argv)
        else:
            indices = self.getNodeTankIndex()
        return self.__getNodeInfo(self.ToolkitConstants.EN_CANOVERFLOW, indices)

    def getNodeTankCount(self):
        """ Retrieves the number of Tanks.

        Example:

        >>> d.getNodeTankCount()

        See also getNodeReservoirCount, getNodeCount.
        """
        return self.getNodeTypeIndex().count(self.ToolkitConstants.EN_TANK)

    def getNodeTankData(self, *argv):
        """ Retrieves a group of properties for a tank. (EPANET Version 2.2)

        Tank data that is retrieved:

        1) Tank index
        2) Elevation
        3) Initial Level
        4) Minimum Water Level
        5) Maximum Water Level
        6) Diameter
        7) Minimum Water Volume
        8) Volume Curve Index

        Example 1:

        >>> tankData = d.getNodeTankData().to_dict()          # Retrieves all the data of all tanks

        Example 2:

        >>> tankIndex = d.getNodeTankIndex()
        >>> tankData = d.getNodeTankData(tankIndex)        # Retrieves all the data given the index/indices of tanks.

        Example 3:

        >>> d.getNodeTankData().Elevation                  # Retrieves the elevations of all tanks.

        See also setNodeTankData, getNodeElevations, getNodeTankInitialLevel,
        getNodeTankMinimumWaterLevel, getNodeTankDiameter.
        """
        tankData = val()
        tankIndices = self.getNodeTankIndex()
        if len(argv) == 1:
            if argv[0] in tankIndices:
                tankIndices = argv[0]
            else: 
                tankIndices = self.getNodeTankIndex(argv[0])
                
        tankData.Index = tankIndices
        tankData.Elevation = self.getNodeElevations(tankIndices)
        tankData.Initial_Level = self.getNodeTankInitialLevel(tankIndices)
        tankData.Minimum_Water_Level = self.getNodeTankMinimumWaterLevel(tankIndices)
        tankData.Maximum_Water_Level = self.getNodeTankMaximumWaterLevel(tankIndices)
        tankData.Diameter = self.getNodeTankDiameter(tankIndices)
        tankData.Minimum_Water_Volume = self.getNodeTankMinimumWaterVolume(tankIndices)
        tankData.Maximum_Water_Volume = self.getNodeTankMaximumWaterVolume(tankIndices)
        tankData.Volume_Curve_Index = self.getNodeTankVolumeCurveIndex(tankIndices)
        return tankData

    def getNodeTankDiameter(self, *argv):
        """ Retrieves the tank diameters.

        Example 1:

        >>> d.getNodeTankDiameter()                # Retrieves the diameters of all tanks

        Example 2:

        >>> d.getNodeTankDiameter(1)               # Retrieves the diameter of the 1st tank

        Example 3:

        >>> d.getNodeTankDiameter([1,2])           # Retrieves the diameters of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankDiameter(tankIndex)       # Retrieves the diameters of the tanks given their indices

        See also setNodeTankDiameter, getNodeTankBulkReactionCoeff, getNodeTankInitialLevel,
        getNodeTankMixingModelType, getNodeTankVolume, getNodeTankNameID.
        """
        return self.__getTankNodeInfo(self.ToolkitConstants.EN_TANKDIAM, *argv)

    def getNodeTankIndex(self, *argv):
        """ Retrieves the tank indices.

        Example 1:

        d.getNodeTankIndex()       # Retrieves the tank indices.
        d.getNodeTankIndex(1)      # Retrieves the first tank index.

        See also getNodeTankCount, getNodeTankNameID.
        """
        tmpNodeTypes = self.getNodeTypeIndex()
        value = [i for i, x in enumerate(tmpNodeTypes) if x == self.ToolkitConstants.EN_TANK]
        if (len(value) > 0) and (len(argv) > 0):
            index = argv[0]
            try:
                if type(index) is list:
                    tIndices = []
                    for i in index:
                        tIndices.append(value[i - 1] + 1)
                    return tIndices
                else:
                    return value[index - 1] + 1
            except:
                raise Exception('Some TANK indices do not exist.')
        else:
            return [i + 1 for i in value]

    def getNodeTankInitialLevel(self, *argv):
        """ Retrieves the value of all tank initial water levels.

        Example:

        >>> d = epanet("ky10.inp")
        >>> d.getNodeTankInitialLevel()         # Retrieves the value of all tank initial water levels
        >>> d.getNodeTankInitialLevel(11)       # Retrieves the value of the eleventh node(tank) water level

        See also setNodeTankInitialLevel, getNodeTankInitialWaterVolume, getNodeTankVolume,
        getNodeTankMaximumWaterLevel, getNodeTankMinimumWaterLevel.
        """
        return self.__getTankNodeInfo(self.ToolkitConstants.EN_TANKLEVEL, *argv)

    def getNodeTankInitialWaterVolume(self, *argv):
        """ Retrieves the tank initial water volume.

        Example 1:

        >>> d.getNodeTankInitialWaterVolume()                 #  Retrieves the initial water volume of all tanks

        Example 2:

        >>> d.getNodeTankInitialWaterVolume(1)                #  Retrieves the initial water volume of the 1st tank

        Example 3:

        >>> d.getNodeTankInitialWaterVolume([1,2])            #  Retrieves the initial water volume of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankInitialWaterVolume(tankIndex)        # Retrieves the initial water volume of the tanks given their indices

        See also getNodeTankInitialLevel,  getNodeTankVolume,
        getNodeTankMaximumWaterVolume, getNodeTankMinimumWaterVolume.
        """
        return self.__getTankNodeInfo(self.ToolkitConstants.EN_INITVOLUME, *argv)

    def getNodeTankMaximumWaterLevel(self, *argv):
        """ Retrieves the tank maximum water level.

        Example 1:

        >>> d.getNodeTankMaximumWaterLevel()                # Retrieves the maximum water level of all tanks

        Example 2:

        >>> d.getNodeTankMaximumWaterLevel(1)               # Retrieves the maximum water level of the 1st tank

        Example 3:

        >>> d.getNodeTankMaximumWaterLevel([1,2])           # Retrieves the maximum water level of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankMaximumWaterLevel(tankIndex)       # Retrieves the maximum water level of the tanks given their indices

        See also setNodeTankMaximumWaterLevel, getNodeTankMinimumWaterLevel, getNodeTankInitialLevel,
        getNodeTankMaximumWaterVolume, getNodeTankMinimumWaterVolume, getNodeTankVolume.
        """
        return self.__getTankNodeInfo(self.ToolkitConstants.EN_MAXLEVEL, *argv)

    def getNodeTankMaximumWaterVolume(self, *argv):
        """ Retrieves the tank maximum water volume. (EPANET Version 2.1)

        Example 1:

        >>> d.getNodeTankMaximumWaterVolume()              # Retrieves the maximum water volume of all tanks

        Example 2:

        >>> d.getNodeTankMaximumWaterVolume(1)             # Retrieves the maximum water volume of the 1st tank

        Example 3:

        >>> d.getNodeTankMaximumWaterVolume([1,2])         # Retrieves the maximum water volume of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankMaximumWaterVolume(tankIndex)     # Retrieves the maximum water volume of the tanks given their indices

        See also getNodeTankMinimumWaterVolume, getNodeTankData.
        """
        return self.__getTankNodeInfo(self.ToolkitConstants.EN_MAXVOLUME, *argv)

    def getNodeTankMinimumWaterLevel(self, *argv):
        """ Retrieves the tank minimum water level.

        Example 1:

        >>> d.getNodeTankMinimumWaterLevel()                # Retrieves the minimum water level of all tanks

        Example 2:

        >>> d.getNodeTankMinimumWaterLevel(1)               # Retrieves the minimum water level of the 1st tank

        Example 3:

        >>> d.getNodeTankMinimumWaterLevel([1,2])           # Retrieves the minimum water level of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankMinimumWaterLevel(tankIndex)       # Retrieves the minimum water level of the tanks given their indices

        See also setNodeTankMinimumWaterLevel, getNodeTankMaximumWaterLevel, getNodeTankInitialLevel,
        getNodeTankMaximumWaterVolume, getNodeTankMinimumWaterVolume, getNodeTankVolume.
        """
        return self.__getTankNodeInfo(self.ToolkitConstants.EN_MINLEVEL, *argv)

    def getNodeTankMinimumWaterVolume(self, *argv):
        """ Retrieves the tank minimum water volume.

        Example 1:

        >>> d.getNodeTankMinimumWaterVolume()                # Retrieves the minimum water volume of all tanks

        Example 2:

        >>> d.getNodeTankMinimumWaterVolume(1)               # Retrieves the minimum water volume of the 1st tank

        Example 3:

        >>> d.getNodeTankMinimumWaterVolume([1,2])           # Retrieves the minimum water volume of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankMinimumWaterVolume(tankIndex)       # Retrieves the minimum water volume of the tanks given their indices

        See also setNodeTankMinimumWaterVolume, getNodeTankMaximumWaterVolume, getNodeTankInitialWaterVolume,
        getNodeTankInitialLevel,  getNodeTankVolume, getNodeTankMixZoneVolume.
        """
        return self.__getTankNodeInfo(self.ToolkitConstants.EN_MINVOLUME, *argv)

    def getNodeTankMixingFraction(self, *argv):
        """ Retrieves the tank Fraction of total volume occupied by the inlet/outlet zone in a 2-compartment tank.

        Example 1:

        >>> d.getNodeTankMixingFraction()                # Retrieves the mixing fraction of all tanks

        Example 2:

        >>> d.getNodeTankMixingFraction(1)                # Retrieves the mixing fraction of the 1st tank

        Example 3:

        >>> d.getNodeTankMixingFraction([1,2])            # Retrieves the mixing fraction of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankMixingFraction(tankIndex)        # Retrieves the mixing fraction of the tanks given their indices

        See also setNodeTankMixingFraction, getNodeTankData.
        """
        return self.__getTankNodeInfo(self.ToolkitConstants.EN_MIXFRACTION, *argv)

    def getNodeTankMixingModelCode(self, *argv):
        """ Retrieves the tank mixing model code.

        Code meaning:
          0 = Complete mix model (MIX1)
          1 = 2-compartment model (MIX2)
          2 = First in, first out model (FIFO)
          3 = Last in, first out model (LIFO)

        Example 1:

        >>> d.getNodeTankMixingModelCode()                # Retrieves the mixing model code of all tanks

        Example 2:

        >>> d.getNodeTankMixingModelCode(1)               # Retrieves the mixing model code of the 1st tank

        Example 3:

        >>> d.getNodeTankMixingModelCode([1,2])           # Retrieves the mixing model code of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankMixingModelCode(tankIndex)       # Retrieves the mixing model code of the tanks given their indices

        See also setNodeTankMixingModelType, getNodeTankMixingModelType, getNodeTankMixZoneVolume.
        """
        return self.__getNodeTankMixiningModel(*argv)[0]

    def getNodeTankMixingModelType(self, *argv):
        """ Retrieves the tank mixing model type.

        Types of models that describe water quality mixing in storage tanks:
          MIX1 = Complete mix model
          MIX2 = 2-compartment model
          FIFO = First in, first out model
          LIFO = Last in, first out model

        Example 1:

        >>> d.getNodeTankMixingModelType()               # Retrieves the mixing model type of all tanks

        Example 2:

        >>> d.getNodeTankMixingModelType(1)              # Retrieves the mixing model type of the 1st tank

        Example 3:

        >>> d.getNodeTankMixingModelType([1,2])          # Retrieves the mixing model type of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankMixingModelType(tankIndex)      # Retrieves the mixing model type of the tanks given their indices

        See also setNodeTankMixingModelType, getNodeTankMixingModelCode, getNodeTankMixZoneVolume
        """
        return self.__getNodeTankMixiningModel(*argv)[1]

    def getNodeTankMixZoneVolume(self, *argv):
        """ Retrieves the tank mixing zone volume.

        Example 1:

        >>> d.getNodeTankMixZoneVolume()                # Retrieves the mixing zone volume of all tanks

        Example 2:

        >>> d.getNodeTankMixZoneVolume(1)               # Retrieves the mixing zone volume of the 1st tank

        Example 3:

        >>> d.getNodeTankMixZoneVolume([1,2])           # Retrieves the mixing zone volume of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankMixZoneVolume(tankIndex)       # Retrieves the mixing zone volume of the tanks given their indices

        See also getNodeTankMixingModelCode, getNodeTankMixingModelType.
        """
        return self.__getTankNodeInfo(self.ToolkitConstants.EN_MIXZONEVOL, *argv)

    def getNodeTankNameID(self, *argv):
        """ Retrieves the tank IDs.

        Example:

        d.getNodeTankNameID()       # Retrieves the IDs of all tanks
        d.getNodeTankNameID(1)      # Retrieves the ID of the 1st tank
        d.getNodeTankNameID([1,2])  # Retrieves the ID of the first 2 tanks (if they exist!)

        See also getNodeTankCount, getNodeTankIndex.
        """
        if len(argv) == 0:
            return self.getNodeNameID(self.getNodeTankIndex())
        else:
            indices = self.getNodeTankIndex(*argv)
            if isList(indices):
                return [self.getNodeNameID(i) for i in indices]
            else:
                return self.getNodeNameID(indices)

    def getNodeTankReservoirCount(self):
        """ Retrieves the number of tanks/reservoirs.

        Example:

        >>> d.getNodeTankReservoirCount()

        See also getNodeTankIndex, getNodeReservoirIndex.
        """
        return self.api.ENgetcount(self.ToolkitConstants.EN_TANKCOUNT)

    def getNodeTankVolume(self, *argv):
        """ Retrieves the tank volume. (EPANET Version 2.1)

        Example 1:

        >>> d.getNodeTankVolume()                  # Retrieves the volume of all tanks

        Example 2:

        >>> d.getNodeTankVolume(1)                 # Retrieves the volume of the 1st tank

        Example 3:

        >>> d.getNodeTankVolume([1,2])             # Retrieves the volume of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankVolume(tankIndex)         # Retrieves the volume of the tanks given their indices

        See also getNodeTankData.
        """
        return self.__getTankNodeInfo(self.ToolkitConstants.EN_TANKVOLUME, *argv)

    def getNodeTankVolumeCurveIndex(self, *argv):
        """ Retrieves the tank volume curve index.

        Example 1:

        >>> d.getNodeTankVolumeCurveIndex()                # Retrieves the volume curve index of all tanks

        Example 2:

        >>> d.getNodeTankVolumeCurveIndex(1)               # Retrieves the volume curve index of the 1st tank

        Example 3:

        >>> d.getNodeTankVolumeCurveIndex([1,2])           # Retrieves the volume curve index of the first 2 tanks

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.getNodeTankVolumeCurveIndex(tankIndex)       # Retrieves the volume curve index of the tanks given their indices

        See also getNodeTankVolume, getNodeTankMaximumWaterVolume, getNodeTankMinimumWaterVolume,
        getNodeTankInitialWaterVolume, getNodeTankMixZoneVolume.
        """
        value = self.__getTankNodeInfo(self.ToolkitConstants.EN_VOLCURVE, *argv)
        return self.__returnValue(value)

    def getNodeType(self, *argv):
        """ Retrieves the node-type code for all nodes.

        Example 1:

        >>> d.getNodeType()          # Retrieves the node-type code for all nodes

        Example 2:

        >>> d.getNodeType(1)         # Retrieves the node-type code for the first node

        Example 3:

        >>> d.getNodeType([10,11])   # Retrieves the node-type code for the tenth and eleventh nodes

        See also getNodeNameID, getNodeIndex, getNodeTypeIndex, getNodesInfo.
        """
        nTypes = []
        if len(argv) > 0:
            index = argv[0]
            if type(index) is list:
                for i in index:
                    nTypes.append(self.TYPENODE[self.api.ENgetnodetype(i)])
            else:
                nTypes = self.TYPENODE[self.api.ENgetnodetype(index)]
        else:
            for i in range(self.getNodeCount()):
                nTypes.append(self.TYPENODE[self.api.ENgetnodetype(i + 1)])
        return nTypes

    def getNodeTypeIndex(self, *argv):
        """ Retrieves the node-type code for all nodes.

        Example:

        >>> d.getNodeTypeIndex()      # Retrieves the node-type code for all nodes
        >>> d.getNodeTypeIndex(1)     # Retrieves the node-type code for the first node

        See also getNodeNameID, getNodeIndex, getNodeType, getNodesInfo.
        """
        nTypes = []
        if len(argv) > 0:
            index = argv[0]
            if type(index) is list:
                for i in index:
                    nTypes.append(self.api.ENgetnodetype(i))
            else:
                nTypes = self.api.ENgetnodetype(index)
        else:
            for i in range(self.getNodeCount()):
                nTypes.append(self.api.ENgetnodetype(i + 1))
        return nTypes

    def getOptionsAccuracyValue(self):
        """ Retrieves the total normalized flow change for hydraulic convergence.

        Example:

        >>> d.getOptionsAccuracyValue()

        See also setOptionsAccuracyValue, getOptionsExtraTrials, getOptionsMaxTrials.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_ACCURACY)

    def getOptionsCheckFrequency(self):
        """ Retrieves the frequency of hydraulic status checks. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsCheckFrequency()

        See also setOptionsCheckFrequency, getOptionsMaxTrials, getOptionsMaximumCheck.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_CHECKFREQ)

    def getOptionsDampLimit(self):
        """ Retrieves the accuracy level where solution damping begins. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsDampLimit()

        See also setOptionsDampLimit, getOptionsMaxTrials, getOptionsCheckFrequency.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_DAMPLIMIT)

    def getOptionsDemandCharge(self):
        """ Retrieves the energy charge per maximum KW usage. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsDemandCharge()

        See also setOptionsDemandCharge, getOptionsGlobalPrice, getOptionsGlobalPattern.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_DEMANDCHARGE)

    def getOptionsEmitterExponent(self):
        """ Retrieves the power exponent for the emmitters.

        Example:

        >>> d.getOptionsEmitterExponent()

        See also setOptionsEmitterExponent, getOptionsPatternDemandMultiplier, getOptionsAccuracyValue.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_EMITEXPON)

    def getOptionsExtraTrials(self):
        """ Retrieves the extra trials allowed if hydraulics don't converge. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsExtraTrials()

        See also setOptionsExtraTrials, getOptionsMaxTrials, getOptionsMaximumCheck.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_UNBALANCED)

    def getOptionsFlowChange(self):
        """ Retrieves the maximum flow change for hydraulic convergence. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsFlowChange()

        See also setOptionsFlowChange, getOptionsHeadError, getOptionsHeadLossFormula.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_FLOWCHANGE)

    def getOptionsGlobalEffic(self):
        """ Retrieves the global efficiency for pumps(percent). (EPANET Version 2.2)

        Example:

        >>> d.getOptionsGlobalEffic()

        See also setOptionsGlobalEffic, getOptionsGlobalPrice, getOptionsGlobalPattern.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_GLOBALEFFIC)

    def getOptionsGlobalPrice(self):
        """ Retrieves the global average energy price per kW-Hour. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsGlobalPrice()

        See also setOptionsGlobalPrice, getOptionsGlobalEffic, getOptionsGlobalPattern.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_GLOBALPRICE)

    def getOptionsGlobalPattern(self):
        """ Retrieves the index of the global energy price pattern. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsGlobalPattern()

        See also setOptionsGlobalPattern, getOptionsGlobalEffic, getOptionsGlobalPrice.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_GLOBALPATTERN)

    def getOptionsHeadError(self):
        """ Retrieves the maximum head loss error for hydraulic convergence. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsHeadError()

        See also setOptionsHeadError, getOptionsEmitterExponent, getOptionsAccuracyValue.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_HEADERROR)

    def getOptionsHeadLossFormula(self):
        """ Retrieves the headloss formula. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsHeadLossFormula()

        See also setOptionsHeadLossFormula, getOptionsHeadError, getOptionsFlowChange.
        """
        headloss = self.api.ENgetoption(self.ToolkitConstants.EN_HEADLOSSFORM)
        return self.TYPEHEADLOSS[int(headloss)]

    def getOptionsLimitingConcentration(self):
        """ Retrieves the limiting concentration for growth reactions. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsLimitingConcentration()

        See also setOptionsLimitingConcentration, getOptionsPipeBulkReactionOrder, getOptionsPipeWallReactionOrder.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_CONCENLIMIT)

    def getOptionsMaximumCheck(self):
        """ Retrieves the maximum trials for status checking. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsMaximumCheck()

        See also setOptionsMaximumCheck, getOptionsMaxTrials, getOptionsCheckFrequency.
        """
        return int(self.api.ENgetoption(self.ToolkitConstants.EN_MAXCHECK))

    def getOptionsMaxTrials(self):
        """ Retrieves the maximum hydraulic trials allowed for hydraulic convergence.

        Example:

        >>> d.getOptionsMaxTrials()

        See also setOptionsMaxTrials, getOptionsExtraTrials, getOptionsAccuracyValue.
        """
        return int(self.api.ENgetoption(self.ToolkitConstants.EN_TRIALS))

    def getOptionsPatternDemandMultiplier(self):
        """ Retrieves the global pattern demand multiplier.

        Example:

        >>> d.getOptionsPatternDemandMultiplier()

        See also setOptionsPatternDemandMultiplier, getOptionsEmitterExponent, getOptionsAccuracyValue.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_DEMANDMULT)

    def getOptionsPipeBulkReactionOrder(self):
        """ Retrieves the bulk water reaction order for pipes. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsPipeBulkReactionOrder()

        See also setOptionsPipeBulkReactionOrder, getOptionsPipeWallReactionOrder, getOptionsTankBulkReactionOrder.
        """
        return int(self.api.ENgetoption(self.ToolkitConstants.EN_BULKORDER))

    def getOptionsPipeWallReactionOrder(self):
        """ Retrieves the wall reaction order for pipes (either 0 or 1). (EPANET Version 2.2)

        Example:

        >>> d.getOptionsPipeWallReactionOrder()

        See also setOptionsPipeWallReactionOrder, getOptionsPipeBulkReactionOrder, getOptionsTankBulkReactionOrder.
        """
        return int(self.api.ENgetoption(self.ToolkitConstants.EN_WALLORDER))

    def getOptionsQualityTolerance(self):
        """ Retrieves the water quality analysis tolerance.

        Example:

        >>> d.getOptionsQualityTolerance()

        See also setOptionsQualityTolerance, getOptionsSpecificDiffusivity, getOptionsLimitingConcentration.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_TOLERANCE)

    def getOptionsSpecificDiffusivity(self):
        """ Retrieves the specific diffusivity (relative to chlorine at 20 deg C). (EPANET Version 2.2)

        Example:

        >>> d.getOptionsSpecificDiffusivity()

        See also setOptionsSpecificDiffusivity, getOptionsSpecificViscosity, getOptionsSpecificGravity.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_SP_DIFFUS)

    def getOptionsSpecificGravity(self):
        """ Retrieves the specific gravity. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsSpecificGravity()

        See also setOptionsSpecificGravity, getOptionsSpecificViscosity, getOptionsHeadLossFormula.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_SP_GRAVITY)

    def getOptionsSpecificViscosity(self):
        """ Retrieves the specific viscosity. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsSpecificViscosity()

        See also setOptionsSpecificViscosity, getOptionsSpecificGravity, getOptionsHeadLossFormula.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_SP_VISCOS)

    def getOptionsTankBulkReactionOrder(self):
        """ Retrieves the bulk water reaction order for tanks. (EPANET Version 2.2)

        Example:

        >>> d.getOptionsTankBulkReactionOrder()

        See also setOptionsTankBulkReactionOrder, getOptionsPipeBulkReactionOrder, getOptionsPipeWallReactionOrder.
        """
        return int(self.api.ENgetoption(self.ToolkitConstants.EN_TANKORDER))

    def getPattern(self):
        """
        Retrieves the multiplier factor for all patterns and all times.

        Example:

        >>> d.getPattern()

        See also getPatternLengths, getPatternValue, getPatternAverageValue().
        """
        patLens = self.getPatternLengths()
        tmpmaxlen = max(patLens) if patLens else 0
        patCnt = self.getPatternCount()
        value = np.zeros((patCnt, tmpmaxlen))
        for i in range(patCnt):
            tmplength = self.getPatternLengths(i + 1)
            for j in range(tmplength):
                value[i][j] = self.api.ENgetpatternvalue(i + 1, j + 1)
            if tmplength < tmpmaxlen:
                for j in range(tmplength + 1, tmpmaxlen):
                    value[i][j] = value[i][j - tmplength - 1]
        return value

    def getPatternAverageValue(self):
        """ Retrieves the average values of all the time patterns. (EPANET Version 2.1)

        Example:

        >>> d.getPatternAverageValue()

        See also getPattern, setPattern,
        getPatternValue, getPatternLengths.
        """
        value = []
        for i in self.getPatternIndex():
            value.append(self.api.ENgetaveragepatternvalue(i))
        return value

    def getPatternComment(self, *argv):
        """ Retrieves the comment string assigned to the pattern object.

        Example:

        >>> d.getPatternComment()       # Retrieves the comments of all the patterns
        >>> d.getPatternComment(1)      # Retrieves the comment of the 1st pattern
        >>> d.getPatternComment([1,2])  # Retrieves the comments of the first 2 patterns

        See also setPatternComment, getPattern.
        """
        if len(argv) == 0:
            value = []
            for i in range(1, self.getPatternCount() + 1):
                value.append(self.api.ENgetcomment(self.ToolkitConstants.EN_TIMEPAT, i))
        elif isList(argv[0]):
            value = []
            for i in argv[0]:
                value.append(self.api.ENgetcomment(self.ToolkitConstants.EN_TIMEPAT, i))
        else:
            value = self.api.ENgetcomment(self.ToolkitConstants.EN_TIMEPAT, argv[0])
        return value

    def getPatternCount(self):
        """ Retrieves the number of patterns.

        Example:

        >>> d.getPatternCount()

        See also getPatternIndex, getPattern.
        """
        return self.api.ENgetcount(self.ToolkitConstants.EN_PATCOUNT)

    def getPatternIndex(self, *argv):
        """ Retrieves the index of all or some time patterns given their IDs.

        Example 1:

        >>> d.getPatternIndex()              # Retrieves the indices of all time patterns

        Example 2:

        >>> patternIndex = 1
        >>> patternID = d.getPatternNameID(patternIndex)
        >>> d.getPatternIndex(patternID)     # Retrieves the index of the 1st time pattern given it's ID

        Example 3:

        >>> d = epanet('Richmond_standard.inp')
        >>> patternIndex = [1,2]
        >>> patternID = d.getPatternNameID(patternIndex)
        >>> d.getPatternIndex(patternID)     # Retrieves the index of the first 2 time patterns given their IDs

        See also getPatternNameID, getPattern.
        """
        value = []
        if len(argv) == 0:
            value = list(range(1, self.getPatternCount() + 1))
        elif isList(argv[0]):
            value = []
            for j in range(len(argv[0])):
                value.append(self.api.ENgetpatternindex(argv[0][j]))
        elif type(argv[0]) is str:
            value = self.api.ENgetpatternindex(argv[0])
        return value

    def getPatternLengths(self, *argv):
        """ Retrieves the number of time periods in all or some time patterns.

        Example 1:

        >>> d.getPatternLengths()                 # Retrieves the number of time periods of all time patterns

        Example 2:

        >>> patternIndex = 1
        >>> d.getPatternLengths(patternIndex)     # Retrieves the number of time periods of the 1st time pattern

        Example 3:

        >>> d = epanet('BWSN_Network_1.inp')
        >>> patternIndex = [1,2,3]
        >>> d.getPatternLengths(patternIndex)     # Retrieves the number of time periods of the first 2 time patterns

        See also getPatternIndex, getPattern.
        """
        value = []
        if len(argv) == 0:
            for i in range(self.getPatternCount()):
                value.append(self.api.ENgetpatternlen(i + 1))
        elif isList(argv[0]) and type(argv[0][0]) is str:
            for j in range(len(argv[0])):
                value.append(self.api.ENgetpatternlen(self.getPatternIndex(argv[0][j])))
        elif type(argv[0]) is str:
            value.append(self.api.ENgetpatternlen(self.getPatternIndex(argv[0])))
        else:
            if not isList(argv[0]):
                value = self.api.ENgetpatternlen(argv[0])
            else:
                for i in argv[0]:
                    value.append(self.api.ENgetpatternlen(i))
        return value

    def getPatternNameID(self, *argv):
        """ Retrieves the ID label of all or some time patterns indices.

        Example 1:

        >>> d.getPatternNameID()          # Retrieves the IDs of all the patterns

        Example 2:

        >>> d.getPatternNameID(1)         # Retrieves the ID of the 1st pattern

        Example 3:

        >>> d.getPatternNameID([1,2])     # Retrieves the IDs of the first 2 patterns

        See also setPatternNameID, getPattern.
        """
        values = []
        if len(argv) > 0:
            index = argv[0]
            if type(index) is list:
                for i in index:
                    values.append(self.api.ENgetpatternid(i))
            else:
                values = self.api.ENgetpatternid(index)
        else:
            for i in range(self.getPatternCount()):
                values.append(self.api.ENgetpatternid(i + 1))
        return values

    def getPatternValue(self, patternIndex, patternStep):
        """ Retrieves the multiplier factor for a certain pattern and time.

        Example:

        >>> patternIndex = 1
        >>> patternStep = 5
        >>> d.getPatternValue(patternIndex, patternStep)   # Retrieves the 5th multiplier factor of the 1st time pattern

        See also getPattern, getPatternLengths, getPatternAverageValue().
        """
        return self.api.ENgetpatternvalue(patternIndex, patternStep)

    def getQualityCode(self):
        """ Retrieves the code of water quality analysis type.

        Water quality analysis code:
          0 = No quality analysis
          1 = Chemical analysis
          2 = Water age analysis
          3 = Source tracing

        Example:

        >>> d.getQualityCode()

        See also getQualityInfo, getQualityType.
        """
        [value, self.QualityTraceNodeIndex] = self.api.ENgetqualtype()
        return value 

    def getQualityInfo(self):
        """ Retrieves quality analysis information (type, chemical name, units, trace node ID).

        Information that is retrieved:
          1) Water quality analysis code
             0 = No quality analysis
             1 = Chemical analysis
             2 = Water age analysis
             3 = Source tracing
          2) Name of the chemical being analyzed
          3) Units that the chemical is measured in
          4) Index of node traced in a source tracing analysis
          5) Quality type

        Example:

        >>> qualInfo = d.getQualityInfo()          # Retrieves all the quality info
        >>> qualInfo.to_dict()
        >>> d.getQualityInfo().QualityCode         # Retrieves the water quality analysis code
        >>> d.getQualityInfo().QualityChemName     # Retrieves the name of the chemical being analyzed
        >>> d.getQualityInfo().QualityChemUnits    # Retrieves the units that the chemical is measured in
        >>> d.getQualityInfo().TraceNode           # Retrieves the index of node traced in a source tracing analysis
        >>> d.getQualityInfo().QualityType         # Retrieves the quality type

        See also getQualityType, getQualityCode.
        """
        value = val()
        qual_list = self.api.ENgetqualinfo()
        value.QualityCode = qual_list[0]
        value.QualityChemName = qual_list[1]
        value.QualityChemUnits = qual_list[2]
        value.TraceNode = qual_list[3]
        value.QualityType = self.TYPEQUALITY[value.QualityCode]
        self.qual = value
        return value

    def getQualityTraceNodeIndex(self):
        """ Retrieves the trace node index of water quality analysis type.

        Example:

        >>> d.getQualityTraceNodeIndex()

        See also getQualityInfo, getQualityType.
        """
        [self.QualityCode, value] = self.api.ENgetqualtype()
        return value

    def getQualityType(self, *argv):
        """ Retrieves the type of water quality analysis type.

        Example:

        >>> d.getQualityType()

        See also getQualityInfo, getQualityCode.
        """
        return self.TYPEQUALITY[self.api.ENgetqualinfo()[0]]

    def getLinkResultIndex(self, link_index):
        """ Retrieves the order in which a link's results
        were saved to an output file. (EPANET Version 2.2)

        Example:

        >>> link_index = 3
        >>> result_index = d.getLinkResultIndex(link_index)

        See also getComputedHydraulicTimeSeries, deleteNode, getNodeResultIndex
        """
        return self.api.ENgetresultindex(self.ToolkitConstants.EN_LINK, link_index)

    def getRuleCount(self):
        """ Retrieves the number of rules. (EPANET Version 2.2)

        Example:

        >>> d.getRuleCount()

        See also getRules, getControlRulesCount.
        """
        return self.api.ENgetcount(self.ToolkitConstants.EN_RULECOUNT)

    def getRuleID(self, *argv):
        """ Retrieves the ID name of a rule-based control given its index. (EPANET Version 2.2)

        # The examples are based on d = epanet('BWSN_Network_1.inp')

        Example:

        >>> d.getRuleID()           # Retrieves the ID name of every rule-based control
        >>> d.getRuleID(1)          # Retrieves the ID name of the 1st rule-based control
        >>> d.getRuleID([1,2,3])    # Retrieves the ID names of the 1st to 3rd rule-based control

        See also getRules, getRuleInfo, addRules.
        """
        if len(argv) == 0:
            index = list(range(1, self.getRuleCount()))
        elif len(argv) == 1:
            index = argv[0]
        if isList(index):
            value = []
            for i in index:
                value.append(self.api.ENgetruleID(i))
            return value
        else:
            return self.api.ENgetruleID(index)

    def getRuleInfo(self, *argv):
        """ Retrieves summary information about a rule-based control given it's index. (EPANET Version 2.2)

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example:

        >>> RuleInfo = d.getRuleInfo()          # Retrieves summary information about every rule-based control
        >>> d.getRuleInfo(1).to_dict()           # Retrieves summary information about the 1st rule-based control
        >>> d.getRuleInfo([1,2,3]).to_dict()     # Retrieves summary information about the 1st to 3rd rule-based control

        See also getRuleID, getRules, addRules.
        """
        value = val()
        if len(argv) == 0:
            index = list(range(1, self.getRuleCount() + 1))
        elif isList(argv[0]):
            index = argv[0]
        else:
            index = [argv[0]]
        value.Index = index
        value.Premises, value.ThenActions, value.ElseActions, value.Priority = [], [], [], []
        for i in index:
            tempVal = self.api.ENgetrule(i)
            value.Premises.append(tempVal[0])
            value.ThenActions.append(tempVal[1])
            value.ElseActions.append(tempVal[2])
            value.Priority.append(tempVal[3])
        return value

    def getRules(self, *argv):
        """ Retrieves the rule - based control statements. (EPANET Version 2.2)

        # The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> rules = d.getRules()
        >>> rule_first_index = 1
        >>> rule_first = rules[rule_first_index]                   # Retrieves all the statements of the 1st rule - based control
        >>> rule_second_index = 2
        >>> rule_second = rules[rule_second_index]                 # Retrieves all the statements of the 2nd rule - based control

        Example 2:

        >>> rule_first = d.getRules(1)                                  # Retrieves all the statements of the 1st rule - based control
        >>> rule_first_ID = d.getRules()[1]['Rule_ID']                  # Retrieves the ID of the 1st rule - based control
        >>> rule_first_premises = d.getRules()[1]['Premises']           # Retrieves all the premises of the 1st rule - based control
        >>> rule_first_Then_Actions = d.getRules()[1]['Then_Actions']   # Retrieves all the then actions of the 1st rule - based control
        >>> rule_first_Else_Actions = d.getRules()[1]['Else_Actions']   # Retrieves all the else actions of the 1st rule - based control
        >>> rule_first_Rule = d.getRules()[1]['Rule']

        See also getRuleInfo, getRuleID, getRuleCount, setRules, deleteRules, addRules.
        """
        ruleDict = {}
        if len(argv) == 0:
            ruleIndex = list(range(1, self.getRuleCount() + 1))
        elif isList(argv[0]):
            ruleIndex = argv[0]
        else:
            ruleIndex = [argv[0]]

        for i in ruleIndex:
            cnt = self.getRuleInfo().Premises[i - 1]
            premises = []
            for j in range(1, cnt + 1):
                [logop, object_, objIndex, variable, relop, status, value_premise] = self.api.ENgetpremise(i, j)
                if j == 1:
                    logop = 1
                if object_ == self.ToolkitConstants.EN_R_NODE:
                    objectNameID = self.getNodeNameID(objIndex)
                    space = ' '
                elif object_ == self.ToolkitConstants.EN_R_LINK:
                    objectNameID = self.getLinkNameID(objIndex)
                    space = ' '
                elif object_ == self.ToolkitConstants.EN_R_SYSTEM:
                    objectNameID = ' '
                    space = ''
                if variable >= self.ToolkitConstants.EN_R_TIME:
                    value_premise = datetime.utcfromtimestamp(value_premise).strftime("%I:%M %p UTC")
                else:
                    value_premise = str(value_premise)
                if status == 0:
                    ruleStatus = ''
                else:
                    ruleStatus = self.RULESTATUS[status - 1]
                    value_premise = ''
                premises.append(
                    self.LOGOP[logop - 1] + ' ' + self.RULEOBJECT[object_ - 6] + space + objectNameID + space +
                    self.RULEVARIABLE[variable]
                    + ' ' + self.RULEOPERATOR[relop] + ' ' + ruleStatus + value_premise)
            cnt = self.getRuleInfo().ThenActions[i - 1]
            thenactions = []
            for j in range(1, cnt + 1):
                [linkIndex, status, setting] = self.api.ENgetthenaction(i, j)
                if j == 1:
                    logop = 'THEN'
                else:
                    logop = 'AND'
                link_type = self.getLinkType(linkIndex)
                linkNameID = self.getLinkNameID(linkIndex)
                if status in [1, 2, 3]:
                    status = 'STATUS IS ' + self.RULESTATUS[status - 1]
                else:
                    status = ''
                if setting >= 0:
                    setting = 'SETTING IS ' + str(setting)
                else:
                    setting = ''
                thenactions.append(logop + ' ' + link_type + ' ' + linkNameID + ' ' + status + setting)
            cnt = self.getRuleInfo().ElseActions[i - 1]
            elseactions = []
            for j in range(1, cnt + 1):
                [linkIndex, status, setting] = self.api.ENgetelseaction(i, j)
                if j == 1:
                    logop = 'ELSE'
                else:
                    logop = 'AND'
                link_type = self.getLinkType(linkIndex)
                linkNameID = self.getLinkNameID(linkIndex)
                if status in [1, 2, 3]:
                    status = ' STATUS IS ' + self.RULESTATUS[status - 1]
                else:
                    status = ''
                if setting >= 0:
                    setting = ' SETTING IS ' + str(setting)
                else:
                    setting = ''
                elseactions.append(logop + ' ' + link_type + ' ' + linkNameID + '' + status + setting)
            ruleDict[i] = {}
            ruleDict[i]['Rule_ID'] = self.getRuleID(i)
            ruleDict[i]['Premises'] = premises
            ruleDict[i]['Then_Actions'] = thenactions
            ruleDict[i]['Else_Actions'] = elseactions
            ruleDict[i]['Rule'] = ['RULE ' + self.getRuleID(i), premises, thenactions, elseactions,
                                   'PRIORITY ' + str(self.getRuleInfo().Priority[i - 1])]
        return ruleDict

    def getStatistic(self):
        """ Returns error code. (EPANET Version 2.1)

        Input:  none

        Output:
            * iter:   # of iterations to reach solution
            * relerr: convergence error in solution

        Example:

        >>> d.getStatistic().disp()

        """
        value = val()
        value.Iterations = self.api.ENgetstatistic(self.ToolkitConstants.EN_ITERATIONS)
        value.RelativeError = self.api.ENgetstatistic(self.ToolkitConstants.EN_RELATIVEERROR)
        value.DeficientNodes = self.api.ENgetstatistic(self.ToolkitConstants.EN_DEFICIENTNODES)
        value.DemandReduction = self.api.ENgetstatistic(self.ToolkitConstants.EN_DEMANDREDUCTION)
        return value

    def getTimeSimulationDuration(self):
        """ Retrieves the value of simulation duration.

        Example:

        >>> d.getTimeSimulationDuration()

        See also getTimePatternStep, getTimeSimulationDuration.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_DURATION)

    def getTimeHydraulicStep(self):
        """ Retrieves the value of the hydraulic time step.

        Example:

        >>> d.getTimeHydraulicStep()

        See also getTimeQualityStep, getTimeSimulationDuration.
        """

        return self.api.ENgettimeparam(self.ToolkitConstants.EN_HYDSTEP)

    def getTimeQualityStep(self):
        """ Retrieves the value of the water quality time step.

        Example:

        >>> d.getTimeQualityStep()

        See also getTimeSimulationDuration, getTimeSimulationDuration.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_QUALSTEP)

    def getTimePatternStep(self):
        """ Retrieves the value of the pattern time step.

        Example:

        >>> d.getTimePatternStep()

        See also getTimePatternStart, getTimeSimulationDuration.
        """

        return self.api.ENgettimeparam(self.ToolkitConstants.EN_PATTERNSTEP)

    def getTimePatternStart(self):
        """ Retrieves the value of pattern start time.

        Example:

        >>> d.getTimePatternStart()

        See also getTimePatternStep, getTimeSimulationDuration.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_PATTERNSTART)

    def getTimeReportingStep(self):
        """ Retrieves the value of the reporting time step.

        Example:

        >>> d.getTimeReportingStep()

        See also getTimeReportingPeriods, getTimeReportingStart.
        """

        return self.api.ENgettimeparam(self.ToolkitConstants.EN_REPORTSTEP)

    def getTimeReportingStart(self):
        """ Retrieves the value of the reporting start time.

        Example:

        >>> d.getTimeReportingStart()

        See also getTimeReportingPeriods, getTimeReportingStep.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_REPORTSTART)

    def getTimeRuleControlStep(self):
        """ Retrieves the time step for evaluating rule-based controls.

        Example:

        >>> d.getTimeRuleControlStep()

        See also getTimeSimulationDuration.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_RULESTEP)

    def getTimeStatisticsType(self):
        """ Retrieves the type of time series post-processing.

        Types:
            1. NONE:    Reports the full time series for all quantities for all nodes and links (default)
            2. AVERAGE: Reports a set of time-averaged results
            3. MINIMUM: Reports only the minimum values
            4. MAXIMUM: Reports only the maximum values
            5. RANGE:   Reports the difference between the minimum and maximum values

        Example:

        >>> d.getTimeStatisticsType()

        See also getTimeStatisticsIndex, getTimeSimulationDuration.
        """
        self.TimeStatisticsIndex = self.api.ENgettimeparam(self.ToolkitConstants.EN_STATISTIC)
        return self.TYPESTATS[self.TimeStatisticsIndex]

    def getTimeStatisticsIndex(self):
        """ Retrieves the index of the type of time series post-processing.

        Type of time series post-processing:
          0 = 'NONE'
          1 = 'AVERAGE'
          2 = 'MINIMUM'
          3 = 'MAXIMUM'
          4 = 'RANGE'

        Example:

        >>> d.getTimeStatisticsIndex()

        See also getTimeStatisticsType, getTimeSimulationDuration.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_STATISTIC)

    def getTimeReportingPeriods(self):
        """ Retrieves the number of reporting periods saved to the binary.

        Example:

        >>> d.getTimeReportingPeriods()

        See also getTimeReportingStart, getTimeReportingStep.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_PERIODS)

    def getTimeStartTime(self):
        """ Retrieves the simulation starting time of day.

        Example:

        >>> d.getTimeStartTime()

        See also getTimeSimulationDuration, getTimePatternStart.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_STARTTIME)

    def getTimeHTime(self):
        """ Retrieves the elapsed time of current hydraulic solution.

        Example:

        >>> d.getTimeHTime()

        See also getTimeSimulationDuration, getComputedHydraulicTimeSeries.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_HTIME)

    def getTimeQTime(self):
        """Retrieves the elapsed time of current quality solution.

        Example:

        >>> d.getTimeQTime()

        See also getTimeQualityStep, getComputedQualityTimeSeries.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_QTIME)

    def getTimeHaltFlag(self):
        """ Retrieves the number of halt flag indicating if the simulation was halted.

        Example:

        >>> d.getTimeHaltFlag()

        See also getTimeStartTime, getTimeSimulationDuration.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_HALTFLAG)

    def getTimeNextEvent(self):
        """ Retrieves the shortest time until a tank becomes empty or full.

        Example:

        >>> d.getTimeNextEvent()

        See also getTimeNextEventTank.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_NEXTEVENT)

    def getTimeNextEventTank(self):
        """ Retrieves the index of tank with shortest time to become empty or full.

        Example:

        >>> d.getTimeNextEventTank()

        See also getTimeNextEvent.
        """
        return self.api.ENgettimeparam(self.ToolkitConstants.EN_NEXTEVENTTANK)

    def getTitle(self, *argv):
        """ Retrieves the title lines of the project.

        Example: Retrieves the three title lines of the project.

        >>> [Line1, Line2, Line3] = d.getTitle()

        See also setTitle.
        """
        return self.api.ENgettitle()

    def getUnits(self):
        """ Retrieves the Units of Measurement.

        Example 1:

        >>> allUnits = d.getUnits()           # Retrieves all the unitperiod
        >>> allUnits.to_dict()                # Print all values

        Example 2:

        >>> d.getUnits().NodeElevationUnits   # Retrieves elevation units
        >>> d.getUnits().LinkVelocityUnits    # Retrieves velocity units

        OWA-EPANET Toolkit: https://github.com/OpenWaterAnalytics/EPANET/wiki/Units-of-Measurement

        See also getFlowUnits.
        """
        value = val()
        if self.TYPEUNITS.index(self.getFlowUnits()) < 5:
            value.Units_US_Customary = 1
            value.Units_SI_Metric = 0
        else:
            value.Units_SI_Metric = 1
            value.Units_US_Customary = 0

        value.LinkFlowUnits = self.getFlowUnits()
        if value.Units_US_Customary:
            value.NodePressureUnits = 'psi'
            value.PatternDemandsUnits = value.LinkFlowUnits
            value.LinkPipeDiameterUnits = 'inches'
            value.NodeTankDiameterUnits = 'feet'
            value.EnergyEfficiencyUnits = 'percent'
            value.NodeElevationUnits = 'feet'
            value.NodeDemandUnits = value.LinkFlowUnits
            value.NodeEmitterCoefficientUnits = 'flow units @ 1 psi drop'
            value.EnergyUnits = 'kwatt-hours'
            value.LinkFrictionFactorUnits = 'unitless'
            value.NodeHeadUnits = 'feet'
            value.LinkLengthsUnits = 'feet'
            value.LinkMinorLossCoeffUnits = 'unitless'
            value.LinkPumpPowerUnits = 'horsepower'
            value.QualityReactionCoeffBulkUnits = '1/day (1st-order)'
            value.QualityReactionCoeffWallUnits = 'mass/sq-ft/day (0-order), ft/day (1st-order)'
            value.LinkPipeRoughnessCoeffUnits = 'millifeet(Darcy-Weisbach), unitless otherwise'
            value.QualitySourceMassInjectionUnits = 'mass/minute'
            value.LinkVelocityUnits = 'ft/sec'
            value.NodeTankVolumeUnits = 'cubic feet'
            value.QualityWaterAgeUnits = 'hours'
        else:  # SI Metric
            value.NodePressureUnits = 'meters'
            value.PatternDemandsUnits = value.LinkFlowUnits
            value.LinkPipeDiameterUnits = 'millimeters'
            value.NodeTankDiameterUnits = 'meters'
            value.EnergyEfficiencyUnits = 'percent'
            value.NodeElevationUnits = 'meters'
            value.NodeDemandUnits = value.LinkFlowUnits
            value.NodeEmitterCoefficientUnits = 'flow units @ 1 meter drop'
            value.EnergyUnits = 'kwatt-hours'
            value.LinkFrictionFactorUnits = 'unitless'
            value.NodeHeadUnits = 'meters'
            value.LinkLengthsUnits = 'meters'
            value.LinkMinorLossCoeffUnits = 'unitless'
            value.LinkPumpPowerUnits = 'kwatts'
            value.QualityReactionCoeffBulkUnits = '1/day (1st-order)'
            value.QualityReactionCoeffWallUnits = 'mass/sq-m/day(0-order), meters/day (1st-order)'
            value.LinkPipeRoughnessCoeffUnits = 'mm(Darcy-Weisbach), unitless otherwise'
            value.QualitySourceMassInjectionUnits = 'mass/minute'
            value.LinkVelocityUnits = 'meters/sec'
            value.NodeTankVolumeUnits = 'cubic meters'
            value.QualityWaterAgeUnits = 'hours'
        self.units = value
        return value

    def getVersion(self):
        """ Retrieves the current EPANET version of DLL.

        Example:

        >>> d.getVersion()

        See also getENfunctionsImpemented, getLibFunctions.
        """
        return self.api.ENgetversion()

    def initializeEPANET(self, unitsType, headLossType):
        """ Initializes an EPANET project that isn't opened with an input file

        Example:

        >>> d.initializeEPANET(d.ToolkitConstants.EN_GPM, d.ToolkitConstants.EN_HW)

        See also initializeHydraulicAnalysis.
        """
        self.api.ENinit(unitsType, headLossType)

    def initializeQualityAnalysis(self, *argv):
        """ Initializes water quality and the simulation clock time prior to running a water quality analysis.

        Codes:
          1) NOSAVE        = 0,   Don't save the results to the project's binary output file.
          2) SAVE          = 1,   Save the results to the project's binary output file.

        Example 1:

        >>> d.initializeQualityAnalysis()       #  Uses the default code i.e. SAVE = 1

        Example 2:

        >>> code = 0                            # i.e. Don't save
        >>> d.initializeQualityAnalysis(code)

        For more, you can type `help getNodePressure` and check examples 3 & 4.

        See also openQualityAnalysis, initializeHydraulicAnalysis.
        """
        if len(argv) == 0:
            code = self.ToolkitConstants.EN_SAVE
        # self.ToolkitConstants.EN_SAVE_AND_INIT
        # self.ToolkitConstants.EN_NOSAVE
        # self.ToolkitConstants.EN_INITFLOW
        else:
            code = argv[0]
        self.api.ENinitQ(code)

    def loadEPANETFile(self, *argv):
        """ Load epanet file when use bin functions.

        Example:

        >>> d.loadEPANETFile(d.TempInpFile)
        """

        if len(argv) == 1:
            self.api.ENopen(argv[0], argv[0][0:-4] + '.txt', argv[0][0:-4] + '.bin')
        else:
            self.api.ENopen(argv[0], argv[1], argv[2])

    def max(self, value):
        """ Retrieves the max value of numpy.array or numpy.mat """
        return np.max(value)

    def multiply_elements(self, arr1, arr2):
        """ Multiply elementwise two numpy.array or numpy.mat variables """
        return np.multiply(arr1,arr2)

    def min(self, value):
        """ Retrieves the min value of numpy.array or numpy.mat """
        return np.min(value)

    def nextQualityAnalysisStep(self):
        """ Advances the water quality simulation to the start of the next hydraulic time period.

        Example:

        >>> d.nextQualityAnalysisStep()

        For more, you can type `help getNodePressure` and check examples 3 & 4.

        See also nextHydraulicAnalysisStep, runQualityAnalysis.
        """
        return self.api.ENnextQ()

    def openAnyInp(self, *argv):
        """ Open as on matlab editor any EPANET input file using built in
        function open. Open current loaded input file (not temporary)

        Example:

        >>> d.openAnyInp()
        >>> d.openAnyInp('epyt/networks/Net2.inp')
        """
        arg = self.InputFile
        if len(argv) == 1:
            arg = argv[0]
        try:
            subprocess.call(['Spyder.exe', arg])
        except:
            subprocess.call(['notepad.exe', arg])

    def openCurrentInp(self, *argv):
        """ Opens EPANET input file who is loaded

        Example:

        >>> d.openCurrentInp()
        """
        try:
            subprocess.call(['Spyder.exe', self.TempInpFile])
        except:
            subprocess.call(['notepad.exe', self.TempInpFile])

    def openQualityAnalysis(self):
        """ Opens the water quality analysis system.

        Example:

        >>> d.openQualityAnalysis()

        For more, you can type `help getNodePressure` and check examples 3 & 4.

        See also openHydraulicAnalysis, initializeQualityAnalysis.
        """
        self.api.ENopenQ()

    def reloadNetwork(self):
        """ Reloads the Network (ENopen) """
        self.api.ENopen(self.TempInpFile, self.BinTempfile[0:-4] + '.txt', self.BinTempfile[0:-4] + '.bin')

    def runEPANETexe(self):
        """ Runs epanet .exe file """
        arch = sys.platform
        [inpfile, rptfile, binfile] = self.__createTempfiles(self.TempInpFile)
        if arch == 'win64' or arch == 'win32':
            r = '"%s.exe" "%s" %s %s & exit' % (self.LibEPANET[:-4], inpfile, rptfile, binfile)

        else:
            r = '"%s" "%s" %s %s & exit' % (self.LibEPANET[:-3], inpfile, rptfile, binfile)

        try:
            subprocess.run(r)
        except:
            return [False, '', '']
        fid = open(binfile, "rb")

        return [fid, binfile, rptfile]

    def runQualityAnalysis(self):
        """ Makes available the hydraulic and water quality results that occur at the start of
        the next time period of a water quality analysis, where the start of the period is returned in t.

        Example:

        >>> tstep = d.runQualityAnalysis()

        For more, you can type `help getNodePressure` and check examples 3 & 4.

        See also runHydraulicAnalysis, initializeQualityAnalysis.
        """
        return self.api.ENrunQ()

    def runsCompleteSimulation(self, *argv):
        """ Runs a complete hydraulic and water simulation to create
        binary & report files with name: [NETWORK_temp.txt], [NETWORK_temp.bin]
        OR you can use argument to runs a complete simulation via self.api.en_epanet

        Example:

        >>> d.runsCompleteSimulation()
        >>> d.runsCompleteSimulation('results')  # using d.api.en_epanet
        """
        if len(argv) == 0:
            self.solveCompleteHydraulics()
            self.solveCompleteQuality()
            self.writeReport()
        elif len(argv) == 1:
            rptfile = argv[0] + '.txt'
            binfile = argv[0] + '.bin'
            self.api.ENepanet(self.TempInpFile, rptfile, binfile)
            self.reloadNetwork()

    def saveHydraulicFile(self, hydname):
        """ Saves the current contents of the binary hydraulics file to a file.

        Example:

        >>> filename = 'test.hyd'
        >>> d.saveHydraulicFile(filename)

        For more, you can type `help getNodePressure` and check examples 3 & 4.

        See also useHydraulicFile, initializeHydraulicAnalysis.
        """
        self.api.ENsavehydfile(hydname)

    def saveHydraulicsOutputReportingFile(self):
        """ Transfers results of a hydraulic simulation from the binary Hydraulics file
        to the binary Output file, where results are only reported at uniform reporting intervals.

        Example:

        >>> d.saveHydraulicsOutputReportingFile()

        See also saveHydraulicFile, closeHydraulicAnalysis.
        """
        self.api.ENsaveH()

    def saveInputFile(self, *argv):
        """ Writes all current network input data to a file using the format of an EPANET input file.
        Returns an error code.

        Example:

        >>> filename = ('test.inp')
        >>> d.saveInputFile(filename)

        See also unload, saveHydraulicFile.
        """
        if len(argv) == 0:
            inpname = self.TempInpFile
        elif len(argv) == 1:
            inpname = argv[0]
        self.api.ENsaveinpfile(inpname)

    def setCMDCODE(self, code):
        """ Sets the CMC code """
        value = code
        if code != 0 and code != 1:
            value = self.CMDCODE
        self.CMDCODE = value

    def setControls(self, index, control=None, *argv):
        """ Sets the parameters of a simple control statement.

        The examples are based on d = epanet('Net1.inp')

        Example 1:

        >>> controlIndex = 1
        >>> d.getControls(controlIndex).disp()       # Retrieves the 1st control
        >>> control = 'LINK 9 CLOSED IF NODE 2 ABOVE 180'
        >>> d.setControls(controlIndex, control)     # Sets a control given it's index and the control statement
        >>> d.getControls(controlIndex).disp()

        Example 2:

        >>> controls = d.getControls()
        >>> d.setControls(controls)              # Sets multiple controls given as dicts with keys

        Example 3:

        >>> control_1 = 'LINK 9 OPEN IF NODE 2 BELOW 110'
        >>> control_2 = 'LINK 9 CLOSED IF NODE 2 ABOVE 200'
        >>> controls = [control_1, control_2]
        >>> d.setControls(controls)              # Sets multiple controls given as cell
        >>> d.getControls(1).disp()
        >>> d.getControls(2).disp()

        Example 4:
              * index:     control statement index
              * control:   control type code
              * lindex:    index of link being controlled
              * setting:   value of the control setting
              * nindex:    index of controlling node
              * level:     value of controlling water level or pressure for
                  level controls or of time of control action
                  (in seconds) for time-based controls

        Control type codes consist of the following:
         * EN_LOWLEVEL      0   Control applied when tank level or node pressure drops below specified level
         * EN_HILEVEL       1   Control applied when tank level or node pressure rises above specified level
         * EN_TIMER         2   Control applied at specific time into simulation
         * EN_TIMEOFDAY     3   Control applied at specific time of day

        Code example: d.setControls(index, control, lindex, setting, nindex, level)

        >>> d.setControls(1, 0, 13, 0, 11, 30)

        See also getControls, getControlRulesCount, addControls, deleteControls.
        """
        if type(index) is dict:
            for key in index:
                self.__setControlFunction(key, index[key].Control)
        else:
            if len(argv) == 0:
                if isList(index):
                    tmpC = index
                    for i in tmpC:
                        self.__setControlFunction(tmpC.index(i) + 1, i)
                else:
                    if type(index) is int:
                        tmpC = control
                    else:
                        tmpC = index
                        index = 1
                    self.__setControlFunction(index, tmpC)
            else:
                linkIndex = argv[0]
                controlSettingValue = argv[1]
                nodeIndex = argv[2]
                controlLevel = argv[3]
                self.api.ENsetcontrol(index, control, linkIndex, controlSettingValue, nodeIndex, controlLevel)

    def setCurve(self, index, curveVector):
        """ Sets x, y values for a specific curve. (EPANET Version 2.1)

        The example is based on d = epanet('BWSN_Network_1.inp')

        Example:

        >>> curveIndex = 1
        >>> d.getCurvesInfo().CurveXvalue[curveIndex-1]    # Retrieves the X values of the 1st curve
        >>> d.getCurvesInfo().CurveYvalue[curveIndex-1]    # Retrieves the Y values of the 1st curve
        >>> x_y_1 = [0, 730]
        >>> x_y_2 = [1000, 500]
        >>> x_y_3 = [1350, 260]
        >>> values = [x_y_1, x_y_2, x_y_3]             # X and Y values selected.
        >>> d.setCurve(curveIndex, values)             # Sets the X and Y values of the 1st curve
        >>> d.getCurvesInfo().CurveXvalue[curveIndex-1]
        >>> d.getCurvesInfo().CurveYvalue[curveIndex-1]

        See also setCurveValue, getCurvesInfo.
        """
        if isList(curveVector[0]):
            nfactors = len(curveVector)  # x = number of points in curve
            self.api.ENsetcurve(index, [i[0] for i in curveVector], [i[1] for i in curveVector], nfactors)
        else:
            self.api.ENsetcurve(index, curveVector[0], curveVector[1], 1)

    def setCurveComment(self, value, *argv):
        """ Sets the comment string of a curve.

        Example 1:

        >>> d.getCurveComment()                      # Retrieves the comments of all the curves
        >>> curveIndex = 1
        >>> comment = 'This is a curve'
        >>> d.setCurveComment(curveIndex, comment)   # Sets a comment to the 1st curve
        >>> d.getCurveComment(curveIndex)

        Example 2:

        >>> d = epanet('BWSN_Network_1.inp')
        >>> d.getCurveComment()
        >>> curveIndex = [1,2]
        >>> comment = ['This is the 1st curve', 'This is the 2nd curve']
        >>> d.setCurveComment(curveIndex, comment)   # Sets comments to the first 2 curves
        >>> d.getCurveComment(curveIndex)

        See also getCurveComment, getCurveIndex, getCurvesInfo.
        """
        if len(argv) == 0:
            cIndices = list(range(1,self.getCurveCount()+1))
        else:
            cIndices = argv[0]
        self.__addComment(self.ToolkitConstants.EN_CURVE, value, cIndices)

    def setCurveNameID(self, index, Id):
        """ Sets the name ID of a curve given it's index and the new ID. (EPANET Version 2.2)

        Example 1:

        >>> d.getCurveNameID()                               # Retrieves the name IDs of all the curves
        >>> d.setCurveNameID(1, 'Curve1')                    # Sets to the 1st curve the new name ID 'Curve1'
        >>> d.getCurveNameID()

        Example 2: Sets to the 1st and 2nd curve the new name IDs 'Curve1' and 'Curve2' respectively.

        >>> d.setCurveNameID([1, 2], ['Curve1', 'Curve2'])
        >>> d.getCurveNameID()

        See also getCurveNameID, getCurveIndex, getCurveLengths, setCurve, setCurveComment, getCurveComment.
        """
        if isList(index):
            for i in index:
                self.api.ENsetcurveid(index[index.index(i)], Id[index.index(i)])
        else:
            self.api.ENsetcurveid(index, Id)

    def setCurveValue(self, index, curvePnt, value):
        """ Sets x, y point for a specific point number and curve. (EPANET Version 2.1)

        The example is based on d = epanet('BWSN_Network_1.inp')

        Example:

        >>> curveIndex = 1
        >>> d.getCurvesInfo().CurveXvalue[curveIndex-1]            # Retrieves the X values of the 1st curve
        >>> d.getCurvesInfo().CurveYvalue[curveIndex-1]            # Retrieves the Y values of the 1st curve
        >>> curvePoint = 1                                         # Point of the curve selected
        >>> x_y_values = [10, 400]                                 # X and Y values selected
        >>> d.setCurveValue(curveIndex, curvePoint, x_y_values)    # Sets the X and Y values of the 1st point on the 1st curve
        >>> d.getCurvesInfo().CurveXvalue[curveIndex-1]
        >>> d.getCurvesInfo().CurveYvalue[curveIndex-1]

        See also getCurveValue, setCurve, getCurvesInfo.
        """
        x = value[0]
        y = value[1]
        self.api.ENsetcurvevalue(index, curvePnt, x, y)

    def setDemandModel(self, code, pmin, preq, pexp):
        """ Sets the type of demand model to use and its parameters. (EPANET Version 2.2)

        :param code: Type of demand model
            * 'DDA' = Demand driven analysis (in which case the
            remaining three parameter values are ignored)
            * 'PDA' = Pressure driven analysis
        :type code: str
        :param pmin: Pressure below which there is no demand
        :type pmin: float
        :param preq: Pressure required to deliver full demand
        :type preq: float
        :param pexp: Pressure exponent in demand function
        :type pexp: float
        :return: None

        Example:

        >>> d.getDemandModel().disp()                  # Print the demand model
        >>> type = 'PDA'
        >>> pmin = 0
        >>> preq = 0.1
        >>> pexp = 0.5
        >>> d.setDemandModel(type, pmin, preq, pexp)   # Sets the demand model
        >>> d.getDemandModel().to_dict()

        See also getDemandModel, setNodeBaseDemands, setNodeJunctionDemandName,
        addNodeJunctionDemand, deleteNodeJunctionDemand.
        """
        model_type = self.DEMANDMODEL.index(code)
        self.api.ENsetdemandmodel(model_type, pmin, preq, pexp)

    def setFlowUnitsAFD(self, *argv):
        """ Sets flow units to AFD(Acre-Feet per Day).

        Example:

        >>> d.setFlowUnitsAFD()   # d.setFlowUnitsAFD('NET1_AFD.inp')
        >>> d.getFlowUnits()

        See also setFlowUnitsCFS, setFlowUnitsIMGD.
        """
        self.__setFlowUnits(self.ToolkitConstants.EN_AFD, *argv)  # acre-feet per day

    def setFlowUnitsCFS(self, *argv):
        """ Sets flow units to CFS(Cubic Feet per Second).

        Example:

        >>> d.setFlowUnitsCFS()   # d.setFlowUnitsCFS('NET1_CFS.inp')
        >>> d.getFlowUnits()

        See also setFlowUnitsAFD, setFlowUnitsIMGD.
        """
        self.__setFlowUnits(self.ToolkitConstants.EN_CFS, *argv)  # cubic feet per second

    def setFlowUnitsCMD(self, *argv):
        """ Sets flow units to CMD(Cubic Meters per Day).

        Example:

        >>> d.setFlowUnitsCMD()  #  d.setFlowUnitsCMD('NET1_CMD.inp')
        >>> d.getFlowUnits()

        See also setFlowUnitsMLD, setFlowUnitsCMH.
        """
        self.__setFlowUnits(self.ToolkitConstants.EN_CMD, *argv)  # cubic meters per day

    def setFlowUnitsCMH(self, *argv):
        """ Sets flow units to CMH(Cubic Meters per Hour).

        Example:

        >>> d.setFlowUnitsCMH()   # d.setFlowUnitsCMH('NET1_CMH.inp')
        >>> d.getFlowUnits()

        See also setFlowUnitsMLD, setFlowUnitsCMD.
        """
        self.__setFlowUnits(self.ToolkitConstants.EN_CMH, *argv)  # cubic meters per hour

    def setFlowUnitsGPM(self, *argv):
        """ Sets flow units to GPM(Gallons Per Minute).

        Example:

        >>> d.setFlowUnitsGPM()   # d.setFlowUnitsGPM('NET1_GPM.inp')
        >>> d.getFlowUnits()

        See also setFlowUnitsLPS, setFlowUnitsMGD.
        """
        self.__setFlowUnits(self.ToolkitConstants.EN_GPM, *argv)  # gallons per minute

    def setFlowUnitsIMGD(self, *argv):
        """ Sets flow units to IMGD(Imperial Million Gallons per Day).

        Example:

        >>> d.setFlowUnitsIMGD()   # d.setFlowUnitsIMGD('NET1_IMGD.inp')
        >>> d.getFlowUnits()

        See also setFlowUnitsMGD, setFlowUnitsCFS.
        """
        self.__setFlowUnits(self.ToolkitConstants.EN_IMGD, *argv)  # imperial mgd

    def setFlowUnitsLPM(self, *argv):
        """ Sets flow units to LPM(Liters Per Minute).

        Example:

        >>> d.setFlowUnitsLPM()   #  d.setFlowUnitsLPM('NET1_LPM.inp')
        >>> d.getFlowUnits()

        See also setFlowUnitsAFD, setFlowUnitsMLD.
        """
        self.__setFlowUnits(self.ToolkitConstants.EN_LPM, *argv)  # liters per minute

    def setFlowUnitsLPS(self, *argv):
        """ Sets flow units to LPS(Liters Per Second).

        Example:

        >>> d.setFlowUnitsLPS()   #  d.setFlowUnitsLPS('NET1_LPS.inp')
        >>> d.getFlowUnits()

        See also setFlowUnitsGPM, setFlowUnitsMGD.
        """
        self.__setFlowUnits(self.ToolkitConstants.EN_LPS, *argv)  # liters per second

    def setFlowUnitsMGD(self, *argv):
        """ Sets flow units to MGD(Million Gallons per Day).

        Example:

        >>> d.setFlowUnitsMGD()   #  d.setFlowUnitsMGD('NET1_MGD.inp')
        >>> d.getFlowUnits()

        See also setFlowUnitsGPM, setFlowUnitsLPS.
        """
        self.__setFlowUnits(self.ToolkitConstants.EN_MGD, *argv)  # million gallons per day

    def setFlowUnitsMLD(self, *argv):
        """ Sets flow units to MLD(Million Liters per Day).

        Example:

        >>> d.setFlowUnitsMLD()   #  d.setFlowUnitsMLD('NET1_MLD.inp')
        >>> d.getFlowUnits()

        See also setFlowUnitsLPM, setFlowUnitsCMH.
        """
        self.__setFlowUnits(self.ToolkitConstants.EN_MLD, *argv)  # million liters per day

    def setLinkBulkReactionCoeff(self, value, *argv):
        """ Sets the value of bulk chemical reaction coefficient.

        Example 1:

        >>> index_pipe = 1
        >>> d.getLinkBulkReactionCoeff(index_pipe)              # Retrieves the bulk chemical reaction coefficient of the 1st link
        >>> coeff = 0
        >>> d.setLinkBulkReactionCoeff(index_pipe, coeff)       # Sets the bulk chemical reaction coefficient of the 1st link
        >>> d.getLinkBulkReactionCoeff(index_pipe)

        Example 2:

        >>> coeffs = d.getLinkBulkReactionCoeff()               # Retrieves the bulk chemical reaction coefficients of all links
        >>> coeffs_new = [0 for i in coeffs]
        >>> d.setLinkBulkReactionCoeff(coeffs_new)              # Sets the bulk chemical reaction coefficient of all links
        >>> d.getLinkBulkReactionCoeff()

        See also getLinkBulkReactionCoeff, setLinkRoughnessCoeff,
        setLinkPipeData, addLink, deleteLink.
        """
        self.__setEval('ENsetlinkvalue', 'KBULK', 'LINK', value, *argv)

    def setLinkComment(self, value, *argv):
        """ Sets the comment string assigned to the link object.

        Example 1:

        >>> linkIndex = 1
        >>> d.getLinkComment(linkIndex)
        >>> comment = 'This is a link'
        >>> d.setLinkComment(linkIndex, comment)   # Sets a comment to the 1st link
        >>> d.getLinkComment(linkIndex)

        Example 2:

        >>> linkIndex = [1, 2]
        >>> d.getLinkComment(linkIndex)
        >>> comment = ['This is link 1', 'This is link 2']
        >>> d.setLinkComment(linkIndex, comment)   # Sets comments to the first 2 links
        >>> d.getLinkComment(linkIndex)

        See also getLinkComment, setLinkNameID, setLinkPipeData.
        """
        if len(argv) == 0:
            lIndices = list(range(1,self.getLinkCount()+1))
        else:
            lIndices = value
            value = argv[0]
        self.__addComment(self.ToolkitConstants.EN_LINK, lIndices, value)

    def setLinkDiameter(self, value, *argv):
        """ Sets the values of diameters.

        Example 1:

        >>> d.getLinkDiameter()                           # Retrieves the diameters of all links
        >>> index_pipe = 1
        >>> diameter = 20
        >>> d.setLinkDiameter(index_pipe, diameter)       # Sets the diameter of the 1st pipe
        >>> d.getLinkDiameter(index_pipe)

        Example 2:

        >>> index_pipes = [1, 2]
        >>> diameters = [20, 25]
        >>> d.setLinkDiameter(index_pipes, diameters)     # Sets the diameters of the first 2 pipes
        >>> d.getLinkDiameter(index_pipes)

        Example 3:

        >>> diameters = d.getLinkDiameter()
        >>> diameters = diameters * 1.5
        >>> d.setLinkDiameter(diameters)                  # Sets the diameters of all the links
        >>> d.getLinkDiameter()

        See also setLinkPipeData, setLinkLength, setLinkBulkReactionCoeff, setLinkTypePipe.
        """
        self.__setEval('ENsetlinkvalue', 'DIAMETER', 'LINK', value, *argv)

    def setLinkInitialSetting(self, value, *argv):
        """ Sets the values of initial settings, roughness for pipes or initial speed for pumps or initial setting for valves.

        Example 1:

        >>> index_pipe = 1
        >>> d.getLinkInitialSetting(index_pipe)                 # Retrieves the initial setting of the 1st link
        >>> setting = 80
        >>> d.setLinkInitialSetting(index_pipe, setting)        # Sets the initial setting of the 1st link
        >>> d.getLinkInitialSetting(index_pipe)

        Example 2:

        >>> settings = d.getLinkInitialSetting()                # Retrieves the initial setting of all links
        >>> settings_new = settings + 140
        >>> d.setLinkInitialSetting(settings_new)               # Sets the initial setting of all links
        >>> d.getLinkInitialSetting()

        See also getLinkInitialSetting, setLinkInitialStatus, setLinkRoughnessCoeff,
        setLinkPipeData, addLink, deleteLink.
        """
        self.__setEval('ENsetlinkvalue', 'INITSETTING', 'LINK', value, *argv)

    def setLinkInitialStatus(self, value, *argv):
        """ Sets the values of initial status.

        Note: Cannot set status for a check valve

        Example 1:

        >>> index_pipe = 1
        >>> d.getLinkInitialStatus(index_pipe)                # Retrieves the initial status of the 1st link
        >>> status = 0
        >>> d.setLinkInitialStatus(index_pipe, status)        # Sets the initial status of the 1st link
        >>> d.getLinkInitialStatus(index_pipe)

        Example 2:

        >>> statuses = d.getLinkInitialStatus()                 # Retrieves the initial status of all links
        >>> statuses_new = np.zeros(len(statuses))
        >>> d.setLinkInitialStatus(statuses_new)                # Sets the initial status of all links
        >>> d.getLinkInitialStatus()

        See also getLinkInitialStatus, setLinkInitialSetting, setLinkDiameter,
        setLinkPipeData, addLink, deleteLink.
        """
        self.__setEval('ENsetlinkvalue', 'INITSTATUS', 'LINK', value, *argv)

    def setLinkLength(self, value, *argv):
        """ Sets the values of lengths.

        Example 1:

        >>> index_pipe = 1
        >>> d.getLinkLength(index_pipe)                   # Retrieves the length of the 1st link
        >>> length_pipe = 100
        >>> d.setLinkLength(index_pipe, length_pipe)      # Sets the length of the 1st link
        >>> d.getLinkLength(index_pipe)

        Example 2:

        >>> lengths = d.getLinkLength()                   # Retrieves the lengths of all the links
        >>> lengths_new = [i * 1.5 for i in lengths]
        >>> d.setLinkLength(lengths_new)                  # Sets the new lengths of all links
        >>> d.getLinkLength()

        See also getLinkLength, setLinkDiameter, setLinkMinorLossCoeff,
        setLinkPipeData, addLink, deleteLink.
        """
        self.__setEval('ENsetlinkvalue', 'LENGTH', 'LINK', value, *argv)

    def setLinkMinorLossCoeff(self, value, *argv):
        """ Sets the values of minor loss coefficient.

        Example 1:

        >>> index_pipe = 1
        >>> d.getLinkMinorLossCoeff(index_pipe)               # Retrieves the minor loss coefficient of the 1st link
        >>> coeff = 105
        >>> d.setLinkMinorLossCoeff(index_pipe, coeff)        # Sets the minor loss coefficient of the 1st link
        >>> d.getLinkMinorLossCoeff(index_pipe)

        Example 2:

        >>> coeffs = d.getLinkMinorLossCoeff()                # Retrieves the minor loss coefficients of all the links
        >>> coeffs_new = coeffs + 0.2
        >>> d.setLinkMinorLossCoeff(coeffs_new)               # Sets the minor loss coefficient of all links
        >>> d.getLinkMinorLossCoeff()

        See also getLinkMinorLossCoeff, setLinkDiameter, setLinkRoughnessCoeff,
        setLinkPipeData, addLink, deleteLink.
        """
        self.__setEval('ENsetlinkvalue', 'MINORLOSS', 'LINK', value, *argv)

    def setLinkNameID(self, value, *argv):
        """ Sets the ID name for links.

        Example 1:

        >>> index_pipe = 1
        >>> d.getLinkNameID(index_pipe)         # Retrieves the ID of the 1st link
        >>> linkID = 'New_ID'                   # ID selected without a space in between the letters
        >>> d.setLinkNameID(index_pipe, linkID) # Sets the ID name of the 1st link
        >>> d.getLinkNameID(index_pipe)

        Example 2: (the size of the cell must equal to the number of links)

        >>> IDs = ['1', '2', '3', '4']          # Select the IDS of the first four links
        >>> d.setLinkNameID(IDs)                # Sets the ID names of the first four links
        >>> d.getLinkNameID()

        See also getLinkNameID, setLinkComment, setLinkDiameter,
        setLinkPipeData, addLink, deleteLink.
        """
        if len(argv) == 1:
            indices = value
            value = argv[0]
        else:
            indices = self.__getlinkIndices()
        if isList(indices):
            for i in value:
                self.api.ENsetlinkid(indices[value.index(i)], i)
        else:
            self.api.ENsetlinkid(indices, value)

    def setLinkNodesIndex(self, linkIndex, startNode, endNode):
        """ Sets the indexes of a link's start- and end-nodes. (EPANET Version 2.2)

        Example 1: Sets to the 1st link the start-node index = 2 and end-node index = 3

        >>> d.getLinkNodesIndex()   # Retrieves the indexes of the from/to nodes of all links
        >>> linkIndex = 1
        >>> startNode = 2
        >>> endNode   = 3
        >>> d.setLinkNodesIndex(linkIndex, startNode, endNode)
        >>> d.getLinkNodesIndex()

        Example 2: Sets to the 1st link the start-node index = 2 and end-node index = 3
        and to 2nd link the start-node index = 4 and end-node index = 5.

        >>> linkIndex = [1, 2]
        >>> startNode = [2, 4]
        >>> endNode   = [3, 5]
        >>> d.setLinkNodesIndex(linkIndex, startNode, endNode)
        >>> d.getLinkNodesIndex()

        See also getLinkNodesIndex, setLinkDiameter, setLinkLength,
        setLinkNameID, setLinkComment.
        """
        if isList(linkIndex):
            for i in range(len(linkIndex)):
                self.api.ENsetlinknodes(linkIndex[i], startNode[i], endNode[i])
        else:
            self.api.ENsetlinknodes(linkIndex, startNode, endNode)

    def setLinkPipeData(self, Index, Length, Diameter, RoughnessCoeff, MinorLossCoeff):
        """ Sets a group of properties for a pipe. (EPANET Version 2.2)

        :param Index: Pipe Index
        :type Index: int
        :param Length: Pipe length
        :type Length: float
        :param Diameter: Pipe diameter
        :type Diameter: float
        :param RoughnessCoeff: Pipe roughness coefficient
        :type RoughnessCoeff: float
        :param MinorLossCoeff: Pipe minor loss coefficient
        :type MinorLossCoeff: float
        :return: None

        Example: Sets to the 1st pipe the following properties.

        >>> pipeIndex = 1
        >>> length = 1000
        >>> diameter = 20
        >>> RoughnessCoeff = 110
        >>> MinorLossCoeff = 0.2
        >>> d.getLinksInfo()    # Retrieves all link info
        >>> d.setLinkPipeData(pipeIndex, length, diameter, RoughnessCoeff, MinorLossCoeff)
        >>> d.getLinksInfo()

        Example 2: Sets to the 1st and 2nd pipe the following properties.

        >>> pipeIndex = [1, 2]
        >>> length = [1000, 1500]
        >>> diameter = [20, 23]
        >>> RoughnessCoeff = [110, 115]
        >>> MinorLossCoeff = [0.2, 0.3]
        >>> d.getLinksInfo().disp()    # Retrieves all link info
        >>> d.setLinkPipeData(pipeIndex, length, diameter, RoughnessCoeff, MinorLossCoeff)
        >>> d.getLinksInfo().to_dict()

        See also getLinksInfo, setLinkComment, setLinkDiameter,
        setLinkLength, setLinkStatus, setNodeTankData.
        """
        if not isList(Index):
            Index = [Index]
        if not isList(Length):
            Length = [Length]
        if not isList(Diameter):
            Diameter = [Diameter]
        if not isList(RoughnessCoeff):
            RoughnessCoeff = [RoughnessCoeff]
        if not isList(MinorLossCoeff):
            MinorLossCoeff = [MinorLossCoeff]
        for i in range(len(Index)):
            self.api.ENsetpipedata(Index[i], Length[i], Diameter[i], RoughnessCoeff[i], MinorLossCoeff[i])

    def setLinkPumpECost(self, value, *argv):
        """ Sets the pump average energy price. (EPANET Version 2.2)

        The examples are based on d = epanet('Net3_trace.inp')

        Example 1:

        >>> d.getLinkPumpECost()                           # Retrieves the pump average energy price of all pumps
        >>> d.setLinkPumpECost(0.10)                       # Sets the pump average energy price = 0.10 to every pump
        >>> d.getLinkPumpECost()

        Example 2: (The input array must have a length equal to the number of pumps).

        >>> d.setLinkPumpECost([0.10, 0.12])               # Sets the pump average energy price = 0.10 and 0.12 to the 2 pumps
        >>> d.getLinkPumpECost()

        Example 3:

        >>> d.setLinkPumpECost(1, 0.10)                    # Sets the pump average energy price = 0.10 to the 1st pump
        >>> d.getLinkPumpECost()

        Example 4:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.setLinkPumpECost(pumpIndex, 0.10)            # Sets the pump average energy price = 0.10 to the pumps with index 118 and 119
        >>> d.getLinkPumpECost()

        Example 5:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.setLinkPumpECost(pumpIndex, [0.10, 0.12])    # Sets the pump average energy price = 0.10 and 0.12 to the pumps with index 118 and 119 respectively
        >>> d.getLinkPumpECost()

        See also getLinkPumpECost, setLinkPumpPower, setLinkPumpHCurve,
        setLinkPumpECurve, setLinkPumpEPat.
        """
        self.__setEvalLinkNode('ENsetlinkvalue', 'PUMP_ECOST', 'PUMP', value, *argv)

    def setLinkPumpECurve(self, value, *argv):
        """ Sets the pump efficiency v. flow curve index. (EPANET Version 2.2)

        The examples are based on d = epanet('Net3_trace.inp')

        Example 1:

        >>> d.getLinkPumpECurve()                    # Retrieves the pump efficiency v. flow curve index of all pumps
        >>> d.setLinkPumpECurve(1)                   # Sets the pump efficiency v. flow curve index = 1 to every pump
        >>> d.getLinkPumpECurve()

        Example 2: The input array must have a length equal to the number of pumps.

        >>> d.setLinkPumpECurve([1, 2])              # Sets the pump efficiency v. flow curve index = 1 and 2 to the 2 pumps
        >>> d.getLinkPumpECurve()

        Example 3:

        >>> d.setLinkPumpECurve(1, 2)                # Sets the pump efficiency v. flow curve index = 2 to the 1st pump
        >>> d.getLinkPumpECurve()

        Example 4:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.setLinkPumpECurve(pumpIndex, 1)        # Sets the pump efficiency v. flow curve index = 1 to the pumps with index 118 and 119
        >>> d.getLinkPumpECurve()

        Example 5:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.setLinkPumpECurve(pumpIndex,[1, 2])    # Sets the pump efficiency v. flow curve index = 1 and 2 to the pumps with index 118 and 119 respectively
        >>> d.getLinkPumpECurve()

        See also getLinkPumpECurve, setLinkPumpPower, setLinkPumpHCurve, setLinkPumpECost, setLinkPumpEPat.
        """
        self.__setEvalLinkNode('ENsetlinkvalue', 'PUMP_ECURVE', 'PUMP', value, *argv)

    def setLinkPumpEPat(self, value, *argv):
        """ Sets the pump energy price time pattern index. (EPANET Version 2.2)

        The examples are based on d = epanet('Net3_trace.inp')

        Example 1:

        >>> d.getLinkPumpEPat()                    # Retrieves the pump energy price time pattern index of all pumps
        >>> d.setLinkPumpEPat(1)                   # Sets the pump energy price time pattern index = 1 to every pump
        >>> d.getLinkPumpEPat()

        Example 2: (The input array must have a length equal to the number of pumps).

        >>> d.setLinkPumpEPat([1, 2])              # Sets the pump energy price time pattern index = 1 and 2 to the 2 pumps
        >>> d.getLinkPumpEPat()

        Example 3:

        >>> d.setLinkPumpEPat(1, 2)                # Sets the pump energy price time pattern index = 2 to the 1st pump
        >>> d.getLinkPumpEPat()

        Example 4:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.setLinkPumpEPat(pumpIndex, 1)        # Sets the pump energy price time pattern index = 1 to the pumps with index 118 and 119
        >>> d.getLinkPumpEPat()

        Example 5:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.setLinkPumpEPat(pumpIndex,[1, 2])    # Sets the pump energy price time pattern index = 1 and 2 to the pumps with index 118 and 119 respectively
        >>> d.getLinkPumpEPat()

        See also getLinkPumpEPat, setLinkPumpPower, setLinkPumpHCurve, setLinkPumpECurve, setLinkPumpECost.
        """
        self.__setEvalLinkNode('ENsetlinkvalue', 'PUMP_EPAT', 'PUMP', value, *argv)

    def setLinkPumpHCurve(self, value, *argv):
        """ Sets the pump head v. flow curve index. (EPANET Version 2.2)

        The examples are based on d = epanet('Net3_trace.inp')

        Example 1:

        >>> d.getLinkPumpHCurve()                    # Retrieves the pump head v. flow curve index of all pumps
        >>> d.setLinkPumpHCurve(1)                   # Sets the pump head v. flow curve index = 1 to every pump
        >>> d.getLinkPumpHCurve()

        Example 2: (The input array must have a length equal to the number of pumps

        >>> d.setLinkPumpHCurve([1, 2])              # Sets the pump head v. flow curve index = 1 and 2 to the 2 pumps
        >>> d.getLinkPumpHCurve()

        Example 3:

        >>> d.setLinkPumpHCurve(1, 2)                # Sets the pump head v. flow curve index = 2 to the 1st pump
        >>> d.getLinkPumpHCurve()

        Example 4:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.setLinkPumpHCurve(pumpIndex, 1)        # Sets the pump head v. flow curve index = 1 to the pumps with index 118 and 119
        >>> d.getLinkPumpHCurve()

        Example 5:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.setLinkPumpHCurve(pumpIndex, [1, 2])   # Sets the pump head v. flow curve index = 1 and 2 to the pumps with index 118 and 119 respectively
        >>> d.getLinkPumpHCurve()

        See also getLinkPumpHCurve, setLinkPumpPower, setLinkPumpECurve, setLinkPumpECost, setLinkPumpEPat.
        """
        self.__setEvalLinkNode('ENsetlinkvalue', 'PUMP_HCURVE', 'PUMP', value, *argv)

    def setLinkPumpHeadCurveIndex(self, value, *argv):
        """ Sets the curves index for pumps index

        >>> d.getLinkPumpHeadCurveIndex()  
        >>> pumpIndex = d.getLinkPumpIndex(1)  
        >>> curveIndex = d.getLinkCurveIndex(2)
        >>> d.setLinkPumpHeadCurveIndex(pumpIndex, curveIndex)
        >>> d.getLinkPumpHeadCurveIndex()

        See also setLinkPumpPatternIndex, getLinkPumpPower, setLinkPumpHCurve,
        setLinkPumpECurve, setLinkPumpECost.
        """
        if len(argv) == 1:
            indices = value
            value = argv[0]
        else:
            indices = self.getNodeIndices(*argv)
        if isList(indices):
            j = 0
            for i in indices:
                self.api.ENsetheadcurveindex(i, value[j])
                j += 1
        else:
            self.api.ENsetheadcurveindex(indices, value)

    def setLinkPumpPatternIndex(self, value, *argv):
        """ Sets the pump speed time pattern index. (EPANET Version 2.2)

        The examples are based on d = epanet('Net3_trace.inp')

        Example 1:

        >>> d.getLinkPumpPatternIndex()                    # Retrieves the pump speed time pattern index of all pumps
        >>> d.setLinkPumpPatternIndex(1)                   # Sets the speed time pattern index = 1 to every pump
        >>> d.getLinkPumpPatternIndex()

        Example 2: The input array must have a length equal to the number of pumps.

        >>> d.setLinkPumpPatternIndex([1, 2])              # Sets the pump speed time pattern index = 1 and 2 to the 2 pumps
        >>> d.getLinkPumpPatternIndex()

        Example 3:

        >>> d.setLinkPumpPatternIndex(1, 2)                # Sets the pump speed time pattern index = 2 to the 1st pump
        >>> d.getLinkPumpPatternIndex()

        Example 4:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.setLinkPumpPatternIndex(pumpIndex, 1)        # Sets the pump speed time pattern index = 1 to the pumps with index 118 and 119
        >>> d.getLinkPumpPatternIndex()

        Example 5:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.setLinkPumpPatternIndex(pumpIndex, [1, 2])    # Sets the pump speed time pattern index = 1 and 2 to the pumps with index 118 and 119 respectively
        >>> d.getLinkPumpPatternIndex()

        Example 6: To remove the pattern index from the pumps you can use input 0.

        >>> pumpIndex = d.getLinkPumpIndex()
       	>>> d.setLinkPumpPatternIndex(pumpIndex, 0)

        See also getLinkPumpPatternIndex, setLinkPumpPower, setLinkPumpHCurve,
        setLinkPumpECurve, setLinkPumpECost.
        """
        self.__setEvalLinkNode('ENsetlinkvalue', 'LINKPATTERN', 'PUMP', value, *argv)

    def setLinkPumpPower(self, value, *argv):
        """ Sets the power for pumps. (EPANET Version 2.2)

        The examples are based on d = epanet('Net3_trace.inp')

        Example 1:

        >>> d.getLinkPumpPower()                      # Retrieves the power of all pumps
        >>> d.setLinkPumpPower(10)                    # Sets the pump power = 10 to every pump
        >>> d.getLinkPumpPower()

        Example 2: (The input array must have a length equal to the number of pumps).

        >>> d.setLinkPumpPower([10, 15])              # Sets the pump power = 10 and 15 to the 2 pumps
        >>> d.getLinkPumpPower()

        Example 3:

        >>> d.setLinkPumpPower(1, 10)                 # Sets the pump power = 10 to the 1st pump
        >>> d.getLinkPumpPower()

        Example 4:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.setLinkPumpPower(pumpIndex, 10)         # Sets the pump power = 10 to the pumps with index 118 and 119
        >>> d.getLinkPumpPower()

        Example 5:

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.setLinkPumpPower(pumpIndex, [10, 15])   # Sets the pump power = 10 and 15 to the pumps with index 118 and 119 respectively
        >>> d.getLinkPumpPower()

        See also getLinkPumpPower, setLinkPumpHCurve, setLinkPumpECurve, setLinkPumpECost, setLinkPumpEPat.
        """
        self.__setEvalLinkNode('ENsetlinkvalue', 'PUMP_POWER', 'PUMP', value, *argv)

    def setLinkRoughnessCoeff(self, value, *argv):
        """ Sets the values of roughness coefficient.

        Example 1:

        >>> index_pipe = 1
        >>> d.getLinkRoughnessCoeff(index_pipe)               # Retrieves the roughness coefficient of the 1st link
        >>> coeff = 105
        >>> d.setLinkRoughnessCoeff(index_pipe, coeff)        # Sets the roughness coefficient of the 1st link
        >>> d.getLinkRoughnessCoeff(index_pipe)

        Example 2:

        >>> coeffs = d.getLinkRoughnessCoeff()                  # Retrieves the roughness coefficients of all the links
        >>> coeffs_new = coeffs + 10
        >>> d.setLinkRoughnessCoeff(coeffs_new)               # Sets the roughness coefficient of all links
        >>> d.getLinkRoughnessCoeff()

        See also getLinkRoughnessCoeff, setLinkDiameter, setLinkMinorLossCoeff, setLinkPipeData, addLink, deleteLink.
        """
        self.__setEval('ENsetlinkvalue', 'ROUGHNESS', 'LINK', value, *argv)

    def setLinkSettings(self, value, *argv):
        """Sets the values of current settings, roughness for pipes or initial speed for pumps or initial setting for valves.

        Example 1:

        >>> index_pipe = 1
        >>> d.getLinkSettings(index_pipe)                 # Retrieves the current setting of the 1st link
        >>> setting = 80
        >>> d.setLinkSettings(index_pipe, setting)        # Sets the current setting of the 1st link
        >>> d.getLinkSettings(index_pipe)

        Example 2:

        >>> settings = d.getLinkSettings()                # Retrieves the current setting of all links
        >>> settings_new = [i + 40 for i in settings]
        >>> d.setLinkSettings(settings_new)               # Sets the current setting of all links
        >>> d.getLinkSettings()

        See also getLinkSettings, setLinkStatus, setLinkRoughnessCoeff,
                 setLinkPipeData, addLink, deleteLink.
        """
        self.__setEval('ENsetlinkvalue', 'SETTING', 'LINK', value, *argv)

    def setLinkStatus(self, value, *argv):
        """ Sets the values of current status for links.

        Note: Cannot set status for a check valve

        Example 1:

        >>> index_pipe = 1
        >>> d.getLinkStatus(index_pipe)                  # Retrieves the current status of the 1st link
        >>> status = 1
        >>> d.setLinkStatus(index_pipe, status)          # Sets the current status of the 1st link
        >>> d.getLinkStatus(index_pipe)

        Example 2:

        >>> statuses = d.getLinkStatus()                 # Retrieves the current status of all links
        >>> statuses_new = [0 for i in statuses]
        >>> d.setLinkStatus(statuses_new)                # Sets the current status of all links
        >>> d.getLinkStatus()

        See also getLinkStatus, setLinkInitialStatus, setLinkDiameter,
        setLinkPipeData, addLink, deleteLink.
        """
        self.__setEval('ENsetlinkvalue', 'STATUS', 'LINK', value, *argv)

    def setLinkTypePipe(self, Id, *argv):
        """ Sets the link type pipe for a specified link.

        Note:
             * condition = 0 | if is EN_UNCONDITIONAL: Delete all controls that contain object
             * condition = 1 | if is EN_CONDITIONAL: Cancel object type change if contained in controls

        Default condition is 0.

        Example 1:

        >>> d.getLinkType()
        >>> linkid = d.getLinkPumpNameID(1)
        >>> index = d.setLinkTypePipe(linkid)            # Changes the 1st pump to pipe given it's ID
        >>> d.getLinkType(index)

        Example 2:

        >>> linkid = d.getLinkPumpNameID(1)
        >>> condition = 1
        >>> index = d.setLinkTypePipe(linkid, condition) # Changes the 1st pump to pipe given it's ID and a condition (if possible)
        >>> d.getLinkType(index)

        See also getLinkType, getLinkPumpNameID, setLinkTypePipeCV, setLinkTypePump, setLinkTypeValveFCV.
        """
        condition = 0  # default
        if len(argv) == 1:
            condition = argv[0]
        index = self.__checkLinkIfString(Id)
        return self.api.ENsetlinktype(index, self.ToolkitConstants.EN_PIPE, condition)

    def setLinkTypePipeCV(self, Id, *argv):
        """ Sets the link type cvpipe(pipe with check valve) for a specified link.

        Note:
            * condition = 0 | if is EN_UNCONDITIONAL: Delete all controls that contain object
            * condition = 1 | if is EN_CONDITIONAL: Cancel object type change if contained in controls

        Default condition is 0.

        Example 1:

        >>> d.getLinkType(1)                              # Retrieves the type of the 1st link
        >>> linkid = d.getLinkPipeNameID(1)               # Retrieves the ID of the 1t pipe
        >>> index = d.setLinkTypePipeCV(linkid)           # Changes the 1st pipe to cvpipe given it's ID
        >>> d.getLinkType(index)

        Example 2:

        >>> linkid = d.getLinkPipeNameID(1)
        >>> condition = 1
        >>> index = d.setLinkTypePipeCV(linkid, condition)  # Changes the 1st pipe to cvpipe given it's ID and a condition (if possible)
        >>> d.getLinkType(index)

        See also getLinkType, getLinkPipeNameID, setLinkTypePipe, setLinkTypePump, setLinkTypeValveFCV.
        """
        condition = 0  # default
        if len(argv) == 1:
            condition = argv[0]
        index = self.__checkLinkIfString(Id)
        return self.api.ENsetlinktype(index, self.ToolkitConstants.EN_CVPIPE, condition)

    def setLinkTypePump(self, Id, *argv):
        """ Sets the link type pump for a specified link.

        Note:
            * condition = 0 | if is EN_UNCONDITIONAL: Delete all controls that contain object
            * condition = 1 | if is EN_CONDITIONAL: Cancel object type change if contained in controls

        Default condition is 0.

        Example 1:

        >>> d.getLinkType(1)                            # Retrieves the type of the 1st link
        >>> linkid = d.getLinkPipeNameID(1)             # Retrieves the ID of the 1t pipe
        >>> index = d.setLinkTypePump(linkid)           # Changes the 1st pipe to pump given it's ID
        >>> d.getLinkType(index)

        Example 2:

        >>> linkid = d.getLinkPipeNameID(1)
        >>> condition = 1
        >>> index = d.setLinkTypePump(linkid, condition)   # Changes the 1st pipe to pump given it's ID and a condition (if possible)
        >>> d.getLinkType(index)

        See also getLinkType, getLinkPipeNameID, setLinkTypePipe, setLinkTypePipeCV, setLinkTypeValveFCV.
        """
        condition = 0  # default
        if len(argv) == 1:
            condition = argv[0]
        index = self.__checkLinkIfString(Id)
        return self.api.ENsetlinktype(index, self.ToolkitConstants.EN_PUMP, condition)

    def setLinkTypeValveFCV(self, Id, *argv):
        """ Sets the link type valve FCV(flow control valve) for a specified link.

        Note:
            * condition = 0 | if is EN_UNCONDITIONAL: Delete all controls that contain object
            * condition = 1 | if is EN_CONDITIONAL: Cancel object type change if contained in controls

        Default condition is 0.

        Example 1:

        >>> d.getLinkType(1)                                    # Retrieves the type of the 1st link
        >>> linkid = d.getLinkPipeNameID(1)                     # Retrieves the ID of the 1t pipe
        >>> index = d.setLinkTypeValveFCV(linkid)               # Changes the 1st pipe to valve FCV given it's ID
        >>> d.getLinkType(index)

        Example 2:

        >>> linkid = d.getLinkPipeNameID(1)
        >>> condition = 1
        >>> index = d.setLinkTypeValveFCV(linkid, condition)    # Changes the 1st pipe to valve FCV given it's ID and a condition (if possible)
        >>> d.getLinkType(index)

        See also getLinkType, getLinkPipeNameID, setLinkTypePipe, setLinkTypePump, setLinkTypeValveGPV.
        """
        condition = 0  # default
        if len(argv) == 1:
            condition = argv[0]
        index = self.__checkLinkIfString(Id)
        return self.api.ENsetlinktype(index, self.ToolkitConstants.EN_FCV, condition)

    def setLinkTypeValveGPV(self, Id, *argv):
        """ Sets the link type valve GPV(general purpose valve) for a specified link.

        Note:
            * condition = 0 | if is EN_UNCONDITIONAL: Delete all controls that contain object
            * condition = 1 | if is EN_CONDITIONAL: Cancel object type change if contained in controls

        Default condition is 0.

        Example 1:

        >>> d.getLinkType(1)                                    # Retrieves the type of the 1st link
        >>> linkid = d.getLinkPipeNameID(1)                     # Retrieves the ID of the 1t pipe
        >>> index = d.setLinkTypeValveGPV(linkid)               # Changes the 1st pipe to valve GPV given it's ID
        >>> d.getLinkType(index)

        Example 2:

        >>> linkid = d.getLinkPipeNameID(1)
        >>> condition = 1
        >>> index = d.setLinkTypeValveGPV(linkid, condition)    # Changes the 1st pipe to valve GPV given it's ID and a condition (if possible)
        >>> d.getLinkType(index)

        See also getLinkType, getLinkPipeNameID, setLinkTypePipe,
        setLinkTypePump, setLinkTypeValveFCV.
        """
        condition = 0  # default
        if len(argv) == 1:
            condition = argv[0]
        index = self.__checkLinkIfString(Id)
        return self.api.ENsetlinktype(index, self.ToolkitConstants.EN_GPV, condition)

    def setLinkTypeValvePBV(self, Id, *argv):
        """ Sets the link type valve PBV(pressure breaker valve) for a specified link.

        Note:
            * condition = 0 | if is EN_UNCONDITIONAL: Delete all controls that contain object
            * condition = 1 | if is EN_CONDITIONAL: Cancel object type change if contained in controls

        Default condition is 0.

        Example 1:

        >>> d.getLinkType(1)                                    # Retrieves the type of the 1st link
        >>> linkid = d.getLinkPipeNameID(1)                     # Retrieves the ID of the 1t pipe
        >>> index = d.setLinkTypeValvePBV(linkid)               # Changes the 1st pipe to valve PBV given it's ID
        >>> d.getLinkType(index)

        Example 2:

        >>> linkid = d.getLinkPipeNameID(1)
        >>> condition = 1
        >>> index = d.setLinkTypeValvePBV(linkid, condition)    # Changes the 1st pipe to valve PBV given it's ID and a condition (if possible)
        >>> d.getLinkType(index)

        See also getLinkType, getLinkPipeNameID, setLinkTypePipe, setLinkTypePump, setLinkTypeValvePRV.
        """
        condition = 0  # default
        if len(argv) == 1:
            condition = argv[0]
        index = self.__checkLinkIfString(Id)
        return self.api.ENsetlinktype(index, self.ToolkitConstants.EN_PBV, condition)

    def setLinkTypeValvePRV(self, Id, *argv):
        """ Sets the link type valve PRV(pressure reducing valve) for a specified link.

        Note:
            * condition = 0 | if is EN_UNCONDITIONAL: Delete all controls that contain object
            * condition = 1 | if is EN_CONDITIONAL: Cancel object type change if contained in controls

        Default condition is 0.

        Example 1:

        >>> d.getLinkType(1)                                    # Retrieves the type of the 1st link
        >>> linkid = d.getLinkPipeNameID(1)                     # Retrieves the ID of the 1t pipe
        >>> index = d.setLinkTypeValvePRV(linkid)               # Changes the 1st pipe to valve PRV given it's ID
        >>> d.getLinkType(index)

        Example 2:

        >>> linkid = d.getLinkPipeNameID(1)
        >>> condition = 1
        >>> index = d.setLinkTypeValvePRV(linkid, condition)    # Changes the 1st pipe to valve PRV given it's ID and a condition (if possible)
        >>> d.getLinkType(index)

        See also getLinkType, getLinkPipeNameID, setLinkTypePipe, setLinkTypePump, setLinkTypeValvePSV.
        """
        condition = 0  # default
        if len(argv) == 1:
            condition = argv[0]
        index = self.__checkLinkIfString(Id)
        return self.api.ENsetlinktype(index, self.ToolkitConstants.EN_PRV, condition)

    def setLinkTypeValvePSV(self, Id, *argv):
        """ Sets the link type valve PSV(pressure sustaining valve) for a specified link.

        Note:
            * condition = 0 | if is EN_UNCONDITIONAL: Delete all controls that contain object
            * condition = 1 | if is EN_CONDITIONAL: Cancel object type change if contained in controls

        Default condition is 0.

        Example 1:

        >>> d.getLinkType(1)                                    # Retrieves the type of the 1st link
        >>> linkid = d.getLinkPipeNameID(1)                     # Retrieves the ID of the 1t pipe
        >>> index = d.setLinkTypeValvePSV(linkid)               # Changes the 1st pipe to valve PSV given it's ID
        >>> d.getLinkType(index)

        Example 2:

        >>> linkid = d.getLinkPipeNameID(1)
        >>> condition = 1
        >>> index = d.setLinkTypeValvePSV(linkid, condition)    # Changes the 1st pipe to valve PSV given it's ID and a condition (if possible)
        >>> d.getLinkType(index)

        See also getLinkType, getLinkPipeNameID, setLinkTypePipe, setLinkTypePump, setLinkTypeValvePBV.
        """
        condition = 0  # default
        if len(argv) == 1:
            condition = argv[0]
        index = self.__checkLinkIfString(Id)
        return self.api.ENsetlinktype(index, self.ToolkitConstants.EN_PSV, condition)

    def setLinkTypeValveTCV(self, Id, *argv):
        """ Sets the link type valve TCV(throttle control valve) for a specified link.

        Note:
            * condition = 0 | if is EN_UNCONDITIONAL: Delete all controls that contain object
            * condition = 1 | if is EN_CONDITIONAL: Cancel object type change if contained in controls

        Default condition is 0.

        Example 1:

        >>> d.getLinkType(1)                                    # Retrieves the type of the 1st link
        >>> linkid = d.getLinkPipeNameID(1)                     # Retrieves the ID of the 1t pipe
        >>> index = d.setLinkTypeValveTCV(linkid)               # Changes the 1st pipe to valve TCV given it's ID
        >>> d.getLinkType(index)

        Example 2:

        >>> linkid = d.getLinkPipeNameID(1)
        >>> condition = 1
        >>> index = d.setLinkTypeValveTCV(linkid, condition)    # Changes the 1st pipe to valve TCV given it's ID and a condition (if possible)
        >>> d.getLinkType(index)

        See also getLinkType, getLinkPipeNameID, setLinkTypePipe, setLinkTypePump, setLinkTypeValveGPV.
        """
        condition = 0  # default
        if len(argv) == 1:
            condition = argv[0]
        index = self.__checkLinkIfString(Id)
        return self.api.ENsetlinktype(index, self.ToolkitConstants.EN_TCV, condition)

    def setLinkVertices(self, linkID, x, y, *argv):
        """ Assigns a set of internal vertex points to a link.

        The example is based on d = epanet('Net1.inp')

        Example:

        >>> d = epanet('Net1.inp')
        >>> linkID = '10'
        >>> x = [22, 24, 28]
        >>> y = [69, 68, 69]
        >>> d.setLinkVertices(linkID, x, y)

        See also getLinkVertices, getLinkVerticesCount.
        """
        index = self.getLinkIndex(linkID)
        self.api.ENsetvertices(index, x, y, len(x))

    def setLinkWallReactionCoeff(self, value, *argv):
        """ Sets the value of wall chemical reaction coefficient.

        Example 1:

        >>> index_pipe = 1
        >>> d.getLinkWallReactionCoeff(index_pipe)               # Retrieves the wall chemical reaction coefficient of the 1st link
        >>> coeff = 0
        >>> d.setLinkWallReactionCoeff(index_pipe, coeff)        # Sets the wall chemical reaction coefficient of the 1st link
        >>> d.getLinkWallReactionCoeff(index_pipe)

        Example 2:

        >>> coeffs = d.getLinkWallReactionCoeff()                # Retrieves the wall chemical reaction coefficients of all links
        >>> coeffs_new = [0] * len(coeffs)
        >>> d.setLinkWallReactionCoeff(coeffs_new)               # Sets the wall chemical reaction coefficient of all links
        >>> d.getLinkWallReactionCoeff()

        See also getLinkWallReactionCoeff, setLinkBulkReactionCoeff, setLinkPipeData, addLink, deleteLink.
        """
        self.__setEval('ENsetlinkvalue', 'KWALL', 'LINK', value, *argv)

    def setNodeBaseDemands(self, value, *argv):
        """ Sets the values of demand for nodes.
        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> index_node = 1
        >>> d.getNodeBaseDemands()[1][index_node]                      # Retrieves the demand of the 1st node
        >>> demand = 5
        >>> d.setNodeBaseDemands(index_node, demand)                   # Sets the demand of the 1st node
        >>> d.getNodeBaseDemands()[1][index_node-1]

        Example 2:

        >>> nodeIndex = list(range(1,6))
        >>> BaseDems = d.getNodeBaseDemands()[1]
        >>> baseDems = list(np.array(BaseDems)[0:5])                   # Retrieves the demands of first 5 nodes
        >>> demands = [10, 5, 15, 20, 5]
        >>> d.setNodeBaseDemands(nodeIndex, demands)                   # Sets the demands of first 5 nodes
        >>> newBaseDems = d.getNodeBaseDemands()[1][0:5]
        >>> newbaseDems = newBaseDems

        Example 3:

        >>> demands = d.getNodeBaseDemands()[1]                        # Retrieves the demands of all nodes
        >>> demands_new = [i+15 for i in demands]
        >>> d.setNodeBaseDemands(demands_new)                          # Sets the demands of all nodes
        >>> d.getNodeBaseDemands()[1]

        If a category is not given, the default is categoryIndex = 1.

        Example 4:

        >>> d = epanet('BWSN_Network_1.inp')
        >>> nodeIndex = 121
        >>> categoryIndex = 2
        >>> d.getNodeBaseDemands()[categoryIndex][nodeIndex-1]           # Retrieves the demand of the 2nd category of the 121th node
        >>> demand = 25
        >>> d.setNodeBaseDemands(nodeIndex, categoryIndex, demand)       # Sets the demand of the 2nd category of the 121th node
        >>> d.getNodeBaseDemands()[categoryIndex][nodeIndex-1]

        Example 5:

        >>> d = epanet('BWSN_Network_1.inp')
        >>> nodeIndex = list(range(1,6))
        >>> categoryIndex = 1
        >>> baseDems = d.getNodeBaseDemands()[categoryIndex]
        >>> baseDems = baseDems[0:5]                       # Retrieves the demands of the 1st category of the first 5 nodes
        >>> demands = [10, 5, 15, 20, 5]
        >>> d.setNodeBaseDemands(nodeIndex, categoryIndex, demands)      # Sets the demands of the 1st category of the first 5 nodes
        >>> newbaseDems = d.getNodeBaseDemands()[categoryIndex]
        >>> newbaseDems = newbaseDems[0:5]

        See also getNodeBaseDemands, setNodeJunctionDemandName, setNodeDemandPatternIndex, addNodeJunction, deleteNode.
        """
        self.__setNodeDemandPattern('ENsetbasedemand', self.ToolkitConstants.EN_BASEDEMAND, value, *argv)

    def setNodeComment(self, value, *argv):
        """ Sets the comment string assigned to the node object.

        Example 1:

        >>> d.setNodeComment(1, 'This is a node')                     # Sets a comment to the 1st node
        >>> d.getNodeComment(1)

        Example 2:

        >>> d.setNodeComment([1,2], ['This is a node', 'Test comm'])  # Sets a comment to the 1st and 2nd node
        >>> d.getNodeComment([1,2])

        See also getNodeComment, getNodesInfo, setNodeNameID, setNodeCoordinates.
        """
        self.__addComment(self.ToolkitConstants.EN_NODE, value, *argv)

    def setNodeCoordinates(self, value, *argv):
        """ Sets node coordinates.

        Example 1:

        >>> nodeIndex = 1
        >>> d.getNodeCoordinates(nodeIndex)              # Retrieves the X and Y coordinates of the 1st node
        >>> coords = [0,0]
        >>> d.setNodeCoordinates(nodeIndex, coords)      # Sets the coordinates of the 1st node
        >>> d.getNodeCoordinates(nodeIndex)


        Example 2:

        >>> x_values = d.getNodeCoordinates('x')
        >>> y_values = d.getNodeCoordinates('y')
        >>> x_new = [x_values[i]+10 for i in x_values]
        >>> y_new = [y_values[i]+10 for i in y_values]
        >>> new_coords = [x_new, y_new]                     # Creates a cell array with the new coordinates
        >>> d.setNodeCoordinates(new_coords)                # Sets the coordinates of all nodes
        >>> x_values_new = d.getNodeCoordinates('x')
        >>> y_values_new = d.getNodeCoordinates('y')

        See also getNodeCoordinates, setNodeElevations, plot, addNodeJunction, addNodeTank, deleteNode.
        """
        if len(argv) == 1:
            indices = value
            value = argv[0]
        else:
            indices = self.__getNodeIndices(*argv)
        if not isList(indices):
            indices = [indices]
        if len(argv) == 0:
            for i in indices:
                self.api.ENsetcoord(i, value[0][indices.index(i)], value[1][indices.index(i)])
        else:
            value = [value]
            for i in range(len(value)):
                x = value[i][0]
                y = value[i][1]
                self.api.ENsetcoord(indices[i], x, y)

    def setNodeDemandPatternIndex(self, value, *argv):
        """ Sets the values of demand time pattern indices.

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> nodeIndex = 1
        >>> d.getNodeDemandPatternIndex()[1][nodeIndex-1]                            # Retrieves the index of the 1st category's time pattern of the 1st node
        >>> patternIndex = 2
        >>> d.setNodeDemandPatternIndex(nodeIndex, patternIndex)                     # Sets the demand time pattern index to the 1st node
        >>> d.getNodeDemandPatternIndex()[1][nodeIndex-1]

        Example 2:

        >>> nodeIndex = np.array(range(1,6))
        >>> d.getNodeDemandPatternIndex()[1][0:5]
        >>> patternIndices = [1, 3, 2, 4, 2]
        >>> d.setNodeDemandPatternIndex(nodeIndex, patternIndices)                   # Sets the demand time pattern index to the first 5 nodes
        >>> d.getNodeDemandPatternIndex()[1][0:5]

        Example 3:

        >>> patternIndices = d.getNodeDemandPatternIndex()[1]
        >>> patternIndices_new = [i+1 for i in patternIndices]
        >>> d.setNodeDemandPatternIndex(patternIndices_new)                          # Sets all primary demand time pattern indices
        >>> d.getNodeDemandPatternIndex()[1]

        If a category is not given, the default is categoryIndex = 1.

        Example 4:

        >>> nodeIndex = 121
        >>> categoryIndex = 2
        >>> d.getNodeDemandPatternIndex()[categoryIndex][nodeIndex-1]                 # Retrieves the index of the 2nd category's time pattern of the 121th node
        >>> patternIndex = 4
        >>> d.setNodeDemandPatternIndex(nodeIndex, categoryIndex, patternIndex)       # Sets the demand time pattern index of the 2nd category of the 121th node
        >>> d.getNodeDemandPatternIndex()[categoryIndex][nodeIndex-1]

        Example 5:

        >>> nodeIndex = np.array(range(1,6))
        >>> categoryIndex = 1
        >>> patDems = d.getNodeDemandPatternIndex()[categoryIndex]
        >>> patDems = list(np.array(patDems)[0:5])
        >>> patternIndices = [1, 3, 2, 4, 2]
        >>> d.setNodeDemandPatternIndex(nodeIndex, categoryIndex, patternIndices)     # Sets the demand time pattern index of the 1st category of the first 5 nodes
        >>> patDems_new = d.getNodeDemandPatternIndex()[categoryIndex][0:5]

        See also getNodeDemandPatternIndex, getNodeDemandCategoriesNumber, setNodeBaseDemands, addPattern, deletePattern.
        """
        self.__setNodeDemandPattern('ENsetdemandpattern', self.ToolkitConstants.EN_PATTERN, value, *argv)

    def setNodeElevations(self, value, *argv):
        """ Sets the values of elevation for nodes.

        Example 1:

        >>> index_node = 1
        >>> d.getNodeElevations(index_node)            # Retrieves the elevation of the 1st node
        >>> elev = 500
        >>> d.setNodeElevations(index_node, elev)      # Sets the elevation of the 1st node
        >>> d.getNodeElevations(index_node)

        Example 2:

        >>> elevs = d.getNodeElevations()               # Retrieves the elevations of all the nodes
        >>> elevs_new = elevs + 100 
        >>> d.setNodeElevations(elevs_new)              # Sets the elevations of all nodes
        >>> d.getNodeElevations()

        See also getNodeElevations, setNodeCoordinates, setNodeBaseDemands,
        setNodeJunctionData, addNodeJunction, deleteNode.
        """
        self.__setEval('ENsetnodevalue', 'ELEVATION', 'NODE', value, *argv)

    def setNodeEmitterCoeff(self, value, *argv):
        """ Sets the values of emitter coefficient for nodes.

        Example 1:

        >>> nodeset = d.getNodeEmitterCoeff()                # Retrieves the value of all nodes emmitter coefficients
        >>> nodeset[0] = 0.1                                 # First node emitter coefficient = 0.1
        >>> d.setNodeEmitterCoeff(nodeset)                   # Sets the value of all nodes emitter coefficient
        >>> d.getNodeEmitterCoeff()

        Example 2:

        >>> nodeIndex = 1
        >>> d.getNodeEmitterCoeff(nodeIndex)
        >>> emitterCoeff = 0
        >>> d.setNodeEmitterCoeff(nodeIndex, emitterCoeff)   # Sets the value of the 1st node emitter coefficient = 0
        >>> d.getNodeEmitterCoeff(nodeIndex)

        See also getNodeEmitterCoeff, setNodeBaseDemands, setNodeJunctionData.
        """
        self.__setEval('ENsetnodevalue', 'EMITTER', 'NODE', value, *argv)

    def setNodeInitialQuality(self, value, *argv):
        """ Sets the values of initial quality for nodes.

        Example 1:

        >>> nodeset = d.getNodeInitialQuality()                  # Retrieves the value of all nodes initial qualities
        >>> nodeset[0] = 0.5                                     # First node initial quality = 0.5
        >>> d.setNodeInitialQuality(nodeset)                     # Sets the values of all nodes initial quality
        >>> d.getNodeInitialQuality()

        Example 2:

        >>> nodeIndex = 1
        >>> d.getNodeInitialQuality(nodeIndex)
        >>> initialQuality = 1
        >>> d.setNodeInitialQuality(nodeIndex, initialQuality)    # Sets the value of the 1st node initial quality
        >>> d.getNodeInitialQuality(nodeIndex)

        See also getNodeInitialQuality, getNodeActualQuality, setNodeJunctionData.
        """
        self.__setEval('ENsetnodevalue', 'INITQUAL', 'NODE', value, *argv)

    def setNodeJunctionData(self, index, elev, dmnd, dmndpat):
        """ Sets a group of properties for a junction node. (EPANET Version 2.2)

        :param index: a junction node's index (starting from 1).
        :type index: int
        :param elev: the value of the junction's elevation.
        :type elev: float
        :param dmnd: the value of the junction's primary base demand.
        :type dmnd: float
        :param dmndpat: the ID name of the demand's time pattern ("" for no pattern)
        :type dmndpat: str
        :return: None

        Example:

        >>> junctionIndex = 1
        >>> elev = 35
        >>> dmnd = 100
        >>> dmndpat = 'NEW_PATTERN'
        >>> d.addPattern(dmndpat)                                         # Adds a new pattern
        >>> d.setNodeJunctionData(junctionIndex, elev, dmnd, dmndpat)     # Sets the elevation, primary base demand and time pattern of the 1st junction
        >>> d.getNodeElevations(junctionIndex)                            # Retrieves the elevation of the 1st junction
        >>> d.getNodeBaseDemands(junctionIndex)                           # Retrieves the primary base demand of the 1st junction
        >>> d.getNodeDemandPatternNameID()[junctionIndex]                 # Retrieves the demand pattern ID (primary base demand is the first category)

        See also setNodeTankData, getNodeElevations, getNodeBaseDemands,
        getNodeDemandPatternNameID, addPattern, setNodeJunctionDemandName.
        """
        self.api.ENsetjuncdata(index, elev, dmnd, dmndpat)

    def setNodeJunctionDemandName(self, nodeIndex, demandIndex, demandName):
        """ Assigns a name to a node's demand category. (EPANET Version 2.2)

        Example:

        >>> nodeIndex = 1
        >>> demandIndex = 1
        >>> d.getNodeJunctionDemandName()[demandIndex][nodeIndex-1]              # Retrieves the name of the 1st node, 1st demand category
        >>> demandName = 'NEW NAME'
        >>> d.setNodeJunctionDemandName(nodeIndex, demandIndex, demandName)      # Sets a new name of the 1st node, 1st demand category
        >>> d.getNodeJunctionDemandName()[demandIndex][nodeIndex-1]

        See also getNodeJunctionDemandName, setNodeBaseDemands, setDemandModel,
        addNodeJunctionDemand, deleteNodeJunctionDemand.
        """
        self.api.ENsetdemandname(nodeIndex, demandIndex, demandName)

    def setNodeNameID(self, value, *argv):
        """ Sets the ID name for nodes.

        Example 1:

        >>> nodeIndex = 1
        >>> d.getNodeNameID(nodeIndex)          # Retrieves the ID of the 1st node
        >>> nameID = 'newID'
        >>> d.setNodeNameID(nodeIndex, nameID)  # Sets the ID of the 1st node.
        >>> d.getNodeNameID(nodeIndex)

        Example 2:

        >>> nameID = d.getNodeNameID()          # Retrieves the IDs of all nodes
        >>> nameID[0] = 'newID_1'
        >>> nameID[4] = 'newID_5'
        >>> d.setNodeNameID(nameID)             # Sets the IDs of all nodes
        >>> d.getNodeNameID()

        See also getNodeNameID, setNodeComment, setNodeJunctionData.
        """
        if len(argv) == 1:
            indices = value
            value = argv[0]
            if not isList(indices):
                self.api.ENsetnodeid(indices, value)
            else:
                for i in indices:
                    self.api.ENsetnodeid(i, value[indices.index(i)])
        else:
            nameId = self.getNodeNameID()
            for i in nameId:
                if i != value[nameId.index(i)]:
                    self.api.ENsetnodeid(nameId.index(i) + 1, value[nameId.index(i)])

    def setNodesConnectingLinksID(self, linkIndex, startNodeID, endNodeID):
        """ Sets the IDs of a link's start- and end-nodes. (EPANET Version 2.2)

        Example 1:

        >>> d.getNodesConnectingLinksID()  # Retrieves the ids of the from/to nodes of all links
        >>> linkIndex = 2
        >>> startNodeID = '11'
        >>> endNodeID = '22'
        >>> d.setNodesConnectingLinksID(linkIndex, startNodeID, endNodeID)
        >>> d.getNodesConnectingLinksID()

        Example 2:

        >>> linkIndex   = [2, 3]
        >>> startNodeID = ['12', '13']
        >>> endNodeID   = ['21', '22']
        >>> d.setNodesConnectingLinksID(linkIndex, startNodeID, endNodeID)
        >>> d.getNodesConnectingLinksID()
        >>> d.plot()

        See also getLinkNodesIndex, getNodesConnectingLinksID, setLinkLength,
        setLinkNameID, setLinkComment.
        """
        startNode = self.getNodeIndex(startNodeID)
        endNode = self.getNodeIndex(endNodeID)
        self.setLinkNodesIndex(linkIndex, startNode, endNode)

    def setNodeSourcePatternIndex(self, value, *argv):
        """ Sets the values of quality source pattern index.

        Example 1:

        >>> nodeIndex = 1
        >>> d.getNodeSourcePatternIndex(nodeIndex)                        # Retrieves the quality source pattern index of the 1st node
        >>> sourcePatternIndex = 1
        >>> d.setNodeSourcePatternIndex(nodeIndex, sourcePatternIndex)    # Sets the quality source pattern index = 1 to the 1st node
        >>> d.getNodeSourcePatternIndex(nodeIndex)

        Example 2:

        >>> nodeIndex = [1,2,3]
        >>> d.getNodeSourcePatternIndex(nodeIndex)                        # Retrieves the quality source pattern index of the first 3 nodes
        >>> sourcePatternIndex = [1, 1, 1]
        >>> d.setNodeSourcePatternIndex(nodeIndex, sourcePatternIndex)    # Sets the quality source pattern index = 1 to the first 3 nodes
        >>> d.getNodeSourcePatternIndex(nodeIndex)

        See also getNodeSourcePatternIndex, setNodeSourceQuality, setNodeSourceType.
        """
        self.__setEval('ENsetnodevalue', 'SOURCEPAT', 'NODE', value, *argv)

    def setNodeSourceQuality(self, value, *argv):
        """ Sets the values of quality source strength.

        Example 1:

        >>> nodeIndex = 1
        >>> d.getNodeSourceQuality(nodeIndex)                    # Retrieves the quality source strength of the 1st node
        >>> sourceStrength = 10
        >>> d.setNodeSourceQuality(nodeIndex, sourceStrength)    # Sets the quality source strength = 10 to the 1st node
        >>> d.getNodeSourceQuality(nodeIndex)

        Example 2:

        >>> nodeIndex = [1,2,3]
        >>> d.getNodeSourceQuality(nodeIndex)                    # Retrieves the quality source strength of the first 3 nodes
        >>> sourceStrength = [10, 12, 8]
        >>> d.setNodeSourceQuality(nodeIndex, sourceStrength)    # Sets the quality source strength = 10, 12 and 8 to the first 3 nodes
        >>> d.getNodeSourceQuality(nodeIndex)

        See also getNodeSourceQuality, setNodeSourcePatternIndex, setNodeSourceType.
        """
        self.__setEval('ENsetnodevalue', 'SOURCEQUAL', 'NODE', value, *argv)

    def setNodeSourceType(self, index, value):
        """ Sets the values of quality source type.

        Types of external water quality sources that can be set:
          1) CONCEN      Sets the concentration of external inflow entering a node
          2) MASS        Injects a given mass/minute into a node
          3) SETPOINT    Sets the concentration leaving a node to a given value
          4) FLOWPACED   Adds a given value to the concentration leaving a node

        Example:

        >>> nodeIndex = 1
        >>> d.getNodeSourceType(nodeIndex)                 # Retrieves the quality source type of the 1st node
        >>> sourceType = 'MASS'
        >>> d.setNodeSourceType(nodeIndex, sourceType)     # Sets the quality source type = 'MASS' to the 1st node
        >>> d.getNodeSourceType(nodeIndex)

        See also getNodeSourceType, setNodeSourceQuality, setNodeSourcePatternIndex.
        """
        value = self.TYPESOURCE.index(value)
        self.api.ENsetnodevalue(index, self.ToolkitConstants.EN_SOURCETYPE, value)

    def setNodeTankBulkReactionCoeff(self, value, *argv):
        """ Sets the tank bulk reaction coefficient.

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> d.getNodeTankBulkReactionCoeff()                          # Retrieves the  bulk reaction coefficient of all tanks
        >>> d.setNodeTankBulkReactionCoeff(-0.5)                      # Sets the bulk reaction coefficient = -0.5 to every tank
        >>> d.getNodeTankBulkReactionCoeff()

        Example 2: (The input array must have a length equal to the number of tanks).

        >>> d.setNodeTankBulkReactionCoeff([0, -0.5])                 # Sets the bulk reaction coefficient = 0 and -0.5 to the 2 tanks
        >>> d.getNodeTankBulkReactionCoeff()

        Example 3:

        >>> d.setNodeTankBulkReactionCoeff(1, -0.8)                   # Sets the bulk reaction coefficient = -0.5 to the 1st tank
        >>> d.getNodeTankBulkReactionCoeff()

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankBulkReactionCoeff(tankIndex, 0)              # Sets the bulk reaction coefficient = 0 to the tanks with index 128 and 129
        >>> d.getNodeTankBulkReactionCoeff()

        Example 5:

        >>> tankIndex = d.getNodeTankIndex([1,2])
        >>> d.setNodeTankBulkReactionCoeff(tankIndex, [-0.5, 0])      # Sets the bulk reaction coefficient = -0.5 and 0 to the tanks with index 128 and 129 respectively
        >>> d.getNodeTankBulkReactionCoeff()

        See also getNodeTankBulkReactionCoeff, setNodeTankInitialLevel, setNodeTankMixingModelType,
        setNodeTankCanOverFlow, setNodeTankDiameter, setNodeTankData.
        """
        self.__setEvalLinkNode('ENsetnodevalue', 'TANK_KBULK', 'TANK', value, *argv)

    def setNodeTankCanOverFlow(self, value, *argv):
        """ Sets the tank can-overflow (= 1) or not (= 0). (EPANET Version 2.2)

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> d.getNodeTankCanOverFlow()               # Retrieves the can-overflow of all tanks
        >>> d.setNodeTankCanOverFlow(1)              # Sets the can-overflow = 1 to every tank
        >>> d.getNodeTankCanOverFlow()

        Example 2: (The input array must have a length equal to the number of tanks).

        >>> d.setNodeTankCanOverFlow([1, 0])         # Sets the can-overflow = 1 and 0 to the 2 tanks
        >>> d.getNodeTankCanOverFlow()

        Example 3:

        >>> d.setNodeTankCanOverFlow(1, 0)           # Sets the can-overflow = 0 to the 1st tank
        >>> d.getNodeTankCanOverFlow()

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankCanOverFlow(tankIndex, 1)   # Sets the can-overflow = 1 to the tanks with index 128 and 129
        >>> d.getNodeTankCanOverFlow()

        Example 5:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankCanOverFlow(tankIndex, [0, 1])   # Sets the can-overflow = 0 and 1 to the tanks with index 128 and 129 respectively
        >>> d.getNodeTankCanOverFlow()

        See also getNodeTankCanOverFlow, setNodeTankBulkReactionCoeff, setNodeTankMinimumWaterLevel,
        setNodeTankMinimumWaterVolume, setNodeTankDiameter, setNodeTankData.
        """
        self.__setEvalLinkNode('ENsetnodevalue', 'CANOVERFLOW', 'TANK', value, *argv)

    def setNodeTankData(self, index, elev, intlvl, minlvl, maxlvl, diam, minvol, volcurve):
        """ Sets a group of properties for a tank. (EPANET Version 2.2)

        :param index: Tank index
        :type index: int
        :param elev: Tank Elevation
        :type elev: float
        :param intlvl: Tank Initial water Level
        :type intlvl: float
        :param minlvl: Tank Minimum Water Level
        :type minlvl: float
        :param maxlvl: Tank Maximum Water Level
        :type maxlvl: float
        :param diam: Tank Diameter (0 if a volume curve is supplied)
        :type diam: float
        :param minvol: Tank Minimum Water Volume
        :type minvol: float
        :param volcurve: Tank Volume Curve Index ("" for no curve)
        :type volcurve: str
        :return: None

        The examples are based on d = epanet('Net3_trace.inp')

        Example 1: (Sets to the 1st tank the following properties).

        >>> tankIndex = 1    # You can also use tankIndex = 95 (i.e. the index of the tank).
        >>> elev = 100
        >>> intlvl = 13
        >>> minlvl =  0.2
        >>> maxlvl = 33
        >>> diam = 80
        >>> minvol = 50000
        >>> volcurve = ''    # For no curve
        >>> d.setNodeTankData(tankIndex, elev, intlvl, minlvl, maxlvl, diam, minvol, volcurve)
        >>> d.getNodeTankData().disp()

        Example 2: (Sets to the 1st and 2nd tank the following properties).

        >>> tankIndex = [1, 2]    # You can also use tankIndex = [95, 96] (i.e. the indices of the tanks).
        >>> elev = [100, 105]
        >>> intlvl = [13, 13.5]
        >>> minlvl =  [0.2, 0.25]
        >>> maxlvl = [30, 35]
        >>> diam = [80, 85]
        >>> minvol = [50000, 60000]
        >>> volcurve = ['', '']    # For no curves
        >>> d.setNodeTankData(tankIndex, elev, intlvl, minlvl, maxlvl, diam, minvol, volcurve)
        >>> d.getNodeTankData(tankIndex).disp()

        See also getNodeTankData, setNodeTankInitialLevel, setNodeTankMinimumWaterLevel, setNodeTankDiameter.
        """
        if not isList(index):
            index = [index]
        index_ = []
        for i in index:
            if i not in self.getNodeTankIndex():
                tankIndices = self.getNodeTankIndex()
                index_.append(tankIndices[i - 1])
        if len(index_) != 0: index = index_
        if not isList(elev):
            elev = [elev]
        if not isList(intlvl):
            intlvl = [intlvl]
        if not isList(minlvl):
            minlvl = [minlvl]
        if not isList(maxlvl):
            maxlvl = [maxlvl]
        if not isList(diam):
            diam = [diam]
        if not isList(minvol):
            minvol = [minvol]
        if not isList(volcurve):
            volcurve = [volcurve]
        for i in range(len(index)):
            self.api.ENsettankdata(index[i], elev[i], intlvl[i], minlvl[i], maxlvl[i], diam[i], minvol[i], volcurve[i])

    def setNodeTankDiameter(self, value, *argv):
        """ Sets the diameter value for tanks.

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> d.getNodeTankDiameter()                         #  Retrieves the diameter of all tanks
        >>> d.setNodeTankDiameter(120)                      #  Sets the diameter = 120 to every tank
        >>> d.getNodeTankDiameter()

        Example 2: (The input array must have a length equal to the number of tanks).

        >>> d.setNodeTankDiameter([110, 130])               # Sets the diameter = 110 and 130 to the 2 tanks
        >>> d.getNodeTankDiameter()

        Example 3:

        >>> d.setNodeTankDiameter(1, 120)                   # Sets the diameter = 120 to the 1st tank
        >>> d.getNodeTankDiameter()

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankDiameter(tankIndex, 150)           # Sets the diameter = 150 to the tanks with index 128 and 129
        >>> d.getNodeTankDiameter()

        Example 5:

        >>> tankIndex = d.getNodeTankIndex([1,2])
        >>> d.setNodeTankDiameter(tankIndex, [100, 120])    # Sets the diameter = 100 and 120 to the tanks with index 128 and 129 respectively
        >>> d.getNodeTankDiameter()

        See also getNodeTankDiameter, setNodeTankInitialLevel, setNodeTankMinimumWaterLevel,
        setNodeTankBulkReactionCoeff, setNodeTankCanOverFlow, setNodeTankData.
        """
        self.__setEvalLinkNode('ENsetnodevalue', 'TANKDIAM', 'TANK', value, *argv)

    def setNodeTankInitialLevel(self, value, *argv):
        """ Sets the values of initial level for tanks.

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> d.getNodeTankInitialLevel()                       # Retrieves the initial level of all tanks
        >>> d.setNodeTankInitialLevel(10)                     # Sets the initial level = 10 to every tank
        >>> d.getNodeTankInitialLevel()

        Example 2: (The input array must have a length equal to the number of tanks).

        >>> d.setNodeTankInitialLevel([10, 15])               # Sets the initial level = 10 and 15 to the 2 tanks
        >>> d.getNodeTankInitialLevel()

        Example 3:

        >>> d.setNodeTankInitialLevel(1, 10)                  # Sets the initial level = 10 to the 1st tank
        >>> d.getNodeTankInitialLevel()

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankInitialLevel(tankIndex, 10)          # Sets the initial level = 10 to the tanks with index 128 and 129
        >>> d.getNodeTankInitialLevel()

        Example 5:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankInitialLevel(tankIndex, [10, 15])    # Sets the initial level = 10 and 15 to the tanks with index 128 and 129 respectively
        >>> d.getNodeTankInitialLevel()

        See also getNodeTankInitialLevel, setNodeTankMinimumWaterLevel, setNodeTankMaximumWaterLevel,
        setNodeTankMinimumWaterVolume, setNodeTankMixingFraction, setNodeTankData.
        """
        self.__setEvalLinkNode('ENsetnodevalue', 'TANKLEVEL', 'TANK', value, *argv)

    def setNodeTankMaximumWaterLevel(self, value, *argv):
        """ Sets the maximum water level value for tanks.

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> d.getNodeTankMaximumWaterLevel()                       # Retrieves the maximum water level of all tanks
        >>> d.setNodeTankMaximumWaterLevel(35)                     # Sets the maximum water level = 35 to every tank
        >>> d.getNodeTankMaximumWaterLevel()

        Example 2: (The input array must have a length equal to the number of tanks).

        >>> d.setNodeTankMaximumWaterLevel([30, 40])               # Sets the maximum water level = 30 and 40 to the 2 tanks
        >>> d.getNodeTankMaximumWaterLevel()

        Example 3:

        >>> d.setNodeTankMaximumWaterLevel(1, 35)                  # Sets the maximum water level = 35 to the 1st tank
        >>> d.getNodeTankMaximumWaterLevel()

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankMaximumWaterLevel(tankIndex, 30)          # Sets the maximum water level = 30 to the tanks with index 128 and 129
        >>> d.getNodeTankMaximumWaterLevel()

        Example 5:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankMaximumWaterLevel(tankIndex, [35, 45])    # Sets the maximum water level = 35 and 45 to the tanks with index 128 and 129 respectively
        >>> d.getNodeTankMaximumWaterLevel()

        See also getNodeTankMaximumWaterLevel, setNodeTankInitialLevel, setNodeTankMinimumWaterLevel,
        setNodeTankMinimumWaterVolume, setNodeTankMixingFraction, setNodeTankData.
        """
        self.__setEvalLinkNode('ENsetnodevalue', 'MAXLEVEL', 'TANK', value, *argv)

    def setNodeTankMinimumWaterLevel(self, value, *argv):
        """ Sets the minimum water level value for tanks.

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> d.getNodeTankMinimumWaterLevel()                         # Retrieves the minimum water level of all tanks
        >>> d.setNodeTankMinimumWaterLevel(5)                        # Sets the minimum water level = 5 to every tank
        >>> d.getNodeTankMinimumWaterLevel()

        Example 2: (The input array must have a length equal to the number of tanks).

        >>> d.setNodeTankMinimumWaterLevel([10, 15])                 # Sets the minimum water level = 10 and 15 to the 2 tanks
        >>> d.getNodeTankMinimumWaterLevel()

        Example 3:

        >>> d.setNodeTankMinimumWaterLevel(1, 5)                     # Sets the minimum water level = 5 to the 1st tank
        >>> d.getNodeTankMinimumWaterLevel()

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankMinimumWaterLevel(tankIndex, 10)            # Sets the minimum water level = 10 to the tanks with index 128 and 129
        >>> d.getNodeTankMinimumWaterLevel()

        Example 5:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankMinimumWaterLevel(tankIndex, [5, 15])       # Sets the minimum water level = 5 and 15 to the tanks with index 128 and 129 respectively
        >>> d.getNodeTankMinimumWaterLevel()

        See also getNodeTankMinimumWaterLevel, setNodeTankInitialLevel, setNodeTankMaximumWaterLevel,
        setNodeTankMinimumWaterVolume, setNodeTankMixingFraction, setNodeTankData.
        """
        self.__setEvalLinkNode('ENsetnodevalue', 'MINLEVEL', 'TANK', value, *argv)

    def setNodeTankMinimumWaterVolume(self, value, *argv):
        """ Sets the minimum water volume value for tanks.

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> d.getNodeTankMinimumWaterVolume()                           # Retrieves the minimum water volume of all tanks
        >>> d.setNodeTankMinimumWaterVolume(1000)                       # Sets the minimum water volume = 1000 to every tank
        >>> d.getNodeTankMinimumWaterVolume()

        Example 2: (The input array must have a length equal to the number of tanks).

        >>> d.setNodeTankMinimumWaterVolume([1500, 2000])               # Sets the minimum water volume = 1500 and 2000 to the 2 tanks
        >>> d.getNodeTankMinimumWaterVolume()

        Example 3:

        >>> d.setNodeTankMinimumWaterVolume(1, 1000)                    # Sets the minimum water volume = 1000 to the 1st tank
        >>> d.getNodeTankMinimumWaterVolume()

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankMinimumWaterVolume(tankIndex, 1500)            # Sets the minimum water volume = 1500 to the tanks with index 128 and 129
        >>> d.getNodeTankMinimumWaterVolume()

        Example 5:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankMinimumWaterVolume(tankIndex, [1000, 2000])     # Sets the minimum water volume = 1000 and 2000 to the tanks with index 128 and 129 respectively
        >>> d.getNodeTankMinimumWaterVolume()

        See also getNodeTankMinimumWaterVolume, setNodeTankInitialLevel, setNodeTankMinimumWaterLevel,
        setNodeTankMaximumWaterLevel, setNodeTankMixingFraction, setNodeTankData.
        """
        self.__setEvalLinkNode('ENsetnodevalue', 'MINVOLUME', 'TANK', value, *argv)

    def setNodeTankMixingFraction(self, value, *argv):
        """ Sets the tank mixing fraction of total volume occupied by the inlet/outlet zone in a 2-compartment tank.

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> d.getNodeTankMixingFraction()                     # Retrieves the mixing fraction of all tanks
        >>> d.setNodeTankMixingFraction(0)                    # Sets the mixing fraction = 0 to every tank
        >>> d.getNodeTankMixingFraction()

        Example 2: (The input array must have a length equal to the number of tanks).

        >>> d.setNodeTankMixingFraction([1, 0])               # Sets the mixing fraction = 1 and 0 to the 2 tanks
        >>> d.getNodeTankMixingFraction()

        Example 3:

        >>> d.setNodeTankMixingFraction(1, 0)                 # Sets the mixing fraction = 0 to the 1st tank
        >>> d.getNodeTankMixingFraction()

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankMixingFraction(tankIndex, 1)         # Sets the mixing fraction = 1 to the tanks with index 128 and 129
        >>> d.getNodeTankMixingFraction()

        Example 5:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankMixingFraction(tankIndex, [1, 0])     # Sets the mixing fraction = 1 and 0 to the tanks with index 128 and 129 respectively
        >>> d.getNodeTankMixingFraction()

        See also getNodeTankMixingFraction, setNodeTankMixingModelType, setNodeTankMinimumWaterLevel,
        setNodeTankMinimumWaterVolume, setNodeTankDiameter, setNodeTankData.
        """
        self.__setEvalLinkNode('ENsetnodevalue', 'MIXFRACTION', 'TANK', value, *argv)

    def setNodeTankMixingModelType(self, value, *argv):
        """ Sets the mixing model type value for tanks.

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> d.getNodeTankMixingModelType()                                 # Retrieves the  mixing model type of all tanks
        >>> d.setNodeTankMixingModelType('MIX2')                           # Sets the  mixing model type = 'MIX2' to every tank
        >>> d.getNodeTankMixingModelType()

        Example 2: (The input array must have a length equal to the number of tanks)

        >>> d.setNodeTankMixingModelType(['MIX1', 'LIFO'])                 # Sets the  mixing model type = 'MIX1' and 'LIFO' to the 2 tanks
        >>> d.getNodeTankMixingModelType()

        Example 3:

        >>> d.setNodeTankMixingModelType(1, 'FIFO')                        # Sets the  mixing model type = 'FIFO' to the 1st tank
        >>> d.getNodeTankMixingModelType()

        Example 4:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankMixingModelType(tankIndex, 'MIX1')                # Sets the  mixing model type = 'MIX1' to the tanks with index 128 and 129
        >>> d.getNodeTankMixingModelType()

        Example 5:

        >>> tankIndex = d.getNodeTankIndex()
        >>> d.setNodeTankMixingModelType(tankIndex, ['MIX2', 'LIFO'])      # Sets the  mixing model type = 'MIX2' and 'LIFO' to the tanks with index 128 and 129 respectively
        >>> d.getNodeTankMixingModelType()

        See also getNodeTankMixingModelType, setNodeTankBulkReactionCoeff, setNodeTankMixingFraction,
        setNodeTankMinimumWaterVolume, setNodeTankMinimumWaterLevel, setNodeTankData.
        """
        if len(argv) == 0:
            _type = value
        elif len(argv) == 1:
            _type = argv[0]
        if type(_type) is list:
            code = []
            for i in _type:
                code.append(self.TYPEMIXMODEL.index(i))
        else:
            code = self.TYPEMIXMODEL.index(_type)
        if len(argv) == 0:
            value = code
        elif len(argv) == 1:
            argv = code
            self.__setEvalLinkNode('ENsetnodevalue', 'MIXMODEL', 'TANK', value, argv)
            return
        self.__setEvalLinkNode('ENsetnodevalue', 'MIXMODEL', 'TANK', value, *argv)

    def setNodeTypeJunction(self, Id):
        """ Transforms a node to JUNCTION
        The new node keeps the id,coordinates and elevation of the
        deleted one

        Example 1:

        >>> d = epanet('Net1.inp')
        >>> index = d.setNodeTypeJunction('2')
        >>> d.getNodeType(index)
        >>> d.plot()
        """
        nodeIndex = self.getNodeIndex(Id)
        if self.getNodeTypeIndex(nodeIndex) == 0:
            raise Exception('The current node is already a junction')
        return self.__changeNodeType(Id, 0)

    def setNodeTypeReservoir(self, Id):
        """ Transforms a node to RESERVOIR
        The new node keeps the id,coordinates and elevation of the
        deleted one

        Example 1:

        >>> d = epanet('Net1.inp')
        >>> index = d.setNodeTypeReservoir('13')
        >>> d.getNodeType(index)
        >>> d.plot()
        """
        nodeIndex = self.getNodeIndex(Id)
        if self.getNodeTypeIndex(nodeIndex) == 1:
            raise Exception('The current node is already a reservoir')
        return self.__changeNodeType(Id, 1)

    def setNodeTypeTank(self, Id):
        """ Transforms a node to TANK
        The new node keeps the id,coordinates and elevation of the
        deleted one

        Example 1:

        >>> d = epanet('Net1.inp')
        >>> index = d.setNodeTypeTank('13')
        >>> d.getNodeType(index)
        >>> d.plot()
        """
        nodeIndex = self.getNodeIndex(Id)
        if self.getNodeTypeIndex(nodeIndex) == 2:
            raise Exception('The current node is already a tank')
        return self.__changeNodeType(Id, 2)

    def setOptionsAccuracyValue(self, value):
        """ Sets the total normalized flow change for hydraulic convergence.

        Example:

        >>> d.setOptionsAccuracyValue(0.001)
        >>> d.getOptionsAccuracyValue()

        See also getOptionsAccuracyValue, setOptionsExtraTrials, setOptionsMaxTrials.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_ACCURACY, value)

    def setOptionsCheckFrequency(self, value):
        """ Sets the frequency of hydraulic status checks. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsCheckFrequency(2)
        >>> d.getOptionsCheckFrequency()

        See also getOptionsCheckFrequency, setOptionsMaxTrials, setOptionsMaximumCheck.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_CHECKFREQ, value)

    def setOptionsDampLimit(self, value):
        """ Sets the accuracy level where solution damping begins. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsDampLimit(0)
        >>> d.getOptionsDampLimit()

        See also getOptionsDampLimit, setOptionsMaxTrials, setOptionsCheckFrequency.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_DAMPLIMIT, value)

    def setOptionsDemandCharge(self, value):
        """ Sets the energy charge per maximum KW usage. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsDemandCharge(0)
        >>> d.getOptionsDemandCharge()

        See also getOptionsDemandCharge, setOptionsGlobalPrice, setOptionsGlobalPattern.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_DEMANDCHARGE, value)

    def setOptionsEmitterExponent(self, value):
        """ Sets the power exponent for the emmitters.

        Example:

        >>> d.setOptionsEmitterExponent(0.5)
        >>> d.getOptionsEmitterExponent()

        See also getOptionsEmitterExponent, setOptionsPatternDemandMultiplier, setOptionsAccuracyValue.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_EMITEXPON, value)

    def setOptionsExtraTrials(self, value):
        """ Sets the extra trials allowed if hydraulics don't converge. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsExtraTrials(10)
        >>> d.getOptionsExtraTrials()
        >>> # Set UNBALANCED to STOP
        >>> d.setOptionsExtraTrials(-1)

        See also getOptionsExtraTrials, setOptionsMaxTrials, setOptionsMaximumCheck.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_UNBALANCED, value)

    def setOptionsFlowChange(self, value):
        """ Sets the maximum flow change for hydraulic convergence. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsFlowChange(0)
        >>> d.getOptionsFlowChange()

        See also getOptionsFlowChange, setOptionsHeadError, setOptionsHeadLossFormula.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_FLOWCHANGE, value)

    def setOptionsGlobalEffic(self, value):
        """ Sets the global efficiency for pumps(percent). (EPANET Version 2.2)

        Example:

        >>> d.setOptionsGlobalEffic(75)
        >>> d.getOptionsGlobalEffic()

        See also getOptionsGlobalEffic, setOptionsGlobalPrice, setOptionsGlobalPattern.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_GLOBALEFFIC, value)

    def setOptionsGlobalPrice(self, value):
        """ Sets the global average energy price per kW-Hour. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsGlobalPrice(0)
        >>> d.getOptionsGlobalPrice()

        See also getOptionsGlobalPrice, setOptionsGlobalEffic, setOptionsGlobalPattern.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_GLOBALPRICE, value)

    def setOptionsGlobalPattern(self, value):
        """ Sets the global energy price pattern. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsGlobalPattern(1)
        >>> d.getOptionsGlobalPattern()

        See also getOptionsGlobalPattern, setOptionsGlobalEffic, setOptionsGlobalPrice.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_GLOBALPATTERN, value)

    def setOptionsHeadError(self, value):
        """ Sets the maximum head loss error for hydraulic convergence. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsHeadError(0)
        >>> d.getOptionsHeadError()

        See also getOptionsHeadError, setOptionsEmitterExponent, setOptionsAccuracyValue.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_HEADERROR, value)

    def setOptionsHeadLossFormula(self, value):
        """ Sets the headloss formula. (EPANET Version 2.2)
        'HW' = 0, 'DW' = 1, 'CM' = 2

        Example:

        >>> d.setOptionsHeadLossFormula('HW')    # Sets the 'HW' headloss formula
        >>> d.getOptionsHeadLossFormula()

        See also getOptionsHeadLossFormula, setOptionsHeadError, setOptionsFlowChange.
        """
        if value == 'HW':
            codevalue = 0
        elif value == 'DW':
            codevalue = 1
        elif value == 'CM':
            codevalue = 2
        return self.api.ENsetoption(self.ToolkitConstants.EN_HEADLOSSFORM, codevalue)

    def setOptionsLimitingConcentration(self, value):
        """ Sets the limiting concentration for growth reactions. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsLimitingConcentration(0)
        >>> d.getOptionsLimitingConcentration()

        See also getOptionsLimitingConcentration, setOptionsPipeBulkReactionOrder, setOptionsPipeWal
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_CONCENLIMIT, value)

    def setOptionsMaximumCheck(self, value):
        """ Sets the maximum trials for status checking. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsMaximumCheck(10)
        >>> d.getOptionsMaximumCheck()

        See also getOptionsMaximumCheck, setOptionsMaxTrials, setOptionsCheckFrequency.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_MAXCHECK, value)

    def setOptionsMaxTrials(self, value):
        """ Sets the maximum hydraulic trials allowed for hydraulic convergence.

        Example:

        >>> d.setOptionsMaxTrials(40)
        >>> d.getOptionsMaxTrials()

        See also getOptionsMaxTrials, setOptionsExtraTrials, setOptionsAccuracyValue.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_TRIALS, value)

    def setOptionsPatternDemandMultiplier(self, value):
        """ Sets the global pattern demand multiplier.

        Example:

        >>> d.setOptionsPatternDemandMultiplier(1)
        >>> d.getOptionsPatternDemandMultiplier()

        See also getOptionsPatternDemandMultiplier, setOptionsEmitterExponent, setOptionsAccuracyValue.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_DEMANDMULT, value)

    def setOptionsPipeBulkReactionOrder(self, value):
        """ Sets the bulk water reaction order for pipes. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsPipeBulkReactionOrder(1)
        >>> d.getOptionsPipeBulkReactionOrder()

        See also getOptionsPipeBulkReactionOrder, setOptionsPipeWallReactionOrder, setOptionsTankBulkReactionOrder.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_BULKORDER, value)

    def setOptionsPipeWallReactionOrder(self, value):
        """ Sets the wall reaction order for pipes (either 0 or 1). (EPANET Version 2.2)

        Example:

        >>> d.setOptionsPipeWallReactionOrder(1)
        >>> d.getOptionsPipeWallReactionOrder()

        See also getOptionsPipeWallReactionOrder, setOptionsPipeBulkReactionOrder, setOptionsTankBulkReactionOrder.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_WALLORDER, value)

    def setOptionsQualityTolerance(self, value):
        """ Sets the water quality analysis tolerance.

        Example:

        >>> d.setOptionsQualityTolerance(0.01)
        >>> d.getOptionsQualityTolerance()

        See also getOptionsQualityTolerance, setOptionsSpecificDiffusivity, setOptionsLimitingConcentration.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_TOLERANCE, value)

    def setOptionsSpecificDiffusivity(self, value):
        """ Sets the specific diffusivity (relative to chlorine at 20 deg C). (EPANET Version 2.2)

        Example:

        >>> d.setOptionsSpecificDiffusivity(1)
        >>> d.getOptionsSpecificDiffusivity()

        See also getOptionsSpecificDiffusivity, setOptionsSpecificViscosity, setOptionsSpecificGravity.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_SP_DIFFUS, value)

    def setOptionsSpecificGravity(self, value):
        """ Sets the specific gravity. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsSpecificGravity(1)
        >>> d.getOptionsSpecificGravity()

        See also getOptionsSpecificGravity, setOptionsSpecificViscosity, setOptionsHeadLossFormula.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_SP_GRAVITY, value)

    def setOptionsSpecificViscosity(self, value):
        """ Sets the specific viscosity. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsSpecificViscosity(1)
        >>> d.getOptionsSpecificViscosity()

        See also getOptionsSpecificViscosity, setOptionsSpecificGravity, setOptionsHeadLossFormula.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_SP_VISCOS, value)

    def setOptionsTankBulkReactionOrder(self, value):
        """ Sets the bulk water reaction order for tanks. (EPANET Version 2.2)

        Example:

        >>> d.setOptionsTankBulkReactionOrder(1)
        >>> d.getOptionsTankBulkReactionOrder()

        See also getOptionsTankBulkReactionOrder, setOptionsPipeBulkReactionOrder, setOptionsPipeWallReactionOrder.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_TANKORDER, value)

    def setQualityType(self, *argv):
        """ Sets the type of water quality analysis called for.

        Example 1:

        >>> d.setQualityType('none')                         # Sets no quality analysis.
        >>> qualInfo = d.getQualityInfo()                      # Retrieves quality analysis information

        Example 2:

        >>> d.setQualityType('age')                          # Sets water age analysis
        >>> qualInfo = d.getQualityInfo()

        Example 3:

        >>> d.setQualityType('chem', 'Chlorine')             # Sets chemical analysis given the name of the chemical being analyzed
        >>> qualInfo = d.getQualityInfo()
        >>> d.setQualityType('chem', 'Chlorine', 'mg/Kg')    # Sets chemical analysis given the name of the chemical being analyzed and units that the chemical is measured in
        >>> qualInfo = d.getQualityInfo()

        Example 4:

        >>> nodeID = d.getNodeNameID(1)
        >>> d.setQualityType('trace', nodeID)                # Sets source tracing analysis given the ID label of node traced in a source tracing analysis
        >>> qualInfo = d.getQualityInfo()

        See also getQualityInfo, getQualityType, getQualityCode, getQualityTraceNodeIndex.
        """
        qualcode = self.ToolkitConstants.EN_NONE
        chemname = ""
        chemunits = ""
        tracenode = ""
        if 'none' in argv:
            pass
        elif 'age' in argv:
            qualcode = self.ToolkitConstants.EN_AGE
        elif 'chem' in argv:
            qualcode = self.ToolkitConstants.EN_CHEM
            chemname = argv[1]
            if len(argv) <= 2:
                chemunits = 'mg/L'
            else:
                chemunits = argv[2]
        elif 'trace' in argv:
            qualcode = self.ToolkitConstants.EN_TRACE
            tracenode = argv[1]
        else:
            qualcode = self.ToolkitConstants.EN_CHEM
            chemname = argv[0]
            if len(argv) < 2:
                chemunits = 'mg/L'
            else:
                chemunits = argv[1]
        self.api.ENsetqualtype(qualcode, chemname, chemunits, tracenode)

    def setPattern(self, index, patternVector):
        """ Sets all of the multiplier factors for a specific time pattern.

        Example:

        >>> patternID = 'new_pattern'
        >>> patternIndex = d.addPattern(patternID)     # Adds a new time pattern
        >>> patternMult = [1.56, 1.36, 1.17, 1.13, 1.08,
        ...    1.04, 1.2, 0.64, 1.08, 0.53, 0.29, 0.9, 1.11,
        ...    1.06, 1.00, 1.65, 0.55, 0.74, 0.64, 0.46,
        ...    0.58, 0.64, 0.71, 0.66]
        >>> d.setPattern(patternIndex, patternMult)    # Sets the multiplier factors for the new time pattern
        >>> d.getPattern()                             # Retrieves the multiplier factor for all patterns and all times

        See also getPattern, setPatternValue, setPatternMatrix, setPatternNameID, addPattern, deletePattern.
        """
        nfactors = len(patternVector)
        self.api.ENsetpattern(index, patternVector, nfactors)

    def setPatternComment(self, value, *argv):
        """ Sets the comment string assigned to the pattern object.

        Example 1:

        >>> patternIndex = 1
        >>> patternComment = 'This is a PATTERN'
        >>> d.setPatternComment(patternIndex, patternComment)   # Sets the comment of the 1st pattern
        >>> d.getPatternComment(patternIndex)                   # Retrieves the comment of the 1st pattern

        Example 2:

        >>> patternIndex = [1,2]
        >>> patternComment = ['1st PATTERN', '2nd PATTERN']
        >>> d.setPatternComment(patternIndex, patternComment)   # Sets the comments of the first 2 patterns (if exist)
        >>> d.getPatternComment(patternIndex)

        Example 3:

        >>> d = epanet('BWSN_Network_1.inp')
        >>> patternComment = ['1st PAT', '2nd PAT', '3rd PAT', "4rth PAT"]
        >>> d.setPatternComment(patternComment)                 # Sets the comments of all the patterns (the length of the list
                                                                  must be equal to the number of patterns)
        >>> d.getPatternComment()

        See also getPatternComment, setPatternNameID, setPattern.
        """
        if len(argv) == 0:
            patIndices = list(range(1,self.getPatternCount()+1))
        else:
            patIndices = argv[0]
        self.__addComment(self.ToolkitConstants.EN_PATTERN, patIndices, value)

    def setPatternMatrix(self, patternMatrix):
        """ Sets all of the multiplier factors for all time patterns.

        Example:

        >>> patternID_1 = 'new_pattern_1'
        >>> patternIndex_1 = d.addPattern(patternID_1)    # Adds a new time pattern
        >>> patternID_2 = 'new_pattern_2'
        >>> patternIndex_2 = d.addPattern(patternID_2)    # Adds a new time pattern
        >>> patternMult = d.getPattern()
        >>> patternMult[patternIndex_1-1, 1] = 5            # The 2nd multiplier = 5 of the 1st time pattern
        >>> patternMult[patternIndex_2-1, 2] = 7            # The 3rd multiplier = 7 of the 2nd time pattern
        >>> d.setPatternMatrix(patternMult)               # Sets all of the multiplier factors for all the time patterns given a matrix
        >>> d.getPattern()                                # Retrieves the multiplier factor for all patterns and all times

        See also getPattern, setPattern, setPatternValue, setPatternNameID, addPattern, deletePattern.
        """
        if isList(patternMatrix[0]):
            nfactors = len(patternMatrix[0])
            for i in range(1, len(patternMatrix) + 1):
                self.api.ENsetpattern(i, patternMatrix[i - 1, :], nfactors)
        else:
            # For a single pattern
            self.api.ENsetpattern(1, patternMatrix, len(patternMatrix)) 

    def setPatternNameID(self, index, Id):
        """ Sets the name ID of a time pattern given it's index and the new ID. (EPANET Version 2.2)

        Example 1:

        >>> d.getPatternNameID()                                   # Retrieves the name IDs of all the time patterns
        >>> d.setPatternNameID(1, 'Pattern1')                      # Sets to the 1st time pattern the new name ID 'Pattern1'
        >>> d.getPatternNameID()

        Example 2:

        >>> d.setPatternNameID([1, 2], ['Pattern1', 'Pattern2'])   # Sets to the 1st and 2nd time pattern the new name IDs 'Pattern1' and 'Pattern2' respectively
        >>> d.getPatternNameID()

        See also getPatternNameID, getPatternIndex, getPatternLengths, setPatternComment, setPattern.
        """
        if isList(index):
            for i in index:
                self.api.ENsetpatternid(index[index.index(i)], Id[index.index(i)])
        else:
            self.api.ENsetpatternid(index, Id)

    def setPatternValue(self, index, patternTimeStep, patternFactor):
        """ Sets the multiplier factor for a specific period within a time pattern.

        Example:

        >>> patternID = 'new_pattern'
        >>> patternIndex = d.addPattern(patternID)                          # Adds a new time pattern
        >>> patternTimeStep = 2
        >>> patternFactor = 5
        >>> d.setPatternValue(patternIndex, patternTimeStep, patternFactor) # Sets the multiplier factor = 5 to the 2nd time period of the new time pattern
        >>> d.getPattern()                                                    # Retrieves the multiplier factor for all patterns and all times

        See also getPattern, setPattern, setPatternMatrix, setPatternNameID, addPattern, deletePattern.
        """
        self.api.ENsetpatternvalue(index, patternTimeStep, patternFactor)

    def setReport(self, value):
        """ Issues a report formatting command. Formatting commands are the same as used in the [REPORT] section of the EPANET Input file.
        More: https://github.com/OpenWaterAnalytics/EPANET/wiki/%5BREPORT%5D

        Example 1:

        >>> d.setReport('FILE TestReport.txt')

        Example 2:

        >>> d.setReport('STATUS YES')

        See also setReportFormatReset, setReport.
        """
        self.api.ENsetreport(value)

    def setReportFormatReset(self):
        """ Resets a project's report options to their default values.

        Example:

        >>> d.setReportFormatReset()

        See also setReport, setReportStatus.
        """
        self.api.ENresetreport()
        
    def setReportStatus(self, value):
        """ Sets the level of hydraulic status reporting.

        Possible status that can be set:
          1) 'yes'
          2) 'no'
          3) 'full'

        Example:

        >>> d.setReportStatus('full')

        See also setReport, setReportFormatReset.
        """
        statuslevel = self.TYPEREPORT.index(value.upper())
        self.api.ENsetstatusreport(statuslevel)

    def setRulePremise(self, ruleIndex, premiseIndex, premise):
        """ Sets the premise of a rule - based control. (EPANET Version 2.2)

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example 1:

        >>> d.getRules()[1]['Premises']                          # Retrieves the premise of the 1st rule
        >>> ruleIndex = 1
        >>> premiseIndex = 1
        >>> premise = 'IF SYSTEM CLOCKTIME >= 8 PM'
        >>> d.setRulePremise(ruleIndex, premiseIndex, premise)   # Sets the 1st premise of the 1st rule - based control
        >>> d.getRules()[1]['Premises']

        Example 2:

        >>> d.getRules()[1]['Premises']
        >>> ruleIndex = 1
        >>> premiseIndex = 1
        >>> premise = 'IF NODE TANK-131 LEVEL > 20'
        >>> d.setRulePremise(ruleIndex, premiseIndex, premise)   # Sets the 1st premise of the 1st rule - based control
        >>> d.getRules()[1]['Premises']

        See also setRulePremiseObjectNameID, setRulePremiseStatus, setRulePremiseValue,
        setRules, getRules, addRules, deleteRules.
        """
        premise_new = premise.split()
        logop = self.LOGOP.index(premise_new[0]) + 1
        object_ = eval('self.ToolkitConstants.EN_R_' + premise_new[1])
        if object_ == self.ToolkitConstants.EN_R_NODE:
            objIndex = self.getNodeIndex(premise_new[2])
        elif object_ == self.ToolkitConstants.EN_R_LINK:
            objIndex = self.getLinkIndex(premise_new[2])
        elif object_ == self.ToolkitConstants.EN_R_SYSTEM:
            objIndex = 0
        if object_ == self.ToolkitConstants.EN_R_SYSTEM:
            j, k, m = 2, 3, 4
        else:
            j, k, m = 3, 4, 5
        variable = eval('self.ToolkitConstants.EN_R_' + premise_new[j])
        relop = self.RULEOPERATOR.index(premise_new[k])
        if variable == self.ToolkitConstants.EN_R_STATUS:
            value = -1
            status = eval('self.ToolkitConstants.EN_R_IS_' + premise_new[m])
        else:
            value = float(premise_new[m])
            status = 0
        if object_ == self.ToolkitConstants.EN_R_SYSTEM:
            if premise_new[5] == 'AM':
                value = value * 3600
            elif premise_new[5] == 'PM':
                value = value * 3600 + 43200
        self.api.ENsetpremise(ruleIndex, premiseIndex, logop, object_, objIndex, variable, relop, status, value)

    def setRulePremiseObjectNameID(self, ruleIndex, premiseIndex, objNameID):
        """ Sets the ID of an object in a premise of a rule-based control. (EPANET Version 2.2)

        # The example is based on d = epanet('BWSN_Network_1.inp')

        Example: Sets the node's ID = 'TANK-131' to the 1st premise of the 1st rule - based control.

        >>> d.getRules()[1]['Premises']
        >>> ruleIndex = 1
        >>> premiseIndex = 1
        >>> objNameID = 'TANK-131'
        >>> d.setRulePremiseObjectNameID(ruleIndex, premiseIndex, objNameID)
        >>> d.getRules()[1]['Premises']

        See also setRulePremise, setRulePremiseStatus, setRulePremiseValue,
        setRules, getRules, addRules, deleteRules.
        """
        [_, object_, objIndex, _, _, _, _] = self.api.ENgetpremise(ruleIndex, premiseIndex)
        if object_ == self.ToolkitConstants.EN_R_NODE:
            objIndex = self.getNodeIndex(objNameID)
        elif object_ == self.ToolkitConstants.EN_R_LINK:
            objIndex = self.getLinkIndex(objNameID)
        self.api.ENsetpremiseindex(ruleIndex, premiseIndex, objIndex)

    def setRulePremiseValue(self, ruleIndex, premiseIndex, value):
        """ Sets the value being compared to in a premise of a rule-based control. (EPANET Version 2.2)

        The example is based on d = epanet('BWSN_Network_1.inp')

        Example:

        >>> d.getRules()[1]['Premises']
        >>> ruleIndex = 1
        >>> premiseIndex = 1
        >>> value = 20
        >>> d.setRulePremiseValue(ruleIndex, premiseIndex, value)   # Sets the value = 20 to the 1st premise of the 1st rule - based control
        >>> d.getRules()[1]['Premises']

        See also setRulePremise, setRulePremiseObjectNameID, setRulePremiseStatus,
        setRules, getRules, addRules, deleteRules.
        """
        self.api.ENsetpremisevalue(ruleIndex, premiseIndex, value)

    def setRules(self, ruleIndex, rule):
        """ Sets a rule - based control. (EPANET Version 2.2)

        The example is based on d = epanet('Net1.inp')

        Example:

        >>> rule = 'RULE RULE-1 \n IF NODE 2 LEVEL >= 140 \n THEN PIPE 10 STATUS IS CLOSED \n ELSE PIPE 10 STATUS IS OPEN \n PRIORITY 1'
        >>> d.addRules(rule)              # Adds a new rule - based control
        >>> d.getRules()[1]['Rule']       # Retrieves the 1st rule - based control
        >>> ruleIndex = 1
        >>> rule_new = 'IF NODE 2 LEVEL > 150 \n THEN PIPE 10 STATUS IS OPEN \n ELSE PIPE 11 STATUS IS OPEN \n PRIORITY 2'
        >>> d.setRules(ruleIndex, rule_new)   # Sets rule - based control
        >>> d.getRules()[1]['Rule']

        See also setRulePremise, setRuleThenAction, setRuleElseAction, getRules, addRules, deleteRules.
        """
        rule_new = rule.split('\n')
        for i in rule_new:
            if i[0] == ' ':
                rule_new[rule_new.index(i)] = rule_new[rule_new.index(i)][1:]
        i = 0
        while 'IF' in rule_new[i][0:2] or 'AND' in rule_new[i][0:3] or 'OR' in rule_new[i][0:2]:
            self.setRulePremise(ruleIndex, i + 1, rule_new[i])
            i += 1
        j = 1
        while 'THEN' in rule_new[i][0:4] or 'AND' in rule_new[i][0:3]:
            self.setRuleThenAction(ruleIndex, j, rule_new[i])
            i += 1
            j += 1
        j = 1
        while 'ELSE' in rule_new[i][0:4] or 'AND' in rule_new[i][0:3]:
            self.setRuleElseAction(ruleIndex, j, rule_new[i])
            i = i + 1
            j = j + 1
        if self.getRuleInfo().Priority[ruleIndex - 1]:
            self.setRulePriority(ruleIndex, float(rule_new[i][-1]))

    def setRuleElseAction(self, ruleIndex, actionIndex, else_action):
        """ Sets rule - based control else actions. (EPANET Version 2.2)

        Input Arguments:
         * Rule Index
         * Action Index
         * Link Index
         * Type
         * Value
        Where Type = 'STATUS' or 'SETTING' and Value = the value of STATUS/SETTING

        See more: 'https://nepis.epa.gov/Adobe/PDF/P1007WWU.pdf' (Page 164)

        The example is based on d = epanet('Net1.inp')

        Example:

        >>> d.addRules("RULE RULE-1 \n IF TANK 2 LEVEL >= 140 \n THEN PIPE 10 STATUS IS CLOSED \n ELSE PIPE 10 STATUS IS OPEN \n PRIORITY 1")   # Adds a new rule - based control
        >>> rule = d.getRules(1)   # Retrieves the 1st rule - based control
        >>> ruleIndex = 1
        >>> actionIndex = 1
        >>> else_action = 'ELSE PIPE 11 STATUS IS CLOSED'
        >>> d.setRuleElseAction(ruleIndex, actionIndex, else_action)   # Sets the new else - action in the 1st rule - based control, in the 1st else - action.
        >>> rule = d.getRules(1)

        See also setRules, setRuleThenAction, setRulePriority, getRuleInfo, getRules, addRules, deleteRules.
        """
        else_new = else_action.split()
        if else_new[3] == 'STATUS':
            status = eval('self.ToolkitConstants.EN_R_IS_' + else_new[5])
            setting = -1
        elif else_new[3] == 'SETTING':
            status = -1
            setting = float(else_new[5])
        linkIndex = self.getLinkIndex(else_new[2])
        self.api.ENsetelseaction(ruleIndex, actionIndex, linkIndex, status, setting)

    def setRulePremiseStatus(self, ruleIndex, premiseIndex, status):
        """ Sets the status being compared to in a premise of a rule-based control. (EPANET Version 2.2)

        The example is based on d = epanet('Net1.inp')

        Example:

        >>> d.getRules()
        >>> d.addRules('RULE RULE-1 \n IF LINK 110 STATUS = CLOSED \n THEN PUMP 9 STATUS IS CLOSED \n PRIORITY 1')
        >>> d.getRules(1)
        >>> ruleIndex = 1
        >>> premiseIndex = 1
        >>> status = 'OPEN'
        >>> d.setRulePremiseStatus(ruleIndex, premiseIndex, status)   # Sets the status = 'OPEN' to the 1st premise of the 1st rule - based control
        >>> d.getRules()[1]['Premises']

        See also setRulePremise, setRulePremiseObjectNameID, setRulePremiseValue, setRules, getRules, addRules, deleteRules.
        """
        if status == 'OPEN':
            status_code = self.ToolkitConstants.EN_R_IS_OPEN
        elif status == 'CLOSED':
            status_code = self.ToolkitConstants.EN_R_IS_CLOSED
        elif status == 'ACTIVE':
            status_code = self.ToolkitConstants.EN_R_IS_ACTIVE
        self.api.ENsetpremisestatus(ruleIndex, premiseIndex, status_code)

    def setRulePriority(self, ruleIndex, priority):
        """ Sets rule - based control priority. (EPANET Version 2.2)

        The example is based on d = epanet('BWSN_Network_1.inp')

        Example:

        >>> d.getRules()[1]['Rule']                  # Retrieves the 1st rule - based control
        >>> ruleIndex = 1
        >>> priority = 2
        >>> d.setRulePriority(ruleIndex, priority)   # Sets the 1st rule - based control priority = 2
        >>> d.getRules()[1]['Rule']

        See also setRules, setRuleThenAction, setRuleElseAction, getRuleInfo, getRules, addRules, deleteRules.
        """
        self.api.ENsetrulepriority(ruleIndex, priority)

    def setRuleThenAction(self, ruleIndex, actionIndex, then_action):
        """ Sets rule - based control then actions. (EPANET Version 2.2)

        Input Arguments:
          * Rule Index
          * Action Index
          * Then clause

        See more: 'https://nepis.epa.gov/Adobe/PDF/P1007WWU.pdf' (Page 164)

        The example is based on d = epanet('Net1.inp')

        Example:

          >>> d.addRules('RULE RULE-1 \n IF TANK 2 LEVEL >= 140 \n THEN PIPE 10 STATUS IS CLOSED \n ELSE PIPE 10 STATUS IS OPEN \n PRIORITY 1')   # Adds a new rule - based control
          >>> rule = d.getRules(1)   # Retrieves the 1st rule - based control
          >>> ruleIndex = 1
          >>> actionIndex = 1
          >>> then_action = 'THEN PIPE 11 STATUS IS OPEN'
          >>> d.setRuleThenAction(ruleIndex, actionIndex, then_action)
          >>> rule = d.getRules(1)

        See also setRules, setRuleElseAction, setRulePriority, getRuleInfo, getRules, addRules, deleteRules.
        """
        then_action = then_action.split()
        if then_action[3] == 'STATUS':
            status = eval('self.ToolkitConstants.EN_R_IS_' + then_action[5])
            setting = -1
        elif then_action[3] == 'SETTING':
            status = -1
            setting = float(then_action[5])
        linkIndex = self.getLinkIndex(then_action[2])
        self.api.ENsetthenaction(ruleIndex, actionIndex, linkIndex, status, setting)

    def setTimeHydraulicStep(self, value):
        """ Sets the hydraulic time step.

        Example:

        >>> Hstep = 1800
        >>> d.setTimeHydraulicStep(Hstep)
        >>> d.getTimeHydraulicStep()

        See also getTimeSimulationDuration, setTimeQualityStep, setTimePatternStep.
        """
        self.api.ENsettimeparam(self.ToolkitConstants.EN_HYDSTEP, value)

    def setTimePatternStart(self, value):
        """ Sets the time when time patterns begin.

        Example:

        >>> patternStart = 0
        >>> d.setTimePatternStart(patternStart)
        >>> d.getTimePatternStart()

        See also getTimePatternStart, setTimePatternStep, setTimeHydraulicStep.
        """
        self.api.ENsettimeparam(self.ToolkitConstants.EN_PATTERNSTART, value)

    def setTimePatternStep(self, value):
        """ Sets the time pattern step.

        Example:

        >>> patternStep = 3600
        >>> d.setTimePatternStep(patternStep)
        >>> d.getTimePatternStep()

        See also getTimePatternStep, setTimePatternStart, setTimeHydraulicStep.
        """
        self.api.ENsettimeparam(self.ToolkitConstants.EN_PATTERNSTEP, value)

    def setTimeQualityStep(self, value):
        """ Sets the quality time step.

        Example:

        >>> Qstep = 1800
        >>> d.setTimeQualityStep(Qstep)
        >>> d.getTimeQualityStep()

        See also getTimeQualityStep, setTimeHydraulicStep, setTimePatternStep.
        """
        self.api.ENsettimeparam(self.ToolkitConstants.EN_QUALSTEP, value)

    def setTimeReportingStart(self, value):
        """ Sets the time when reporting starts.

        Example:

        >>> reportingStart = 0
        >>> d.setTimeReportingStart(reportingStart)
        >>> d.getTimeReportingStart()

        See also getTimeReportingStart, setTimeReportingStep, setTimePatternStart.
        """
        self.api.ENsettimeparam(self.ToolkitConstants.EN_REPORTSTART, value)

    def setTimeReportingStep(self, value):
        """ Sets the reporting time step.

        Example:

        >>> reportingStep = 3600
        >>> d.setTimeReportingStep(reportingStep)
        >>> d.getTimeReportingStep()

        See also getTimeReportingStep(), setTimeReportingStart, setTimeRuleControlStep.
        """
        self.api.ENsettimeparam(self.ToolkitConstants.EN_REPORTSTEP, value)

    def setTimeRuleControlStep(self, value):
        """ Sets the rule-based control evaluation time step.

        Example:

        >>> ruleControlStep = 360
        >>> d.setTimeRuleControlStep(ruleControlStep)
        >>> d.getTimeRuleControlStep()

        See also getTimeRuleControlStep, setTimeReportingStep, setTimePatternStep.
        """
        self.api.ENsettimeparam(self.ToolkitConstants.EN_RULESTEP, value)

    def setTimeSimulationDuration(self, value):
        """ Sets the simulation duration (in seconds).

        Example:

        >>> simulationDuration = 172800    # 172800 seconds = 2days
        >>> d.setTimeSimulationDuration(simulationDuration)
        >>> d.getTimeSimulationDuration()

        See also getTimeSimulationDuration(), getTimeStartTime(), getTimeHaltFlag().
        """
        self.api.ENsettimeparam(self.ToolkitConstants.EN_DURATION, value)

    def setTimeStatisticsType(self, value):
        """ Sets the statistic type.

        Types that can be set:
          1) 'NONE'
          2) 'AVERAGE'
          3) 'MINIMUM'
          4) 'MAXIMUM'
          5) 'RANGE'

        Example:

        >>> d.getTimeStatisticsType()
        >>> statisticsType = 'AVERAGE'
        >>> d.setTimeStatisticsType(statisticsType)
        >>> d.getTimeStatisticsType()

        See also getTimeStatisticsType, setTimeReportingStart, setTimeReportingStep.
        """
        tmpindex = self.TYPESTATS.index(value)
        self.api.ENsettimeparam(self.ToolkitConstants.EN_STATISTIC, tmpindex)

    def setTitle(self, *argv):
        """ Sets the title lines of the project. (EPANET Version 2.2)

        Example:

        >>> line_1 = 'This is a title'
        >>> line_2 = 'This is a test line 2'
        >>> line_3 = 'This is a test line 3'
        >>> d.setTitle(line_1, line_2, line_3)
        >>> [Line1, Line2, Line3] = d.getTitle()

        See also getTitle, setLinkComment, setNodeComment.
        """
        line2 = ''
        line3 = ''
        if len(argv) > 0:
            line1 = argv[0]
        if len(argv) > 1:
            line2 = argv[1]
        if len(argv) > 2:
            line3 = argv[2]
        self.api.ENsettitle(line1, line2, line3)

    def solveCompleteHydraulics(self):
        """ Runs a complete hydraulic simulation with results for all time periods written to the binary Hydraulics file.

        Example:

        >>> d.solveCompleteHydraulics()

        See also solveCompleteQuality.
        """
        self.api.solve = 1
        self.api.ENsolveH()

    def solveCompleteQuality(self):
        """ Runs a complete water quality simulation with results at uniform reporting intervals written to EPANET's binary Output file.

        Example:

        >>> d.solveCompleteQuality()

        See also solveCompleteHydraulics.
        """
        self.api.ENsolveQ()

    def splitPipe(self, pipeID, newPipeID, newNodeID):
        """ Splits a pipe (pipeID), creating two new pipes (pipeID and newPipeID) and adds a
        junction/node (newNodeID) in between. If the pipe is linear
        the pipe is splitted in half, otherwisw the middle point of
        the vertice array elemnts is taken as the split point.
        The two new pipes have the same properties as the one which is splitted.
        The new node's properties are the same with the nodes on the left and right
        and New Node Elevation and Initial quality is the average of the two.

        Example 1: Splits pipe with ID '11' to pipes '11' and '11a' and creates the
        node '11a' in the link of the two new pipes.

        >>> d = epanet('Net1.inp')
        >>> pipeID = '11'
        >>> newPipeID = '11a'
        >>> newNodeID = '11node'
        >>> [leftPipeIndex, rightPipeIndex] = d.splitPipe(pipeID,newPipeID,newNodeID)
        >>> d.getLinkIndex()
        >>> d.getNodesConnectingLinksID()
        >>> d.plot('highlightlink', pipeID)

        Example 2: Splits pipe with ID 'P-837' to pipes 'P-837' and 'P-837a' and creates the
        node 'P-837node' in the link of the two new pipes, using vertices.
        (The new left pipe can be noticed at the top left of the plot in red colour)

        >>> d = epanet('ky10.inp')
        >>> pipeID = 'P-837'
        >>> newPipeID= 'P-837a'
        >>> newNodeID= 'P-837node'
        >>> [leftPipeIndex, rightPipeIndex] = d.splitPipe(pipeID,newPipeID,newNodeID)
        >>> d.plot('highlightlink', pipeID)
        """
        # Find the coordinates of the Nodes connected with the link/pipe
        pipeIndex = self.getLinkIndex(pipeID)
        nodesIndex = self.getLinkNodesIndex(pipeIndex)
        leftNodeIndex = nodesIndex[0]
        rightNodeIndex = nodesIndex[1]
        coordNode1 = self.getNodeCoordinates(leftNodeIndex)
        coordNode2 = self.getNodeCoordinates(rightNodeIndex)
        if coordNode1['x'] == 0 and coordNode1['y'] == 0 \
                and coordNode2['x'] == 0 and coordNode2['y'] == 0:
            raise Exception('Some nodes have zero values for coordinates')
        if (len(self.getLinkVertices()['x'][pipeIndex]) == 0):
            # Calculate mid position of the link/pipe based on nodes
            midX = (coordNode1['x'][leftNodeIndex] + coordNode2['x'][rightNodeIndex]) / 2
            midY = (coordNode1['y'][leftNodeIndex] + coordNode2['y'][rightNodeIndex]) / 2
        else:
            # Calculate mid position based on vertices pick midpoint of vertices
            xVert = self.getLinkVertices()['x'][pipeIndex]
            xMidPos = int(len(xVert) / 2)
            midX = self.getLinkVertices()['x'][pipeIndex][xMidPos]
            midY = self.getLinkVertices()['y'][pipeIndex][xMidPos]
        # Add the new node between the link/pipe and add the same properties
        # as the left node (the elevation is the average of left-right nodes)
        self.addNodeJunction(newNodeID, [midX, midY])
        newNodeIndex = self.getNodeIndex(newNodeID)
        midElev = (self.getNodeElevations(leftNodeIndex) + self.getNodeElevations(rightNodeIndex)) / 2
        self.setNodeJunctionData(newNodeIndex, midElev, 0, '')
        self.setNodeEmitterCoeff(newNodeIndex, self.getNodeEmitterCoeff(leftNodeIndex))
        if self.getQualityCode()[0] > 0:
            midInitQual = (self.getNodeInitialQuality(leftNodeIndex) + self.getNodeInitialQuality(rightNodeIndex)) / 2
            self.setNodeInitialQuality(newNodeIndex, midInitQual)
            self.setNodeSourceQuality(newNodeIndex, self.getNodeSourceQuality(leftNodeIndex)[0])
            self.setNodeSourcePatternIndex(newNodeIndex, self.getNodeSourcePatternIndex(leftNodeIndex))
            if self.getNodeSourceTypeIndex(leftNodeIndex) != 0:
                self.setNodeSourceType(newNodeIndex, self.getNodeSourceTypeIndex(leftNodeIndex))

        # Access link properties
        linkProp = self.getLinksInfo()
        linkDia = linkProp.LinkDiameter[pipeIndex - 1]
        linkLength = linkProp.LinkLength[pipeIndex - 1]
        linkRoughnessCoeff = linkProp.LinkRoughnessCoeff[pipeIndex - 1]
        linkMinorLossCoeff = linkProp.LinkMinorLossCoeff[pipeIndex - 1]
        linkInitialStatus = linkProp.LinkInitialStatus[pipeIndex - 1]
        linkInitialSetting = linkProp.LinkInitialSetting[pipeIndex - 1]
        linkBulkReactionCoeff = linkProp.LinkBulkReactionCoeff[pipeIndex - 1]
        linkWallReactionCoeff = linkProp.LinkWallReactionCoeff[pipeIndex - 1]
        # Delete the link/pipe that is splitted
        self.deleteLink(pipeID)

        # Add two new pipes
        # d.addLinkPipe(pipeID, fromNode, toNode)
        # Add the Left Pipe and add the same properties as the deleted link
        leftNodeID = self.getNodeNameID(leftNodeIndex)
        leftPipeIndex = self.addLinkPipe(pipeID, leftNodeID, newNodeID)
        self.setNodesConnectingLinksID(leftPipeIndex, leftNodeID, newNodeID)
        self.setLinkPipeData(leftPipeIndex, linkLength, linkDia, linkRoughnessCoeff, linkMinorLossCoeff)
        if linkMinorLossCoeff != 0:
            self.setLinklinkMinorLossCoeff(leftPipeIndex, linkMinorLossCoeff)
        self.setLinkInitialSetting(leftPipeIndex, linkInitialSetting)
        self.setLinkInitialSetting(leftPipeIndex, linkInitialSetting)
        self.setLinkBulkReactionCoeff(leftPipeIndex, linkBulkReactionCoeff)
        self.setLinkWallReactionCoeff(leftPipeIndex, linkWallReactionCoeff)
        self.setLinkTypePipe(leftPipeIndex)
        # Add the Right Pipe and add the same properties as the deleted link
        rightNodeID = self.getNodeNameID(rightNodeIndex)
        rightPipeIndex = self.addLinkPipe(newPipeID, newNodeID, rightNodeID)
        self.setNodesConnectingLinksID(rightPipeIndex, newNodeID, rightNodeID)
        self.setLinkPipeData(rightPipeIndex, linkLength, linkDia, linkRoughnessCoeff, linkMinorLossCoeff)
        if linkMinorLossCoeff != 0:
            self.setLinklinkMinorLossCoeff(rightPipeIndex, linkMinorLossCoeff)
        self.setLinkInitialStatus(rightPipeIndex, linkInitialStatus)
        self.setLinkInitialSetting(rightPipeIndex, linkInitialSetting)
        self.setLinkBulkReactionCoeff(rightPipeIndex, linkBulkReactionCoeff)
        self.setLinkWallReactionCoeff(rightPipeIndex, linkWallReactionCoeff)
        self.setLinkTypePipe(rightPipeIndex)
        return [leftPipeIndex, rightPipeIndex]

    def stepQualityAnalysisTimeLeft(self):
        """ Advances the water quality simulation one water quality time step.
        The time remaining in the overall simulation is returned in tleft.

        Example:

        >>> tleft = d.stepQualityAnalysisTimeLeft()

        For more, you can type `help getNodePressure` and check examples 3 & 4.

        See also runQualityAnalysis, closeQualityAnalysis.
        """
        return self.api.ENstepQ()

    def to_array(self, list_value):
        """ Transforms a list to numpy.array type """
        return np.array(list_value)

    def to_mat(self, list_value):
        """ Transforms a list to numpy.array type """
        return np.mat(list_value)

    def initializeHydraulicAnalysis(self, *argv):
        """ Initializes storage tank levels, link status and settings, and the simulation clock time prior to running a hydraulic analysis.

        Codes:
          1) NOSAVE        = 0,    Don't save hydraulics  don't re-initialize flows
          2) SAVE          = 1,    Save hydraulics to file, don't re-initialize flows
          3) INITFLOW      = 10,   Don't save hydraulics  re-initialize flows
          4) SAVE_AND_INIT = 11    Save hydraulics  re-initialize flows

        Example 1:

        >>> d.initializeHydraulicAnalysis()     # Uses the default code i.e. SAVE = 1

        Example 2:

        >>> code = 0                            # i.e. Don't save
        >>> d.initializeHydraulicAnalysis(code)

        For more, you can type `help d.getNodePressure` and check examples 3 & 4.

        See also saveHydraulicFile, initializeQualityAnalysis.
        """
        code = self.ToolkitConstants.EN_SAVE
        if len(argv) > 0:
            code = argv[0]
        return self.api.ENinitH(code)

    def nextHydraulicAnalysisStep(self):
        """ Determines the length of time until the next hydraulic event occurs in an extended period simulation.

        Example:

        >>> d.nextHydraulicAnalysisStep()

        For more, you can type `help (d.getNodePressure)` and check examples 3 & 4.

        See also nextQualityAnalysisStep, runHydraulicAnalysis.
        """
        return self.api.ENnextH()

    def openHydraulicAnalysis(self):
        """ Opens the hydraulics analysis system.

        Example:

        >>> d.openHydraulicAnalysis()

        For more, you can type `help d.getNodePressure` and check examples 3 & 4.

        See also openQualityAnalysis, initializeHydraulicAnalysis.
        """
        self.api.ENopenH()

    def plot(self, title=None, line=None, point=None, nodesID=None,
             nodesindex=None, linksID=None, linksindex=None, highlightlink=None,
             highlightnode=None, legend=True, fontsize=5, figure=True,
             elevation=None, elevation_text=False, pressure=None, pressure_text=False,
             flow=None, flow_text=False, colorbar='turbo', min_colorbar=None, max_colorbar=None,
             colors=None, colorbar_label=None, *argv):
        """ Plot Network, show all components, plot pressure/flow/elevation

        Example 1:

        >>> d = epanet('Net1.inp')
        >>> d.plot()                                   # Plot Net1.inp network

        Example 2:

        >>> d = epanet('Net1.inp')                     # Run hydralic analysis and plot the pressures at 10hrs
        >>> d.openHydraulicAnalysis()
        >>> d.initializeHydraulicAnalysis()
        >>> tstep, P = 1, []
        >>> while tstep>0:
        ...    t = d.runHydraulicAnalysis()
        ...    P.append(d.getNodePressure())
        ...    tstep=d.nextHydraulicAnalysisStep()
        >>> d.closeHydraulicAnalysis()
        >>> hr = 10
        >>> d.plot(pressure = P[hr])
        """
        plot_links = True
        plot_nodes = True
        fix_colorbar = False
        text_links_ID = False
        text_links_ind = False
        text_nodes_ID = False
        text_nodes_ind = False
        text_nodes_ID_spec = False
        text_nodes_ind_spec = False
        text_links_ID_spec = False
        text_links_ind_spec = False
        nodes_to_show_ID = []
        nodes_to_show_ind = []
        links_to_show_ID = []
        links_to_show_ind = []
        links_ind = self.getLinkIndex()
        links_ID = self.getLinkNameID()

        if point is True:
            plot_links = False
        if line is True:
            plot_nodes = False
        if linksID is not None:
            text_links_ID_spec = True
            links_to_show_ID = linksID
        if linksID is True:
            text_links_ID = True
        if linksindex is not None:
            links_to_show_ind = linksindex
            text_links_ind_spec = True
        if linksindex is True:
            text_links_ind = True
        if nodesID is not None:
            valves_ID = self.getLinkValveNameID()
            junc_ID = self.getNodeJunctionNameID()
            res_ID = self.getNodeReservoirNameID()
            tank_ID = self.getNodeTankNameID()
            text_nodes_ID_spec = True
            nodes_to_show_ID = nodesID
        if nodesID is True:
            text_nodes_ID = True
        if nodesindex is not None:
            nodes_to_show_ind = nodesindex
            text_nodes_ind_spec = True
        if nodesindex is True:
            text_nodes_ind = True

        if pressure is not None:
            plot_nodes = False
            legend = False
            fix_colorbar = True
            if colorbar_label is None:
                colorbar_label = 'Pressure (' + self.units.NodePressureUnits + ')'
            if colors is None:
                if min_colorbar is None:
                    min_colorbar = np.min(pressure)
                if max_colorbar is None:
                    max_colorbar = np.max(pressure)
            if pressure is True:
                pressure = self.getNodePressure()
            else:
                pressure = np.squeeze(np.asarray(pressure))
            if pressure_text is True:
                plot_nodes = True
        if elevation is not None:
            plot_nodes = False
            legend = False
            if colors is None:
                if min_colorbar is None:
                    min_colorbar = np.min(elevation)
                if max_colorbar is None:
                    max_colorbar = np.max(elevation)
            if colorbar_label is None:
                colorbar_label = 'Elevation (' + self.units.NodeElevationUnits + ')'
            if elevation is True:
                elevation = self.getNodeElevations()
            else:
                elevation = np.squeeze(np.asarray(elevation))
            if elevation_text is True:
                plot_nodes = True
        if flow is not None:
            fix_colorbar = True
            if colorbar_label is None:
                colorbar_label = 'Flow (' + self.units.LinkFlowUnits + ')'
            legend = False
            if flow is True:
                flow = self.getLinkFlows()
            else:
                flow = np.squeeze(np.asarray(flow))
            if colors is None:
                if min_colorbar is None:
                    min_colorbar = np.min(flow)
                if max_colorbar is None:
                    max_colorbar = np.max(flow)
                Flow_new = [(i - min_colorbar) / (max_colorbar - min_colorbar) for i in flow]
                colors = eval(f"cm.{colorbar}(Flow_new)")

        # get info from EN functions
        nodenameid = self.getNodeNameID()
        linknameid = self.getLinkNameID()
        if len(nodenameid) == 0 or len(linknameid) == 0:
            raise Exception('Not enough network nodes/links.')
        nodeconlinkIndex = self.getNodesConnectingLinksIndex()
        pumpindex = self.getLinkPumpIndex()
        pipeindex = self.getLinkPipeIndex()
        valveindex = list(self.getLinkValveIndex())
        juncind = self.getNodeJunctionIndex()
        resindex = self.getNodeReservoirIndex()
        tankindex = self.getNodeTankIndex()
        nodecoords = self.getNodeCoordinates()

        # Create figure
        plt.rcParams["figure.figsize"] = [3, 2]
        plt.rcParams['figure.dpi'] = 300
        if figure:
            plt.figure()
        plt.axis('off')

        if fix_colorbar and flow is not None:
            scal = cm.ScalarMappable(norm=mpl.colors.Normalize(min_colorbar, max_colorbar), cmap=colorbar)
            bar = plt.colorbar(scal, orientation='horizontal', shrink=0.7, pad=0.05)
            bar.ax.tick_params(labelsize=fontsize)
            bar.outline.set_visible(False)
            bar.set_label(label=colorbar_label, size=fontsize)

        # Plot Links
        if plot_links:
            x, y = [0, 0], [0, 0]
            for i in links_ind:
                fromNode = nodeconlinkIndex[i - 1][0]
                toNode = nodeconlinkIndex[i - 1][1]
                x[0] = nodecoords['x'][fromNode]
                y[0] = nodecoords['y'][fromNode]
                x[1] = nodecoords['x'][toNode]
                y[1] = nodecoords['y'][toNode]
                if not nodecoords['x_vert'][i]: # Check if not vertices
                    if fix_colorbar and flow is not None:
                        plt.plot(x, y, '-', linewidth=0.7, zorder=0, color=colors[i - 1])
                    else:
                        if i != pipeindex[-1]:
                            plt.plot(x, y, color='steelblue', linewidth=0.2, zorder=0)
                        else:
                            plt.plot(x, y, color='steelblue', linewidth=0.2, zorder=0, label='Pipes')

                    if text_links_ID or (text_links_ID_spec and links_ID[i - 1] in links_to_show_ID):
                        plt.text(
                            (x[0] + x[1]) / 2, (y[0] + y[1]) / 2, links_ID[i - 1], {'fontsize': fontsize}
                        )
                    elif text_links_ind or (text_links_ind_spec and i in links_to_show_ind):
                        plt.text(
                            (x[0] + x[1]) / 2, (y[0] + y[1]) / 2, links_ind[i - 1], {'fontsize': fontsize}
                        )
                    if flow_text:
                        plt.text(
                            (x[0] + x[1]) / 2, (y[0] + y[1]) / 2, "{:.2f}".format(flow[i - 1]), {'fontsize': fontsize}
                        )
                else:
                    xV_old = x[0]
                    yV_old = y[0]
                    for j in range(len(nodecoords['x_vert'][i])):
                        xV = nodecoords['x_vert'][i][j]
                        yV = nodecoords['y_vert'][i][j]
                        if fix_colorbar and flow is not None:
                            plt.plot([xV_old, xV], [yV_old, yV], '-', linewidth=1, zorder=0, color=colors[i])
                        else:
                            plt.plot([xV_old, xV], [yV_old, yV], color='steelblue', linewidth=0.2, zorder=0)
                        xV_old = xV
                        yV_old = yV
                    if fix_colorbar and flow is not None:
                        plt.plot([xV, x[1]], [yV, y[1]], '-', linewidth=1, zorder=0, color=colors[i])
                    else:
                        plt.plot([xV, x[1]], [yV, y[1]], color='steelblue', linewidth=0.2, zorder=0)
                    if text_links_ID or (text_links_ID_spec and links_ID[i - 1] in links_to_show_ID):
                        plt.text(
                            nodecoords['x_vert'][i][int(len(nodecoords['x_vert'][i]) / 2)],
                            nodecoords['y_vert'][i][int(len(nodecoords['x_vert'][i]) / 2)],
                            links_ID[i], {'fontsize': 'xx-small'}
                        )
                    elif text_links_ind or (text_links_ind_spec and i in links_to_show_ind):
                        plt.text(
                            nodecoords['x_vert'][i][int(len(nodecoords['x_vert'][i]) / 2)],
                            nodecoords['y_vert'][i][int(len(nodecoords['x_vert'][i]) / 2)],
                            links_ind[i], {'fontsize': fontsize}
                        )
                    if flow_text:
                        plt.text(
                            nodecoords['x_vert'][i][int(len(nodecoords['x_vert'][i]) / 2)],
                            nodecoords['y_vert'][i][int(len(nodecoords['x_vert'][i]) / 2)],
                            "{:.2f}".format(flow[i - 1]), {'fontsize': fontsize}
                        )

            if not line:
                # Plot Pumps
                x, y = [0, 0], [0, 0]
                for i in pumpindex:
                    fromNode = nodeconlinkIndex[i - 1][0]
                    toNode = nodeconlinkIndex[i - 1][1]
                    x[0] = nodecoords['x'][fromNode]
                    y[0] = nodecoords['y'][fromNode]
                    x[1] = nodecoords['x'][toNode]
                    y[1] = nodecoords['y'][toNode]
                    xx = (x[0] + x[1]) / 2
                    yy = (y[0] + y[1]) / 2
                    if i != pumpindex[-1]:
                        plt.plot(xx, yy, color='fuchsia', marker='v', linestyle='None', markersize=0.8)
                    else:
                        plt.plot(xx, yy, color='fuchsia', marker='v', linestyle='None', markersize=0.8, label='Pumps')

                # Plot Valves
                for i in valveindex: 
                    if not nodecoords['x_vert'][i]: # Check if not vertices
                        fromNode = nodeconlinkIndex[i - 1][0]
                        toNode = nodeconlinkIndex[i - 1][1]
                        x[0] = nodecoords['x'][fromNode]
                        y[0] = nodecoords['y'][fromNode]
                        x[1] = nodecoords['x'][toNode]
                        y[1] = nodecoords['y'][toNode]
                        xx = (x[0] + x[1]) / 2
                        yy = (y[0] + y[1]) / 2
                    else:
                        xVert = nodecoords['x_vert'][i]
                        yVert = nodecoords['y_vert'][i] 
                        xx = xVert[math.floor(xVert.index(xVert[-1])/2)]
                        yy = yVert[math.floor(yVert.index(yVert[-1])/2)]
                    if i != valveindex[-1]:
                        plt.plot(xx, yy, 'k*', markersize=1.5)
                    else:
                        plt.plot(xx, yy, 'k*', markersize=1.5, label='Valves')
                    if text_nodes_ID or (text_nodes_ID_spec and valves_ID[valveindex.index(i)] in nodes_to_show_ID):
                        plt.text(xx, yy, valves_ID[valveindex.index(i)], {'fontsize': fontsize})
                    elif text_nodes_ind or (text_nodes_ind_spec and i in nodes_to_show_ind):
                        plt.text(xx, yy, i, {'fontsize': fontsize})
                    if pressure_text:
                        plt.text(xx, yy, "{:.2f}".format(pressure[i - 1]),
                                {'fontsize': fontsize})


        if highlightlink is not None:
            if type(highlightlink) == str:
                lindex = self.getLinkIndex(highlightlink)
            else:
                lindex = highlightlink
            lNodesInd = self.getLinkNodesIndex(lindex)
            xy = self.getNodeCoordinates(lNodesInd)
            x_from_to = list(xy['x'].values())
            y_from_to = list(xy['y'].values())
            if self.getLinkVerticesCount(lindex) == 0:
                plt.plot(x_from_to, y_from_to, 'r-', linewidth=1, zorder=0)
            else:
                vertXY = self.getLinkVertices(lindex)
                x = [x_from_to[0]]
                x.extend(list(vertXY['x'].values())[0])
                x.append(x_from_to[1])
                y = [y_from_to[0]]
                y.extend(list(vertXY['y'].values())[0])
                y.append(y_from_to[1])
                xV_old = x[0]
                yV_old = y[0]
                for i in range(len(x)):
                    plt.plot([xV_old, x[i]], [yV_old, y[i]], 'r-',
                             linewidth=1.5, zorder=0)
                    xV_old = x[i]
                    yV_old = y[i]

        if plot_nodes:
            # Plot Tanks
            for i in tankindex:
                x = nodecoords['x'][i]
                y = nodecoords['y'][i]
                if i != tankindex[-1]:
                    plt.plot(x, y, color='cyan', marker='*', linestyle='None', markersize=3.5, zorder=0)
                else:
                    plt.plot(x, y, color='cyan', marker='*', linestyle='None', markersize=3.5, label='Tanks', zorder=0)
                if text_nodes_ID or (text_nodes_ID_spec and tank_ID[tankindex.index(i)] in nodes_to_show_ID):
                    plt.text(x, y, tank_ID[tankindex.index(i)], {'fontsize': fontsize})
                elif text_nodes_ind or (text_nodes_ind_spec and i in nodes_to_show_ind):
                    plt.text(x, y, i, {'fontsize': fontsize})
                if pressure_text:
                    plt.text(x, y, "{:.2f}".format(pressure[i - 1]), {'fontsize': fontsize})

            # Plot Reservoirs
            for i in resindex:
                x = nodecoords['x'][i]
                y = nodecoords['y'][i]
                if i != resindex[-1]:
                    plt.plot(x, y, color='lime', marker='s', linestyle='None', markersize=1.5, zorder=0)
                else:
                    plt.plot(x, y, color='lime', marker='s', linestyle='None', markersize=1.5, label='Reservoirs',
                             zorder=0)
                if text_nodes_ID or (text_nodes_ID_spec and res_ID[resindex.index(i)] in nodes_to_show_ID):
                    plt.text(x, y, res_ID[resindex.index(i)], {'fontsize': fontsize})
                elif text_nodes_ind or (text_nodes_ind_spec and i in nodes_to_show_ind):
                    plt.text(x, y, i, {'fontsize': fontsize})
                if pressure_text:
                    plt.text(x, y, "{:.2f}".format(pressure[i - 1]), {'fontsize': fontsize})

            # Plot Junctions
            for i in juncind:
                x = nodecoords['x'][i]
                y = nodecoords['y'][i]
                if i != juncind[-1]:
                    plt.plot(x, y, 'bo', markersize=0.7, zorder=0)
                else:
                    plt.plot(x, y, 'bo', markersize=0.7, label='Junctions', zorder=0)
                if text_nodes_ID or (text_nodes_ID_spec and junc_ID[juncind.index(i)] in nodes_to_show_ID):
                    plt.text(x, y, junc_ID[juncind.index(i)], {'fontsize': fontsize})
                elif text_nodes_ind or (text_nodes_ind_spec and i in nodes_to_show_ind):
                    plt.text(x, y, i, {'fontsize': fontsize})
                if pressure_text:
                    plt.text(x, y, "{:.2f}".format(pressure[i - 1]), {'fontsize': fontsize})

        if elevation is not None:
            # Plot Elevation
            if elevation is True:
                elevation = self.getNodeElevations()
            # plot pressure nodes
            x = list(nodecoords['x'].values())
            y = list(nodecoords['y'].values())
            plt.scatter(x, y, c=elevation, cmap=colorbar, s=3.5, zorder=2)
            # Plot details
            bar = plt.colorbar(orientation='horizontal', shrink=0.7, pad=0.05)
            bar.ax.tick_params(labelsize=fontsize)
            bar.outline.set_visible(False)
            bar.set_label(label=colorbar_label, size=fontsize)

        if pressure is not None:
            # Plot pressure
            x = list(nodecoords['x'].values())
            y = list(nodecoords['y'].values())
            plt.scatter(x, y, c=pressure, cmap=colorbar, s=3.5, zorder=2)
            scal = cm.ScalarMappable(norm=mpl.colors.Normalize(min_colorbar, max_colorbar), cmap=colorbar)
            bar = plt.colorbar(scal, orientation='horizontal', shrink=0.7, pad=0.05)
            bar.ax.tick_params(labelsize=fontsize)
            bar.outline.set_visible(False)
            bar.set_label(label=colorbar_label, size=fontsize)

        if highlightnode is not None:
            nodeIndices = self.__getNodeIndices(highlightnode)
            for i in nodeIndices:
                temp_coords = self.getNodeCoordinates(i)
                plt.plot(temp_coords['x'][i], temp_coords['y'][i], '.r', markersize=3.5)

        if legend:
            leg = plt.legend(loc=0, fontsize=fontsize, markerscale=1)
            frame = leg.get_frame()
            # frame.set_edgecolor('black')
            frame.set_linewidth(0.3)

        if title is not None:
            plt.title(title, fontsize=fontsize, fontweight="bold")
        if figure:
            plt.show(block=False)

    def plot_close(self):
        """ Close all open figures
        """
        plt.close("all")

    def plot_show(self):
        """ Show plot
        """
        plt.show()

    def plot_ts(self, X=None, Y=None, title='', xlabel='', ylabel='', color='b', marker='x',
                figure_size=[3, 2.5], constrained_layout=True, fontsize=5):
        """ Plot X Y data
        """
        plt.rc('xtick', labelsize=fontsize - 1)
        plt.rc('ytick', labelsize=fontsize - 1)
        plt.figure(figsize=figure_size, constrained_layout=constrained_layout)
        if marker:
            if X is None:
                plt.plot(Y, color=color, marker=marker)
            else:
                plt.plot(X, Y, color=color, marker=marker)
        else:
            if X is None:
                plt.plot(Y, color=color, linewidth=1)
            else:
                plt.plot(X, Y, color=color, linewidth=1)
        plt.xlabel(xlabel, fontsize=fontsize)
        plt.ylabel(ylabel, fontsize=fontsize)
        plt.title(title, fontsize=fontsize, fontweight="bold")
        # plt.tight_layout()
        plt.show(block=False)

    def printv(self, var):
        try:
            frame = currentframe().f_back
            v = getframeinfo(frame).code_context[0]
            r = re.search(r"\((.*)\)", v).group(1)
            print("{} = {}".format(r, var))
        except:
            print(var)

    def runHydraulicAnalysis(self):
        """ Runs a single period hydraulic analysis, retrieving the current simulation clock time t.

        Example:

        >>> tstep = d.runHydraulicAnalysis()

        For more, you can type `help getNodePressure` and check examples 3 & 4.

        See also runQualityAnalysis, initializeHydraulicAnalysis.
        """
        return self.api.ENrunH()

    def unload(self):
        """ unload() library and close the EPANET Toolkit system.

        Example:

        >>> d.unload()

        See also epanet, saveInputFile, closeNetwork().
        """
        self.api.ENclose()
        try:
            os.remove(self.TempInpFile)
        except:
            pass

        try:
            os.remove(self.TempInpFile[0:-4] + '.txt')
            os.remove(self.InputFile[0:-4] + '.txt')
            os.remove(self.BinTempfile)
        except:
            pass
        for file in Path(".").glob("@#*.txt"):
            file.unlink()

        print(f'Close toolkit for the input file "{self.netName[0:-4]}". EPANET Toolkit is unloaded.\n')

    def useHydraulicFile(self, hydname):
        """ Uses the contents of the specified file as the current binary hydraulics file.

        Example:

        >>> filename = 'test.hyd'
        >>> d.useHydraulicFile(filename)

        See also saveHydraulicFile, initializeHydraulicAnalysis.
        """
        self.api.ENusehydfile(hydname)

    def writeLineInReportFile(self, line):
        """ Writes a line of text to the EPANET report file.

        Example:

        >>> line = 'Status YES'
        >>> d.writeLineInReportFile(line)

        See also writeReport, copyReport.
        """
        self.api.ENwriteline(line)

    def writeReport(self):
        """ Writes a formatted text report on simulation results to the Report file.

        Example:

        >>> d = epanet('Net1.inp')
        >>> d.solveCompleteHydraulics()
        >>> d.solveCompleteQuality()
        >>> d.setReportFormatReset()
        >>> d.setReport('FILE TestReport3.txt')
        >>> d.setReport('NODES ALL')
        >>> d.setReport('LINKS ALL')
        >>> d.writeReport()
        >>> report_file_string = open('TestReport3.txt').read()

        See also copyReport, writeLineInReportFile.
        """
        self.api.ENreport()


    ######### PRIVATE FUNCTIONS ############

    def __addComment(self, code, value, *argv):
        if len(argv) == 1:
            indices = value
            value = argv[0]
        else:
            indices = self.__getNodeIndices(*argv)
        if not isList(indices):
            self.api.ENsetcomment(code, indices, value)
        else:
            for i in indices:
                self.api.ENsetcomment(code, i, value[indices.index(i)])

    def __addControlFunction(self, value):
        if isList(value):
            controlRuleIndex = []
            for c in value:
                [controlTypeIndex, linkIndex, controlSettingValue, nodeIndex, controlLevel] = self.__controlSettings(
                    c)
                controlRuleIndex.append(self.api.ENaddcontrol(controlTypeIndex, linkIndex,
                                                              controlSettingValue, nodeIndex, controlLevel))
        else:
            [controlTypeIndex, linkIndex, controlSettingValue, nodeIndex, controlLevel] = self.__controlSettings(value)
            controlRuleIndex = self.api.ENaddcontrol(controlTypeIndex, linkIndex,
                                                     controlSettingValue, nodeIndex, controlLevel)
        return controlRuleIndex

    def __changeNodeType(self, Id, Type):
        # Change the type of node to junction, reservoir or tank
        # The new node has the coordinates and elevation of the deleted
        # node
        # Get node coordinates and info
        oldIndex = self.getNodeIndex(Id)
        nodeCoords = self.getNodeCoordinates(oldIndex)
        vertCoords = self.getLinkVertices()
        if (nodeCoords['x'][oldIndex] == 0 and nodeCoords['y'][oldIndex] == 0):
            warnings.warn('Node has zero value for coordinates')
        # Get the elevation
        elev = self.getNodeElevations(oldIndex)
        # Get the connected links and link info
        connLinkMat = self.getNodesConnectingLinksID()
        lInfo = self.getLinksInfo()
        linkTypeMat = self.getLinkType()
        linkMat, linktypeMat, linknodeIndex, linknodeIndices, choiceMat = [], [], [], [], []
        # Get data of nameID and type for connected links
        for i in range(len(connLinkMat)):
            if connLinkMat[i][0] == Id:
                linkMat.append(connLinkMat[i][1])
                linktypeMat.append(linkTypeMat[i])
                linknodeIndex.append(self.getNodeIndex(connLinkMat[i][1]))
                linknodeIndices.append(i + 1)
                choiceMat.append(1 + 1)
            elif connLinkMat[i][1] == Id:
                linkMat.append(connLinkMat[i][0])
                linktypeMat.append(linkTypeMat[i])
                linknodeIndex.append(self.getNodeIndex(connLinkMat[i][0]))
                linknodeIndices.append(i + 1)
                choiceMat.append(2)
        # Delete the node to be replaced
        self.deleteNode(oldIndex)
        # Create a new node according to the type
        nodeCoords = [nodeCoords['x'][oldIndex], nodeCoords['y'][oldIndex]]
        if Type == 0:
            # Add new jucntion with previous nodes coordinates and elevation
            index = self.addNodeJunction(Id, nodeCoords, elev)
        elif Type == 1:
            # Add new reservoir with previous nodes coordinates and elevation
            index = self.addNodeReservoir(Id, nodeCoords, elev)
        elif Type == 2:
            # Add new tank with previous nodes coordinates and elevation
            index = self.addNodeTank(Id, nodeCoords, elev)
        # Add the deleted links with the newIndex
        for i in range(len(linkMat)):
            linkId = 'L_' + Id + str(i)
            lType_code = eval('self.ToolkitConstants.EN_' + linktypeMat[i])
            # Add a link
            # Check which node x coordinate is smaller to set it as the start
            if choiceMat[i] == 1:
                lindex = self.api.ENaddlink(linkId, lType_code, Id, linkMat[i])
            else:
                lindex = self.api.ENaddlink(linkId, lType_code, linkMat[i], Id)
            # add attributes to the new links
            self.setLinkLength(lindex, lInfo.LinkLength[linknodeIndices[i]])
            self.setLinkDiameter(lindex, lInfo.LinkDiameter[linknodeIndices[i]])
            self.setLinkRoughnessCoeff(lindex, lInfo.LinkRoughnessCoeff[linknodeIndices[i]])
            if lInfo.LinkMinorLossCoeff[linknodeIndices[i]]:
                self.setLinkMinorLossCoeff(lindex, lInfo.LinkMinorLossCoeff[linknodeIndices(i)])
            self.setLinkInitialStatus(lindex, lInfo.LinkInitialStatus[linknodeIndices[i]])
            self.setLinkInitialSetting(lindex, lInfo.LinkInitialSetting[linknodeIndices[i]])
            self.setLinkBulkReactionCoeff(lindex, lInfo.LinkBulkReactionCoeff[linknodeIndices[i]])
            self.setLinkWallReactionCoeff(lindex, lInfo.LinkWallReactionCoeff[linknodeIndices[i]])
            if len(vertCoords['x'][linknodeIndices[i]]) != 0:
                # Add vertices with neighbour nodes
                xCoord = vertCoords['x'][linknodeIndices[i]]
                yCoord = vertCoords['y'][linknodeIndices[i]]
                self.setLinkVertices(linkId, xCoord, yCoord)
        return index

    def __checkLinkIfString(self, value):
        if type(value) is str:
            return self.getLinkIndex(value)
        else:
            return value

    def __controlSettings(self, value):
        splitControl = value.split()
        try:
            controlSettingValue = self.TYPESTATUS.index(splitControl[2])
        except:
            if splitControl[2] == 'CLOSE':
                controlSettingValue = 0
            else:
                # control setting Value (type should be int) for pump or valve
                controlSettingValue = float(splitControl[2])
        linkIndex = self.getLinkIndex(splitControl[1])
        if not linkIndex:
            raise Exception('Wrong link ID. Please change your control.')
        if splitControl[3] == 'IF':
            # LINK linkID status IF NODE nodeID ABOVE/BELOW value
            nodeIndex = self.getNodeIndex(splitControl[5])
            controlTypeIndex = 0  # LOWLEVEL
            if splitControl[6] == 'ABOVE':
                controlTypeIndex = 1  # HIGHLEVEL
            controlLevel = float(splitControl[7])
        if splitControl[3] == 'AT':
            if splitControl[4] == 'CLOCKTIME':
                # LINK linkID status AT CLOCKTIME clocktime AM/PM
                nodeIndex = 0
                controlTypeIndex = 3
            else:
                # LINK linkID status AT TIME time
                nodeIndex = 0
                controlTypeIndex = 2
            if ':' not in splitControl[5]:
                controlLevel = int(splitControl[5])
            else:
                time_ = splitControl[5].split(':')
                controlLevel = int(time_[0]) * 3600 + int(time_[1]) * 60
        return [controlTypeIndex, linkIndex, controlSettingValue, nodeIndex, controlLevel]

    def __createTempfiles(self, BinTempfile):
        inpfile = BinTempfile
        uuID = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        rptfile = '@#' + uuID + '.txt'
        binfile = '@#' + uuID + '.bin'
        return [inpfile, rptfile, binfile]

    def __getControlIndices(self, *argv):
        if len(argv) == 0:
            indices = list(range(1, self.getControlRulesCount() + 1))
        else:
            indices = argv[0]
        return indices

    def __getCurveIndices(self, *argv):
        if len(argv) == 0:
            numCurves = self.getCurveCount()
            return list(range(1, numCurves + 1))
        else:
            return argv[0]

    def __getInitParams(self):
        # Retrieve all initial parameters from the inp file
        self.CMDCODE = 1
        self.linkInfo = self.getLinksInfo().to_dict()
        self.nodeInfo = self.getNodesInfo().to_dict()
        self.demModelInfo = self.getDemandModel()
        self.libFunctions = self.getLibFunctions()
        self.NodeCount = self.getNodeCount()
        self.NodeTankReservoirCount = self.getNodeTankReservoirCount()
        self.LinkCount = self.getLinkCount()
        self.PatternCount = self.getPatternCount()
        self.CurveCount = self.getCurveCount()
        self.CurveIndex = self.getCurveIndex()
        self.ControlRulesCount = self.getControlRulesCount()
        self.NodeJunctionCount = self.getNodeJunctionCount()
        self.LinkType = self.getLinkType()
        self.NodeType = self.getNodeType()
        self.LinkPipeCount = self.getLinkPipeCount()
        self.LinkPumpCount = self.getLinkPumpCount()
        self.NodeReservoirCount = self.getNodeReservoirCount()
        self.NodeTankCount = self.getNodeTankCount()
        self.LinkValveCount = self.getLinkValveCount()
        self.Controls = self.getControls()
        self.LinkFlowUnits = self.getFlowUnits()
        self.LinkNameID = self.getLinkNameID()
        self.LinkIndex = self.getLinkIndex()
        self.LinkPipeIndex = self.getLinkPipeIndex()
        self.LinkPumpIndex = self.getLinkPumpIndex()
        self.LinkValveIndex = self.getLinkValveIndex()
        self.LinkPipeNameID = self.getLinkPipeNameID()
        self.LinkPumpNameID = self.getLinkPumpNameID()
        self.LinkValveNameID = self.getLinkValveNameID()
        self.NodeNameID = self.getNodeNameID()
        self.NodesConnectingLinksID = self.getNodesConnectingLinksID()
        self.NodesConnectingLinksIndex = self.getNodesConnectingLinksIndex()
        self.NodeIndex = self.getNodeIndex()
        self.NodeReservoirIndex = self.getNodeReservoirIndex()
        self.NodeTankIndex = self.getNodeTankIndex()
        self.NodeJunctionIndex = self.getNodeJunctionIndex()
        self.NodeReservoirNameID = self.getNodeReservoirNameID()
        self.NodeTankNameID = self.getNodeTankNameID()
        self.NodeJunctionNameID = self.getNodeJunctionNameID()
        self.NodePatternIndex = self.getNodePatternIndex()
        self.NodeBaseDemands = self.getNodeBaseDemands()
        self.NodeTankInitialLevel = self.getNodeTankInitialLevel()
        self.NodeTankInitialWaterVolume = self.getNodeTankInitialWaterVolume()
        self.NodeTankMixingModelCode = self.getNodeTankMixingModelCode()
        self.NodeTankMixingModelType = self.getNodeTankMixingModelType()
        self.NodeTankMixZoneVolume = self.getNodeTankMixZoneVolume()
        self.NodeTankDiameter = self.getNodeTankDiameter()
        self.NodeTankMinimumWaterVolume = self.getNodeTankMinimumWaterVolume()
        self.NodeTankVolumeCurveIndex = self.getNodeTankVolumeCurveIndex()
        self.NodeTankMinimumWaterLevel = self.getNodeTankMinimumWaterLevel()
        self.NodeTankMaximumWaterLevel = self.getNodeTankMaximumWaterLevel()
        self.NodeTankMinimumFraction = self.getNodeTankMixingFraction()
        self.NodeTankBulkReactionCoeff = self.getNodeTankBulkReactionCoeff()
        self.OptionsMaxTrials = self.getOptionsMaxTrials()
        self.OptionsAccuracyValue = self.getOptionsAccuracyValue()
        self.OptionsQualityTolerance = self.getOptionsQualityTolerance()
        self.OptionsEmitterExponent = self.getOptionsEmitterExponent()
        self.OptionsPatternDemandMultiplier = self.getOptionsPatternDemandMultiplier()
        self.OptionsHeadError = self.getOptionsHeadError()
        self.OptionsFlowChange = self.getOptionsFlowChange()
        self.OptionsHeadLossFormula = self.getOptionsHeadLossFormula()
        self.PatternNameID = self.getPatternNameID()
        self.PatternIndex = self.getPatternIndex()
        self.PatternLengths = self.getPatternLengths()
        self.Pattern = self.getPattern()
        self.QualityCode = self.getQualityCode()
        self.QualityTraceNodeIndex = self.getQualityTraceNodeIndex()
        self.QualityType = self.getQualityType()
        n = self.getQualityInfo()
        self.QualityChemUnits = n.QualityChemUnits
        self.QualityChemName = n.QualityChemName
        self.TimeSimulationDuration = self.getTimeSimulationDuration()
        self.TimeHydraulicStep = self.getTimeHydraulicStep()
        self.TimeQualityStep = self.getTimeQualityStep()
        self.TimePatternStep = self.getTimePatternStep()
        self.TimePatternStart = self.getTimePatternStart()
        self.TimeReportingStep = self.getTimeReportingStep()
        self.TimeReportingStart = self.getTimeReportingStart()
        self.TimeRuleControlStep = self.getTimeRuleControlStep()
        self.TimeStatisticsIndex = self.getTimeStatisticsIndex()
        self.TimeStatisticsType = self.getTimeStatisticsType()
        self.TimeReportingPeriods = self.getTimeReportingPeriods()
        self.Version = self.getVersion()
        self.TimeStartTime = self.getTimeStartTime()
        self.TimeHTime = self.getTimeHTime()
        self.TimeHaltFlag = self.getTimeHaltFlag()
        self.TimeNextEvent = self.getTimeNextEvent()
        self.NodeTankMaximumWaterVolume = self.getNodeTankMaximumWaterVolume()
        self.NodeBaseDemands = self.getNodeBaseDemands()
        self.NodeDemandCategoriesNumber = self.getNodeDemandCategoriesNumber()
        self.PatternAverageValue = self.getPatternAverageValue()
        n = self.getStatistic()
        self.RelativeError = n.RelativeError
        self.Iterations = n.Iterations
        self.NodeDemandPatternNameID = self.getNodeDemandPatternNameID()
        self.NodeDemandPatternIndex = self.getNodeDemandPatternIndex()
        self.LinkPumpHeadCurveIndex = self.getLinkPumpHeadCurveIndex()
        self.LinkPumpPatternNameID = self.getLinkPumpPatternNameID()
        self.LinkPumpPatternIndex = self.getLinkPumpPatternIndex()
        self.LinkPumpTypeCode = self.getLinkPumpTypeCode()
        self.LinkPumpType = self.getLinkPumpType()
        self.LinkPumpPower = self.getLinkPumpPower()
        self.CurvesInfo = self.getCurvesInfo()
        self.getUnits()
        self.NodeCoordinates = self.getNodeCoordinates()

    def __getlinkIndices(self, *argv):
        if len(argv) > 0:
            if type(argv[0]) is list:
                if type(argv[0][0]) is str:
                    return self.getLinkIndex(argv[0])
                else:
                    return argv[0]
            else:
                if type(argv[0]) is str:
                    return [self.getLinkIndex(argv[0])]
                else:
                    return [argv[0]]
        else:
            return self.getLinkIndex()

    def __getLinkInfo(self, iCode, *argv):
        values = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, (list, np.ndarray)):
                for i in index:
                    values.append(self.api.ENgetlinkvalue(i, iCode))
            else:
                values = self.api.ENgetlinkvalue(index, iCode)
        else:
            for i in range(self.getLinkCount()):
                values.append(self.api.ENgetlinkvalue(i + 1, iCode))
        return np.array(values)

    def __getNodeIndices(self, *argv):
        if len(argv) > 0:
            if type(argv[0]) is list:
                if type(argv[0][0]) is str:
                    return self.getNodeIndex(argv[0])
                else:
                    return argv[0]
            else:
                if type(argv[0]) is str:
                    return [self.getNodeIndex(argv[0])]
                else:
                    return [argv[0]]
        else:
            return self.getNodeIndex()

    def __getNodeInfo(self, iCode, *argv):
        value = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, (list, np.ndarray)):
                for i in index:
                    value.append(self.api.ENgetnodevalue(i, iCode))
            else:
                return self.api.ENgetnodevalue(index, iCode)
        else:
            for i in range(self.getNodeCount()):
                value.append(self.api.ENgetnodevalue(i + 1, iCode))
        return np.array(value)

    def __getNodeJunctionIndices(self, *argv):
        if len(argv) == 0:
            numJuncs = self.getNodeJunctionCount()
            return list(range(1, numJuncs + 1))
        else:
            return argv[0]

    def __getNodeTankMixiningModel(self, *argv):
        self.NodeTankMixingModelCode = self.__getTankNodeInfo(self.ToolkitConstants.EN_MIXMODEL, *argv)
        if isinstance(self.NodeTankMixingModelCode, (list, np.ndarray)):
            self.NodeTankMixingModelType = [self.TYPEMIXMODEL[i.astype(int)] for i in self.NodeTankMixingModelCode]
        else:
            self.NodeTankMixingModelType = self.TYPEMIXMODEL[self.NodeTankMixingModelCode.astype(int)]
        return [self.NodeTankMixingModelCode, self.NodeTankMixingModelType]

    def __getPumpLinkInfo(self, iCode, *argv):
        indices = self.getLinkPumpIndex()
        values = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, (list, np.ndarray)):
                if not sum(self.__isMember(index, indices)):
                    index = self.getLinkPumpIndex(index)
                for i in index:
                    values.append(self.api.ENgetlinkvalue(i, iCode))
            else:
                if index not in indices:
                    pIndex = self.getLinkPumpIndex(index)
                    if not pIndex:
                        return []
                else:
                    pIndex = index
                return self.api.ENgetlinkvalue(pIndex, iCode)
        else:
            for i in indices:
                values.append(self.api.ENgetlinkvalue(i, iCode))
        return np.array(values)

    def __getTankNodeInfo(self, iCode, *argv):
        indices = self.getNodeTankIndex()
        values = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, (list, np.ndarray)):
                if not sum(self.__isMember(index, indices)):
                    index = self.getNodeTankIndex(index)
                for i in index:
                    values.append(self.api.ENgetnodevalue(i, iCode))
            else:
                if index not in indices:
                    pIndex = self.getNodeTankIndex(index)
                    if not pIndex:
                        return []
                else:
                    pIndex = index
                values = self.api.ENgetnodevalue(pIndex, iCode)
        else:
            for i in indices:
                values.append(self.api.ENgetnodevalue(i, iCode))
        return np.array(values)

    def __isMember(self, A, B):
        return [np.sum(a == B) for a in np.array(A)]

    def __readEpanetBin(self, f, binfile, *argv):
        value = val()
        if f.readable():
            data = np.fromfile(binfile, dtype=np.uint32)
            value.NumberReportingPeriods = data[-3]
            # Beginning of file
            value.magicnumber = data[0]
            value.LibEPANET = data[1]
            value.NumberNodes = data[2]
            value.NumberReservoirsTanks = data[3]
            value.NumberLinks = data[4]
            value.NumberPumps = data[5]
            value.NumberValves = data[6]
            value.WaterQualityOption = data[7]
            value.IndexNodeSourceTracing = data[8]
            value.FlowUnitsOption = data[9]
            value.PressureUnitsOption = data[10]
            value.TimeStatisticsFlag = data[11]
            value.ReportingStartTimeSec = data[12]
            value.ReportingTimeStepSec = data[13]
            value.SimulationDurationSec = data[14]
            f.seek(50)
            try:
                value.ProblemTitle1 = f.read(80).split(b'\x01')[1].replace(b'\x00', b'').decode()
            except:
                pass
            try:
                value.ProblemTitle2 = f.read(80).replace(b'\x00', b'').decode()
            except:
                pass
            try:
                value.ProblemTitle3 = f.read(80).replace(b'\x00', b'').decode()
            except:
                pass
            value.NameInputFile = f.read(260).replace(b'\x00', b'').decode()
            value.NameReportFile = f.read(260).replace(b'\x00', b'').decode()
            value.NameChemical = f.read(20).replace(b'\x00', b'').decode()
            value.ChemicalConcentrationUnits = f.read(32).replace(b'\x00', b'').decode()
            f.read(4)
            value.IDLabelEachNode = []
            for i in range(value.NumberNodes):
                value.IDLabelEachNode.append(f.read(32).replace(b'\x00', b'').decode())
            value.IDLabelEachLink = []
            for i in range(value.NumberLinks):
                value.IDLabelEachLink.append(f.read(32).replace(b'\x00', b'').decode())
            while (True):
                binval = list(f.read(1))[0]
                if binval != 0:
                    break
            # IndexStartNodeEachLink
            value.IndexStartNodeEachLink = []
            for i in range(value.NumberLinks):
                value.IndexStartNodeEachLink.append(binval)
                f.read(3)
                binval = list(f.read(1))[0]
            # IndexEndNodeEachLink
            value.IndexEndNodeEachLink = []
            for i in range(value.NumberLinks):
                value.IndexEndNodeEachLink.append(binval)
                f.read(3)
                binval = list(f.read(1))[0]
            # TypeCodeEachLink
            value.TypeCodeEachLink = []
            for i in range(value.NumberLinks):
                value.TypeCodeEachLink.append(binval)
                f.read(3)
                binval = list(f.read(1))[0]
            # NodeIndexEachReservoirsTank
            value.NodeIndexEachReservoirsTank = []
            for i in range(value.NumberReservoirsTanks):
                value.NodeIndexEachReservoirsTank.append(binval)
                if i == value.NumberReservoirsTanks - 1:
                    break
                f.read(3)
                binval = list(f.read(1))[0]
            f.read(3)
            value.CrossSectionalAreaEachTank = struct.unpack('f' * value.NumberReservoirsTanks,
                                                             f.read(4 * value.NumberReservoirsTanks))
            value.ElevationEachNode = struct.unpack('f' * value.NumberNodes, f.read(4 * value.NumberNodes))
            value.LengthEachLink = struct.unpack('f' * value.NumberLinks, f.read(4 * value.NumberLinks))
            value.DiameterEachLink = struct.unpack('f' * value.NumberLinks, f.read(4 * value.NumberLinks))

            value.PumpIndexListLinks = []
            value.PumpUtilization = []
            value.AverageEfficiency = []
            value.AverageKwattsOrMillionGallons = []
            value.AverageKwatts = []
            value.PeakKwatts = []
            value.AverageCostPerDay = []
            for p in range(value.NumberPumps):
                value.PumpIndexListLinks.append(struct.unpack('f', f.read(4))[0])
                value.PumpUtilization.append(struct.unpack('f', f.read(4))[0])
                value.AverageEfficiency.append(struct.unpack('f', f.read(4))[0])
                value.AverageKwattsOrMillionGallons.append(struct.unpack('f', f.read(4))[0])
                value.AverageKwatts.append(struct.unpack('f', f.read(4))[0])
                value.PeakKwatts.append(struct.unpack('f', f.read(4))[0])
                value.AverageCostPerDay.append(struct.unpack('f', f.read(4))[0])
            struct.unpack('f', f.read(4))
            value.NodeDemand, value.NodeHead, value.NodePressure, value.NodeQuality, value.LinkFlow = {}, {}, {}, {}, {}
            value.LinkVelocity, value.LinkHeadloss, value.LinkQuality, value.LinkStatus = {}, {}, {}, {}
            value.LinkSetting, value.LinkReactionRate, value.LinkFrictionFactor = {}, {}, {}

            for i in range(1, value.NumberReportingPeriods + 1):
                value.NodeDemand[i] = struct.unpack('f' * value.NumberNodes, f.read(4 * value.NumberNodes))
                value.NodeHead[i] = struct.unpack('f' * value.NumberNodes, f.read(4 * value.NumberNodes))
                value.NodePressure[i] = struct.unpack('f' * value.NumberNodes, f.read(4 * value.NumberNodes))
                value.NodeQuality[i] = struct.unpack('f' * value.NumberNodes, f.read(4 * value.NumberNodes))
                value.LinkFlow[i] = struct.unpack('f' * value.NumberLinks, f.read(4 * value.NumberLinks))
                value.LinkVelocity[i] = struct.unpack('f' * value.NumberLinks, f.read(4 * value.NumberLinks))
                value.LinkHeadloss[i] = struct.unpack('f' * value.NumberLinks, f.read(4 * value.NumberLinks))
                value.LinkQuality[i] = struct.unpack('f' * value.NumberLinks, f.read(4 * value.NumberLinks))
                value.LinkStatus[i] = struct.unpack('f' * value.NumberLinks, f.read(4 * value.NumberLinks))
                value.LinkSetting[i] = struct.unpack('f' * value.NumberLinks, f.read(4 * value.NumberLinks))
                value.LinkReactionRate[i] = struct.unpack('f' * value.NumberLinks,
                                                          f.read(4 * value.NumberLinks))
                value.LinkFrictionFactor[i] = struct.unpack('f' * value.NumberLinks,
                                                            f.read(4 * value.NumberLinks))

            value.AverageBulkReactionRate = struct.unpack('f', f.read(4))
            value.AverageWallReactionRate = struct.unpack('f', f.read(4))
            value.AverageTankReactionRate = struct.unpack('f', f.read(4))
            value.AverageSourceInflowRate = struct.unpack('f', f.read(4))
            value.NumberReportingPeriods2 = list(f.read(1))[0]
            value.WarningFlag = list(f.read(1))[0]
            value.MagicNumber = f.read(10)

        if len(argv) > 0:
            v = val()
            v.Time = [int(i * value.ReportingTimeStepSec) for i in
                      range(int(value.SimulationDurationSec / value.ReportingTimeStepSec) + 1)]
            fields_param = ['NodePressure', 'NodeDemand', 'NodeHead', 'NodeQuality',
                            'LinkFlow', 'LinkVelocity', 'LinkHeadloss', 'LinkStatus', 'LinkSetting',
                            'LinkReactionRate', 'LinkFrictionFactor', 'LinkQuality']
            fields_new = ['Pressure', 'Demand', 'Head', 'NodeQuality',
                          'Flow', 'Velocity', 'HeadLoss', 'Status', 'Setting',
                          'ReactionRate', 'FrictionFactor', 'LinkQuality']
            for i in range(len(fields_param)):
                exec("v." + fields_new[i] + " = value." + fields_param[i])
            value = v
        # Close bin file and remove it
        f.close()
        try:
            os.remove(binfile)
        except:
            pass
        return value

    def __returnValue(self, value):
        if isList(value):
            try:
                if type(value) is list:
                    value = np.array(value)
                value = value.astype(int)
            except:
                value = int(value)
            return value
        else:
            return int(value)

    def __setControlFunction(self, index, value):
        controlRuleIndex = index
        [controlTypeIndex, linkIndex, controlSettingValue, nodeIndex, controlLevel] = self.__controlSettings(value)
        self.api.ENsetcontrol(controlRuleIndex, controlTypeIndex, linkIndex, controlSettingValue, nodeIndex,
                              controlLevel)

    def __setEval(self, func, iCodeStr, Type, value, *argv):
        if len(argv) == 1:
            index = value
            value = argv[0]
            if type(index) is list:
                j = 0
                for i in index:
                    if np.isnan(value[j]):
                        continue
                    strFunc = 'self.api.' + func + '(' + str(
                        i) + ',' + 'self.ToolkitConstants.EN_' + iCodeStr + ',' + str(value[j]) + ')'
                    eval(strFunc)
                    j += 1
            else:
                strFunc = 'self.api.' + func + '(' + str(
                    index) + ',' + 'self.ToolkitConstants.EN_' + iCodeStr + ',' + str(value) + ')'
                eval(strFunc)
        else:
            count = 0
            if (Type == 'LINK'):
                count = self.getLinkCount()
            elif (Type == 'NODE'):
                count = self.getNodeCount()
            for i in range(count):
                if np.isnan(value[i]):
                    continue
                strFunc = 'self.api.' + func + '(' + str(
                    i + 1) + ',' + 'self.ToolkitConstants.EN_' + iCodeStr + ',' + str(value[i]) + ')'
                eval(strFunc)

    def __setEvalLinkNode(self, func, iCodeStr, Type, value, *argv):
        if len(argv) == 1:
            index = value
            value = argv[0]
            if isinstance(index, (list, np.ndarray)):
                j = 0
                if type(value) is list:
                    for i in index:
                        strFunc = 'self.api.' + func + '(' + str(
                            i) + ',' + 'self.ToolkitConstants.EN_' + iCodeStr + ',' + str(value[j]) + ')'
                        eval(strFunc)
                        j += 1
                else:
                    for i in index:
                        strFunc = 'self.api.' + func + '(' + str(
                            i) + ',' + 'self.ToolkitConstants.EN_' + iCodeStr + ',' + str(value) + ')'
                        eval(strFunc)
                        j += 1
            else:
                if (Type == 'TANK'):
                    Index = self.getNodeTankIndex()
                elif (Type == 'PUMP'):
                    Index = self.getLinkPumpIndex()
                if index not in Index:
                    Index = Index[index - 1]
                else:
                    Index = index
                    if isinstance(value, (list, np.ndarray)):
                        value = value[0]
                strFunc = 'self.api.' + func + '(' + str(
                    Index) + ',' + 'self.ToolkitConstants.EN_' + iCodeStr + ',' + str(value) + ')'
                eval(strFunc)
        else:
            count = 0
            if (Type == 'TANK'):
                count = self.getNodeTankCount()
                indices = self.getNodeTankIndex()
            elif (Type == 'PUMP'):
                count = self.getLinkPumpCount()
                indices = self.getLinkPumpIndex()
            if isinstance(value, (list, np.ndarray)):
                for i in range(count):
                    strFunc = 'self.api.' + func + '(' + str(
                        indices[i]) + ',' + 'self.ToolkitConstants.EN_' + iCodeStr + ',' + str(value[i]) + ')'
                    eval(strFunc)
            else:
                for i in range(count):
                    strFunc = 'self.api.' + func + '(' + str(
                        indices[i]) + ',' + 'self.ToolkitConstants.EN_' + iCodeStr + ',' + str(value) + ')'
                    eval(strFunc)

    def __setFlowUnits(self, unitcode, *argv):
        self.api.ENsetflowunits(unitcode)
        if len(argv) == 1:
            self.saveInputFile(argv[0])

    def __setNodeDemandPattern(self, fun, propertyCode, value, *argv):

        categ = 1
        if len(argv) == 2:
            indices = value
            categ = argv[0]
            param = argv[1]
        elif len(argv) == 1:
            indices = value
            param = argv[0]
        elif len(argv) == 0:
            indices = self.__getNodeJunctionIndices()
            param = value
            # if isList(param):
            #     categ = len(param)

        for c in range(categ):
            if len(argv) == 0 and type(value) is dict:
                param = value[c]
            j = 0
            resInd = self.getNodeReservoirIndex()
            if not isList(indices):
                indices = [indices]
            if not isList(param):
                param = [param]
            for i in indices:
                if i in resInd:
                    if c + 1 > self.getNodeDemandCategoriesNumber(i):
                        self.addNodeJunctionDemand(i, param[j])
                    else:
                        eval('self.api.' + fun + '(i, c, param[j])')
                elif categ == 1:
                    self.api.ENsetnodevalue(i, propertyCode, param[j])
                else:
                    eval('self.api.' + fun + '(i, categ, param[j])')
                j += 1



class epanetapi:
    """
    EPANET Toolkit functions - API
    """

    EN_MAXID = 32  # toolkit constant

    def __init__(self, version=2.2):
        """Load the EPANET library.

        Parameters:
        version     EPANET version to use (currently 2.2)
        """
        self._lib = None
        self.errcode = 0
        self.isloaded = False
        self.inpfile = None
        self.rptfile = None
        self.binfile = None

        # Check platform and Load epanet library
        libname = f"epanet{str(version).replace('.', '_')}"
        ops = platform.system().lower()
        if ops in ["windows"]:
            if "32" in str(platform.architecture()):
                self.LibEPANET = resource_filename("epyt", os.path.join("libraries", "win", libname, '32bit',
                                                                        f"{libname[:-2]}.dll"))
            elif "64" in str(platform.architecture()):
                self.LibEPANET = resource_filename("epyt", os.path.join("libraries", "win", libname, '64bit',
                                                                        f"{libname[:-2]}.dll"))
        elif ops in ["darwin"]:
            self.LibEPANET = resource_filename("epyt", os.path.join("libraries", f"mac/lib{libname}.dylib"))
        else:
            self.LibEPANET = resource_filename("epyt", os.path.join("libraries", f"glnx/lib{libname}.so"))

        self._lib = ctypes.cdll.LoadLibrary(self.LibEPANET)
        self.LibEPANETpath = os.path.dirname(self.LibEPANET)

        if float(version) >= 2.2 and '64' in str(platform.architecture()):
            self._ph = ctypes.c_uint64()
        elif float(version) >= 2.2:
            self._ph = ctypes.c_uint32()
        else:
            self._ph = None

    def ENepanet(self, inpfile="", rptfile="", binfile=""):
        """ Runs a complete EPANET simulation
        Parameters:
        inpfile     Input file to use
        rptfile     Output file to report to
        binfile     Results file to generate
        """
        self.inpfile = inpfile.encode("utf-8")
        self.rptfile = rptfile.encode("utf-8")
        self.binfile = binfile.encode("utf-8")
        self.errcode = self._lib.ENepanet(self.inpfile, self.rptfile, self.binfile, ctypes.c_void_p())
        self.ENgeterror()

    def ENaddcontrol(self, conttype, lindex, setting, nindex, level):
        """ Adds a new simple control to a project.

        ENaddcontrol(ctype, lindex, setting, nindex, level)

        Parameters:
        conttype    the type of control to add (see ControlTypes).
        lindex      the index of a link to control (starting from 1).
        setting     control setting applied to the link.
        nindex      index of the node used to control the link (0 for EN_TIMER and EN_TIMEOFDAY controls).
        level       action level (tank level, junction pressure, or time in seconds) that triggers the control.

        Returns:
        cindex 	index of the new control.
        """
        index = ctypes.c_int()
        self.errcode = self._lib.EN_addcontrol(self._ph, conttype, int(lindex), ctypes.c_double(setting), nindex,
                                               ctypes.c_double(level), ctypes.byref(index))
        self.ENgeterror()
        return index.value

    def ENaddcurve(self, cid):
        """ Adds a new data curve to a project.
        EPANET Version 2.1

        ENaddcurve(cid)

        Parameters:
        cid        The ID name of the curve to be added.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___curves.html
        """
        self.errcode = self._lib.EN_addcurve(self._ph, cid.encode('utf-8'))
        self.ENgeterror()

    def ENadddemand(self, nodeIndex, baseDemand, demandPattern, demandName):
        """ Appends a new demand to a junction node demands list.
        EPANET Version 2.2

        ENadddemand(nodeIndex, baseDemand, demandPattern, demandName)

        Parameters:
        nodeIndex        the index of a node (starting from 1).
        baseDemand       the demand's base value.
        demandPattern    the name of a time pattern used by the demand.
        demandName       the name of the demand's category.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___demands.html
        """
        self.errcode = self._lib.EN_adddemand(self._ph, int(nodeIndex), ctypes.c_double(baseDemand), demandPattern.encode("utf-8"),
                                              demandName.encode("utf-8"))
        self.ENgeterror()
        return

    def ENaddlink(self, linkid, linktype, fromnode, tonode):
        """ Adds a new link to a project.

        ENaddlink(linkid, linktype, fromnode, tonode)

        Parameters:
        linkid        The ID name of the link to be added.
        linktype      The type of link being added (see EN_LinkType, self.LinkType).
        fromnode      The ID name of the link's starting node.
        tonode        The ID name of the link's ending node.

        Returns:
        index the index of the newly added link.
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___links.html
        """
        index = ctypes.c_int()
        self.errcode = self._lib.EN_addlink(self._ph, linkid.encode('utf-8'), linktype,
                                            fromnode.encode('utf-8'), tonode.encode('utf-8'), ctypes.byref(index))
        self.ENgeterror()
        return index.value

    def ENaddnode(self, nodeid, nodetype):
        """ Adds a new node to a project.

        ENaddnode(nodeid, nodetype)

        Parameters:
        nodeid       the ID name of the node to be added.
        nodetype     the type of node being added (see EN_NodeType).

        Returns:
        index    the index of the newly added node.
        See also EN_NodeProperty, NodeType
        """
        index = ctypes.c_int()
        self.errcode = self._lib.EN_addnode(self._ph, nodeid.encode("utf-8"), nodetype, ctypes.byref(index))
        self.ENgeterror()
        return index.value

    def ENaddpattern(self, patid):
        """ Adds a new time pattern to a project.

        ENaddpattern(patid)

        Parameters:
        patid      the ID name of the pattern to add.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___patterns.html
        """
        self.errcode = self._lib.EN_addpattern(self._ph, patid.encode("utf-8"))
        self.ENgeterror()
        return

    def ENaddrule(self, rule):
        """ Adds a new rule-based control to a project.
        EPANET Version 2.2

        ENaddrule(rule)

        Parameters:
        rule        text of the rule following the format used in an EPANET input file.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___rules.html
        """
        self.errcode = self._lib.EN_addrule(self._ph, rule.encode('utf-8'))
        self.ENgeterror()

    def ENclearreport(self):
        """ Clears the contents of a project's report file.
        EPANET Version 2.2

        ENclearreport()

        """
        self.errcode = self._lib.EN_clearreport(self._ph)
        self.ENgeterror()

    def ENclose(self):
        """ Closes a project and frees all of its memory.

        ENclose()

        See also ENopen
        """
        self.errcode = self._lib.EN_close(self._ph)
        self._ph = ctypes.c_uint64()
        self.ENgeterror()
        if self.errcode < 100:
            self.isloaded = False
        return

    def ENcloseH(self):
        """ Closes the hydraulic solver freeing all of its allocated memory.

        ENcloseH()

        See also  ENinitH, ENrunH, ENnextH
        """
        self.errcode = self._lib.EN_closeH(self._ph)
        self.ENgeterror()
        return

    def ENcloseQ(self):
        """ Closes the water quality solver, freeing all of its allocated memory.

        ENcloseQ()

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___quality.html
        """
        self.errcode = self._lib.EN_closeQ(self._ph)
        self.ENgeterror()
        return

    def ENcopyreport(self, filename):
        """ Copies the current contents of a project's report file to another file.
        EPANET Version 2.2

        ENcopyreport(filename)

        Parameters:
        filename  the full path name of the destination file

        """
        self.errcode = self._lib.EN_copyreport(self._ph, filename.encode("utf-8"))
        self.ENgeterror()

    def ENcreateproject(self):
        """ Copies the current contents of a project's report file to another file.
        *** ENcreateproject must be called before any other API functions are used. ***
        ENcreateproject()

        Parameters:
        ph	an EPANET project handle that is passed into all other API functions.

        """
        self.errcode = self._lib.EN_createproject(ctypes.byref(self._ph))
        self.ENgeterror()
        return

    def ENdeletecontrol(self, index):
        """ Deletes an existing simple control.
        EPANET Version 2.2

        ENdeletecontrol(index)

        Parameters:
        index       the index of the control to delete (starting from 1).

        """
        self.errcode = self._lib.EN_deletecontrol(self._ph, int(index))
        self.ENgeterror()

    def ENdeletecurve(self, indexCurve):
        """ Deletes a data curve from a project.
        EPANET Version 2.2

        ENdeletecurve(indexCurve)

        Parameters:
        indexCurve  The ID name of the curve to be added.

        """
        self.errcode = self._lib.EN_deletecurve(self._ph, int(indexCurve))
        self.ENgeterror()

    def ENdeletedemand(self, nodeIndex, demandIndex):
        """ Deletes a demand from a junction node.

        ENdeletedemand(nodeIndex, demandInde)

        Parameters:
        nodeIndex        the index of a node (starting from 1).
        demandIndex      the position of the demand in the node's demands list (starting from 1).

        """
        self.errcode = self._lib.EN_deletedemand(self._ph, int(nodeIndex), demandIndex)
        self.ENgeterror()

    def ENdeletelink(self, indexLink, condition):
        """ Deletes a link from the project.

        ENdeletelink(indexLink, condition)

        Parameters:
        indexLink      the index of the link to be deleted.
        condition      The action taken if any control contains the link.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___links.html
        """
        self.errcode = self._lib.EN_deletelink(self._ph, int(indexLink), condition)
        self.ENgeterror()

    def ENdeletenode(self, indexNode, condition):
        """ Deletes a node from a project.

        ENdeletenode(indexNode, condition)

        Parameters:
        indexNode    the index of the node to be deleted.
        condition    	the action taken if any control contains the node and its links.

        See also EN_NodeProperty, NodeType
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___nodes.html
        """
        self.errcode = self._lib.EN_deletenode(self._ph, int(indexNode), condition)
        self.ENgeterror()

    def ENdeletepattern(self, indexPat):
        """ Deletes a time pattern from a project.
        EPANET Version 2.2

        ENdeletepattern(indexPat)

        Parameters:
        indexPat   the time pattern's index (starting from 1).

        """
        self.errcode = self._lib.EN_deletepattern(self._ph, int(indexPat))
        self.ENgeterror()

    def ENdeleteproject(self):
        """ Deletes an EPANET project.
        *** EN_deleteproject should be called after all network analysis has been completed. ***
        ENdeleteproject()

        Parameters:
        ph	an EPANET project handle which is returned as NULL.

        """
        self.errcode = self._lib.EN_deleteproject(self._ph)
        self.ENgeterror()
        return

    def ENdeleterule(self, index):
        """ Deletes an existing rule-based control.
        EPANET Version 2.2

        ENdeleterule(index)

        Parameters:
        index       the index of the rule to be deleted (starting from 1).

        """
        self.errcode = self._lib.EN_deleterule(self._ph, int(index))
        self.ENgeterror()

    def ENgetaveragepatternvalue(self, index):
        """ Retrieves the average of all pattern factors in a time pattern.
        EPANET Version 2.1

        ENgetaveragepatternvalue(index)

        Parameters:
        index      a time pattern index (starting from 1).

        Returns:
        value The average of all of the time pattern's factors.
        """
        value = ctypes.c_double()
        self.errcode = self._lib.EN_getaveragepatternvalue(self._ph, int(index), ctypes.byref(value))
        self.ENgeterror()
        return value.value

    def ENgetbasedemand(self, index, numdemands):
        """ Gets the base demand for one of a node's demand categories.
        EPANET 20100

        ENgetbasedemand(index, numdemands)

        Parameters:
        index        a node's index (starting from 1).
        numdemands   the index of a demand category for the node (starting from 1).

        Returns:
        value  the category's base demand.
        """
        bDem = ctypes.c_double()
        self.errcode = self._lib.EN_getbasedemand(self._ph, int(index), numdemands, ctypes.byref(bDem))
        self.ENgeterror()
        return bDem.value

    def ENgetcomment(self, object_, index):
        """ Retrieves the comment of a specific index of a type object.
        EPANET Version 2.2

        ENgetcomment(object, index, comment)

        Parameters:
        object_    a type of object (either EN_NODE, EN_LINK, EN_TIMEPAT or EN_CURVE)
                   e.g, self.ToolkitConstants.EN_NODE
        index      object's index (starting from 1).

        Returns:
        out_comment  the comment string assigned to the object.
        """
        out_comment = ctypes.create_string_buffer(80)
        self.errcode = self._lib.EN_getcomment(self._ph, object_, int(index), ctypes.byref(out_comment))
        self.ENgeterror()
        return out_comment.value.decode()

    def ENgetcontrol(self, cindex):
        """ Retrieves the properties of a simple control.

        ENgetcontrol(cindex)

        Parameters:
        cindex      the control's index (starting from 1).

        Returns:
        ctype   the type of control (see ControlTypes).
        lindex  the index of the link being controlled.
        setting the control setting applied to the link.
        nindex  the index of the node used to trigger the control (0 for EN_TIMER and EN_TIMEOFDAY controls).
        level   the action level (tank level, junction pressure, or time in seconds) that triggers the control.
        """
        ctype = ctypes.c_int()
        lindex = ctypes.c_int()
        setting = ctypes.c_double()
        nindex = ctypes.c_int()
        level = ctypes.c_double()
        self.errcode = self._lib.EN_getcontrol(self._ph, int(cindex), ctypes.byref(ctype), ctypes.byref(lindex),
                                               ctypes.byref(setting), ctypes.byref(nindex), ctypes.byref(level))
        self.ENgeterror()
        return [ctype.value, lindex.value, setting.value, nindex.value, level.value]

    def ENgetcoord(self, index):
        """ Gets the (x,y) coordinates of a node.
        EPANET Version 2.1

        ENgetcoord(index)

        Parameters:
        index      a node index (starting from 1).

        Returns:
        x 	the node's X-coordinate value.
        y   the node's Y-coordinate value.
        """
        x = ctypes.c_double()
        y = ctypes.c_double()
        self.errcode = self._lib.EN_getcoord(self._ph, int(index), ctypes.byref(x), ctypes.byref(y))
        self.ENgeterror()
        return [x.value, y.value]

    def ENgetcount(self, countcode):
        """ Retrieves the number of objects of a given type in a project.

        ENgetcount(countcode)

        Parameters:
        countcode	number of objects of the specified type

        Returns:
        count	number of objects of the specified type
        """
        count = ctypes.c_int()
        self.errcode = self._lib.EN_getcount(self._ph, countcode, ctypes.byref(count))
        self.ENgeterror()
        return count.value

    def ENgetcurve(self, index):
        """ Retrieves all of a curve's data.

        ENgetcurve(index)

        Parameters:
        index         a curve's index (starting from 1).

        out_id	 the curve's ID name
        nPoints	 the number of data points on the curve.
        xValues	 the curve's x-values.
        yValues	 the curve's y-values.

        See also ENgetcurvevalue
        """
        out_id = ctypes.create_string_buffer(self.EN_MAXID)
        nPoints = ctypes.c_int()
        xValues = (ctypes.c_double * self.ENgetcurvelen(index))()
        yValues = (ctypes.c_double * self.ENgetcurvelen(index))()
        self.errcode = self._lib.EN_getcurve(self._ph, index, ctypes.byref(out_id), ctypes.byref(nPoints),
                                             ctypes.byref(xValues), ctypes.byref(yValues))
        self.ENgeterror()
        curve_attr = {}
        curve_attr['id'] = out_id.value.decode()
        curve_attr['nPoints'] = nPoints.value
        curve_attr['x'] = []
        curve_attr['y'] = []
        for i in range(len(xValues)):
            curve_attr['x'].append(xValues[i])
            curve_attr['y'].append(yValues[i])
        return curve_attr

    def ENgetcurveid(self, index):
        """ Retrieves the ID name of a curve given its index.
        EPANET Version 2.1

        ENgetcurveid(index)

        Parameters:
        index       a curve's index (starting from 1).

        Returns:
        Id	the curve's ID name

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___curves.html
        """
        Id = ctypes.create_string_buffer(self.EN_MAXID)
        self.errcode = self._lib.EN_getcurveid(self._ph, int(index), ctypes.byref(Id))
        self.ENgeterror()
        return Id.value.decode()

    def ENgetcurveindex(self, Id):
        """ Retrieves the index of a curve given its ID name.
        EPANET Version 2.1

        ENgetcurveindex(Id)

        Parameters:
        Id          the ID name of a curve.

        Returns:
        index   The curve's index (starting from 1).
        """
        index = ctypes.c_int()
        self.errcode = self._lib.EN_getcurveindex(self._ph, Id.encode("utf-8"), ctypes.byref(index))
        self.ENgeterror()
        return index.value

    def ENgetcurvelen(self, index):
        """ Retrieves the number of points in a curve.
        EPANET Version 2.1

        ENgetcurvelen(index)

        Parameters:
        index       a curve's index (starting from 1).

        Returns:
        len  The number of data points assigned to the curve.
        """
        length = ctypes.c_int()
        self.errcode = self._lib.EN_getcurvelen(self._ph, int(index), ctypes.byref(length))
        self.ENgeterror()
        return length.value

    def ENgetcurvetype(self, index):
        """ Retrieves a curve's type.
        EPANET Version 2.2

        ENgetcurvetype(index)

        Parameters:
        index       a curve's index (starting from 1).

        Returns:
        type_  The curve's type (see EN_CurveType).
        """
        type_ = ctypes.c_int()
        self.errcode = self._lib.EN_getcurvetype(self._ph, int(index), ctypes.byref(type_))
        self.ENgeterror()
        return type_.value

    def ENgetcurvevalue(self, index, period):
        """ Retrieves the value of a single data point for a curve.
        EPANET Version 2.1

        ENgetcurvevalue(index, period)

        Parameters:
        index       a curve's index (starting from 1).
        period      the index of a point on the curve (starting from 1).

        Returns:
        x  the point's x-value.
        y  the point's y-value.
        """
        x = ctypes.c_double()
        y = ctypes.c_double()
        self.errcode = self._lib.EN_getcurvevalue(self._ph, int(index), period, ctypes.byref(x), ctypes.byref(y))
        self.ENgeterror()
        return [x.value, y.value]

    def ENgetdemandindex(self, nodeindex, demandName):
        """ Retrieves the index of a node's named demand category.
        EPANET Version 2.2

        ENgetdemandindex(nodeindex, demandName)

        Parameters:
        nodeindex    the index of a node (starting from 1).
        demandName   the name of a demand category for the node.

        Returns:
        demandIndex  the index of the demand being sought.
        """
        demandIndex = ctypes.c_int()
        self.errcode = self._lib.EN_getdemandindex(self._ph, int(nodeindex), demandName.encode('utf-8'),
                                                   ctypes.byref(demandIndex))
        self.ENgeterror()
        return demandIndex.value

    def ENgetdemandmodel(self):
        """ Retrieves the type of demand model in use and its parameters.
        EPANET Version 2.2

        ENgetdemandmodel()

        Returns:
        Type  Type of demand model (see EN_DemandModel).
        pmin  Pressure below which there is no demand.
        preq  Pressure required to deliver full demand.
        pexp  Pressure exponent in demand function.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___demands.html
        """
        Type = ctypes.c_int()
        pmin = ctypes.c_double()
        preq = ctypes.c_double()
        pexp = ctypes.c_double()
        self.errcode = self._lib.EN_getdemandmodel(self._ph, ctypes.byref(Type), ctypes.byref(pmin),
                                                   ctypes.byref(preq), ctypes.byref(pexp))
        self.ENgeterror()
        return [Type.value, pmin.value, preq.value, pexp.value]

    def ENgetdemandname(self, node_index, demand_index):
        """ Retrieves the name of a node's demand category.
        EPANET Version 2.2

        ENgetdemandname(node_index, demand_index)

        Parameters:
        node_index    	a node's index (starting from 1).
        demand_index    the index of one of the node's demand categories (starting from 1).

        Returns:
        demand_name  The name of the selected category.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___demands.html
        """
        demand_name = ctypes.create_string_buffer(100)
        self.errcode = self._lib.EN_getdemandname(self._ph, int(node_index), int(demand_index), ctypes.byref(demand_name))
        self.ENgeterror()
        return demand_name.value.decode()

    def ENgetdemandpattern(self, index, numdemands):
        """ Retrieves the index of a time pattern assigned to one of a node's demand categories.
        EPANET 20100
        ENgetdemandpattern(index, numdemands)

        Parameters:
        index    	 the node's index (starting from 1).
        numdemands   the index of a demand category for the node (starting from 1).

        Returns:
        value  the index of the category's time pattern.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___demands.html
        """
        patIndex = ctypes.c_int()
        self.errcode = self._lib.EN_getdemandpattern(self._ph, int(index), numdemands, ctypes.byref(patIndex))
        self.ENgeterror()
        return patIndex.value

    def ENgetelseaction(self, ruleIndex, actionIndex):
        """ Gets the properties of an ELSE action in a rule-based control.
        EPANET Version 2.2

        ENgetelseaction(ruleIndex, actionIndex)

        Parameters:
        ruleIndex   	the rule's index (starting from 1).
        actionIndex   the index of the ELSE action to retrieve (starting from 1).

        Returns:
        linkIndex  the index of the link sin the action.
        status     the status assigned to the link (see RULESTATUS).
        setting    the value assigned to the link's setting.
        """
        linkIndex = ctypes.c_int()
        status = ctypes.c_int()
        setting = ctypes.c_double()
        self.errcode = self._lib.EN_getelseaction(self._ph, int(ruleIndex), int(actionIndex), ctypes.byref(linkIndex),
                                                  ctypes.byref(status), ctypes.byref(setting))
        self.ENgeterror()
        return [linkIndex.value, status.value, setting.value]

    def ENgeterror(self):
        """ Returns the text of an error message generated by an error code, as warning.

        ENgeterror()

        """
        if self.errcode:
            errmssg = ctypes.create_string_buffer(150)
            self._lib.ENgeterror(self.errcode, ctypes.byref(errmssg), 150)
            warnings.warn(errmssg.value.decode())

    def ENgetflowunits(self):
        """ Retrieves a project's flow units.

        ENgetflowunits()

        Returns:
        flowunitsindex a flow units code.
        """
        flowunitsindex = ctypes.c_int()
        self.errcode = self._lib.EN_getflowunits(self._ph, ctypes.byref(flowunitsindex))
        self.ENgeterror()
        return flowunitsindex.value

    def ENgetheadcurveindex(self, pumpindex):
        """ Retrieves the curve assigned to a pump's head curve.
        EPANET Version 2.1

        ENgetheadcurveindex(pumpindex)

        Parameters:
        pumpindex      the index of a pump link (starting from 1).

        Returns:
        value   the index of the curve assigned to the pump's head curve.
        """
        value = ctypes.c_long()
        self.errcode = self._lib.EN_getheadcurveindex(self._ph, int(pumpindex), ctypes.byref(value))
        self.ENgeterror()
        return value.value

    def ENgetlinkid(self, index):
        """ Gets the ID name of a link given its index.

        ENgetlinkid(index)

        Parameters:
        index      	a link's index (starting from 1).

        Returns:
        id   The link's ID name.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___links.html
        """
        nameID = ctypes.create_string_buffer(self.EN_MAXID)
        self.errcode = self._lib.EN_getlinkid(self._ph, int(index), ctypes.byref(nameID))
        self.ENgeterror()
        return nameID.value.decode()

    def ENgetlinkindex(self, Id):
        """ Gets the index of a link given its ID name.

        ENgetlinkindex(Id)

        Parameters:
        Id      	  a link's ID name.

        Returns:
        index   the link's index (starting from 1).
        """
        index = ctypes.c_int()
        self.errcode = self._lib.EN_getlinkindex(self._ph, Id.encode("utf-8"), ctypes.byref(index))
        self.ENgeterror()
        return index.value

    def ENgetlinknodes(self, index):
        """ Gets the indexes of a link's start- and end-nodes.

        ENgetlinknodes(index)

        Parameters:
        index      	a link's index (starting from 1).

        Returns:
        from   the index of the link's start node (starting from 1).
        to     the index of the link's end node (starting from 1).
        """
        fromNode = ctypes.c_int()
        toNode = ctypes.c_int()
        self.errcode = self._lib.EN_getlinknodes(self._ph, int(index), ctypes.byref(fromNode), ctypes.byref(toNode))
        self.ENgeterror()
        return [fromNode.value, toNode.value]

    def ENgetlinktype(self, iIndex):
        """ Retrieves a link's type.

        ENgetlinktype(index)

        Parameters:
        index      	a link's index (starting from 1).

        Returns:
        typecode   the link's type (see LinkType).
        """
        iCode = ctypes.c_int()
        self.errcode = self._lib.EN_getlinktype(self._ph, int(iIndex), ctypes.byref(iCode))
        self.ENgeterror()
        if iCode.value != -1:
            return iCode.value
        else:
            return sys.maxsize

    def ENgetlinkvalue(self, index, paramcode):
        """ Retrieves a property value for a link.

        ENgetlinkvalue(index, paramcode)

        Parameters:
        index      	a link's index (starting from 1).
        paramcode   the property to retrieve (see EN_LinkProperty).

        Returns:
        value   the current value of the property.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___links.html
        """
        fValue = ctypes.c_double()
        self.errcode = self._lib.EN_getlinkvalue(self._ph, int(index), paramcode, ctypes.byref(fValue))
        self.ENgeterror()
        return fValue.value

    def ENgetnodeid(self, index):
        """ Gets the ID name of a node given its index

        ENgetnodeid(index)

        Parameters:
        index  nodes index

        Returns:
        nameID nodes id
        """
        nameID = ctypes.create_string_buffer(self.EN_MAXID)
        self.errcode = self._lib.EN_getnodeid(self._ph, int(index), ctypes.byref(nameID))
        self.ENgeterror()
        return nameID.value.decode()


    def ENgetnodeindex(self, Id):
        """ Gets the index of a node given its ID name.

        ENgetnodeindex(Id)

        Parameters:
        Id      	 a node ID name.

        Returns:
        index  the node's index (starting from 1).
        """
        index = ctypes.c_int()
        self.errcode = self._lib.EN_getnodeindex(self._ph, Id.encode("utf-8"), ctypes.byref(index))
        self.ENgeterror()
        return index.value

    def ENgetnodetype(self, iIndex):
        """ Retrieves a node's type given its index.

        ENgetnodetype(index)

        Parameters:
        index      a node's index (starting from 1).

        Returns:
        type the node's type (see NodeType).
        """
        iCode = ctypes.c_int()
        self.errcode = self._lib.EN_getnodetype(self._ph, int(iIndex), ctypes.byref(iCode))
        self.ENgeterror()
        return iCode.value

    def ENgetnodevalue(self, iIndex, iCode):
        """ Retrieves a property value for a node.

        ENgetnodevalue(index, paramcode)

        Parameters:
        index      a node's index.
        paramcode  the property to retrieve (see EN_NodeProperty, self.getToolkitConstants).

        Returns:
        value the current value of the property.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___nodes.html
        """
        fValue = ctypes.c_double()
        self.errcode = self._lib.EN_getnodevalue(self._ph, int(iIndex), iCode, ctypes.byref(fValue))
        if self.errcode != 240:
            self.ENgeterror()
            return fValue.value
        else:
            return 240

    def ENgetnumdemands(self, index):
        """ Retrieves the number of demand categories for a junction node.
        EPANET 20100

        ENgetnumdemands(index)

        Parameters:
        index    	   the index of a node (starting from 1).

        Returns:
        value  the number of demand categories assigned to the node.
        """
        numDemands = ctypes.c_int()
        self.errcode = self._lib.EN_getnumdemands(self._ph, int(index), ctypes.byref(numDemands))
        self.ENgeterror()
        return numDemands.value

    def ENgetoption(self, optioncode):
        """ Retrieves the value of an analysis option.

        ENgetoption(optioncode)

        Parameters:
        optioncode   a type of analysis option (see EN_Option).

        Returns:
        value the current value of the option.
        """
        value = ctypes.c_double()
        self.errcode = self._lib.EN_getoption(self._ph, optioncode, ctypes.byref(value))
        self.ENgeterror()
        return value.value

    def ENgetpatternid(self, index):
        """ Retrieves the ID name of a time pattern given its index.

        ENgetpatternid(index)

        Parameters:
        index      a time pattern index (starting from 1).

        Returns:
        id   the time pattern's ID name.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___patterns.html
        """
        nameID = ctypes.create_string_buffer(self.EN_MAXID)
        self.errcode = self._lib.EN_getpatternid(self._ph, int(index), ctypes.byref(nameID))
        self.ENgeterror()
        return nameID.value.decode()

    def ENgetpatternindex(self, Id):
        """ Retrieves the index of a time pattern given its ID name.

        ENgetpatternindex(id)

        Parameters:
        id         the ID name of a time pattern.

        Returns:
        index   the time pattern's index (starting from 1).
        """
        index = ctypes.c_int()
        self.errcode = self._lib.EN_getpatternindex(self._ph, Id.encode("utf-8"), ctypes.byref(index))
        self.ENgeterror()
        return index.value

    def ENgetpatternlen(self, index):
        """ Retrieves the number of time periods in a time pattern.

        ENgetpatternlen(index)

        Parameters:
        index      a time pattern index (starting from 1).

        Returns:
        leng   the number of time periods in the pattern.
        """
        leng = ctypes.c_int()
        self.errcode = self._lib.EN_getpatternlen(self._ph, int(index), ctypes.byref(leng))
        self.ENgeterror()
        return leng.value

    def ENgetpatternvalue(self, index, period):
        """ Retrieves a time pattern's factor for a given time period.

        ENgetpatternvalue(index, period)

        Parameters:
        index      a time pattern index (starting from 1).
        period     a time period in the pattern (starting from 1).

        Returns:
        value   the pattern factor for the given time period.
        """
        value = ctypes.c_double()
        self.errcode = self._lib.EN_getpatternvalue(self._ph, int(index), period, ctypes.byref(value))
        self.ENgeterror()
        return value.value

    def ENgetpremise(self, ruleIndex, premiseIndex):
        """ Gets the properties of a premise in a rule-based control.
        EPANET Version 2.2

        ENgetpremise(ruleIndex, premiseIndex)

        Parameters:
        ruleIndex   	 the rule's index (starting from 1).
        premiseIndex   the position of the premise in the rule's list of premises (starting from 1).

        Returns:
        logop       the premise's logical operator ( IF = 1, AND = 2, OR = 3 ).
        object_     the status assigned to the link (see RULEOBJECT).
        objIndex    the index of the object (e.g. the index of a tank).
        variable    the object's variable being compared (see RULEVARIABLE).
        relop       the premise's comparison operator (see RULEOPERATOR).
        status      the status that the object's status is compared to (see RULESTATUS).
        value       the value that the object's variable is compared to.
        """
        logop = ctypes.c_int()
        object_ = ctypes.c_int()
        objIndex = ctypes.c_int()
        variable = ctypes.c_int()
        relop = ctypes.c_int()
        status = ctypes.c_int()
        value = ctypes.c_double()
        self.errcode = self._lib.EN_getpremise(self._ph, int(ruleIndex), int(premiseIndex), ctypes.byref(logop),
                                               ctypes.byref(object_), ctypes.byref(objIndex),
                                               ctypes.byref(variable), ctypes.byref(relop), ctypes.byref(status),
                                               ctypes.byref(value))
        self.ENgeterror()
        return [logop.value, object_.value, objIndex.value, variable.value, relop.value, status.value, value.value]

    def ENgetpumptype(self, iIndex):
        """ Retrieves the type of head curve used by a pump.
        EPANET Version 2.1

        ENgetpumptype(pumpindex)

        Parameters:
        pumpindex   the index of a pump link (starting from 1).

        Returns:
        value   the type of head curve used by the pump (see EN_PumpType).
        """
        iCode = ctypes.c_int()
        self.errcode = self._lib.EN_getpumptype(self._ph, int(iIndex), ctypes.byref(iCode))
        self.ENgeterror()
        return iCode.value

    def ENgetqualinfo(self):
        """ Gets information about the type of water quality analysis requested.

        ENgetqualinfo()

        Returns:
        qualType    type of analysis to run (see self.QualityType).
        chemname    name of chemical constituent.
        chemunits   concentration units of the constituent.
        tracenode 	index of the node being traced (if applicable).
        """
        qualType = ctypes.c_int()
        chemname = ctypes.create_string_buffer(self.EN_MAXID)
        chemunits = ctypes.create_string_buffer(self.EN_MAXID)
        tracenode = ctypes.c_int()
        self.errcode = self._lib.EN_getqualinfo(self._ph, ctypes.byref(qualType), ctypes.byref(chemname),
                                                ctypes.byref(chemunits), ctypes.byref(tracenode))
        self.ENgeterror()
        return [qualType.value, chemname.value.decode(), chemunits.value.decode(), tracenode.value]

    def ENgetqualtype(self):
        """ Retrieves the type of water quality analysis to be run.

        ENgetqualtype()

        Returns:
        qualcode    type of analysis to run (see self.QualityType).
        tracenode 	index of the node being traced (if applicable).
        """
        qualcode = ctypes.c_int()
        tracenode = ctypes.c_int()
        self.errcode = self._lib.EN_getqualtype(self._ph, ctypes.byref(qualcode), ctypes.byref(tracenode))
        self.ENgeterror()
        return [qualcode.value, tracenode.value]

    def ENgetresultindex(self, objecttype, iIndex):
        """Retrieves the order in which a node or link appears in an output file.
           EPANET Version 2.2

           ENgetresultindex(objecttype, index)

        Parameters:
        objecttype  a type of element (either EN_NODE or EN_LINK).
        iIndex       the element's current index (starting from 1).

        Returns:
        value the order in which the element's results were written to file.
        """
        value = ctypes.c_int()
        self.errcode = self._lib.EN_getresultindex(self._ph, objecttype, int(iIndex), ctypes.byref(value))
        self.ENgeterror()
        return value.value

    def ENgetrule(self, index):
        """ Retrieves summary information about a rule-based control.
        EPANET Version 2.2

        ENgetrule(index):

        Parameters:
        index   	  the rule's index (starting from 1).

        Returns:
        nPremises     	 number of premises in the rule's IF section.
        nThenActions    number of actions in the rule's THEN section.
        nElseActions    number of actions in the rule's ELSE section.
        priority        the rule's priority value.
        """
        nPremises = ctypes.c_int()
        nThenActions = ctypes.c_int()
        nElseActions = ctypes.c_int()
        priority = ctypes.c_double()
        self.errcode = self._lib.EN_getrule(self._ph, int(index), ctypes.byref(nPremises), ctypes.byref(nThenActions),
                                            ctypes.byref(nElseActions), ctypes.byref(priority))
        self.ENgeterror()
        return [nPremises.value, nThenActions.value, nElseActions.value, priority.value]

    def ENgetruleID(self, index):
        """ Gets the ID name of a rule-based control given its index.
        EPANET Version 2.2

        ENgetruleID(index)

        Parameters:
        index   	  the rule's index (starting from 1).

        Returns:
        id  the rule's ID name.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___rules.html
        """
        nameID = ctypes.create_string_buffer(self.EN_MAXID)
        self.errcode = self._lib.EN_getruleID(self._ph, int(index), ctypes.byref(nameID))
        self.ENgeterror()
        return nameID.value.decode()

    def ENgetstatistic(self, code):
        """ Retrieves a particular simulation statistic.
        EPANET 20100

        ENgetstatistic(code)

        Parameters:
        code  	   the type of statistic to retrieve (see EN_AnalysisStatistic).

        Returns:
        value the value of the statistic.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___reporting.html
        """
        value = ctypes.c_double()
        self.errcode = self._lib.EN_getstatistic(self._ph, int(code), ctypes.byref(value))
        self.ENgeterror()
        return value.value

    def ENgetthenaction(self, ruleIndex, actionIndex):
        """ Gets the properties of a THEN action in a rule-based control.
        EPANET Version 2.2

        ENgetthenaction(ruleIndex, actionIndex)

        Parameters:
        ruleIndex   	the rule's index (starting from 1).
        actionIndex   the index of the THEN action to retrieve (starting from 1).

        Returns:
        linkIndex   the index of the link in the action (starting from 1).
        status      the status assigned to the link (see RULESTATUS).
        setting     the value assigned to the link's setting.
        """
        linkIndex = ctypes.c_int()
        status = ctypes.c_int()
        setting = ctypes.c_double()
        self.errcode = self._lib.EN_getthenaction(self._ph, int(ruleIndex), int(actionIndex), ctypes.byref(linkIndex),
                                                  ctypes.byref(status), ctypes.byref(setting))
        self.ENgeterror()
        return [linkIndex.value, status.value, setting.value]

    def ENgettimeparam(self, paramcode):
        """ Retrieves the value of a time parameter.

        ENgettimeparam(paramcode)

        Parameters:
        paramcode    a time parameter code (see EN_TimeParameter).

        Returns:
        timevalue the current value of the time parameter (in seconds).
        """
        timevalue = ctypes.c_long()
        self.errcode = self._lib.EN_gettimeparam(self._ph, ctypes.c_int(paramcode), ctypes.byref(timevalue))
        self.ENgeterror()
        return timevalue.value

    def ENgettitle(self):
        """ Retrieves the title lines of the project.
        EPANET Version 2.2

        ENgettitle()

        Returns:
        line1 first title line
        line2 second title line
        line3 third title line
        """
        line1 = ctypes.create_string_buffer(80)
        line2 = ctypes.create_string_buffer(80)
        line3 = ctypes.create_string_buffer(80)
        self.errcode = self._lib.EN_gettitle(self._ph, ctypes.byref(line1), ctypes.byref(line2),
                                             ctypes.byref(line3))
        self.ENgeterror()
        return [line1.value.decode(), line2.value.decode(), line3.value.decode()]

    def ENgetversion(self):
        """ Retrieves the toolkit API version number.

        ENgetversion()

        Returns:
        LibEPANET the version of the OWA-EPANET toolkit.
        """
        LibEPANET = ctypes.c_int()
        self.errcode = self._lib.EN_getversion(ctypes.byref(LibEPANET))
        self.ENgeterror()
        return LibEPANET.value

    def ENgetvertex(self, index, vertex):
        """ Retrieves the coordinate's of a vertex point assigned to a link.
        EPANET Version 2.2

        ENgetvertex(index, vertex)

        Parameters:
        index      a link's index (starting from 1).
        vertex     a vertex point index (starting from 1).

        Returns:
        x  the vertex's X-coordinate value.
        y  the vertex's Y-coordinate value.
        """
        x = ctypes.c_double()
        y = ctypes.c_double()
        self.errcode = self._lib.EN_getvertex(self._ph, int(index), vertex, ctypes.byref(x), ctypes.byref(y))
        self.ENgeterror()
        return [x.value, y.value]

    def ENgetvertexcount(self, index):
        """ Retrieves the number of internal vertex points assigned to a link.

        ENgetvertexcount(index)

        Parameters:
        index      a link's index (starting from 1).

        Returns:
        count  the number of vertex points that describe the link's shape.
        """
        count = ctypes.c_int()
        self.errcode = self._lib.EN_getvertexcount(self._ph, int(index), ctypes.byref(count))
        self.ENgeterror()
        return count.value

    def ENinit(self, unitsType, headLossType):
        """ Initializes an EPANET project.
        EPANET Version 2.2

        ENinit(unitsType, headLossType)

        Parameters:
        unitsType    the choice of flow units (see EN_FlowUnits).
        headLossType the choice of head loss formula (see EN_HeadLossType).

        """
        self.errcode = self._lib.EN_init(self._ph, "", "", unitsType, headLossType)
        self.ENgeterror()

    def ENinitH(self, flag):
        """ Initializes a network prior to running a hydraulic analysis.

        ENinitH(flag)

        Parameters:
        flag    	a 2-digit initialization flag (see EN_InitHydOption).

        See also  ENinitH, ENrunH, ENnextH, ENreport, ENsavehydfile
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html
        """
        self.errcode = self._lib.EN_initH(self._ph, flag)
        self.ENgeterror()
        return

    def ENinitQ(self, saveflag):
        """ Initializes a network prior to running a water quality analysis.

        ENinitQ(saveflag)

        Parameters:
        saveflag  set to EN_SAVE (1) if results are to be saved to the project's
                  binary output file, or to EN_NOSAVE (0) if not.

        See also  ENinitQ, ENrunQ, ENnextQ
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___quality.html
        """
        self.errcode = self._lib.EN_initQ(self._ph, saveflag)
        self.ENgeterror()
        return

    def ENnextH(self):
        """ Determines the length of time until the next hydraulic event occurs in an extended period simulation.

        ENnextH()

        Returns:
        tstep the time (in seconds) until the next hydraulic event or 0 if at the end of the full simulation duration.

        See also  ENrunH
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html
        """
        tstep = ctypes.c_long()
        self.errcode = self._lib.EN_nextH(self._ph, ctypes.byref(tstep))
        self.ENgeterror()
        return tstep.value

    def ENnextQ(self):
        """ Advances a water quality simulation over the time until the next hydraulic event.

        ENnextQ()

        Returns:
        tstep time (in seconds) until the next hydraulic event or 0 if at the end of the full simulation duration.

        See also  ENstepQ, ENrunQ
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___quality.html
        """
        tstep = ctypes.c_long()
        self.errcode = self._lib.EN_nextQ(self._ph, ctypes.byref(tstep))
        self.ENgeterror()
        return tstep.value

    def ENopen(self, inpname=None, repname=None, binname=None):
        """ Opens an EPANET input file & reads in network data.

        ENopen(inpname, repname, binname)

        Parameters:
        inpname the name of an existing EPANET-formatted input file.
        repname the name of a report file to be created (or "" if not needed).
        binname the name of a binary output file to be created (or "" if not needed).

        See also ENclose
        """
        if inpname is None:
            inpname = self.inpfile
        if repname is None:
            repname = self.rptfile
            if repname is None:
                repname = inpname[0:-4] + '.txt'
        if binname is None:
            binname = self.binfile
            if binname is None:
                binname = repname[0:-4] + '.bin'

        self.inpfile = bytes(inpname, 'utf-8')
        self.rptfile = bytes(repname, 'utf-8')
        self.binfile = bytes(binname, 'utf-8')

        if self.isloaded:
            self.ENclose()
        if self.isloaded:
            raise RuntimeError("File is loaded and cannot be closed.")

        self._lib.EN_createproject(ctypes.byref(self._ph))
        self.errcode = self._lib.EN_open(self._ph, self.inpfile, self.rptfile, self.binfile)
        self.ENgeterror()
        if self.errcode < 100:
            self.isloaded = True
        return

    def ENopenH(self):
        """ Opens a project's hydraulic solver.

        ENopenH()

        See also  ENinitH, ENrunH, ENnextH, ENcloseH
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html"""
        self.errcode = self._lib.EN_openH(self._ph)
        self.ENgeterror()
        return

    def ENopenQ(self):
        """ Opens a project's water quality solver.

        ENopenQ()

        See also  ENopenQ, ENinitQ, ENrunQ, ENnextQ,
        ENstepQ, ENcloseQ
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___quality.html
        """
        self.errcode = self._lib.EN_openQ(self._ph)
        self.ENgeterror()
        return

    def ENreport(self):
        """ Writes simulation results in a tabular format to a project's report file.

        ENreport()

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___reporting.html
        """
        self.errcode = self._lib.EN_report(self._ph)
        self.ENgeterror()

    def ENresetreport(self):
        """ Resets a project's report options to their default values.

        ENresetreport()

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___reporting.html
        """
        self.errcode = self._lib.EN_resetreport(self._ph)
        self.ENgeterror()

    def ENrunH(self):
        """ Computes a hydraulic solution for the current point in time.

        ENrunH()

        Returns:
        t  the current simulation time in seconds.

        See also  ENinitH, ENrunH, ENnextH, ENcloseH
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html
        """
        t = ctypes.c_long()
        self.errcode = self._lib.EN_runH(self._ph, ctypes.byref(t))
        self.ENgeterror()
        return t.value

    def ENrunQ(self):
        """ Makes hydraulic and water quality results at the start of the current
        time period available to a project's water quality solver.

        ENrunQ()

        Returns:
        t  current simulation time in seconds.
        See also  ENopenQ, ENinitQ, ENrunQ, ENnextQ, ENstepQ
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___quality.html
        """
        t = ctypes.c_long()
        self.errcode = self._lib.EN_runQ(self._ph, ctypes.byref(t))
        self.ENgeterror()
        return t.value

    def ENsaveH(self):
        """ Transfers a project's hydraulics results from its temporary hydraulics file to its binary output file,
        where results are only reported at uniform reporting intervals.

        ENsaveH()

        """
        self.errcode = self._lib.EN_saveH(self._ph)
        self.ENgeterror()
        return

    def ENsavehydfile(self, fname):
        """ Saves a project's temporary hydraulics file to disk.

        ENsaveHydfile(fname)

        """
        self.errcode = self._lib.EN_savehydfile(self._ph, fname.encode("utf-8"))
        self.ENgeterror()

    def ENsaveinpfile(self, inpname):
        """ Saves a project's data to an EPANET-formatted text file.

        ENsaveinpfile(inpname)

        """
        self.errcode = self._lib.EN_saveinpfile(self._ph, inpname.encode("utf-8"))
        self.ENgeterror()
        return

    def ENsetbasedemand(self, index, demandIdx, value):
        """ Sets the base demand for one of a node's demand categories.
        EPANET Version 2.1

        ENsetbasedemand(index, demandIdx, value)

        Parameters:
        index    	  a node's index (starting from 1).
        demandIdx     the index of a demand category for the node (starting from 1).
        value    	  the new base demand for the category.

        """
        self.errcode = self._lib.EN_setbasedemand(self._ph, int(index), demandIdx, ctypes.c_double(value))
        self.ENgeterror()

    def ENsetcomment(self, object_, index, comment):
        """ Sets a comment to a specific index
        EPANET Version 2.2

        ENsetcomment(object, index, comment)

        Parameters:
        object_     a type of object (either EN_NODE, EN_LINK, EN_TIMEPAT or EN_CURVE)
                   e.g, obj.ToolkitConstants.EN_NODE
        index      objects index (starting from 1).
        comment    comment to be added.

        """
        self.errcode = self._lib.EN_setcomment(self._ph, object_, index, comment.encode('utf-8'))
        self.ENgeterror()

    def ENsetcontrol(self, cindex, ctype, lindex, setting, nindex, level):
        """ Sets the properties of an existing simple control.

        ENsetcontrol(cindex, ctype, lindex, setting, nindex, level)

        Parameters:
        cindex  the control's index (starting from 1).
        ctype   the type of control (see ControlTypes).
        lindex  the index of the link being controlled.
        setting the control setting applied to the link.
        nindex  the index of the node used to trigger the control (0 for EN_TIMER and EN_TIMEOFDAY controls).
        level   the action level (tank level, junction pressure, or time in seconds) that triggers the control.

        """
        self.errcode = self._lib.EN_setcontrol(self._ph, int(cindex), ctype, lindex, ctypes.c_double(setting), nindex,
                                               ctypes.c_double(level))
        self.ENgeterror()

    def ENsetcoord(self, index, x, y):
        """ Sets the (x,y) coordinates of a node.
        EPANET Version 2.1

        ENsetcoord(index, x, y)

        Parameters:
        index      a node's index.
        x          the node's X-coordinate value.
        y          the node's Y-coordinate value.

        """
        self.errcode = self._lib.EN_setcoord(self._ph, int(index), ctypes.c_double(x), ctypes.c_double(y))
        self.ENgeterror()

    def ENsetcurve(self, index, x, y, nfactors):
        """ Assigns a set of data points to a curve.
        EPANET Version 2.1

        ENsetcurve(index, x, y, nfactors)

        Parameters:
        index         a curve's index (starting from 1).
        x        	  an array of new x-values for the curve.
        y        	  an array of new y-values for the curve.
        nfactors      the new number of data points for the curve.

        See also ENsetcurvevalue
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___curves.html
        """
        if nfactors == 1:
            self.errcode = self._lib.EN_setcurve(self._ph, int(index), (ctypes.c_double * 1)(x),
                                                 (ctypes.c_double * 1)(y), nfactors)
        else:
            self.errcode = self._lib.EN_setcurve(self._ph, int(index), (ctypes.c_double * nfactors)(*x),
                                                 (ctypes.c_double * nfactors)(*y), nfactors)
        self.ENgeterror()

    def ENsetcurveid(self, index, Id):
        """ Changes the ID name of a data curve given its index.
        EPANET Version 2.2

        ENsetcurveid(index, Id)

        Parameters:
        index       a curve's index (starting from 1).
        Id        	an array of new x-values for the curve.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___curves.html
        """
        self.errcode = self._lib.EN_setcurveid(self._ph, int(index), Id.encode('utf-8'))
        self.ENgeterror()

    def ENsetcurvevalue(self, index, pnt, x, y):
        """ Sets the value of a single data point for a curve.
        EPANET Version 2.1

        ENsetcurvevalue(index, pnt, x, y)

        Parameters:
        index         a curve's index (starting from 1).
        pnt        	  the index of a point on the curve (starting from 1).
        x        	  the point's new x-value.
        y        	  the point's new y-value.

        """
        self.errcode = self._lib.EN_setcurvevalue(self._ph, int(index), pnt,
                                                  ctypes.c_double(x), ctypes.c_double(y))
        self.ENgeterror()

    def ENsetdemandmodel(self, Type, pmin, preq, pexp):
        """ Sets the Type of demand model to use and its parameters.
        EPANET Version 2.2

        ENsetdemandmodel(index, demandIdx, value)

        Parameters:
        Type         Type of demand model (see DEMANDMODEL).
        pmin         Pressure below which there is no demand.
        preq    	 Pressure required to deliver full demand.
        pexp    	 Pressure exponent in demand function.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___demands.html
        """
        self.errcode = self._lib.EN_setdemandmodel(self._ph, Type, ctypes.c_double(pmin),
                                                   ctypes.c_double(preq), ctypes.c_double(pexp))
        self.ENgeterror()

    def ENsetdemandname(self, node_index, demand_index, demand_name):
        """ Assigns a name to a node's demand category.
        EPANET Version 2.2

        ENsetdemandname(node_index, demand_index, demand_name)
        Parameters:
        node_index     a node's index (starting from 1).
        demand_index   the index of one of the node's demand categories (starting from 1).
        demand_name    the new name assigned to the category.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___demands.html
        """
        self.errcode = self._lib.EN_setdemandname(self._ph, int(node_index), int(demand_index), demand_name.encode("utf-8"))
        self.ENgeterror()
        return

    def ENsetdemandpattern(self, index, demandIdx, patInd):
        """ Sets the index of a time pattern used for one of a node's demand categories.

        ENsetdemandpattern(index, demandIdx, patInd)

        Parameters:
        index         a node's index (starting from 1).
        demandIdx     the index of one of the node's demand categories (starting from 1).
        patInd        the index of the time pattern assigned to the category.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___demands.html
        """
        self.errcode = self._lib.EN_setdemandpattern(self._ph, int(index), int(demandIdx), int(patInd))

    def ENsetelseaction(self, ruleIndex, actionIndex, linkIndex, status, setting):
        """ Sets the properties of an ELSE action in a rule-based control.
        EPANET Version 2.2

        ENsetelseaction(ruleIndex, actionIndex, linkIndex, status, setting)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        actionIndex   the index of the ELSE action being modified (starting from 1).
        linkIndex     the index of the link in the action (starting from 1).
        status        the new status assigned to the link (see RULESTATUS).
        setting       the new value assigned to the link's setting.

        """
        self.errcode = self._lib.EN_setelseaction(self._ph, int(ruleIndex), int(actionIndex), int(linkIndex), status,
                                                  ctypes.c_double(setting))
        self.ENgeterror()

    def ENsetflowunits(self, code):
        """ Sets a project's flow units.

        ENsetflowunits(code)

        Parameters:
        code        a flow units code (see EN_FlowUnits)

        """
        self.errcode = self._lib.EN_setflowunits(self._ph, code)
        self.ENgeterror()

    def ENsetheadcurveindex(self, pumpindex, curveindex):
        """ Assigns a curve to a pump's head curve.

        ENsetheadcurveindex(pumpindex, curveindex)

        Parameters:
        pumpindex     the index of a pump link (starting from 1).
        curveindex    the index of a curve to be assigned as the pump's head curve.

        """
        self.errcode = self._lib.EN_setheadcurveindex(self._ph, int(pumpindex), int(curveindex))
        self.ENgeterror()

    def ENsetjuncdata(self, index, elev, dmnd, dmndpat):
        """ Sets a group of properties for a junction node.
        EPANET Version 2.2

        ENsetjuncdata(index, elev, dmnd, dmndpat)

        Parameters:
        index      a junction node's index (starting from 1).
        elev       the value of the junction's elevation.
        dmnd       the value of the junction's primary base demand.
        dmndpat    the ID name of the demand's time pattern ("" for no pattern).

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___nodes.html
        """
        self.errcode = self._lib.EN_setjuncdata(self._ph, int(index), ctypes.c_double(elev), ctypes.c_double(dmnd),
                                                dmndpat.encode("utf-8"))
        self.ENgeterror()

    def ENsetlinkid(self, index, newid):
        """ Changes the ID name of a link.
        EPANET Version 2.2

        ENsetlinkid(index, newid)

        Parameters:
        index         a link's index (starting from 1).
        newid         the new ID name for the link.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___links.html
        """
        self.errcode = self._lib.EN_setlinkid(self._ph, int(index), newid.encode("utf-8"))
        self.ENgeterror()

    def ENsetlinknodes(self, index, startnode, endnode):
        """ Sets the indexes of a link's start- and end-nodes.
        EPANET Version 2.2

        ENsetlinknodes(index, startnode, endnode)

        Parameters:
        index         a link's index (starting from 1).
        startnode     The index of the link's start node (starting from 1).
        endnode       The index of the link's end node (starting from 1).
        """
        self.errcode = self._lib.EN_setlinknodes(self._ph, int(index), startnode, endnode)
        self.ENgeterror()

    def ENsetlinktype(self, indexLink, paramcode, actionCode):
        """ Changes a link's type.
        EPANET Version 2.2

        ENsetlinktype(id, paramcode, actionCode)

        Parameters:
        indexLink     a link's index (starting from 1).
        paramcode     the new type to change the link to (see self.LinkType).
        actionCode    the action taken if any controls contain the link.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___links.html
        """
        indexLink = ctypes.c_int(indexLink)
        self.errcode = self._lib.EN_setlinktype(self._ph, ctypes.byref(indexLink), paramcode, actionCode)
        self.ENgeterror()
        return indexLink.value

    def ENsetlinkvalue(self, index, paramcode, value):
        """ Sets a property value for a link.

        ENsetlinkvalue(index, paramcode, value)

        Parameters:
        index         a link's index.
        paramcode     the property to set (see EN_LinkProperty).
        value         the new value for the property.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___links.html
        """
        self.errcode = self._lib.EN_setlinkvalue(self._ph, ctypes.c_int(index), ctypes.c_int(paramcode),
                                                 ctypes.c_double(value))
        self.ENgeterror()
        return

    def ENsetnodeid(self, index, newid):
        """ Changes the ID name of a node.
        EPANET Version 2.2

        ENsetnodeid(index, newid)

        Parameters:
        index      a node's index (starting from 1).
        newid      the new ID name for the node.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___nodes.html
        """
        self.errcode = self._lib.EN_setnodeid(self._ph, int(index), newid.encode('utf-8'))
        self.ENgeterror()

    def ENsetnodevalue(self, index, paramcode, value):
        """ Sets a property value for a node.
        EPANET Version 2.2

        ENsetnodevalue(index, paramcode, value)

        Parameters:
        index      a node's index (starting from 1).
        paramcode  the property to set (see EN_NodeProperty, self.getToolkitConstants).
        value      the new value for the property.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___nodes.html
        """
        self.errcode = self._lib.EN_setnodevalue(self._ph, ctypes.c_int(index), ctypes.c_int(paramcode),
                                                 ctypes.c_double(value))
        self.ENgeterror()
        return

    def ENsetoption(self, optioncode, value):
        """ Sets the value for an anlysis option.

        ENsetoption(optioncode, value)

        Parameters:
        optioncode   a type of analysis option (see EN_Option).
        value        the new value assigned to the option.
        """
        self.errcode = self._lib.EN_setoption(self._ph, optioncode, ctypes.c_double(value))
        self.ENgeterror()

    def ENsetpattern(self, index, factors, nfactors):
        """ Sets the pattern factors for a given time pattern.

        ENsetpattern(index, factors, nfactors)

        Parameters:
        index      a time pattern index (starting from 1).
        factors    an array of new pattern factor values.
        nfactors   the number of factor values supplied.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___patterns.html
        """
        self.errcode = self._lib.EN_setpattern(self._ph, int(index), (ctypes.c_double * nfactors)(*factors), nfactors)
        self.ENgeterror()

    def ENsetpatternid(self, index, Id):
        """ Changes the ID name of a time pattern given its index.
        EPANET Version 2.2

        ENsetpatternid(index, id)

        Parameters:
        index      a time pattern index (starting from 1).
        id         the time pattern's new ID name.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___patterns.html
        """
        self.errcode = self._lib.EN_setpatternid(self._ph, int(index), Id.encode('utf-8'))
        self.ENgeterror()

    def ENsetpatternvalue(self, index, period, value):
        """ Sets a time pattern's factor for a given time period.

        ENsetpatternvalue(index, period, value)

        Parameters:
        index      a time pattern index (starting from 1).
        period     a time period in the pattern (starting from 1).
        value      the new value of the pattern factor for the given time period.
        """
        self.errcode = self._lib.EN_setpatternvalue(self._ph, int(index), period, ctypes.c_double(value))
        self.ENgeterror()

    def ENsetpipedata(self, index, length, diam, rough, mloss):
        """ Sets a group of properties for a pipe link.
        EPANET Version 2.2

        ENsetpipedata(index, length, diam, rough, mloss)

        Parameters:
        index         the index of a pipe link (starting from 1).
        length        the pipe's length.
        diam          the pipe's diameter.
        rough         the pipe's roughness coefficient.
        mloss         the pipe's minor loss coefficient.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___links.html
        """
        self.errcode = self._lib.EN_setpipedata(self._ph, int(index), ctypes.c_double(length),
                                                ctypes.c_double(diam), ctypes.c_double(rough),
                                                ctypes.c_double(mloss))
        self.ENgeterror()

    def ENsetpremise(self, ruleIndex, premiseIndex, logop, object_, objIndex, variable, relop, status, value):
        """ Sets the properties of a premise in a rule-based control.
        EPANET Version 2.2

        ENsetpremise(ruleIndex, premiseIndex, logop, object, objIndex, variable, relop, status, value)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        premiseIndex  the position of the premise in the rule's list of premises.
        logop         the premise's logical operator ( IF = 1, AND = 2, OR = 3 ).
        object_       the type of object the premise refers to (see RULEOBJECT).
        objIndex      the index of the object (e.g. the index of a tank).
        variable      the object's variable being compared (see RULEVARIABLE).
        relop         the premise's comparison operator (see RULEOPERATOR).
        status        the status that the object's status is compared to (see RULESTATUS).
        value         the value that the object's variable is compared to.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___rules.html
        """
        self.errcode = self._lib.EN_setpremise(self._ph, int(ruleIndex), int(premiseIndex), logop, object_,
                                               objIndex, variable, relop, status, ctypes.c_double(value))
        self.ENgeterror()

    def ENsetpremiseindex(self, ruleIndex, premiseIndex, objIndex):
        """ Sets the index of an object in a premise of a rule-based control.
        EPANET Version 2.2

        ENsetpremiseindex(ruleIndex, premiseIndex, objIndex)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        premiseIndex  the premise's index (starting from 1).
        objIndex      the index of the object (e.g. the index of a tank).
        """
        self.errcode = self._lib.EN_setpremiseindex(self._ph, int(ruleIndex), int(premiseIndex), objIndex)
        self.ENgeterror()

    def ENsetpremisestatus(self, ruleIndex, premiseIndex, status):
        """ Sets the status being compared to in a premise of a rule-based control.
        EPANET Version 2.2

        ENsetpremisestatus(ruleIndex, premiseIndex, status)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        premiseIndex  the premise's index (starting from 1).
        status        the status that the premise's object status is compared to (see RULESTATUS).
        """
        self.errcode = self._lib.EN_setpremisestatus(self._ph, int(ruleIndex), int(premiseIndex), status)
        self.ENgeterror()

    def ENsetpremisevalue(self, ruleIndex, premiseIndex, value):
        """ Sets the value in a premise of a rule-based control.
        EPANET Version 2.2

        ENsetpremisevalue(ruleIndex, premiseIndex, value)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        premiseIndex  the premise's index (starting from 1).
        value         The value that the premise's variable is compared to.
        """
        self.errcode = self._lib.EN_setpremisevalue(self._ph, int(ruleIndex), premiseIndex, ctypes.c_double(value))
        self.ENgeterror()

    def ENsetqualtype(self, qualcode, chemname, chemunits, tracenode):
        """ Sets the type of water quality analysis to run.

        ENsetqualtype(qualcode, chemname, chemunits, tracenode)

        Parameters:
        qualcode    the type of analysis to run (see EN_QualityType, self.QualityType).
        chemname    the name of the quality constituent.
        chemunits   the concentration units of the constituent.
        tracenode   a type of analysis option (see ENOption).

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___options.html
        """
        self.errcode = self._lib.EN_setqualtype(self._ph, qualcode, chemname.encode("utf-8"),
                                                chemunits.encode("utf-8"), tracenode.encode("utf-8"))
        self.ENgeterror()
        return

    def ENsetreport(self, command):
        """ Processes a reporting format command.

        ENsetreport(command)

        Parameters:
        command    a report formatting command.

        See also ENreport
        """
        self.errcode = self._lib.EN_setreport(self._ph, command.encode("utf-8"))
        self.ENgeterror()

    def ENsetrulepriority(self, ruleIndex, priority):
        """ Sets the priority of a rule-based control.
        EPANET Version 2.2

        ENsetrulepriority(ruleIndex, priority)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        priority      the priority value assigned to the rule.
        """
        self.errcode = self._lib.EN_setrulepriority(self._ph, int(ruleIndex), ctypes.c_double(priority))
        self.ENgeterror()

    def ENsetstatusreport(self, statuslevel):
        """ Sets the level of hydraulic status reporting.

        ENsetstatusreport(statuslevel)

        Parameters:
        statuslevel  a status reporting level code (see EN_StatusReport).


        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___reporting.html
        """
        self.errcode = self._lib.EN_setstatusreport(self._ph, statuslevel)
        self.ENgeterror()

    def ENsettankdata(self, index, elev, initlvl, minlvl, maxlvl, diam, minvol, volcurve):
        """ Sets a group of properties for a tank node.
        EPANET Version 2.2

        ENsettankdata(index, elev, initlvl, minlvl, maxlvl, diam, minvol, volcurve)

        Parameters:
        index       a tank node's index (starting from 1).
        elev      	the tank's bottom elevation.
        initlvl     the initial water level in the tank.
        minlvl      the minimum water level for the tank.
        maxlvl      the maximum water level for the tank.
        diam        the tank's diameter (0 if a volume curve is supplied).
        minvol      the new value for the property.
        volcurve    the volume of the tank at its minimum water level.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___nodes.html
        """
        self.errcode = self._lib.EN_settankdata(
            self._ph, index, ctypes.c_double(elev), ctypes.c_double(initlvl), ctypes.c_double(minlvl),
            ctypes.c_double(maxlvl), ctypes.c_double(diam), ctypes.c_double(minvol), volcurve.encode('utf-8'))
        self.ENgeterror()

    def ENsetthenaction(self, ruleIndex, actionIndex, linkIndex, status, setting):
        """ Sets the properties of a THEN action in a rule-based control.
        EPANET Version 2.2

        ENsetthenaction(ruleIndex, actionIndex, linkIndex, status, setting)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        actionIndex   the index of the THEN action to retrieve (starting from 1).
        linkIndex     the index of the link in the action.
        status        the new status assigned to the link (see EN_RuleStatus)..
        setting       the new value assigned to the link's setting.

        """
        self.errcode = self._lib.EN_setthenaction(self._ph, int(ruleIndex), int(actionIndex), int(linkIndex), status,
                                                  ctypes.c_double(setting))
        self.ENgeterror()

    def ENsettimeparam(self, paramcode, timevalue):
        """ Sets the value of a time parameter.

        ENsettimeparam(paramcode, timevalue)

        Parameters:
        paramcode    a time parameter code (see EN_TimeParameter).
        timevalue    the new value of the time parameter (in seconds).
        """
        self.solve = 0
        self.errcode = self._lib.EN_settimeparam(self._ph, ctypes.c_int(paramcode), ctypes.c_long(int(timevalue)))
        self.ENgeterror()

    def ENsettitle(self, line1, line2, line3):
        """ Sets the title lines of the project.
        EPANET Version 2.2

        ENsettitle(line1, line2, line3)

        Parameters:
        line1   first title line
        line2   second title line
        line3   third title line
        """
        self.errcode = self._lib.EN_settitle(self._ph, line1.encode("utf-8"), line2.encode("utf-8"),
                                             line3.encode("utf-8"))
        self.ENgeterror()

    def ENsetvertices(self, index, x, y, vertex):
        """ Assigns a set of internal vertex points to a link.
        EPANET Version 2.2

        ENsetvertices(index, x, y, vertex)

        Parameters:
        index      a link's index (starting from 1).
        x          an array of X-coordinates for the vertex points.
        y          an array of Y-coordinates for the vertex points.
        vertex     the number of vertex points being assigned.
        """
        self.errcode = self._lib.EN_setvertices(self._ph, int(index), (ctypes.c_double * vertex)(*x),
                                                (ctypes.c_double * vertex)(*y), vertex)
        self.ENgeterror()

    def ENsolveH(self):
        """ Runs a complete hydraulic simulation with results for all time periods
        written to a temporary hydraulics file.

        ENsolveH()

        See also ENopenH, ENinitH, ENrunH, ENnextH, ENcloseH
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html
        """
        self.errcode = self._lib.EN_solveH(self._ph)
        self.ENgeterror()
        return

    def ENsolveQ(self):
        """ Runs a complete water quality simulation with results at uniform reporting
        intervals written to the project's binary output file.

        ENsolveQ()

        See also ENopenQ, ENinitQ, ENrunQ, ENnextQ, ENcloseQ
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html"""
        self.errcode = self._lib.EN_solveQ(self._ph)
        self.ENgeterror()
        return

    def ENstepQ(self):
        """ Advances a water quality simulation by a single water quality time step.

        ENstepQ()

        Returns:
        tleft  time left (in seconds) to the overall simulation duration.

        See also ENrunQ, ENnextQ
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html
        """
        tleft = ctypes.c_long()
        self.errcode = self._lib.EN_stepQ(self._ph, ctypes.byref(tleft))
        self.ENgeterror()
        return tleft.value

    def ENusehydfile(self, hydfname):
        """ Uses a previously saved binary hydraulics file to supply a project's hydraulics.

        ENusehydfile(hydfname)

        Parameters:
        hydfname  the name of the binary file containing hydraulic results.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html
        """
        self.errcode = self._lib.EN_usehydfile(self._ph, hydfname.encode("utf-8"))
        self.ENgeterror()
        return

    def ENwriteline(self, line):
        """ Writes a line of text to a project's report file.

        ENwriteline(line)

        Parameters:
        line         a text string to write.
        """
        self.errcode = self._lib.EN_writeline(self._ph, line.encode("utf-8"))
        self.ENgeterror()
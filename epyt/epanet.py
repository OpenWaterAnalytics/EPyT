# -*- coding: utf-8 -*-
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
   D.G. Eliades, M. Kyriakou, S. Vrachimis and M.M. Polycarpou,
   "EPANET-MATLAB Toolkit: An Open-Source Software for Interfacing EPANET with MATLAB", in Proc. 14th International
   Conference on Computing and Control for the Water Industry (CCWI),
   The Netherlands, Nov 2016, p.8. (doi:10.5281/zenodo.831493)

   Other python packages related to the EPANET engine:
   wntr
   Klise, K.A., Murray, R., Haxton, T. (2018). An overview of the Water
   Network Tool for Resilience (WNTR),
   In Proceedings of the 1st International WDSA/CCWI Joint Conference,
   Kingston, Ontario, Canada, July 23-25, 075, 8p.

   epanet-python
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
import json
import math
import os
import platform
import random
import re
import string
import struct
import subprocess
import sys
import traceback
import warnings
from ctypes import cdll, byref, create_string_buffer, c_uint64, c_void_p, c_int, c_double, c_float, c_long, \
    c_char_p
from datetime import datetime, timezone

try:
    from importlib.resources import files  # Python 3.9+
except ImportError:
    from importlib_resources import files  # Backport for < 3.9
from inspect import getmembers, isfunction, currentframe, getframeinfo
from pathlib import Path
from shutil import copyfile
from types import SimpleNamespace

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm

epyt_root = str(files("epyt"))

from epyt import __version__, __msxversion__, __lastupdate__

red = "\033[91m"
reset = "\033[0m"


class error_handler:
    _psi_units = {"MDG", "IMGD", "CFS", "GPM"}
    _kpa_units = {"CMH", "CMS", "MLD", "CMD", "LPS", "LPM"}
    last_error = None

    def _logFunctionError(self, function_name):
        """Log and display a detailed error with traceback."""
        # Print visible error
        print(f"{red}UserWarning: {function_name}{reset}")
        if hasattr(self, 'msx') and 'MSX' in function_name:
            message = self.msx.MSXgeterror(self.msx.errcode)

            print(f"{red}MSX Error: {message}{reset}")
        elif hasattr(self, 'api'):
            message = self.api.ENgeterror(self.api.errcode)
            print(f"{red}EPANET Error: {message}{reset}")

        self.last_error = [function_name, message]
        # Show where in user code it occurred
        tb = traceback.extract_stack()
        for frame in reversed(tb):
            if "epanet.py" not in frame.filename:
                print(f"{red}{frame.filename}, line {frame.lineno}: {frame.line.strip()}{reset}")
                break
    # dev 2.3
    # def _flowUnitsCheck(self):
    #     """Return metric type based on unit."""
    #     flow_unit = self.getFlowUnits()
    #     if flow_unit in self._psi_units:
    #         return "PSI"
    #     if flow_unit in self._kpa_units:
    #         return "KPA AND METERS"
    #     return "UNKNOWN"

    def __getattribute__(self, function_id):
        attr = super().__getattribute__(function_id)

        if (callable(attr) and not function_id.startswith(("__", "_", "EN", "printv", "MSX", "test", "load"))):
            def _wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                api = None
                if hasattr(self, 'msx') and 'MSX' in function_id.upper():
                    api = self.msx
                elif hasattr(self, 'api'):
                    api = self.api
                if api is not None and api.errcode != 0:
                    self._logFunctionError(function_id)
                return result

            return _wrapper
        return attr


class ToolkitConstants:
    # Limits on the size of character arrays used to store ID names
    # and text messages.
    def __init__(self):
        pass

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

    # MSX Constants
    MSX_NODE = 0
    MSX_LINK = 1
    MSX_TANK = 2
    MSX_SPECIES = 3
    MSX_TERM = 4
    MSX_PARAMETER = 5
    MSX_CONSTANT = 6
    MSX_PATTERN = 7

    MSX_BULK = 0
    MSX_WALL = 1

    MSX_NOSOURCE = -1
    MSX_CONCEN = 0
    MSX_MASS = 1
    MSX_SETPOINT = 2
    MSX_FLOWPACED = 3


def safe_delete(file):
    if isinstance(file, list):
        for file_path in file:
            if os.path.exists(file_path):
                try:
                    try:
                        os.unlink(rf"{file_path}")
                    except:
                        os.remove(rf"{file_path}")
                except Exception as e:
                    print(f"Could not delete {file}: {e}")
    else:
        if os.path.exists(file):
            try:
                try:
                    os.unlink(rf"{file}")
                except:
                    os.remove(rf"{file}")
            except Exception as e:
                print(f"Could not delete {file}: {e}")


class EpytValues:

    def __init__(self):
        pass

    def disp(self):
        """ Displays the values on the command window

        :param self: Values to be printed on the command window
        :type self: EpytValues class
        :return: None

        """
        print_values = vars(self)
        print('\n')
        for i in print_values:
            print(f'{i}: {print_values[str(i)]}', end='\n')

    def to_dict(self):
        """ Transform EpytValues class values to dict format

        :param self: Values to add in the dictionary
        :type self: EpytValues class
        :return: dictionary with the values
        :rtype: dict

        """
        dict_values = vars(self)
        return dict_values

    def to_excel(self, filename=None, attributes=None, allValues=False,
                 node_id_list=None, link_id_list=None, both=False, header=True):
        """
        Save to an Excel file the values of EpytValues class.

        :param filename: Excel filename, defaults to None
        :type filename: str, optional
        :param attributes: Attributes to add to the file, defaults to None
        :type attributes: str or list of str, optional
        :param allValues: If True, writes all the values into a separate "All values" sheet, defaults to False
        :type allValues: bool, optional
        :param node_id_list: Array of IDs for node-related attributes
        :type node_id_list: list or np.ndarray, optional
        :param link_id_list: Array of IDs for link-related attributes
        :type link_id_list: list or np.ndarray, optional
        :param both: If True, and ID array available, print both 'Index' and 'Id'. If no ID array, just Index.
                     If False and ID array available, print only 'Id'; if no ID array, print only 'Index'.
        :type both: bool, optional
        :param header: If False, remove the first row from all sheets and do not write column headers
        :type header: bool, optional
        :return: None
        """
        node_keywords = ['nodequality', 'head', 'demand', 'pressure']
        link_keywords = [
            'linkquality', 'flow', 'velocity', 'headloss',
            'Status', 'Setting', 'ReactionRate', 'StatusStr', 'FrictionFactor'
        ]

        def is_node_attribute(key):
            key_lower = key.lower()
            return (any(re.search(r'\b' + kw + r'\b', key_lower) for kw in node_keywords)
                    or 'node' in key_lower)

        def is_link_attribute(key):
            key_lower = key.lower()
            return (any(re.search(r'\b' + kw + r'\b', key_lower) for kw in link_keywords)
                    or 'link' in key_lower)

        if filename is None:
            rand_id = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            filename = 'ToExcelfile_' + rand_id + '.xlsx'
        if '.xlsx' not in filename:
            filename = filename + '.xlsx'

        dictVals = EpytValues.to_dict(self)
        dictValss = {}
        for i in dictVals:
            if isinstance(dictVals[i], (np.ndarray, np.matrix)):
                dictValss[i] = dictVals[i].transpose().tolist()
            else:
                dictValss[i] = dictVals[i]
        dictVals = dictValss

        def process_dataframe(key, df):
            header_labels = []
            num_rows = len(df)
            chosen_id_array = None

            if is_node_attribute(key) and node_id_list is not None:
                chosen_id_array = node_id_list
            elif is_link_attribute(key) and link_id_list is not None:
                chosen_id_array = link_id_list

            print_id_col = False
            print_index_col = False

            if both:
                print_index_col = True
                if chosen_id_array is not None:
                    print_id_col = True
            else:
                if chosen_id_array is not None:
                    print_id_col = True
                else:
                    print_index_col = True

            if print_id_col and chosen_id_array is not None:
                if len(chosen_id_array) != num_rows:
                    warnings.warn(
                        f"ID array length does not match rows for '{key}'. Truncating."
                    )
                adjusted_id_array = chosen_id_array[:num_rows]
                df.insert(0, 'Id', adjusted_id_array)
                header_labels.append('Id')

            if print_index_col:
                index_values = list(range(1, num_rows + 1))
                if print_id_col:
                    id_col = df.pop('Id')
                    df.insert(0, 'Index', index_values)
                    df.insert(1, 'Id', id_col)
                    header_labels.insert(0, 'Index')
                else:
                    df.insert(0, "Index", index_values)
                    header_labels.insert(0, 'Index')

            num_data_columns = df.shape[1] - len(header_labels)
            if 'Time' in dictVals and len(dictVals['Time']) == num_data_columns:
                header_labels.extend(dictVals['Time'])
            else:
                data_column_names = [f"Column{i + 1}" for i in range(num_data_columns)]
                header_labels.extend(data_column_names)

            df.columns = header_labels
            return df

        with pd.ExcelWriter(filename, mode="w") as writer:

            for key, data in dictVals.items():
                if key == 'Time':
                    continue
                if attributes and key not in attributes:
                    continue
                if not isinstance(data, (list, np.ndarray, pd.Series, pd.DataFrame)):
                    continue

                df = pd.DataFrame(data)
                df = process_dataframe(key, df)

                if not header:
                    df.columns = df.iloc[0]
                    df = df.iloc[1:]
                    df.to_excel(writer, sheet_name=key, index=False, header=True)
                else:
                    df.to_excel(writer, sheet_name=key, index=False, header=True)

            if allValues:
                worksheet_name = 'All values'
                first_iter = True
                for key, data in dictVals.items():
                    if key == 'Time':
                        continue
                    if attributes and key not in attributes:
                        continue
                    if not isinstance(data, (list, np.ndarray, pd.Series, pd.DataFrame)):
                        print(f"Skipping key '{key}' due to unsupported data type: {type(data)}")
                        continue

                    df = pd.DataFrame(data)
                    df = process_dataframe(key, df)

                    worksheet = writer.sheets.get(worksheet_name)
                    if first_iter:
                        df.to_excel(writer, sheet_name=worksheet_name, index=False, header=header, startrow=1)
                        worksheet = writer.sheets[worksheet_name]
                        worksheet.write(0, 0, key)
                        first_iter = False
                    else:
                        startrow = worksheet.dim_rowmax + 3
                        worksheet.write(startrow - 1, 0, key)
                        df.to_excel(writer, sheet_name=worksheet_name, index=False, header=header, startrow=startrow)

        print(f"Data successfully exported to {filename}")

    def to_json(self, filename=None):
        """ Transforms val class values to json object and saves them
        to a json file if filename is provided

        :param self: Values to add in the json file
        :type self: val class
        :param filename: json filename, defaults to None
        :type filename: str, optional
        :return: the json object with the values
        :rtype: json object

        """
        dictVals = EpytValues.to_dict(self)
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


class epanet(error_handler):
    """ EPyt main functions class

    Example with custom library
            epanetlib=os.path.join(os.getcwd(), 'epyt','libraries','win','epanet2.dll')
            d = epanet(inpname, msx=True,customlib=epanetlib)
     """

    def __init__(self, *argv, version=2.2, ph=False, loadfile=False, customlib=None, display_msg=True,
                 display_warnings=True):
        # Constants
        self.msx = None
        if display_warnings:
            warnings.simplefilter('always')  # 'action', "error", "ignore", "always", "default", "module", "once"
        # Demand model types. DDA #0 Demand driven analysis,
        # PDA #1 Pressure driven analysis.
        self.customlib = customlib
        self.MSXFile = None
        self.MSXTempFile = None
        self.DEMANDMODEL = ['DDA', 'PDA']
        # Link types
        self.TYPELINK = ['CVPIPE', 'PIPE', 'PUMP', 'PRV', 'PSV',
                         'PBV', 'FCV', 'TCV', 'GPV']
        # Constants for mixing models
        self.TYPEMIXMODEL = ['MIX1', 'MIX2', 'FIFO', 'LIFO']
        # Node types
        self.TYPENODE = ['JUNCTION', 'RESERVOIR', 'TANK']
        # Constants for pumps
        self.TYPEPUMP = ['CONSTANT_HORSEPOWER', 'POWER_FUNCTION', 'CUSTOM']
        # Link PUMP status
        self.TYPEPUMPSTATE = ['XHEAD', '', 'CLOSED', 'OPEN', '', 'XFLOW']
        # Constants for quality
        self.TYPEQUALITY = ['NONE', 'CHEM', 'AGE', 'TRACE', 'MULTIS']
        # Constants for sources
        self.TYPESOURCE = ['CONCEN', 'MASS', 'SETPOINT', 'FLOWPACED']
        # Constants for statistics
        self.TYPESTATS = ['NONE', 'AVERAGE', 'MINIMUM', 'MAXIMUM', 'RANGE']
        # Constants for control: 'LOWLEVEL', 'HILEVEL', 'TIMER', 'TIMEOFDAY'
        self.TYPECONTROL = ['LOWLEVEL', 'HIGHLEVEL', 'TIMER', 'TIMEOFDAY']
        # Constants for report: 'YES', 'NO', 'FULL'
        self.TYPEREPORT = ['YES', 'NO', 'FULL']
        # Link Status
        self.TYPESTATUS = ['CLOSED', 'OPEN']
        # Constants for pump curves: 'PUMP', 'EFFICIENCY', 'VOLUME', 'HEADLOSS'
        self.TYPECURVE = ['VOLUME', 'PUMP', 'EFFICIENCY', 'HEADLOSS', 'GENERAL']
        # Constants of headloss types: HW: Hazen-Williams,
        # DW: Darcy-Weisbach, CM: Chezy-Manning
        self.TYPEHEADLOSS = ['HW', 'DW', 'CM']
        # Constants for units
        self.TYPEUNITS = ['CFS', 'GPM', 'MGD', 'IMGD', 'AFD',
                          'LPS', 'LPM', 'MLD', 'CMH', 'CMD']
        # 0 = closed (max. head exceeded), 1 = temporarily closed,
        # 2 = closed, 3 = open, 4 = active (partially open)
        # 5 = open (max. flow exceeded), 6 = open (flow setting not met),
        # 7 = open (pressure setting not met)
        self.TYPEBINSTATUS = ['CLOSED (MAX. HEAD EXCEEDED)', 'TEMPORARILY CLOSED',
                              'CLOSED', 'OPEN', 'ACTIVE(PARTIALY OPEN)',
                              'OPEN (MAX. FLOW EXCEEDED',
                              'OPEN (PRESSURE SETTING NOT MET)']
        # Constants for rule-based controls: 'OPEN', 'CLOSED', 'ACTIVE'
        self.RULESTATUS = ['OPEN', 'CLOSED', 'ACTIVE']
        # Constants for rule-based controls: 'IF', 'AND', 'OR'
        self.LOGOP = ['IF', 'AND', 'OR']
        # Constants for rule-based controls: 'NODE','LINK','SYSTEM'
        self.RULEOBJECT = ['NODE', 'LINK', 'SYSTEM']
        # Constants for rule-based controls: 'DEMAND', 'HEAD', 'GRADE' etc.
        self.RULEVARIABLE = ['DEMAND', 'HEAD', 'GRADE', 'LEVEL', 'PRESSURE', 'FLOW',
                             'STATUS', 'SETTING', 'POWER', 'TIME',
                             'CLOCKTIME', 'FILLTIME', 'DRAINTIME']
        # Constants for rule-based controls: '=', '~=', '<=' etc.
        self.RULEOPERATOR = ['=', '~=', '<=', '>=', '<', '>', 'IS',
                             'NOT', 'BELOW', 'ABOVE']

        # Initial attributes
        self.classversion = __version__
        self.api = epanetapi(version, ph=ph, customlib=customlib)
        self.display_msg = display_msg
        if self.display_msg and self.customlib is None:
            print(f'EPANET version {self.getVersion()} '
                  f'loaded (EPyT version v{self.classversion} - Last Update: {__lastupdate__}).')

        # ToolkitConstants: Contains all parameters from epanet2_2.h
        self.ToolkitConstants = ToolkitConstants()
        self.api.solve = 0

        if len(argv) > 0:
            self.InputFile = argv[0]

            self.__exist_inp_file = False
            if len(argv) == 1:
                if not os.path.exists(self.InputFile):
                    for root, dirs, files in os.walk(epyt_root):
                        for name in files:
                            if name.lower().endswith(".inp"):
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
                # Create a new INP file (Working Copy)
                copyfile(self.InputFile, self.TempInpFile)
                # self.saveInputFile(self.TempInpFile)
                # Close input file
                self.closeNetwork()
                # Load temporary file
                rptfile = self.InputFile[0:-4] + '_temp.txt'
                binfile = self.InputFile[0:-4] + '_temp.bin'
                self.RptTempfile = rptfile
                self.BinTempfile = binfile
                self.api.ENopen(self.TempInpFile, rptfile, binfile)
                # Parameters
                if not loadfile:
                    self.__getInitParams()

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
            if self.display_msg:
                print(f'Input File {self.netName} loaded successfully.\n')

    def addControls(self, control, *argv):
        """ Adds a new simple control.

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

        Example 3: Pump 9 speed is set to 1.5 at 16 hours or 57600
        seconds into the simulation.

        >>> index = d.addControls('LINK 9 1.5 AT TIME 16:00')
        >>> d.getControls(index).disp()
        >>> index = d.addControls('LINK 9 1.5 AT TIME 57600') #in seconds
        >>> d.getControls(index).disp()

        Example 4: Link 12 is closed at 10 am and opened at 8 pm throughout
        the simulation.

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
            * nodeIndex:  index of the node used to control the link
            (0 for EN_TIMER and EN_TIMEOFDAY controls).
            * level:	  action level (tank level, junction pressure, or
            time in seconds) that triggers the control.

        Control type codes consist of the following:
            * EN_LOWLEVEL      0   Control applied when tank level or node
            pressure drops below specified level
            * EN_HILEVEL       1   Control applied when tank level or node
            pressure rises above specified level
            * EN_TIMER         2   Control applied at specific time
            into simulation
            * EN_TIMEOFDAY     3   Control applied at specific time of day

        Code example:
        index = d.addControls(type, linkIndex, setting, nodeIndex, level)

        >>> index = d.addControls(0, 13, 0, 11, 100)
        # retrieve controls of index in dict format
        >>> d.getControls(index).to_dict()

        See also deleteControls, getControls, setControls,
        getControlRulesCount.
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
                index = self.api.ENaddcontrol(control,
                                              linkIndex,
                                              controlSettingValue,
                                              nodeIndex,
                                              controlLevel)
        return index

    def addCurve(self, *argv):
        """ Adds a new curve appended to the end of the existing curves.
        Returns the new curve's index.

        :param *argv: value index or value
        :type *argv: int or float
        :raises: No curve ID or curve values exist
        :return: new curve valueIndex
        :rtype: int

        Example: ID selected without a space in between the letters

        >>> new_curve_ID = 'NewCurve'
        >>> x_y_1 = [0, 730]
        >>> x_y_2 = [1000, 500]
        >>> x_y_3 = [1350, 260]
        # X and Y values selected
        >>> values = [x_y_1, x_y_2, x_y_3]
        # New curve added
        >>> curve_index = d.addCurve(new_curve_ID, values)
        # Retrieves all the info of curves
        >>> d.getCurvesInfo().disp()

        See also getCurvesInfo, getCurveType, setCurve,setCurveValue,
        setCurveNameID, setCurveComment.
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
        # Retrieves the number of links
        >>> d.getLinkPipeCount()
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
        # Retrieves the new link's length
        >>> d.getLinkLength(pipeIndex)
        >>> d.plot()

        Example 3: Adds a new pipe given it's length, diameter,
        roughness coefficient and minor loss coefficient.

        >>> pipeID = 'newPipe_3'
        >>> fromNode = '31'
        >>> toNode = '22'
        >>> length = 500
        >>> diameter = 15
        >>> roughness = 120
        >>> minorLossCoeff = 0.2
        >>> d.getLinkPipeCount()
        >>> pipeIndex = d.addLinkPipe(pipeID, fromNode, toNode, length,
        >>>                           diameter, roughness, minorLossCoeff)
        >>> d.getLinkPipeCount()
        >>> d.getLinkLength(pipeIndex)
        # Retrieves the new link's diameter
        >>> d.getLinkDiameter(pipeIndex)
        # Retrieves the new link's roughness coefficient
        >>> d.getLinkRoughnessCoeff(pipeIndex)
        # Retrieves the new link's minor loss coefficient
        >>> d.getLinkMinorLossCoeff(pipeIndex)
        >>> d.plot()

        See also plot, setLinkNodesIndex, addLinkPipeCV, addNodeJunction,
        deleteLink, setLinkDiameter.
        """
        index = self.api.ENaddlink(pipeID, self.ToolkitConstants.EN_PIPE,
                                   fromNode, toNode)
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
        # Retrieves the number of pipes
        >>> d.getLinkPipeCount()
        >>> cvPipeIndex = d.addLinkPipeCV(cvPipeID, fromNode, toNode)
        >>> d.getLinkPipeCount()
        # Plots the network in a new figure
        >>> d.plot()

        Example 2: Adds a new control valve pipe given it's length.

        >>> cvPipeID = 'newCVPipe_2'
        >>> fromNode = '11'
        >>> toNode = '22'
        >>> length = 600
        >>> d.getLinkPipeCount()
        >>> cvPipeIndex = d.addLinkPipeCV(cvPipeID, fromNode, toNode, length)
        >>> d.getLinkPipeCount()
        # Retrieves the new link's length
        >>> d.getLinkLength(cvPipeIndex)
        >>> d.plot()

        Example 3: Adds a new control valve pipe given it's length, diameter,
        roughness coefficient and minor loss coefficient.

        >>> cvPipeID = 'newCVPipe_3'
        >>> fromNode = '31'
        >>> toNode = '22'
        >>> length = 500
        >>> diameter = 15
        >>> roughness = 120
        >>> minorLossCoeff = 0.2
        >>> d.getLinkPipeCount()
        >>> cvPipeIndex = d.addLinkPipeCV(cvPipeID, fromNode, toNode, length,
        >>>                               diameter, roughness, minorLossCoeff)
        >>> d.getLinkPipeCount()
        >>> d.getLinkLength(cvPipeIndex)
        # Retrieves the new link's diameter
        >>> d.getLinkDiameter(cvPipeIndex)
        # Retrieves the new link's roughness coefficient
        >>> d.getLinkRoughnessCoeff(cvPipeIndex)
        # Retrieves the new link's minor loss coefficient
        >>> d.getLinkMinorLossCoeff(cvPipeIndex)
        >>> d.plot()

        See also plot, setLinkNodesIndex, addLinkPipe, addNodeJunction,
        deleteLink, setLinkDiameter.
        """
        index = self.api.ENaddlink(cvpipeID, self.ToolkitConstants.EN_CVPIPE,
                                   fromNode, toNode)
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
        # Retrieves the number of pumps
        >>> d.getLinkPumpCount()
        >>> pumpIndex = d.addLinkPump(pumpID, fromNode, toNode)
        >>> d.getLinkPumpCount()
        # Plots the network in a new figure
        >>> d.plot()

        Example 2: Adds a new pump given it's initial status.::

        >>> pumpID = 'newPump_2'
        >>> fromNode = '31'
        >>> toNode = '22'
        >>> initialStatus = 0    # (CLOSED)
        >>> d.getLinkPumpCount()
        >>> pumpIndex = d.addLinkPump(pumpID, fromNode, toNode, initialStatus)
        >>> d.getLinkPumpCount()
        # Retrieves the new pump's initial status
        >>> d.getLinkInitialStatus(pumpIndex)
        >>> d.plot()

        Example 3: Adds a new pump given it's initial status, initial speed
        setting, power and pattern index.

        >>> pumpID = 'newPump_3'
        >>> fromNode = '11'
        >>> toNode = '22'
        >>> initialStatus = 1    # (OPEN)
        >>> initialSetting = 1.2
        >>> power = 10
        >>> patternIndex = 1
        >>> d.getLinkPumpCount()
        >>> pumpIndex = d.addLinkPump(pumpID, fromNode, toNode, initialStatus,
        >>>                           initialSetting, power, patternIndex)
        >>> d.getLinkPumpCount()
        >>> d.getLinkInitialStatus(pumpIndex)
        # Retrieves the new pump's initial setting
        >>> d.getLinkInitialSetting(pumpIndex)
        # Retrieves the new pump's power
        >>> d.getLinkPumpPower(pumpIndex)
        # Retrieves the new pump's pattern index
        >>> d.getLinkPumpPatternIndex(pumpIndex)
        >>> d.plot()

        See also: plot, setLinkNodesIndex, addLinkPipe, addNodeJunction,
        deleteLink, setLinkInitialStatus.
        """
        index = self.api.ENaddlink(pumpID, self.ToolkitConstants.EN_PUMP,
                                   fromNode, toNode)
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
        return self.api.ENaddlink(vID, self.ToolkitConstants.EN_FCV,
                                  fromNode, toNode)

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
        return self.api.ENaddlink(vID, self.ToolkitConstants.EN_GPV,
                                  fromNode, toNode)

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
        return self.api.ENaddlink(vID, self.ToolkitConstants.EN_PBV,
                                  fromNode, toNode)

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
        return self.api.ENaddlink(vID, self.ToolkitConstants.EN_PRV,
                                  fromNode, toNode)

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
        return self.api.ENaddlink(vID, self.ToolkitConstants.EN_PSV,
                                  fromNode, toNode)

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
        return self.api.ENaddlink(vID, self.ToolkitConstants.EN_TCV,
                                  fromNode, toNode)

    def addNodeJunction(self, juncID, *argv):
        """ Adds new junction

        Returns the index of the new junction.

        The following data can be set(optional):
          1. Coordinates
          2. Elevation
          3. Primary base demand
          4. ID name of the demand's time pattern

        Example 1: Adds a new junction with the default coordinates
        (i.e. [0, 0]).

        >>> junctionID = 'newJunction_1'
        >>> junctionIndex = d.addNodeJunction(junctionID)
        >>> d.plot()

        Example 2: Adds a new junction with coordinates [X, Y] = [20, 10].

        >>> junctionID = 'newJunction_2'
        >>> junctionCoords = [20, 10]
        >>> junctionIndex = d.addNodeJunction(junctionID, junctionCoords)
        >>> d.plot(highlightnode=junctionIndex)

        Example 3: Adds a new junction with coordinates [X, Y] = [20, 20]
        and elevation = 500.

        >>> junctionID = 'newJunction_3'
        >>> junctionCoords = [20, 20]
        >>> junctionElevation = 500
        >>> junctionIndex = d.addNodeJunction(junctionID, junctionCoords,
        >>>                                   junctionElevation)
        >>> d.getNodeElevations(junctionIndex)
        >>> d.plot()

        Example 4: Adds a new junction with coordinates [X, Y] = [10, 40],
        elevation = 500 and demand = 50.

        >>> junctionID = 'newJunction_4'
        >>> junctionCoords = [10, 40]
        >>> junctionElevation = 500
        >>> demand = 50
        >>> junctionIndex = d.addNodeJunction(junctionID, junctionCoords,
        >>>                                   junctionElevation, demand)
        >>> d.getNodeBaseDemands(junctionIndex)
        >>> d.plot()

        Example 5: Adds a new junction with coordinates [X, Y] = [10, 20],
        elevation = 500,
        demand = 50 and pattern ID = the 1st time pattern ID(if exists).

        >>> junctionID = 'newJunction_5'
        >>> junctionCoords = [10, 20]
        >>> junctionElevation = 500
        >>> demand = 50
        >>> demandPatternID = d.getPatternNameID(1)
        >>> junctionIndex = d.addNodeJunction(junctionID, junctionCoords,
        >>>                                   junctionElevation, demand,
        >>>                                   demandPatternID)
        >>> d.getNodeDemandPatternNameID()[1][junctionIndex-1]
        >>> d.plot()

        See also plot, setLinkNodesIndex, addNodeReservoir, setNodeComment,
        deleteNode, setNodeBaseDemands.
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
        """ Adds a new demand to a junction given the junction index,
        base demand, demand time pattern and demand
        category name.  Returns the values of the new demand
        category index.
        A blank string can be used for demand time pattern and demand name
        category to indicate
        that no time pattern or category name is associated with the demand.

        Example 1: New demand added with the name 'new demand' to the 1st node,
        with 100 base demand,
        using the 1st time pattern.

        >>> d.addNodeJunctionDemand(1, 100, '1', 'new demand')
        # Retrieves the indices of all demands for all nodes.
        >>> d.getNodeJunctionDemandIndex()
        # Retrieves the demand category names of the 2nd demand index.
        >>> d.getNodeJunctionDemandName()[2]

        Example 2: New demands added with the name 'new demand' to the 1st and
        2nd node, with 100 base demand, using the 1st time pattern.

        >>> d.addNodeJunctionDemand([1, 2], 100, '1', 'new demand')
        # Retrieves the indices of all demands for all nodes.
        >>> d.getNodeJunctionDemandIndex()
        # Retrieves the demand category names of the 2nd demand index.
        >>> d.getNodeJunctionDemandName()[2]

        Example 3: New demands added with the name 'new demand' to the 1st and
        2nd node, with 100 and 110 base demand respectively, using the
        1st time pattern.

        >>> d.addNodeJunctionDemand([1, 2], [100, 110], '1', 'new demand')
        # Retrieves the indices of all demands for all nodes.
        >>> d.getNodeJunctionDemandIndex()
        # Retrieves the demand category names of the 2nd demand index
        >>> d.getNodeJunctionDemandName()[2]     .

        Example 4: New demands added with the name 'new demand' to the 1st and
        2nd node, with 100 and 110 base demand respectively, using the 1st
         time pattern.

        >>> d.addNodeJunctionDemand([1, 2], [100, 110], ['1', '1'],
        >>>                         'new demand')
        # Retrieves the indices of all demands for all nodes.
        >>> d.getNodeJunctionDemandIndex()
        # Retrieves the demand category names of the 2nd demand index.
        >>> d.getNodeJunctionDemandName()[2]

        Example 5: New demands added with the names 'new demand1' and
        'new demand2' to the 1st and 2nd node, with 100 and 110 base demand
        respectively, using the 1st and 2nd(if exists)
        time pattern respectively.

        >>> d.addNodeJunctionDemand([1, 2], [100, 110], ['1', '2'],
        >>>                         ['new demand1', 'new demand2'])
        # Retrieves the indices of all demands for all nodes.
        >>> d.getNodeJunctionDemandIndex()
        # Retrieves the demand category names of the 2nd demand index.
        >>> d.getNodeJunctionDemandName()[2]
        See also deleteNodeJunctionDemand, getNodeJunctionDemandIndex,
        getNodeJunctionDemandName, setNodeJunctionDemandName,
        getNodeBaseDemands.
        """
        nodeIndex = argv[0]
        baseDemand = argv[1]
        demandPattern = ''
        demandName = ''
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
            demandName = [demandName for _ in nodeIndex]

        return self.getNodeJunctionDemandIndex(nodeIndex, demandName)

    def addNodeReservoir(self, resID, *argv):
        """
        Adds a new reservoir.
        Returns the index of the new reservoir.

        Example 1: Adds a new reservoir with the default coordinates
        (i.e. [0, 0])

        >>> reservoirID = 'newReservoir_1'
        >>> reservoirIndex = d.addNodeReservoir(reservoirID)
        >>> d.plot()

        Example 2: Adds a new reservoir with coordinates [X, Y] = [20, 30].

        >>> reservoirID = 'newReservoir_2'
        >>> reservoirCoords = [20, 30]
        >>> reservoirIndex = d.addNodeReservoir(reservoirID, reservoirCoords)
        >>> d.plot()

        See also plot, setLinkNodesIndex, addNodeJunction, self.addLinkPipe,
        deleteNode, setNodeBaseDemands.
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

        Example 3: Adds a new tank with coordinates [X, Y] = [20, 20]
        and elevation = 100.

        >>> tankID = 'newTank_3'
        >>> tankCoords = [20, 20]
        >>> elevation = 100
        >>> tankIndex = d.addNodeTank(tankID, tankCoords, elevation)
        >>> d.plot()

        Example 4: Adds a new tank with coordinates [X, Y] = [20, 30],
        elevation = 100, initial level = 130, minimum water level = 110,
        maximum water level = 160, diameter = 60,
        minimum water volume = 200000, volume curve ID = ''.

        >>> tankID = 'newTank_4'
        >>> tankCoords = [20, 30]
        >>> elevation = 100
        >>> initialLevel = 130
        >>> minimumWaterLevel = 110
        >>> maximumWaterLevel = 160
        >>> diameter = 60
        >>> minimumWaterVolume = 200000
        >>> volumeCurveID = ''   # Empty for no curve
        >>> tankIndex = d.addNodeTank(tankID, tankCoords, elevation,
        >>>                           initialLevel, minimumWaterLevel,
        >>>                           maximumWaterLevel, diameter,
        >>>                           minimumWaterVolume, volumeCurveID)
        >>> t_data = d.getNodeTankData(tankIndex)
        >>> d.plot()

        See also plot, setLinkNodesIndex, addNodeJunction, addLinkPipe,
        deleteNode, setNodeBaseDemands.
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
        self.setNodeTankData(index, elev, intlvl, minlvl, maxlvl, diam,
                             minvol, volcurve)
        return index

    def addPattern(self, *argv):
        """ Adds a new time pattern to the network.

        Example 1:

        # Retrieves the ID labels of time patterns
        >>> d.getPatternNameID()
        >>> patternID = 'new_pattern'
        # Adds a new time pattern given it's ID
        >>> patternIndex = d.addPattern(patternID)
        >>> patternIndex = d.addPattern(patternID+'2', 1)
        >>> d.getPatternNameID()

        Example 2:

        >>> patternID = 'new_pattern'
        >>> patternMult = [1.56, 1.36, 1.17, 1.13, 1.08,
        ... 1.04, 1.2, 0.64, 1.08, 0.53, 0.29, 0.9, 1.11,
        ... 1.06, 1.00, 1.65, 0.55, 0.74, 0.64, 0.46,
        ... 0.58, 0.64, 0.71, 0.66]
        # Adds a new time pattern given ID and the multiplier
        >>> patternIndex = d.addPattern(patternID, patternMult)
        >>> d.getPatternNameID()
        >>> d.getPattern()

        See also getPattern, setPattern, setPatternNameID, setPatternValue,
        setPatternComment.
        """
        self.api.ENaddpattern(argv[0])
        index = self.getPatternIndex(argv[0])
        if len(argv) == 1:
            self.setPattern(index, [1] * max(self.getPatternLengths()))
        else:
            self.setPattern(index, argv[1])
        return index

    def addRules(self, rule):
        """ Adds a new rule-based control to a project.

        .. note:: Rule format: Following the format used in an EPANET input
                      file.
                     'RULE ruleid \n IF object objectid attribute relation
                      attributevalue \n THEN object objectid
                      STATUS/SETTING IS value \n PRIORITY value'

        See more: 'https://nepis.epa.gov/Adobe/PDF/P1007WWU.pdf' (Page 164)

        The example is based on d = epanet('Net1.inp')

        Example:
        >>> d.getRuleCount()
        >>> d.addRules('RULE RULE-1 \n IF TANK 2 LEVEL >= 140 \n THEN PUMP 9
        >>>             STATUS IS CLOSED \n PRIORITY 1')
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

        Example 1: Rotate the network by 60 degrees counter-clockwise around
        the index 1 node.
        >>> d = epanet('Net1.inp')
        >>> d.plot()
        >>> d.appRotateNetwork(60)
        >>> d.plot()

        Example 2: Rotate the network by 150 degrees counter-clockwise around
        the reservoir with index 921.
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
        R = np.array([[np.cos(theta * 2 * np.pi / 360),
                       -np.sin(theta * 2 * np.pi / 360)],
                      [np.sin(theta * 2 * np.pi / 360),
                       np.cos(theta * 2 * np.pi / 360)]], dtype=float)
        # Do the rotation:
        xCoord_new = [xCoord[i] - x_center for i in xCoord]
        yCoord_new = [yCoord[i] - y_center for i in yCoord]
        # v = [xCoord, yCoord]
        # s = v - center   # Shift points in the plane so that the center of
        # rotation is at the origin.
        s = np.array([xCoord_new, yCoord_new], dtype=float)
        so = R * s  # Apply the rotation about the origin.
        newxCoord = so[0, :] + x_center  # Shift again so the origin goes back
        # to the desired center of rotation.
        newyCoord = so[1, :] + y_center
        # Set the new coordinates
        for i in range(1, self.getNodeCount() + 1):
            self.setNodeCoordinates(i, [newxCoord[0, i - 1],
                                        newyCoord[0, i - 1]])
        if sum(self.getLinkVerticesCount()) != 0:
            xVertCoord = self.getNodeCoordinates()['x_vert']
            yVertCoord = self.getNodeCoordinates()['y_vert']
            for i in range(1, self.getLinkCount() + 1):
                if self.getLinkVerticesCount(i) != 0:
                    vertX_temp = xVertCoord[i]
                    vertY_temp = yVertCoord[i]
                    # Shift points in the plane so that the center of
                    # rotation is at the origin.
                    vertX_temp = [j - x_center for j in vertX_temp]
                    vertY_temp = [j - y_center for j in vertY_temp]
                    # Apply the rotation about the origin.
                    s = np.array([vertX_temp, vertY_temp], dtype=float)
                    so = R * s
                    # Shift again so the origin goes back to the desired
                    # center of rotation.
                    newxVertCoord = so[0, :] + x_center
                    newvyVertCoord = so[1, :] + y_center
                    LinkID = self.getLinkNameID(i)
                    self.setLinkVertices(LinkID,
                                         newxVertCoord.tolist()[0],
                                         newvyVertCoord.tolist()[0])

    def appShiftNetwork(self, xDisp, yDisp):
        """ Shifts the network by xDisp in the x-direction and
        by yDisp in the y-direction

        Example 1: Shift the network by 1000 feet in the x-axis and
        -1000 feet in the y-axis

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
        """ Clears the contents of a project's report file.

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

        See also openHydraulicAnalysis, saveHydraulicFile,
        closeQualityAnalysis.
        """
        self.api.ENcloseH()

    def closeNetwork(self):
        """ Closes down the Toolkit system.

        Example:

        >>> d.closeNetwork()

        See also loadEPANETFile, closeHydraulicAnalysis,
        closeQualityAnalysis.
        """
        self.api.ENclose()

    def closeQualityAnalysis(self):
        """ Closes the water quality analysis system, freeing
        all allocated memory.

        Example:

        >>> d.closeQualityAnalysis()

        For more, you can type help (d.epanet.getNodePressure)
        and check examples 3 & 4.

        See also openQualityAnalysis, initializeQualityAnalysis,
        closeHydraulicAnalysis.
        """
        self.api.ENcloseQ()

    def copyReport(self, fileName):
        """ Copies the current contents of a project's report file
        to another file.

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
                    os.unlink(os.path.join(net_dir, filename))
                except:
                    pass

    def deleteControls(self, *argv):
        """ Deletes an existing simple control.

        Example 1:

        # Retrieves the parameters of all controls
        >>> d.getControls()
        # Deletes the existing simple controls
        >>> d.deleteControls()
        >>> d.getControls()

        Example 2:

        # Adds a new simple control(index = 3)
        >>> index = d.addControls('LINK 9 43.2392 AT TIME 4:00:00')
        >>> d.getControls(index)
        # Deletes the 3rd simple control
        >>> d.deleteControls(index)
        >>> d.getControls()

        Example 3:

        # Adds a new simple control(index = 3)
        >>> index_3 = d.addControls('LINK 9 43.2392 AT TIME 4:00:00')
        # Adds a new simple control(index = 4)
        >>> index_4 = d.addControls('LINK 10 43.2392 AT TIME 4:00:00')
        >>> d.getControls(index_3)
        >>> d.getControls(index_4)
        # Deletes the 3rd and 4th simple controls
        >>> d.deleteControls([index_3, index_4])
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
        # Retrieves the ID of the 1st curve
        >>> idCurve = d.getCurveNameID(1)
        #  Deletes a curve given it's ID
        >>> d.deleteCurve(idCurve)
        >>> d.getCurveNameID()

        Example 2:

        >>> index = 1
        >>> d.deleteCurve(index)             # Deletes a curve given it's index
        >>> d.getCurveNameID()

        See also addCurve, setCurve, setCurveNameID, setCurveValue,
        setCurveComment.
        """
        if type(idCurve) is str:
            indexCurve = self.getCurveIndex(idCurve)
        else:
            indexCurve = idCurve
        self.api.ENdeletecurve(indexCurve)

    def deleteLink(self, idLink, *argv):
        """ Deletes a link.

        condition = 0 | if is EN_UNCONDITIONAL: Deletes all controls and
        rules related to the object
        condition = 1 | if is EN_CONDITIONAL: Cancel object deletion
        if contained in controls and rules
        Default condition is 0.

        Example 1:

        # Retrieves the ID label of all links
        >>> d.getLinkNameID()
        # Retrieves the ID label of the 1st link
        >>> idLink = d.getLinkNameID(1)
        # Deletes the 1st link given it's ID
        >>> d.deleteLink(idLink)
        >>> d.getLinkNameID()

        Example 2:

        >>> idLink = d.getLinkPumpNameID(1)
        >>> condition = 1
        # Attempts to delete a link contained in controls (error occurs)
        >>> d.deleteLink(idLink, condition)

        Example 3:

        >>> indexLink = 1
        # Deletes the 1st link given it's index
        >>> d.deleteLink(indexLink)
        >>> d.getLinkNameID()

        See also addLinkPipe, deleteNode, deleteRules, setNodeCoordinates,
        setLinkPipeData.
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
        """ Deletes nodes.

        condition = 0 | if is EN_UNCONDITIONAL: Deletes all controls,
        rules and links related to the object
        condition = 1 | if is EN_CONDITIONAL: Cancel object deletion if
        contained in controls, rules and links
        Default condition is 0.

        Example 1:

        # Retrieves the total number of all nodes
        >>> d.getNodeCount()
        # Retrieves the ID label of the 1st node
        >>> idNode = d.getNodeNameID(1)
        # Deletes the 1st node given it's ID
        >>> d.deleteNode(idNode)
        >>> d.getNodeCount()

        Example 2:

        >>> idNode = d.getNodeNameID(1)
        >>> condition = 1
        # Attempts to delete a node connected to links (error occurs)
        >>> d.deleteNode(idNode, condition)

        Example 3:

        >>> index = 1
        # Deletes the 1st node given it's index
        >>> d.deleteNode(index)
        >>> d.getNodeNameID()

        Example 4:

        >>> idNodes = d.getNodeNameID([1,2])
        >>> d.getNodeCount()
        # Deletes 2 nodes given their IDs
        >>> d.deleteNode(idNodes)
        >>> d.getNodeCount()

        See also addNodeJunction, deleteLink, deleteRules, setNodeCoordinates,
        setNodeJunctionData.
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
        """ Deletes a demand from a junction given the junction
        index and demand index.
        Returns the remaining(if exist) node demand indices.

        Example 1:

        >>> nodeIndex = 1
        >>> baseDemand = 100
        >>> patternId = '1'
        >>> categoryIndex = 1
        # Retrieves the indices of all demands for the 1st node
        >>> d.getNodeJunctionDemandIndex(nodeIndex)
        # Retrieves the names of all nodes demand category
        >>> d.getNodeJunctionDemandName()
        # Retrieves the name of the 1st demand category of the 1st node
        >>> d.getNodeJunctionDemandName()[categoryIndex][nodeIndex-1]
        # Adds a new demand to the 1st node and returns the new
        # demand index
        >>> categoryIndex = d.addNodeJunctionDemand(nodeIndex, baseDemand,
        >>>                                         patternId, 'new demand')
        # Retrieves the indices of all demands for the 1st node
        >>> d.getNodeJunctionDemandIndex(nodeIndex)
        # Retrieves the names of all nodes demand category
        >>> d.getNodeJunctionDemandName()
        # Retrieves the name of the 2nd demand category of the 1st node
        >>> d.getNodeJunctionDemandName()[categoryIndex][nodeIndex-1]
        # Deletes the 2nd demand of the 1st node
        >>> d.deleteNodeJunctionDemand(1, 2)
        >>> d.getNodeJunctionDemandIndex(nodeIndex)

        Example 2:

        >>> nodeIndex = 1
        >>> baseDemand = 100
        >>> patternId = '1'
        # Adds a new demand to the first node and returns the new demand index
        >>> categoryIndex_2 = d.addNodeJunctionDemand(nodeIndex,
        ...                                           baseDemand,
        ...                                           patternId,
        ...                                           'new demand_2')
        # Adds a new demand to the first node and returns the new demand index
        >>> categoryIndex_3 = d.addNodeJunctionDemand(nodeIndex,
        ...                                           baseDemand,
        ...                                           patternId,
        ...                                           'new demand_3')
        # Retrieves the name of the 2nd demand category of the 1st node
        >>> d.getNodeJunctionDemandName()[categoryIndex_2][nodeIndex-1]
        # Deletes all the demands of the 1st node
        >>> d.deleteNodeJunctionDemand(1)
        # Retrieves the indices of all demands for the 1st node
        >>> d.getNodeJunctionDemandIndex(nodeIndex)

        Example 3:

        >>> nodeIndex = [1, 2, 3]
        >>> baseDemand = [100, 110, 150]
        >>> patternId = ['1', '1', '']
        # Adds 3 new demands to the first 3 nodes
        >>> categoryIndex = d.addNodeJunctionDemand(nodeIndex, baseDemand,
        ...                                         patternId, ['new demand_1',
        ...                                         'new demand_2',
        ...                                         'new demand_3'])
        # Deletes all the demands of the first 3 nodes
        >>> d.getNodeJunctionDemandName()[2]
        >>> d.getNodeJunctionDemandIndex(nodeIndex)
        >>> d.deleteNodeJunctionDemand([1,2,3])
        >>> d.getNodeJunctionDemandIndex(nodeIndex)


        See also addNodeJunctionDemand, getNodeJunctionDemandIndex,
        getNodeJunctionDemandName, setNodeJunctionDemandName,
        getNodeBaseDemands.
        """
        nodeIndex = argv[0]
        if len(argv) == 1:
            numDemand = len(self.getNodeJunctionDemandIndex())
            if not isList(nodeIndex):
                for i in range(1, numDemand + 1):
                    self.api.ENdeletedemand(nodeIndex, 1)
            else:
                for j in nodeIndex:
                    for i in range(1, numDemand + 1):
                        self.api.ENdeletedemand(j, 1)

        elif len(argv) == 2:
            self.api.ENdeletedemand(nodeIndex, argv[1])

    def deletePattern(self, idPat):
        """ Deletes a time pattern from a project.

        Example 1:

        # Retrieves the ID of the 1st pattern
        >>> idPat = d.getPatternNameID(1)
        # Deletes the 1st pattern given it's ID
        >>> d.deletePattern(idPat)
        >>> d.getPatternNameID()

        Example 2:

        >>> index = 1
        # Deletes the 1st pattern given it's index
        >>> d.deletePattern(index)
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
        for i in range(len(idPat), 0, -1):
            self.api.ENdeletepattern(i)

    def deleteProject(self):
        """ Deletes the epanet project
        """
        self.api.ENdeleteproject()

    def deleteRules(self, *argv):
        """ Deletes an existing rule-based control given it's index.
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
            self.api.ENdeleterule(index[i - 1])

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

        # Retrieves the computed quality value at the first node
        >>> d.getNodeActualQualitySensingNodes(1)
        # Retrieves the computed quality value at the first three nodes
        >>> d.getNodeActualQualitySensingNodes(1,2,3)
        For more, you can check examples 3 & 4 of getNodePressure.

        See also getNodeActualDemand, getNodeActualDemandSensingNodes,
        getNodePressure, getNodeHydraulicHead, getNodeActualQuality,
        getNodeMassFlowRate.
        """
        value = []
        if len(argv) > 0:
            indices = argv[0]
        else:
            indices = self.getNodeIndex()
        for i in indices:
            value.append(
                self.api.ENgetnodevalue(i, self.ToolkitConstants.EN_QUALITY)
            )
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

        # Retrieves all the time-series data
        >>> d.getComputedHydraulicTimeSeries()

        Example 2:

        # Retrieves all the time-series demands
        >>> d.getComputedHydraulicTimeSeries().Demand
        # Retrieves all the time-series flows
        >>> d.getComputedHydraulicTimeSeries().Flow

        Example 3:

        # Retrieves all the time-series Time, Pressure, Velocity
        >>> data = d.getComputedHydraulicTimeSeries(['Time',
        ...                                         'Pressure',
        ...                                         'Velocity'])
        >>> time = data.Time
        >>> pressure = data.Pressure
        >>> velocity = data.Velocity

        See also getComputedQualityTimeSeries, getComputedTimeSeries.
        """
        value = EpytValues()
        self.openHydraulicAnalysis()
        self.api.solve = 1
        self.initializeHydraulicAnalysis()
        sensingnodes = 0
        if len(argv) == 0:
            attrs = ['time', 'pressure', 'demand', 'demanddeficit', 'head',
                     'tankvolume', 'flow', 'velocity', 'headloss', 'status',
                     'setting', 'energy', 'efficiency', 'state']
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
            value.DemandSensingNodes = {}
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
                value.DemandSensingNodes[k] = \
                    self.getNodeActualDemandSensingNodes(
                        attrs[sensingnodes - 1]
                    )
            if 'head' in attrs:
                value.Head[k] = self.getNodeHydraulicHead()
            if 'tankvolume' in attrs:
                value.TankVolume[k] = np.zeros(
                    self.getNodeJunctionCount() +
                    self.getNodeReservoirCount()
                )
                value.TankVolume[k] = np.concatenate((
                    value.TankVolume[k],
                    self.getNodeTankVolume()))
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
                value.Efficiency[k] = np.concatenate((
                    value.Efficiency[k],
                    self.getLinkPumpEfficiency()))
                value.Efficiency[k] = np.concatenate((
                    value.Efficiency[k],
                    np.zeros(self.getLinkValveCount())))
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

        value_final = EpytValues()
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

        # Retrieves all the time-series data
        >>> d.getComputedQualityTimeSeries()
        Example 2:

        # Retrieves all the time-series node quality
        >>> d.getComputedQualityTimeSeries().NodeQuality
        # Retrieves all the time-series link quality
        >>> d.getComputedQualityTimeSeries().LinkQuality

        Example 3:

        # Retrieves all the time-series Time, NodeQuality, LinkQuality
        >>> data = d.getComputedQualityTimeSeries(['time',
        ...                                        'nodequality',
                                                   'linkquality'])
        >>> time = data.Time
        >>> node_quality = data.NodeQuality
        >>> link_quality = data.LinkQuality

        See also getComputedHydraulicTimeSeries, getComputedTimeSeries.
        """
        value = EpytValues()
        sensingnodes = 0
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
                value.QualitySensingNodes[k] = \
                    self.getNodeActualQualitySensingNodes(argv[1])
            if 'demandSensingNodes' in attrs:
                value.DemandSensingNodes[k] = \
                    self.getNodeActualDemandSensingNodes(
                        attrs[sensingnodes - 1]
                    )
            if t < sim_duration:
                tleft = self.stepQualityAnalysisTimeLeft()
            k += 1
        self.closeQualityAnalysis()
        value.Time = np.array(value.Time)
        value_final = EpytValues()
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
        value.WarnFlag = False
        if self.errcode:
            value.WarnFlag = True
            value.ErrCode = self.errcode
            self.api.ENgeterror(self.errcode)

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
        value_final = EpytValues()
        val_dict = value.__dict__
        for i in val_dict:
            if type(val_dict[i]) is dict:
                exec(f"value_final.{i} = np.array(list(val_dict[i].values()))")
            else:
                exec(f"value_final.{i} = val_dict[i]")
        value_final.Status = value_final.Status.astype(int)
        return value_final

    def getComputedTimeSeries_ENepanet(self, tempfile=None, binfile=None, rptfile=None):
        """ Run analysis using ENepanet function """

        if tempfile is not None:
            self.saveInputFile(tempfile)
        else:
            self.saveInputFile(self.TempInpFile)
            uuID = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        if binfile is None:
            binfile = '@#' + uuID + '.bin'
        if rptfile is None:
            rptfile = self.TempInpFile[:-4] + '.txt'
        self.api.ENclose()
        if tempfile is not None:
            self.api.ENepanet(tempfile, rptfile, binfile)
        else:
            self.api.ENepanet(self.TempInpFile, rptfile, binfile)

        fid = open(binfile, "rb")
        value = self.__readEpanetBin(fid, binfile, 0)
        value.WarnFlag = False
        if self.errcode:
            value.ErrCode = self.errcode
            value.WarnFlag = True
        value.StatusStr = {}
        for i in range(1, len(value.Status) + 1):
            value.StatusStr[i] = []
            for j in value.Status[i]:
                value.StatusStr[i].append(self.TYPEBINSTATUS[int(j)])
        # Remove report bin txt , files @#
        for file in Path(".").glob("@#*.txt"):
            file.unlink()
        value.Time = np.array(value.Time)
        value_final = EpytValues()
        val_dict = value.__dict__
        for i in val_dict:
            if type(val_dict[i]) is dict:
                exec(f"value_final.{i} = np.array(list(val_dict[i].values()))")
            else:
                exec(f"value_final.{i} = val_dict[i]")
        value_final.Status = value_final.Status.astype(int)
        self.loadEPANETFile(self.TempInpFile)
        return value_final

    def getAdjacencyMatrix(self):
        """Compute the adjacency matrix (connectivity graph) considering the flows, at different time steps or the
        mean flow, Compute the new adjacency matrix based on the mean flow in the network"""
        Fmean = np.mean(self.getComputedTimeSeries().Flow, 0)
        Fsign = np.sign(Fmean)
        Nidx = self.getLinkNodesIndex()
        fmax = np.max(Nidx)
        A = np.zeros((fmax, fmax))
        for i, nnid in enumerate(Nidx):
            if Fsign.item(i) == 1:
                A[nnid[0] - 1, nnid[1] - 1] = 1
            else:
                A[nnid[1] - 1, nnid[0] - 1] = 1
        return A

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

        # Retrieves the parameters of all control statements
        >>> d.getControls()
        # Retrieves the type of the 1st control
        >>> d.getControls(1).Type
        # Retrieves the ID of the link associated with the 1st control
        >>> d.getControls(1).LinkID
        # Retrieves the setting of the link associated with the 1st control
        >>> d.getControls(1).Setting
        # Retrieves the ID of the node associated with the 1st control
        >>> d.getControls(1).NodeID
        # Retrieves the value of the node associated with the 1st control
        >>> d.getControls(1).Value
        # Retrieves the 1st control statement
        >>> d.getControls(1).Control
        # Retrieves all the parameters of the first control statement in a dict
        >>> d.getControls(1).to_dict()
        # Retrieves the parameters of the first two control statements
        >>> d.getControls([1,2])

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
            value[i] = EpytValues()
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
                value[i].Control = 'LINK ' + value[i].LinkID + ' ' + \
                                   str(value[i].Setting) + ' IF NODE ' + \
                                   value[i].NodeID + ' BELOW ' + str(value[i].Value)
            elif self.ControlTypes[-1] == 'HIGHLEVEL':
                value[i].Control = 'LINK ' + value[i].LinkID + ' ' + \
                                   str(value[i].Setting) + ' IF NODE ' + \
                                   value[i].NodeID + ' ABOVE ' + str(value[i].Value)
            elif self.ControlTypes[-1] == 'TIMER':
                value[i].Control = 'LINK ' + value[i].LinkID + ' ' + \
                                   str(value[i].Setting) + \
                                   ' AT TIME ' + str(value[i].Value)
            elif self.ControlTypes[-1] == 'TIMEOFDAY':
                value[i].Control = 'LINK ' + value[i].LinkID + ' ' + \
                                   str(value[i].Setting) + \
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

        # Retrieves the comment string assigned to all the curves
        >>> d.getCurveComment()

        Example 2:

        # Retrieves the comment string assigned to the 1st curve
        >>> d.getCurveComment(1)

        Example 3:

        # Retrieves the comment string assigned to the first 2 curves
        >>> d.getCurveComment([1,2])

        See also getCurveNameID, getCurveType, getCurvesInfo
        """
        if len(argv) == 0:
            value = []
            for i in range(1, self.getCurveCount() + 1):
                value.append(self.api.ENgetcomment(
                    self.ToolkitConstants.EN_CURVE,
                    i)
                )
        elif isList(argv[0]):
            value = []
            for i in argv[0]:
                value.append(self.api.ENgetcomment(
                    self.ToolkitConstants.EN_CURVE,
                    i)
                )
        else:
            value = self.api.ENgetcomment(
                self.ToolkitConstants.EN_CURVE,
                argv[0]
            )
        return value

    def getCounts(self):
        """ Retrieves the number of network components.
        Nodes, Links, Junctions, Reservoirs, Tanks, Pipes, Pumps,
        Valves, Curves, SimpleControls, RuleBasedControls, Patterns.

        Example:

        # Retrieves the number of all network components
        >>> counts = d.getCounts().to_dict()
        # Retrieves the number of nodes
        >>> d.getCounts().Nodes
        # Retrieves the number of simple controls
        >>> d.getCounts().SimpleControls

        See also getNodeCount, getNodeJunctionCount, getLinkCount,
        getControlRulesCount.
        """
        value = EpytValues()
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
        """ Retrieves the index of a curve with specific ID.

        Example 1:

        # Retrieves the indices of all the curves
        >>> d.getCurveIndex()

        Example 2:

        # Retrieves the index of the 1st curve given it's ID
        >>> curveID = d.getCurveNameID(1)
        >>> d.getCurveIndex(curveID)

        Example 3:

        # Retrieves the indices of the first 2 curves given their ID
        >>> curveID = d.getCurveNameID([1,2])
        >>> d.getCurveIndex(curveID)

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
        """ Retrieves number of points in a curve.

        The examples are based on: d = epanet('Richmond_standard.inp')

        Example:

        # Retrieves the number of points in all the curves
        >>> d.getCurveLengths()
        # Retrieves the number of points in the 1st curve
        >>> d.getCurveLengths(1)
        # Retrieves the number of points in the first 2 curves
        >>> d.getCurveLengths([1,2])
        # Retrieves the number of points for curve with id = '1'
        >>> d.getCurveLengths('1006')

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
                    value.append(
                        self.api.ENgetcurvelen(
                            self.getCurveIndex(curves[i])
                        )
                    )
            else:
                for i in range(1, len(curves) + 1):
                    value.append(self.api.ENgetcurvelen(i))
        return value

    def getCurveNameID(self, *argv):
        """Retrieves the IDs of curves.

        Example:

        # Retrieves the IDs of all the curves
        >>> d.getCurveNameID()
        # Retrieves the ID of the 1st curve
        >>> d.getCurveNameID(1)
        # Retrieves the IDs of the first 2 curves
        >>> d.getCurveNameID([1,2])

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
        Retrieves all the info of curves.

        Returns the following informations:
          1) Curve Name ID
          2) Number of points on curve
          3) X values of points
          4) Y values of points

        Example:

        >>> d.getCurvesInfo().disp()
        # Retrieves the IDs of curves
        >>> d.getCurvesInfo().CurveNameID
        # Retrieves the number of points on curv
        # # Retrieves the number of points on curvee
        >>> d.getCurvesInfo().CurveNvalue
        # Retrieves the X values of points of all curves
        >>> d.getCurvesInfo().CurveXvalue
        # Retrieves the X values of points of the 1st curve
        >>> d.getCurvesInfo().CurveXvalue[0]
        # Retrieves the Y values of points of all curves
        >>> d.getCurvesInfo().CurveYvalue
        # Retrieves the Y values of points of the 1st curve
        >>> d.getCurvesInfo().CurveYvalue[0]

        See also setCurve, getCurveType, getCurveLengths, getCurveValue,
        getCurveNameID, getCurveComment.
        """
        value = EpytValues()
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

        # Retrieves the curve-type for all curves
        >>> d.getCurveType()
        # Retrieves the curve-type for the 1st curve
        >>> d.getCurveType(1)
        # Retrieves the curve-type for the first 2 curves
        >>> d.getCurveType([1,2])

        See also getCurveTypeIndex, getCurvesInfo.
        """
        indices = self.__getCurveIndices(*argv)
        return [self.TYPECURVE[self.getCurveTypeIndex(i)] for i in indices] \
            if isList(indices) \
            else self.TYPECURVE[self.getCurveTypeIndex(indices)]

    def getCurveTypeIndex(self, *argv):
        """ Retrieves the curve-type index for all curves.

        Example:

        # Retrieves the curve-type index for all curves
        >>> d.getCurveTypeIndex()
        # Retrieves the curve-type index for the 1st curve
        >>> d.getCurveTypeIndex(1)
        # Retrieves the curve-type index for the first 2 curves
        >>> d.getCurveTypeIndex([1,2])

        See also getCurveType, getCurvesInfo.
        """
        indices = self.__getCurveIndices(*argv)
        return [self.api.ENgetcurvetype(i) for i in indices] \
            if isList(indices) else self.api.ENgetcurvetype(indices)

    def getCurveValue(self, *argv):
        """ Retrieves the X, Y values of points of curves.

        Example:

        # Retrieves all the X and Y values of all curves
        >>> d.getCurveValue()
        >>> curveIndex = 1
        # Retrieves all the X and Y values of the 1st curve
        >>> d.getCurveValue(curveIndex)
        >>> pointIndex = 1
        # Retrieves the X and Y values of the 1st point of the 1st curve
        >>> d.getCurveValue(curveIndex, pointIndex)

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

        Demand model code DDA - 0, PDA - 1
        Pmin - Pressure below
        Preq - Pressure required to deliver full demand.
        Pexp - Pressure exponent in demand function

        Example:

        >>> model = d.getDemandModel()

        See also setDemandModel, getNodeBaseDemands,
        getNodeDemandCategoriesNumber, getNodeDemandPatternIndex,
        getNodeDemandPatternNameID.
        """
        value = EpytValues()
        [value.DemandModelCode, value.DemandModelPmin, value.DemandModelPreq,
         value.DemandModelPexp] = self.api.ENgetdemandmodel()
        value.DemandModelType = self.DEMANDMODEL[value.DemandModelCode]
        return value

    def getError(self, Errcode):
        """ Retrieves the text of the message associated with a particular
        error or warning code.

        Example:

        >>> error = 250
        >>> d.getError(error)
        """
        errmssg = create_string_buffer(150)
        self.api._lib.ENgeterror(Errcode, byref(errmssg), 150)
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

        # Retrieves the comments of all links
        >>> d.getLinkComment()

        Example 2:

        >>> linkIndex = 1
        # Retrieves the comment of the 1st link
        >>> d.getLinkComment(linkIndex)

        Example 3:

        >>> linkIndex = [1,2,3,4,5]
        # Retrieves the comments of the first 5 links
        >>> d.getLinkComment(linkIndex)

        See also setLinkComment, getLinkNameID, getLinksInfo.
        """
        value = []
        indices = self.__getLinkIndices(*argv)
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

        # Retrieves the value of all link quality
        >>> d.getLinkQuality()

        Example 2:

        # Retrieves the value of the first link quality
        >>> d.getLinkQuality(1)

        See also getLinkType, getLinksInfo, getLinkDiameter,
        getLinkRoughnessCoeff, getLinkMinorLossCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_QUALITY, *argv)

    def getLinkType(self, *argv):
        """ Retrieves the link-type code for all links.

        Example 1:

        # Retrieves the link-type code for all links
        >>> d.getLinkType()

        Example 2:

        # Retrieves the link-type code for the first link
        >>> d.getLinkType(1)

        See also getLinkTypeIndex, getLinksInfo, getLinkDiameter,
        getLinkLength, getLinkRoughnessCoeff, getLinkMinorLossCoeff.
        """
        lTypes = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, list):
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

        # Retrieves the link-type code for all links
        >>> d.getLinkTypeIndex()
        # Retrieves the link-type code for the first link
        >>> d.getLinkTypeIndex(1)
        # Retrieves the link-type code for the second and third links
        >>> d.getLinkTypeIndex([2,3])

        See also getLinkType, getLinksInfo, getLinkDiameter,
        getLinkLength, getLinkRoughnessCoeff, getLinkMinorLossCoeff.
        """
        lTypes = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, list):
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

        # Retrieves the value of all link diameters
        >>> d.getLinkDiameter()
        # Retrieves the value of the first link diameter
        >>> d.getLinkDiameter(1)
        # Retrieves the value of the second and third link diameter
        >>> d.getLinkDiameter([1,2])

        See also getLinkType, getLinksInfo, getLinkLength,
        getLinkRoughnessCoeff, getLinkMinorLossCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_DIAMETER, *argv)

    def getLinkLength(self, *argv):
        """ Retrieves the value of link lengths.
        Pipe length

        Example:

        # Retrieves the value of all link lengths
        >>> d.getLinkLength()
        # Retrieves the value of the first link length
        >>> d.getLinkLength(1)

        See also getLinkType, getLinksInfo, getLinkDiameter,
        getLinkRoughnessCoeff, getLinkMinorLossCoeff.ughnessCoeff,
        getLinkMinorLossCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_LENGTH, *argv)

    def getLinkRoughnessCoeff(self, *argv):
        """ Retrieves the value of link roughness coefficient.
        Pipe roughness coefficient

        Example:

        # Retrieves the value of all link roughness coefficients
        >>> d.getLinkRoughnessCoeff()
        # Retrieves the value of the first link roughness coefficient
        >>> d.getLinkRoughnessCoeff(1)

        See also getLinkType, getLinksInfo, getLinkDiameter,
        getLinkLength, getLinkMinorLossCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_ROUGHNESS, *argv)

    def getLinkMinorLossCoeff(self, *argv):
        """ Retrieves the value of link minor loss coefficients.
        Pipe/valve minor loss coefficient

        Example:

        # Retrieves the value of all link minor loss coefficients
        >>> d.getLinkMinorLossCoeff()
        # Retrieves the value of the first link minor loss coefficient
        >>> d.getLinkMinorLossCoeff(1)

        See also getLinkType, getLinksInfo, getLinkDiameter,
        getLinkLength, getLinkRoughnessCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_MINORLOSS, *argv)

    def getLinkNameID(self, *argv):
        """ Retrieves the ID label(s) of all links, or the IDs of
        an index set of links.

        Example 1:

        # Retrieves the ID's of all links
        >>> d.getLinkNameID()

        Example 2:

        >>> linkIndex = 1
        # Retrieves the ID of the link with index = 1
        >>> d.getLinkNameID(linkIndex)

        Example 3:

        >>> linkIndices = [1,2,3]
        # Retrieves the IDs of the links with indices = 1, 2, 3
        >>> d.getLinkNameID(linkIndices)

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

        # Retrieves the value of all link initial status
        >>> d.getLinkInitialStatus()
        # Retrieves the value of the first link initial status
        >>> d.getLinkInitialStatus(1)

        See also getLinkType, getLinksInfo, getLinkInitialSetting,
        getLinkBulkReactionCoeff, getLinkWallReactionCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_INITSTATUS, *argv)

    def getLinkInitialSetting(self, *argv):
        """ Retrieves the value of all link roughness for pipes or initial
        speed for pumps or initial setting for valves.

        Example:

        # Retrieves the value of all link initial settings
        >>> d.getLinkInitialSetting()
        # Retrieves the value of the first link initial setting
        >>> d.getLinkInitialSetting(1)

        See also getLinkType, getLinksInfo, getLinkInitialStatus,
        getLinkBulkReactionCoeff, getLinkWallReactionCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_INITSETTING, *argv)

    def getLinkBulkReactionCoeff(self, *argv):
        """ Retrieves the value of all link bulk chemical reaction coefficient.

        Example:

        >>> d.getLinkBulkReactionCoeff() # Retrieves the value of all link bulk chemical reaction coefficient
        # Retrieves the value of the first link bulk chemical reaction coefficient
        >>> d.getLinkBulkReactionCoeff(1)

        See also getLinkType, getLinksInfo, getLinkRoughnessCoeff,
        getLinkMinorLossCoeff, getLinkInitialStatus,
        getLinkInitialSetting, getLinkWallReactionCoeff.
        """
        return self.__getLinkInfo(self.ToolkitConstants.EN_KBULK, *argv)

    def getLinkWallReactionCoeff(self, *argv):
        """ Retrieves the value of all pipe wall chemical reaction coefficient.

        Example:

        >>> d.getLinkWallReactionCoeff()  # Retrieves the value of all pipe wall chemical reaction coefficient
        # Retrieves the value of the first pipe wall chemical reaction coefficient
        >>> d.getLinkWallReactionCoeff(1)

        See also getLinkType, getLinksInfo, getLinkRoughnessCoeff,
        getLinkMinorLossCoeff, getLinkInitialStatus,
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
        return linkTypes.count(self.ToolkitConstants.EN_CVPIPE) + \
            linkTypes.count(self.ToolkitConstants.EN_PIPE)

    def getLinkPumpEfficiency(self, *argv):
        """ Retrieves the current computed pump efficiency (read only).

        Example:

        >>> d.getLinkPumpEfficiency()  # Retrieves the current computed pump efficiency for all links
        # Retrieves the current computed pump efficiency for the first link
        >>> d.getLinkPumpEfficiency(1)

        See also getLinkFlows, getLinkStatus, getLinkPumpState,
        getLinkSettings, getLinkEnergy, getLinkActualQuality.
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
        """ Retrieves the pump average energy price.

        Example 1: Retrieves the average energy price of all pumps

        >>> d.getLinkPumpECost()

        Example 2: Retrieves the average energy price of the 1st pump

        >>> d.getLinkPumpECost(1)

        Example 3:

        >>> d = epanet('Richmond_standard.inp')
        >>> pIndex = 950
        >>> pIndices = d.getLinkPumpIndex()
        # Retrieves the average energy price of the pump with link index 950
        >>> d.getLinkPumpECost(pIndex)

        See also setLinkPumpECost, getLinkPumpPower, getLinkPumpHCurve,
        getLinkPumpEPat, getLinkPumpPatternIndex, getLinkPumpPatternNameID.
        """
        return self.__getPumpLinkInfo(
            self.ToolkitConstants.EN_PUMP_ECOST,
            *argv
        )

    def getLinkPumpECurve(self, *argv):
        """ Retrieves the pump efficiency v. flow curve index.

        Example 1: Retrieves the efficiency v. flow curve index of all pumps

        >>> d.getLinkPumpECurve()

        Example 2: Retrieves the efficiency v. flow curve index of the 1st pump

        >>> d.getLinkPumpECurve(1)

        Example 3: Retrieves the efficiency v. flow curve index of the first 2 pumps

        >>> d.getLinkPumpECurve([1,2])

        Example 4: Retrieves the efficiency v. flow curve index of the pumps with link index 950

        >>> d = epanet('Richmond_standard.inp')
        >>> pIndex = 950
        >>> pIndices = d.getLinkPumpIndex()
        >>> d.getLinkPumpECurve(pIndex)

        See also setLinkPumpECurve, getLinkPumpHCurve, getLinkPumpECost,
        getLinkPumpEPat, getLinkPumpPatternIndex, getLinkPumpPatternNameID.
        """
        value = self.__getPumpLinkInfo(
            self.ToolkitConstants.EN_PUMP_ECURVE,
            *argv
        )
        return self.__returnValue(value)

    def getLinkPumpEPat(self, *argv):
        """ Retrieves the pump energy price time pattern index.

        Example 1: Retrieves the energy price time pattern index of all pumps

        >>> d.getLinkPumpEPat()

        Example 2: Retrieves the energy price time pattern index of the 1st pump

        >>> d.getLinkPumpEPat(1)

        Example 3: Retrieves the energy price time pattern index of the first 2 pumps

        >>> d.getLinkPumpEPat([1,2])

        Example 4: Retrieves the energy price time pattern index of pump with link index 950

        >>> d = epanet('Richmond_standard.inp')
        >>> pIndex = 950
        >>> pIndices = d.getLinkPumpIndex()
        >>> d.getLinkPumpEPat(pIndex)

        See also setLinkPumpEPat, getLinkPumpHCurve, getLinkPumpECurve,
        getLinkPumpECost, getLinkPumpPatternIndex, getLinkPumpPatternNameID.
        """
        value = self.__getPumpLinkInfo(self.ToolkitConstants.EN_PUMP_EPAT, *argv)
        return self.__returnValue(value)

    def getLinkPumpHCurve(self, *argv):
        """ Retrieves the pump head v. flow curve index.

        Example 1: Retrieves the head v. flow curve index of all pumps

        >>> d.getLinkPumpHCurve()

        Example 2: Retrieves the head v. flow curve index of the 1st pump

        >>> d.getLinkPumpHCurve(1)

        Example 3: Retrieves the head v. flow curve index of the first 2 pumps

        >>> d.getLinkPumpHCurve([1,2])

        Example 4: Retrieves the head v. flow curve index of pump with link index 950

        >>> d = epanet('Richmond_standard.inp')
        >>> pIndex = 950
        >>> pIndices = d.getLinkPumpIndex()
        >>> d.getLinkPumpHCurve(pIndex)

        See also setLinkPumpHCurve, getLinkPumpECurve, getLinkPumpECost,
        getLinkPumpEPat, getLinkPumpPatternIndex, getLinkPumpPatternNameID.
        """
        value = self.__getPumpLinkInfo(self.ToolkitConstants.EN_PUMP_HCURVE, *argv)
        return self.__returnValue(value)

    def getLinkPumpHeadCurveIndex(self):
        """ Retrieves the index of a head curve for all pumps.

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
        """ Retrieves the pump speed time pattern index.

        Example 1: Retrieves the speed time pattern index of all pumps

        >>> d.getLinkPumpPatternIndex()

        Example 2: Retrieves the speed time pattern index of the 1st pump

        >>> d.getLinkPumpPatternIndex(1)

        Example 3: Retrieves the speed time pattern index of the first 2 pumps

        >>> d.getLinkPumpPatternIndex([1,2])

        Example 4: Retrieves the speed time pattern index of the pumps given their indices

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.getLinkPumpPatternIndex(pumpIndex)

        See also setLinkPumpPatternIndex, getLinkPumpPower, getLinkPumpHCurve,
        getLinkPumpECost, getLinkPumpEPat,  getLinkPumpPatternNameID.
        """
        value = self.__getPumpLinkInfo(self.ToolkitConstants.EN_LINKPATTERN, *argv)
        return self.__returnValue(value)

    def getLinkPumpPatternNameID(self, *argv):
        """ Retrieves pump pattern name ID.
        A value of 0 means empty


        Example 1: Retrieves the pattern name ID of all pumps

        >>> d = epanet('ky10.inp')
        >>> d.getLinkPumpPatternNameID()

        Example 2: Retrieves the pattern name ID of the 1st pump

        >>> d.getLinkPumpPatternNameID(1)

        Example 3: Retrieves the pattern name ID of the first 2 pumps

        >>> d.getLinkPumpPatternNameID([1,2])

        Example 4: Retrieves the pattern name ID of the pumps given their indices

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.getLinkPumpPatternNameID(pumpIndex)

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
        """ Retrieves the pump constant power rating (read only).

        Example 1: Retrieves the constant power rating of all pumps

        >>> d.getLinkPumpPower()

        Example 2: Retrieves the constant power rating of the 1st pump

        >>> d.getLinkPumpPower(1)

        Example 3: Retrieves the constant power rating of the first 2 pumps

        >>> d.getLinkPumpPower([1,2])

        Example 4: Retrieves the constant power rating of the pumps given their indices

        >>> pumpIndex = d.getLinkPumpIndex()
        >>> d.getLinkPumpPower(pumpIndex)

        See also getLinkPumpHCurve, getLinkPumpECurve, getLinkPumpECost,
        getLinkPumpEPat, getLinkPumpPatternIndex, getLinkPumpPatternNameID.
        """
        return self.__getPumpLinkInfo(self.ToolkitConstants.EN_PUMP_POWER, *argv)

    def getLinkPumpState(self, *argv):
        """ Retrieves the current computed pump state (read only) (see @ref EN_PumpStateType).
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
        """ Retrieves the type of a pump.

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
        """ Retrieves the code of type of a pump.

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
        value = EpytValues()
        value.LinkDiameter = []
        value.LinkLength = []
        value.LinkRoughnessCoeff = []
        value.LinkMinorLossCoeff = []
        value.LinkInitialStatus = []
        value.LinkInitialSetting = []
        value.LinkBulkReactionCoeff = []
        value.LinkWallReactionCoeff = []
        value.LinkTypeIndex = []
        value.NodesConnectingLinksIndex = [[0, 0] for _ in range(self.getLinkCount())]
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
        value.NodesConnectingLinksIndex = np.array(value.NodesConnectingLinksIndex)
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
        """ Retrieves the current computed link quality (read only).

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
            if isinstance(index, list):
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
        indices = self.__getLinkIndices(*argv)
        value: list[list[int]] = []
        for i in indices:
            value.append(self.api.ENgetlinknodes(i))
        if len(argv) == 1 and not isList(argv[0]):
            return np.array(value[0])
        else:
            return np.array(value)

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

    def getNetworksDatabase(self):
        """Return all EPANET Input Files from EPyT database."""
        networksdb = []
        for root, dirs, files in os.walk(epyt_root):
            for name in files:
                if name.lower().endswith(".inp") and '_temp' not in name:
                    networksdb.append(name)
        return networksdb

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
        """ Retrieves the value of all node base demands categorie number.

        Example 1:

       	>>> d.getNodeDemandCategoriesNumber()  # Retrieves the value of all node base demands categorie number

        Example 2:

       	>>> d.getNodeDemandCategoriesNumber(1)  # Retrieves the value of the first node base demand categorie number

        Example 3:

       	>>> d.getNodeDemandCategoriesNumber([1,2,3,4])  # Retrieves the value of the first 4 nodes base demand
       	categorie number

        See also getNodeBaseDemands, getNodeDemandPatternIndex, getNodeDemandPatternNameID.
        """
        value = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, list):
                for i in index:
                    value.append(self.api.ENgetnumdemands(i))
            else:
                value = self.api.ENgetnumdemands(index)
        else:
            for i in range(self.getNodeCount()):
                value.append(self.api.ENgetnumdemands(i + 1))
        return value

    def getNodeDemandDeficit(self, *argv):
        """  Retrieves the amount that full demand is reduced under PDA.

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
        """ Retrieves the value of all node base demands pattern index.

        Example:

        >>> d.getNodeDemandPatternIndex()
        >>> d.getNodeDemandPatternIndex()[1]

        See also getNodeBaseDemands, getNodeDemandCategoriesNumber, getNodeDemandPatternNameID,
        setNodeDemandPatternIndex.
        """
        numdemands = self.getNodeDemandCategoriesNumber()
        value = {}
        val = np.zeros((max(numdemands), self.getNodeCount()), dtype=int)
        v = 0
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

    def getNodeReservoirHeadPatternIndex(self):
        """ Retrieves the value of all reservoir head pattern index.

        Example:
            d = epanet('net2-cl2.inp')
            res_index = d.addNodeReservoir("res-1")
            pidx = d.addPattern("pat-1", [1, 3])
            d.setNodeReservoirHeadPatternIndex(res_index, pidx)
            print(d.getNodeDemandPatternIndex())
            print(d.getNodeReservoirHeadPatternIndex())

        """
        value = []
        for i in self.getNodeReservoirIndex():
            pattern_index = self.api.ENgetnodevalue(i, self.ToolkitConstants.EN_PATTERN)
            value.append(pattern_index)
        return value

    def getNodeDemandPatternNameID(self):
        """ Retrieves the value of all node base demands pattern name ID.

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
            val_tmp = [['' for _ in range(self.getNodeCount())] for _ in range(max(numdemands))]
            for i in indices:
                for u in range(numdemands[i - 1]):
                    if v[u + 1][i - 1] != np.array(0):
                        val_tmp[u][i - 1] = m[v[u + 1][i - 1] - 1]
                    else:
                        val_tmp[u][i - 1] = ''
                if numdemands[i - 1] == 0:
                    val_tmp[0][i - 1] = ''
            for i in range(len(val_tmp)):
                value[i + 1] = list(val_tmp[i])
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
            if isinstance(index, list):
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
        """ Retrieves the demand index of the junctions.

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
        value = []
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
                    value.append(self.api.ENgetdemandindex(nodeIndex, demandNameIn[nodeIndex - 1]))
            else:
                value = [[0 for i in range(len(nodeIndex))] for j in range(len(demandName))]
                for i in range(len(demandName)):
                    demandNameIn = demandName[i + 1]
                    for j in range(len(nodeIndex)):
                        value[i][j] = self.api.ENgetdemandindex(nodeIndex[j], demandNameIn[nodeIndex[j] - 1])
        elif len(argv) == 0:
            demandName = self.getNodeJunctionDemandName()
            indices = self.__getNodeJunctionIndices(*argv)
            value = [[0 for _ in range(len(indices))] for _ in range(len(demandName))]
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
        if not isList(numdemands): numdemands = [numdemands]
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
                if isinstance(index, list):
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
            if temp_val != 240:
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
                if isinstance(index, list):
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
        indices = self.__getLinkIndices(*argv)
        values = self.getLinkNodesIndex(indices)
        conn_vals = []
        for value in values:
            conn_vals.append(self.getNodeNameID(value.tolist()))
        return np.array(conn_vals)

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
        value = EpytValues()
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
            if isinstance(index, list):
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
        were saved to an output file.

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
            if e is not None:
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
                if e is not None:
                    value.append(e)
                else:
                    value.append(0)
            except Exception as Errcode:
                if self.api.errcode == 203:
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
                if e is not None:
                    value.append(self.TYPESOURCE[e])
                else:
                    value.append(0)
            except Exception as Errcode:
                if self.api.errcode == 203:
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
                if e is not None:
                    value.append(e)
                else:
                    value.append(0)
            except Exception as Errcode:
                if self.api.errcode == 203:
                    return self.getError(Errcode)
            j = j + 1

        if len(argv) == 0:
            return np.array(value)
        else:
            return value

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
        """ Retrieves the tank can overflow (= 1) or not (= 0).

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
        """ Retrieves a group of properties for a tank.

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
        tankData = EpytValues()
        tankIndices = self.getNodeTankIndex()

        if len(argv) == 1:
            if isinstance(argv[0], list):
                result = [True for c in argv[0] if c in tankIndices]
                if result:
                    tankIndices = argv[0]
                else:
                    tankIndices = self.getNodeTankIndex(argv[0])
            else:
                tankIndices = argv[0]

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
                if isinstance(index, list):
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
        """ Retrieves the tank maximum water volume.

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
        """ Retrieves the tank volume.

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
            if isinstance(index, list):
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
            if isinstance(index, list):
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
        """ Retrieves the frequency of hydraulic status checks.

        Example:

        >>> d.getOptionsCheckFrequency()

        See also setOptionsCheckFrequency, getOptionsMaxTrials, getOptionsMaximumCheck.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_CHECKFREQ)

    def getOptionsDampLimit(self):
        """ Retrieves the accuracy level where solution damping begins.

        Example:

        >>> d.getOptionsDampLimit()

        See also setOptionsDampLimit, getOptionsMaxTrials, getOptionsCheckFrequency.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_DAMPLIMIT)

    def getOptionsDemandCharge(self):
        """ Retrieves the energy charge per maximum KW usage.

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
        """ Retrieves the extra trials allowed if hydraulics don't converge.

        Example:

        >>> d.getOptionsExtraTrials()

        See also setOptionsExtraTrials, getOptionsMaxTrials, getOptionsMaximumCheck.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_UNBALANCED)

    def getOptionsFlowChange(self):
        """ Retrieves the maximum flow change for hydraulic convergence.

        Example:

        >>> d.getOptionsFlowChange()

        See also setOptionsFlowChange, getOptionsHeadError, getOptionsHeadLossFormula.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_FLOWCHANGE)

    def getOptionsGlobalEffic(self):
        """ Retrieves the global efficiency for pumps(percent).

        Example:

        >>> d.getOptionsGlobalEffic()

        See also setOptionsGlobalEffic, getOptionsGlobalPrice, getOptionsGlobalPattern.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_GLOBALEFFIC)

    def getOptionsGlobalPrice(self):
        """ Retrieves the global average energy price per kW-Hour.

        Example:

        >>> d.getOptionsGlobalPrice()

        See also setOptionsGlobalPrice, getOptionsGlobalEffic, getOptionsGlobalPattern.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_GLOBALPRICE)

    def getOptionsGlobalPattern(self):
        """ Retrieves the index of the global energy price pattern.

        Example:

        >>> d.getOptionsGlobalPattern()

        See also setOptionsGlobalPattern, getOptionsGlobalEffic, getOptionsGlobalPrice.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_GLOBALPATTERN)

    def getOptionsHeadError(self):
        """ Retrieves the maximum head loss error for hydraulic convergence.

        Example:

        >>> d.getOptionsHeadError()

        See also setOptionsHeadError, getOptionsEmitterExponent, getOptionsAccuracyValue.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_HEADERROR)

    def getOptionsHeadLossFormula(self):
        """ Retrieves the headloss formula.

        Example:

        >>> d.getOptionsHeadLossFormula()

        See also setOptionsHeadLossFormula, getOptionsHeadError, getOptionsFlowChange.
        """
        headloss = self.api.ENgetoption(self.ToolkitConstants.EN_HEADLOSSFORM)
        return self.TYPEHEADLOSS[int(headloss)]

    def getOptionsLimitingConcentration(self):
        """ Retrieves the limiting concentration for growth reactions.

        Example:

        >>> d.getOptionsLimitingConcentration()

        See also setOptionsLimitingConcentration, getOptionsPipeBulkReactionOrder, getOptionsPipeWallReactionOrder.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_CONCENLIMIT)

    def getOptionsMaximumCheck(self):
        """ Retrieves the maximum trials for status checking.

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
        """ Retrieves the bulk water reaction order for pipes.

        Example:

        >>> d.getOptionsPipeBulkReactionOrder()

        See also setOptionsPipeBulkReactionOrder, getOptionsPipeWallReactionOrder, getOptionsTankBulkReactionOrder.
        """
        return int(self.api.ENgetoption(self.ToolkitConstants.EN_BULKORDER))

    def getOptionsPipeWallReactionOrder(self):
        """ Retrieves the wall reaction order for pipes (either 0 or 1).

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
        """ Retrieves the specific diffusivity (relative to chlorine at 20 deg C).

        Example:

        >>> d.getOptionsSpecificDiffusivity()

        See also setOptionsSpecificDiffusivity, getOptionsSpecificViscosity, getOptionsSpecificGravity.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_SP_DIFFUS)

    def getOptionsSpecificGravity(self):
        """ Retrieves the specific gravity.

        Example:

        >>> d.getOptionsSpecificGravity()

        See also setOptionsSpecificGravity, getOptionsSpecificViscosity, getOptionsHeadLossFormula.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_SP_GRAVITY)

    def getOptionsSpecificViscosity(self):
        """ Retrieves the specific viscosity.

        Example:

        >>> d.getOptionsSpecificViscosity()

        See also setOptionsSpecificViscosity, getOptionsSpecificGravity, getOptionsHeadLossFormula.
        """
        return self.api.ENgetoption(self.ToolkitConstants.EN_SP_VISCOS)

    def getOptionsTankBulkReactionOrder(self):
        """ Retrieves the bulk water reaction order for tanks.

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
        """ Retrieves the average values of all the time patterns.

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
            if isinstance(index, list):
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
        value = EpytValues()
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
        were saved to an output file.

        Example:

        >>> link_index = 3
        >>> result_index = d.getLinkResultIndex(link_index)

        See also getComputedHydraulicTimeSeries, deleteNode, getNodeResultIndex
        """
        return self.api.ENgetresultindex(self.ToolkitConstants.EN_LINK, link_index)

    def getRuleCount(self):
        """ Retrieves the number of rules.

        Example:

        >>> d.getRuleCount()

        See also getRules, getControlRulesCount.
        """
        return self.api.ENgetcount(self.ToolkitConstants.EN_RULECOUNT)

    def getRuleID(self, *argv):
        """ Retrieves the ID name of a rule-based control given its index.

        # The examples are based on d = epanet('BWSN_Network_1.inp')

        Example:

        >>> d.getRuleID()           # Retrieves the ID name of every rule-based control
        >>> d.getRuleID(1)          # Retrieves the ID name of the 1st rule-based control
        >>> d.getRuleID([1,2,3])    # Retrieves the ID names of the 1st to 3rd rule-based control

        See also getRules, getRuleInfo, addRules.
        """
        index = 0
        if len(argv) == 0:
            index = list(range(1, self.getRuleCount() + 1))
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
        """ Retrieves summary information about a rule-based control given it's index.

        The examples are based on d = epanet('BWSN_Network_1.inp')

        Example:

        >>> RuleInfo = d.getRuleInfo()          # Retrieves summary information about every rule-based control
        >>> d.getRuleInfo(1).to_dict()           # Retrieves summary information about the 1st rule-based control
        >>> d.getRuleInfo([1,2,3]).to_dict()     # Retrieves summary information about the 1st to 3rd rule-based control

        See also getRuleID, getRules, addRules.
        """
        value = EpytValues()
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
        """ Retrieves the rule - based control statements.

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

        objectNameID = ''
        for i in ruleIndex:
            cnt = self.getRuleInfo().Premises[i - 1]
            premises = []
            space = ''
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
                    value_premise = datetime.fromtimestamp(value_premise, tz=timezone.utc).strftime("%I:%M %p")
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
        """ Returns error code.

        Input:  none

        Output:
            * iter:   # of iterations to reach solution
            * relerr: convergence error in solution

        Example:

        >>> d.getStatistic().disp()

        """
        value = EpytValues()
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
        value = EpytValues()
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

    def loadlibrary(self):
        self._lib = cdll.LoadLibrary(self.LibEPANET)

    def loadEPANETFile(self, *argv):
        """ Load epanet file when use bin functions.

        Example:

        >>> d.loadEPANETFile(d.TempInpFile)
        """

        if len(argv) == 1:
            self.api.ENopen(argv[0], argv[0][0:-4] + '.txt', argv[0][0:-4] + '.bin')
        else:
            self.api.ENopen(argv[0], argv[1], argv[2])

    def loadMSXEPANETFile(self, msxfile):
        """ Load EPANET MSX file.

        Example:

        >>> d.loadMSXEPANETFile(d.MSXTempFile)
        """
        self.errcode = self.msx.msx_lib.MSXopen(c_char_p(msxfile.encode('utf-8')))
        return self.errcode

    def max(self, value):
        """ Retrieves the smax value of numpy.array or numpy.mat """
        return np.max(value)

    def multiply_elements(self, arr1, arr2):
        """ Multiply elementwise two numpy.array or numpy.mat variables """
        return np.multiply(arr1, arr2)

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
        plat = platform.system().lower()
        if len(argv) == 1:
            arg = argv[0]
        if plat in ['windows']:
            try:
                subprocess.call(['Spyder.exe', arg])
            except:
                subprocess.call(['notepad.exe', arg])
        elif plat in ['darwin']:
            try:
                subprocess.call(['spyder', arg])
            except:
                subprocess.call(['open', '-e', arg])
        else:
            try:
                subprocess.call(['spyder', arg])
            except:
                try:
                    subprocess.call(['spyder3', arg])
                except:  # i aint touching this one
                    subprocess.call(['vi', arg])
                    subprocess.call(['emacs', arg])

    def openCurrentInp(self, *argv):
        """ Opens EPANET input file who is loaded

        Example:

        >>> d.openCurrentInp()
        """
        plat = platform.system().lower()
        if plat in ['windows']:
            try:
                subprocess.call(['Spyder.exe', self.TempInpFile])
            except:
                subprocess.call(['notepad.exe', self.TempInpFile])
        elif plat in ['darwin']:
            try:
                subprocess.call(['spyder', self.TempInpFile])
            except:
                subprocess.call(['open', '-e', self.TempInpFile])
        else:
            try:
                subprocess.call(['spyder', self.TempInpFile])
            except:
                try:
                    subprocess.call(['spyder3', self.TempInpFile])
                except:
                    subprocess.call(['vi', self.TempInpFile])
                    subprocess.call(['emacs', self.TempInpFile])

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
            if self.getCMDCODE():
                subprocess.run(r, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            else:
                subprocess.run(r)
        except Exception as e:
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
        inpname = ''
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
        """ Sets x, y values for a specific curve.

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
            cIndices = list(range(1, self.getCurveCount() + 1))
        else:
            cIndices = argv[0]
        self.__addComment(self.ToolkitConstants.EN_CURVE, value, cIndices)

    def setCurveNameID(self, index, Id):
        """ Sets the name ID of a curve given it's index and the new ID.

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
        """ Sets x, y point for a specific point number and curve.

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
        """ Sets the type of demand model to use and its parameters.

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
            lIndices = list(range(1, self.getLinkCount() + 1))
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
            indices = self.__getLinkIndices()
        if isList(indices):
            for i in value:
                self.api.ENsetlinkid(indices[value.index(i)], i)
        else:
            self.api.ENsetlinkid(indices, value)

    def setLinkNodesIndex(self, linkIndex, startNode, endNode):
        """ Sets the indexes of a link's start- and end-nodes.

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
        """ Sets a group of properties for a pipe.

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
        """ Sets the pump average energy price.

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
        """ Sets the pump efficiency v. flow curve index.

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
        """ Sets the pump energy price time pattern index.

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
        """ Sets the pump head v. flow curve index.

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
            indices = self.__getLinkIndices(*argv)
        if isList(indices):
            j = 0
            for i in indices:
                self.api.ENsetheadcurveindex(i, value[j])
                j += 1
        else:
            self.api.ENsetheadcurveindex(indices, value)

    def setLinkPumpPatternIndex(self, value, *argv):
        """ Sets the pump speed time pattern index.

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
        """ Sets the power for pumps.

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
            if len(indices) == 1:
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

    def setNodeReservoirHeadPatternIndex(self, value, *argv):
        """ Sets the pattern index for a reservoir node head
        This is a duplicate function—identical in behavior to setNodeDemandPatternIndex

        Example 1:
            d = epanet('net2-cl2.inp')
            res_index = d.addNodeReservoir("res-1")
            pidx = d.addPattern("pat-1")
            d.setNodeReservoirHeadPatternIndex(res_index, pidx)
            d.setPattern(pidx, 1)
         """
        if value in self.getNodeReservoirIndex():
            self.__setNodeDemandPattern('ENsetdemandpattern', self.ToolkitConstants.EN_PATTERN, value, *argv)
        else:
            warnings.warn("Invalid reservoir index. For non-reservoir nodes, please use the setNodeDemandPatternIndex function.")

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
        """ Sets a group of properties for a junction node.

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
        """ Assigns a name to a node's demand category.

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
        """ Sets the IDs of a link's start- and end-nodes.

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
        """ Sets the tank can-overflow (= 1) or not (= 0).

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
        """ Sets a group of properties for a tank.

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
        _type = []
        if len(argv) == 0:
            _type = value
        elif len(argv) == 1:
            _type = argv[0]
        if isinstance(_type, list):
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
        """ Sets the frequency of hydraulic status checks.

        Example:

        >>> d.setOptionsCheckFrequency(2)
        >>> d.getOptionsCheckFrequency()

        See also getOptionsCheckFrequency, setOptionsMaxTrials, setOptionsMaximumCheck.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_CHECKFREQ, value)

    def setOptionsDampLimit(self, value):
        """ Sets the accuracy level where solution damping begins.

        Example:

        >>> d.setOptionsDampLimit(0)
        >>> d.getOptionsDampLimit()

        See also getOptionsDampLimit, setOptionsMaxTrials, setOptionsCheckFrequency.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_DAMPLIMIT, value)

    def setOptionsDemandCharge(self, value):
        """ Sets the energy charge per maximum KW usage.

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
        """ Sets the extra trials allowed if hydraulics don't converge.

        Example:

        >>> d.setOptionsExtraTrials(10)
        >>> d.getOptionsExtraTrials()
        >>> # Set UNBALANCED to STOP
        >>> d.setOptionsExtraTrials(-1)

        See also getOptionsExtraTrials, setOptionsMaxTrials, setOptionsMaximumCheck.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_UNBALANCED, value)

    def setOptionsFlowChange(self, value):
        """ Sets the maximum flow change for hydraulic convergence.

        Example:

        >>> d.setOptionsFlowChange(0)
        >>> d.getOptionsFlowChange()

        See also getOptionsFlowChange, setOptionsHeadError, setOptionsHeadLossFormula.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_FLOWCHANGE, value)

    def setOptionsGlobalEffic(self, value):
        """ Sets the global efficiency for pumps(percent).

        Example:

        >>> d.setOptionsGlobalEffic(75)
        >>> d.getOptionsGlobalEffic()

        See also getOptionsGlobalEffic, setOptionsGlobalPrice, setOptionsGlobalPattern.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_GLOBALEFFIC, value)

    def setOptionsGlobalPrice(self, value):
        """ Sets the global average energy price per kW-Hour.

        Example:

        >>> d.setOptionsGlobalPrice(0)
        >>> d.getOptionsGlobalPrice()

        See also getOptionsGlobalPrice, setOptionsGlobalEffic, setOptionsGlobalPattern.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_GLOBALPRICE, value)

    def setOptionsGlobalPattern(self, value):
        """ Sets the global energy price pattern.

        Example:

        >>> d.setOptionsGlobalPattern(1)
        >>> d.getOptionsGlobalPattern()

        See also getOptionsGlobalPattern, setOptionsGlobalEffic, setOptionsGlobalPrice.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_GLOBALPATTERN, value)

    def setOptionsHeadError(self, value):
        """ Sets the maximum head loss error for hydraulic convergence.

        Example:

        >>> d.setOptionsHeadError(0)
        >>> d.getOptionsHeadError()

        See also getOptionsHeadError, setOptionsEmitterExponent, setOptionsAccuracyValue.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_HEADERROR, value)

    def setOptionsHeadLossFormula(self, value):
        """ Sets the headloss formula.
        'HW' = 0, 'DW' = 1, 'CM' = 2

        Example:

        >>> d.setOptionsHeadLossFormula('HW')    # Sets the 'HW' headloss formula
        >>> d.getOptionsHeadLossFormula()

        See also getOptionsHeadLossFormula, setOptionsHeadError, setOptionsFlowChange.
        """
        codevalue = 0
        if value == 'HW':
            codevalue = 0
        elif value == 'DW':
            codevalue = 1
        elif value == 'CM':
            codevalue = 2
        return self.api.ENsetoption(self.ToolkitConstants.EN_HEADLOSSFORM, codevalue)

    def setOptionsLimitingConcentration(self, value):
        """ Sets the limiting concentration for growth reactions.

        Example:

        >>> d.setOptionsLimitingConcentration(0)
        >>> d.getOptionsLimitingConcentration()

        See also getOptionsLimitingConcentration, setOptionsPipeBulkReactionOrder, setOptionsPipeWal
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_CONCENLIMIT, value)

    def setOptionsMaximumCheck(self, value):
        """ Sets the maximum trials for status checking.

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
        """ Sets the bulk water reaction order for pipes.

        Example:

        >>> d.setOptionsPipeBulkReactionOrder(1)
        >>> d.getOptionsPipeBulkReactionOrder()

        See also getOptionsPipeBulkReactionOrder, setOptionsPipeWallReactionOrder, setOptionsTankBulkReactionOrder.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_BULKORDER, value)

    def setOptionsPipeWallReactionOrder(self, value):
        """ Sets the wall reaction order for pipes (either 0 or 1).

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
        """ Sets the specific diffusivity (relative to chlorine at 20 deg C).

        Example:

        >>> d.setOptionsSpecificDiffusivity(1)
        >>> d.getOptionsSpecificDiffusivity()

        See also getOptionsSpecificDiffusivity, setOptionsSpecificViscosity, setOptionsSpecificGravity.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_SP_DIFFUS, value)

    def setOptionsSpecificGravity(self, value):
        """ Sets the specific gravity.

        Example:

        >>> d.setOptionsSpecificGravity(1)
        >>> d.getOptionsSpecificGravity()

        See also getOptionsSpecificGravity, setOptionsSpecificViscosity, setOptionsHeadLossFormula.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_SP_GRAVITY, value)

    def setOptionsSpecificViscosity(self, value):
        """ Sets the specific viscosity.

        Example:

        >>> d.setOptionsSpecificViscosity(1)
        >>> d.getOptionsSpecificViscosity()

        See also getOptionsSpecificViscosity, setOptionsSpecificGravity, setOptionsHeadLossFormula.
        """
        return self.api.ENsetoption(self.ToolkitConstants.EN_SP_VISCOS, value)

    def setOptionsTankBulkReactionOrder(self, value):
        """ Sets the bulk water reaction order for tanks.

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
        if isinstance(patternVector, int):
            nfactors = 1
            patternVector = [patternVector]
        else:
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
            patIndices = list(range(1, self.getPatternCount() + 1))
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
        """ Sets the name ID of a time pattern given it's index and the new ID.

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
        """ Sets the premise of a rule - based control.

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
        objIndex = 0
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
            try:
                value = float(premise_new[m])
            except:
                time_str = premise_new[m]
                hours, minutes = map(int, time_str.split(':'))
                value = hours + minutes / 60
            status = 0
        if object_ == self.ToolkitConstants.EN_R_SYSTEM:
            if premise_new[5] == 'AM':
                value = value * 3600
            elif premise_new[5] == 'PM':
                value = value * 3600 + 43200
        self.api.ENsetpremise(ruleIndex, premiseIndex, logop, object_, objIndex, variable, relop, status, value)

    def setRulePremiseObjectNameID(self, ruleIndex, premiseIndex, objNameID):
        """ Sets the ID of an object in a premise of a rule-based control.

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
        """ Sets the value being compared to in a premise of a rule-based control.

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
        """ Sets a rule - based control.

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
        """ Sets rule - based control else actions.

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
        status = ''
        setting = -1
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
        """ Sets the status being compared to in a premise of a rule-based control.

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
        status_code = 0
        if status == 'OPEN':
            status_code = self.ToolkitConstants.EN_R_IS_OPEN
        elif status == 'CLOSED':
            status_code = self.ToolkitConstants.EN_R_IS_CLOSED
        elif status == 'ACTIVE':
            status_code = self.ToolkitConstants.EN_R_IS_ACTIVE
        self.api.ENsetpremisestatus(ruleIndex, premiseIndex, status_code)

    def setRulePriority(self, ruleIndex, priority):
        """ Sets rule - based control priority.

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
        """ Sets rule - based control then actions.

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
        status = ''
        setting = -1
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
        """ Sets the title lines of the project.

        Example:

        >>> line_1 = 'This is a title'
        >>> line_2 = 'This is a test line 2'
        >>> line_3 = 'This is a test line 3'
        >>> d.setTitle(line_1, line_2, line_3)
        >>> [Line1, Line2, Line3] = d.getTitle()

        See also getTitle, setLinkComment, setNodeComment.
        """
        line1 = ''
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
        if self.getQualityCode() > 0:
            midInitQual = (self.getNodeInitialQuality(leftNodeIndex) + self.getNodeInitialQuality(rightNodeIndex)) / 2
            self.setNodeInitialQuality(newNodeIndex, midInitQual)
            self.setNodeSourceQuality(newNodeIndex, self.getNodeSourceQuality(leftNodeIndex)[0])
            self.setNodeSourcePatternIndex(newNodeIndex, self.getNodeSourcePatternIndex(leftNodeIndex))
            if self.getNodeSourceTypeIndex(leftNodeIndex)[0] != 0:
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
        self.setLinkInitialStatus(leftPipeIndex, linkInitialStatus)
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
             highlightnode=None, legend=True, fontsize=5, figure=True, fig_size=[3, 2], dpi=300,
             node_values=None, node_text=False, link_values=None, link_text=False, colorbar='turbo',
             min_colorbar=None, max_colorbar=None, colors=None, colorbar_label=None, highligthlink_linewidth=1,
             highligthnode_linewidth=3.5, *argv):
        """ Plot Network, show all components, plot pressure/flow/elevation/waterage/anyvalue

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
        >>> d.plot(node_values = P[hr])
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
        valves_ID = []
        junc_ID = []
        res_ID = []
        tank_ID = []
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

        if node_values is not None:
            plot_nodes = False
            legend = False
            fix_colorbar = True
            if colorbar_label is None:
                colorbar_label = ' '
            if colors is None:
                if min_colorbar is None:
                    min_colorbar = np.min(node_values)
                if max_colorbar is None:
                    max_colorbar = np.max(node_values)
            node_values = np.squeeze(np.asarray(node_values))
            if node_text is True:
                plot_nodes = True
        if link_values is not None:
            fix_colorbar = True
            if colorbar_label is None:
                colorbar_label = ' '
            legend = False
            link_values = np.squeeze(np.asarray(link_values))
            if colors is None:
                if min_colorbar is None:
                    min_colorbar = np.min(link_values)
                if max_colorbar is None:
                    max_colorbar = np.max(link_values)
                link_values_t = [(i - min_colorbar) / (max_colorbar - min_colorbar) for i in link_values]
                colors = eval(f"cm.{colorbar}(link_values_t)")

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
        linkvertices = self.getLinkVerticesCount()

        # Create figure
        plt.rcParams["figure.figsize"] = fig_size
        plt.rcParams['figure.dpi'] = dpi
        if figure:
            figure = plt.figure()
        plt.axis('off')

        # Plot Links
        xV = 0
        yV = 0
        if plot_links:
            lindex = [0]
            if highlightlink is not None:
                lindex = self.__getLinkIndices(highlightlink)
                lNodesInd = self.getLinkNodesIndex(lindex)
            x, y = [0, 0], [0, 0]
            for i in links_ind:
                fromNode = nodeconlinkIndex[i - 1][0]
                toNode = nodeconlinkIndex[i - 1][1]
                x[0] = nodecoords['x'][fromNode]
                y[0] = nodecoords['y'][fromNode]
                x[1] = nodecoords['x'][toNode]
                y[1] = nodecoords['y'][toNode]
                if not nodecoords['x_vert'][i]:  # Check if not vertices
                    if fix_colorbar and link_values is not None:
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
                    if link_text:
                        plt.text((x[0] + x[1]) / 2, (y[0] + y[1]) / 2, "{:.2f}".format(link_values[i - 1]),
                                 {'fontsize': fontsize})

                    if i in lindex:
                        plt.plot(x, y, 'r-', linewidth=highligthlink_linewidth, zorder=0)

                else:
                    xV_old = x[0]
                    yV_old = y[0]

                    for j in range(len(nodecoords['x_vert'][i])):
                        xV = nodecoords['x_vert'][i][j]
                        yV = nodecoords['y_vert'][i][j]
                        if i in lindex:
                            plt.plot([xV_old, xV], [yV_old, yV], 'r-', linewidth=highligthlink_linewidth, zorder=0)
                        else:
                            if fix_colorbar and link_values is not None:
                                plt.plot([xV_old, xV], [yV_old, yV], '-', linewidth=1, zorder=0, color=colors[i])
                            else:
                                plt.plot([xV_old, xV], [yV_old, yV], color='steelblue', linewidth=0.2, zorder=0)
                        xV_old = xV
                        yV_old = yV

                    if fix_colorbar and link_values is not None:
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
                    if link_text:
                        plt.text(
                            nodecoords['x_vert'][i][int(len(nodecoords['x_vert'][i]) / 2)],
                            nodecoords['y_vert'][i][int(len(nodecoords['x_vert'][i]) / 2)],
                            "{:.2f}".format(link_values[i - 1]), {'fontsize': fontsize})
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
                    if not nodecoords['x_vert'][i]:  # Check if not vertices
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
                        xx = xVert[math.floor(xVert.index(xVert[-1]) / 2)]
                        yy = yVert[math.floor(yVert.index(yVert[-1]) / 2)]
                    if i != valveindex[-1]:
                        plt.plot(xx, yy, 'k*', markersize=1.5)
                    else:
                        plt.plot(xx, yy, 'k*', markersize=1.5, label='Valves')
                    if text_nodes_ID or (text_nodes_ID_spec and valves_ID[valveindex.index(i)] in nodes_to_show_ID):
                        plt.text(xx, yy, valves_ID[valveindex.index(i)], {'fontsize': fontsize})
                    elif text_nodes_ind or (text_nodes_ind_spec and i in nodes_to_show_ind):
                        plt.text(xx, yy, i, {'fontsize': fontsize})
                    if node_text:
                        plt.text(xx, yy, "{:.2f}".format(node_values[i - 1]), {'fontsize': fontsize})

        if plot_nodes:
            highlight_nodeIndices = [0]
            if highlightnode is not None:
                highlight_nodeIndices = self.__getNodeIndices(highlightnode)

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
                if node_text:
                    plt.text(x, y, "{:.2f}".format(node_values[i - 1]), {'fontsize': fontsize})
                if i in highlight_nodeIndices:
                    plt.plot(nodecoords['x'][i], nodecoords['y'][i], '.r', markersize=highligthnode_linewidth)

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
                if node_text:
                    plt.text(x, y, "{:.2f}".format(node_values[i - 1]), {'fontsize': fontsize})
                if i in highlight_nodeIndices:
                    plt.plot(nodecoords['x'][i], nodecoords['y'][i], '.r', markersize=highligthnode_linewidth)

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
                if node_text:
                    plt.text(x, y, "{:.2f}".format(node_values[i - 1]), {'fontsize': fontsize})

                if i in highlight_nodeIndices:
                    plt.plot(nodecoords['x'][i], nodecoords['y'][i], '.r', markersize=highligthnode_linewidth)

        if node_values is not None:
            # Plot node values
            x = list(nodecoords['x'].values())
            y = list(nodecoords['y'].values())
            plt.scatter(x, y, c=node_values, cmap=colorbar, s=3.5, zorder=2)

        if fix_colorbar and link_values is not None or node_values is not None:
            scal = cm.ScalarMappable(norm=mpl.colors.Normalize(min_colorbar, max_colorbar), cmap=colorbar)
            bar = plt.colorbar(scal, ax=plt.gca(), orientation='horizontal', shrink=0.7, pad=0.05)
            bar.ax.tick_params(labelsize=fontsize)
            bar.outline.set_visible(False)
            bar.set_label(label=colorbar_label, size=fontsize)

        if legend:
            leg = plt.legend(loc=0, fontsize=fontsize, markerscale=1)
            frame = leg.get_frame()
            # frame.set_edgecolor('black')
            frame.set_linewidth(0.3)

        if title is not None:
            plt.title(title, fontsize=fontsize, fontweight="bold")
        if figure:
            plt.show()  # (block=False)

        return figure

    def plot_save(self, name, dpi=300):
        """ Save plot
        """
        plt.savefig(name, dpi=dpi)

    def plot_close(self):
        """ Close all open figures
        """
        plt.close("all")

    def plot_show(self):
        """ Show plot
        """
        plt.show()

    def plot_ts(self, X=None, Y=None, title='', xlabel='', ylabel='', color=None, marker='x',
                figure_size=[3, 2.5], constrained_layout=True, fontweight='normal', fontsize_title=8, fontsize=8,
                labels=None, save_fig=False, filename='temp', tight_layout=False, dpi=300, filetype='png',
                legend_location='best'):
        """ Plot X Y data
        """
        num_points = np.atleast_2d(Y).shape[1]
        try:
            values = Y[:, 1]
        except:
            num_points = 1

        plt.rc('xtick', labelsize=fontsize)
        plt.rc('ytick', labelsize=fontsize)
        fig = plt.figure(figsize=figure_size, constrained_layout=constrained_layout)
        for i in range(num_points):
            if color is None:
                color_user = (random.uniform(0, 1), random.uniform(0, 1),
                              random.uniform(0, 1))
            else:
                color_user = color[i]

            try:
                values = Y[:, i]
            except:
                values = Y

            if labels is not None:
                label = labels[i]
            else:
                label = None

            if marker:
                if X is None:
                    plt.plot(values, color=color_user, marker=marker, label=label)
                else:
                    plt.plot(X, values, color=color_user, marker=marker, label=label)
            else:
                if X is None:
                    plt.plot(values, color=color_user, linewidth=1, label=label)
                else:
                    plt.plot(X, values, color=color_user, linewidth=1, label=label)
        plt.xlabel(xlabel, fontsize=fontsize)
        plt.ylabel(ylabel, fontsize=fontsize)
        plt.title(title, fontsize=fontsize_title, fontweight=fontweight)
        if tight_layout:
            plt.tight_layout()
        if labels is not None:
            plt.legend(loc=legend_location, fontsize=fontsize, markerscale=1)
        plt.show(block=False)

        if save_fig:
            fig.savefig(f'{filename}.png', dpi=dpi, format=filetype, bbox_inches="tight")

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
        try:
            if self.api._ph is not None:
                self.api.ENdeleteproject()
            else:
                self.api.ENclose()
        finally:
            try:
                safe_delete(self.TempInpFile)

                files_to_delete = [self.TempInpFile[0:-4] + '.txt', self.InputFile[0:-4] + '.txt', self.BinTempfile]
                for file in files_to_delete:
                    safe_delete(file)
                for file in Path(".").glob("@#*.txt"):
                    safe_delete(file)

                arch = sys.platform
                if arch == 'win64' or arch == 'win32':
                    cwd = os.getcwd()
                    files = os.listdir(cwd)
                    tmp_files = [
                        f for f in files
                        if os.path.isfile(os.path.join(cwd, f)) and
                           (f.startswith('s') or f.startswith('en')) and
                           5 <= len(f) <= 8 and
                           "." not in f
                    ]
                    tmp_files_paths = [os.path.join(cwd, f) for f in tmp_files]
                    safe_delete(tmp_files_paths)
            except:
                pass
        if self.display_msg:
            print(f'Close toolkit for the input file "{self.netName[0:-4]}". EPANET Toolkit is '
                  f'unloaded.\n')

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
        old_index = self.getNodeIndex(Id)
        node_coords = self.getNodeCoordinates(old_index)
        vert_coords = self.getLinkVertices()
        if node_coords['x'][old_index] == 0 and node_coords['y'][old_index] == 0:
            warnings.warn('Node has zero value for coordinates')
        # Get the elevation
        elev = self.getNodeElevations(old_index)
        # Get the connected links and link info
        conn_link_mat = self.getNodesConnectingLinksID()
        link_info = self.getLinksInfo()
        link_type_mat = self.getLinkType()
        link_mat, link_type_m, link_node_index, link_node_indices, choice_mat = [], [], [], [], []
        # Get data of nameID and type for connected links
        for i in range(len(conn_link_mat)):
            if conn_link_mat[i][0] == Id:
                link_mat.append(conn_link_mat[i][1])
                link_type_m.append(link_type_mat[i])
                link_node_index.append(self.getNodeIndex(conn_link_mat[i][1]))
                link_node_indices.append(i + 1)
                choice_mat.append(1 + 1)
            elif conn_link_mat[i][1] == Id:
                link_mat.append(conn_link_mat[i][0])
                link_type_m.append(link_type_mat[i])
                link_node_index.append(self.getNodeIndex(conn_link_mat[i][0]))
                link_node_indices.append(i + 1)
                choice_mat.append(2)
        # Delete the node to be replaced
        self.deleteNode(old_index)
        # Create a new node according to the type
        node_coords = [node_coords['x'][old_index], node_coords['y'][old_index]]
        index = 0
        if Type == 0:
            # Add new jucntion with previous nodes coordinates and elevation
            index = self.addNodeJunction(Id, node_coords, elev)
        elif Type == 1:
            # Add new reservoir with previous nodes coordinates and elevation
            index = self.addNodeReservoir(Id, node_coords, elev)
        elif Type == 2:
            # Add new tank with previous nodes coordinates and elevation
            index = self.addNodeTank(Id, node_coords, elev)
        # Add the deleted links with the newIndex
        for i in range(len(link_mat)):
            link_id = 'L_' + Id + str(i)
            l_type_code = eval('self.ToolkitConstants.EN_' + link_type_m[i])
            # Add a link
            # Check which node x coordinate is smaller to set it as the start
            if choice_mat[i] == 1:
                lindex = self.api.ENaddlink(link_id, l_type_code, Id, link_mat[i])
            else:
                lindex = self.api.ENaddlink(link_id, l_type_code, link_mat[i], Id)
            # add attributes to the new links
            self.setLinkLength(lindex, link_info.LinkLength[link_node_indices[i]])
            self.setLinkDiameter(lindex, link_info.LinkDiameter[link_node_indices[i]])
            self.setLinkRoughnessCoeff(lindex, link_info.LinkRoughnessCoeff[link_node_indices[i]])
            if link_info.LinkMinorLossCoeff[link_node_indices[i]]:
                self.setLinkMinorLossCoeff(lindex, link_info.LinkMinorLossCoeff[link_node_indices[i]])
            self.setLinkInitialStatus(lindex, link_info.LinkInitialStatus[link_node_indices[i]])
            self.setLinkInitialSetting(lindex, link_info.LinkInitialSetting[link_node_indices[i]])
            self.setLinkBulkReactionCoeff(lindex, link_info.LinkBulkReactionCoeff[link_node_indices[i]])
            self.setLinkWallReactionCoeff(lindex, link_info.LinkWallReactionCoeff[link_node_indices[i]])
            if len(vert_coords['x'][link_node_indices[i]]) != 0:
                # Add vertices with neighbour nodes
                x_coord = vert_coords['x'][link_node_indices[i]]
                y_coord = vert_coords['y'][link_node_indices[i]]
                self.setLinkVertices(link_id, x_coord, y_coord)
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
        controlTypeIndex = 0
        nodeIndex = 0
        controlLevel = 0
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
                if splitControl.__len__() > 6 and "PM" == splitControl[6]:
                    controlLevel += 43200
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
        self.CMDCODE = 1  # Hide messages at command window from bin computed
        self.LibEPANET = None,  # EPANET library dll
        self.LibEPANETpath = None,  # EPANET library dll path
        self.LinkBulkReactionCoeff = None,  # Bulk reaction coefficient of each link
        self.OptionsHydraulics = None,  # Save or Use hydraulic soltion. *** Not implemented ***
        self.OptionsPattern = None,  # *** Not implemented ***

        self.linkInfo = self.getLinksInfo().to_dict()
        self.LinkDiameter = self.linkInfo['LinkDiameter']  # Link diameters
        self.LinkLength = self.linkInfo['LinkLength']  # Link lengths
        self.LinkRoughnessCoeff = self.linkInfo['LinkRoughnessCoeff']  # Link roughness coefficients
        self.LinkMinorLossCoeff = self.linkInfo['LinkMinorLossCoeff']  # Link minor loss coefficients
        self.LinkInitialStatus = self.linkInfo['LinkInitialStatus']  # Link initial status
        self.LinkInitialSetting = self.linkInfo['LinkInitialSetting']  # Link initial settings
        self.LinkBulkReactionCoeff = self.linkInfo['LinkBulkReactionCoeff']  # Link bulk reaction coeff.
        self.LinkWallReactionCoeff = self.linkInfo['LinkWallReactionCoeff']  # Link wall reaction coeff.
        self.LinkTypeIndex = self.linkInfo['LinkTypeIndex']  # Link type index
        self.LinkType = self.getLinkType()  # ID of link type
        self.LinkPipeCount = self.getLinkPipeCount()  # Number of pipes
        self.LinkPumpCount = self.getLinkPumpCount()  # Number of pumps
        self.LinkValveCount = self.getLinkValveCount()  # Number of valves
        self.LinkCount = self.getLinkCount()  # Number of links
        self.LinkFlowUnits = self.getFlowUnits()  # Units of flow
        self.LinkNameID = self.getLinkNameID()  # Name ID of links
        self.LinkIndex = self.getLinkIndex()  # Index of links
        self.LinkPipeIndex = self.getLinkPipeIndex()  # Index of pipe links
        self.LinkPumpIndex = self.getLinkPumpIndex()  # Index of pumps
        self.LinkValveIndex = self.getLinkValveIndex()  # Index of valves
        self.LinkPipeNameID = self.getLinkPipeNameID()  # Name ID of pipe links
        self.LinkPumpNameID = self.getLinkPumpNameID()  # Name ID of pumps
        self.LinkValveNameID = self.getLinkValveNameID()  # ID name of valves
        self.LinkPumpHeadCurveIndex = self.getLinkPumpHeadCurveIndex()  # Head curve indices
        self.LinkPumpPatternNameID = self.getLinkPumpPatternNameID()  # ID of pump pattern
        self.LinkPumpPatternIndex = self.getLinkPumpPatternIndex()  # Index of pump pattern
        self.LinkPumpTypeCode = self.getLinkPumpTypeCode()  # Pump index/code
        self.LinkPumpType = self.getLinkPumpType()  # Pump type e.g. constant horsepower, power function,
        # user-defined custom curve
        self.LinkPumpPower = self.getLinkPumpPower()  # Power value

        self.demModelInfo = self.getDemandModel()
        self.libFunctions = self.getLibFunctions()  # EPANET functions in dll

        self.NodesConnectingLinksIndex = self.linkInfo['NodesConnectingLinksIndex']  # Indices of nodes
        self.NodesConnectingLinksID = self.getNodesConnectingLinksID()  # Name IDs of nodes which connect links
        # which connect links
        self.nodeInfo = self.getNodesInfo().to_dict()
        self.NodeElevations = self.nodeInfo['NodeElevations']  # Elevations of nodes
        self.NodePatternIndex = self.nodeInfo['NodePatternIndex']  # Indices of the patterns
        self.NodeEmitterCoeff = self.nodeInfo['NodeEmitterCoeff']  # Node emitter coeff.
        self.NodeInitialQuality = self.nodeInfo['NodeInitialQuality']  # Node initial quality values
        self.NodeTypeIndex = self.nodeInfo['NodeTypeIndex']  # Index /code of node type
        self.NodeSourcePatternIndex = self.nodeInfo['NodeSourcePatternIndex']  # Index of pattern for node sources
        self.NodeSourceTypeIndex = self.nodeInfo['NodeSourceTypeIndex']  # Index of source type
        self.NodeSourceQuality = self.nodeInfo['NodeSourceQuality']  # Quality of node sources
        self.NodeNameID = self.getNodeNameID()  # Name ID of all nodes
        self.NodeCount = self.getNodeCount()  # Number of nodes
        self.NodeTankReservoirCount = self.getNodeTankReservoirCount()  # Number of tanks and reservoirs
        self.NodeJunctionCount = self.getNodeJunctionCount()  # Number of junctions
        self.NodeReservoirCount = self.getNodeReservoirCount()  # Number of reservoirs
        self.NodeTankCount = self.getNodeTankCount()  # Number of tanks
        self.NodeType = self.getNodeType()  # ID of node type
        self.NodeIndex = self.getNodeIndex()  # Index of nodes
        self.NodeReservoirIndex = self.getNodeReservoirIndex()  # Index of reservoirs
        self.NodeTankIndex = self.getNodeTankIndex()  # Indices of Tanks
        self.NodeJunctionIndex = self.getNodeJunctionIndex()  # Index of node junctions
        self.NodeReservoirNameID = self.getNodeReservoirNameID()  # Name ID of reservoirs
        self.NodeTankNameID = self.getNodeTankNameID()  # Name ID of Tanks
        self.NodeJunctionNameID = self.getNodeJunctionNameID()  # Name ID of node junctions
        self.NodeBaseDemands = self.getNodeBaseDemands()  # Base demands of nodes
        self.NodeTankInitialLevel = self.getNodeTankInitialLevel()  # Initial water level in tanks
        self.NodeTankInitialWaterVolume = self.getNodeTankInitialWaterVolume()  # Initial water volume in tanks
        self.NodeTankMixingModelCode = self.getNodeTankMixingModelCode()  # Code of mixing model
        # (MIXED:0, 2COMP:1, FIFO:2, LIFO:3)
        self.NodeTankMixingModelType = self.getNodeTankMixingModelType()  # Type of mixing model
        # (MIXED, 2COMP, FIFO, or LIFO)
        self.NodeTankMixZoneVolume = self.getNodeTankMixZoneVolume()  # Mixing zone volume
        self.NodeTankDiameter = self.getNodeTankDiameter()  # Diameters of tanks
        self.NodeTankMinimumWaterVolume = self.getNodeTankMinimumWaterVolume()  # Minimum water volume
        self.NodeTankVolumeCurveIndex = self.getNodeTankVolumeCurveIndex()  # Index of curve for tank volumes
        self.NodeTankMinimumWaterLevel = self.getNodeTankMinimumWaterLevel()  # Minimum water level
        self.NodeTankMaximumWaterLevel = self.getNodeTankMaximumWaterLevel()  # Maximum water level in tanks
        self.NodeTankMinimumFraction = self.getNodeTankMixingFraction()  # Fraction of the total tank volume
        # devoted to the inlet/outlet compartment
        self.NodeTankBulkReactionCoeff = self.getNodeTankBulkReactionCoeff()  # Bulk reaction coefficients in tanks
        self.NodeDemandPatternNameID = self.getNodeDemandPatternNameID()  # ID of demand patterns
        self.NodeDemandPatternIndex = self.getNodeDemandPatternIndex()  # Index of demand patterns

        self.CurveCount = self.getCurveCount()  # Number of curves
        self.CurveIndex = self.getCurveIndex()  # Index of curves
        self.CurvesInfo = self.getCurvesInfo()  # Curves info

        self.ControlRulesCount = self.getControlRulesCount()  # Number of controls
        self.Controls = self.getControls()  # Controls information

        self.OptionsMaxTrials = self.getOptionsMaxTrials()  # Maximum number of trials (40 is default)
        self.OptionsAccuracyValue = self.getOptionsAccuracyValue()  # Convergence value (0.001 is default)
        self.OptionsQualityTolerance = self.getOptionsQualityTolerance()  # Tolerance for water  (0.01 is default)
        self.OptionsEmitterExponent = self.getOptionsEmitterExponent()  # Exponent of pressure at an emitter node
        # (0.5 is default)
        self.OptionsPatternDemandMultiplier = self.getOptionsPatternDemandMultiplier()  # Multiply demand values
        # (1 is default)
        self.OptionsSpecificGravity = None,  # *** Not yet implemented ***
        self.OptionsUnbalanced = None,  # *** Not yet implemented ***
        self.OptionsViscosity = None,  # *** Not yet implemented ***
        self.OptionsHeadError = self.getOptionsHeadError()  # Retrieves the maximum head loss error for
        # hydraulic convergence
        self.OptionsFlowChange = self.getOptionsFlowChange()  # Retrieves the maximum flow change for
        # hydraulic convergence
        self.OptionsHeadLossFormula = self.getOptionsHeadLossFormula()  # Headloss formula (Hazen-Williams,
        # Darcy-Weisbach or Chezy-Manning)

        self.PatternCount = self.getPatternCount()  # Number of patterns
        self.PatternNameID = self.getPatternNameID()  # ID of the patterns
        self.PatternIndex = self.getPatternIndex()
        self.PatternLengths = self.getPatternLengths()  # Length of the patterns
        self.Pattern = self.getPattern()  # Get all patterns - matrix

        self.QualityCode = self.getQualityCode()  # Water quality analysis code (None:0/Chemical:1/Age:2/Trace:3)
        self.QualityTraceNodeIndex = self.getQualityTraceNodeIndex()  # Index of trace node (0 if QualityCode<3)
        self.QualityType = self.getQualityType()  # Water quality analysis type (None/Chemical/Age/Trace)
        n = self.getQualityInfo()
        self.QualityChemUnits = n.QualityChemUnits  # Units for quality concentration
        self.QualityChemName = n.QualityChemName  # Name of quality type

        self.TimeSimulationDuration = self.getTimeSimulationDuration()  # Simulation duration
        self.TimeHydraulicStep = self.getTimeHydraulicStep()  # Hydraulic time step
        self.TimeQualityStep = self.getTimeQualityStep()  # Quality Step
        self.TimePatternStep = self.getTimePatternStep()  # Pattern Step
        self.TimePatternStart = self.getTimePatternStart()  # Pattern start time
        self.TimeReportingStep = self.getTimeReportingStep()  # Reporting time step
        self.TimeReportingStart = self.getTimeReportingStart()  # Start time for reporting
        self.TimeRuleControlStep = self.getTimeRuleControlStep()  # Time step for evaluating rule-based controls
        self.TimeStatisticsIndex = self.getTimeStatisticsIndex()  # Index of type ('NONE':0, 'AVERAGE':1,
        # 'MINIMUM':2, 'MAXIMUM':3, 'RANGE':4)
        self.TimeStatisticsType = self.getTimeStatisticsType()  # Type ('NONE', 'AVERAGE', 'MINIMUM',
        # 'MAXIMUM', 'RANGE')
        self.TimeReportingPeriods = self.getTimeReportingPeriods()  # Reporting periods
        self.TimeStartTime = self.getTimeStartTime()  # Number of start time
        self.TimeHTime = self.getTimeHTime()  # Number of htime
        self.TimeHaltFlag = self.getTimeHaltFlag()  # Number of halt flag
        self.TimeNextEvent = self.getTimeNextEvent()  # Find the next event of the hydraulic time step length,
        # or the time to next fill/empty
        self.NodeTankMaximumWaterVolume = self.getNodeTankMaximumWaterVolume()  # Maximum water volume
        self.NodeDemandCategoriesNumber = self.getNodeDemandCategoriesNumber()  # Number of demand categories for nodes
        self.PatternAverageValue = self.getPatternAverageValue()  # Average value of patterns
        n = self.getStatistic()
        self.RelativeError = n.RelativeError  # Relative error - hydraulic simulation statistic
        self.Iterations = n.Iterations  # Iterations to reach solution

        units = self.getUnits()  # Get all units of the network parameters
        self.NodeCoordinates = self.getNodeCoordinates()  # Coordinates for each node
        # (long/lat & intermediate pipe coordinates)
        self.Version = self.getVersion()

        # Units
        self.NodePressureUnits = units.NodePressureUnits
        self.PatternDemandsUnits = units.PatternDemandsUnits
        self.LinkPipeDiameterUnits = units.LinkPipeDiameterUnits
        self.NodeTankDiameterUnits = units.NodeTankDiameterUnits
        self.EnergyEfficiencyUnits = units.EnergyEfficiencyUnits
        self.NodeElevationUnits = units.NodeElevationUnits
        self.NodeDemandUnits = units.NodeDemandUnits
        self.NodeEmitterCoefficientUnits = units.NodeEmitterCoefficientUnits
        self.EnergyUnits = units.EnergyUnits
        self.LinkFrictionFactorUnits = units.LinkFrictionFactorUnits
        self.NodeHeadUnits = units.NodeHeadUnits
        self.LinkLengthsUnits = units.LinkLengthsUnits
        self.LinkMinorLossCoeffUnits = units.LinkMinorLossCoeffUnits
        self.LinkPumpPowerUnits = units.LinkPumpPowerUnits
        self.QualityReactionCoeffBulkUnits = units.QualityReactionCoeffBulkUnits
        self.QualityReactionCoeffWallUnits = units.QualityReactionCoeffWallUnits
        self.LinkPipeRoughnessCoeffUnits = units.LinkPipeRoughnessCoeffUnits
        self.QualitySourceMassInjectionUnits = units.QualitySourceMassInjectionUnits
        self.LinkVelocityUnits = units.LinkVelocityUnits
        self.NodeTankVolumeUnits = units.NodeTankVolumeUnits
        self.QualityWaterAgeUnits = units.QualityWaterAgeUnits

    def __getLinkIndices(self, *argv):
        if len(argv) > 0:
            if isinstance(argv[0], list):
                if isinstance(argv[0][0], str):
                    return self.getLinkIndex(argv[0])
                else:
                    return argv[0]
            else:
                if isinstance(argv[0], str):
                    return [self.getLinkIndex(argv[0])]
                else:
                    return [argv[0]]
        else:
            return self.getLinkIndex()

    def __getLinkInfo(self, code_p, *argv):
        values = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, (list, np.ndarray)):
                for i in index:
                    values.append(self.api.ENgetlinkvalue(i, code_p))
            else:
                values = self.api.ENgetlinkvalue(index, code_p)
        else:
            for i in range(self.getLinkCount()):
                values.append(self.api.ENgetlinkvalue(i + 1, code_p))
        return np.array(values)

    def __getNodeIndices(self, *argv):
        if len(argv) > 0:
            if isinstance(argv[0], list):
                if isinstance(argv[0][0], str):
                    return self.getNodeIndex(argv[0])
                else:
                    return argv[0]
            else:
                if isinstance(argv[0], str):
                    return [self.getNodeIndex(argv[0])]
                else:
                    return [argv[0]]
        else:
            return self.getNodeIndex()

    def __getNodeInfo(self, code_p, *argv):
        value = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, (list, np.ndarray)):
                for i in index:
                    value.append(self.api.ENgetnodevalue(i, code_p))
            else:
                return self.api.ENgetnodevalue(index, code_p)
        else:
            for i in range(self.getNodeCount()):
                value.append(self.api.ENgetnodevalue(i + 1, code_p))
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
            if isinstance(self.NodeTankMixingModelCode, np.ndarray):
                if self.NodeTankMixingModelCode.shape == ():  # Handle cases with strange shapes
                    self.NodeTankMixingModelCode = [self.NodeTankMixingModelCode]
            self.NodeTankMixingModelType = [self.TYPEMIXMODEL[i.astype(int)] for i in self.NodeTankMixingModelCode]
        else:
            self.NodeTankMixingModelType = self.TYPEMIXMODEL[self.NodeTankMixingModelCode.astype(int)]
        return [self.NodeTankMixingModelCode, self.NodeTankMixingModelType]

    def __getPumpLinkInfo(self, code_p, *argv):
        indices = self.getLinkPumpIndex()
        values = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, (list, np.ndarray)):
                if not sum(self.__isMember(index, indices)):
                    index = self.getLinkPumpIndex(index)
                for i in index:
                    values.append(self.api.ENgetlinkvalue(i, code_p))
            else:
                if index not in indices:
                    pIndex = self.getLinkPumpIndex(index)
                    if not pIndex:
                        return []
                else:
                    pIndex = index
                return self.api.ENgetlinkvalue(pIndex, code_p)
        else:
            for i in indices:
                values.append(self.api.ENgetlinkvalue(i, code_p))
        return np.array(values)

    def __getTankNodeInfo(self, code_p, *argv):
        indices = self.getNodeTankIndex()
        values = []
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, (list, np.ndarray)):
                if not sum(self.__isMember(index, indices)):
                    index = self.getNodeTankIndex(index)
                for i in index:
                    values.append(self.api.ENgetnodevalue(i, code_p))
            else:
                if index not in indices:
                    pIndex = self.getNodeTankIndex(index)
                    if not pIndex:
                        return []
                else:
                    pIndex = index
                values = self.api.ENgetnodevalue(pIndex, code_p)
        else:
            for i in indices:
                values.append(self.api.ENgetnodevalue(i, code_p))
        return np.array(values)

    def __isMember(self, A, B):
        return [np.sum(a == B) for a in np.array(A)]

    def __readEpanetBin(self, f, binfile, *argv):
        value = EpytValues()
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
            while True:
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
            f.read(1)
            f.read(1)
            f.read(1)
            value.WarningFlag = list(f.read(1))[0]
            self.errcode = value.WarningFlag
            # check here - error
            value.MagicNumber = struct.unpack('b', f.read(1))

        if len(argv) > 0:
            v = EpytValues()
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
                if isinstance(value, list):
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

    def __setEval(self, func, code_pstr, Type, value, *argv):
        if len(argv) == 1:
            index = value
            value = argv[0]
            if isinstance(index, list):
                j = 0
                for i in index:
                    if np.isnan(value[j]):
                        continue
                    strFunc = 'self.api.' + func + '(' + str(
                        i) + ',' + 'self.ToolkitConstants.EN_' + code_pstr + ',' + str(value[j]) + ')'
                    eval(strFunc)
                    j += 1
            else:
                strFunc = 'self.api.' + func + '(' + str(
                    index) + ',' + 'self.ToolkitConstants.EN_' + code_pstr + ',' + str(value) + ')'
                eval(strFunc)
        else:
            count = 0
            if Type == 'LINK':
                count = self.getLinkCount()
            elif Type == 'NODE':
                count = self.getNodeCount()
            for i in range(count):
                if np.isnan(value[i]):
                    continue
                strFunc = 'self.api.' + func + '(' + str(
                    i + 1) + ',' + 'self.ToolkitConstants.EN_' + code_pstr + ',' + str(value[i]) + ')'
                eval(strFunc)

    def __setEvalLinkNode(self, func, code_pstr, Type, value, *argv):
        if len(argv) == 1:
            index = value
            value = argv[0]
            if isinstance(index, (list, np.ndarray)):
                j = 0
                if isinstance(value, list):
                    for i in index:
                        strFunc = 'self.api.' + func + '(' + str(
                            i) + ',' + 'self.ToolkitConstants.EN_' + code_pstr + ',' + str(value[j]) + ')'
                        eval(strFunc)
                        j += 1
                else:
                    for i in index:
                        strFunc = 'self.api.' + func + '(' + str(
                            i) + ',' + 'self.ToolkitConstants.EN_' + code_pstr + ',' + str(value) + ')'
                        eval(strFunc)
                        j += 1
            else:
                Index = []
                if Type == 'TANK':
                    Index = self.getNodeTankIndex()
                elif Type == 'PUMP':
                    Index = self.getLinkPumpIndex()
                if index not in Index:
                    Index = Index[index - 1]
                else:
                    Index = index
                    if isinstance(value, (list, np.ndarray)):
                        value = value[0]
                strFunc = 'self.api.' + func + '(' + str(
                    Index) + ',' + 'self.ToolkitConstants.EN_' + code_pstr + ',' + str(value) + ')'
                eval(strFunc)
        else:
            count = 0
            indices = []
            if Type == 'TANK':
                count = self.getNodeTankCount()
                indices = self.getNodeTankIndex()
            elif Type == 'PUMP':
                count = self.getLinkPumpCount()
                indices = self.getLinkPumpIndex()
            if isinstance(value, (list, np.ndarray)):
                for i in range(count):
                    strFunc = 'self.api.' + func + '(' + str(
                        indices[i]) + ',' + 'self.ToolkitConstants.EN_' + code_pstr + ',' + str(value[i]) + ')'
                    eval(strFunc)
            else:
                for i in range(count):
                    strFunc = 'self.api.' + func + '(' + str(
                        indices[i]) + ',' + 'self.ToolkitConstants.EN_' + code_pstr + ',' + str(value) + ')'
                    eval(strFunc)

    def __setFlowUnits(self, unitcode, *argv):
        self.api.ENsetflowunits(unitcode)
        if len(argv) == 1:
            self.saveInputFile(argv[0])

    def __setNodeDemandPattern(self, fun, propertyCode, value, *argv):

        categ = 1
        indices = self.__getNodeJunctionIndices()
        param = value
        if len(argv) == 2:
            indices = value
            categ = argv[0]
            param = argv[1]
        elif len(argv) == 1:
            indices = value
            param = argv[0]

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
                    self.api.ENsetnodevalue(i, propertyCode, param[j])
                elif categ == 1 or len(indices) == 1:
                    eval('self.api.' + fun + '(i, categ, param[j])')
                else:
                    if c + 1 > self.getNodeDemandCategoriesNumber(i):
                        self.addNodeJunctionDemand(i, param[j])
                    else:
                        eval('self.api.' + fun + '(i, c, param[j])')
                j += 1

    """MSX Functions"""

    def loadMSXFile(self, msxname, customMSXlib=None, ignore_properties=False):
        """Loads an msx file
        Example:
            d.loadMSXFile('net2-cl2.msx')

        Example using custom msx library :
        msxlib=os.path.join(os.getcwd(), 'epyt','libraries','win','epanetmsx.dll')

        d = epanet(inpname, msx=True, customlib=epanetlib)
        d.loadMSXFile(msxname, customMSXlib=msxlib)"""

        if not os.path.exists(msxname):
            for root, dirs, files in os.walk(epyt_root):
                for name in files:
                    if name.lower().endswith(".msx"):
                        if name == msxname:
                            msxname = os.path.join(root, msxname)
                            break
                else:
                    continue
                break

        self.MSXFile = msxname[:-4]
        self.MSXTempFile = msxname[:-4] + '_temp.msx'
        copyfile(msxname, self.MSXTempFile)
        self.msx = epanetmsxapi(self.MSXTempFile, customMSXlib=customMSXlib, display_msg=self.display_msg,
                                msxrealfile=self.MSXFile)

        # Message to user if he uses ph with msx
        if self.api._ph is not None:
            warnings.warn('Please set ph=False when using MSX.')

        if ignore_properties:
            self.msx.MSXEquationsTerms = self.getMSXEquationsTerms()
            self.msx.MSXEquationsPipes = self.getMSXEquationsPipes()
            self.msx.MSXEquationsTanks = self.getMSXEquationsTanks()
            self.msx.MSXSpeciesCount = self.getMSXSpeciesCount()
            self.msx.MSXConstantsCount = self.getMSXConstantsCount()
            self.msx.MSXParametersCount = self.getMSXParametersCount()
            self.msx.MSXPatternsCount = self.getMSXPatternsCount()
            self.msx.MSXSpeciesIndex = self.getMSXSpeciesIndex()
            self.msx.MSXSpeciesNameID = self.getMSXSpeciesNameID()
            self.msx.MSXSpeciesType = self.getMSXSpeciesType()
            self.msx.MSXSpeciesUnits = self.getMSXSpeciesUnits()
            self.msx.MSXSpeciesATOL = self.getMSXSpeciesATOL()
            self.msx.MSXSpeciesRTOL = self.getMSXSpeciesRTOL()
            self.msx.MSXConstantsNameID = self.getMSXConstantsNameID()
            self.msx.MSXConstantsValue = self.getMSXConstantsValue()
            self.msx.MSXConstantsIndex = self.getMSXConstantsIndex()
            self.msx.MSXParametersNameID = self.getMSXParametersNameID()
            self.msx.MSXParametersIndex = self.getMSXParametersIndex()
            self.msx.MSXParametersTanksValue = self.getMSXParametersTanksValue()
            self.msx.MSXParametersPipesValue = self.getMSXParametersPipesValue()
            self.msx.MSXPatternsNameID = self.getMSXPatternsNameID()
            self.msx.MSXPatternsIndex = self.getMSXPatternsIndex()
            self.msx.MSXPatternsLengths = self.getMSXPatternsLengths()
            self.msx.MSXNodeInitqualValue = self.getMSXNodeInitqualValue()
            self.msx.MSXLinkInitqualValue = self.getMSXLinkInitqualValue()
            self.msx.MSXSources = self.getMSXSources()
            self.msx.MSXSourceType = self.getMSXSourceType()
            self.msx.MSXSourceLevel = self.getMSXSourceLevel()
            self.msx.MSXSourcePatternIndex = self.getMSXSourcePatternIndex()
            self.msx.MSXSourceNodeNameID = self.getMSXSourceNodeNameID()
            self.msx.MSXPattern = self.getMSXPattern()

        return self.msx

    def unloadMSX(self):
        """Unload library and close the MSX Toolkit system.
        Example:
               d.unloadMSX()
               """
        self.msx.MSXclose()
        arch = sys.platform
        if arch == 'win64' or arch == 'win32':
            msx_temp_files = list(filter(lambda f: os.path.isfile(os.path.join(os.getcwd(), f))
                                                   and f.startswith("msx") and "." not in f, os.listdir(os.getcwd())))
            safe_delete(msx_temp_files)
            print('EPANET-MSX Toolkit is unloaded.')

    def getMSXSpeciesCount(self):
        """ Retrieves the number of species.

             Example:
               d = epanet('Net3-NH2CL.inp')
               d.loadMSXFile('Net3-NH2CL.msx')
               d.getMSXSpeciesCount()

             See also getMSXSpeciesIndex, getMSXSpeciesNameID, getMSXSpeciesConcentration,
                      getMSXSpeciesType, getMSXSpeciesUnits, getMSXSpeciesATOL,
                      getMSXSpeciesRTOL."""
        return self.msx.MSXgetcount(self.ToolkitConstants.MSX_SPECIES)

    def getMSXConstantsCount(self):
        """  Retrieves the number of constants.

             Example:
               d = epanet('Net3-NH2CL.inp')
               d.loadMSXFile('Net3-NH2CL.msx')
               d.getMSXConstantsCount()

             See also getMSXConstantsIndex, getMSXConstantsValue,
                      getMSXConstantsNameID."""
        return self.msx.MSXgetcount(self.ToolkitConstants.MSX_CONSTANT)

    def getMSXParametersCount(self):
        """  Retrieves the number of parameters.

             Example:
               d = epanet('Net3-NH2CL.inp')
               d.loadMSXFile('Net3-NH2CL.msx')
               d.getMSXParametersCount()

             See also setMSXParametersTanksValue, setMSXParametersPipesValue,
                      getMSXParametersIndex, getMSXParametersTanksValue,
                      getMSXParametersPipesValue."""
        return self.msx.MSXgetcount(self.ToolkitConstants.MSX_PARAMETER)

    def getMSXPatternsCount(self):
        """ Retrieves the number of patterns.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.addMSXPattern('P1', [1.0, 0.0 1.0])
               d.addMSXPattern('P2', [0.0, 0.0 2.0])
               d.getMSXPatternsCount()

             See also setMSXPattern, setMSXPatternValue, addMSXPattern."""
        return self.msx.MSXgetcount(self.ToolkitConstants.MSX_PATTERN)

    def saveMSXFile(self, msxname):
        """ Saves the data associated with the current MSX project into a new MSX input file.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.saveMSXFile('testMSX.msx')

             See also writeMSXFile."""
        self.msx.MSXsavemsxfile(msxname)

    def saveMSXQualityFile(self, outfname):
        """  Saves the quality as bin file.

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXComputedQualitySpecie('CL2')
              d.saveMSXQualityFile('testMSXQuality.bin')"""
        self.msx.MSXsaveoutfile(outfname)

    def solveMSXCompleteHydraulics(self):
        """Solve complete hydraulic over the entire simulation period.
            %
            % Example:
            %   d = epanet('net2-cl2.inp')
            %   d.loadMSXFile('net2-cl2.msx')
            %   d.solveMSXCompleteHydraulics()
            %
            % See also solveMSXCompleteQuality."""
        self.msx.MSXsolveH()

    def solveMSXCompleteQuality(self):
        """Solve complete hydraulic over the entire simulation period.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.solveMSXCompleteQuality()

            See also solveMSXCompleteHydraulics."""
        self.msx.MSXsolveQ()

    def writeMSXReport(self):
        self.msx.MSXreport()

    def useMSXHydraulicFile(self, hydname):
        """% Uses a previously saved EPANET hydraulics file as the source
            % of hydraulic information.
            %
            % Example:
            %  d = epanet('net2-cl2.inp');
            %  d.loadMSXFile('net2-cl2.msx');
            %  d.saveHydraulicsOutputReportingFile
            %  d.saveHydraulicFile('testMSXHydraulics.hyd')
            %  d.useMSXHydraulicFile('testMSXHydraulics.hyd')
            %
            % See also saveHydraulicsOutputReportingFile, saveHydraulicFile."""
        self.msx.MSXusehydfile(hydname)

    def getMSXPatternValue(self, patternIndex, patternStep):
        """  Retrieves the multiplier at a specific time period for a given source time pattern.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.addMSXPattern('P1', [1.0 0.0 3.0])
               d.getMSXPatternValue(1,3)   Retrieves the third multiplier of the first pattern.

             See also setMSXPatternValue, setMSXPattern, setMSXPatternMatrix,
                      getMSXPatternsIndex, getMSXPatternsNameID."""
        return self.msx.MSXgetpatternvalue(patternIndex, patternStep)

    def initializeMSXQualityAnalysis(self, flag):
        """ Initializes the MSX system before solving for water quality results
             in step-wise fashion.

             flag options:
                1: if water quality results should be saved to a scratch
                   binary file or
                0: if results are not saved to file.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               tleft = 1
               d.solveMSXCompleteHydraulics()
               d.initializeMSXQualityAnalysis(0)
               while(tleft>0):
                   t,tleft = d.stepMSXQualityAnalysisTimeLeft


             See also solveMSXCompleteHydraulics, stepMSXQualityAnalysisTimeLeft."""
        self.msx.MSXinit(flag)

    def stepMSXQualityAnalysisTimeLeft(self):
        """ Advances the water quality solution through a single water quality time step when
             performing a step-wise simulation.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               tleft = 1
               d.solveMSXCompleteHydraulics()
               d.initializeMSXQualityAnalysis(0)
               while(tleft>0):
                   t,tleft = d.stepMSXQualityAnalysisTimeLeft()


            % See also solveMSXCompleteHydraulics, initializeMSXQualityAnalysis."""
        t, tleft = self.msx.MSXstep()
        return t, tleft

    def getMSXError(self, code):
        """  Retrieves the MSX erorr message for specific erorr code.

             Example:
               d.getMSXError(510)"""
        self.msx.MSXgeterror(code)

    def getMSXOptions(self):
        """ Retrieves all the options.

             Example:
               d=epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.getMSXOptions()"""

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
        try:
            # Key-value pairs to search for
            keys = ["AREA_UNITS", "RATE_UNITS", "SOLVER", "COUPLING", "TIMESTEP", "ATOL", "RTOL", "COMPILER",
                    "SEGMENTS", \
                    "PECLET"]
            float_values = ["TIMESTEP", "ATOL", "RTOL", "SEGMENTS", "PECLET"]
            values = {key: None for key in keys}

            # Flag to determine if we're in the [OPTIONS] section
            in_options = False

            # Open and read the file
            with open(self.MSXTempFile, 'r') as file:
                for line in file:
                    # Check for [OPTIONS] section
                    if "[OPTIONS]" in line:
                        in_options = True
                    elif "[" in line and "]" in line:
                        in_options = False  # We've reached a new section

                    if in_options:
                        # Pattern to match the keys and extract values, ignoring comments and whitespace
                        pattern = re.compile(r'^\s*(' + '|'.join(keys) + r')\s+(.*?)\s*(?:;.*)?$')
                        match = pattern.search(line)
                        if match:
                            key, value = match.groups()
                            if key in float_values:
                                values[key] = float(value)
                            else:
                                values[key] = value

            return SimpleNamespace(**values)
        except FileNotFoundError:
            warnings.warn("Please load MSX File.")
            return {}

    def getMSXTimeStep(self):
        """ Retrieves the time step.

             Example:
               d=epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.getMSXTimeStep()

             See also setMSXTimeStep."""
        return self.getMSXOptions().TIMESTEP

    def getMSXRateUnits(self):
        """ Retrieves  rate units.
             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.getMSXRateUnits()

             See also setMSXRateUnits."""
        return self.getMSXOptions().RATE_UNITS

    def getMSXAreaUnits(self):
        """ Retrieves  Are units.
            Example:
             d = epanet('net2-cl2.inp')
             d.loadMSXFile('net2-cl2.msx')
             d.getMSXAreaUnits()

             See also setMSXAreaUnits."""
        return self.getMSXOptions().AREA_UNITS

    def getMSXCompiler(self):
        """  Retrieves the chemistry function compiler code.

             Compiler Options:
               NONE: no compiler (default option)
               gc: MinGW or Gnu C++ compilers
               vc: Visual C++ compiler

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.getMSXCompiler()

             See also setMSXCompilerNONE, setMSXCompilerVC,
                      setMSXCompilerGC."""
        return self.getMSXOptions().COMPILER

    def getMSXCoupling(self):
        """  Retrieves the degree of coupling for solving DAE's.

             Coupling Options:
               NONE: The solution to the algebraic equations is only updated
                     at the end of each integration time step.
               FULL: The updating is done whenever a new set of values for the
                     rate-dependent variables in the reaction
                     rate expressions is computed.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.getMSXCoupling()

             See also setMSXCouplingFULL, setMSXCouplingNONE."""
        return self.getMSXOptions().COUPLING

    def getMSXSolver(self):
        """ Retrieves the solver method.

             Numerical integration methods:
               EUL = standard Euler integrator
               RK5 = Runge-Kutta 5th order integrator
               ROS2 = 2nd order Rosenbrock integrator.

             Example:
               d=epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.getMSXSolver()

             See also setMSXSolverEUL, setMSXSolverRK5, setMSXSolverROS2."""
        return self.getMSXOptions().SOLVER

    def getMSXAtol(self):
        """ Retrieves the absolute tolerance.

              Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.getMSXAtol()

             See also getMSXRtol."""
        return self.getMSXOptions().ATOL

    def getMSXRtol(self):
        """  Retrieves the relative accuracy level.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.getMSXRtol()

             See also getMSXAtol."""
        return self.getMSXOptions().RTOL

    def getMSXConstantsNameID(self, *ids):
        """Return one or more MSX constant names by index.

        Parameters
        ----------
        *ids : int or iterable of int, optional
            Indices (1-based) of the constants to retrieve.
            • If no ids are given, all constants are returned.
            • If the first and only positional argument is an iterable
              (list/tuple/set), its contents are used as the index list.

        Returns
        -------
        list[str]
            Constant names in the order requested.

        Setup:
               d = epanet('Net3-NH2CL.inp')
               d.loadMSXFile('Net3-NH2CL.msx')
        Examples:
        --------
        >>> d.getMSXConstantsNameID()         # all constants
        >>> d.getMSXConstantsNameID(1)        # first constant
        >>> d.getMSXConstantsNameID(1, 2)     # constants 1, 2
        >>> d.getMSXConstantsNameID([1, 2])   # constants 1, 2

        See also getMSXConstantsCount, getMSXConstantsValue,
                      getMSXConstantsNameID.
        """
        total = self.getMSXConstantsCount()


        if not ids:
            indices = range(1, total + 1)

        elif len(ids) == 1 and isinstance(ids[0], (list, tuple, set)):
            indices = ids[0]

        else:
            indices = ids


        MSX_CONSTANT = self.ToolkitConstants.MSX_CONSTANT
        names = []
        for i in indices:
            if not 1 <= i <= total:
                raise IndexError(f"Constant index {i} is out of range 1…{total}")

            id_len = self.msx.MSXgetIDlen(MSX_CONSTANT, i)
            names.append(self.msx.MSXgetID(MSX_CONSTANT, i, id_len))

        return names

    def getMSXParametersNameID(self, *ids):
        """
        Return one or more MSX parameter names (IDs) by index.

        Parameters
        ----------
        *ids : int or iterable of int, optional
            1-based indices of the parameters to retrieve.
            • No arguments  -> all parameters are returned.
            • One iterable  -> its contents are treated as the index list.
            • Several ints  -> those specific indices are returned.

        Returns
        -------
        list[str]
            Parameter names in the order requested.

        Setup:
               d = epanet('Net3-NH2CL.inp')
               d.loadMSXFile('Net3-NH2CL.msx')
        Examples:
        --------
        >>> d.getMSXParametersNameID()          # all parameters
        >>> d.getMSXParametersNameID(1)         # first parameter
        >>> d.getMSXParametersNameID(1, 3)      # parameters 1 and 3
        >>> d.getMSXParametersNameID([2, 4, 5]) # parameters 2, 4, 5

        See also getMSXParametersCount, getMSXParametersIndex,
                      getMSXParametersTanksValue, getMSXParametersPipesValue.
        """

        total = self.getMSXParametersCount()

        # --- decide which indices to fetch -------------------------------------
        if not ids:  # nothing passed -> all
            indices = range(1, total + 1)
        elif len(ids) == 1 and isinstance(ids[0], (list, tuple, set)):
            indices = ids[0]  # a single iterable arg
        else:
            indices = ids  # regular star-args

        # --- fetch the IDs from the toolkit ------------------------------------
        MSX_PARAMETER = self.ToolkitConstants.MSX_PARAMETER
        names = []
        for i in indices:
            if not 1 <= i <= total:
                raise IndexError(f"Parameter index {i} is out of range 1…{total}")

            id_len = self.msx.MSXgetIDlen(MSX_PARAMETER, i)
            names.append(self.msx.MSXgetID(MSX_PARAMETER, i, id_len))

        return names

    def getMSXPatternsNameID(self, *ids):
        """
        Return one or more MSX pattern names (IDs) by index.

        Parameters
        ----------
        *ids : int or iterable of int, optional
            1-based indices of the patterns to retrieve.
            • Call with no arguments  → all patterns are returned.
            • Pass a single iterable  → its contents are treated as the index list.
            • Pass several ints       → those specific indices are returned.

        Returns
        -------
        list[str]
            Pattern names in the order requested.
        Setup:
               d = epanet('Net3-NH2CL.inp')
               d.loadMSXFile('Net3-NH2CL.msx')
               d.addMSXPattern('P1', [1.0, 0.0, 1.0])
               d.addMSXPattern('P2', [0.0, 0.0, 2.0])
               d.addMSXPattern('P3', [0.0, 1.0, 2.0])
               d.addMSXPattern('P4', [1.0, 1.0, 2.0])
        Examples
        --------
        >>> d.getMSXPatternsNameID()            # all patterns
        >>> d.getMSXPatternsNameID(1)           # first pattern
        >>> d.getMSXPatternsNameID(1, 3)        # patterns 1 and 3
        >>> d.getMSXPatternsNameID([2, 4, 5])   # patterns 2, 4, 5

        See also getMSXPattern, getMSXPatternsIndex, getMSXPatternsLengths,
                      setMSXPattern, setMSXPatternMatrix, setMSXPatternValue.
        """
        total = self.getMSXPatternsCount()

        # -------- figure out which indices the caller wants --------------------
        if not ids:  # no args → all patterns
            indices = range(1, total + 1)
        elif len(ids) == 1 and isinstance(ids[0], (list, tuple, set)):
            indices = ids[0]  # a single iterable given
        else:
            indices = ids  # regular *args

        # -------- fetch the IDs from the toolkit --------------------------------
        MSX_PATTERN = self.ToolkitConstants.MSX_PATTERN
        names = []
        for i in indices:
            if not 1 <= i <= total:
                raise IndexError(f"Pattern index {i} is out of range 1…{total}")

            id_len = self.msx.MSXgetIDlen(MSX_PATTERN, i)
            names.append(self.msx.MSXgetID(MSX_PATTERN, i, id_len))

        return names

    def getMSXSpeciesNameID(self, *argv):
        """Retrieves the species' ID.

             Example:
               d = epanet('Net3-NH2CL.inp')
               d.loadMSXFile('Net3-NH2CL.msx')
               d.getMSXSpeciesNameID()        Retrieves the IDs of all the species.
               d.getMSXSpeciesNameID(1)      Retrieves the IDs of the first specie.

             See also getMSXSpeciesIndex, getMSXSpeciesCount, getMSXSpeciesConcentration,
                      getMSXSpeciesType, getMSXSpeciesUnits, getMSXSpeciesATOL,
                      getMSXSpeciesRTOL."""
        values = []
        msx_species = self.ToolkitConstants.MSX_SPECIES
        if len(argv) > 0:
            index = argv[0]
            if isinstance(index, list):
                for i in index:
                    len_id = self.msx.MSXgetIDlen(msx_species, i+1)
                    values.append(self.msx.MSXgetID(msx_species, i+1, len_id))
            else:
                len_id = self.msx.MSXgetIDlen(self.ToolkitConstants.MSX_SPECIES, index)
                values = self.msx.MSXgetID(msx_species, index, len_id)
        else:
            for i in range(self.getMSXSpeciesCount()):
                len_id = self.msx.MSXgetIDlen(msx_species, i+1)
                values.append(self.msx.MSXgetID(msx_species, i+1, len_id))
        return values

    def getMSXParametersIndex(self, *names):
        """
        Return the MSX index of one or more parameters, looked up by name.

        Parameters
        ----------
        *names : str or iterable of str, optional
            Parameter IDs (names) to look up.
            • Call with no arguments  → all parameters are returned.
            • A single iterable       → its contents are used as the name list.
            • Several strings         → those exact names are looked up.

        Returns
        -------
        list[int]
            Parameter indices, in the same order the names were requested.
        Setup:
            d = epanet('Net3-NH2CL.inp')
            d.loadMSXFile('Net3-NH2CL.msx')
        Examples:
        --------
        >>> d.getMSXParametersIndex()                       # all parameters
        >>> d.getMSXParametersIndex('k1')                   # index of 'k1'
        >>> d.getMSXParametersIndex('k1', 'k3', 'kDOC1')    # specific set
        >>> d.getMSXParametersIndex(['k1', 'k3'])           # list/iterable

        See also getMSXParametersCount, getMSXParametersIndex,
                      getMSXParametersTanksValue, getMSXParametersPipesValue.
        """

        if not names:  # no args → all names
            names_to_lookup = self.getMSXParametersNameID()
        elif len(names) == 1 and isinstance(names[0], (list, tuple, set)):
            names_to_lookup = names[0]  # iterable passed
        else:
            names_to_lookup = names  # regular *args

        MSX_PARAMETER = self.ToolkitConstants.MSX_PARAMETER
        indices = []
        for name in names_to_lookup:
            try:
                idx = self.msx.MSXgetindex(MSX_PARAMETER, name)
            except Exception as err:
                raise ValueError(f"Unknown parameter name '{name}'") from err
            indices.append(idx)

        return indices

    def getMSXSpeciesIndex(self, *names):
        """
        Return the MSX index (1-based) of one or more species.

        Parameters
        ----------
        *names : str | iterable[str], optional
            Species IDs (names) to look up.

            • **No arguments** – return indices for *all* species.
            • **One iterable** – its elements are treated as the list of names.
            • **Several strings** – those specific species names.

        Returns
        -------
        list[int]
            Indices in the same order the names were requested.

        Setup:
               d = epanet('Net3-NH2CL.inp')
               d.loadMSXFile('Net3-NH2CL.msx')
        Examples:
        --------
        >>> d.getMSXSpeciesIndex()                     # all species
        >>> d.getMSXSpeciesIndex('NH3')                 # index of Na
        >>> d.getMSXSpeciesIndex('NH2CL', 'NH3', 'H')    # CL2, Nb, Na
        >>> d.getMSXSpeciesIndex(['NH3', 'TOC'])        # iterable form

        See also getMSXSpeciesUnits, getMSXSpeciesCount, getMSXSpeciesConcentration,
                      getMSXSpeciesType, getMSXSpeciesNameID, getMSXSpeciesRTOL,
                      getMSXSpeciesATOL.
        """
        total_species = self.getMSXSpeciesCount()

        if not names:  # no args → all species
            names_to_lookup = self.getMSXSpeciesNameID()
        elif len(names) == 1 and isinstance(names[0], (list, tuple, set)):
            names_to_lookup = names[0]  # an iterable was passed
        else:
            names_to_lookup = names  # regular *args

        MSX_SPECIES = self.ToolkitConstants.MSX_SPECIES
        indices = []
        for name in names_to_lookup:
            try:
                idx = self.msx.MSXgetindex(MSX_SPECIES, name)
            except Exception as err:
                raise ValueError(f"Unknown species name '{name}'") from err
            indices.append(idx)

        return indices

    def getMSXPatternsIndex(self, *names):
        """
        Return the MSX index (1-based) of one or more patterns.

        Parameters
        ----------
        *names : str | iterable[str], optional
            Pattern names (IDs) to look up.
            • **No arguments** – indices of *all* patterns are returned.
            • **One iterable** – its elements are treated as the name list.
            • **Several strings** – those exact pattern names.

        Returns
        -------
        list[int]
            Pattern indices in the same order requested.

        Setup:
                d = epanet('Net3-NH2CL.inp')
                d.loadMSXFile('Net3-NH2CL.msx')
                d.addMSXPattern('P1', [1.0, 0.0, 1.0])
                d.addMSXPattern('P2', [0.0, 0.0, 2.0])
                d.addMSXPattern('P3', [0.0, 1.0, 2.0])
                d.addMSXPattern('P4', [1.0, 1.0, 2.0])

        Examples:
        --------
        >>> d.getMSXPatternsIndex()                     # all patterns
        >>> d.getMSXPatternsIndex('P1')                 # index of 'P1'
        >>> d.getMSXPatternsIndex('P1', 'P2', 'P3')     # specific set
        >>> d.getMSXPatternsIndex(['P1', 'P3'])         # iterable form

        See also getMSXPattern, getMSXPatternsNameID, getMSXPatternsLengths,
                      setMSXPattern, setMSXPatternMatrix, setMSXPatternValue.
        """
        total_patterns = self.getMSXPatternsCount()

        if not names:  # no args → all
            names_to_lookup = self.getMSXPatternsNameID()
        elif len(names) == 1 and isinstance(names[0], (list, tuple, set)):
            names_to_lookup = names[0]  # iterable passed
        else:
            names_to_lookup = names  # regular *args

        MSX_PATTERN = self.ToolkitConstants.MSX_PATTERN
        indices = []
        for name in names_to_lookup:
            try:
                idx = self.msx.MSXgetindex(MSX_PATTERN, name)
            except Exception as err:
                raise ValueError(f"Unknown pattern name '{name}'") from err
            indices.append(idx)

        return indices

    def getMSXConstantsIndex(self, *names):
        """
        Return the MSX indices (1-based) of one or more constants.

        Parameters
        ----------
        *names : str | iterable[str], optional
            Constant IDs to look up.
            • **No arguments** – return indices for *all* constants.
            • **One iterable** – its elements form the lookup list.
            • **Several strings** – those exact constant names.

        Returns
        -------
        list[int]
            Indices in the same order the names were requested.

        Setup:
            d = epanet('Net3-NH2CL.inp')
            d.loadMSXFile('Net3-NH2CL.msx')
        Examples:
        --------
        >>> d.getMSXConstantsIndex()             # all constants
        >>> d.getMSXConstantsIndex('S1')         # index of 'S1'
        >>> d.getMSXConstantsIndex('S1', 'S2')   # specific set
        >>> d.getMSXConstantsIndex(['S2', 'S1']) # iterable form

          See also getMSXConstantsCount, getMSXConstantsValue,
                      getMSXConstantsNameID.
        """

        if not names:  # no args → all
            names_to_lookup = self.getMSXConstantsNameID()
        elif len(names) == 1 and isinstance(names[0], (list, tuple, set)):
            names_to_lookup = names[0]  # iterable passed
        else:
            names_to_lookup = names  # regular *args

        MSX_CONSTANT = self.ToolkitConstants.MSX_CONSTANT
        indices = []
        for name in names_to_lookup:
            try:
                idx = self.msx.MSXgetindex(MSX_CONSTANT, name)
            except Exception as err:
                raise ValueError(f"Unknown constant name '{name}'") from err
            indices.append(idx)

        return indices

    def getMSXConstantsValue(self, *indices):
        """
        Return the value of one or more MSX constants, addressed by index.

        Parameters
        ----------
        *indices : int | iterable[int], optional
            1-based constant indices.
            • **No arguments**  → values for *all* constants.
            • **One iterable**  → its items are the index list.
            • **Several ints**  → those exact indices.

        Returns
        -------
        list[float]
            Constant values, in the same order requested.

        Setup:
            d = epanet('Net3-NH2CL.inp')
            d.loadMSXFile('Net3-NH2CL.msx')
        Examples:
        --------
        >>> d.getMSXConstantsValue()            # all constants
        >>> d.getMSXConstantsValue(1)           # constant 1
        >>> d.getMSXConstantsValue(1, 2)        # constants 1 and 2
        >>> d.getMSXConstantsValue([2, 1])   # iterable form

        See also setMSXConstantsValue, getMSXConstantsCount,
                      getMSXConstantsIndex, getMSXConstantsNameID
        """
        total = self.getMSXConstantsCount()

        if not indices:  # no args → all
            idx_list = range(1, total + 1)
        elif len(indices) == 1 and isinstance(indices[0], (list, tuple, set)):
            idx_list = indices[0]  # iterable passed
        else:
            idx_list = indices  # regular *args

        values = []
        for i in idx_list:
            if not 1 <= i <= total:
                raise IndexError(f"Constant index {i} is out of range 1…{total}")
            values.append(self.msx.MSXgetconstant(i))

        return values

    def getMSXParametersPipesValue(self):
        """ Retrieves the parameters pipes value.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.getMSXParametersPipesValue()

             See also setMSXParametersPipesValue, getMSXParametersTanksValue,
                      getMSXParametersCount, getMSXParametersIndex."""
        x = self.getLinkPipeCount()
        y = self.getMSXParametersCount()
        value = []
        for i in range(1, x + 1):
            value_row = []
            for j in range(1, y + 1):
                param = self.msx.MSXgetparameter(1, i, j)
                value_row.append(param)
            value.append(value_row)
        return value

    def getMSXParametersTanksValue(self):
        """ Retrieves the parameters tanks value.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               tankIndex = d.getNodeTankIndex()
               d.getMSXParametersTanksValue{tankIndex}  Retrieves the value of the first tank.

             See also setMSXParametersTanksValue, getMSXParametersCount,
                      getMSXParametersIndex, getMSXParametersPipesValue."""
        x = self.getNodeTankIndex()
        y = self.getMSXParametersCount()
        value = [None] * max(x)
        for i in x:
            value[i - 1] = []
            for j in range(y):
                param = self.msx.MSXgetparameter(0, i, j + 1)
                value[i - 1].append(param)

        return value

    def getMSXPatternsLengths(self, *indices):
        """
        Return the length (number of factors) of one or more MSX patterns.

        Parameters
        ----------
        *indices : int | iterable[int], optional
            1-based pattern indices.
            • **No arguments**  → return the length of *all* patterns.
            • **One iterable**  → its items are treated as the index list.
            • **Several ints**  → those exact pattern indices.

        Returns
        -------
        list[int]
            Pattern lengths in the same order requested.
        Setup:
            d = epanet('Net3-NH2CL.inp')
            d.loadMSXFile('Net3-NH2CL.msx')
            d.addMSXPattern('P1', [1.0, 0.0, 1.0])
            d.addMSXPattern('P2', [0.0, 0.0, 2.0])
            d.addMSXPattern('P3', [0.0, 1.0, 2.0])
            d.addMSXPattern('P4', [1.0, 1.0, 2.0])
        Examples:
        --------
        >>> d.getMSXPatternsLengths()           # all patterns
        >>> d.getMSXPatternsLengths(1)          # pattern 1
        >>> d.getMSXPatternsLengths(1, 2)       # patterns 1 and 2
        >>> d.getMSXPatternsLengths([2, 4])     # iterable form
        """
        total = self.getMSXPatternsCount()

        if not indices:  # no args → all
            idx_list = range(1, total + 1)
        elif len(indices) == 1 and isinstance(indices[0], (list, tuple, set)):
            idx_list = indices[0]  # iterable passed
        else:
            idx_list = indices  # regular *args

        lengths = []
        for i in idx_list:
            if not 1 <= i <= total:
                raise IndexError(f"Pattern index {i} is out of range 1…{total}")
            lengths.append(self.msx.MSXgetpatternlen(i))

        return lengths

    def getMSXPattern(self):
        """ Retrieves the time patterns.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.addMSXPattern('P1', [1.0 0.0 1.0])
               d.addMSXPattern('P2', [1.0 0.0 1.0])
               d.addMSXPattern('P3', [0.0 1.0 2.0])
               d.addMSXPattern('P4', [1.0 2.0 2.5])
               patterns = d.getMSXPattern()   Retrieves all the patterns.


             See also setMSXPattern, setMSXPatternMatrix, setMSXPatternValue,
                      getMSXPatternsIndex, getMSXPatternsNameID,."""
        z = self.getMSXPatternsCount()
        if z == 0:
            return
        val = self.getMSXPatternsLengths()
        y = val
        tmpmaxlen = max(y)
        value = [[0] * tmpmaxlen for _ in range(self.getMSXPatternsCount())]
        for i in range(1, self.getMSXPatternsCount() + 1):
            z = self.getMSXPatternsLengths([i])
            tmplength = z
            for j in range(1, tmplength[0] + 1):
                value[i - 1][j - 1] = self.msx.MSXgetpatternvalue(i, j)

            if tmplength[0] < tmpmaxlen:
                for j in range(tmplength[0] + 1, tmpmaxlen + 1):
                    value[i - 1][j - 1] = value[i - 1][j - tmplength[0] - 1]

        return value

    def getMSXSpeciesType(self, *indices):
        """
        Return the MSX *type* (bulk-flow, wall, etc.) of one or more species.

        Parameters
        ----------
        *indices : int | iterable[int], optional
            1-based species indices.
            • **No arguments**  → types for *all* species.
            • **One iterable**  → its items are treated as the index list.
            • **Several ints**  → those exact species indices.

        Returns
        -------
        list[int]
            Species-type codes in the same order requested.

        Setup:
            d = epanet('Net3-NH2CL.inp')
            d.loadMSXFile('Net3-NH2CL.msx')

        Examples:
        --------
        >>> d.getMSXSpeciesType()           # all species
        >>> d.getMSXSpeciesType(1)          # species 1
        >>> d.getMSXSpeciesType(5, 7)       # species 5 and 7
        >>> d.getMSXSpeciesType([2, 4, 6])  # iterable form

         See also getMSXSpeciesIndex, getMSXSpeciesCount, getMSXSpeciesConcentration,
                      getMSXSpeciesnameID, getMSXSpeciesUnits, getMSXSpeciesATOL,
                      getMSXSpeciesRTOL.
        """
        total = self.getMSXSpeciesCount()

        if not indices:  # no args  → all
            idx_list = range(1, total + 1)
        elif len(indices) == 1 and isinstance(indices[0], (list, tuple, set)):
            idx_list = indices[0]  # iterable passed
        else:
            idx_list = indices  # regular *args

        types = []
        for i in idx_list:
            if not 1 <= i <= total:
                raise IndexError(f"Species index {i} is out of range 1…{total}")
            # MSXgetspecies returns (speciesType, units, atol, rtol)
            species_info = self.msx.MSXgetspecies(i)
            types.append(species_info[0])

        return types

    def getMSXSpeciesUnits(self, *indices):
        """
        Return the units string for one or more MSX species.

        Parameters
        ----------
        *indices : int | iterable[int], optional
            1-based species indices.
            • **No arguments**  – return units for *all* species.
            • **One iterable**  – its elements are treated as the index list.
            • **Several ints**  – those exact species indices.

        Returns
        -------
        list[str]
            Units strings in the same order requested.

        Setup:
            d = epanet('Net3-NH2CL.inp')
            d.loadMSXFile('Net3-NH2CL.msx')

        Examples:
        --------
        >>> d.getMSXSpeciesUnits()             # all species
        >>> d.getMSXSpeciesUnits(1)            # species 1
        >>> d.getMSXSpeciesUnits(1, 16)        # species 1 and 16
        >>> d.getMSXSpeciesUnits([2, 4, 5])    # iterable form
        See also getMSXSpeciesIndex, getMSXSpeciesCount, getMSXSpeciesConcentration,
                      getMSXSpeciesType, getMSXSpeciesNameID, getMSXSpeciesATOL,
                      getMSXSpeciesRTOL.
        """
        total = self.getMSXSpeciesCount()

        if not indices:  # no args → all
            idx_list = range(1, total + 1)
        elif len(indices) == 1 and isinstance(indices[0], (list, tuple, set)):
            idx_list = indices[0]  # iterable passed
        else:
            idx_list = indices  # regular *args

        units = []
        for i in idx_list:
            if not 1 <= i <= total:
                raise IndexError(f"Species index {i} is out of range 1…{total}")
            # MSXgetspecies returns (type, units, atol, rtol)
            species_info = self.msx.MSXgetspecies(i)
            units.append(species_info[1])

        return units

    def getEquations(self):
        msxname = self.MSXTempFile
        Terms = {}
        Pipes = {}
        Tanks = {}
        with open(msxname, 'r') as f:

            sect = 0
            i = 1
            t = 1
            k = 1
            while True:
                tline = f.readline()
                if not tline:
                    break
                tline = tline.strip()
                if not tline:
                    continue
                tok = tline.split()[0]

                if not tok:
                    continue
                if tok[0] == ';':
                    continue

                if tok[0] == '[':

                    if tok[1:6].upper() == 'TERMS':
                        sect = 1
                        continue
                    elif tok[1:6].upper() == 'PIPE]':
                        sect = 2
                        continue
                    elif tok[1:6].upper() == 'TANK]':
                        sect = 3
                        continue
                    elif tok[1:6].upper() == '[END':
                        break
                    else:
                        sect = 0
                        continue
                if sect == 0:
                    continue

                elif sect == 1:
                    Terms[i] = tline
                    i = i + 1
                elif sect == 2:
                    Pipes[t] = tline
                    t = t + 1
                elif sect == 3:
                    Tanks[k] = tline
                    k = k + 1
            return Terms, Pipes, Tanks

    def getMSXEquationsTerms(self):
        """ Retrieves equation terms.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.getMSXEquationsTerms()

             See also getMSXEquationsPipes, getMSXEquationsTanks."""
        x, y, z = self.getEquations()
        x = list(x.values())
        return x

    def getMSXEquationsPipes(self):
        """ Retrieves equation for pipes.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.getMSXEquationsPipes()

             See also getMSXEquationsTerms, getMSXEquationsTanks."""
        x, y, z = self.getEquations()
        y = list(y.values())
        return y

    def getMSXEquationsTanks(self):
        """ Retrieves equation for tanks.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.getMSXEquationsTanks()

             See also getMSXEquationsTerms, getMSXEquationsPipes."""
        x, y, z = self.getEquations()
        z = list(z.values())
        return z

    def getMSXSources(self):
        value = []
        for i in range(1, self.getNodeCount() + 1):
            value_row = []
            for j in range(1, self.getMSXSpeciesCount() + 1):
                y = self.msx.MSXgetsource(i, j)
                value_row.append(y)
            value.append(value_row)
        return value

    def getMSXSourceType(self, *nodes):
        """
        Return the source-type code(s) for one or more nodes.

        Each MSX source is defined per (*node*, *species*).  The toolkit call
        ``MSXgetsource(node, species)`` returns a 4-tuple
        ``(type, level, pattern, _reserved)``; we keep only the first element
        (the *type* code).

        Parameters
        ----------
        *nodes : int | iterable[int], optional
            1-based node indices.
            • **No arguments**  → all nodes.
            • **One iterable**  → its items are treated as the node list.
            • **Several ints**  → those exact nodes.

        Returns
        -------
        list[list[int]]
            Outer list follows the order requested; inner list contains the source-
            type code for every species at that node (length = `getMSXSpeciesCount()`).

        Setup:
                d = epanet('Net3-NH2CL.inp')
                d.loadMSXFile('Net3-NH2CL.msx')
        Examples:
        --------
        >>> d.getMSXSourceType()            # all nodes
        >>> d.getMSXSourceType(1)           # node 1
        >>> d.getMSXSourceType(1, 2)        # nodes 1 and 2
        >>> d.getMSXSourceType([3, 5, 7])   # iterable form

        See also getMSXSources, getMSXSourceNodeNameID
                      getMSXSourceLevel, getMSXSourcePatternIndex.
        """
        total_nodes = self.getNodeCount()
        total_species = self.getMSXSpeciesCount()

        if not nodes:  # no args → all nodes
            node_list = range(1, total_nodes + 1)
        elif len(nodes) == 1 and isinstance(nodes[0], (list, tuple, set)):
            node_list = nodes[0]  # single iterable
        else:
            node_list = nodes  # regular *args

        source_types = []
        for n in node_list:
            if not 1 <= n <= total_nodes:
                raise IndexError(f"Node index {n} is out of range 1…{total_nodes}")

            row = [
                self.msx.MSXgetsource(n, s)[0]  # take only the *type* field
                for s in range(1, total_species + 1)
            ]
            source_types.append(row)

        return source_types

    def getMSXSourceLevel(self, *nodes):
        """
        Return the *level* value of one or more MSX sources.

        For every (node, species) pair the EPANET-MSX toolkit call
        ``MSXgetsource(node, species)`` returns a 4-tuple
        ``(type, level, pattern, _reserved)``.
        This helper extracts only **level** (index 1).

        Parameters
        ----------
        *nodes : int | iterable[int], optional
            1-based node indices.
            • **No arguments**  – all nodes.
            • **One iterable**  – its items are treated as the node list.
            • **Several ints**  – those exact node indices.

        Returns
        -------
        list[list[float]]
            Outer list follows the order requested; each inner list contains the
            *level* for every species at that node
            (length = `getMSXSpeciesCount()`).

        Setup:
            d = epanet('Net3-NH2CL.inp')
            d.loadMSXFile('Net3-NH2CL.msx')
        Examples:
        --------
        >>> d.getMSXSourceLevel()               # levels for all nodes
        >>> d.getMSXSourceLevel(1)              # node 1
        >>> d.getMSXSourceLevel(1, 5)           # nodes 1 and 5
        >>> d.getMSXSourceLevel([2, 4, 7])      # iterable form

        See also getMSXSources, getMSXSourceNodeNameID
                      getMSXSourceType, getMSXSourcePatternIndex.
        """
        total_nodes = self.getNodeCount()
        total_species = self.getMSXSpeciesCount()

        if not nodes:  # no args → all
            node_list = range(1, total_nodes + 1)
        elif len(nodes) == 1 and isinstance(nodes[0], (list, tuple, set)):
            node_list = nodes[0]  # single iterable
        else:
            node_list = nodes  # regular *args

        levels = []
        for n in node_list:
            if not 1 <= n <= total_nodes:
                raise IndexError(f"Node index {n} is out of range 1…{total_nodes}")

            row = [
                self.msx.MSXgetsource(n, s)[1]  # take only *level*
                for s in range(1, total_species + 1)
            ]
            levels.append(row)

        return levels

    def getMSXSourcePatternIndex(self, *nodes):
        """
        Return the *pattern index* associated with the source at one or more nodes.

        For every (node, species) pair the EPANET-MSX call

            MSXgetsource(node, species)

        returns a 4-tuple **(type, level, patternIndex, _reserved)**.
        This helper extracts only **patternIndex** (element 2).

        Parameters
        ----------
        *nodes : int | iterable[int], optional
            1-based node indices.
            • **No arguments**  → pattern indices for *all* nodes.
            • **One iterable**  → its elements are the node list.
            • **Several ints**  → those exact nodes.

        Returns
        -------
        list[list[int]]
            Outer list follows the order requested; each inner list contains the
            pattern index for every species at that node
            (length = ``getMSXSpeciesCount()``).

        Setup:
            d = epanet('Net3-NH2CL.inp')
            d.loadMSXFile('Net3-NH2CL.msx')
        Examples:
        --------
        >>> d.getMSXSourcePatternIndex()              # every node
        >>> d.getMSXSourcePatternIndex(1)             # node 1
        >>> d.getMSXSourcePatternIndex(1, 5)          # nodes 1 and 5
        >>> d.getMSXSourcePatternIndex([2, 4, 7])     # iterable form
        
        See also getMSXSources, getMSXSourceNodeNameID
                      getMSXSourceType, getMSXSourceLevel.
        """
        total_nodes = self.getNodeCount()
        total_species = self.getMSXSpeciesCount()

        if not nodes:  # no args  → all
            node_list = range(1, total_nodes + 1)
        elif len(nodes) == 1 and isinstance(nodes[0], (list, tuple, set)):
            node_list = nodes[0]  # iterable passed
        else:
            node_list = nodes  # regular *args

        pattern_indices = []
        for n in node_list:
            if not 1 <= n <= total_nodes:
                raise IndexError(f"Node index {n} is out of range 1…{total_nodes}")

            row = [
                self.msx.MSXgetsource(n, s)[2]  # take only patternIndex
                for s in range(1, total_species + 1)
            ]
            pattern_indices.append(row)

        return pattern_indices

    def getMSXLinkInitqualValue(self, *links):
        """
        Return the initial-quality value for one or more links.

        Parameters
        ----------
        *links : int | iterable[int], optional
            1-based link indices.
            • **No arguments**  → values for *all* links.
            • **One iterable**  → its items are treated as the index list.
            • **Several ints**  → those exact link indices.

        Returns
        -------
        list[list[float]]
            Outer list follows the order requested; each inner list contains the
            initial-quality value for every species at that link
            (length = ``getMSXSpeciesCount()``).

        Setup:
             d = epanet('Net3-NH2CL.inp')
             d.loadMSXFile('Net3-NH2CL.msx')

        Examples:
        --------
        >>> d.getMSXLinkInitqualValue()             # every link
        >>> d.getMSXLinkInitqualValue(1)            # link 1
        >>> d.getMSXLinkInitqualValue(1, 3)         # links 1 and 3
        >>> d.getMSXLinkInitqualValue([2, 5, 7])    # iterable form

        See also setMSXLinkInitqualValue
        """
        total_links = self.getLinkCount()
        total_species = self.getMSXSpeciesCount()

        if not links:  # no args → all links
            link_list = range(1, total_links + 1)
        elif len(links) == 1 and isinstance(links[0], (list, tuple, set)):
            link_list = links[0]  # iterable passed
        else:
            link_list = links  # regular *args

        values = []
        for l in link_list:
            if not 1 <= l <= total_links:
                raise IndexError(f"Link index {l} is out of range 1…{total_links}")

            row = [
                self.msx.MSXgetinitqual(1, l, s)  # 1 = link flag
                for s in range(1, total_species + 1)
            ]
            values.append(row)

        return values

    def getMSXNodeInitqualValue(self, *nodes):
        """
        Return the initial-quality values for one or more nodes.

        Parameters
        ----------
        *nodes : int or iterable of int, optional
            1-based node indices.
            • No arguments  → all nodes.
            • One iterable  → the iterable’s contents are the node list.
            • Several ints  → those specific nodes.

        Returns
        -------
        list[list[float]]
            Outer list is in the same order requested; each inner list
            contains the species-quality values for that node.

        Setup:
            d = epanet('Net3-NH2CL.inp')
            d.loadMSXFile('Net3-NH2CL.msx')
        Examples:
        --------
        >>> d.getMSXNodeInitqualValue()          # all nodes
        >>> d.getMSXNodeInitqualValue(1)         # node 1
        >>> d.getMSXNodeInitqualValue(1, 3, 7)   # nodes 1, 3, 7
        >>> d.getMSXNodeInitqualValue([2, 5])    # nodes 2 and 5

        See also setMSXNodeInitqualValue.
        """
        total_nodes = self.getNodeCount()
        total_species = self.getMSXSpeciesCount()

        if not nodes:  # no args  → all nodes
            indices = range(1, total_nodes + 1)
        elif len(nodes) == 1 and isinstance(nodes[0], (list, tuple, set)):
            indices = nodes[0]  # single iterable given
        else:
            indices = nodes  # regular *args

        values = []
        for n in indices:
            if not 1 <= n <= total_nodes:
                raise IndexError(f"Node index {n} is out of range 1…{total_nodes}")

            row = [
                self.msx.MSXgetinitqual(0, n, s)
                for s in range(1, total_species + 1)
            ]
            values.append(row)

        return values

    def getMSXSpeciesATOL(self):
        """ Retrieves the species' absolute tolerance.

             Example:
               d = epanet('net3-bio.inp')
               d.loadMSXFile('net3-bio.msx')
               d.getMSXSpeciesATOL()

             See also getMSXSpeciesIndex, getMSXSpeciesCount, getMSXSpeciesConcentration,
                      getMSXSpeciesType, getMSXSpeciesNameID, getMSXSpeciesUnits,
                      getMSXSpeciesRTOL."""
        value = []
        for i in range(1, self.getMSXSpeciesCount() + 1):
            Atol = []
            value.append(self.msx.MSXgetspecies(i))
            Atol.append([item[2] for item in value])
        return Atol[0]

    def getMSXSpeciesRTOL(self):
        """ Retrieves the species' relative accuracy level.

             Example:
               d = epanet('net3-bio.inp')
               d.loadMSXFile('net3-bio.msx')
               d.getMSXSpeciesRTOL()

             See also getMSXSpeciesIndex, getMSXSpeciesCount, getMSXSpeciesConcentration,
                      getMSXSpeciesType, getMSXSpeciesNameID, getMSXSpeciesUnits,
                      getMSXSpeciesATOL."""
        value = []
        for i in range(1, self.getMSXSpeciesCount() + 1):
            Rtol = []
            value.append(self.msx.MSXgetspecies(i))
            Rtol.append([item[3] for item in value])
        return Rtol[0]

    def getMSXSpeciesConcentration(self, type, index, species):
        """ Returns the node/link concentration for specific specie.

             type options:
                    node = 0
                    link = 1

             Example:
               d = epanet('net2-cl2.inp');
               d.loadMSXFile('net2-cl2.msx');
               d.getMSXComputedQualitySpecie('CL2')
               speciesIndex = d.getMSXSpeciesIndex('CL2')
               d.getMSXSpeciesConcentration(0, 1, spIndex)  Retrieves the CL2 concentration of the first node.
               d.getMSXSpeciesConcentration(1, 1, spIndex)  Retrieves the CL2 concentration of the first link.

             See also getMSXSpeciesIndex, getMSXSpeciesNameID,
                      getMSXSpeciesCount, getMSXSpeciesType,
                      getMSXSpeciesUnits, getMSXSpeciesATOL,
                      getMSXSpeciesRTOL."""
        return self.msx.MSXgetqual(type, index, species)

    def getMSXSourceNodeNameID(self):
        """ Retrieves the sources node ID.

             Example:
               d = epanet('net2-cl2.inp');
               d.loadMSXFile('net2-cl2.msx');
               d.getMSXSourceNodeNameID         Retrieves all the source node IDs.



             See also getMSXSources, getMSXSourceType
                      getMSXSourceLevel, getMSXSourcePatternIndex."""
        nodes = []
        for i in range(1, self.getNodeCount() + 1):
            source = []
            value = []
            flag = 0
            value_row = []
            for j in range(1, self.getMSXSpeciesCount() + 1):
                y = self.msx.MSXgetsource(i, j)
                value_row.append(y)
                value.append(value_row)
            for k in value:
                source.append([item[0] for item in k])
            for sublist in source:
                for item in sublist:
                    if item != 'NOSOURCE':
                        flag = 1
                        break
            if flag == 1:
                nodes.append(i)
        return nodes

    def changeMSXOptions(self, param, change):
        options_section = 'options_section.msx'
        self.saveMSXFile(options_section)

        with open(options_section, 'r+') as f:
            lines = f.readlines()
            options_index = -1  # Default to -1 in case the [OPTIONS] section does not exist
            flag = 0
            for i, line in enumerate(lines):
                if line.strip() == '[OPTIONS]':
                    options_index = i
                elif line.strip().startswith(param):
                    lines[i] = param + "\t" + str(change) + "\n"
                    flag = 1
            if flag == 0 and options_index != -1:
                lines.insert(options_index + 1, param + "\t" + str(change) + "\n")
            f.seek(0)
            f.writelines(lines)
            f.truncate()

        self.msx.MSXclose()
        copyfile(options_section, self.MSXTempFile)
        try:
            os.remove(options_section)
        except:
            pass
        self.loadMSXEPANETFile(self.MSXTempFile)

    def setMSXAreaUnitsCM2(self):
        """  Sets the area units to square centimeters.

             The default is FT2.

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXAreaUnits()
              d.setMSXAreaUnitsCM2()
              d.getMSXAreaUnits()

             See also setMSXAreaUnitsFT2, setMSXAreaUnitsM2."""
        self.changeMSXOptions("AREA_UNITS", "CM2")

    def setMSXAreaUnitsFT2(self):
        """ Sets the area units to square feet.

             The default is FT2.

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXAreaUnits()
              d.setMSXAreaUnitsFT2()
              d.getMSXAreaUnits()

             See also setMSXAreaUnitsM2, setMSXAreaUnitsCM2."""
        self.changeMSXOptions("AREA_UNITS", "FT2")

    def setMSXAreaUnitsM2(self):
        """ Sets the area units to square meters.

             The default is FT2.

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXAreaUnits()
              d.setMSXAreaUnitsM2()
              d.getMSXAreaUnits()

             See also setMSXAreaUnitsFT2, setMSXAreaUnitsCM2."""
        self.changeMSXOptions("AREA_UNITS", "M2")

    def setMSXAtol(self, value):
        """ Sets the absolute tolerance used to determine when two concentration levels of a
             species are the same.

             If no ATOL option is specified then it defaults to 0.01
             (regardless of species concentration units).

             Example:
              d = epanet('net2-cl2.inp');
              d.loadMSXFile('net2-cl2.msx');
              d.getMSXAtol()
              d.setMSXAtol(2e-3);
              d.getMSXAtol()

            % See also setMSXRtol."""
        self.changeMSXOptions("ATOL", value)

    def setMSXRtol(self, value):
        """Sets the relative accuracy level on a species’ concentration
             used to adjust time steps in the RK5 and ROS2 integration methods.

             If no RTOL option is specified then it defaults to 0.001.

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXRtol()
              d.setMSXRtol(2e-3)
              d.getMSXRtol()

             See also setMSXAtol."""
        self.changeMSXOptions("RTOL", value)

    def setMSXCompilerGC(self):
        """  Sets chemistry function compiler code to GC.

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2-vc.msx')
              d.getMSXCompiler()
              d.setMSXCompilerGC()
              d.getMSXCompiler()

             See also setMSXCompilerNONE, setMSXCompilerVC."""
        self.changeMSXOptions("COMPILER", "GC")

    def setMSXCompilerVC(self):
        """ Sets chemistry function compiler code to VC.

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXCompiler()
              d.setMSXCompilerVC()
              d.getMSXCompiler()

             See also setMSXCompilerNONE, setMSXCompilerGC."""
        self.changeMSXOptions("COMPILER", "VC")

    def setMSXCompilerNONE(self):
        """ Sets chemistry function compiler code to NONE.

             Example:
              d = epanet('net2-cl2.inp');
              d.loadMSXFile('net2-cl2.msx');
              d.getMSXCompiler()
              d.setMSXCompilerNONE()
              d.getMSXCompiler()

             See also setMSXCompilerVC, setMSXCompilerGC."""
        self.changeMSXOptions("COMPILER", "NONE")

    def setMSXCouplingFULL(self):
        """  Sets coupling to FULL.

             COUPLING determines to what degree the solution of any algebraic
             equilibrium equations is coupled to the integration of the reaction
             rate equations. With FULL coupling the updating is done whenever a
             new set of values for the rate-dependent variables in the reaction
             rate expressions is computed. The default is FULL coupling.

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXCoupling()
              d.setMSXCouplingFULL()
              d.getMSXCoupling()

             See also setMSXCouplingNONE."""
        self.changeMSXOptions("COUPLING", "FULL")

    def setMSXCouplingNONE(self):
        """ Sets coupling to NONE.

             COUPLING determines to what degree the solution of any algebraic
             equilibrium equations is coupled to the integration of the reaction
             rate equations. If coupling is NONE then the solution to the
             algebraic equations is only updated at the end of each
             integration time step. The default is FULL coupling.

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXCoupling()
              d.setMSXCouplingFULL()
              d.getMSXCoupling()

             See also setMSXCouplingFULL."""
        self.changeMSXOptions("COUPLING", "NONE")

    def setMSXRateUnitsDAY(self):
        """  Sets the rate units to days.

             The default units are hours (HR)

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXRateUnits()
              d.setMSXRateUnitsDAY()
              d.getMSXRateUnits()

             See also setMSXRateUnitsSEC, setMSXRateUnitsMIN
                      setMSXRateUnitsHR."""
        self.changeMSXOptions("RATE_UNITS", "DAY")

    def setMSXRateUnitsHR(self):
        """  Sets the rate units to hours.

             The default units are hours (HR)

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXRateUnits()
              d.setMSXRateUnitsHR()
              d.getMSXRateUnits()

             See also setMSXRateUnitsSEC, setMSXRateUnitsMIN
                      setMSXRateUnitsDAY."""
        self.changeMSXOptions("RATE_UNITS", "HR")

    def setMSXRateUnitsMIN(self):
        """ Sets the rate units to minutes.

             The default units are hours (HR)

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXRateUnits()
              d.setMSXRateUnitsMIN()
              d.getMSXRateUnits()

             See also setMSXRateUnitsSEC, setMSXRateUnitsHR,
                      setMSXRateUnitsDAY."""
        self.changeMSXOptions("RATE_UNITS", "MIN")

    def setMSXRateUnitsSEC(self):
        """ Sets the rate units to seconds.

             The default units are hours (HR)

              Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXRateUnits()
              d.setMSXRateUnitsSEC()
              d.getMSXRateUnits()

             See also setMSXRateUnitsMIN, setMSXRateUnitsHR,
                      setMSXRateUnitsDAY."""
        self.changeMSXOptions("RATE_UNITS", "SEC")

    def setMSXSolverEUL(self):
        """ Sets the numerical integration method to solve the reaction
             system to standard Euler integrator (EUL).

             The default solver is EUL.

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXSolver()
              d.setMSXSolverEUL()
              d.getMSXSolver()

             See also setMSXSolverRK5, setMSXSolverROS2."""
        self.changeMSXOptions("SOLVER", "EUL")

    def setMSXSolverRK5(self):
        """ Sets the numerical integration method to solve the reaction
             system to Runge-Kutta 5th order integrator (RK5).

             The default solver is EUL.

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXSolver()
              d.setMSXSolverRK5()
              d.getMSXSolver()

            % See also setMSXSolverEUL, setMSXSolverROS2."""
        self.changeMSXOptions("SOLVER", "RK5")

    def setMSXSolverROS2(self):
        """  Sets the numerical integration method to solve the reaction
             system to 2nd order Rosenbrock integrator (ROS2).

             The default solver is EUL.

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXSolver()
              d.setMSXSolverROS2()
              d.getMSXSolver()

             See also setMSXSolverEUL, setMSXSolverRK5."""
        self.changeMSXOptions("SOLVER", "ROS2")

    def setMSXTimeStep(self, value):
        """ Sets the time step.

             The default timestep is 300 seconds (5 minutes).

             Example:
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              d.getMSXTimeStep()
              d.setMSXTimeStep(3600)
              d.getMSXTimeStep()

             See also getMSXTimeStep."""
        self.changeMSXOptions("TIMESTEP", value)

    def setMSXPatternValue(self, index, patternTimeStep, patternFactor):
        """ Sets the pattern factor for an index for a specific time step.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.addMSXPattern('P1', [2.0 2.0 2.0 2.0])
               d.getMSXPatternValue(1,1)
               d.setMSXPatternValue(1,1,3.0) Sets the first timestep of the first pattern to 3.0.
               d.getMSXPatternValue(1,1)

             See also getMSXPatternValue, getMSXPattern, addMSXPattern."""
        self.msx.MSXsetpatternvalue(index, patternTimeStep, patternFactor)

    def setMSXPattern(self, index, patternVector):
        """ Sets the multiplier at a specific time period for a given pattern.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.addMSXPattern('Pl', [1.0 2.0 1.5 1.0])
               d.getMSXPattern()
               d.setMSXPattern(1, [1.0 0.0 3.0])
               d.getMSXPattern()

             See also getMSXPattern, addMSXPattern."""
        if not isinstance(index, int):
            index = self.getMSXPatternsIndex(index)
            index = index[0]
        nfactors = len(patternVector)
        self.msx.MSXsetpattern(index, patternVector, nfactors)

    def setMSXParametersTanksValue(self, NodeTankIndex, paramOrValues, value=None):
        """Assigns a value to one or multiple reaction parameters for a given tank within the pipe network.

        Example 1:
            d = epanet('net2-cl2.inp')
            d.loadMSXFile('net2-cl2.msx')
            x=d.getMSXParametersTanksValue()
            print(x[35])
            d.setMSXParametersTanksValue(36,[5,6])
            x=d.getMSXParametersTanksValue()
            print(x[35])
        Example 2:
            d = epanet('net2-cl2.inp')
            d.loadMSXFile('net2-cl2.msx')
            x = d.getMSXParametersTanksValue()
            print(x[35])
            d.setMSXParametersTanksValue(36, 2,20)
            x = d.getMSXParametersTanksValue()
            print(x[35])


        See also getMSXParametersTanksValue, setMSXParametersPipesValue,
                 getMSXParametersPipesValue, getMSXParametersCount,
                 getMSXParametersIndex.
        """
        if not NodeTankIndex in self.NodeTankIndex:
            warnings.warn("Invalid Tank Index")
            return

        if value is None:
            values = paramOrValues
            for i, val in enumerate(values):
                self.msx.MSXsetparameter(0, NodeTankIndex, i + 1, val)
        else:
            paramIndex = paramOrValues
            self.msx.MSXsetparameter(0, NodeTankIndex, paramIndex, value)

    def setMSXParametersPipesValue(self, pipeIndex, paramOrValues, value=None):
        """Assigns a value to one or multiple reaction parameters
        for a given pipe within the pipe network.
        Example 1:
               d = epanet('net2-cl2.inp');
               d.loadMSXFile('net2-cl2.msx');
               x = d.getMSXParametersPipesValue()
               print(x[0])
               d.setMSXParametersPipesValue(1, [1.5, 2])
               x = d.getMSXParametersPipesValue()
               print(x[0])
        Example 2:
               d = epanet('net2-cl2.inp');
               d.loadMSXFile('net2-cl2.msx');
               x = d.getMSXParametersPipesValue()
               print(x[0])
               d.setMSXParametersPipesValue(1, 2,5)
               x = d.getMSXParametersPipesValue()
               print(x[0])

        See also getMSXParametersPipesValue, setMSXParametersTanksValue,
                 getMSXParametersTanksValue, getMSXParametersCount,
                 getMSXParametersIndex.
        """
        if value is None:
            values = paramOrValues
            for i, val in enumerate(values):
                self.msx.MSXsetparameter(1, pipeIndex, i + 1, val)
        else:
            paramIndex = paramOrValues
            self.msx.MSXsetparameter(1, pipeIndex, paramIndex, value)

    def setMSXConstantsValue(self, value):
        """ Sets the values of constants.

             Example:
               d = epanet('net3-bio.inp')
               d.loadMSXFile('net3-bio.msx')
               d.getMSXConstantsValue()
               d.setMSXConstantsValue([1, 2, 3]) Set the values of the first three constants.
               d.getMSXConstantsValue()

             See also getMSXConstantsCount, getMSXConstantsIndex,
                      getMSXConstantsNameID."""
        for i in range(len(value)):
            self.msx.MSXsetconstant(i + 1, value[i])

    def addMSXPattern(self, *args):
        """ Adds new time pattern

            Example:
            d = epanet('net2-cl2.inp');
            d.loadMSXFile('net2-cl2.msx');
            print(d.getMSXPatternsNameID())
            mult = [0.5, 0.8, 1.2, 1.0, 0.7, 0.3]
            d.addMSXPattern('Pattern1', mult)
            print(d.getMSXPattern())
            print(d.getMSXPatternsNameID())

            See also getMSXPattern, setMSXPattern."""
        index = -1
        MSX_PATTERN = self.ToolkitConstants.MSX_PATTERN
        if len(args) == 1:

            self.msx.MSXaddpattern(args[0])
            index = self.msx.MSXgetindex(MSX_PATTERN, args[0])
        elif len(args) == 2:
            self.msx.MSXaddpattern(args[0])
            index = self.msx.MSXgetindex(MSX_PATTERN, args[0])
            self.setMSXPattern(index, args[1])
        return index

    def getMSXComputedQualitySpecie(self, species=None, nodes=1, links=1):
        """  Returns the node/link quality for specific specie.

             Example :
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               MSX_comp = d.getMSXComputedQualitySpecie(['CL2'])
               MSX_comp.NodeQuality  row: time, col: node index
               MSX_comp.LinkQuality  row: time, col: link index
               MSX_comp.Time

                See also getMSXComputedQualityNode, getMSXComputedQualityLink.
            """
        if not isinstance(species, list):
            species = [species]
        if self.getMSXSpeciesCount() == 0:
            return -1
        if species is None:
            species_index_name = self.getMSXSpeciesIndex()
        else:
            species_index_name = self.getMSXSpeciesIndex(species)

        node_count = self.getNodeCount()
        link_count = self.getLinkCount()
        specie_count = len(species_index_name)
        node_indices = list(range(1, node_count + 1))
        link_indices = list(range(1, link_count + 1))
        # Initialized quality and time
        msx_time_step = self.getMSXTimeStep()
        time_steps = int(self.getTimeSimulationDuration() / msx_time_step) + 1
        quality = 0
        lquality = 0
        if nodes is not None:
            quality = [np.zeros((time_steps, specie_count)) for _ in range(node_count)]
        if links is not None:
            lquality = [np.zeros((time_steps, specie_count)) for _ in range(link_count)]

        data = {
            'NodeQuality': quality,
            'LinkQuality': lquality,
        }
        time_smle = self.getTimeSimulationDuration()

        # Obtain a hydraulic solution
        self.solveMSXCompleteHydraulics()

        # Run a step-wise water quality analysis without saving results to file
        self.initializeMSXQualityAnalysis(0)

        # Retrieve species concentration at node
        k = 0
        for j_idx, j in enumerate(species_index_name, start=1):
            if nodes is not None:
                for i, nl in enumerate(node_indices, start=1):
                    data['NodeQuality'][i - 1][k, j_idx - 1] = self.getMSXNodeInitqualValue()[i - 1][j - 1]
            if links is not None:
                for i, nl in enumerate(link_indices, start=1):
                    data['LinkQuality'][i - 1][k, j_idx - 1] = self.getMSXLinkInitqualValue()[i - 1][j - 1]

        k = 1
        t = 0
        tleft = 1
        # Initialized data time with 0
        while tleft > 0 and time_smle != t:
            t, tleft = self.stepMSXQualityAnalysisTimeLeft()
            if t >= msx_time_step:
                for g, j in enumerate(species_index_name, start=1):
                    if nodes is not None:
                        for i, nl in enumerate(node_indices, start=1):
                            data['NodeQuality'][i - 1][k, g - 1] = self.getMSXSpeciesConcentration(0, nl, j)
                    if links is not None:
                        for i, nl in enumerate(link_indices, start=1):
                            data['LinkQuality'][i - 1][k, g - 1] = self.getMSXSpeciesConcentration(1, nl, j)
            k += 1

        value = EpytValues()
        value.NodeQuality, value.LinkQuality = {}, {}
        value.NodeQuality = data['NodeQuality']
        value.LinkQuality = data['LinkQuality']
        value.Time = [int(i * msx_time_step) for i in
                      range(int(self.getTimeSimulationDuration() / msx_time_step) + 1)]
        return value

    def getMSXComputedNodeQualitySpecie(self, node_indices, species_id):
        """  Returns the node quality for specific specie.

                     Example :
                       d = epanet('net2-cl2.inp')
                       d.loadMSXFile('net2-cl2.msx')
                       node_indices = [1,2,3]
                       MSX_comp = d.getMSXComputedNodeQualitySpecie(node_indices, 'CL2')
                       MSX_comp.NodeQuality  row: time, col: node index
                       MSX_comp.Time

                    Example wtih 2 species:
                        msx=d.getMSXComputedNodeQualitySpecie(x,['CL2',"H"])
                        print(msx["CL2"].NodeQuality)
                     See also getMSXComputedQualitySpecie, getMSXComputedLinkQualitySpecie."""
        value = {}  # Use a dictionary instead of a list
        counter = 0
        for specie in species_id:
            MSX_comp = self.getMSXComputedQualitySpecie(specie, nodes=1, links=None)
            MSX_comp_Node = MSX_comp.NodeQuality
            merged = []  # Reset merged list for each specie
            for i in node_indices:
                column = MSX_comp_Node[i]
                merged.append(column)
            # Create a new EpytValues object and populate its attributes
            new_value = EpytValues()
            new_value.NodeQuality = merged
            new_value.Time = MSX_comp.Time
            # Store the new EpytValues object in the dictionary with the specie number as the key
            value[specie] = new_value
            counter += 1
        if len(species_id) == 1:
            return value[species_id[0]]
        else:
            return value

    def getMSXComputedLinkQualitySpecie(self, node_indices, species_id):
        """ Returns the link quality for specific specie.

            Example :
              d = epanet('net2-cl2.inp')
              d.loadMSXFile('net2-cl2.msx')
              node_indices = [1,2,3,4]
              MSX_comp = d.getMSXComputedLinkQualitySpecie(node_indices, 'CL2')
              MSX_comp.LinkQuality  row: time, col: node index
              MSX_comp.Time

            Example wtih 2 species:
                    msx=d.getMSXComputedLinkQualitySpecie(x,['CL2',"H"])
                    print(msx.LinkQuality)
            See also getMSXComputedQualitySpecie, getMSXComputedNodeQualitySpecie."""
        value = {}  # Use a dictionary instead of a list
        counter = 0

        for specie in species_id:
            MSX_comp = self.getMSXComputedQualitySpecie(specie, nodes=None, links=1)
            MSX_comp_Link = MSX_comp.LinkQuality
            merged = []  # Reset merged list for each specie
            for i in node_indices:
                column = MSX_comp_Link[i]
                merged.append(column)
            # Create a new EpytValues object and populate its attributes
            new_value = EpytValues()
            new_value.LinkQuality = merged
            new_value.Time = MSX_comp.Time
            # Store the new EpytValues object in the dictionary with the specie number as the key
            value[specie] = new_value
            counter += 1

        if len(species_id) == 1:
            return value[species_id[0]]
        else:
            return value

    def getMSXComputedQualityNode(self, *args):
        """
        Returns the computed quality for nodes.
        Example:
            d = epanet('net2-cl2.inp')
            d.loadMSXFile('net2-cl2.msx')

            MSX_comp = d.getMSXComputedQualityNode()
            x = MSX_comp.Quality
            y = MSX_comp.Time
        """
        if self.getMSXSpeciesCount() == 0:
            return 0

        if args:
            if len(args) == 1:
                ss = args[0]
                uu = list(range(1, self.getMSXSpeciesCount() + 1))
            elif len(args) == 2:
                ss = args[0]
                uu = args[1]
        else:
            ss = list(range(1, self.getNodeCount() + 1))
            uu = list(range(1, self.getMSXSpeciesCount() + 1))
        self.solveMSXCompleteHydraulics()
        self.initializeMSXQualityAnalysis(0)

        time_steps = int(self.getTimeSimulationDuration() / self.getMSXTimeStep()) + 1

        quality_data = {node: np.zeros((time_steps, len(uu))) for node in ss}
        time_data = []

        k = 0
        t = 0
        tleft = 1
        # Initialize Quality Data for each node and species
        for nl in ss:
            for idx, j in enumerate(uu, start=1):
                try:
                    quality_data[nl][k, idx - 1] = self.getMSXSpeciesConcentration(0, nl, j)
                except IndexError:
                    raise ValueError(
                        'Wrong species index. Please check the functions getMSXSpeciesNameID, getMSXSpeciesCount.')
        k += 1
        time_data.append(0)
        # Run simulation steps and collect quality data
        simulation_duration = self.getTimeSimulationDuration()
        while tleft > 0 and t != simulation_duration:
            t, tleft = self.stepMSXQualityAnalysisTimeLeft()
            time_data.append(t)
            for nl in ss:
                for idx, j in enumerate(uu, start=1):
                    concentration = self.getMSXSpeciesConcentration(0, nl, j)
                    quality_data[nl][k, idx - 1] = concentration
            k += 1

        out = EpytValues()
        out.Quality = quality_data
        out.Time = np.array(time_data)
        return out

    def getMSXComputedQualityLink(self, *args):
        """
        Returns the computed quality for links.
        Example:
            d = epanet('net2-cl2.inp')
            d.loadMSXFile('net2-cl2.msx')

            MSX_comp = d.getMSXComputedQualityLink()
            x = MSX_comp.Quality
            y = MSX_comp.Time
        """
        if self.getMSXSpeciesCount() == 0:
            return 0

        if args:
            if len(args) == 1:
                ss = args[0]
                uu = list(range(1, self.getMSXSpeciesCount() + 1))
            elif len(args) == 2:
                ss = args[0]
                uu = args[1]
        else:
            ss = list(range(1, self.getLinkCount() + 1))
            uu = list(range(1, self.getMSXSpeciesCount() + 1))

        self.solveMSXCompleteHydraulics()
        self.initializeMSXQualityAnalysis(0)

        time_steps = int(self.getTimeSimulationDuration() / self.getMSXTimeStep()) + 1

        quality_data = {link: np.zeros((time_steps, len(uu))) for link in ss}
        time_data = []

        k = 0
        t = 0
        tleft = 1
        # Initialize Quality Data for each link and species
        for nl in ss:
            for idx, j in enumerate(uu, start=1):
                try:
                    quality_data[nl][k, idx - 1] = self.getMSXSpeciesConcentration(1, nl, j)
                except IndexError:
                    raise ValueError(
                        'Wrong species index. Please check the functions getMSXSpeciesNameID, getMSXSpeciesCount.')
        k += 1

        # Run simulation steps and collect quality data
        simulation_duration = self.getTimeSimulationDuration()
        while tleft > 0 and t != simulation_duration:
            t, tleft = self.stepMSXQualityAnalysisTimeLeft()
            time_data.append(t)
            for nl in ss:
                for idx, j in enumerate(uu, start=1):
                    concentration = self.getMSXSpeciesConcentration(1, nl, j)
                    quality_data[nl][k, idx - 1] = concentration
            k += 1

        out = EpytValues()
        out.Quality = quality_data
        out.Time = np.array(time_data)
        return out

    def setMSXLinkInitqualValue(self, value):
        """"
        Sets all links initial quality value.

            Example:
                linkIndex=0
                speciesIndex=0
                values = [[0] * linkIndex for _ in range(speciesIndex)]
                values=d.getMSXLinkInitqualValue()
                values[linkIndex][speciesIndex]=1500
                d.setMSXLinkInitqualValue(values)
                x=d.getMSXLinkInitqualValue()

        See also getMSXLinkInitqualValue, setMSXNodeInitqualValue.
        """
        for i in range(len(value)):
            for j in range(len(value[0])):
                self.msx.MSXsetinitqual(1, i + 1, j + 1, value[i][j])

    def setMSXSources(self, nodeID, speciesID, sourcetype, concentration, patID):
        """ Sets the attributes of an external source of a particular chemical species
             to a specific node of the pipe network.

             Example:
               d = epanet('net2-cl2.inp');
               d.loadMSXFile('net2-cl2.msx')
               srcs = d.getMSXSources()
               d.addMSXPattern('PatAsIII',[2, .3, .4, 6, 5, 2, 4])
               d.setMSXSources(d.NodeNameID{2}, d.MSXSpeciesNameID{1}, Setpoint', 0.5, 'PatAsIII') % Sets the second node as setpoint.
               d.setMSXSources(d.getNodeNameID(2), d.getMSXSpeciesNameID([1]),'FLOWPACED', 0.5, 'PatAsIII')
               srcs = d.getMSXSources()

             See also getMSXSources, getMSXSourceNodeNameID, getMSXSourceType
                      getMSXSourceLevel, getMSXSourcePatternIndex."""
        MSXTYPESOURCE = {'NOSOURCE', 'CONCEN', 'MASS', 'SETPOINT', 'FLOWPACED'}

        if not isinstance(speciesID, list):
            speciesID = [speciesID]
        node = self.getNodeIndex(nodeID)
        species = self.getMSXSpeciesIndex(speciesID)
        species = species[0]
        pat = self.getMSXPatternsIndex(patID)
        pat = pat[0]
        sourcetype = sourcetype.upper()
        if sourcetype == 'NOSOURCE':
            type = -1
        elif sourcetype == 'CONCEN':
            type = 0
        elif sourcetype == 'MASS':
            type = 1
        elif sourcetype == 'SETPOINT':
            type = 2
        elif sourcetype == 'FLOWPACED':
            type = 3

        self.msx.MSXsetsource(node, species, type, concentration, pat)

    def setMSXNodeInitqualValue(self, value):
        """
        Sets all nodes initial quality value.

            Example:
                linkIndex=0
                speciesIndex=0
                values = [[0] * linkIndex for _ in range(speciesIndex)]
                values=d.getMSXNodeInitqualValue()
                values[linkIndex][speciesIndex]=1500
                d.setMSXNodeInitqualValue(values)
                x=d.getMSXNodeInitqualValue()
         See also getMSXNodeInitqualValue, setMSXLinkInitqualValue.
         """
        for i in range(len(value)):
            for j in range(len(value[0])):
                self.msx.MSXsetinitqual(0, i + 1, j + 1, value[i][j])

    def initializeMSXWrite(self):
        value = EpytValues()

        # Initialize strs
        string_attrs = [
            "FILENAME", "TITLE", "AREA_UNITS", "RATE_UNITS",
            "SOLVER", "COMPILER", "COUPLING"
        ]

        for attr in string_attrs:
            setattr(value, attr, "")

        # Initialize dicts
        dict_attrs = [
            "TIMESTEP", "RTOL", "ATOL", "SPECIES", "COEFFICIENTS",
            "TERMS", "PIPES", "TANKS", "SOURCES", "GLOBAL",
            "QUALITY", "PARAMETERS", "PATERNS"
        ]

        for attr in dict_attrs:
            setattr(value, attr, {})

        return value

    def writeMSXFile(self, msx):
        """
        Write a new MSX file
                Example for wirteMSXFile:
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
                    d.unload()
                 """
        filename = msx.FILENAME
        with open(filename, 'w') as f:
            # Writing the TITLE section
            f.write("[TITLE]\n")
            f.write(msx.TITLE)

            # Writing the OPTIONS section
            options = {
                "AREA_UNITS": msx.AREA_UNITS,
                "RATE_UNITS": msx.RATE_UNITS,
                "SOLVER": msx.SOLVER,
                "TIMESTEP": msx.TIMESTEP,
                "COMPILER": msx.COMPILER,
                "COUPLING": msx.COUPLING,
                "RTOL": msx.RTOL,
                "ATOL": msx.ATOL
            }
            f.write("\n\n[OPTIONS]")
            for key, value in options.items():
                f.write("\n{}\t{}".format(key, value))
            # Sections with list data
            sections = {
                "[SPECIES]": msx.SPECIES,
                "[COEFFICIENTS]": msx.COEFFICIENTS,
                "[TERMS]": msx.TERMS,
                "[PIPES]": msx.PIPES,
                "[TANKS]": msx.TANKS,
                "[SOURCES]": msx.SOURCES,
                "[QUALITY]": msx.QUALITY,
                "[GLOBAL]": msx.GLOBAL,
                "[PARAMETERS]": msx.PARAMETERS,
                "[PATTERNS]": msx.PATERNS
            }
            for section, items in sections.items():
                f.write("\n\n{}".format(section))
                for item in items:
                    f.write("\n{}".format(item))

            f.write('\n\n[REPORT]\n')
            f.write('NODES ALL\n')
            f.write('LINKS ALL\n')

    def setMSXPatternMatrix(self, pattern_matrix):
        """Sets all of the multiplier factors for all patterns

            Example:
                inpname = os.path.join(os.getcwd(), 'epyt', 'networks','msx-examples', 'net2-cl2.inp')
                msxname = os.path.join(os.getcwd(), 'epyt', 'networks','msx-examples', 'net2-cl2.msx')
                d = epanet(inpname)
                d.loadMSXFile(msxname)
                d.addMSXPattern('1',[])
                d.setMSXPatternMatrix([.1,.2,.5,.2,1,.9])
                print(d.getMSXPattern())
        """
        if not all(isinstance(i, list) for i in pattern_matrix):
            pattern_matrix = [pattern_matrix]

        pattern_matrix = [[float(value) for value in row] for row in pattern_matrix]
        nfactors = len(pattern_matrix[0])
        for i, pattern in enumerate(pattern_matrix):
            self.msx.MSXsetpattern(i + 1, pattern, nfactors)

    def getAllAttributes(self, obj):
        """Get all attributes of a given Python object

            Example:
                filename = 'Net1.inp' #you can also try 'net2-cl2.inp', 'Net3.inp', etc.
                d = epanet(filename)
                Q = d.getComputedQualityTimeSeries()
                attr = d.getAllAttributes(Q)
                print(attr) #Will print Time, LinkQuality , NodeQuality and MassFlowRate
            """
        attributes = []

        def recurse_attrs(obj):
            for k, v in obj.__dict__.items():
                attributes.append((k, v))
                if hasattr(v, '__dict__'):
                    recurse_attrs(v)

        recurse_attrs(obj)
        return attributes

    def getMethods(self):
        """Returns all methods of epanet

            Example:
                filename = 'L-TOWN.inp'
                d=epanet(filename)
                methods = G.getmethods()
                print(methods)
        """
        methods_dir = [method for method in dir(self) if
                       callable(getattr(self, method)) and not method.startswith('__') and not method.startswith('_')]
        return methods_dir

    def plotMSXSpeciesNodeConcentration(self, *args):
        """Plots concentration of species for nodes over time.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.plotMSXSpeciesNodeConcentration([1],[1])  # Plots first node's concentration of the first specie over time.

             Example 2:
                d = epanet('net2-cl2.inp')
                d.loadMSXFile('net2-cl2.msx')
                x = [1,2,3,4,5]
                d.plotMSXSpeciesNodeConcentration(x,1)  # Plots concentration of nodes 1 to 5 for the first specie over time.
             See also plotMSXSpeciesLinkConcentration.
        """
        node = args[0]
        specie = args[1]
        if not isinstance(node, list):
            node = [node]
        if not isinstance(specie, list):
            specie = [specie]
        s = self.getMSXComputedQualityNode(node, specie)
        nodesID = self.getNodeNameID()
        SpeciesNameID = self.getMSXSpeciesNameID()

        for nd, l in enumerate(node):
            nodeID = nodesID[l - 1]
            plt.figure(figsize=(10, 6))
            plt.title(f'NODE {nodeID}')
            for i in specie:
                specie_index = specie.index(i)
                quality_data = np.array(s.Quality[l])[:, specie_index]
                time_data = np.array(s.Time)
                min_length = min(len(time_data), len(quality_data))  # Calculate the minimum length
                plt.plot(time_data[:min_length], quality_data[:min_length], label=SpeciesNameID[i - 1])

            plt.xlabel('Time(s)')
            plt.ylabel('Quantity')
            plt.legend()
            plt.show()

    def plotMSXSpeciesLinkConcentration(self, *args):
        """% Plots concentration of species for links over time.

             Example:
               d = epanet('net2-cl2.inp')
               d.loadMSXFile('net2-cl2.msx')
               d.plotMSXSpeciesLinkConcentration(5, 2)    Plots node index 5 concentration of the second specie over time.
               d.plotMSXSpeciesLinkConcentration(1, 1)    Plots first node's concentration of the first specie over time.

                Example 2:
                d = epanet('net2-cl2.inp')
                d.loadMSXFile('net2-cl2.msx')
                x = [1,2,3,4,5]
                d.plotMSXSpeciesLinkConcentration(x,1)  # Plots concentration of links 1 to 5 for the first specie over time.
            % See also plotMSXSpeciesNodeConcentration."""
        link = args[0]
        specie = args[1]
        if not isinstance(link, list):
            link = [link]
        if not isinstance(specie, list):
            specie = [specie]
        s = self.getMSXComputedQualityLink(link, specie)
        linksID = self.getLinkNameID()
        SpeciesNameID = self.getMSXSpeciesNameID()

        for nd, l in enumerate(link):
            linkID = linksID[l - 1]
            plt.figure(figsize=(10, 6))
            plt.title(f'LINK {linkID}')
            for i in specie:
                specie_index = specie.index(i)
                quality_data = np.array(s.Quality[l])[:, specie_index]
                time_data = np.array(s.Time)
                min_length = min(len(time_data), len(quality_data))  # Calculate the minimum length
                plt.plot(time_data[:min_length], quality_data[:min_length], label=SpeciesNameID[i - 1])

            plt.xlabel('Time(s)')
            plt.ylabel('Quantity')
            plt.legend()
            plt.show()

    def exportMSXts(self, results, output_file='computedtoexcel.xlsx', selected_nodes=None,
                        selected_species=None,
                        header=True):
        """
        Exports multi-species water-quality time-series results (from an EPANET-MSX
    simulation) to an Excel workbook—one sheet per species.

    Parameters:
    ----------
        results : obj
            A results object returned by `getMSXComputedQualityNode`.
            It must expose ``Time`` (1-D array-like) and ``Quality``
        output_file : str, default ``"computedtoexcel.xlsx"``
            Name (or path) for the Excel file to create. “.xlsx” is appended
            automatically when omitted.
        selected_nodes : list[str | int] | None, default ``None``
            Node IDs or zero-based node indices to include.
            • ``None``  → export **all** nodes.
            • Strings   → treated as node IDs.
            • Integers  → treated as node indices.
        selected_species : list[str | int] | None, default ``None``
            Species names or zero-based species indices to include.
            Same ID / index rules as *selected_nodes*.
        header : bool, default ``True``
            Write column headers (“NODE INDEX”, “NODE ID”, time steps …).
            If ``False``, headers are suppressed and the first data row is
            removed—useful for appending to an existing sheet.

        Simple Example with all nodes and species:
            G = epanet("net2-cl2.inp")
            G.loadMSXFile("net2-cl2.msx")
            MSX_comp = G.getMSXComputedQualityNode()
            G.exportMSXts(MSX_comp, "net2")
            G.exportMSXstatistics("net2","summarynet2")

        Advanced Examples:
            G = epanet("net2-cl2.inp")
            G.loadMSXFile("net2-cl2.msx")

            # Run MSX simulation and grab node-quality results
            msx_results = G.getMSXComputedQualityNode()

            # 1) Export every species for every node (default behaviour)
            G.exportMSXts(msx_results, "net2_full.xlsx")

            # 2) Export only chlorine for two specific nodes, keep headers
            G.exportMSXts(
                    MSX_comp,
                    output_file="chlorine_subset.xlsx",
                    selected_nodes=["10", "15"], #select nodes by their id
                    selected_species=["CL2"]
                )


            G.exportMSXts(
                            MSX_comp,
                            output_file="chlorine_subset1.xlsx",
                            selected_nodes=[9, 14], #select node by their index
                            selected_species=["CL2"]
                        )

            # 3) Export species index 0 for nodes 0-4, omit headers
            G.exportMSXts(
                msx_results,
                "first_species_nodes0to4.xlsx",
                selected_nodes=list(range(5)),
                selected_species=[0],  #select specie by its index
                header=False

        """
        if not output_file.endswith('.xlsx'):
            output_file += '.xlsx'

        if not hasattr(results, 'Time') or not hasattr(results, 'Quality'):
            raise ValueError("Simulation results are not properly initialized or run.")

        time_data = results.Time
        species_list = self.getMSXSpeciesNameID()

        node_ids = self.getNodeNameID()
        node_indices = list(range(len(node_ids)))

        if selected_nodes:
            selected_node_indices = []
            for node in selected_nodes:
                if isinstance(node, str):  # Node ID
                    if node in node_ids:
                        selected_node_indices.append(node_ids.index(node))
                    else:
                        raise ValueError(f"Node ID '{node}' not found.")
                elif isinstance(node, int):  # Node index
                    if 0 <= node < len(node_ids):
                        selected_node_indices.append(node)
                    else:
                        raise ValueError(f"Node index '{node}' is out of range.")
                else:
                    raise ValueError(f"Invalid node identifier: {node}")
        else:
            selected_node_indices = node_indices

        if selected_species:
            selected_species_indices = []
            for species in selected_species:
                if isinstance(species, str):  # Species name
                    if species in species_list:
                        selected_species_indices.append(species_list.index(species))
                    else:
                        raise ValueError(f"Species name '{species}' not found.")
                elif isinstance(species, int):  # Species index
                    if 0 <= species < len(species_list):
                        selected_species_indices.append(species)
                    else:
                        raise ValueError(f"Species index '{species}' is out of range.")
                else:
                    raise ValueError(f"Invalid species identifier: {species}")
        else:
            selected_species_indices = list(range(len(species_list)))

        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            node_keys = list(results.Quality.keys())

            for species_index in selected_species_indices:
                species_name = species_list[species_index]
                species_data = []

                for node_index in selected_node_indices:
                    node_key = node_keys[node_index]
                    quality_data = np.array(results.Quality[node_key])

                    # If quality_data has an extra leading dimension
                    if quality_data.ndim == 3 and quality_data.shape[0] == 1:
                        quality_data = quality_data[0]

                    num_timesteps = len(time_data)
                    num_species = len(species_list)
                    expected_shape = (num_timesteps, num_species)

                    if quality_data.shape != expected_shape:
                        raise ValueError(
                            f"Node {node_key}: quality_data does not match expected shape {expected_shape}. "
                            f"Actual shape: {quality_data.shape}"
                        )
                    species_data.append(quality_data[:, species_index])

                species_data_array = np.array(species_data)

                df = pd.DataFrame(species_data_array, columns=time_data,
                                  index=[node_ids[i] for i in selected_node_indices])
                df.insert(0, 'NODE INDEX', [node_indices[i] for i in selected_node_indices])
                df.insert(1, 'NODE ID', [node_ids[i] for i in selected_node_indices])

                # If header is False, remove the first data row from df
                if not header and len(df) > 0:
                    df = df.iloc[1:].copy()

                sheet_name = f"{species_name}"
                # If header=False, no column headers will be written to the Excel sheet.
                df.to_excel(writer, index=False, sheet_name=sheet_name, header=header)

                worksheet = writer.sheets[sheet_name]
                worksheet.set_column('A:A', 13.0)

        print(f"Data successfully written to {output_file}")

    def exportMSXstatistics(self,input_path, output_path="summary_output.xlsx", nodeids=True, nodeindex=True):
        """
        Summarizes min, max, and average values for each node in an Excel file with a specific structure.

        Parameters:
            input_path (str): Path to the input Excel file.
            output_path (str): Path to save the output summary Excel file.
            nodeids (bool): Include node IDs (from column 1) in the summary.
            nodeindex (bool): Include node index (from column 0) in the summary.

        Simple Example with all nodes and species:
            G = epanet("net2-cl2.inp")
            G.loadMSXFile("net2-cl2.msx")
            MSX_comp = G.getMSXComputedQualityNode()
            G.exportMSXts(MSX_comp, "net2")
            G.exportMSXstatistics("net2","summarynet2")

        # Example usage:
        exportMSXstatistics("outexcel3.xlsx","summary_output1.xlsx", nodeids=True, nodeindex=False)  # Only node IDs
        exportMSXstatistics("outexcel3.xlsx", "summary_output2.xlsx",nodeids=False, nodeindex=True)  # Only node indices
        exportMSXstatistics("outexcel3.xlsx","summary_output3.xlsx", nodeids=True, nodeindex=True)   # Both
        """
        if not input_path.endswith('.xlsx'):
            input_path += '.xlsx'

        if not output_path.endswith('.xlsx'):
            output_path += '.xlsx'
        xls = pd.ExcelFile(input_path)
        output_data = {}

        for sheet in xls.sheet_names:
            df = xls.parse(sheet, header=None)

            data = df.iloc[1:].reset_index(drop=True)

            summary_rows = []

            for _, row in data.iterrows():
                index = int(row[0])
                node_id = str(row[1])
                values = pd.to_numeric(row[2:], errors='coerce').dropna()

                if values.empty:
                    continue

                summary = {
                    'Min': values.min(),
                    'Max': values.max(),
                    'Mean': values.mean()
                }

                if nodeids:
                    summary['NodeID'] = node_id
                if nodeindex:
                    summary['NodeIndex'] = index

                ordered_summary = {}
                if nodeids:
                    ordered_summary['NodeID'] = summary['NodeID']
                if nodeindex:
                    ordered_summary['NodeIndex'] = summary['NodeIndex']
                ordered_summary['Min'] = summary['Min']
                ordered_summary['Max'] = summary['Max']
                ordered_summary['Mean'] = summary['Mean']

                summary_rows.append(ordered_summary)

            output_data[sheet] = pd.DataFrame(summary_rows)

        with pd.ExcelWriter(output_path) as writer:
            for sheet_name, df in output_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"Summary saved to: {output_path}")


class epanetapi:
    """
    EPANET Toolkit functions - API
    """

    EN_MAXID = 32  # toolkit constant

    def __init__(self, version=2.2, ph=False, loadlib=True, customlib=None):
        """Load the EPANET library.

        Parameters:
        version     EPANET version to use (currently 2.2)
        """
        self._lib = None
        self.errcode = 0
        self.inpfile = None
        self.rptfile = None
        self.binfile = None
        self._ph = None

        # Check platform and Load epanet library
        # libname = f"epanet{str(version).replace('.', '_')}"
        if customlib is not None:
            if not os.path.isabs(customlib):
                self.LibEPANET = os.path.join(os.getcwd(), customlib)
            else:
                self.LibEPANET = customlib
            loadlib = False
            self._lib = cdll.LoadLibrary(self.LibEPANET)
            self.LibEPANETpath = os.path.dirname(self.LibEPANET)

        if loadlib:
            libname = f"epanet2"
            ops = platform.system().lower()
            if ops in ["windows"]:
                self.LibEPANET = os.path.join(epyt_root, os.path.join("libraries", "win", f"{libname}.dll"))
            elif ops in ["darwin"]:
                self.LibEPANET = os.path.join(epyt_root, os.path.join("libraries", f"mac/lib{libname}.dylib"))
            else:
                self.LibEPANET = os.path.join(epyt_root, os.path.join("libraries", f"glnx/lib{libname}.so"))

            self._lib = cdll.LoadLibrary(self.LibEPANET)
            self.LibEPANETpath = os.path.dirname(self.LibEPANET)

        if float(version) >= 2.2 and ph:
            self._ph = c_uint64()

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
        self.errcode = self._lib.ENepanet(self.inpfile, self.rptfile, self.binfile, c_void_p())
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
        index = c_int()
        if self._ph is not None:
            self.errcode = self._lib.EN_addcontrol(self._ph, conttype, int(lindex), c_double(setting), nindex,
                                                   c_double(level), byref(index))
        else:
            self.errcode = self._lib.ENaddcontrol(conttype, int(lindex), c_float(setting), nindex,
                                                  c_float(level), byref(index))
        self.ENgeterror()
        return index.value

    def ENaddcurve(self, cid):
        """ Adds a new data curve to a project.


        ENaddcurve(cid)

        Parameters:
        cid        The ID name of the curve to be added.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___curves.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_addcurve(self._ph, cid.encode('utf-8'))
        else:
            self.errcode = self._lib.ENaddcurve(cid.encode('utf-8'))

        self.ENgeterror()

    def ENadddemand(self, nodeIndex, baseDemand, demandPattern, demandName):
        """ Appends a new demand to a junction node demands list.

        ENadddemand(nodeIndex, baseDemand, demandPattern, demandName)

        Parameters:
        nodeIndex        the index of a node (starting from 1).
        baseDemand       the demand's base value.
        demandPattern    the name of a time pattern used by the demand.
        demandName       the name of the demand's category.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___demands.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_adddemand(self._ph, int(nodeIndex), c_double(baseDemand),
                                                  demandPattern.encode("utf-8"),
                                                  demandName.encode("utf-8"))
        else:
            self.errcode = self._lib.ENadddemand(int(nodeIndex), c_float(baseDemand),
                                                 demandPattern.encode("utf-8"),
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
        index = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_addlink(self._ph, linkid.encode('utf-8'), linktype,
                                                fromnode.encode('utf-8'), tonode.encode('utf-8'), byref(index))
        else:
            self.errcode = self._lib.ENaddlink(linkid.encode('utf-8'), linktype,
                                               fromnode.encode('utf-8'), tonode.encode('utf-8'), byref(index))
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
        index = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_addnode(self._ph, nodeid.encode("utf-8"), nodetype, byref(index))
        else:
            self.errcode = self._lib.ENaddnode(nodeid.encode("utf-8"), nodetype, byref(index))

        self.ENgeterror()
        return index.value

    def ENaddpattern(self, patid):
        """ Adds a new time pattern to a project.

        ENaddpattern(patid)

        Parameters:
        patid      the ID name of the pattern to add.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___patterns.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_addpattern(self._ph, patid.encode("utf-8"))
        else:
            self.errcode = self._lib.ENaddpattern(patid.encode("utf-8"))

        self.ENgeterror()
        return

    def ENaddrule(self, rule):
        """ Adds a new rule-based control to a project.


        ENaddrule(rule)

        Parameters:
        rule        text of the rule following the format used in an EPANET input file.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___rules.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_addrule(self._ph, rule.encode('utf-8'))
        else:
            self.errcode = self._lib.ENaddrule(rule.encode('utf-8'))

        self.ENgeterror()

    def ENclearreport(self):
        """ Clears the contents of a project's report file.


        ENclearreport()

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_clearreport(self._ph)
        else:
            self.errcode = self._lib.ENclearreport()

        self.ENgeterror()

    def ENclose(self):
        """ Closes a project and frees all of its memory.

        ENclose()

        See also ENopen
        """
        if self._ph is not None:
            self.errcode = self._lib.EN_close(self._ph)
            self._ph = c_uint64()
        else:
            self.errcode = self._lib.ENclose()

        self.ENgeterror()

    def ENcloseH(self):
        """ Closes the hydraulic solver freeing all of its allocated memory.

        ENcloseH()

        See also  ENinitH, ENrunH, ENnextH
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_closeH(self._ph)
        else:
            self.errcode = self._lib.ENcloseH()

        self.ENgeterror()
        return

    def ENcloseQ(self):
        """ Closes the water quality solver, freeing all of its allocated memory.

        ENcloseQ()

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___quality.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_closeQ(self._ph)
        else:
            self.errcode = self._lib.ENcloseQ()

        self.ENgeterror()
        return

    def ENcopyreport(self, filename):
        """ Copies the current contents of a project's report file to another file.


        ENcopyreport(filename)

        Parameters:
        filename  the full path name of the destination file

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_copyreport(self._ph, filename.encode("utf-8"))
        else:
            self.errcode = self._lib.ENcopyreport(filename.encode("utf-8"))

        self.ENgeterror()

    def ENcreateproject(self):
        """ Copies the current contents of a project's report file to another file.
        *** ENcreateproject must be called before any other API functions are used. ***
        ENcreateproject()

        Parameters:
        ph	an EPANET project handle that is passed into all other API functions.

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_createproject(byref(self._ph))

        self.ENgeterror()
        return

    def ENdeletecontrol(self, index):
        """ Deletes an existing simple control.


        ENdeletecontrol(index)

        Parameters:
        index       the index of the control to delete (starting from 1).

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_deletecontrol(self._ph, int(index))
        else:
            self.errcode = self._lib.ENdeletecontrol(int(index))

        self.ENgeterror()

    def ENdeletecurve(self, indexCurve):
        """ Deletes a data curve from a project.


        ENdeletecurve(indexCurve)

        Parameters:
        indexCurve  The ID name of the curve to be added.

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_deletecurve(self._ph, int(indexCurve))
        else:
            self.errcode = self._lib.ENdeletecurve(int(indexCurve))

        self.ENgeterror()

    def ENdeletedemand(self, nodeIndex, demandIndex):
        """ Deletes a demand from a junction node.

        ENdeletedemand(nodeIndex, demandInde)

        Parameters:
        nodeIndex        the index of a node (starting from 1).
        demandIndex      the position of the demand in the node's demands list (starting from 1).

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_deletedemand(self._ph, int(nodeIndex), demandIndex)
        else:
            self.errcode = self._lib.ENdeletedemand(int(nodeIndex), demandIndex)

        self.ENgeterror()

    def ENdeletelink(self, indexLink, condition):
        """ Deletes a link from the project.

        ENdeletelink(indexLink, condition)

        Parameters:
        indexLink      the index of the link to be deleted.
        condition      The action taken if any control contains the link.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___links.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_deletelink(self._ph, int(indexLink), condition)
        else:
            self.errcode = self._lib.ENdeletelink(int(indexLink), condition)

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

        if self._ph is not None:
            self.errcode = self._lib.EN_deletenode(self._ph, int(indexNode), condition)
        else:
            self.errcode = self._lib.ENdeletenode(int(indexNode), condition)

        self.ENgeterror()

    def ENdeletepattern(self, indexPat):
        """ Deletes a time pattern from a project.


        ENdeletepattern(indexPat)

        Parameters:
        indexPat   the time pattern's index (starting from 1).

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_deletepattern(self._ph, int(indexPat))
        else:
            self.errcode = self._lib.ENdeletepattern(int(indexPat))

        self.ENgeterror()

    def ENdeleteproject(self):
        """ Deletes an EPANET project.
        *** EN_deleteproject should be called after all network analysis has been completed. ***
        ENdeleteproject()

        Parameters:
        ph	an EPANET project handle which is returned as NULL.

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_deleteproject(self._ph)

        self.ENgeterror()
        return

    def ENdeleterule(self, index):
        """ Deletes an existing rule-based control.


        ENdeleterule(index)

        Parameters:
        index       the index of the rule to be deleted (starting from 1).

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_deleterule(self._ph, int(index))
        else:
            self.errcode = self._lib.ENdeleterule(int(index))

        self.ENgeterror()

    def ENgetaveragepatternvalue(self, index):
        """ Retrieves the average of all pattern factors in a time pattern.


        ENgetaveragepatternvalue(index)

        Parameters:
        index      a time pattern index (starting from 1).

        Returns:
        value The average of all of the time pattern's factors.
        """

        if self._ph is not None:
            value = c_double()
            self.errcode = self._lib.EN_getaveragepatternvalue(self._ph, int(index), byref(value))
        else:
            value = c_float()
            self.errcode = self._lib.ENgetaveragepatternvalue(int(index), byref(value))

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

        if self._ph is not None:
            bDem = c_double()
            self.errcode = self._lib.EN_getbasedemand(self._ph, int(index), numdemands, byref(bDem))
        else:
            bDem = c_float()
            self.errcode = self._lib.ENgetbasedemand(int(index), numdemands, byref(bDem))

        self.ENgeterror()
        return bDem.value

    def ENgetcomment(self, object_, index):
        """ Retrieves the comment of a specific index of a type object.


        ENgetcomment(object, index, comment)

        Parameters:
        object_    a type of object (either EN_NODE, EN_LINK, EN_TIMEPAT or EN_CURVE)
                   e.g, self.ToolkitConstants.EN_NODE
        index      object's index (starting from 1).

        Returns:
        out_comment  the comment string assigned to the object.
        """
        out_comment = create_string_buffer(80)

        if self._ph is not None:
            self.errcode = self._lib.EN_getcomment(self._ph, object_, int(index), byref(out_comment))
        else:
            self.errcode = self._lib.ENgetcomment(object_, int(index), byref(out_comment))

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
        ctype = c_int()
        lindex = c_int()
        nindex = c_int()

        if self._ph is not None:
            setting = c_double()
            level = c_double()
            self.errcode = self._lib.EN_getcontrol(self._ph, int(cindex), byref(ctype), byref(lindex),
                                                   byref(setting), byref(nindex), byref(level))
        else:
            setting = c_float()
            level = c_float()
            self.errcode = self._lib.ENgetcontrol(int(cindex), byref(ctype), byref(lindex),
                                                  byref(setting), byref(nindex), byref(level))

        self.ENgeterror()
        return [ctype.value, lindex.value, setting.value, nindex.value, level.value]

    def ENgetcoord(self, index):
        """ Gets the (x,y) coordinates of a node.


        ENgetcoord(index)

        Parameters:
        index      a node index (starting from 1).

        Returns:
        x 	the node's X-coordinate value.
        y   the node's Y-coordinate value.
        """
        x = c_double()
        y = c_double()

        if self._ph is not None:
            self.errcode = self._lib.EN_getcoord(self._ph, int(index), byref(x), byref(y))
        else:
            self.errcode = self._lib.ENgetcoord(int(index), byref(x), byref(y))

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
        count = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getcount(self._ph, countcode, byref(count))
        else:
            self.errcode = self._lib.ENgetcount(countcode, byref(count))

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
        out_id = create_string_buffer(self.EN_MAXID)
        nPoints = c_int()
        if self._ph is not None:
            xValues = (c_double * self.ENgetcurvelen(index))()
            yValues = (c_double * self.ENgetcurvelen(index))()
            self.errcode = self._lib.EN_getcurve(self._ph, index, byref(out_id), byref(nPoints),
                                                 byref(xValues), byref(yValues))
        else:
            xValues = (c_float * self.ENgetcurvelen(index))()
            yValues = (c_float * self.ENgetcurvelen(index))()
            self.errcode = self._lib.ENgetcurve(index, byref(out_id), byref(nPoints),
                                                byref(xValues), byref(yValues))

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


        ENgetcurveid(index)

        Parameters:
        index       a curve's index (starting from 1).

        Returns:
        Id	the curve's ID name

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___curves.html
        """
        Id = create_string_buffer(self.EN_MAXID)

        if self._ph is not None:
            self.errcode = self._lib.EN_getcurveid(self._ph, int(index), byref(Id))
        else:
            self.errcode = self._lib.ENgetcurveid(int(index), byref(Id))

        self.ENgeterror()
        return Id.value.decode()

    def ENgetcurveindex(self, Id):
        """ Retrieves the index of a curve given its ID name.


        ENgetcurveindex(Id)

        Parameters:
        Id          the ID name of a curve.

        Returns:
        index   The curve's index (starting from 1).
        """
        index = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getcurveindex(self._ph, Id.encode("utf-8"), byref(index))
        else:
            self.errcode = self._lib.ENgetcurveindex(Id.encode("utf-8"), byref(index))

        self.ENgeterror()
        return index.value

    def ENgetcurvelen(self, index):
        """ Retrieves the number of points in a curve.


        ENgetcurvelen(index)

        Parameters:
        index       a curve's index (starting from 1).

        Returns:
        len  The number of data points assigned to the curve.
        """
        length = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getcurvelen(self._ph, int(index), byref(length))
        else:
            self.errcode = self._lib.ENgetcurvelen(int(index), byref(length))

        self.ENgeterror()
        return length.value

    def ENgetcurvetype(self, index):
        """ Retrieves a curve's type.


        ENgetcurvetype(index)

        Parameters:
        index       a curve's index (starting from 1).

        Returns:
        type_  The curve's type (see EN_CurveType).
        """
        type_ = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getcurvetype(self._ph, int(index), byref(type_))
        else:
            self.errcode = self._lib.ENgetcurvetype(int(index), byref(type_))

        self.ENgeterror()
        return type_.value

    def ENgetcurvevalue(self, index, period):
        """ Retrieves the value of a single data point for a curve.


        ENgetcurvevalue(index, period)

        Parameters:
        index       a curve's index (starting from 1).
        period      the index of a point on the curve (starting from 1).

        Returns:
        x  the point's x-value.
        y  the point's y-value.
        """
        if self._ph is not None:
            x = c_double()
            y = c_double()
            self.errcode = self._lib.EN_getcurvevalue(self._ph, int(index), period, byref(x), byref(y))
        else:
            x = c_float()
            y = c_float()
            self.errcode = self._lib.ENgetcurvevalue(int(index), period, byref(x), byref(y))

        self.ENgeterror()
        return [x.value, y.value]

    def ENgetdemandindex(self, nodeindex, demandName):
        """ Retrieves the index of a node's named demand category.


        ENgetdemandindex(nodeindex, demandName)

        Parameters:
        nodeindex    the index of a node (starting from 1).
        demandName   the name of a demand category for the node.

        Returns:
        demandIndex  the index of the demand being sought.
        """
        demandIndex = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getdemandindex(self._ph, int(nodeindex), demandName.encode('utf-8'),
                                                       byref(demandIndex))
        else:
            self.errcode = self._lib.ENgetdemandindex(int(nodeindex), demandName.encode('utf-8'),
                                                      byref(demandIndex))

        self.ENgeterror()
        return demandIndex.value

    def ENgetdemandmodel(self):
        """ Retrieves the type of demand model in use and its parameters.


        ENgetdemandmodel()

        Returns:
        Type  Type of demand model (see EN_DemandModel).
        pmin  Pressure below which there is no demand.
        preq  Pressure required to deliver full demand.
        pexp  Pressure exponent in demand function.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___demands.html
        """
        Type = c_int()
        if self._ph is not None:
            pmin = c_double()
            preq = c_double()
            pexp = c_double()
            self.errcode = self._lib.EN_getdemandmodel(self._ph, byref(Type), byref(pmin),
                                                       byref(preq), byref(pexp))
        else:
            pmin = c_float()
            preq = c_float()
            pexp = c_float()
            self.errcode = self._lib.ENgetdemandmodel(byref(Type), byref(pmin),
                                                      byref(preq), byref(pexp))

        self.ENgeterror()
        return [Type.value, pmin.value, preq.value, pexp.value]

    def ENgetdemandname(self, node_index, demand_index):
        """ Retrieves the name of a node's demand category.


        ENgetdemandname(node_index, demand_index)

        Parameters:
        node_index    	a node's index (starting from 1).
        demand_index    the index of one of the node's demand categories (starting from 1).

        Returns:
        demand_name  The name of the selected category.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___demands.html
        """

        if self._ph is not None:
            demand_name = create_string_buffer(100)
            self.errcode = self._lib.EN_getdemandname(self._ph, int(node_index), int(demand_index),
                                                      byref(demand_name))
        else:
            demand_name = create_string_buffer(80)
            self.errcode = self._lib.ENgetdemandname(int(node_index), int(demand_index),
                                                     byref(demand_name))

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
        patIndex = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getdemandpattern(self._ph, int(index), numdemands, byref(patIndex))
        else:
            self.errcode = self._lib.ENgetdemandpattern(int(index), numdemands, byref(patIndex))

        self.ENgeterror()
        return patIndex.value

    def ENgetelseaction(self, ruleIndex, actionIndex):
        """ Gets the properties of an ELSE action in a rule-based control.


        ENgetelseaction(ruleIndex, actionIndex)

        Parameters:
        ruleIndex   	the rule's index (starting from 1).
        actionIndex   the index of the ELSE action to retrieve (starting from 1).

        Returns:
        linkIndex  the index of the link sin the action.
        status     the status assigned to the link (see RULESTATUS).
        setting    the value assigned to the link's setting.
        """
        linkIndex = c_int()
        status = c_int()

        if self._ph is not None:
            setting = c_double()
            self.errcode = self._lib.EN_getelseaction(self._ph, int(ruleIndex), int(actionIndex),
                                                      byref(linkIndex),
                                                      byref(status), byref(setting))
        else:
            setting = c_float()
            self.errcode = self._lib.ENgetelseaction(int(ruleIndex), int(actionIndex),
                                                     byref(linkIndex),
                                                     byref(status), byref(setting))

        self.ENgeterror()
        return [linkIndex.value, status.value, setting.value]

    def ENgeterror(self, errcode=0):
        """ Returns the text of an error message generated by an error code, as warning.

        ENgeterror()

        """
        if self.errcode or errcode:
            if errcode:
                self.errcode = errcode
            errmssg = create_string_buffer(150)
            self._lib.ENgeterror(self.errcode, byref(errmssg), 150)
            return errmssg.value.decode()

    def ENgetflowunits(self):
        """ Retrieves a project's flow units.

        ENgetflowunits()

        Returns:
        flowunitsindex a flow units code.
        """
        flowunitsindex = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getflowunits(self._ph, byref(flowunitsindex))
        else:
            self.errcode = self._lib.ENgetflowunits(byref(flowunitsindex))

        self.ENgeterror()
        return flowunitsindex.value

    def ENgetheadcurveindex(self, pumpindex):
        """ Retrieves the curve assigned to a pump's head curve.


        ENgetheadcurveindex(pumpindex)

        Parameters:
        pumpindex      the index of a pump link (starting from 1).

        Returns:
        value   the index of the curve assigned to the pump's head curve.
        """
        value = c_long()

        if self._ph is not None:
            self.errcode = self._lib.EN_getheadcurveindex(self._ph, int(pumpindex), byref(value))
        else:
            self.errcode = self._lib.ENgetheadcurveindex(int(pumpindex), byref(value))

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
        nameID = create_string_buffer(self.EN_MAXID)

        if self._ph is not None:
            self.errcode = self._lib.EN_getlinkid(self._ph, int(index), byref(nameID))
        else:
            self.errcode = self._lib.ENgetlinkid(int(index), byref(nameID))

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
        index = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getlinkindex(self._ph, Id.encode("utf-8"), byref(index))
        else:
            self.errcode = self._lib.ENgetlinkindex(Id.encode("utf-8"), byref(index))

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
        fromNode = c_int()
        toNode = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getlinknodes(self._ph, int(index), byref(fromNode), byref(toNode))
        else:
            self.errcode = self._lib.ENgetlinknodes(int(index), byref(fromNode), byref(toNode))

        self.ENgeterror()
        return [fromNode.value, toNode.value]

    def ENgetlinktype(self, index):
        """ Retrieves a link's type.

        ENgetlinktype(index)

        Parameters:
        index      	a link's index (starting from 1).

        Returns:
        typecode   the link's type (see LinkType).
        """
        code_p = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getlinktype(self._ph, int(index), byref(code_p))
        else:
            self.errcode = self._lib.ENgetlinktype(int(index), byref(code_p))

        self.ENgeterror()
        if code_p.value != -1:
            return code_p.value
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

        if self._ph is not None:
            fValue = c_double()
            self.errcode = self._lib.EN_getlinkvalue(self._ph, int(index), paramcode, byref(fValue))
        else:
            fValue = c_float()
            self.errcode = self._lib.ENgetlinkvalue(int(index), paramcode, byref(fValue))

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
        nameID = create_string_buffer(self.EN_MAXID)

        if self._ph is not None:
            self.errcode = self._lib.EN_getnodeid(self._ph, int(index), byref(nameID))
        else:
            self.errcode = self._lib.ENgetnodeid(int(index), byref(nameID))

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
        index = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getnodeindex(self._ph, Id.encode("utf-8"), byref(index))
        else:
            self.errcode = self._lib.ENgetnodeindex(Id.encode("utf-8"), byref(index))

        self.ENgeterror()
        return index.value

    def ENgetnodetype(self, index):
        """ Retrieves a node's type given its index.

        ENgetnodetype(index)

        Parameters:
        index      a node's index (starting from 1).

        Returns:
        type the node's type (see NodeType).
        """
        code_p = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getnodetype(self._ph, int(index), byref(code_p))
        else:
            self.errcode = self._lib.ENgetnodetype(int(index), byref(code_p))

        self.ENgeterror()
        return code_p.value

    def ENgetnodevalue(self, index, code_p):
        """ Retrieves a property value for a node.

        ENgetnodevalue(index, paramcode)

        Parameters:
        index      a node's index.
        paramcode  the property to retrieve (see EN_NodeProperty, self.getToolkitConstants).

        Returns:
        value the current value of the property.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___nodes.html
        """
        if self._ph is not None:
            fValue = c_double()
            self.errcode = self._lib.EN_getnodevalue(self._ph, int(index), code_p, byref(fValue))
        else:
            fValue = c_float()
            self.errcode = self._lib.ENgetnodevalue(int(index), code_p, byref(fValue))

        if self.errcode == 240:
            self.errcode = 0
            return None
        else:
            self.ENgeterror()
            return fValue.value

    def ENgetnumdemands(self, index):
        """ Retrieves the number of demand categories for a junction node.
        EPANET 20100

        ENgetnumdemands(index)

        Parameters:
        index    	   the index of a node (starting from 1).

        Returns:
        value  the number of demand categories assigned to the node.
        """
        numDemands = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getnumdemands(self._ph, int(index), byref(numDemands))
        else:
            self.errcode = self._lib.ENgetnumdemands(int(index), byref(numDemands))

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
        if self._ph is not None:
            value = c_double()
            self.errcode = self._lib.EN_getoption(self._ph, optioncode, byref(value))
        else:
            value = c_float()
            self.errcode = self._lib.ENgetoption(optioncode, byref(value))

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
        nameID = create_string_buffer(self.EN_MAXID)

        if self._ph is not None:
            self.errcode = self._lib.EN_getpatternid(self._ph, int(index), byref(nameID))
        else:
            self.errcode = self._lib.ENgetpatternid(int(index), byref(nameID))

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
        index = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getpatternindex(self._ph, Id.encode("utf-8"), byref(index))
        else:
            self.errcode = self._lib.ENgetpatternindex(Id.encode("utf-8"), byref(index))

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
        leng = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getpatternlen(self._ph, int(index), byref(leng))
        else:
            self.errcode = self._lib.ENgetpatternlen(int(index), byref(leng))

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
        if self._ph is not None:
            value = c_double()
            self.errcode = self._lib.EN_getpatternvalue(self._ph, int(index), period, byref(value))
        else:
            value = c_float()
            self.errcode = self._lib.ENgetpatternvalue(int(index), period, byref(value))

        self.ENgeterror()
        return value.value

    def ENgetpremise(self, ruleIndex, premiseIndex):
        """ Gets the properties of a premise in a rule-based control.


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
        logop = c_int()
        object_ = c_int()
        objIndex = c_int()
        variable = c_int()
        relop = c_int()
        status = c_int()

        if self._ph is not None:
            value = c_double()
            self.errcode = self._lib.EN_getpremise(self._ph, int(ruleIndex), int(premiseIndex), byref(logop),
                                                   byref(object_), byref(objIndex),
                                                   byref(variable), byref(relop), byref(status),
                                                   byref(value))
        else:
            value = c_float()
            self.errcode = self._lib.ENgetpremise(int(ruleIndex), int(premiseIndex), byref(logop),
                                                  byref(object_), byref(objIndex),
                                                  byref(variable), byref(relop), byref(status),
                                                  byref(value))

        self.ENgeterror()
        return [logop.value, object_.value, objIndex.value, variable.value, relop.value, status.value, value.value]

    def ENgetpumptype(self, index):
        """ Retrieves the type of head curve used by a pump.


        ENgetpumptype(pumpindex)

        Parameters:
        pumpindex   the index of a pump link (starting from 1).

        Returns:
        value   the type of head curve used by the pump (see EN_PumpType).
        """
        code_p = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getpumptype(self._ph, int(index), byref(code_p))
        else:
            self.errcode = self._lib.ENgetpumptype(int(index), byref(code_p))

        self.ENgeterror()
        return code_p.value

    def ENgetqualinfo(self):
        """ Gets information about the type of water quality analysis requested.

        ENgetqualinfo()

        Returns:
        qualType    type of analysis to run (see self.QualityType).
        chemname    name of chemical constituent.
        chemunits   concentration units of the constituent.
        tracenode 	index of the node being traced (if applicable).
        """
        qualType = c_int()
        chemname = create_string_buffer(self.EN_MAXID)
        chemunits = create_string_buffer(self.EN_MAXID)
        tracenode = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getqualinfo(self._ph, byref(qualType), byref(chemname),
                                                    byref(chemunits), byref(tracenode))
        else:
            self.errcode = self._lib.ENgetqualinfo(byref(qualType), byref(chemname),
                                                   byref(chemunits), byref(tracenode))

        self.ENgeterror()
        return [qualType.value, chemname.value.decode(), chemunits.value.decode(), tracenode.value]

    def ENgetqualtype(self):
        """ Retrieves the type of water quality analysis to be run.

        ENgetqualtype()

        Returns:
        qualcode    type of analysis to run (see self.QualityType).
        tracenode 	index of the node being traced (if applicable).
        """
        qualcode = c_int()
        tracenode = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getqualtype(self._ph, byref(qualcode), byref(tracenode))
        else:
            self.errcode = self._lib.ENgetqualtype(byref(qualcode), byref(tracenode))

        self.ENgeterror()
        return [qualcode.value, tracenode.value]

    def ENgetresultindex(self, objecttype, index):
        """Retrieves the order in which a node or link appears in an output file.


           ENgetresultindex(objecttype, index)

        Parameters:
        objecttype  a type of element (either EN_NODE or EN_LINK).
        index       the element's current index (starting from 1).

        Returns:
        value the order in which the element's results were written to file.
        """
        value = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getresultindex(self._ph, objecttype, int(index), byref(value))
        else:
            self.errcode = self._lib.ENgetresultindex(objecttype, int(index), byref(value))

        self.ENgeterror()
        return value.value

    def ENgetrule(self, index):
        """ Retrieves summary information about a rule-based control.


        ENgetrule(index):

        Parameters:
        index   	  the rule's index (starting from 1).

        Returns:
        nPremises     	 number of premises in the rule's IF section.
        nThenActions    number of actions in the rule's THEN section.
        nElseActions    number of actions in the rule's ELSE section.
        priority        the rule's priority value.
        """
        nPremises = c_int()
        nThenActions = c_int()
        nElseActions = c_int()

        if self._ph is not None:
            priority = c_double()
            self.errcode = self._lib.EN_getrule(self._ph, int(index), byref(nPremises),
                                                byref(nThenActions),
                                                byref(nElseActions), byref(priority))
        else:
            priority = c_float()
            self.errcode = self._lib.ENgetrule(int(index), byref(nPremises),
                                               byref(nThenActions),
                                               byref(nElseActions), byref(priority))

        self.ENgeterror()
        return [nPremises.value, nThenActions.value, nElseActions.value, priority.value]

    def ENgetruleID(self, index):
        """ Gets the ID name of a rule-based control given its index.


        ENgetruleID(index)

        Parameters:
        index   	  the rule's index (starting from 1).

        Returns:
        id  the rule's ID name.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___rules.html
        """
        nameID = create_string_buffer(self.EN_MAXID)

        if self._ph is not None:
            self.errcode = self._lib.EN_getruleID(self._ph, int(index), byref(nameID))
        else:
            self.errcode = self._lib.ENgetruleID(int(index), byref(nameID))

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
        if self._ph is not None:
            value = c_double()
            self.errcode = self._lib.EN_getstatistic(self._ph, int(code), byref(value))
        else:
            value = c_float()
            self.errcode = self._lib.ENgetstatistic(int(code), byref(value))

        self.ENgeterror()
        return value.value

    def ENgetthenaction(self, ruleIndex, actionIndex):
        """ Gets the properties of a THEN action in a rule-based control.


        ENgetthenaction(ruleIndex, actionIndex)

        Parameters:
        ruleIndex   	the rule's index (starting from 1).
        actionIndex   the index of the THEN action to retrieve (starting from 1).

        Returns:
        linkIndex   the index of the link in the action (starting from 1).
        status      the status assigned to the link (see RULESTATUS).
        setting     the value assigned to the link's setting.
        """
        linkIndex = c_int()
        status = c_int()
        if self._ph is not None:
            setting = c_double()
            self.errcode = self._lib.EN_getthenaction(self._ph, int(ruleIndex), int(actionIndex),
                                                      byref(linkIndex),
                                                      byref(status), byref(setting))
        else:
            setting = c_float()
            self.errcode = self._lib.ENgetthenaction(int(ruleIndex), int(actionIndex),
                                                     byref(linkIndex),
                                                     byref(status), byref(setting))

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
        timevalue = c_long()

        if self._ph is not None:
            self.errcode = self._lib.EN_gettimeparam(self._ph, c_int(paramcode), byref(timevalue))
        else:
            self.errcode = self._lib.ENgettimeparam(c_int(paramcode), byref(timevalue))

        self.ENgeterror()
        return timevalue.value

    def ENgettitle(self):
        """ Retrieves the title lines of the project.


        ENgettitle()

        Returns:
        line1 first title line
        line2 second title line
        line3 third title line
        """
        line1 = create_string_buffer(80)
        line2 = create_string_buffer(80)
        line3 = create_string_buffer(80)

        if self._ph is not None:
            self.errcode = self._lib.EN_gettitle(self._ph, byref(line1), byref(line2),
                                                 byref(line3))
        else:
            self.errcode = self._lib.ENgettitle(byref(line1), byref(line2),
                                                byref(line3))

        self.ENgeterror()
        return [line1.value.decode(), line2.value.decode(), line3.value.decode()]

    def ENgetversion(self):
        """ Retrieves the toolkit API version number.

        ENgetversion()

        Returns:
        LibEPANET the version of the OWA-EPANET toolkit.
        """
        LibEPANET = c_int()
        self.errcode = self._lib.EN_getversion(byref(LibEPANET))
        self.ENgeterror()
        return LibEPANET.value

    def ENgetvertex(self, index, vertex):
        """ Retrieves the coordinate's of a vertex point assigned to a link.


        ENgetvertex(index, vertex)

        Parameters:
        index      a link's index (starting from 1).
        vertex     a vertex point index (starting from 1).

        Returns:
        x  the vertex's X-coordinate value.
        y  the vertex's Y-coordinate value.
        """
        x = c_double()  # need double for EN_ or EN functions.
        y = c_double()
        if self._ph is not None:
            self.errcode = self._lib.EN_getvertex(self._ph, int(index), vertex, byref(x), byref(y))
        else:
            self.errcode = self._lib.ENgetvertex(int(index), vertex, byref(x), byref(y))

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
        count = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getvertexcount(self._ph, int(index), byref(count))
        else:
            self.errcode = self._lib.ENgetvertexcount(int(index), byref(count))

        self.ENgeterror()
        return count.value

    def ENinit(self, unitsType, headLossType):
        """ Initializes an EPANET project.


        ENinit(unitsType, headLossType)

        Parameters:
        unitsType    the choice of flow units (see EN_FlowUnits).
        headLossType the choice of head loss formula (see EN_HeadLossType).

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_init(self._ph, "", "", unitsType, headLossType)
        else:
            self.errcode = self._lib.ENinit("", "", unitsType, headLossType)

        self.ENgeterror()

    def ENinitH(self, flag):
        """ Initializes a network prior to running a hydraulic analysis.

        ENinitH(flag)

        Parameters:
        flag    	a 2-digit initialization flag (see EN_InitHydOption).

        See also  ENinitH, ENrunH, ENnextH, ENreport, ENsavehydfile
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_initH(self._ph, flag)
        else:
            self.errcode = self._lib.ENinitH(flag)

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

        if self._ph is not None:
            self.errcode = self._lib.EN_initQ(self._ph, saveflag)
        else:
            self.errcode = self._lib.ENinitQ(saveflag)

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
        tstep = c_long()

        if self._ph is not None:
            self.errcode = self._lib.EN_nextH(self._ph, byref(tstep))
        else:
            self.errcode = self._lib.ENnextH(byref(tstep))

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
        tstep = c_long()

        if self._ph is not None:
            self.errcode = self._lib.EN_nextQ(self._ph, byref(tstep))
        else:
            self.errcode = self._lib.ENnextQ(byref(tstep))

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

        if self._ph is not None:
            self._lib.EN_createproject(byref(self._ph))
            self.errcode = self._lib.EN_open(self._ph, self.inpfile, self.rptfile, self.binfile)
        else:
            self.errcode = self._lib.ENopen(self.inpfile, self.rptfile, self.binfile)

        self.ENgeterror()
        return

    def ENopenH(self):
        """ Opens a project's hydraulic solver.

        ENopenH()

        See also  ENinitH, ENrunH, ENnextH, ENcloseH
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html"""

        if self._ph is not None:
            self.errcode = self._lib.EN_openH(self._ph)
        else:
            self.errcode = self._lib.ENopenH()

        self.ENgeterror()
        return

    def ENopenQ(self):
        """ Opens a project's water quality solver.

        ENopenQ()

        See also  ENopenQ, ENinitQ, ENrunQ, ENnextQ,
        ENstepQ, ENcloseQ
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___quality.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_openQ(self._ph)
        else:
            self.errcode = self._lib.ENopenQ()

        self.ENgeterror()
        return

    def ENreport(self):
        """ Writes simulation results in a tabular format to a project's report file.

        ENreport()

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___reporting.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_report(self._ph)
        else:
            self.errcode = self._lib.ENreport()

        self.ENgeterror()

    def ENresetreport(self):
        """ Resets a project's report options to their default values.

        ENresetreport()

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___reporting.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_resetreport(self._ph)
        else:
            self.errcode = self._lib.ENresetreport()

        self.ENgeterror()

    def ENrunH(self):
        """ Computes a hydraulic solution for the current point in time.

        ENrunH()

        Returns:
        t  the current simulation time in seconds.

        See also  ENinitH, ENrunH, ENnextH, ENcloseH
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html
        """
        t = c_long()

        if self._ph is not None:
            self.errcode = self._lib.EN_runH(self._ph, byref(t))
        else:
            self.errcode = self._lib.ENrunH(byref(t))

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
        t = c_long()

        if self._ph is not None:
            self.errcode = self._lib.EN_runQ(self._ph, byref(t))
        else:
            self.errcode = self._lib.ENrunQ(byref(t))

        self.ENgeterror()
        return t.value

    def ENsaveH(self):
        """ Transfers a project's hydraulics results from its temporary hydraulics file to its binary output file,
        where results are only reported at uniform reporting intervals.

        ENsaveH()

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_saveH(self._ph)
        else:
            self.errcode = self._lib.ENsaveH()

        self.ENgeterror()
        return

    def ENsavehydfile(self, fname):
        """ Saves a project's temporary hydraulics file to disk.

        ENsaveHydfile(fname)

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_savehydfile(self._ph, fname.encode("utf-8"))
        else:
            self.errcode = self._lib.ENsavehydfile(fname.encode("utf-8"))

        self.ENgeterror()

    def ENsaveinpfile(self, inpname):
        """ Saves a project's data to an EPANET-formatted text file.

        ENsaveinpfile(inpname)

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_saveinpfile(self._ph, inpname.encode("utf-8"))
        else:
            self.errcode = self._lib.ENsaveinpfile(inpname.encode("utf-8"))

        self.ENgeterror()
        return

    def ENsetbasedemand(self, index, demandIdx, value):
        """ Sets the base demand for one of a node's demand categories.


        ENsetbasedemand(index, demandIdx, value)

        Parameters:
        index    	  a node's index (starting from 1).
        demandIdx     the index of a demand category for the node (starting from 1).
        value    	  the new base demand for the category.

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setbasedemand(self._ph, int(index), demandIdx, c_double(value))
        else:
            self.errcode = self._lib.ENsetbasedemand(int(index), demandIdx, c_float(value))

        self.ENgeterror()

    def ENsetcomment(self, object_, index, comment):
        """ Sets a comment to a specific index


        ENsetcomment(object, index, comment)

        Parameters:
        object_     a type of object (either EN_NODE, EN_LINK, EN_TIMEPAT or EN_CURVE)
                   e.g, obj.ToolkitConstants.EN_NODE
        index      objects index (starting from 1).
        comment    comment to be added.

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setcomment(self._ph, object_, index, comment.encode('utf-8'))
        else:
            self.errcode = self._lib.ENsetcomment(object_, index, comment.encode('utf-8'))

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

        if self._ph is not None:
            self.errcode = self._lib.EN_setcontrol(self._ph, int(cindex), ctype, lindex, c_double(setting),
                                                   nindex, c_double(level))
        else:
            self.errcode = self._lib.ENsetcontrol(int(cindex), ctype, lindex, c_float(setting),
                                                  nindex, c_float(level))

        self.ENgeterror()

    def ENsetcoord(self, index, x, y):
        """ Sets the (x,y) coordinates of a node.


        ENsetcoord(index, x, y)

        Parameters:
        index      a node's index.
        x          the node's X-coordinate value.
        y          the node's Y-coordinate value.

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setcoord(self._ph, int(index), c_double(x), c_double(y))
        else:
            self.errcode = self._lib.ENsetcoord(int(index), c_double(x), c_double(y))

        self.ENgeterror()

    def ENsetcurve(self, index, x, y, nfactors):
        """ Assigns a set of data points to a curve.


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

            if self._ph is not None:
                self.errcode = self._lib.EN_setcurve(self._ph, int(index), (c_double * 1)(x),
                                                     (c_double * 1)(y), nfactors)
            else:
                self.errcode = self._lib.ENsetcurve(int(index), (c_float * 1)(x),
                                                    (c_float * 1)(y), nfactors)


        else:

            if self._ph is not None:
                self.errcode = self._lib.EN_setcurve(self._ph, int(index), (c_double * nfactors)(*x),
                                                     (c_double * nfactors)(*y), nfactors)
            else:
                self.errcode = self._lib.ENsetcurve(int(index), (c_float * nfactors)(*x),
                                                    (c_float * nfactors)(*y), nfactors)

        self.ENgeterror()

    def ENsetcurveid(self, index, Id):
        """ Changes the ID name of a data curve given its index.


        ENsetcurveid(index, Id)

        Parameters:
        index       a curve's index (starting from 1).
        Id        	an array of new x-values for the curve.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___curves.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setcurveid(self._ph, int(index), Id.encode('utf-8'))
        else:
            self.errcode = self._lib.ENsetcurveid(int(index), Id.encode('utf-8'))

        self.ENgeterror()

    def ENsetcurvevalue(self, index, pnt, x, y):
        """ Sets the value of a single data point for a curve.


        ENsetcurvevalue(index, pnt, x, y)

        Parameters:
        index         a curve's index (starting from 1).
        pnt        	  the index of a point on the curve (starting from 1).
        x        	  the point's new x-value.
        y        	  the point's new y-value.

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setcurvevalue(self._ph, int(index), pnt,
                                                      c_double(x), c_double(y))
        else:
            self.errcode = self._lib.ENsetcurvevalue(int(index), pnt,
                                                     c_float(x), c_float(y))

        self.ENgeterror()

    def ENsetdemandmodel(self, Type, pmin, preq, pexp):
        """ Sets the Type of demand model to use and its parameters.


        ENsetdemandmodel(index, demandIdx, value)

        Parameters:
        Type         Type of demand model (see DEMANDMODEL).
        pmin         Pressure below which there is no demand.
        preq    	 Pressure required to deliver full demand.
        pexp    	 Pressure exponent in demand function.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___demands.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setdemandmodel(self._ph, Type, c_double(pmin),
                                                       c_double(preq), c_double(pexp))
        else:
            self.errcode = self._lib.ENsetdemandmodel(Type, c_float(pmin),
                                                      c_float(preq), c_float(pexp))

        self.ENgeterror()

    def ENsetdemandname(self, node_index, demand_index, demand_name):
        """ Assigns a name to a node's demand category.


        ENsetdemandname(node_index, demand_index, demand_name)
        Parameters:
        node_index     a node's index (starting from 1).
        demand_index   the index of one of the node's demand categories (starting from 1).
        demand_name    the new name assigned to the category.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___demands.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setdemandname(self._ph, int(node_index), int(demand_index),
                                                      demand_name.encode("utf-8"))
        else:
            self.errcode = self._lib.ENsetdemandname(int(node_index), int(demand_index),
                                                     demand_name.encode("utf-8"))

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

        if self._ph is not None:
            self.errcode = self._lib.EN_setdemandpattern(self._ph, int(index), int(demandIdx), int(patInd))
        else:
            self.errcode = self._lib.ENsetdemandpattern(int(index), int(demandIdx), int(patInd))

    def ENsetelseaction(self, ruleIndex, actionIndex, linkIndex, status, setting):
        """ Sets the properties of an ELSE action in a rule-based control.


        ENsetelseaction(ruleIndex, actionIndex, linkIndex, status, setting)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        actionIndex   the index of the ELSE action being modified (starting from 1).
        linkIndex     the index of the link in the action (starting from 1).
        status        the new status assigned to the link (see RULESTATUS).
        setting       the new value assigned to the link's setting.

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setelseaction(self._ph, int(ruleIndex), int(actionIndex), int(linkIndex),
                                                      status,
                                                      c_double(setting))
        else:
            self.errcode = self._lib.ENsetelseaction(int(ruleIndex), int(actionIndex), int(linkIndex),
                                                     status,
                                                     c_float(setting))

        self.ENgeterror()

    def ENsetflowunits(self, code):
        """ Sets a project's flow units.

        ENsetflowunits(code)

        Parameters:
        code        a flow units code (see EN_FlowUnits)

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setflowunits(self._ph, code)
        else:
            self.errcode = self._lib.ENsetflowunits(code)

        self.ENgeterror()

    def ENsetheadcurveindex(self, pumpindex, curveindex):
        """ Assigns a curve to a pump's head curve.

        ENsetheadcurveindex(pumpindex, curveindex)

        Parameters:
        pumpindex     the index of a pump link (starting from 1).
        curveindex    the index of a curve to be assigned as the pump's head curve.

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setheadcurveindex(self._ph, int(pumpindex), int(curveindex))
        else:
            self.errcode = self._lib.ENsetheadcurveindex(int(pumpindex), int(curveindex))

        self.ENgeterror()

    def ENsetjuncdata(self, index, elev, dmnd, dmndpat):
        """ Sets a group of properties for a junction node.


        ENsetjuncdata(index, elev, dmnd, dmndpat)

        Parameters:
        index      a junction node's index (starting from 1).
        elev       the value of the junction's elevation.
        dmnd       the value of the junction's primary base demand.
        dmndpat    the ID name of the demand's time pattern ("" for no pattern).

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___nodes.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setjuncdata(self._ph, int(index), c_double(elev), c_double(dmnd),
                                                    dmndpat.encode("utf-8"))
        else:
            self.errcode = self._lib.ENsetjuncdata(int(index), c_float(elev), c_float(dmnd),
                                                   dmndpat.encode("utf-8"))

        self.ENgeterror()

    def ENsetlinkid(self, index, newid):
        """ Changes the ID name of a link.


        ENsetlinkid(index, newid)

        Parameters:
        index         a link's index (starting from 1).
        newid         the new ID name for the link.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___links.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setlinkid(self._ph, int(index), newid.encode("utf-8"))
        else:
            self.errcode = self._lib.ENsetlinkid(int(index), newid.encode("utf-8"))

        self.ENgeterror()

    def ENsetlinknodes(self, index, startnode, endnode):
        """ Sets the indexes of a link's start- and end-nodes.


        ENsetlinknodes(index, startnode, endnode)

        Parameters:
        index         a link's index (starting from 1).
        startnode     The index of the link's start node (starting from 1).
        endnode       The index of the link's end node (starting from 1).
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setlinknodes(self._ph, int(index), startnode, endnode)
        else:
            self.errcode = self._lib.ENsetlinknodes(int(index), startnode, endnode)

        self.ENgeterror()

    def ENsetlinktype(self, indexLink, paramcode, actionCode):
        """ Changes a link's type.


        ENsetlinktype(id, paramcode, actionCode)

        Parameters:
        indexLink     a link's index (starting from 1).
        paramcode     the new type to change the link to (see self.LinkType).
        actionCode    the action taken if any controls contain the link.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___links.html
        """
        indexLink = c_int(indexLink)

        if self._ph is not None:
            self.errcode = self._lib.EN_setlinktype(self._ph, byref(indexLink), paramcode, actionCode)
        else:
            self.errcode = self._lib.ENsetlinktype(byref(indexLink), paramcode, actionCode)

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

        if self._ph is not None:
            self.errcode = self._lib.EN_setlinkvalue(self._ph, c_int(index), c_int(paramcode),
                                                     c_double(value))
        else:
            self.errcode = self._lib.ENsetlinkvalue(c_int(index), c_int(paramcode),
                                                    c_float(value))

        self.ENgeterror()
        return

    def ENsetnodeid(self, index, newid):
        """ Changes the ID name of a node.


        ENsetnodeid(index, newid)

        Parameters:
        index      a node's index (starting from 1).
        newid      the new ID name for the node.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___nodes.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setnodeid(self._ph, int(index), newid.encode('utf-8'))
        else:
            self.errcode = self._lib.ENsetnodeid(int(index), newid.encode('utf-8'))
        self.ENgeterror()

    def ENsetnodevalue(self, index, paramcode, value):
        """ Sets a property value for a node.


        ENsetnodevalue(index, paramcode, value)

        Parameters:
        index      a node's index (starting from 1).
        paramcode  the property to set (see EN_NodeProperty, self.getToolkitConstants).
        value      the new value for the property.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___nodes.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setnodevalue(self._ph, c_int(index), c_int(paramcode),
                                                     c_double(value))
        else:
            self.errcode = self._lib.ENsetnodevalue(c_int(index), c_int(paramcode),
                                                    c_float(value))
        self.ENgeterror()
        return

    def ENsetoption(self, optioncode, value):
        """ Sets the value for an anlysis option.

        ENsetoption(optioncode, value)

        Parameters:
        optioncode   a type of analysis option (see EN_Option).
        value        the new value assigned to the option.
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setoption(self._ph, optioncode, c_double(value))
        else:
            self.errcode = self._lib.ENsetoption(optioncode, c_float(value))
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

        if self._ph is not None:
            self.errcode = self._lib.EN_setpattern(self._ph, int(index), (c_double * nfactors)(*factors), nfactors)
        else:
            self.errcode = self._lib.ENsetpattern(int(index), (c_float * nfactors)(*factors),
                                                  nfactors)
        self.ENgeterror()

    def ENsetpatternid(self, index, Id):
        """ Changes the ID name of a time pattern given its index.


        ENsetpatternid(index, id)

        Parameters:
        index      a time pattern index (starting from 1).
        id         the time pattern's new ID name.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___patterns.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setpatternid(self._ph, int(index), Id.encode('utf-8'))
        else:
            self.errcode = self._lib.ENsetpatternid(int(index), Id.encode('utf-8'))
        self.ENgeterror()

    def ENsetpatternvalue(self, index, period, value):
        """ Sets a time pattern's factor for a given time period.

        ENsetpatternvalue(index, period, value)

        Parameters:
        index      a time pattern index (starting from 1).
        period     a time period in the pattern (starting from 1).
        value      the new value of the pattern factor for the given time period.
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setpatternvalue(self._ph, int(index), period, c_double(value))
        else:
            self.errcode = self._lib.ENsetpatternvalue(int(index), period, c_float(value))
        self.ENgeterror()

    def ENsetpipedata(self, index, length, diam, rough, mloss):
        """ Sets a group of properties for a pipe link.


        ENsetpipedata(index, length, diam, rough, mloss)

        Parameters:
        index         the index of a pipe link (starting from 1).
        length        the pipe's length.
        diam          the pipe's diameter.
        rough         the pipe's roughness coefficient.
        mloss         the pipe's minor loss coefficient.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___links.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setpipedata(self._ph, int(index), c_double(length),
                                                    c_double(diam), c_double(rough),
                                                    c_double(mloss))
        else:
            self.errcode = self._lib.ENsetpipedata(int(index), c_float(length),
                                                   c_float(diam), c_float(rough),
                                                   c_float(mloss))

        self.ENgeterror()

    def ENsetpremise(self, ruleIndex, premiseIndex, logop, object_, objIndex, variable, relop, status, value):
        """ Sets the properties of a premise in a rule-based control.


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

        if self._ph is not None:
            self.errcode = self._lib.EN_setpremise(self._ph, int(ruleIndex), int(premiseIndex), logop, object_,
                                                   objIndex, variable, relop, status, c_double(value))
        else:
            self.errcode = self._lib.ENsetpremise(int(ruleIndex), int(premiseIndex), logop, object_,
                                                  objIndex, variable, relop, status, c_float(value))

        self.ENgeterror()

    def ENsetpremiseindex(self, ruleIndex, premiseIndex, objIndex):
        """ Sets the index of an object in a premise of a rule-based control.


        ENsetpremiseindex(ruleIndex, premiseIndex, objIndex)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        premiseIndex  the premise's index (starting from 1).
        objIndex      the index of the object (e.g. the index of a tank).
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setpremiseindex(self._ph, int(ruleIndex), int(premiseIndex), objIndex)
        else:
            self.errcode = self._lib.ENsetpremiseindex(int(ruleIndex), int(premiseIndex), objIndex)

        self.ENgeterror()

    def ENsetpremisestatus(self, ruleIndex, premiseIndex, status):
        """ Sets the status being compared to in a premise of a rule-based control.


        ENsetpremisestatus(ruleIndex, premiseIndex, status)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        premiseIndex  the premise's index (starting from 1).
        status        the status that the premise's object status is compared to (see RULESTATUS).
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setpremisestatus(self._ph, int(ruleIndex), int(premiseIndex), status)
        else:
            self.errcode = self._lib.ENsetpremisestatus(int(ruleIndex), int(premiseIndex), status)

        self.ENgeterror()

    def ENsetpremisevalue(self, ruleIndex, premiseIndex, value):
        """ Sets the value in a premise of a rule-based control.


        ENsetpremisevalue(ruleIndex, premiseIndex, value)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        premiseIndex  the premise's index (starting from 1).
        value         The value that the premise's variable is compared to.
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setpremisevalue(self._ph, int(ruleIndex), premiseIndex, c_double(value))
        else:
            self.errcode = self._lib.ENsetpremisevalue(int(ruleIndex), premiseIndex, c_float(value))

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

        if self._ph is not None:
            self.errcode = self._lib.EN_setqualtype(self._ph, qualcode, chemname.encode("utf-8"),
                                                    chemunits.encode("utf-8"), tracenode.encode("utf-8"))
        else:
            self.errcode = self._lib.ENsetqualtype(qualcode, chemname.encode("utf-8"),
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

        if self._ph is not None:
            self.errcode = self._lib.EN_setreport(self._ph, command.encode("utf-8"))
        else:
            self.errcode = self._lib.ENsetreport(command.encode("utf-8"))

        self.ENgeterror()

    def ENsetrulepriority(self, ruleIndex, priority):
        """ Sets the priority of a rule-based control.


        ENsetrulepriority(ruleIndex, priority)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        priority      the priority value assigned to the rule.
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setrulepriority(self._ph, int(ruleIndex), c_double(priority))
        else:
            self.errcode = self._lib.ENsetrulepriority(int(ruleIndex), c_float(priority))

        self.ENgeterror()

    def ENsetstatusreport(self, statuslevel):
        """ Sets the level of hydraulic status reporting.

        ENsetstatusreport(statuslevel)

        Parameters:
        statuslevel  a status reporting level code (see EN_StatusReport).


        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___reporting.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setstatusreport(self._ph, statuslevel)
        else:
            self.errcode = self._lib.ENsetstatusreport(statuslevel)

        self.ENgeterror()

    def ENsettankdata(self, index, elev, initlvl, minlvl, maxlvl, diam, minvol, volcurve):
        """ Sets a group of properties for a tank node.


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

        if self._ph is not None:
            self.errcode = self._lib.EN_settankdata(
                self._ph, index, c_double(elev), c_double(initlvl), c_double(minlvl),
                c_double(maxlvl), c_double(diam), c_double(minvol), volcurve.encode('utf-8'))
        else:
            self.errcode = self._lib.ENsettankdata(index, c_float(elev), c_float(initlvl), c_float(minlvl),
                                                   c_float(maxlvl), c_float(diam), c_float(minvol),
                                                   volcurve.encode('utf-8'))

        self.ENgeterror()

    def ENsetthenaction(self, ruleIndex, actionIndex, linkIndex, status, setting):
        """ Sets the properties of a THEN action in a rule-based control.


        ENsetthenaction(ruleIndex, actionIndex, linkIndex, status, setting)

        Parameters:
        ruleIndex     the rule's index (starting from 1).
        actionIndex   the index of the THEN action to retrieve (starting from 1).
        linkIndex     the index of the link in the action.
        status        the new status assigned to the link (see EN_RuleStatus)..
        setting       the new value assigned to the link's setting.

        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setthenaction(self._ph, int(ruleIndex), int(actionIndex), int(linkIndex),
                                                      status,
                                                      c_double(setting))
        else:
            self.errcode = self._lib.ENsetthenaction(int(ruleIndex), int(actionIndex), int(linkIndex),
                                                     status,
                                                     c_float(setting))

        self.ENgeterror()

    def ENsettimeparam(self, paramcode, timevalue):
        """ Sets the value of a time parameter.

        ENsettimeparam(paramcode, timevalue)

        Parameters:
        paramcode    a time parameter code (see EN_TimeParameter).
        timevalue    the new value of the time parameter (in seconds).
        """
        self.solve = 0

        if self._ph is not None:
            self.errcode = self._lib.EN_settimeparam(self._ph, c_int(paramcode), c_long(int(timevalue)))
        else:
            self.errcode = self._lib.ENsettimeparam(c_int(paramcode), c_long(int(timevalue)))

        self.ENgeterror()

    def ENsettitle(self, line1, line2, line3):
        """ Sets the title lines of the project.


        ENsettitle(line1, line2, line3)

        Parameters:
        line1   first title line
        line2   second title line
        line3   third title line
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_settitle(self._ph, line1.encode("utf-8"), line2.encode("utf-8"),
                                                 line3.encode("utf-8"))

        else:
            self.errcode = self._lib.ENsettitle(line1.encode("utf-8"), line2.encode("utf-8"),
                                                line3.encode("utf-8"))

        self.ENgeterror()

    def ENsetvertices(self, index, x, y, vertex):
        """ Assigns a set of internal vertex points to a link.


        ENsetvertices(index, x, y, vertex)

        Parameters:
        index      a link's index (starting from 1).
        x          an array of X-coordinates for the vertex points.
        y          an array of Y-coordinates for the vertex points.
        vertex     the number of vertex points being assigned.
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_setvertices(self._ph, int(index), (c_double * vertex)(*x),
                                                    (c_double * vertex)(*y), vertex)

        else:
            self.errcode = self._lib.ENsetvertices(int(index), (c_double * vertex)(*x),
                                                   (c_double * vertex)(*y), vertex)

        self.ENgeterror()

    def ENsolveH(self):
        """ Runs a complete hydraulic simulation with results for all time periods
        written to a temporary hydraulics file.

        ENsolveH()

        See also ENopenH, ENinitH, ENrunH, ENnextH, ENcloseH
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_solveH(self._ph)

        else:
            self.errcode = self._lib.ENsolveH()

        self.ENgeterror()
        return

    def ENsolveQ(self):
        """ Runs a complete water quality simulation with results at uniform reporting
        intervals written to the project's binary output file.

        ENsolveQ()

        See also ENopenQ, ENinitQ, ENrunQ, ENnextQ, ENcloseQ
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html"""

        if self._ph is not None:
            self.errcode = self._lib.EN_solveQ(self._ph)

        else:
            self.errcode = self._lib.ENsolveQ()

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
        tleft = c_long()

        if self._ph is not None:
            self.errcode = self._lib.EN_stepQ(self._ph, byref(tleft))

        else:
            self.errcode = self._lib.ENstepQ(byref(tleft))

        self.ENgeterror()
        return tleft.value

    def ENusehydfile(self, hydfname):
        """ Uses a previously saved binary hydraulics file to supply a project's hydraulics.

        ENusehydfile(hydfname)

        Parameters:
        hydfname  the name of the binary file containing hydraulic results.

        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_usehydfile(self._ph, hydfname.encode("utf-8"))

        else:
            self.errcode = self._lib.ENusehydfile(hydfname.encode("utf-8"))

        self.ENgeterror()
        return

    def ENwriteline(self, line):
        """ Writes a line of text to a project's report file.

        ENwriteline(line)

        Parameters:
        line         a text string to write.
        """

        if self._ph is not None:
            self.errcode = self._lib.EN_writeline(self._ph, line.encode("utf-8"))

        else:
            self.errcode = self._lib.ENwriteline(line.encode("utf-8"))

        self.ENgeterror()


class epanetmsxapi(error_handler):
    """example msx = epanetmsxapi()"""

    def __init__(self, msxfile='', loadlib=True, ignore_msxfile=False, customMSXlib=None, display_msg=True,
                 msxrealfile=''):
        self.display_msg = display_msg
        self.customMSXlib = customMSXlib
        if customMSXlib is not None:
            self.MSXLibEPANET = customMSXlib
            loadlib = False
            self.msx_lib = cdll.LoadLibrary(self.MSXLibEPANET)
            self.MSXLibEPANETPath = os.path.dirname(self.MSXLibEPANET)
            self.msx_error = self.msx_lib.MSXgeterror
            self.msx_error.argtypes = [c_int, c_char_p, c_int]
        if loadlib:
            ops = platform.system().lower()
            if ops in ["windows"]:
                self.MSXLibEPANET = os.path.join(epyt_root, os.path.join("libraries", "win", "epanetmsx.dll"))
            elif ops in ["darwin"]:
                self.MSXLibEPANET = os.path.join(epyt_root, os.path.join("libraries", "mac", "epanetmsx.dylib"))
            else:
                self.MSXLibEPANET = os.path.join(epyt_root, os.path.join("libraries", "glnx", "epanetmsx.so"))

            self.msx_lib = cdll.LoadLibrary(self.MSXLibEPANET)
            self.MSXLibEPANETPath = os.path.dirname(self.MSXLibEPANET)

            self.msx_error = self.msx_lib.MSXgeterror
            self.msx_error.argtypes = [c_int, c_char_p, c_int]

        if not ignore_msxfile:
            self.MSXopen(msxfile, msxrealfile)

    def MSXopen(self, msxfile, msxrealfile):
        """
        Open MSX file
        filename - Arsenite.msx or use full path

        Example:
            msx.MSXopen(filename)
            msx.MSXopen(Arsenite.msx)
        """
        if not os.path.exists(msxfile):
            raise FileNotFoundError(f"File not found: ")

        if self.display_msg:
            msxname = os.path.basename(msxrealfile)
            if self.customMSXlib is None:
                print(f"EPANET-MSX version {__msxversion__} loaded.")

        self.errcode = self.msx_lib.MSXopen(c_char_p(msxfile.encode('utf-8')))
        if self.errcode != 0:
            self.MSXerror(self.errcode)
            # if self.errcode == 520:
            #     if self.display_msg:
            #         print(f"MSX file {msxname}.msx loaded successfully.")
            if self.errcode == 503:
                if self.display_msg:
                    print("Error 503 may indicate a problem with the MSX file or the MSX library.")
        else:
            if self.display_msg:
                print(f"MSX file {msxname}.msx loaded successfully.")

    def MSXclose(self):
        """  Close .msx file
            example : msx.MSXclose()"""
        self.errcode = self.msx_lib.MSXclose()
        if self.errcode != 0:
            self.MSXerror(self.errcode)
        return self.errcode

    def MSXerror(self, err_code):
        """ Function that every other function uses in case of an error """
        errmsg = create_string_buffer(256)
        self.msx_error(err_code, errmsg, 256)
        print(errmsg.value.decode())

    def MSXgetindex(self, obj_type, obj_id):
        """ Retrieves the number of objects of a specific type
          MSXgetcount(obj_type, obj_id)

          Parameters:
               obj_type: code type of object being sought and must be one of the following
               pre-defined constants:
               MSX_SPECIES (for a chemical species) the number 3
               MSX_CONSTANT (for a reaction constant) the number 6
               MSX_PARAMETER (for a reaction parameter) the number 5
               MSX_PATTERN (for a time pattern) the number 7

               obj_id: string containing the object's ID name
          Returns:
              The index number (starting from 1) of object of that type with that specific name."""
        obj_type = c_int(obj_type)
        # obj_id=c_char_p(obj_id)
        index = c_int()
        self.errcode = self.msx_lib.MSXgetindex(obj_type, obj_id.encode("utf-8"), byref(index))
        if self.errcode != 0:
            Warning(self.MSXerror(self.errcode))
        return index.value

    def MSXgetID(self, obj_type, index, id_len=80):
        """ Retrieves the ID name of an object given its internal
            index number
            msx.MSXgetID(obj_type, index, id_len)
            print(msx.MSXgetID(3,1,8))

            Parameters:
                obj_type: type of object being sought and must be on of the
                following pre-defined constants:
                MSX_SPECIES (for chemical species)
                MSX_CONSTANT(for reaction constant)
                MSX_PARAMETER(for a reaction parameter)
                MSX_PATTERN (for a time pattern)

                index: the sequence number of the object (starting from 1
                as listed in the MSX input file)

                id_len: the maximum number of characters that id can hold

                Returns:
                    id object's ID name"""

        obj_id = create_string_buffer(id_len + 1)
        self.errcode = self.msx_lib.MSXgetID(obj_type, index, obj_id, id_len)
        if self.errcode != 0:
            Warning(self.MSXerror(self.errcode))
        return obj_id.value.decode()

    def MSXgetIDlen(self, obj_type, index):
        """Retrieves the number of characters in the ID name of an MSX
           object given its internal index number
           msx.MSXgetIDlen(obj_type, index)
           print(msx.MSXgetIDlen(3,3))
           Parameters:
            obj_type: type of object being sought and must be on of the
                  following pre-defined constants:
                  MSX_SPECIES (for chemical species)
                  MSX_CONSTANT(for reaction constant)
                  MSX_PARAMETER(for a reaction parameter)
                  MSX_PATTERN (for a time pattern)

            index: the sequence number of the object (starting from 1
                   as listed in the MSX input file)

            Returns : the number of characters in the ID name of MSX object

            """
        len = c_int()
        self.errcode = self.msx_lib.MSXgetIDlen(obj_type, index, byref(len))
        if self.errcode:
            Warning(self.MSXerror(self.errcode))
        return len.value

    def MSXgetspecies(self, index):
        """ Retrieves the attributes of a chemical species given its
            internal index number
            msx.MSXgetspecies(index)
            msx.MSXgetspecies(1)
            Parameters:
             index : integer -> sequence number of the species

            Returns:
                type : is returned with one of the following pre-defined constants:
                       MSX_BULK (defined as 0) for a bulk water species , or
                       MSX_WALL (defined as 1) for a pipe wall surface species
                units: mass units that were defined for the species in question
                atol : the absolute concentration tolerance defined for the species.
                rtol : the relative concentration tolerance defined for the species.  """
        type = c_int()
        units = create_string_buffer(16)
        atol = c_double()
        rtol = c_double()

        self.errcode = self.msx_lib.MSXgetspecies(
            index, byref(type), units, byref(atol), byref(rtol))

        if type.value == 0:
            type = 'BULK'
        elif type.value == 1:
            type = 'WALL'

        if self.errcode:
            Warning(self.MSXerror(self.errcode))
        return type, units.value.decode("utf-8"), atol.value, rtol.value

    def MSXgetcount(self, code):
        """ Retrieves the number of objects of a specific type
            MSXgetcount(code)

            Parameters:
                 code type of object being sought and must be one of the following
                 pre-defined constants:
                 MSX_SPECIES (for a chemical species) the number 3
                 MSX_CONSTANT (for a reaction constant) the number 6
                 MSX_PARAMETER (for a reaction parameter) the number 5
                 MSX_PATTERN (for a time pattern) the number 7
            Returns:
                The count number of object of that type.
         """
        count = c_int()
        self.errcode = self.msx_lib.MSXgetcount(code, byref(count))
        if self.errcode:
            Warning(self.MSXerror(self.errcode))
        return count.value

    def MSXgetconstant(self, index):
        """ Retrieves the value of a particular rection constant  """
        """msx.MSXgetconstant(index)
        msx.MSXgetconstant(1)"""
        """" Parameters:
        index : integer is the sequence number of the reaction
                constant ( starting from 1 ) as it 
                appeared in the MSX input file

        Returns: value -> the value assigned to the constant.    """
        value = c_double()
        self.errcode = self.msx_lib.MSXgetconstant(index, byref(value))
        if self.errcode:
            Warning(self.MSXerror(self.errcode))
        return value.value

    def MSXgetparameter(self, obj_type, index, param):
        """Retrieves the value of a particular reaction parameter for a given
           pipe
           msx.MSXgetparameter(obj_type, index, param)
           msx.MSXgetparameter(1,1,1)
           Parameters:
               obj_type: is type of object being queried and must be either:
                    MSX_NODE (defined as 0) for a node or
                    MSX_LINK(defined as 1) for alink

               index: is the internal sequence number (starting from 1)
                      assigned to the node or link

               param: the sequence number of the parameter (starting from 1
                      as listed in the MSX input file)

               Returns:
                   value : the value assigned to the parameter for the node or link
                           of interest.        """
        value = c_double()
        self.errcode = self.msx_lib.MSXgetparameter(obj_type, index, param, byref(value))
        if self.errcode:
            Warning(self.MSXerror(self.errcode))
        return value.value

    def MSXgetpatternlen(self, pattern_index):
        """Retrieves the number of time periods within a source time pattern

         MSXgetpatternlen(pattern_index)

        Parameters:
             pattern_index:  the internal sequence number (starting from 1)
                             of the pattern as it appears in the MSX input file.

        Returns:
             len:   the number of time periods (and therefore number of multipliers)
                   that appear in the pattern."""
        len = c_int()
        self.errcode = self.msx_lib.MSXgetpatternlen(pattern_index, byref(len))
        if self.errcode:
            Warning(self.MSXerror(self.errcode))
        return len.value

    def MSXgetpatternvalue(self, pattern_index, period):
        """  Retrieves the multiplier at a specific time period for a
             given source time pattern
            msx.MSXgetpatternvalue(pattern_index, period)
            msx.MSXgetpatternvalue(1,1)
             Parameters:
                 pattern_index: the internal sequence number(starting from 1)
                 of the pattern as it appears in the MSX input file

                 period: the index of the time period (starting from 1) whose
                 multiplier is being sought """
        value = c_double()
        self.errcode = self.msx_lib.MSXgetpatternvalue(pattern_index, period, byref(value))
        if self.errcode:
            Warning(self.MSXerror(self.errcode))
        return value.value

    def MSXgetinitqual(self, obj_type, index, species):
        """  Retrieves the intial concetration of a particular chemical species
             assigned to a specific node or link of the pipe network
            msx.MSXgetinitqual(obj_type, index)
            msx.MSXgetinitqual(1,1,1)
             Parameters:

                 type : type of object being queeried and must be either:
                        MSX_NODE (defined as 0) for a node or ,
                        MSX_LINK (defined as 1) for a link

                 index : the internal sequence number (starting from 1) assigned
                         to the node or link

                 species: the sequence number of the species (starting from 1)

                 Returns:
                        value: the initial concetration of the species at the node or
                               link of interest."""
        value = c_double()
        obj_type = c_int(obj_type)
        species = c_int(species)
        index = c_int(index)
        self.errcode = self.msx_lib.MSXgetinitqual(obj_type, index, species, byref(value))
        if self.errcode:
            Warning(self.MSXerror(self.errcode))
        return value.value

    def MSXgetsource(self, node_index, species_index):
        """ Retrieves information on any external source of a particular
            chemical species assigned to a specific node or link of the pipe
            network.
            msx.MSXgetsource(node_index, species_index)
            msx.MSXgetsource(1,1)

            Parameters:
                node_index: the internal sequence number (starting from 1)
                assigned to the node of interest.

                species_index: the sequence number of the species of interest
                (starting from 1 as listed in MSX input file)
            Returns:

                type: the type of external source to be utilized and will be one of
                     the following predefined constants:
                    MSX_NOSOURCE (defined as -1) for no source
                    MSX_CONCEN (defined as 0) for a concetration sourc
                    MSX_MASS (defined as 1) for a mass booster source
                    MSX_SETPOINT (defined as 2) for a setpoint source
                    MSX_FLOWPACE (defined as 3) for a flow paced source

                level: the baseline concentration ( or mass flow rate) of the source)

                pat : the index of the time pattern used to add variability to the
                      the source's baseline level (and will be 0 if no pattern
                      was defined for the source)
              """
        type = c_int()
        level = c_double()
        pattern = c_int()
        node_index = c_int(node_index)
        self.errcode = self.msx_lib.MSXgetsource(node_index, species_index,
                                        byref(type), byref(level), byref(pattern))

        if type.value == -1:
            type = 'NOSOURCE'
        elif type.value == 0:
            type = 'CONCEN'
        elif type.value == 1:
            type = 'MASS'
        elif type.value == 2:
            type = 'SETPOINT'
        elif type.value == 3:
            type = 'FLOWPACED'

        if self.errcode:
            Warning(self.MSXerror(self.errcode))

        return type, level.value, pattern.value

    def MSXsaveoutfile(self, filename):
        """ Saves water quality results computed for each node, link
            and reporting time period to a named binary file.
            msx.MSXsaveoutfile(filename)
            msx.MSXsaveoufile(Arsenite.msx)

            Parameters:
                filename: name of the permanent output results file"""
        self.errcode = self.msx_lib.MSXsaveoutfile(filename.encode())
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXsavemsxfile(self, filename):
        """ Saves the data associated with the current MSX project into a new
            MSX input file
            msx.MSXsavemsxfile(filename)
            msx.MSXsavemsxfile(Arsenite.msx)

            Parameters:
                filename: name of the file to which data are saved"""
        self.errcode = self.msx_lib.MSXsavemsxfile(filename.encode())
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXsetconstant(self, index, value):
        """ Assigns a new value to a specific reaction constant
            msx.MSXsetconstant(index, value)
            msx.MSXsetconstant(1,10)"""
        """" Parameters
             index : integer -> is the sequence number of the reaction
             constant ( starting from 1 ) as it appeared in the MSX
             input file

             Value: float -> the new value to be assigned to the constant."""

        value = c_double(value)
        self.errcode = self.msx_lib.MSXsetconstant(index, value)
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXsetparameter(self, obj_type, index, param, value):
        """ Assigns a value to a particular reaction parameter for a given pipe
            or tank within the pipe network
            msx.MSXsetparameter(obj_type, index, param, value)
            msx.MSXsetparameter(1,1,1,15)
            Parameters:
                 obj_type: is type of object being queried and must be either:
                    MSX_NODE (defined as 0) for a node or
                    MSX_LINK (defined as 1) for a link

               index: is the internal sequence number (starting from 1)
                      assigned to the node or link

               param: the sequence number of the parameter (starting from 1
                      as listed in the MSX input file)

               value: the value to be assigned to the parameter for the node or
                      link of interest.                 """
        value = c_double(value)
        self.errcode = self.msx_lib.MSXsetparameter(obj_type, index, param, value)
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXsetinitqual(self, obj_type, index, species, value):
        """  Assigns an initial concetration of a particular chemical species
             node or link of the pipe network
             msx.MSXsetinitqual(obj_type, index, species, value)
             msx.MSXsetinitqual(1,1,1,15)
             Parameters:
                 type: type of object being queried and must be either :
                       MSX_NODE(defined as 0) for a node or
                       MSX_LINK(defined as 1) for a link
                 index: integer -> the internal sequence number (starting from 1)
                        assigned to the node or link

                 species: the sequence number of the species (starting from 1 as listed in
                 MASx input file)

                 value: float -> the initial concetration of the species to be applied at the node or link
                        of interest.
                 """

        value = c_double(value)
        self.errcode = self.msx_lib.MSXsetinitqual(obj_type, index, species, value)
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXsetpattern(self, index, factors, nfactors):
        """Assigns a new set of multipliers to a given MSX source time pattern
            MSXsetpattern(index,factors,nfactors)

            Parameters:
                index: the internal sequence number (starting from 1)
                       of the pattern as it appers in the MSX input file
                factors: an array of multiplier values to replace those previously used by
                         the pattern
                nfactors: the number of entries in the multiplier array/ vector factors"""
        if isinstance(index, int):
            index = c_int(index)
        nfactors = c_int(nfactors)
        DoubleArray = c_double * len(factors)
        mult_array = DoubleArray(*factors)
        self.errcode = self.msx_lib.MSXsetpattern(index, mult_array, nfactors)
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXsetpatternvalue(self, pattern, period, value):
        """Assigns a new value to the multiplier for a specific time period
                      in a given MSX source time pattern.
            msx.MSXsetpatternvalue(pattern, period, value)
            msx.MSXsetpatternvalue(1,1,10)
           Parameters:
               pattern: the internal sequence number (starting from 1) of the
               pattern as it appears in the MSX input file.

               period: the time period (starting from 1) in the pattern to be replaced
               value:  the new multiplier value to use for that time period."""
        value = c_double(value)
        self.errcode = self.msx_lib.MSXsetpatternvalue(pattern, period, value)
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXsolveQ(self):
        """ Solves for water quality over the entire simulation period
            and saves the results to an internal scratch file
            msx.MSXsolveQ()"""
        self.errcode = self.msx_lib.MSXsolveQ()
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXsolveH(self):
        """ Solves for system hydraulics over the entire simulation period
            saving results to an internal scratch file
            msx.MSXsolveH() """
        self.errcode = self.msx_lib.MSXsolveH()
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXaddpattern(self, pattern_id):
        """Adds a newm empty MSX source time pattern to an MSX project
                MSXaddpattern(pattern_id)
            Parameters:
                pattern_id: the name of the new pattern """
        self.errcode = self.msx_lib.MSXaddpattern(pattern_id.encode("utf-8"))
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXusehydfile(self, filename):
        """             """
        self.errcode = self.msx_lib.MSXusehydfile(filename.encode())
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXstep(self):
        """Advances the water quality solution through a single water quality time
           step when performing a step-wise simulation

           t, tleft = MSXstep()
           Returns:
               t : current simulation time at the end of the step(in secconds)
               tleft: time left in the simulation (in secconds)
           """
        if platform.system().lower() in ["windows"]:
            t = c_double()
            tleft = c_double()
        else:
            t = c_double()
            tleft = c_long()
        self.errcode = self.msx_lib.MSXstep(byref(t), byref(tleft))

        if self.errcode:
            Warning(self.MSXerror(self.errcode))

        return t.value, tleft.value

    def MSXinit(self, flag):
        """Initialize the MSX system before solving for water quality results
           in the step-wise fashion

           MSXinit(flag)

           Parameters:
               flag:  Set the flag to 1 if the water quality results should be saved
                      to a scratch binary file, or 0 if not
           """
        self.errcode = self.msx_lib.MSXinit(flag)
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXreport(self):
        """ Writes water quality simulations results as instructed by
            MSX input file to a text file.
            msx.MSXreport()"""
        self.errcode = self.msx_lib.MSXreport()
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXgetqual(self, type, index, species):
        """Retrieves a chemical species concentration at a given node
           or the average concentration along a link at the current sumulation
           time step.

           MSXgetqual(type, index, species)

           Parameters:
               type: type of object being queried and must be either:
                    MSX_NODE ( defined as 0) for a node,
                    MSX_LINK (defined as 1) for a link
               index: then internal sequence number (starting from 1)
                      assigned to the node or link.
               species is the sequence number of the species (starting from 1
               as listed in the MSX input file)

           Returns:
               The value of the computed concentration of the species at the current
               time period.
        """

        value = 0
        value = c_double(value)
        self.errcode = self.msx_lib.MSXgetqual(type, index, species, byref(value))
        if self.errcode:
            Warning(self.MSXerror(self.errcode))
        return value.value

    def MSXsetsource(self, node, species, type, level, pat):
        """"Sets the attributes of an external source of particular chemical
            species to specific node of the pipe network
            msx.setsource(node, species, type, level, pat)
            msx.MSXsetsource(1,1,3,10.565,1)
            Parameters:
                node: the internal sequence number (starting from1) assigned
                      to the node of interest.

                species: the sequence number of the species of interest (starting
                         from 1 as listed in the MSX input file)

                type: the type of external source to be utilized and will be one of
                      the following predefined constants:
                      MSX_NOSOURCE (defined as -1) for no source
                      MSX_CONCEN (defined as 0) for a concetration source
                      MSX_MASS (defined as 1) for a mass booster source
                      MSX_SETPOINT (defined as 2) for a setpoint source
                      MSX_FLOWPACE (defined as 3) for a flow paced source

                level: the baseline concetration (or mass flow rate) of the source

                pat: the index of the time pattern used to add variability to the
                     source's baseline level ( use 0 if the source has a constant strength)     """
        level = c_double(level)

        pat = c_int(pat)
        type = c_int(type)
        self.errcode = self.msx_lib.MSXsetsource(node, species, type, level, pat)
        if self.errcode:
            Warning(self.MSXerror(self.errcode))

    def MSXgeterror(self, err):
        """Returns the text for an error message given its error code.
        msx.MSXgeterror(err)
        msx.MSXgeterror(516)
        Parameters:
            err: the code number of an error condition generated by EPANET-MSX

        Returns:
            errmsg: the text of the error message corresponding to the error code"""
        errmsg = create_string_buffer(80)
        e = self.msx_lib.MSXgeterror(err, errmsg, 80)

        # if e:
        #     # Warning(errmsg.value.decode())
        #     print(f"{red}EPANET Error: {errmsg.value.decode()}{reset}")
        return errmsg.value.decode()

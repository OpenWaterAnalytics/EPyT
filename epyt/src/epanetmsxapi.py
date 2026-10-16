import os
import platform
import re
import warnings
from contextlib import suppress
from shutil import copy2
from types import SimpleNamespace

from epyt import __version__, __msxversion__, __lastupdate__, epyt_root

from .epanet_cffi_compat import ffi, cdll, byref, create_string_buffer, c_uint64, c_void_p, c_int, c_double, c_float, \
    c_long, \
    c_char_p, funcptr_null


class epanetmsxapi:
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
            elif ops in ["emscripten"]:
                # Pyodide: EPANET-MSX is in the EPANET library, so that it
                # works on the network EPANET has open
                self.MSXLibEPANET = os.path.join(epyt_root, os.path.join("libraries", "emscripten", "libepanet2.so"))
            else:
                self.MSXLibEPANET = os.path.join(epyt_root, os.path.join("libraries", "glnx", "epanetmsx.so"))

            self.msx_lib = cdll.LoadLibrary(self.MSXLibEPANET)
            self.MSXLibEPANETPath = os.path.dirname(self.MSXLibEPANET)

            self.msx_error = self.msx_lib.MSXgeterror
            # self.msx_error.argtypes = [c_int, c_char_p, c_int]

        if not ignore_msxfile:
            if msxrealfile == '':
                self.MSXTempFile = msxfile[:-4] + '_temp.msx'
                copy2(msxfile, self.MSXTempFile)
                self.MSXopen(msxfile, self.MSXTempFile)
            else:
                self.MSXTempFile = msxfile
                self.MSXopen(self.MSXTempFile, msxrealfile)

    def MSXopen(self, msxfile, msxrealfile=None, ignore_error=True):
        """
        Open MSX file
        filename - Arsenite.msx or use full path

        Example:
            msx.MSXopen(filename)
            msx.MSXopen(Arsenite.msx)
        """
        if not os.path.exists(msxfile):
            raise FileNotFoundError(f"File not found: ")

        if msxrealfile is None:
            msxrealfile = msxfile

        if self.display_msg:
            msxname = os.path.basename(msxrealfile)
            if self.customMSXlib is None and ignore_error:
                print(f"EPANET-MSX version {__msxversion__} loaded.")

        self.errcode = self.msx_lib.MSXopen(c_char_p(msxfile.encode('utf-8')))
        if self.errcode != 0:
            if ignore_error:
                self.MSXerror(self.errcode)
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
        self.msx_error(err_code, byref(errmsg), 256)
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
        self.errcode = self.msx_lib.MSXgetID(obj_type, index, byref(obj_id), id_len)
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
            index, byref(type), byref(units), byref(atol), byref(rtol))

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

        """ Uses hyd file            """
        err = self.msx_lib.MSXusehydfile(filename.encode())
        if err:
            Warning(self.MSXerror(err))

    def MSXstep(self):
        """Advances the water quality solution through a single water quality time
           step when performing a step-wise simulation

           t, tleft = MSXstep()
           Returns:
               t : current simulation time at the end of the step(in secconds)
               tleft: time left in the simulation (in secconds)
           """
        # EPANET-MSX 2.0 returns both as doubles (the Pyodide library is
        # built from it: a 4-byte long would take only half of tleft there)
        if platform.system().lower() in ["windows", "emscripten"]:
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
        value = c_double()
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
        self.msx_lib.MSXgeterror(err, byref(errmsg), 80)

        # if e:
        #     # Warning(errmsg.value.decode())
        #     print(f"{red}EPANET Error: {errmsg.value.decode()}{reset}")
        return errmsg.value.decode()

    def MSXgetoptions(self):
        """ Retrieves all the options.
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
        """
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

    import os
    from shutil import copy2
    from contextlib import suppress

    import os
    import warnings
    from shutil import copy2

    def MSXsetoptions(self, param=None, change=None, **kwargs):
        keys = {
            "AREA_UNITS", "RATE_UNITS", "SOLVER", "COUPLING", "TIMESTEP",
            "ATOL", "RTOL", "COMPILER", "SEGMENTS", "PECLET"
        }

        updates = {}
        if param is not None:
            updates[str(param)] = change
        updates.update(kwargs)
        updates = {k: v for k, v in updates.items() if k in keys}
        if not updates:
            return 0

        src = "options_section.msx"
        tmp = "options_section_tmp.msx"

        try:
            self.MSXsavemsxfile(src)
            if not os.path.exists(src):
                warnings.warn("Please load MSX File.")
                return 0

            with open(src, "r", encoding="utf-8") as f:
                lines = f.readlines()

            try:
                opt_i = next(i for i, l in enumerate(lines) if l.strip() == "[OPTIONS]")
            except StopIteration:
                lines.insert(0, "[OPTIONS]\n")
                opt_i = 0

            def set_or_insert(k, v):
                nonlocal opt_i
                idx = next((i for i, l in enumerate(lines) if l.strip().startswith(k)), -1)
                line = f"{k}\t{v}\n"
                if idx != -1:
                    lines[idx] = line
                else:
                    lines.insert(opt_i + 1, line)
                    opt_i += 1

            for k, v in updates.items():
                set_or_insert(k, v)

            with open(tmp, "w", encoding="utf-8") as f:
                f.writelines(lines)

            copy2(tmp, self.MSXTempFile)
            self.MSXopen(self.MSXTempFile, ignore_error=False)

        finally:
            if os.path.exists(src):
                os.remove(src)
            if os.path.exists(tmp):
                os.remove(tmp)

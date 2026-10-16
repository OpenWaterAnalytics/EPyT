import os
import sys
import warnings
from functools import partial
from pathlib import Path

from epyt import epyt_root

from .epanet_cffi_compat import cdll, byref, create_string_buffer, c_uint64, c_void_p, c_int, c_double, c_float, c_long, \
    c_char_p, funcptr_null, EN_Project_p


def _default_lib_path():
    base = Path(epyt_root) / "libraries"
    if sys.platform.startswith("win"):
        return base / "win" / "epanet2.dll"
    elif sys.platform == "darwin":
        return base / "mac" / "libepanet2.dylib"
    elif sys.platform == "emscripten":
        # Pyodide (Python in the browser): EPANET and EPANET-MSX in one
        # WebAssembly library (built by pyodide/build_libs.sh)
        return base / "emscripten" / "libepanet2.so"
    else:
        return base / "glnx" / "libepanet2.so"


def _load_library(path_str: str):
    lib = _LIB_CACHE.get(path_str)
    if lib is None:
        # Support compat layers that expose either .LoadLibrary(...) or are callable (dlopen)
        loader = getattr(cdll, "LoadLibrary", None)
        lib = loader(path_str) if loader else cdll(path_str)
        _LIB_CACHE[path_str] = lib
    return lib


_DEFAULT_LIB_PATH = str(_default_lib_path())
_LIB_CACHE = {}


class epanetapi:
    """
    EPANET Toolkit functions - API
    """

    __slots__ = ("_lib", "errcode", "inpfile", "rptfile", "binfile",
                 "_ph", "LibEPANET", "LibEPANETpath", "solve", "_t_long",
                 "_openH", "_runH", "_nextH", "_close", "_closeH", "_initH", "_openQ",
                 "_runQ", "_nextQ", "_closeQ", "_initQ", "_t_int", "_t_double", "_t_float",
                 "_t_char_p", "_t_void_p")

    EN_MAXID = 32  # Maximum length of ID names

    def __init__(self, version=2.3, ph=False, loadlib=True, customlib=None):
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
        self.solve = 0

        # Resolve library path (absolute)
        if customlib:
            p = Path(customlib)
            self.LibEPANET = str((p if p.is_absolute() else (Path.cwd() / p)).resolve())
            loadlib = False
        else:
            self.LibEPANET = _DEFAULT_LIB_PATH

        self.LibEPANETpath = os.path.dirname(self.LibEPANET)

        if loadlib:
            self._lib = _load_library(self.LibEPANET)

            self._t_int = c_int
            self._t_double = c_double()
            self._t_float = c_float()
            self._t_void_p = c_void_p()
            self._t_long = c_long()

            self._close = partial(self._lib.EN_close, self._ph) if self._ph is not None else self._lib.ENclose

            self._openH = partial(self._lib.EN_openH, self._ph) if self._ph is not None else self._lib.ENopenH
            self._runH = partial(self._lib.EN_runH, self._ph) if self._ph is not None else self._lib.ENrunH
            self._nextH = partial(self._lib.EN_nextH, self._ph) if self._ph is not None else self._lib.ENnextH
            self._closeH = partial(self._lib.EN_closeH, self._ph) if self._ph is not None else self._lib.ENcloseH
            self._initH = partial(self._lib.EN_initH, self._ph) if self._ph is not None else self._lib.ENinitH

            self._openQ = partial(self._lib.EN_openQ, self._ph) if self._ph is not None else self._lib.ENopenQ
            self._runQ = partial(self._lib.EN_runQ, self._ph) if self._ph is not None else self._lib.ENrunQ
            self._nextQ = partial(self._lib.EN_nextQ, self._ph) if self._ph is not None else self._lib.ENnextQ
            self._closeQ = partial(self._lib.EN_closeQ, self._ph) if self._ph is not None else self._lib.ENcloseQ
            self._initQ = partial(self._lib.EN_initQ, self._ph) if self._ph is not None else self._lib.ENinitQ

        if ph:
            self._ph = EN_Project_p()

    # Optional lazy accessor; loads on first use if loadlib=False
    @property
    def lib(self):
        if self._lib is None:
            self._lib = _load_library(self.LibEPANET)
        return self._lib

    def ENepanet(self, inpfile="", rptfile="", binfile=""):
        """ Runs a complete EPANET simulation
        Parameters:
        inpfile     Input file to use
        rptfile     Output file to report to
        binfile     Results file to generate
        """
        self.inpfile = c_char_p(inpfile)
        self.rptfile = c_char_p(rptfile)
        self.binfile = c_char_p(binfile)
        null_msg = funcptr_null("void (*)(char *)")

        self.errcode = self._lib.ENepanet(self.inpfile, self.rptfile, self.binfile, null_msg)
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
        err = self._close()
        self.errcode = err
        if err:
            self.ENgeterror()
        self._ph = None
        self._close = self._lib.ENclose

    def ENcloseH(self):
        """ Closes the hydraulic solver freeing all of its allocated memory.

        ENcloseH()

        See also  ENinitH, ENrunH, ENnextH
        """
        err = self._closeH()
        self.errcode = err
        if err:
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

    def ENsetcurvetype(self, index, type):
        """ Allow API clients to set a curve's type (e.g., EN_PUMP_CURVE, EN_VOLUME_CURVE, etc.).
        Input:   index = data curve index
                 type = type of data curve (see EN_CurveType)
                 Returns: error code
                 Purpose: sets the type assigned to a data curve"""
        index = c_int(index)
        if self._ph is not None:
            self.errcode = self._lib.EN_setcurvetype(self._ph, index, type)
        else:
            self.errcode = self._lib.ENsetcurvetype(index, type)
        self.ENgeterror()
        return self.errcode

    def ENsetvertex(self, index, vertex, x, y):
        """ Input:   index = link index
             vertex = index of a link vertex point
             x = vertex point's X-coordinate
             y = vertex point's Y-coordinate
          Returns: error code
          Purpose: sets the coordinates of a vertex point in a link"""
        index = c_int(index)
        vertex = c_int(vertex)

        if self._ph is not None:
            x = c_double(x)
            y = c_double(y)
            self.errcode = self._lib.EN_setvertex(self._ph, index, vertex, x, y)
        else:
            x = c_double(x)
            y = c_double(y)
            self.errcode = self._lib.ENsetvertex(index, vertex, x, y)
        self.ENgeterror()
        return self.errcode

    def ENtimetonextevent(self):
        """get the time to next event, and give a reason for the time step truncation"""
        eventType = c_int()  # pointer in C
        # duration = c_double() #long  pointer in C
        elementIndex = c_int()  # pointer in C

        if self._ph is not None:
            duration = c_double()  # not checked
            self.errcode = self._lib.EN_timetonextevent(self._ph, byref(eventType), byref(duration),
                                                        byref(elementIndex))
        else:
            duration = c_long()
            self.errcode = self._lib.ENtimetonextevent(byref(eventType), byref(duration), byref(elementIndex))
        self.ENgeterror()
        return eventType.value, duration.value, elementIndex.value

    def ENgetcontrolenabled(self, index):
        index = c_int(index)
        enabled = c_int()
        if self._ph is not None:
            self.errcode = self._lib.EN_getcontrolenabled(self._ph, index, byref(enabled))
        else:
            self.errcode = self._lib.ENgetcontrolenabled(index, byref(enabled))
        self.ENgeterror()
        return enabled.value

    def ENsetcontrolenabled(self, index, enabled):

        index = c_int(index)
        enabled = c_int(enabled)
        if self._ph is not None:
            self.errcode = self._lib.EN_setcontrolenabled(self._ph, index, enabled)
        else:
            self.errcode = self._lib.ENsetcontrolenabled(index, enabled)
        self.ENgeterror()
        return self.errcode

    def ENgetruleenabled(self, index):

        index = c_int(index)
        enabled = c_int()
        if self._ph is not None:
            self.errcode = self._lib.EN_getruleenabled(self._ph, index, byref(enabled))
        else:
            self.errcode = self._lib.ENgetruleenabled(index, byref(enabled))
        self.ENgeterror()
        return enabled.value

    def ENsetruleenabled(self, index, enabled):

        index = c_int(index)
        enabled = c_int(enabled)
        if self._ph is not None:
            self.errcode = self._lib.EN_setruleenabled(self._ph, index, enabled)
        else:
            self.errcode = self._lib.ENsetruleenabled(index, enabled)
        self.ENgeterror()
        return self.errcode

    def ENopenX(self, inpFile, rptFile, binFile):
        """Input:   inpFile = name of input file
                    rptFile = name of report file
                    binFile = name of binary output file
           Output:  none
           Returns: error code
           Purpose: reads an EPANET input file with errors allowed."""

        self.inpfile = bytes(inpFile, 'utf-8')
        self.rptfile = bytes(rptFile, 'utf-8')
        self.binfile = bytes(binFile, 'utf-8')
        if self._ph is not None:
            self._lib.EN_createproject(byref(self._ph))
            self._ph = self._ph.value
            self.errcode = self._lib.EN_openX(self._ph, self.inpfile, self.rptfile, self.binfile)
        else:
            self.errcode = self._lib.ENopenX(self.inpfile, self.rptfile, self.binfile)
        self.ENgeterror()

    def ENgetlinkvalues(self, property):
        """
          Input:   property = link property code (see EN_LinkProperty)
          Output:  values = array of link property values
          Returns: error code
          Purpose: retrieves property values for all links
        """

        EN_LINKCOUNT = 2
        num_links = self.ENgetcount(EN_LINKCOUNT)

        property = c_int(property)
        if self._ph is not None:
            values_array = (c_double * num_links)()
            self.errcode = self._lib.EN_getlinkvalues(self._ph, property, values_array)
        else:
            values_array = (c_float * num_links)()
            self.errcode = self._lib.ENgetlinkvalues(property, values_array)
        self.ENgeterror()
        return list(values_array)

    def ENloadpatternfile(self, filename, id):
        """ Input:   filename =  name of the file containing pattern data
            id = ID for the new pattern
            Purpose: loads time patterns from a file into a project under a specific pattern ID"""
        self.patternfile = bytes(filename, 'utf-8')
        if self._ph is not None:
            self.errcode = self._lib.EN_loadpatternfile(self._ph, self.patternfile, id)
        else:
            self.errcode = self._lib.ENloadpatternfile(self.patternfile, id)
        self.ENgeterror()

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
            warnings.warn(errmssg.value.decode())
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
        val = c_int()

        if self._ph is not None:
            self.errcode = self._lib.EN_getheadcurveindex(self._ph, c_int(pumpindex), byref(val))
        else:
            self.errcode = self._lib.ENgetheadcurveindex(c_int(pumpindex), byref(val))

        self.ENgeterror()
        return val.value

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
            fValue = self._t_double
            self.errcode = self._lib.EN_getnodevalue(self._ph, int(index), code_p, byref(fValue))
        else:
            fValue = self._t_float
            self.errcode = self._lib.ENgetnodevalue(int(index), code_p, byref(fValue))

        if self.errcode == 240:
            self.errcode = 0
            return None
        else:
            self.ENgeterror()
            return fValue.value

    def ENgetnodevalues(self, property):
        """
          Input:   property = node property code (see EN_NodeProperty)
          Output:  values = array of node property values
          Returns: error code
          Purpose: retrieves property values for all nodes
        """

        EN_NODECOUNT = 0
        num_nodes = self.ENgetcount(EN_NODECOUNT)

        property = c_int(property)
        if self._ph is not None:
            values_array = (c_double * num_nodes)()
            self.errcode = self._lib.EN_getnodevalues(self._ph, property, values_array)
        else:
            values_array = (c_float * num_nodes)()
            self.errcode = self._lib.ENgetnodevalues(property, values_array)
        if self.errcode != 240:
            self.ENgeterror()
        return list(values_array)

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
            self._lib.EN_createproject(byref(self._ph))
            try:
                self._ph = self._ph.ptr[0]
            except:
                pass
            self.errcode = self._lib.EN_init(self._ph, b"", b"", unitsType, headLossType)
        else:
            self.errcode = self._lib.ENinit(b"", b"", unitsType, headLossType)

        self.ENgeterror()

    def ENinitH(self, flag):
        """ Initializes a network prior to running a hydraulic analysis.

        ENinitH(flag)

        Parameters:
        flag    	a 2-digit initialization flag (see EN_InitHydOption).

        See also  ENinitH, ENrunH, ENnextH, ENreport, ENsavehydfile
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___hydraulics.html
        """
        err = self._initH(flag)
        self.errcode = err
        if err:
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
        err = self._initQ(saveflag)
        self.errcode = err
        if err:
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
        tstep = self._t_long
        err = self._nextH(byref(tstep))
        self.errcode = err
        if err:
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
        tstep = self._t_long
        err = self._nextQ(byref(tstep))
        self.errcode = err
        if err:
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
        err = self._openH()
        self.errcode = err
        if err:
            self.ENgeterror()
        return err

    def ENopenQ(self):
        """ Opens a project's water quality solver.

        ENopenQ()

        See also  ENopenQ, ENinitQ, ENrunQ, ENnextQ,
        ENstepQ, ENcloseQ
        OWA-EPANET Toolkit: http://wateranalytics.org/EPANET/group___quality.html
        """
        err = self._openQ()
        self.errcode = err
        if err:
            self.ENgeterror()
        return err

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
        t = self._t_long
        err = self._runH(byref(t))
        self.errcode = err
        if err:
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
        idx_ptr = self._t_int()
        idx_ptr.value = indexLink
        typ = self._t_int(paramcode)
        act = self._t_int(actionCode)

        if self._ph is not None:
            self.errcode = self._lib.EN_setlinktype(self._ph, byref(idx_ptr), typ, act)
        else:
            self.errcode = self._lib.ENsetlinktype(byref(idx_ptr), typ, act)

        self.ENgeterror()
        return idx_ptr.value

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
        return self.errcode

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
        return self.errcode

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
        return self.errcode

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

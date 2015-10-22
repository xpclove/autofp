#!/usr/bin/env python
##############################################################################
#
# diffpy.pyfullprof by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Wenduo Zhou, Jiwu Liu and Peng Tian
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################


"""Read uncertainty from Fullprof output file and 
insert these data to corresponding Fit instance.
"""

__id__="$Id: fpuncertaintyreader.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.exception import RietError

class FPUncertainty(object):
    """
    Import and export refined variable's uncertainty from Fullprof refinement

    Class Variable:
    @ _ParameterList: 


    Class Methods:
    *   Construction
    @   __init__                filename, filetype="out"
    @   importUncertainty   

    *   Information Retrieval
    @   exportToFit             myfit
    """
    __numopen__ = 0

    _FLAG1 = "SYMBOLIC NAMES AND INITIAL VALUES OF PARAMETERS TO BE VARIED"
    _FLAG2 = "SYMBOLIC NAMES AND FINAL VALUES AND SIGMA OF REFINED PARAMETERS"
    _FLAG3 = "Parameter number"
    _NAMEMAPDICT = {
                    "Ztherm":   "Zerot",
                    "Sig-2" :   "Sig2", 
                    "Sig-1" :   "Sig1", 
                    "Sig-0" :   "Sig0", 
                    "Alpha0":   "ALPH0",
                    "Alpha1":   "ALPH1",
                    "Gam-2" :   "Gam2",
                    "Gam-1" :   "Gam1",
                    "Gam-0" :   "Gam0",
                    "Alpha0":   "ALPH0",
                    "Alpha1":   "ALPH1",
                    "Beta0" :   "BETA0",
                    "Beta1" :   "BETA1",
                    "Xpar"  :   "X",
                    "Ypar"  :   "Y",
                    "Wleft" :   "WL",
                    "WRght" :   "WR", 
                    "Uleft" :   "UL",
                    "URght" :   "UR", 
                    "Vleft" :   "VL",
                    "VRght" :   "VR", 
                    "EtaPV" :   "Shape1",
                    "W-Cagl":   "W",
                    "U-Cagl":   "U",
                    "V-Cagl":   "V",
                    }

    def __init__(self, filename, filetype="out"):
        """
        initialization:

        Argument:
        - filename  :   str
        - filetype  :   str, "out" for .out file
                             "sum" for .sum file
        """
        self._ParameterList = []

        if filetype == "out":
            self._outfilename = filename
            self._sumfilename = None
        else:
            self._outfilename = None
            self._sumfilename = filename

        return


    def importUncertainty(self):
        """
        Parse the input file and put the data information to a database

        Return  :   None
        """
        if self._outfilename is not None:
            self.importUncertaintyOutFile()

        elif self._sumfilename is not None:
            self.importUncertaintySumFile()

        else:
            raise RietError()

        return


    def importUncertaintyOutFile(self):
        """
        parse the .out file and put the data information to a database

        Return  :   None
        """
        lineslist = self.readFile(self._outfilename)

        # 1. File Flag Line
        startlinenum = -1
        for lindex in xrange( len(lineslist) ):
            if lineslist[lindex].count(self._FLAG2) == 1:
                startlinenum = lindex
                break
       
        if startlinenum < 0:
            raise RietError()
        
        # 2. Get Informative Lines:
        infolineslist = []
        for lindex in xrange( startlinenum+1, len(lineslist) ):
            candline = lineslist[lindex]
            # 1. Find stop line
            if candline[0]=="=" and candline[1]==">":
                break

            # 2. Judge
            if candline.count(self._FLAG3) > 0:
                infolineslist.append(candline)

        # LOOP-OVER: for lindex in xrange( startlinenum+1, len(lineslist) )

        # 3. Parse to standard database
        for line in infolineslist:
            terms = line.split(":")[1].split("+/-")
            tp1   = terms[0].split()
            tp2   = terms[1].split()

            name   = tp1[0]
            valstr = tp1[1].split("(")[0]
            val    = float(valstr)
            sigstr = tp2[0]
            sig    = float(sigstr)

            nameinfotuple = self.parseNameOutFile(name)

            self._ParameterList.append( (nameinfotuple, val, sig) )

        # LOOP-OVER:  for line in infolineslist


        return


    def parseNameOutFile(self, name):
        """
        Parsing a Fullprof symbolic parameter name to a standard format for future understanding

        Argument:
        - name  :   str

        Return  :   list of uncertain length
                    1. ( pat, patnum, var name, index)
                    2. ( ph,  phanum, var name, index)
                    3. ( con, pat, patnum, ph,  phanum, var name, index)
        """
        # 1. split the terms by _, b/c the format is varname_ph/pat#_...
        terms    = name.split("_")
        numterms = len(terms)
        retlist  = []

        # 2. filter out the correct meaning
        for itm in xrange(numterms):
            term = terms[numterms-1-itm]

            if term.count("pat") > 0:
                patnum = int( term.split("pat")[1] )
                retlist.append("pat")
                retlist.append(patnum)

            elif term.count("ph") > 0 and term.count("Alpha") == 0:
                phanum = int( term.split("ph")[1] )
                retlist.append("ph")
                retlist.append(phanum)

            elif term.isdigit():
                retlist.append( int(term) )

            else:
                retlist.append( term )

        return retlist


    def exportToFit(self, myfit):
        """
        Export the current information to a Fit object

        Argument:
        - myfit :   diffpy.pyfullprof.Fit instance

        Return  :   None
        """
        import diffpy.pyfullprof.pattern as PTN

        for nameinfotuple, val, sig in self._ParameterList:
        
            # 1. From the suffix of the name, determine if the parameter
            #    belongs to pattern, phase, or contribution
            ispattern = False
            isphase = False
            iscontribution = False
            if nameinfotuple.count("pat") > 0:
                ispattern = True
            if nameinfotuple.count("ph") > 0:
                isphase = True
            if ispattern and isphase:
                iscontribution = True
                ispattern = False
                isphase = False

            # 2. Get parameter and its index
            parname = None
            index = None

            if ispattern:
                # background
                patnum  = nameinfotuple[1]
                pattern = myfit.get("Pattern")[patnum-1]
                if nameinfotuple[-1] == "Bck":
                    rietobj = pattern.get("Background")
                    bcknum  = nameinfotuple[-2]+1
                    if isinstance(rietobj, PTN.BackgroundPolynomial):
                        parname = "BACK"
                        index = bcknum-1
                    elif isinstance(rietobj, PTN.BackgroundUserDefined):
                        parname = "BCK"
                        index = bcknum-1
                    else:
                        errmsg = "1045-1:  Object Instance %-10s Unrecoganizable"% (rietobj.__class__.__name__)
                        print errmsg  
                else:
                    iname = nameinfotuple[-1]
                    if FPUncertainty._NAMEMAPDICT.has_key(iname):
                        iname = FPUncertainty._NAMEMAPDICT[iname]
                    rietobj, parname = pattern.locateParameter(iname)
            elif isphase:
                phanum = nameinfotuple[1]
                phase  = myfit.get("Phase")[phanum-1]
                # a. get all atom's name
                atomindexmap  = {}
                for atom in phase.get("Atom"):
                    atomname = atom.get("Name")
                    atomindexmap[atomname] = atom

                # b. see whether belonging to Atom's property
                atomnameslist = atomindexmap.keys()
                if atomnameslist.count(nameinfotuple[-2]) == 1:
                    atom = atomindexmap[nameinfotuple[-2]]
                    rietobj, parname = atom.locateParameter(nameinfotuple[-1])

                # c. if not atom's
                if rietobj is None:
                    iname = nameinfotuple[-1]
                    if FPUncertainty._NAMEMAPDICT.has_key(iname):
                        iname = FPUncertainty._NAMEMAPDICT[iname]
                    rietobj, parname = phase.locateParameter(iname)
            elif iscontribution:
                patnum  = nameinfotuple[1]
                phanum  = nameinfotuple[3]
                pattern = myfit.get("Pattern")[patnum-1]
                phase   = myfit.get("Phase")[phanum-1]
                contrib = myfit.getContribution(pattern, phase)
                # a. Lattice
                if nameinfotuple[-1] == "Cell":
                    rietobj, parname = phase.locateParameter(nameinfotuple[-2])
                else:
                    iname = nameinfotuple[-1]
                    if FPUncertainty._NAMEMAPDICT.has_key(iname):
                        iname = FPUncertainty._NAMEMAPDICT[iname]
                    rietobj, parname = contrib.locateParameter(iname)
            else:
                raise RietError("Parameter %s does not belong to a known case."%str(nameinfotuple))
            
            if parname is None:
                rstring = "%-20s ispat = %-10s ispha = %-10s iscon = %-10s"% \
                    (nameinfotuple, ispat, ispha, iscon)
                print "# 1045-Warning:  Implement this case! %-50s"% (rstring)
            else:
                if rietobj is None:
                    raise RietError("Parameter %s can not be found in the fit object."%parname)
                constraint = rietobj.getConstraint(parname, index)
                if constraint:
                    constraint.sigma = sig
                else:
                    raise RietError("No constraint is bound to the parameter '%s'"%parname)
            
            if 0:   # 1501
                print "1501:Par = %-10s  Val = %-15s  vs. input Val = %-15s  Sig = %-15s"% \
                    (parname, rietobj.get(parname).value(), val, sig)
            # END-DEBUG

        # LOOP-OVER: for nameinfotuple, val, sig in self._ParameterList

        return
    
    # END-DEF exportToFit(self, myfit)

    def readFile(self, fname):  
        """
        read and parse file
        """
        fpfile   = open(fname, "r")
        rawlines = fpfile.readlines()
        fpfile.close()

        lineslist = []
        for rline in rawlines:
            cline = rline.strip()
            if cline != "":
                lineslist.append(cline)
        
        rawlines[:] = []

        return lineslist

# END-CLASS FPUncertainty

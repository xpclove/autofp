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

"""class Fit - a class containing information to perform a multi-phase,
multi-pattern Rietveld refinement
"""
from __future__ import print_function

from future.utils import raise_
from builtins import str
from builtins import range
__id__ = "$Id: fit.py 6843 2013-01-09 22:14:20Z juhas $"

import os
import glob
import shutil

from diffpy.pyfullprof.refine import Refine
from diffpy.pyfullprof.rietveldclass import RietveldClass
from diffpy.pyfullprof.utilfunction import verifyType
from diffpy.pyfullprof.infoclass import ParameterInfo
from diffpy.pyfullprof.infoclass import BoolInfo
from diffpy.pyfullprof.infoclass import EnumInfo
from diffpy.pyfullprof.infoclass import FloatInfo
from diffpy.pyfullprof.infoclass import IntInfo
from diffpy.pyfullprof.infoclass import RefineInfo
from diffpy.pyfullprof.infoclass import StringInfo
from diffpy.pyfullprof.infoclass import ObjectInfo
from diffpy.pyfullprof.utilfunction import checkFileExistence
from diffpy.pyfullprof.exception import RietError

class Fit(RietveldClass):
    """
    Fit contains information for a single Rietveld refinement configuration

    attributes  

    banklist    --  list of integers,  index of banks used
    """
    ParamDict = { 
        # general information
        "Name":         StringInfo("Name",     "Fit Name",           "new fit"), \
        "Information":  StringInfo("Information", "Fit Information",  ""), \
        "physparam":    FloatInfo("physparam", "External Parameter", 0.0),  \
        # refinement solution information
        "Chi2":         FloatInfo("Chi2", "Chi^2", 0.0, '',  0.0, None),
        # refinement setup    information
        "Dum":          EnumInfo("Dum",        "Divergence Control", 0, \
                        {0: "Regular", \
                        1: "criterion of convergence is not applied when shifts are lower than a fraction of standard deviation", \
                        2: "stopped in case of local divergence", \
                        3: "reflection near excluded regions are not taken into account for Bragg R-factor"}, \
                        [0, 1, 2, 3]), 
        "Ias":          EnumInfo("Ias", "Reordering of Reflections", 0, 
                        {0: "At First Cycle",
                         1: "At Each Cycle"},
                        [0, 1]),
        "Cry":          EnumInfo("Cry",  "Job and Refinement Algorithm", 0,            \
                        {0: "Rietveld refinement", \
                        1: "Refinement of single crystal data or integrated intensity of powder data", \
                        2: "No least-square method is applied (Monte Carlo)", \
                        3: "Simulated Annearing"}, \
                        [0, 1, 2, 3]), 
        "Opt":          BoolInfo("Opt", "Calculation Optimization", False), 
        "Aut":          BoolInfo("Aut", "Automatic Mode for Refinement Codes Numbering", False),
        "NCY":          IntInfo("NCY", "Refinement Cycle Number", 1, 1, None),
        "Eps":          FloatInfo("Eps", "Convergence Precision", 0.1, '', 0.0, None),
        "R_at":         FloatInfo("R_at", "Atomic Relaxation Factor",       1.0),
        "R_an":         FloatInfo("R_an", "Anisotropic Relaxation Factor",  1.0),
        "R_pr":         FloatInfo("R_pr", "Profile Relaxation Factor",      1.0),
        "R_gl":         FloatInfo("R_gl", "Global Pamameter Relaxation Factor", 1.0),
        # output options
        "Mat":          EnumInfo("Mat", "Correlation Matrix Output", 1, 
                        {0: "no action", \
                        1:  "written in CODFIL.dat", \
                        2:  "diagonal of least square matrix is printed at every cycle"},
                        [0,1,2]),
        "Pcr":          EnumInfo("Pcr", "Upate .pcr file after refinement", 1,
                        {1: "CODFIL.pcr is re-written with updated parameters",
                        2: "A new input file is generated named CODFIL.new"},
                        [2,1]),
        "Syo":          EnumInfo("Syo", "Output of the symmetry operator", 0,
                        {0: "no action",
                        1:  "symmetry operators are written in CODFIL.out"},
                        [0,1]),
        "Rpa":          EnumInfo("Rpa", "Output .rpa file", 1, 
                        {-1:".cif file",
                        0: "no action",
                        1:  ".rpa file",
                        2:  ".sav file"},
                        [0,1,2]),
        "Sym":          EnumInfo("Sym", "Output .sym file", 1,
                        {0: "no cation",
                        1:  "prepare CODFIL.sym"},
                        [0,1]),
        "Sho":          BoolInfo("Sho", "Reduced output", False),
        "Nre":          IntInfo("Nre", "Number of restrainted parameters", 0),
    }

    ObjectDict  = {
        "Refine":               ObjectInfo("Refine", "Refine"),
    }

    ObjectListDict = {
        #"MonteCarlo":           ObjectInfo("MonteCarlo", "MonteCarlo", 0, 1),
        #"SimulatedAnnealing":   ObjectInfo("SimulatedAnneaing", "SimulatedAnnealing", 0, 1),      
        "Pattern":      ObjectInfo("PatternList", "Pattern", 1, None),
        "Phase":        ObjectInfo("PhaseList", "Phase", 1, None),
        "Contribution": ObjectInfo("ContributionList", "Contribution", 0, None),
    }


    def __init__(self, parent):
        """
        initialization: add a new Fit, and create the refine object belonged to this fit object
        """
        RietveldClass.__init__(self, parent)

        # init refine
        refineobj = Refine(None)
        self.set("Refine", refineobj)

        # bank information:  This is for some specific pattern data such as ".gss" with different bank
        self.banklist = []
        
        # internal data
        self.key = ''
        self._param_indices = {}
        self.updateParamIndices(self._param_indices)

        return

    def __str__(self):
        """
        customerized output
        """
        rstring  = ""

        rstring += RietveldClass.__str__(self)

        return rstring


    def getContribution(self, p1, p2):
        """
        get the contribution by pattern and phase
        p1: pattern/phase
        p2: phase/pattern

        return  --  (1) Contribution
                    (2) None if not exist
        """
        from diffpy.pyfullprof.pattern import Pattern
        from diffpy.pyfullprof.phase import Phase
        from diffpy.pyfullprof.contribution import Contribution

        phase   = None
        pattern = None
        if isinstance(p1, Pattern) and isinstance(p2, Phase):
            pattern = p1
            phase   = p2
        elif isinstance(p1, Phase) and isinstance(p2, Pattern):
            pattern = p2
            phase   = p1
        else:
            raise NotImplementedError("fit.getContribution:  p1 and p2 must be phase and pattern or pattern and phase")

        contributionlist = self.get("Contribution")
        for contribution in contributionlist:
            if contribution._ParentPhase == phase and contribution._ParentPattern == pattern:
                return contribution

        # if return will be None, then print out some debugging information
        if 0:
            contributionlist = self.get("Contribution")
            dbmsg  = "pyfullprof.core.Fit.getContribution():  Cannot Find a Matching Contribution!\n"
            dbmsg += "%-20s: Phase -- %-30s   Pattern -- %-30s\n"%("Input", repr(phase), repr(pattern)) 
            counts = 0
            for contribution in contributionlist:
                addrphase   = repr(contribution._ParentPhase)
                addrpattern = repr(contribution._ParentPattern)
                dbmsg += "%-20s: Phase -- %-30s  Pattern -- %-30s\n"%("Contribution "+str(counts), addrphase, addrpattern)
                counts += 1
            print(dbmsg)
        
        return None


   
    def getParamList(self):
        return self.Refine.constraints

    def updateFit(self, newfit):
        """Update self with the new fit, which is the resultant Fit instance.
        
        newfit --   an instance of Fit
        """
        # update Chi^2
        for paramname in self.ParamDict:
            self.set(paramname, newfit.get(paramname)) 
        for constraint in self.get("Refine").constraints[:]:
            if constraint.on:
                path = constraint.path
                val = newfit.getByPath(path)
                self.setByPath(path, val)
                
                #FIXME: it is a get-around of the engine bug
                newconstraint = newfit.getConstraintByPath(path)
                if newconstraint is not None:
                    constraint.sigma = newconstraint.sigma
                    
        for constraint in self.get("Refine").constraints[:]:
            print("                    %-10s    %-15s    %-15.6f+/- %-11.6f" \
            % ( constraint.name, constraint.varName, constraint.getValue(), 
                constraint.sigma))
        print("\n")
        return


    def validate(self, mode="Refine"):
        """
        validate the parameters, subclass and container to meet the refinement requirement

        Arguments
        - mode  :  string, validate mode, (Refine, Calculate)

        Return  :  Boolean 
        """
        rvalue = RietveldClass.validate(self)
        errmsg = ""

        # I. Synchronization of FulProf Parameter & Check Data File Existence
        for pattern in self.get("Pattern"):

            # 2.1 data file existence
            if mode == "Refine":
                exist = checkFileExistence(pattern.get("Datafile"))
                if not exist:
                    rvalue = False
                    errmsg += "Data File %-10s Cannot Be Found\n"% (pattern.get("Datafile"))

        # 2. Nre
        nre = 0
        for variable in self.get("Refine").get("Variable"):
            if variable.get("usemin") is True:
                nre += 1
        # End -- for variable in ... 
        self.set("Nre", nre)

        # Check Validity
        # 1. parameter
        if self.get("NCY") < 1:
            rvalue = False

        # 2. .hkl file 
        #   the reason why not put the checking .hkl file in Contribution is that
        #   there is a sequence number related between pattern sequence
        #   within contribution, it is hard to get this number
        for pattern in self.get("Pattern"):
            # scan all Phases
            pindex = 1
            fnamer = pattern.get("Datafile").split(".")[0]
            usehkl = False
            for phase in self.get("Phase"):
                # get contribution
                contribution = self.getContribution(pattern, phase)
                
                if contribution is not None and contribution.get("Irf") == 2:
                    # using reflection
                    usehkl = True
                    # check single phase/contribution hkl file
                    hklfname = fnamer+str(pindex)+".hkl"
                    try:
                        hklfile = open(hklfname, "r")
                        hklfile.close()
                    except IOError as err:
                        # if no such file exits, update Irf to 0
                        contribution.set("Irf", 0)
                        # error message output
                        errmsg += "Fit.validate():  Reflection File %-10s Cannot Be Found: "% (hklfname)
                        errmsg += "Chaning Contribution.Irf to 0 ... Related to Phase[%-5s]"% (pindex)
                        print(errmsg)
                # End -- if contribution is not None and Irf == 2:

                pindex += 1
            # End -- for phase in self.get("Phase"):

            if usehkl is True:
                # check overall hkl file
                hklfname = fnamer+".hkl"
                try:
                    hklfile = open(hklfname, "r")
                    hklfile.close()
                except IOError as err:
                    # if no such file exists, update all Irf to 0
                    for contribution in self.get("Contribution"):
                        contribution.set("Irf", 0)
            # END -- if usehkl is True:
        # End -- for pattern in self.get("Pattern"):

        if rvalue is not True:
            # Error output
            errmsg =  "===  Fit.validate() ===\n" + "Invalidity Deteced\n"
            print(errmsg)

        return rvalue


    def refine(self, cycle, srtype="l", mode="refine", signature=["dry","/tmp/"]):
        """ Unify the interface to connect higher level """
        import diffpy.pyfullprof.runfullprof as FpEngine

        subid = signature[0]
        processdir = signature[1]

        # 1. set cycle number
        self.set("NCY", cycle)
        self.adaptPyFullProftoSrRietveld(srtype, processdir)
        # 2. init file name for refinement
        pcrfullname = os.path.join(processdir, "temp.pcr")
        # 3. call runfullprof
        fitsummary = FpEngine.runFullProf(self, pcrfullname, mode, srtype, processdir)
   
        # 4. updateFit and get data/reflectionlist files
        self.getRefineResult(fitsummary, srtype, pcrfullname)

        filedir = processdir + "/" + "temp*.*"
        des = processdir + "/" + subid
        os.mkdir(des)
        for fname in glob.glob(filedir):
            shutil.move(fname, des)

        return fitsummary
 

    def adaptPyFullProftoSrRietveld(self, srtype, processdir, weightscheme="standard"):
        """ Change some setting to FullProf from SrRietveld """
        if srtype == "l":
            # Lebail:  set Jbt -> Profile Matching Mode, and Auto-calculate
            # FIXME  In advanced mode, if Fit can capture mult-step refine, Irf=2 in step>1 refine
            for phase in self.get("Phase"):
                phase.set("Jbt", 2)
                self.Jbt=2
            for contr in self.get("Contribution"):
                contr.set("Irf", 0)   

        elif srtype == "r":
            # Rietveld
            for phase in self.get("Phase"):
                phase.set("Jbt", 0)
                self.Jbt=0
        # END-IF:   if srtype

        for pattern in self.get("Pattern"):
            if weightscheme[0] == "s":
                pattern.set("Iwg", 0)
            elif weightscheme[0] == "u":
                pattern.set("Iwg", 2)
            else:
                errmsg = "Weighting Scheme %-10s Is Not Supported"% (weightscheme)
                raise RietError(errmsg)

        return

    def getRefineResult(self, fitsummary, srtype, pcrfullname):
        """ get out Refinement results
        """
        import diffpy.pyfullprof.fpoutputfileparsers as FPP     
        newfit = fitsummary.getFit()
        if isinstance(newfit, Fit):
            self.updateFit(newfit)
        else:
            #FIXME: should change the refine status and let srr to handle the error
            raise RietError(self.__class__.__name__+".refine(): Fit Error!")
        self._readCalculatePattern(pcrfullname)
        # if mode=lebail, import reflections from RFL file
        if srtype == "l":
            patterns = self.get("Pattern")
            numpat = len(patterns)
            if numpat == 1:
                singlepattern = True
            else:
                singlepattern = False
            # b) Phase
            numpha = len(self.get("Phase"))
            # c) Read all reflections
            hklrange = {}
            for patid in range(numpat):
                tempreflects = []
                hklrange["min"] = patterns[patid].get("Thmin")
                hklrange["max"] = patterns[patid].get("Thmax")
                for phaseid in range(numpha):
                    # Only work on phase-pattern related case
                    corecontrib = self.getContribution(self.get("Phase")[phaseid], 
                                        self.get("Pattern")[patid])
                    if corecontrib is not None:
                        reflectdict = FPP.parseHKLn(pcrfullname, phaseno=phaseid+1, 
                                            singlepattern=singlepattern, patno=patid+1, hklrange=hklrange)
                        tempreflects.append(reflectdict)
                    # END-IF
                # LOOP-OVER
                patterns[patid]._reflections[phaseid] = tempreflects
             # LOOP-OVER
        # turn all constraint refinement off
        #self.fixAll()
        return

    def fixAll(self):
        """Fix all the refinable parameters at their current values."""
        srrefine = self.get("Refine")
        for constraint in srrefine.constraints[:]:
            # there is no removeConstraintByPath, so a constraint can only be removed
            # by its parname + index            
            constraint.owner.removeConstraint(constraint.parname, constraint.index)
        srrefine.constraints = []

        return
    
    def _readCalculatePattern(self, pcrfullname):
        """read the calculated pattern from refinement solution
        put the data as list of 2-tuples to each component/data
        """
        pcrbasename = os.path.basename(pcrfullname)
        pcrrootname = os.path.splitext(pcrbasename)[0]
        processdir = pcrfullname.split(pcrbasename)[0][:-1]

        # get pattern list 
        patternlist = self.get("Pattern")

        # read each model file
        index = 0
        for pattern in patternlist:
            if pattern.get("Prf") == 3 or pattern.get("Prf") == -3:
                # output solution in prf format 
                if len(patternlist) > 1:
                    prffname = processdir+"/"+pcrrootname+"_"+str(index+1)+".prf"
                else:
                    prffname = processdir+"/"+pcrrootname+".prf"
                pattern.importPrfFile(prffname)
            else:
                errmsg = "Prf = %-5s will be implemented soon in Fit._readCalculatePattern()"%(pattern.get("Prf"))
                raise_(NotImplementedError, errmsg)
            index += 1
        # End of:  for pattern in patternlist:

        return 

    def calculate(self, processdir):
        """calculate all the patterns according to the given model, \
            peakprofile and sample corrections

        this method is closely related to Gsas engine

        Arguments:
         - processid    :   str.  directory

        Return      --  None
        """
        import diffpy.pyfullprof.runfullprof as FpEngine
        # 1. set cycle
        self.set("NCY", 1)
        
        for pattern in self.get("Pattern"):
            # 2. set to the correct choice
            pattern.setCalculation()

        # 3. init file names for refinement
        pcrfullname = processdir + "/TEMP.EXP"
        # 5. call GSAS to refine
        FpEngine.runfullprof(self, pcrfullname, mode="Calculate")
        self._readCalculatePattern(pcrfullname)
        return 

    def setDataProperty(self, datadict):
        """ Set Datafile for FullProf """
        id = -1
        for pattern in self.get("Pattern"):
            id += 1
            radiationtype = pattern.get("Job")
            pattern.setDataProperty([list(datadict.keys())[id], list(datadict.values())[id]["Name"]], 
                radiationtype)
        return

""" End of class Fit """

class MonteCarlo(RietveldClass):
    # Optional (Cry=2): Monte Carlo search parameters

    ParamDict = {
        "NCONF":    IntInfo("NCONF", "Number of Configuration", 1, 1, None),
        "NSOLU":    IntInfo("NSOLU", "Number of Solution", 1, 1, None),
        "NREFLEXF": IntInfo("NREFLEXF", "Number of Reflection", 0, 0, None),
        "NSCALE":   IntInfo("NSCALEF", "Scale Factor", 0) 
    } 
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, Parent):
        RietveldClass.__init__(self, Parent)

        return



class CPL(RietveldClass):

    ParamDict = {
        "flag": EnumInfo("flag", "flags to indicate if the coefficient will be switched", 0,
                {0: "remain fixed",
                1:  "switched"},
                [1,0]),
    }
    def __init__(self, Parent):
        RietveldClass.__init__(self, Parent)

        return



class SimulatedAnnealing(RietveldClass):
    # Simulated (Cry=3): Simulated annealing parameters

    ParamDict = {
        "T_INI":    FloatInfo("T_INI", "Initial Temperature", 0.0, '', 0.0, None),
        "ANNEAL":   FloatInfo("ANNEAL", "Reduction Factor of the temperature between the MC Cycles", 0.9, '', 0.0, None),
        "ACCEPT":   FloatInfo("ACCEPT", "Lowest percentage of accepted configurations", 0.5,'', 0.0, None),
        "NUMTEMPS": IntInfo("NUMTEMPS", "Maximum number of temperature", 1, 1, None),
        "NUMTHCYC": IntInfo("NUMTHCYC", "Number of Monte Carlo Cycles", 1, 1, None),
        "INITCONF": EnumInfo("INITCONF", "Initial Configuration", 0,
                    {0: "random",
                    1:  "given"},
                    [0, 1]),
        "SEED_Random":  StringInfo("SEED_Random", "Randomized Seed", ""),
        "NCONF":    IntInfo("NCONF", "Number of Configuration", 1, 1, None),
        "NSOLU":    IntInfo("NSOLU", "Number of Solution", 1, 1, None),
        "NREFLEXF": IntInfo("NREFLEXF", "Number of Reflection", 0, 0, None),
        "NSCALE":   IntInfo("NSCALEF", "Scale Factor", 0), 
        "NALGOR":   EnumInfo("NALGOR", "Algorithm", 0,
                    {0: "Corana algorithm",
                    1:  "Corana algorithm is selected using as initial steps",
                    2:  "Conventional algorithm using fixed steps"},
                    [2, 0, 1]),
        "ISWAP":    IntInfo("ISWAP", "Interchange of Atoms", 0, 0, None),
    }
    ObjectDict  = {}
    ObjectListDict = {
        "CPL":  ObjectInfo("CPLList", "CPL", 0, None),
    }

    def __init__(self, Parent):
        RietveldClass.__init__(self, Parent)

        return

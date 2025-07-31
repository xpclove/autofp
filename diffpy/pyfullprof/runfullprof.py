#!/usr/bin/env python
##############################################################################
#
# diffpy.pyfullprof by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Wenduo Zhou
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

'''classes for running Rietveld refinement through a FullProf engine
(engine can be run as an external command, or as a Python binding)
'''
from __future__ import print_function

from future.utils import raise_
__id__ = "$Id: runfullprof.py 6843 2013-01-09 22:14:20Z juhas $"

import os
import shutil

from diffpy.pyfullprof.exception import RietError
from diffpy.pyfullprof.exception import RietPCRError
from diffpy.pyfullprof.utilfunction import verifyType
from diffpy.pyfullprof.fpsumparser import FPSumFileParser

class FitSummary:
    """
    class FitSummary is a standard outcome of a Rietveld refinement

    Class Variables:
    - result    :   
    """

    def __init__(self):
        """
        initialization

        result:  the refinement result denoted by integer
                 -1: error
                  0: not refined due to bad start value
                  1: refined
        status:  allowed values include 'True' and 'False'
        """
        self._status = False
        self._fpoutputparser = None
        self._fit    = None
        self._errmsg = "Setup Error"

        return
        

    def __str__(self):
        """
        formatted output of FitSummary
        """
        rstring = ""
        rstring += "Status: %-30s\n"% (self._status)
        rstring += "Result: %-60s\n"% (self._result)
        rstring += "Errors: %-60s\n"% (self._errors)

        return rstring

    
    def set(self, fitpro, fpoutputparser, refinesuccess, refinetype, errmsg=None, outputs=None, errors=None):
        """ Set function
        Arguments:
          - refinesuccess :   boolean
          - errmsg        :   str, reason of refinement error
          - fitpro        :   the fit at the status after being refined
          - outputs       :   a list of lines recording output messages
          - errors        :   a list of lines recording error messsges
        """
        self._fpoutputparser = fpoutputparser
        self._refinesuccess  = refinesuccess
        self._errmsg         = errmsg
        self._fit     = fitpro
        self._outputs = outputs
        self._errors  = errors
        self._refinetype = refinetype

        return


    def setFit(self, fitpro):
        """
        Set post-refinement Fit instance to fit summary

        Argument:
        - fitpro    :   Fit instance
        """
        self._fit = fitpro

        return


    def setRefineStatus(self, refinesuccess):
        """
        Set the status of refinement, successful or not

        Argument:
        - refinesuccess :   boolean

        Return          :   None
        """
        self._refinesuccess  = refinesuccess

        return


    def getRefineStatus(self):
        """
        return result
        """
        return self._refinesuccess

    def getRefineType(self):
        """
        return refine type
        """
        return self._refinetype

    def getErrorReason(self):
        """
        return the reason of refinement error
        """
        return self._errmsg


    def getFit(self):
        """
        return fit
        """
        return self._fit


    def getLines(self):
        """
        return a 2-tuples
        """
        return (self._outputs, self._errors)


    def getResidueValue(self, cycle, residname="all", patno=0):
        """
        Get residue value from a certain cycle

        Return  :   RefineDetail instance
        """
        if cycle < 0:
            cycle = self._fpoutputparser.getNumCycles() + cycle + 1

        if residname == "all":
            rtuple = self._fpoutputparser.getResidues(cycle)[patno]
        elif residname == "Rp":
            rtuple = self._fpoutputparser.getResidues(cycle)[patno][0]
        elif residname == "Rwp":
            rtuple = self._fpoutputparser.getResidues(cycle)[patno][1]
        elif residname == "Re":
            rtuple = self._fpoutputparser.getResidues(cycle)[patno][2]
        elif residname == "Chi2":
            rtuple = self._fpoutputparser.getResidues(cycle)[patno][3]

        return rtuple


    def setNumCycles(self, numcycles):
        """
        Set the number of cycles of the refinement

        Argument:
        - numcycles :   int

        Return      :   None
        """
        self._numcycles = numcycles

        return


    def getNumCycles(self):
        """ Get the number of cycles

        Return  :   int
        """
        if self._fpoutputparser is not None:
            self._numcycles = self._fpoutputparser.getNumCycles()
        
        return self._numcycles


# END-CLASS: class FitSummary


def runFullProf(fit, pcrfilename, mode="refine", srtype="r", processdir=dir, userinfo=None, exportsub=False):
    """
    convert fit to FullProf pcr file
    execute Rietveld refinement by FullProf,

    Arguments:
    - fit           :   a fit object to convert to a pcr file and run by FullProf
    - pcrfilename   :   the name of the pcr file that is to write on the disk
    - mode          :   string, for mode.. options = 
                        1. "Refine"     least square refine 
                        2. "Calculate"  just calculate the pattern as the forward calculator
                        3. "pcr"        just print out pcr file
    - srtype        :   string, structure solution type, "r" for "Rietveld", "l" for Lebail
    - userinfo:     :   string, user information to add to pcr file
    - exportsub     :   Boolean (export result in .sub in calculation mode)

    Return          :   1. Refine Mode      FitSummary object
                        2. Calculate Mode   list of list of 2-tuple (or list) for a phase or None
    """
    from diffpy.pyfullprof.fit import Fit
    from diffpy.pyfullprof.pcrfilewriter import pcrFileWriter
    from diffpy.pyfullprof.pcrfilereader import ImportFitFromFullProf
    from diffpy.pyfullprof.fpoutputfileparsers import FPOutFileParser
    from diffpy.pyfullprof.fpuncertaintyreader import FPUncertainty

    # FIXME in 'Calculate' mode, only 1 pattern is allowed NOW!

    def ProcessOutput(infile):
        """
        processing an file thread
        (1) each line in intfile will be stored into a list as string without EOF
        (2) all lines are ordered according to the original order in infile

        infile: an file object
        """
        OutLines = []
        InLines  = infile.readlines()
        for line in InLines:
            newline = line.split("\n")[0]
            OutLines.append(newline)

        return OutLines

    # END FUNCTION:  def ProcessOutput(infile)

    def readFPOutput(lines):
        """ read the output of FullProf output file
          1. Last line contains "=> END"
            - check Chi2: is last Chi2 = "NaN"? "Chi2:-NaN, 
            - refined output 
          2. otherwise to 1
            a) "Error During Opening File" + file_name :  terminate the program
            b) "NO REFLECTIONS FOUND":  as Chi2 = NaN
        algorithm:
        (1) split Chi2 line with ":"

        return  1:  good refinement
                0   not refined
                -1: setup error
                -2: excessive peak overlap 
                -3: singular matrix
        """
        result = 0

        # 1. Exception!
        if len(lines) == 1:
            raise RietError("Fullprof fp2k Does Not Work")

        lastline = lines[-1]
        if lastline.count("=> END") >= 1:

            # 1. collect Chi2
            chi2lines = []
            for line in lines:
                if line.count("Chi2") == 1 and line.count("Rp")==1:
                    chi2lines.append(line)

            # 2. process last chi2 line
            # lastchi2line = chi2lines[len(chi2lines)-1]
            if len(chi2lines) > 1:
                # refinement mode
                lastchi2line = chi2lines[-1]
                if lastchi2line.count("NaN") > 0:
                    # NaN appears in statistic:  refine not done
                    result = 0
                else:
                    # good refinement
                    result = 1
            else:
                # calcuation mode
                result = -1

        else:   # not a normal end
            
            if lastline.count("Error") > 0:
                # Error 
                result = -1
                print("Exception!  FullProf set up error!   " + lastline + "\n")

            elif lastline.count("Excessive peak overlap") == 1:
                # Excessive peak overlap error
                result = -2

            elif lastline.count("Singular Matrix") == 1:
                # Singular Matrix Error
                result = -3

            elif lastline.count("NO REFLECTIONS FOUND") == 1:
                # Singular Matrix Error
                result = -4
        
            else:
                # intial value error
                result = 0

        return result

    # END FUNCTION:  def readFPOutput(lines)
    
    # -1: process input argument
    if userinfo is None:
        userinfo = []
    verifyType(userinfo, list)

    # 0. mandatory setup
    fit.set("Pcr", 1)
    fit.set("Aut", True)

    # 1.  check fit object:
    isvalid = fit.validate(mode)

    if not isvalid:
        dbtag = "1721"
        refine = fit.get("Refine")
        print("Debug Tag: %-20s" % (dbtag))
        print(str(refine))
        errmsg = "runFullProf() Fit object is not valid. Abort!"
        raise RietError(errmsg)

    if mode == "calculate":
        # in this mode, data file is not used, but FullProf needs it!
        from diffpy.pyfullprof.utilfunction import checkFileExistence
        pattern   = fit.get("Pattern")[0]
        datafname = pattern.get("Datafile")
        isexist = checkFileExistence(datafname)
        if isexist is not True:
            fakedatafile = True
            fakefilename = datafname
            cmd = "touch %-10s"% (fakefilename)
            os.system(cmd)
        else:
            fakedatafile = False

    # 2. write out the pcr file and run FullProf
    pcrFileWriter(fit, pcrfilename, userinfo, srtype=srtype)
    # get the root name and ext name of the pcr file
    rootName, extname= os.path.splitext(os.path.basename(pcrfilename))
    baseName = os.path.basename(pcrfilename)
    if mode=="pcr":
        return
    shutil.copyfile(pcrfilename, rootName + '.prefit')

    cmd = 'fp2k ' + baseName

    import subprocess
    from diffpy.pyfullprof.environment import FullProfSubprocessArgs
    fp2kArgs = FullProfSubprocessArgs(cwd=processdir, stdout=subprocess.PIPE,
             stderr=subprocess.PIPE, stdin=open(os.devnull))
    
    
    output = subprocess.Popen(('fp2k', baseName ), **fp2kArgs)
    # 3. process output
    CodeOutput = ProcessOutput(output.stdout)
    #print '\n'.join(CodeOutput)
    CodeError  = ProcessOutput(output.stderr)

    output.stdout.close()
    output.stderr.close()
    output.wait()

    if mode == "refine":
        # 4. process fit result
        newfit = Fit(None)
        try:
            importfile   = ImportFitFromFullProf(pcrfilename)
            importresult = importfile.ImportFile(newfit)    
        except RietPCRError as err:
            print("Error Message:  %-30s"% (err))
            importresult = False

        # 5. pass the parameter and constraint information
        summary = FitSummary()

        if importresult is True:
            # 6. build output
            result = readFPOutput(CodeOutput)
            
            outfname = rootName +".out"

            # 6.2 Judge refine result
            # Note:  result > 0 is a more robust flag than refinesuccess
            if result == 0:
                refinesuccess = False
                errmsg = "NAN"
            elif result == -1:
                outparser = FPOutFileParser(newfit, outfname)
                refinesuccess = outparser.getStatus()
                errmsg = outparser.getErrorReason()
            elif result == -2:
                refinesuccess = False
                errmsg = "Excessive Peak Overlap"
            elif result == -3:
                refinesuccess = False
                errmsg = "Singular Matrix"
            elif result == -4:
                refinesuccess = False
                errmsg = "NO REFLECTIONS FOUND"
            else:
                refinesuccess = True
                errmsg = None
                if result < 0:
                    quitmessage = "result = %-5s < 0 means a failure error" % result
                    raise_(ValueError, quitmessage)
            # END-IF-ELSE

            # 6.3 read uncertainty and phase fraction if refine is good 
            if refinesuccess is True: 
                # a) Uncertainty
                fpsigma = FPUncertainty(outfname)
                fpsigma.importUncertainty()
                fpsigma.exportToFit(newfit)

                # b) Phase Fraction
                sumfilename = rootName + ".sum"
                sumparse = FPSumFileParser(sumfilename)
                sumparse.parsePhaseFraction(newfit)
            # END-IF
            # 6.4 Construct Summary
            if result > 0:
                outparser = FPOutFileParser(newfit, outfname)
                summary.set(newfit, outparser, refinesuccess, srtype, errmsg, CodeOutput, CodeError)
            else:
                summary.setRefineStatus(False)
        else:
            # Bad refinement
            summary.setRefineStatus(False)
        # END-IF-ELSE 
        # 7. Process fp2k remainder
        os.rename(pcrfilename, rootName+".posfit")

        # 8. return
        return summary

    elif mode == "calculate":
        from diffpy.pyfullprof.fpoutputfileparsers import subParser

        # 4. import sub file
        if exportsub is True:
            phases   = fit.get("Phase")
            patterns = fit.get("Pattern")
            rootname = pcrfilename.split(".")[0]

            simpatternslist = []
            for phaseid in range(1, len(phases)+1):
                # FIXME  This is not good for multiple pattern simulation
                if len(patterns) > 1:
                    raise NotImplementedError("See FIXME")
                pat = patterns[0]
                thmin = pat.get("Thmin")
                thmax = pat.get("Thmax")
                step  = pat.get("Step")
                dataset = subParser(rootname, phaseid, thmin=thmin, thmax=thmax, step=step) 
                simpatternslist.append(dataset)

            # 5. clean
            if fakedatafile is True:
                cmd = "rm %-10s"% (fakefilename)
                os.system(cmd)

            # 5. return
            return simpatternslist

        else:
            return
        # END-IF-ELSE

    else:
        errmsg = "run-FullProf:  mode = %-10s is NOT supported"% (mode)
        raise RietError(errmsg)

    return

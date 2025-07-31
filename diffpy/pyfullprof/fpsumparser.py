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

""" Parser for Fullprof .sum file
"""

from future.utils import raise_
__id__ = "$Id: fpsumparser.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.stringop import parseLineToDict
from diffpy.pyfullprof.exception import RietPCRError

class FPSumFileParser:
    """ Class to parse Fullprof .sum file
    """

    def __init__(self, sumfilename):
        """ Initialization of a .sum file

        Argument:
          - sumfilename :   str, .sum file name
        
        Return  :   None
        """
        self.importSumFile(sumfilename)

        return


    def importSumFile(self, sumfilename):
        """ Import a .sum file

        Arguement:
          - sumfilename :   string, summary file name

        Return          :   None
        """
        # 1. Import plain text file
        try:
            sfile = open(sumfilename, "r")
            rawlines = sfile.readlines()
            sfile.close()
        except IOError as err:
            errmsg = "Fullprof .sum %-15s cannot be read properly\n" % \
                    sumfilename + str(err)
            raise_(IOError, err)

        # 2. Clean line
        self.lines = []
        for rline in rawlines:
            cline = rline.strip()
            if cline != "":
                self.lines.append(cline)
        # LOOP-OVER

        # 3.  Start to scan the file in order to make some search quicker
        # 3.1 Reliability factor flag position
        self._reliabilityFactorPos = {}
        lineindex = 0
        for line in self.lines:
            terms = line.split("RELIABILITY FACTORS WITH ALL NON-EXCLUDED POINTS FOR PATTERN:")
            if len(terms) > 1:
                patternid = int(terms[-1])
                self._reliabilityFactorPos[patternid] = lineindex
            lineindex += 1
        # LOOP-OVER

        return


    def parsePhaseFraction(self, myfit):
        """  Parse the phase fraction information out of the .sum file
        and write all the information to the related Fit instance

        Argument:
          - myfit    :   Fit instance
        
        Return  :   None
        """
        # 1. Prepare
        numphases = len(myfit.get("Phase"))
        startlinenumbers = self.locate("BRAGG R-Factors and weight fractions for Pattern #")

        # 2. Parse for phases
        ipat = 0
        for pattern in myfit.get("Pattern"):
            # 2.1 Prepare 
            startlinenumber = startlinenumbers[ipat]
            phaselinenumbers = self.locate("Phase", startlinenumber, numphases)

            # 2.2 Read one block for phase fraction (pattern-phase)
            for ipha in range( numphases ):
                infolist = self.readSinglePhaseFraction( phaselinenumbers[ipha], 
                    ipha )
                fraction, fracuncert = infolist[2]
                phase = myfit.get("Phase")[ipha]
                contrib = myfit.getContribution(pattern, phase)
                if contrib is not None:   
                    # contribution may not exist such as in corefinement
                    contrib.setPhaseFraction(fraction, fracuncert)
                else:
                    pass
            # LOOP-OVER

            # 2.3 Loop control variable
            ipat += 1

        # LOOP-OVER

        return


    def locate(self, flagstring, startlineindex = 0, numtoread = None):
        """ Locate some string in whole lines and return
        all the lines with this string

        Argument:
          - flagstring  :   str

        Return  :   list of int
        """
        returnlist = []

        for lindex in range( startlineindex, len( self.lines ) ):
            line = self.lines[lindex]
            if line.count( flagstring ) > 0:
                # if this line contains the flag string
                returnlist.append( lindex )
                if numtoread is not None and len( returnlist ) == numtoread:
                    # break if limit of number to read is reached
                    break
        # LOOP-OVER

        return returnlist


    def readSinglePhaseFraction(self, startlineindex, phaseindex):
        """ Read a couple of lines for phase

        Argument
          - startlineindex  :   int
          - phaseindex      :   int

        Return  :   dict
        """

        # Line 1: Phase:
        line1 = self.lines[startlineindex]
        parsephaseindex = int( line1.split("Phase:")[1].split()[0] )
        if phaseindex + 1 != parsephaseindex:
            raise RietPCRError("Phase %d with wrong index." % phaseindex)

        # Line 2: Get
        list1 = parseLineToDict(self.lines[startlineindex+1], seplist = [":"],
                startflag = "=>")

        # Line 3: Get
        list2 = parseLineToDict(self.lines[startlineindex+2], seplist = [":", "="], 
                startflag = "=>")

        list1.extend( list2 )
        returnlist = list1

        return returnlist

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

__id__ = "$Id: irfreader.py 6843 2013-01-09 22:14:20Z juhas $"

"""
Irf File Reader

Example:
1. IrfReader:
    IrfReader()
    IrfReader.importIrf()
    IrfReader.setFit()
"""
class IrfReader:
    """
    Class to import Irf
    """
    def __init__(self):
        """
        Initialization
        """
        self._bankinfodict = {}
        self._lines        = None
        self._infodict     = {}

        return


    def importIrf(self, irffname):
        """
        Import Irf File name

        Arguement:
        - irffname  :   str

        Return      :   None
        """
        # 1. Import all lines
        irffile = open(irffname, "r")
        rawlines = irffile.readlines()
        irffile.close()

        # 2. Import non-information information line
        self._lines = []
        for line in rawlines:
            cline = line.strip()
            if cline != "":
                self._lines.append(cline)

        return


class TOFIrfReader(IrfReader):
    """
    Class to import TOF Irf file
    """
    def __init__(self):
        """
        Initialization
        """
        IrfReader.__init__(self)

        return


    def importIrf(self, irffname):
        """
        Import TOF Irf File name

        Arguement:
        - irffname  :   str

        Return      :   None
        """
        IrfReader.importIrf(self, irffname)

        # 1. determine number of banks
        numbank = 0
        banklinedict = {}
        lineindex = 0
        for line in self._lines:
            if line[0] == "!" and line.count("Bank") == 1:
                numbank += 1
                bankno = int(line.split("Bank")[1])
                if bankno != numbank:
                    errmsg = "Irf File Bank Number Error"
                    print errmsg
                banklinedict[numbank] = lineindex
            lineindex += 1
        # LOOP-OVER for line in self._lines

        # 2. import value to dictionary
        for bankno in xrange(1, numbank+1):
            self._infodict[bankno] = {}
            # 2.1 get data lines
            datalines = []
            lineno = banklinedict[bankno]+1
            for l in xrange(13):
                if self._lines[lineno][0] != "!":
                    datalines.append(self._lines[lineno])
                lineno += 1

            # 2.2 Parse Line 1
            self._infodict[bankno]["Pattern"] = {}
            getFloats(self._infodict[bankno]["Pattern"], datalines[0], ["Thmin", "Step", "Thmax"], 1)
            getFloats(self._infodict[bankno]["Pattern"], datalines[1], ["Dtt1" , "Dtt2", "Zero" ], 1)
            getFloats(self._infodict[bankno]["Pattern"], datalines[2], ["TwoSinTh"], 1)

            self._infodict[bankno]["PeakProfile"] = {}
            getFloats(self._infodict[bankno]["PeakProfile"], datalines[3], ["Sig2", "Sig1", "Sig0"], 1)
            getFloats(self._infodict[bankno]["PeakProfile"], datalines[4], ["Gam2", "Gam1", "Gam0"], 1)

            self._infodict[bankno]["ExpDecay"] = {}
            getFloats(self._infodict[bankno]["ExpDecay"], datalines[5], ["ALPH0", "BETA0", "ALPH1", "BETA1"], 1)

        # LOOP-OVER for bankno in xrange(1, numbank+1):

        return


    def setFit(self, theFit):
        """
        Set the content in infodict (from Irf) to a Fit instance

        Argument:
        - theFit    :   Fit instance

        Return      :   None
        """
        for pattern in theFit.get("Pattern"):
            # 1. Get data dictionary
            infodict = self._infodict[pattern.get("Bank")]

            # 2. Pattern setup
            for parname in infodict["Pattern"].keys():
                pattern.set(parname, infodict["Pattern"][parname])

            # 3. Profile and ExpDecay
            for phase in theFit.get("Phase"):
                contribution = theFit.getContribution(pattern, phase)
                peakprofile  = contribution.get("Profile")
                expdecay     = contribution.get("ExpDecayFunction")
                for parname in infodict["PeakProfile"].keys():
                    peakprofile.set(parname, infodict["PeakProfile"][parname])
                for parname in infodict["ExpDecay"].keys():
                    expdecay.set(parname, infodict["ExpDecay"][parname])

        # LOOP-OVER for pattern in theFit.get("Pattern"):

# END-DEFINITION CLASS


def getFloats(datadict, line, keylist, startpos):
    """
    Interpret a line to put value (float) to a dictionary

    Argument:
    - datadict  :   dict
    - line      :   str
    - keylist   :   list
    - startpos  :   int

    Return      :   None
    """
    terms = line.split()

    index = startpos
    for key in keylist:
        datadict[key] = float(terms[index])
        index += 1

    return

            

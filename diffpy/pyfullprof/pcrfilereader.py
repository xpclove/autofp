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

from __future__ import print_function
from future.utils import raise_
__id__ = "$Id: pcrfilereader.py 6843 2013-01-09 22:14:20Z juhas $"

import diffpy.pyfullprof.atom as AtomModule
import diffpy.pyfullprof.contribution as ContributionModule
import diffpy.pyfullprof.ion as IonModule
import diffpy.pyfullprof.laue as LaueModule
import diffpy.pyfullprof.pattern as PatternModule
import diffpy.pyfullprof.phase as PhaseModule
import diffpy.pyfullprof.refine as RefineModule
from diffpy.pyfullprof.fit import Fit
from diffpy.pyfullprof.stringop import StringOP
from diffpy.pyfullprof.exception import RietPCRError, RietError
import diffpy.pyfullprof.warning as warning


def toFloat(fnumber):
    """
    extending method float()

    return      --  a float number corresponding to 'fnumber'

    fnumber     --  string, int, float to convert to float

    Exception:
    ValueError  --  will be converted to RietPCRError 
    """
    try:
        rnumber = float(fnumber)
    except ValueError as err:
        errmsg = "value %-15s is not allowed to be converted to a Float;  Error Message: %-30s\n" % (
            str(fnumber), str(err))
        raise RietPCRError(errmsg)

    return rnumber


"""
definining Line Description
"""
LineDescription = {
    "19-3": "LINE 19-3: Irf, Npr, Jtyp (3 reals)",
}


class ImportFitFromFullProf:
    """ Import an existing Fit from FullProf PCR file
    """

    def __init__(self, pcrfname):
        # print("this is pcr file "+pcrfname)
        self.Name = ""
        self.PCR = pcrfname
        self.Style = "new"      # default to new style
        self.LineContent = {}   # dictionary
        self.LineNumber = 0
        self.ReadIndex = -1
        self.chi2 = None

        self.ionList = []

    def ImportFile(self, fit):
        """
        Import a FullProf PCR file

        arguement:
        - fit   :   pyfullprof.Fit instance

        return  --  None
        """
        self.fit = fit

        # 1. Read in original and fileter
        flag = self.FilterFile()
        if flag is False:
            print("Input file error!  Operation on " + self.PCR + " Abort!")
            return None
        if self.chi2 is not None:
            fit.set("Chi2", self.chi2)

        # 2. Read Block 1
        self.ReadIndex = 0
        goodimport = self.ReadBlock1(fit)
        if not goodimport:
            return False

        # 2. Read Block 2
        goodimport = self.ReadBlock2(fit)
        if not goodimport:
            return False

        # 3. Read Block 3
        goodimport = self.ReadBlock3(fit)
        if not goodimport:
            return False

        # 4. Read Block 4
        goodimport = self.ReadBlock4(fit)
        if not goodimport:
            return False

        # 5. Read Block 5: Monte Carlo or Simulated Annealing
        goodimport = self.ReadBlock5(fit)
        if not goodimport:
            return False

        # print "\t\t--------------  Debug Stop:  Normal Quit  --------------\t\t"
        return True

        # 6. Read Block 6: Line Printer Plot
        # FIXME  Skipped!
        goodimport = self.ReadBlock6(fit)
        if not goodimport:
            return False

        if self.ReadIndex != len(self.LineContent) - 1:
            print("Length of LineContent = " + str(len(self.LineContent)))
            print("ReadIndex = " + str(self.ReadIndex))
            print("Last Line: " + self.LineContent[self.ReadIndex])
            print("Addtional: " + self.LineContent[self.ReadIndex+1])
            raise NotImplementedError(
                "Line Number Incorrect at the End of File")
        else:
            return True    # successfully import

        return True

    # ---------  Internal Function  -------------#

    def FilterFile(self):
        """
        Read whole file to LineContent and filter out the comments line started with '!'
        """
        # print "File Filter:"
        try:
            pcrfile = open(self.PCR, 'r', 1)
            original = pcrfile.readlines()
            pcrfile.close()
        except IOError as err:
            errmsg = "Fails to read file %-10s\n" % (self.PCR)
            errmsg += "Error Message: %-30s" % (err)
            raise IOError(errmsg)

        FindChi2 = True      # flag to find chi^2 information in pcr file
        linenumber = 1
        for line in original:
            try:
                line1 = line.split('\n')
                line2 = line1[0].strip()
                if line2 == "":
                    # empty line
                    continue

                elif line2[0] != '!':
                    # data line
                    # delete comments after !
                    templine1 = line.split('!')
                    templine2 = templine1[0].split(
                        '#')  # delete comments after #
                    # templine3 = templine2[0].split("<--")# delete comments after <- cannot use
                    self.LineContent[self.LineNumber] = templine2[0]
                    self.LineNumber = self.LineNumber+1

                elif FindChi2 and line2.count("Chi2") == 1:
                    # read chi2
                    templist = line2.split()
                    self.chi2 = toFloat(templist[len(templist)-1])
                    FindChi2 = False

            except IndexError as err:
                print("Line "+str(linenumber)+":\t" + line +
                      "\twith items = " + str(len(line1)))
                # s = ""
                # lineindex = 1
                # for l in original[:]:
                #    s += str(lineindex) + ":   " + l
                #    lineindex += 1
                # print s

                raise IndexError

            linenumber += 1
        """ end -- for line  """
        return True

    def ReadBlock1(self, fit):
        """
        Read Read Block 1: from Line 1 to Line ?

        Argument
        - fit   :   diffpy.core.Fit

        Return  :   integer, line index for the last line (in file) of block 1
        """
        from diffpy.pyfullprof.pattern import Pattern

        # Line 1
        index = self.ReadIndex
        words = self.SplitNewLine(index)
        """
        for word in words:
            print word
        """
        info = ""
        if words[0] == "COMM":
            infolist = self.LineContent[index].split("COMM")
            if len(infolist) == 1:
                info = infolist[0].strip()
            elif len(infolist) == 2:
                info = infolist[1].strip()
            else:
                print("Strange")
        else:
            info = self.LineContent[index]
            info = (info.split("\n"))[0]

        fit.set("Information", info)

        # Line 2 and 3
        index = index + 1
        words = self.SplitNewLine(index)
        if words[0] == "NPATT":
            # New Style
            self.Style = "new"

            # Line 2: initialize pattern
            NPATT = int(words[1])
            for pat in xrange(0, NPATT):
                newpattern = Pattern(fit)
                fit.set("Pattern", newpattern)

            # read in bank number
            count = 1
            for i in xrange(2, len(words)):
                sindex = words[i]
                if sindex == "0":
                    count += 1
                elif sindex == "1":
                    bank = count
                    fit.banklist.append(bank)
                    count += 1
                else:
                    break
            # check
            if 0:  # 0/1 List just notice Fullprof to refine or exclude, but not affect File structure
                if fit.banklist != [] and NPATT != len(fit.banklist):
                    errmsg = "Line 2: NPATT = %5d Not Consistent With 1/0 List" % (
                        NPATT)
                    raise RietPCRError(errmsg)

            # Line 3
            index = index+1
            words = self.SplitNewLine(index)
            if words[0] != "W_PAT":
                warning.PrintError("First Letter is Not W_PAT", 3, words)
                return False
            else:
                try:
                    count = 1
                    for pattern in fit.get("Pattern"):
                        pattern.set("W_PAT", toFloat(words[count]))
                        count += 1
                except ValueError as err:
                    warning.PrintError(err, 3, words)
                    return False

        else:
            # Old Style
            self.Style = "old"

            index = index - 1  # line-2 won't be read
            NPATT = 1
            newpattern = Pattern(fit)
            fit.set("Pattern", newpattern)
            newpattern.set("W_PAT", 1.0)

        self.ReadIndex = index

        # debug output # print "Block1-Reading Finished"

        return True

    # -- end of ReadBlock1 --

    def ReadBlock2(self, fit):
        """
        Parse Block2 is from Line 4 to Line ???

        Argument        
        - fit   :   diffpy.core.Fit

        Return  :   integer, line index of last line of this block in file
        """

        index = self.ReadIndex + 1
        words = self.SplitNewLine(index)

        Nph = -1
        Npr = {}

        if self.Style == "new":

            # Line 4
            Nph = int(words[0])
            fit.set("Dum", int(words[1]))
            fit.set("Ias", int(words[2]))
            fit.set("Nre", int(words[3]))
            fit.set("Cry", int(words[4]))
            opt = int(words[5])
            if opt == 0:
                fit.set("Opt", False)
            elif opt == 1:
                fit.set("Opt", True)
            aut = int(words[6])
            if aut == 1:
                fit.set("Aut", True)
            elif aut == 0:
                fit.set("Aut", False)
            else:
                print("Warning/Error/error: Invalid value of Aut")
                fit.set("Aut", False)

            # Line 4n
            count = 0
            for pattern in fit.get("Pattern"):

                # preparation
                lpfactor = pattern.get("LPFactor")

                # read in
                index = index + 1
                words = self.SplitNewLine(index)

                pattern.set("Job", int(words[0]))
                Npr[count] = int(words[1])
                Nba = int(words[2])
                if Nba < -4:
                    pattern.set("Nba", -5)
                    pattern.set("NbaPoint", -Nba)
                elif Nba >= 2:
                    pattern.set("Nba", 2)
                    pattern.set("NbaPoint", Nba)
                else:
                    pattern.set("Nba", Nba)
                pattern.set("Nex", int(words[3]))
                pattern.set("Nsc", int(words[4]))
                pattern.set("Nor", int(words[5]))
                pattern.set("Iwg", int(words[6]))
                lpfactor.set("Ilo", int(words[7]))
                pattern.set("Res", int(words[8]))
                pattern.set("Ste", int(words[9]))
                pattern.set("Uni", int(words[10]))
                pattern.set("Cor", int(words[11]))

                count += 1

        elif self.Style == "old":

            # Line 4
            try:
                pattern = fit.get("Pattern", 0)
                pattern.set("Job", int(words[0]))
                lpfactor = pattern.get("LPFactor")
                Npr[0] = int(words[1])
                Nph = int(words[2])
                Nba = int(words[3])
                if Nba < -4:
                    pattern.set("Nba", -5)
                    pattern.set("NbaPoint", -Nba)
                elif Nba >= 2:
                    pattern.set("Nba", 2)
                    pattern.set("NbaPoint", Nba)
                else:
                    pattern.set("Nba", Nba)
                pattern.set("Nex", int(words[4]))
                pattern.set("Nsc", int(words[5]))
                fit.set("Dum", int(words[7]))
                pattern.set("Iwg", int(words[8]))
                lpfactor.set("Ilo", int(words[9]))
                fit.set("Ias", int(words[10]))
                pattern.set("Res", int(words[11]))
                pattern.set("Ste", int(words[12]))
                # fit.set("Nre", int(words[13]))
                Nre = int(words[13])
                fit.set("Cry", int(words[14]))
                pattern.set("Uni", int(words[15]))
                pattern.set("Cor", int(words[16]))
                opt = int(words[17])
                if opt == 0:
                    fit.set("Opt", False)
                else:
                    fit.set("Opt", True)
                aut = int(words[18])
                if aut == 0:
                    fit.set("Aut", False)
                elif aut == 1:
                    fit.set("Aut", True)
                else:
                    fit.set("Aut", False)

            except ValueError as err:
                errmsg = str(err)+"\n"
                errmsg += "Line 4: %-40s" % (self.LineContent[index])
                print(errmsg)
                warning.PCRFormatValueError(2, "4", err)

        else:
            warning.SystemErrorStyle(2, 4, self.Style)

        # END-IF self.Style == "old"/"new" ...

        # set unit:
        count = 0
        for pattern in fit.get("Pattern"):
            if pattern.get("Uni") == 0:
                # fit.Patterns[pat].setPowderData("2theta")
                pattern2theta = PatternModule.Pattern2Theta()
                pattern2theta.extend(pattern)
            elif pattern.get("Uni") == 1:
                # fit.Patterns[pat].setPowderData("tof")
                patterntof = PatternModule.PatternTOF()
                patterntof.extend(pattern)
                if Npr[count] == 10:
                    # Thermal Neutron
                    patterntofthermal = PatternModule.PatternTOFThermalNeutron()
                    patterntofthermal.extend(patterntof)
            elif pattern.get("Uni") == 2:
                # fit.Patterns[pat].setPowderData("energydispersive")
                patterned = PatternModule.PatternED()
                patterned.extend(pattern)
            else:
                raise NotImplementedError("Here!")
            count += 1
        # LOOP-OVER:  for pattern in fit.get("Pattern")

        # set bank number
        banknum = 1
        for pattern in fit.get("Pattern"):
            if isinstance(pattern, PatternModule.PatternTOF):
                pattern.set("Bank", banknum)
                banknum += 1

        # set Npr
        count = 0
        for pattern in fit.get("Pattern"):
            pattern.set("Npr", Npr[count])
            count += 1

        # set  phases
        if Nph < 0:
            raise NotImplementedError("Number of Phase = " + str(Nph) + " < 0")
        else:
            for n in xrange(0, Nph):
                phase = PhaseModule.Phase(fit)
                fit.set("Phase", phase)

        # Line 5:
        for pattern in fit.get("Pattern"):
            index = index + 1
            words = self.SplitNewLine(index)
            if self.isDataFile(words[0]):
                pattern.set("Datafile", words[0])
            else:
                pattern.set("Datafile", self.useDefaultDataFile())
                index = index - 1     # ContentLine[index] shouldn't be read

        # Line 6:
        for pattern in fit.get("Pattern"):
            if pattern.get("Res") != 0:
                index = index + 1
                words = self.SplitNewLine(index)
                pattern.set("Resofile", words[0])

        # print debug
        """
        for pat in xrange(1, fit.NPATT+1):
            print "\t\tFile Name: " + fit.Patterns[pat].Datafile + "  File Style: " + self.Style
            print "\t\tResolution File" + fit.Patterns[pat].Resofile + "  Res = " + str(fit.Patterns[pat].Res)
        """

        # Line 7:  Output Information
        index = index + 1
        words = self.SplitNewLine(index)
        if self.Style == "new":
            if len(words) != 6:
                warning.PCRFormatItemError(str(2), str(7), "New" + str(words))
                return False
            else:
                fit.set("Mat",  int(words[0]))
                fit.set("Pcr",  int(words[1]))
                fit.set("Syo",  int(words[2]))
                rpa = int(words[3])
                if rpa < 0:
                    print ("Warning/Error/error:  rpa  = " + str(rpa) + " set to 0")
                    rpa = 0
                fit.set("Rpa", rpa)
                sym = int(words[4])
                if sym == 0:
                    fit.set("Sym", 0)
                else:
                    fit.set("Sym", 1)
                sho = int(words[5])
                if sho == 0:
                    fit.set("Sho", False)
                else:
                    fit.set("Sho", True)
                # Line 7n
                for pattern in fit.get("Pattern"):
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 11:
                        warning.PCRFormatItemError(2, "7n", words)
                        return False
                    pattern.set("Ipr", int(words[0]))
                    pattern.set("Ppl", int(words[1]))
                    pattern.set("Ioc", int(words[2]))
                    try:
                        pattern.set("Ls1", int(words[3]))
                    except ValueError as err:
                        print (words[3])
                        print (self.LineContent[index])
                        raise ValueError(err)
                    pattern.set("Ls2", int(words[4]))
                    pattern.set("Ls3", int(words[5]))
                    prf = int(words[6])
                    pattern.set("Prf", prf)
                    pattern.set("Ins", int(words[7]))
                    pattern.set("Hkl", int(words[8]))
                    pattern.set("Fou", int(words[9]))
                    pattern.set("Ana", int(words[10]))
        elif self.Style == "old":
            pattern = fit.get("Pattern", 0)
            if len(words) != 17:
                warning.PCRFormatItemError(2, 7, "Old" + str(words))
            pattern.set("Ipr", int(words[0]))
            pattern.set("Ppl", int(words[1]))
            pattern.set("Ioc", int(words[2]))
            fit.set("Mat", int(words[3]))
            fit.set("Pcr", int(words[4]))
            pattern.set("Ls1", int(words[5]))
            pattern.set("Ls2", int(words[6]))
            pattern.set("Ls3", int(words[7]))
            fit.set("Syo", int(words[8]))
            prf = int(words[9])
            pattern.set("Prf", prf)
            pattern.set("Ins", int(words[10]))
            rpa = int(words[11])
            if rpa < 0:
                print ("Warning/Error/error:  rpa  = " + str(rpa) + " set to 0")
                rpa = 0
            fit.set("Rpa", rpa)
            sym = int(words[12])
            if sym == 0:
                fit.set("Sym", False)
            else:
                fit.set("Sym", True)
            pattern.set("Hkl", int(words[13]))
            pattern.set("Fou", int(words[14]))
            sho = int(words[15])
            if sho == 0:
                fit.set("Sho", False)
            elif sho == 1:
                fit.set("Sho", True)
            else:
                print ("Warning/Error/error Sho = " + str(sho) + " setting to 0")
                fit.set("Sho", False)
            pattern.set("Ana", int(words[16]))
        else:
            warning.SystemErrorStyle("2", "7, 7n", self.Style)

        # Line 8:  0 - 2theta; 1 - T.O.F; 2 - Energy Dispersive
        if fit.get("Cry") == 0:
            for pattern in fit.get("Pattern"):
                # preparation
                lpfactor = pattern.get("LPFactor")
                # read
                index = index + 1
                words = self.SplitNewLine(index)
                if pattern.get("Uni") == 0:
                    # 2theta
                    # The 2nd-muR is added after 2011 Fullprof,
                    if len(words) not in [9, 10]:
                        # so it may be 9 or 10 numbers
                        warning.PCRFormatItemError(
                            "2", "8-"+str(pattern), self.LineContent[index])
                        return False
                    pattern.set("Lambda1", toFloat(words[0]))
                    pattern.set("Lambda2", toFloat(words[1]))
                    pattern.set("Ratio",   toFloat(words[2]))
                    pattern.set("Bkpos",   toFloat(words[3]))
                    pattern.set("Wdt",     toFloat(words[4]))
                    lpfactor.set("Cthm",    toFloat(words[5]))
                    pattern.set("muR",     toFloat(words[6]))
                    pattern.set("AsymLim", toFloat(words[7]))
                    lpfactor.set("Rpolarz", toFloat(words[8]))
                    if len(words) == 10:  # The 2nd-muR is added after 2011 Fullprof,
                        pattern.set("2nd-muR",  toFloat(words[9]))
                    # debug output print "Ratio = " + str(pattern.get("Ratio"))
                elif pattern.get("Uni") == 1:
                    # T.O.F
                    # print "Pattern Type = " + pattern.__class__.__name__
                    if len(words) != 3:
                        warning.PCRFormatItemError(
                            "2", "8-"+str(pattern), self.LineContent[index])
                        return False
                    pattern.set("Bkpos", toFloat(words[0]))
                    pattern.set("Wdt",   toFloat(words[1]))
                    pattern.set("Iabscor", int(words[2]))
                elif pattern.get("Uni") == 2:
                    # Energy Dispersive
                    if len(words) != 3:
                        warning.PCRFormatItemError(
                            "2", "8-"+str(pattern), self.LineContent[index])
                        return False
                    pattern.set("Bkpos", toFloat(words[0]))
                    pattern.set("Wdt",   toFloat(words[1]))
                    pattern.set("Iabscor", int(words[2]))
                else:
                    pass
                # END-IF-ELSE For "Uni"

        # Line 9: compulsory
        index = index + 1
        words = self.SplitNewLine(index)
        if self.Style == "new":

            if len(words) != 6:
                warning.PCRFormatItemError("2", "9", self.LineContent[index])
                return False
            fit.set("NCY",  int(words[0]))
            fit.set("Eps",  toFloat(words[1]))
            fit.set("R_at", toFloat(words[2]))
            fit.set("R_an", toFloat(words[3]))
            fit.set("R_pr", toFloat(words[4]))
            fit.set("R_gl", toFloat(words[5]))
            # Line 9n
            for pattern in fit.get("Pattern"):
                index = index + 1
                words = self.SplitNewLine(index)
                if pattern.get("Uni") == 0:
                    if len(words) != 5:
                        warning.PCRFormatItemError(
                            "2", "9-"+str(pattern), self.LineContent[index])
                        return False
                    pattern.set("Thmin", toFloat(words[0]))
                    pattern.set("Step", toFloat(words[1]))
                    pattern.set("Thmax", toFloat(words[2]))
                    pattern.set("PSD",   toFloat(words[3]))
                    pattern.set("Sent0", toFloat(words[4]))
                elif pattern.get("Uni") == 1:
                    if len(words) != 3:
                        warning.PCRFormatItemError(
                            "2", "9-"+str(pattern), self.LineContent[index])
                        return False
                    pattern.set("Thmin", toFloat(words[0]))
                    pattern.set("Step",  toFloat(words[1]))
                    pattern.set("Thmax", toFloat(words[2]))
                elif pattern.get("Uni") == 2:
                    if len(words) != 3:
                        warning.PCRFormatItemError(
                            "2", "9-"+str(pattern), self.LineContent[index])
                        return False
                    pattern.set("Thmin", toFloat(words[0]))
                    pattern.set("Step",  toFloat(words[1]))
                    pattern.set("Thmax", toFloat(words[2]))

        elif self.Style == "old":
            # print str(words)
            fit.set("NCY",  int(words[0]))
            fit.set("Eps",  toFloat(words[1]))
            fit.set("R_at", toFloat(words[2]))
            fit.set("R_an", toFloat(words[3]))
            fit.set("R_pr", toFloat(words[4]))
            fit.set("R_gl", toFloat(words[5]))

            pattern = fit.get("Pattern")[0]
            if pattern.get("Uni") == 0:

                if len(words) != 11:
                    warning.PCRFormatItemError(
                        "2", "9 old,  Uni =" + str(pattern.get("Uni")), self.LineContent[index])
                    return False
                pattern.set("Thmin",  toFloat(words[6]))
                pattern.set("Step",   toFloat(words[7]))
                pattern.set("Thmax",  toFloat(words[8]))
                pattern.set("PSD",    toFloat(words[9]))
                pattern.set("Sent0",  toFloat(words[10]))

            elif pattern.get("Uni") == 1:

                if len(words) != 9:
                    warning.PCRFormatItemError(
                        "2", "9 old,  Uni =" + str(pattern.get("Uni")), self.LineContent[index])
                    return False
                pattern.set("Thmin", toFloat(words[6]))
                pattern.set("Step",  toFloat(words[7]))
                pattern.set("Thmax", toFloat(words[8]))

            elif pattern.get("Uni") == 2:

                if len(words) != 9:
                    warning.PCRFormatItemError(
                        "2", "9 old,  Uni =" + str(pattern.get("Uni")), self.LineContent[index])
                    return False
                pattern.set("Thmin", toFloat(words[6]))
                pattern.set("Step",  toFloat(words[7]))
                pattern.set("Thmax", toFloat(words[8]))

        else:
            print ("New-Old Error")

        # Line 10 and 11: optional: per pattern
        if fit.get("Cry") == 0:
            for pattern in fit.get("Pattern"):
                # Line 10 print str(pattern.get("Nba"))
                if pattern.get("Nba") >= 2 or pattern.get("Nba") < -4:
                    # Line 10n

                    if pattern.get("Nba") == 2:
                        background = PatternModule.BackgroundUserDefinedLinear(
                            None)
                    else:
                        background = PatternModule.BackgroundUserDefinedCubic(
                            None)
                    background.extend(pattern.get("Background"))

                    linetoread = abs(pattern.get("NbaPoint"))
                    for l in xrange(0, linetoread):
                        index += 1
                        words = self.SplitNewLine(index)
                        try:
                            background.set("POS", toFloat(words[0]))
                            bakval = toFloat(words[1])
                            background.set("BCK", bakval)
                            if len(words) > 2:
                                try:
                                    refinecode = toFloat(words[2])
                                except ValueError as err:
                                    refinecode = 0.0
                            else:
                                refinecode = 0.0

                            self.setRefine(fit, background, "BCK",
                                           bakval, refinecode, l)
                        except KeyError as err:
                            print ("Access " + str(2*l) + "  " + str(2*l+1))
                            raise KeyError
                    """
                    if fit.Patterns[pat].Nba == -4:
                        print "\t\t\t\t-----> This is an Nba = -4"
                    """

                if pattern.get("Nex") > 0:
                    for l in xrange(0, pattern.get("Nex")):
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 2:
                            # warning.PCRFormatItemError("2", "11-"+str(l), self.LineContent[index])
                            print ("warning" + self.LineContent[index])
                        try:
                            newregion = PatternModule.ExcludedRegion(pattern)
                            newregion.set("begin", toFloat(words[0]))
                            newregion.set("end",   toFloat(words[1]))
                            pattern.set("ExcludedRegion", newregion)
                        except IndexError as err:
                            print ("Index Error at Pattern " + str(pattern) + "  Line " + str(l))
                            print ("Line content -2: " + self.LineContent[index-2])
                            print ("Line content -1: " + self.LineContent[index-1])
                            print ("Line content   : " + self.LineContent[index])
                            print (str(err))

        # Line 12 and 12b : if any pattern's Nsc != 0
        for pattern in fit.get("Pattern"):
            if pattern.get("Nsc") != 0:

                lineno = abs(pattern.get("Nsc"))

                for sc in xrange(1, lineno+1):
                    # 1. initialization -> scatterfactor
                    if pattern.get("Job") == 0 or pattern.get("Job") == 2:
                        scatterfactor = PatternModule.ScatterFactorXray(
                            pattern)
                    # elif fit.Patterns[pat].Job == 1 or fit.Patterns[pat].Job == 3:
                    elif pattern.Job == 1 or pattern.Job == 3:
                        scatterfactor = PatternModule.ScatterFactorNeutron(
                            pattern)
                    else:
                        # print "Strange in Line 12, Nsc != 0, but in Job = " + str(fit.Patterns[pat].Job)
                        print ("Strange in Line 12, Nsc != 0, but in Job = " + str(pattern.Job))
                        return False

                    pattern.set("ScatterFactor", scatterfactor)

                    # 2. readLine 12
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 4:
                        warning.PCRFormatItemError("2", "12", str(words))
                    scatterfactor.set("NAM", words[0])
                    if scatterfactor.__class__.__name__ == "ScatterFactorXray":
                        scatterfactor.set("DFP", toFloat(words[1]))
                        scatterfactor.set("DFPP", toFloat(words[2]))
                    else:
                        scatterfactor.set("b", toFloat(words[1]))
                    scatterfactor.set("ITY", int(words[3]))

                    # Line 12b
                    if scatterfactor.__class__.__name__ == "ScatterFactorXray":
                        # Xray
                        if pattern.get("Nsc") > 0 and scatterfactor.get("ITY") == 0:
                            index = index + 1
                            words = self.SplitNewLine(index)
                            if len(words) != 9:
                                warning.PCRFormatItemError(
                                    "2", "12b", "xray "+str(words))
                            # init
                            formfactor = PatternModule.FormFactorXray(
                                scatterfactor)
                            scatterfactor.set("FormFactor", formfactor)
                            # read
                            formfactor.set("A1", toFloat(words[0]))
                            formfactor.set("B1", toFloat(words[1]))
                            formfactor.set("A2", toFloat(words[2]))
                            formfactor.set("B2", toFloat(words[3]))
                            formfactor.set("A3", toFloat(words[4]))
                            formfactor.set("B3", toFloat(words[5]))
                            formfactor.set("A4", toFloat(words[6]))
                            formfactor.set("B4", toFloat(words[7]))
                            formfactor.set("D",  toFloat(words[8]))
                        elif pattern.get("Nsc") < 0 and scatterfactor.get("ITY") == 0:
                            # init
                            formfactor = PatternModule.FormFactorTable(
                                scatterfactor)
                            scatterfactor.set("FormFactor", formfactor)
                            # read
                            index = self.Line12ReadTable(index, formfactor)
                    elif pattern.get("Job") == 1 or pattern.get("Job") == 3:
                        # Neutron
                        if pattern.get("Nsc") > 0 and scatterfactor.get("ITY") == 1:
                            index = index + 1
                            words = self.SplitNewLine(index)
                            if len(words) != 7:
                                warning.PCRFormatItemError(
                                    "2", "12b", "neutron "+str(words))
                            # init
                            formfactor = PatternModule.FormFactorNeutron(
                                scatterfactor)
                            scatterfactor.set("FormFactor", formfactor)
                            # read
                            formfactor.set("A", toFloat(words[0]))
                            formfactor.set("a", toFloat(words[1]))
                            formfactor.set("B", toFloat(words[2]))
                            formfactor.set("b", toFloat(words[3]))
                            formfactor.set("C", toFloat(words[4]))
                            formfactor.set("c", toFloat(words[5]))
                            formfactor.set("D", toFloat(words[6]))
                        # elif fit.Patterns[pat].Nsc < 0 and fit.Patterns[pat].ScatteringFactorList[sc].ITY == 1:
                        elif pattern.Nsc < 0 and pattern.ScatteringFactorList[sc].ITY == 1:
                            # init
                            formfactor = PatternModule.FormFactorTable(
                                scatterfactor)
                            scatterfactor.set("FormFactor", formfactor)
                            # read
                            index = self.Line12ReadTable(index, formfactor)

        # Line 13
        index = index + 1
        words = self.SplitNewLine(index)
        if len(words) != 1:
            print ("warning:\t" + str(words))
            warning.PCRFormatItemError("2", "13", str(words))
        fit.Maxs = int(words[0])

        """
        print "Maxs = " + str(fit.Maxs)
        print "Next Line = " + self.LineContent[index+1]
        """

        # Init Table

        # Line 14 - 17
        for pat, pattern in enumerate(fit.get("Pattern")):
            if fit.get("Cry") == 0 and pattern.get("Uni") == 0:    # 2theta

                # Line 14
                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != 9:
                    warning.PCRFormatItemError(
                        "2", "2theta: Line 14 Lenth = 9", str(words))
                # print("Zero"+str(words[0])+str(words[1]))
                self.setRefine(fit, pattern, "Zero", toFloat(
                    words[0]), toFloat(words[1]))
                self.setRefine(fit, pattern, "Sycos",  toFloat(
                    words[2]), toFloat(words[3]))
                self.setRefine(fit, pattern, "Sysin", toFloat(
                    words[4]), toFloat(words[5]))
                self.setRefine(fit, pattern, "Lambda",
                               toFloat(words[6]), toFloat(words[7]))
                More = int(words[8])
                if More != 0:
                    pattern.set("More", True)
                else:
                    pattern.set("More", False)

                # Line 15: More != 0
                if More != 0:
                    # check whether all the other conditions are satisfied:
                    if pattern.get("LPFactor").get("Ilo") != 0:
                        raise RietError(
                            "readpcrfile @ Line 15:  not allowed Ilo = " + str(pattern.get("Ilo")))
                    # create a MicroAbsorption instance
                    micabs = PatternModule.MicroAbsorption(pattern)
                    pattern.set("MicroAbsorption", micabs)
                    # read in
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 6:
                        warning.PCRFormatItemError(
                            "2", "2theta: 15", str(words))
                    self.setRefine(fit, micabs, "P0",  toFloat(
                        words[0]), toFloat(words[1]))
                    self.setRefine(fit, micabs, "CP",  toFloat(
                        words[2]), toFloat(words[3]))
                    self.setRefine(fit, micabs, "TAU", toFloat(
                        words[4]), toFloat(words[5]))

                # Line 17: -2<=Nba(pat)<-1
                index = self.Line17Read(fit, pattern, index)

            elif fit.get("Cry") == 0 and pattern.get("Uni") == 1:  # T.O.F

                # Line 14:
                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != 7:
                    # warning.PCRFormatItemError("2", "T.O.F: 14 pat" + str(pat), str(words))
                    warning.PCRFormatItemError(
                        "2", "T.O.F: 14 pat" + str(pattern), str(words))
                self.setRefine(fit, pattern, "Zero", toFloat(
                    words[0]), toFloat(words[1]))
                self.setRefine(fit, pattern, "Dtt1", toFloat(
                    words[2]), toFloat(words[3]))
                self.setRefine(fit, pattern, "Dtt2", toFloat(
                    words[4]), toFloat(words[5]))
                pattern.set("TwoSinTh", toFloat(words[6]))

                # Line 16:
                if pattern.get("Npr") == 10:
                    # errmsg  = "Line 16 at Npr=10 format no clear\n"
                    # errmsg += "Line 16:  %-60s"%(self.LineContent[index+1])
                    # raise NotImplementedError, errmsg
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 5:
                        warning.PCRFormatItemError(
                            "2", "T.O.F: 16", self.LineContent[index])
                    # setup dspacing object
                    # tofd = TOFdspacing(pattern)
                    # pattern.set("TOFdspacing", todf)
                    # read value
                    zerot = toFloat(words[0])
                    dtt1t = toFloat(words[1])
                    dtt2t = toFloat(words[2])
                    xcross = toFloat(words[3])
                    width = toFloat(words[4])

                    # read code
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 5:
                        warning.PCRFormatItemError(
                            "2", "T.O.F: 16-code", self.LineContent[index])
                    self.setRefine(fit, pattern, "Zerot",
                                   zerot, toFloat(words[0]))
                    self.setRefine(fit, pattern, "Dtt1t",
                                   dtt1t, toFloat(words[1]))
                    self.setRefine(fit, pattern, "Dtt2t",
                                   dtt2t, toFloat(words[2]))
                    self.setRefine(fit, pattern, "xcross",
                                   xcross, toFloat(words[3]))
                    self.setRefine(fit, pattern, "Width",
                                   width, toFloat(words[4]))
                # end -- if pattern.get("Npr") == 10

                # Line 17: -2<=Nba(pat)<-1
                index = self.Line17Read(fit, pattern, index)

            elif fit.get("Cry") == 0 and pattern.get("Uni") == 2:  # Energy Dispersive

                # Line 14:
                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != 7:
                    warning.PCRFormatItemError(
                        "2", "Energy Dispersive: 14", str(words))
                codeindex = self.CodeWord(
                    toFloat(words[0]), toFloat(words[1]), fit)
                # fit.Patterns[pat].powderData.Zero  = (toFloat(words[0]), codeindex)
                pattern.powderData.Zero = (toFloat(words[0]), codeindex)
                codeindex = self.CodeWord(
                    toFloat(words[2]), toFloat(words[3]), fit)
                # fit.Patterns[pat].powderData.StE1 = (toFloat(words[2]), codeindex)
                pattern.powderData.StE1 = (toFloat(words[2]), codeindex)
                codeindex = self.CodeWord(
                    toFloat(words[4]), toFloat(words[5]), fit)
                # fit.Patterns[pat].powderData.StE2 = (toFloat(words[4]), codeindex)
                # fit.Patterns[pat].powderData.TwoSinTh = toFloat(words[6])
                pattern.powderData.StE2 = (toFloat(words[4]), codeindex)
                pattern.powderData.TwoSinTh = toFloat(words[6])

                # Line 17: -2<=Nba(pat)<-1
                index = self.Line17Read(fit, pat, index)

            elif fit.get("Cry") == 0:
                raise NotImplementedError("Line 14-17")

        # - end for pat -

        self.ReadIndex = index

        # debug output print "-----  Block 2 Over -----"

        return True

    # end --- ReadBlock2 (Block 2) ---

    #

    def ReadBlock3(self, fit):
        """
        Phase information:  
        From Line 18 - ...
        """

        # debug output print "Reading Block 3: "

        index = self.ReadIndex

        for pha, phase in enumerate(fit.get("Phase")):

            # Line 18: consider magnetic
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) < 1 and len(words) > 3:
                warning.PCRFormatItemError(
                    "3", "18 phase "+str(pha), str(words))
            # phase.PHSNM = words[0]
            phase.set("Name", words[0])
            if len(words) == 2:
                magphasename = words[1]
                name = words[0] + " " + words[1]
                phase.set("Name", name)
            elif len(words) == 3:
                spacegroup = words[1]
                magphasename = words[2]
                name = words[0] + " " + words[1] + " " + words[2]
                phase.set("Name", name)
                if 0:   # Debug 1547
                    # FIXME  Get to know exactly the warning is true or not!
                    msg = "(1547) From core: Imported may be a magnetic phase: "
                    msg += "%-40s" % (self.LineContent[index])
                    print (msg)

            # Line 19 set
            if self.Style == "new":
                # Line 19
                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != 10:
                    warning.PCRFormatItemError("3", "19", str(words))
                    print("Problematic Line: " + str(self.LineContent[index-1]))
                    print("Problematic Line: " + str(self.LineContent[index]))
                    print("Problematic Line: " + str(self.LineContent[index+1]))
                phase.set("Nat",    int(words[0]))
                phase.set("Dis",    int(words[1]))
                phase.set("MomMA",  int(words[2]))
                phase.set("Jbt",    int(words[3]))
                phase.set("Isy",    int(words[4]))
                phase.set("Str",    int(words[5]))
                phase.set("Furth",  int(words[6]))
                phase.set("ATZ",    toFloat(words[7]))
                phase.set("Nvk",    int(words[8]))
                More = int(words[9])
                # debug output print "More = " + str(More)
                if More != 0:
                    phase.set("More", True)
                else:
                    phase.set("More", False)
                # Line 19-1
                if More != 0:
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 6 and len(words) != 7:
                        errmsg = "Line %-10s: %-30s\n" %\
                            (19, "Nat, Dis, {Mom(Moment) or Mom(Angles)}, Pr1 Pr2 Pr3, Jbt, Irf, Isy, Str, Furth, ATZ, Nvk, Npr, More")
                        errmsg += "Line %-10s: Jvi, Jdi, Hel, Sol, Mom, Ter, N_Domains" % (
                            "19-1")
                        print(errmsg)
                        warning.PCRFormatItemError(
                            "3", "19-1", self.LineContent[index])
                    phase.set("Jvi", int(words[0]))
                    phase.set("Jdi", int(words[1]))
                    hel = int(words[2])
                    if hel == 0:
                        phase.set("Hel", False)
                    else:
                        phase.set("Hel", True)
                    sol = int(words[3])
                    if sol == 0:
                        phase.set("Sol", False)
                    else:
                        phase.set("Sol", True)
                    # phase.set("Mom", int(words[4]))
                    # phase.set("Ter", int(words[5]))
                    if len(words) == 7:
                        phase.set("N_Domains", int(words[6]))
                # Line 19-2
                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != len(fit.get("Pattern")):
                    warning.PCRFormatItemError("3", "19-2", str(words))
                pat = 0
                for pattern in fit.get("Pattern"):
                    if int(words[pat]) == 1:
                        usecontribution = True
                    elif int(words[pat]) == 0:
                        usecontribution = False
                    else:
                        raise NotImplementedError("Line 19-2, not 1/0")
                    if usecontribution:
                        if pattern.get("Uni") == 0:
                            contribution = ContributionModule.Contribution2Theta(
                                fit, pattern, phase)
                        else:
                            contribution = ContributionModule.ContributionTOF(
                                fit, pattern, phase)
                        fit.set("Contribution", contribution)
                        preferorient = ContributionModule.PreferOrient(None)
                        contribution.set("PreferOrient", preferorient)
                    else:
                        pass
                    pat += 1
                # end for

                # Line 19-3 and 19-4
                patternindex = 1
                for pattern in fit.get("Pattern"):
                    contribution = fit.getContribution(pattern, phase)
                    if contribution is not None:
                        # 19-3
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) < 3 and len(words) > 5:
                            warning.PCRFormatItemError(
                                "3", "19-3: new", str(words))
                        try:
                            contribution.set("Irf",  int(words[0]))
                            contribution.set("Npr",  int(words[1]))
                            contribution.set("Jtyp", int(words[2]))
                        except ValueError as err:
                            errmsg = str(err)+"\n"
                            errmsg += "pcrFileRead:  pcr File Error in Line 19-3  %-40s" % (
                                self.LineContent[index])
                            errmsg += "\nthis error occurs in Contribution Section on Pattern %-5s" % (
                                str(patternindex))
                            errmsg += "\nPrevious Line : %-40s" % (
                                self.LineContent[index-1])
                            errmsg += "\nThis line     : %-40s" % (
                                self.LineContent[index])
                            errmsg += "\nNext line     : %-40s" % (
                                self.LineContent[index+1])
                            errmsg += "\nCorrect Format: %-40s" % (
                                LineDescription["19-3"])
                            raise RietError(errmsg)
                        if len(words) > 3:
                            contribution.set("Nsp_Ref", int(words[3]))
                        else:
                            contribution.set("Nsp_Ref", 0)
                        if len(words) == 5:
                            contribution.set("Ph_Shift", int(words[4]))
                        # 19-4
                        preferorient = contribution.get("PreferOrient")
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "19-4: new", str(words))
                        preferorient.set("Pr1", toFloat(words[0]))
                        preferorient.set("Pr2", toFloat(words[1]))
                        preferorient.set("Pr3", toFloat(words[2]))
                        contribution.set("Brind", toFloat(words[3]))
                        contribution.set("Rmua", toFloat(words[4]))
                        contribution.set("Rmub", toFloat(words[5]))
                        contribution.set("Rmuc", toFloat(words[6]))

                        # debug output print "Line 19 (end) index = " + str(index)

                        # Single Crystal:  Impossible for Irf==4
                        if contribution.get("Irf") == 4:
                            print("Irf = 4 In multiple pattern")
                            raise NotImplementedError(
                                "In multiple pattern, Irf == 4 raise an exception! Manual states")

                    # end --- if fit.Patterns[pat].ContributionList[phase.PHSNM] is not False:

                    patternindex += 1
                # end -- for pat in xrange(1, fit.NPATT+1):
                # end -- 19, -1, -2, -3

            elif self.Style == "old":

                # In old style (single Pattern), Contribution will be added in any way for each pattern-phase
                pattern = fit.get("Pattern")[0]
                if pattern.get("Uni") == 0:
                    contribution = ContributionModule.Contribution2Theta(
                        fit, pattern, phase)
                else:
                    contribution = ContributionModule.ContributionTOF(
                        fit, pattern, phase)
                fit.set("Contribution", contribution)
                preferorient = ContributionModule.PreferOrient(None)
                contribution.set("PreferOrient", preferorient)

                # Line 19
                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != 15:
                    print(str(words))
                    warning.PCRFormatItemError(
                        "3", "19", self.LineContent[index]+"  Next Line: "+self.LineContent[index+1])
                phase.set("Nat", int(words[0]))
                phase.set("Dis", int(words[1]))
                phase.set("MomMA", int(words[2]))
                pr1 = toFloat(words[3])
                pr2 = toFloat(words[4])
                pr3 = toFloat(words[5])
                phase.set("Jbt", int(words[6]))
                contribution.set("Irf", int(words[7]))
                # Debug output   debut output
                if contribution.get("Irf") == 4:
                    print("Irf == 4 in Single Pattern")
                phase.set("Isy", int(words[8]))
                phase.set("Str", int(words[9]))
                phase.set("Furth", int(words[10]))
                phase.set("ATZ", toFloat(words[11]))
                phase.set("Nvk", int(words[12]))
                contribution.set("Npr", int(words[13]))
                preferorient = contribution.get("PreferOrient")
                preferorient.set("Pr1", pr1)
                preferorient.set("Pr2", pr2)
                preferorient.set("Pr3", pr3)
                More = int(words[14])
                if More != 0:
                    phase.set("More", True)
                else:
                    phase.set("More", False)
                # Line 19-1
                if More != 0:
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) < 11 or len(words) > 13:
                        errmsg = "Line %-10s: %-30s\n" %\
                            (19, "Nat, Dis, {Mom(Moment) or Mom(Angles)}, Pr1 Pr2 Pr3, Jbt, Irf, Isy, Str, Furth, ATZ, Nvk, Npr, More")
                        errmsg += "Line %-10s: Jvi, Jdi, Hel, Sol, Mom, Ter, Brind, Rmua, Rmub, Rmuc, Jtyp\n" % (
                            "19-1")
                        print(errmsg)
                        warning.PCRFormatItemError(
                            "3", "19-1: old", self.LineContent[index])
                    phase.set("Jvi", int(words[0]))
                    phase.set("Jdi", int(words[1]))
                    hel = int(words[2])
                    if hel == 0:
                        phase.set("Hel", False)
                    else:
                        phase.set("Hel", True)
                    sol = int(words[3])
                    if sol == 0:
                        phase.set("Sol", False)
                    else:
                        phase.set("Sol", True)
                    # phase.set("Mom", int(words[4]))
                    # phase.set("Ter", int(words[5]))
                    contribution.set("Brind", toFloat(words[6]))
                    contribution.set("Rmua", toFloat(words[7]))
                    contribution.set("Rmub", toFloat(words[8]))
                    contribution.set("Rmuc", toFloat(words[9]))
                    contribution.set("Jtyp", int(words[10]))
                    if len(words) >= 12:
                        contribution.set("Nsp_Ref", int(words[11]))
                    else:
                        contribution.set("Nsp_Ref", 0)
                    if len(words) == 13:
                        contribution.set("Ph_Shift", int(words[12]))

                if contribution.get("Irf") == 4:
                    print("Single Crystal not supported.....   Return")
                    return
                    raise NotImplementedError("Single Crystal not supported")

            # end -- if "new" ...   elif self.Style == "old":

            # Line 20 - 21
            if phase.get("Jdi") == 3 or phase.get("Jdi") == 4:
                # Line 20
                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != 3:
                    warning.PCRFormatItemError("3", "20", str(words))
                phase.set("Dis_max", toFloat(words[0]))
                phase.set("Ang_max", toFloat(words[1]))
                phase.set("BVS",     words[2])
                # Line 21
                if phase.get("BVS") == "BVS":
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 3:
                        warning.PCRFormatItemError("3", "21", str(words))
                    N_CATIONS = int(words[0])
                    N_ANIONS = int(words[1])
                    phase.set("Tolerance", toFloat(words[2]))
                    # Line 12-1
                    if N_CATIONS > 0:
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != N_CATIONS:
                            warning.PCRFormatItemError("3", "21-1", str(words))
                        for cat in xrange(0, N_CATIONS):
                            ion = IonModule.Ion(None)
                            ion.setIon(words[cat])
                            self.ionList.append(ion)
                            # ion.set("Symbol", words[cat])  old instruction
                            # phase.set("Cation", ion)
                    if N_ANIONS > 0:
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != N_ANIONS:
                            warning.PCRFormatItemError("3", "21-2", str(words))
                        for ani in xrange(0, N_ANIONS):
                            ion = IonModule.Ion(None)
                            ion.setIon(words[ani])
                            self.ionList.append(ion)
                            # ion.set("Symbol", words[ani])
                            # phase.set("Anion", ion)

            if phase.get("MomMA") != 0:
                raise NotImplementedError("MomMA != 0 Example")

            # Line 22
            index = index + 1
            # debug output print "Line 22 (start) index = " + str(index)
            words = self.Line22Read(index)
            phase.set("Spacegroup", words[0])
            phase.set("Comment", words[1])
            IsMagnetic = False
            if words[1].count("Mag") >= 1:
                IsMagnetic = True

            # Line 23
            readline23 = 0
            if (phase.get("Jbt") == 10 or phase.get("Jbt") == -10) and IsMagnetic:

                # determine NS
                NS = TimeReversalLookupTable.lookUpNS(phase.get("Spacegroup"))
                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != NS+1:
                    warning.PCRFormatItemError("3", "23", str(
                        words) + " Wrong Length = " + str(len(words)))

                # init TimeRev
                timerev = PhaseModule.TimeRev(None, NS)
                phase.set("TimeRev", timerev)

                # read
                for item in xrange(0, NS+1):
                    param_name = "TimeRev"+str(item)
                    timerev.set(param_name, int(words[item]))

                # set readline23
                readline23 = readline23+1

            if phase.get("Isy") != 0 and phase.get("Jbt") != 15:

                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != 4:
                    warning.PCRFormatItemError("3", "23 choice 1", str(
                        words) + " Wrong Length = " + str(len(words)))
                # symmetry operator init
                symmopschool = PhaseModule.OperatorSetSymmetry(None)
                phase.set("OperatorSet", symmopschool)
                # read
                symmopschool.set("Nsym", int(words[0]))
                symmopschool.set("Cen",  int(words[1]))
                symmopschool.set("Laue", int(words[2]))
                symmopschool.set("MagMat", int(words[3]))
                # set readline23
                readline23 = readline23+1

            if phase.get("Isy") != 0 and phase.get("Jbt") == 15:

                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != 5:
                    warning.PCRFormatItemError("3", "23 choice 2", str(
                        words) + " Wrong Length = " + str(len(words)))
                # symmetry operator init
                symmopschool = PhaseModule.OperatorSetSymmetry(None)
                phase.set("OperatorSetSymmetry", symmopschool)
                # read
                symmopschool.set("Nsym", int(words[0]))
                symmopschool.set("Cen",  int(words[1]))
                symmopschool.set("Laue", int(words[2]))
                symmopschool.set("DepMat", int(words[3]))
                symmopschool.set("MagMat", int(words[4]))
                # set readline23
                readline23 = readline23+1

            if phase.get("Isy") == -2 and (phase.get("Jbt") == 1 or phase.get("Jbt") == -1):

                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != 5:
                    warning.PCRFormatItemError("3", "23 choice 3", str(
                        words) + " Wrong Length = " + str(len(words)))
                # symmetry operator init
                # FIXME: never called, and nowhere to find the definition of this function
                symmopschool = BasisFunctionSet(None)
                phase.set("OperatorSetSymmetry", symmopschool)
                # read
                symmopschool.set("Nsym", int(words[0]))
                symmopschool.set("Cen",  int(words[1]))
                symmopschool.set("Laue", int(words[2]))
                symmopschool.set("Ireps", int(words[3]))
                symmopschool.set("N_Bas", int(words[4]))
                # set readline23
                readline23 = readline23+1

            if readline23 > 1:
                raise NotImplementedError(
                    "Line 23:  Read Line 23 More than Once")

            # Line 23-1
            if phase.get("Isy") == -2:
                # debug output print "Line 23-1 for ICOMPL: " + self.LineContent[index+1]
                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) <= 0 or len(words) > 9:
                    warning.PCRFormatItemError(
                        "3", "23-1", str(words) + " Wrong Length = " + str(len(words)))
                # init
                symmopschool = phase.get("OperatorSetSymmetry")
                icomplobj = PhaseModule.Icompl(
                    symmopschool, symmopschool.get("N_Bas"))
                symmopschool.set("Icompl", icomplobj)
                # read
                for item in xrange(0, len(words)):
                    param_name = "Icompl"+str(item)
                    icomplobj.set(param_name, int(words[item]))

            # Line 24
            if phase.get("Isy") == 1 or phase.get("Isy") == -1:

                # prepare
                symmopschool = phase.get("OperatorSet")
                Nsym = symmopschool.get("Nsym")
                MagMat = symmopschool.get("MagMat")
                DepMat = symmopschool.get("DepMat")
                linetoread = Nsym*(1+MagMat+DepMat)
                # read count = 1
                for nsym in xrange(0, Nsym):
                    # debug output print "Isy == 1/-1:  symmetry operator " + str(count) count += 1

                    combobj = PhaseModule.OperatorComboSymmetry(None)
                    symmopschool.set("OperatorCombo", combobj)
                    if phase.get("Isy") == 1:
                        self.Line24Read3x3(index, combobj, MagMat, DepMat)
                    elif phase.get("Isy") == -1:
                        self.Line24ReadAlpha(index, combobj, MagMat, DepMat)
                # debug output print "symmetry operator number = " + str(len(symmopschool.get("OperatorCombo")))
                index = index + linetoread

            elif phase.get("Isy") == -2:
                # prepare
                linetoread = phase.Nsym*(1+abs(phase.Ireps))
                #
                raise NotImplementedError("Line 24 Isy = -2 Not Implemented")

            elif phase.get("Isy") == 0:
                pass
            else:
                raise NotImplementedError(
                    "Line 24: No idea how to apply Isy = " + str(phase.get("Isy")))

            # Line 25
            if phase.get("Jbt") == 0:

                refinebiso = False

                for at in xrange(0, phase.get("Nat")):

                    # create atom
                    atom = AtomModule.AtomCrystal(None)
                    phase.set("Atom", atom)
                    # 25-1
                    words = {}
                    index = self.ReadByItem(11, words, index)
                    # debug output print "Line 25:  " + self.LineContent[index] print "\t---- " + str(words)
                    atom.set("Name", words[0])
                    atom.set("Typ",  words[1])
                    nX = toFloat(words[2])
                    nY = toFloat(words[3])
                    nZ = toFloat(words[4])
                    nBiso = toFloat(words[5])
                    nOcc = toFloat(words[6])
                    atom.set("In",   int(words[7]))
                    atom.set("Fin",  int(words[8]))
                    atom.set("N_t",  int(words[9]))
                    atom.set("Spc",  int(words[10]))
                    # 25-2
                    words = {}
                    index = self.ReadByItem(5, words, index, 6)
                    code = toFloat(words[0])
                    self.setRefine(fit, atom, "X", nX, code)
                    code = toFloat(words[1])
                    self.setRefine(fit, atom, "Y", nY, code)
                    code = toFloat(words[2])
                    self.setRefine(fit, atom, "Z", nZ, code)
                    biso_code = toFloat(words[3])
                    occ_code = toFloat(words[4])
                    self.setRefine(fit, atom, "Occ", nOcc, occ_code)
                    # debug output print "atom = " + str(atom.get("Name")) + "\tocc = " + str(nOcc) + " , " + str(occ_code)
                    # 25-3 ....
                    if atom.get("N_t") == 0:

                        # init object
                        atomicdisplace = AtomModule.AtomicDisplacementFactorIsotropic(
                            None)
                        atom.set("AtomicDisplacementFactor", atomicdisplace)
                        # set value
                        self.setRefine(fit, atomicdisplace,
                                       "Biso", nBiso, biso_code)

                        # support a new feature such that any biso_code > 0.0 should be
                        # set to refine
                        if abs(biso_code) > 0.99:
                            refinebiso = True

                    elif atom.get("N_t") == 2:

                        # init object
                        atomicdisplace = AtomModule.AtomicDisplacementFactorAnisotropic(
                            None)
                        atom.set("AtomicDisplacementFactor", atomicdisplace)
                        # set value
                        self.setRefine(fit, atomicdisplace,
                                       "Biso", nBiso, biso_code)
                        # Line 25-3-1
                        words = {}
                        B = {}
                        index = self.ReadByItem(6, words, index)
                        count = 0
                        for i in [(1, 1), (2, 2), (3, 3), (1, 2), (1, 3), (2, 3)]:
                            B[i] = toFloat(words[count])
                            count = count + 1
                        # Line 25-3-1
                        index = self.ReadByItem(6, words, index)
                        count = 0
                        for i in [(1, 1), (2, 2), (3, 3), (1, 2), (1, 3), (2, 3)]:
                            code = toFloat(words[count])
                            param_name = "B"+str(i[0])+str(i[1])
                            self.setRefine(fit, atomicdisplace,
                                           param_name, B[i], code)
                            count = count + 1

                    elif atom.get("N_t") == 4:
                        # init object
                        atomicdisplace = AtomModule.AtomicDisplacementFactorFormfactor(
                            None)
                        atom.set("AtomicDisplacementFactor", atomicdisplace)
                        # Line 25-3
                        f = {}
                        words = {}
                        index = self.ReadByItem(7, words, index)
                        count = 0
                        for i in xrange(1, 7+1):
                            f[i] = words[count]
                            count = count + 1
                        # Line 25-4
                        words = {}
                        index = self.ReadByItem(7, words, index)
                        count = 0
                        for i in xrange(1, 7+1):
                            code = toFloat(words[count])
                            codeindex = self.CodeWord(f[i], code, fit)
                            atom.f[i] = (f[i], codeindex)
                            count = count + 1
                        # Line 25-5
                        words = {}
                        index = self.ReadByItem(7, words, index)
                        count = 0
                        for i in xrange(1, 7+1):
                            f[i] = words[count]
                            count = count + 1
                        # Line 25-6
                        words = {}
                        index = self.ReadByItem(7, words, index)
                        count = 0
                        for i in xrange(1, 7+1):
                            code = toFloat(words[count])
                            self.setRefine(fit, atomicdisplace,
                                           param_name, f[i], code)
                            count = count + 1
                        # Line 25-7.8
                        if atom.get("Typ") == "SASH":
                            raise NotImplementedError("Line25-7.8 not implemented yet")
                            words = {}
                            index = self.ReadByItem(11, words, index)
                            atom.SHSA_type = words[0]
                            atom.Ncoeff = int(words[1])
                            for i in xrange(1, 9+1):
                                atom.Matrix[i] = toFloat(words[1+i])
                            # Line 25-8
                            index = index + 1
                            words = self.SplitNewLine(index)
                            if len(words) != 2*atom.Ncoeff and len(words) != 3*atom.Ncoeff:
                                warning.PCRFormatItemError(
                                    "3", "25-8 Jbt=0", str(words))
                            for l in xrange(0, len(words)):
                                atom.lmp[l+1] = int(words[l])

                # end for at

                if refinebiso is True and self.Style == "old":
                    for atom in phase.get("Atom"):
                        adp = atom.get("AtomicDisplacementFactor")
                        biso = adp.getConstraint("Biso")
                        if biso:
                            if not biso.on:
                                biso.turnRefineOn()
                        else:
                            errmsg = "Line 25:  Set all atoms' Biso to be refined.   All Biso should be able to turn on!\n"
                            errmsg += "Biso's Type = %-10s\n" % (type(biso))
                            errmsg += "Biso's class = %-30s" % (
                                biso.__class__.__name__)
                            raise RietError(errmsg)

                # End --      for atom in phase.get("Atom"):
                # End --  if self.refinebiso is True and self.Style == "old":

            elif phase.get("Jbt") == 1:

                for at in xrange(0, phase.get("Nat")):
                    # object init
                    atom = AtomModule.AtomMagneticScatter(None)
                    phase.set("Atom", atom)
                    magmoment = AtomModule.MagneticMomentCartesian(None)
                    atom.set("MagneticMoment", magmoment)
                    # Line 25-1
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 12:
                        warning.PCRFormatItemError(
                            "3", "25-1 Jbt=1", str(words))
                    atom.set("Name", words[0])
                    atom.set("Typ",  words[1])
                    atom.set("Mag",  int(words[2]))
                    atom.set("Vek",  int(words[3]))
                    X = toFloat(words[4])
                    Y = toFloat(words[5])
                    Z = toFloat(words[6])
                    Biso = toFloat(words[7])
                    Occ = toFloat(words[8])
                    RX = toFloat(words[9])
                    RY = toFloat(words[10])
                    RZ = toFloat(words[11])
                    # Line 25-2
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 8:
                        warning.PCRFormatItemError(
                            "3", "25-2 Jbt=1", str(words))
                    code = toFloat(words[0])
                    self.setRefine(fit, atom, "X", X, code)
                    code = toFloat(words[1])
                    self.setRefine(fit, atom, "Y", Y, code)
                    code = toFloat(words[2])
                    self.setRefine(fit, atom, "Z", Z, code)
                    code = toFloat(words[3])
                    self.setRefine(fit, atom, "Biso", Biso, code)
                    code = toFloat(words[4])
                    self.setRefine(fit, atom, "Occ", Occ, code)
                    code = toFloat(words[5])
                    self.setRefine(fit, magmoment, "RX", RX, code)
                    code = toFloat(words[6])
                    self.setRefine(fit, magmoment, "RY", RY, code)
                    code = toFloat(words[7])
                    self.setRefine(fit, magmoment, "RZ", RZ, code)
                    # Line 25-3
                    index = index + 1
                    words = self.SplitNewLine(index)
                    # debug out print "Line ... " + self.LineContent[index-1] print "Line ... " + self.LineContent[index]
                    if len(words) != 7:
                        warning.PCRFormatItemError(
                            "3", "25-3 Jbt=1", str(words))
                    IX = toFloat(words[0])
                    IY = toFloat(words[1])
                    IZ = toFloat(words[2])
                    B11 = toFloat(words[3])
                    B22 = toFloat(words[4])
                    B33 = toFloat(words[5])
                    MagPh = toFloat(words[6])
                    # Line 25-4
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 7:
                        warning.PCRFormatItemError(
                            "3", "25-4 Jbt=1", str(words))
                    code = toFloat(words[0])
                    self.setRefine(fit, magmoment, "IX", IX, code)
                    code = toFloat(words[1])
                    self.setRefine(fit, magmoment, "IY", IY, code)
                    code = toFloat(words[2])
                    self.setRefine(fit, magmoment, "IZ", IZ, code)
                    code = toFloat(words[3])
                    self.setRefine(fit, atom, "B11", B11, code)
                    code = toFloat(words[4])
                    self.setRefine(fit, atom, "B22", B22, code)
                    code = toFloat(words[5])
                    self.setRefine(fit, atom, "B33", B33, code)
                    code = toFloat(words[6])
                    self.setRefine(fit, atom, "MagPh", MagPh, code)

            elif phase.get("Jbt") == -1 and phase.get("Isy") != -2:

                for at in xrange(0, phase.get("Nat")):
                    # object init
                    atom = AtomModule.AtomMagneticScatter(None)
                    phase.set("Atom", atom)
                    magmoment = AtomModule.MagneticMomentSpherical(None)
                    atom.set("MagneticMoment", magmoment)
                    # Line 25-1
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 12:
                        warning.PCRFormatItemError(
                            "3", "25-1 Jbt=1", str(words))
                    atom.set("Name", words[0])
                    atom.set("Typ",  words[1])
                    atom.set("Mag",  int(words[2]))
                    atom.set("Vek",  int(words[3]))
                    X = toFloat(words[4])
                    Y = toFloat(words[5])
                    Z = toFloat(words[6])
                    Biso = toFloat(words[7])
                    Occ = toFloat(words[8])
                    RM = toFloat(words[9])
                    Rphi = toFloat(words[10])
                    Rthet = toFloat(words[11])
                    # Line 25-2
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 8:
                        warning.PCRFormatItemError(
                            "3", "25-2 Jbt=1", str(words))
                    code = toFloat(words[0])
                    self.setRefine(fit, atom, "X", X, code)
                    code = toFloat(words[1])
                    self.setRefine(fit, atom, "Y", Y, code)
                    code = toFloat(words[2])
                    self.setRefine(fit, atom, "Z", Z, code)
                    code = toFloat(words[3])
                    self.setRefine(fit, atom, "Biso", Biso, code)
                    code = toFloat(words[4])
                    self.setRefine(fit, atom, "Occ", Occ, code)
                    code = toFloat(words[5])
                    self.setRefine(fit, magmoment, "RM", RM, code)
                    code = toFloat(words[6])
                    self.setRefine(fit, magmoment, "Rphi", Rphi, code)
                    code = toFloat(words[7])
                    self.setRefine(fit, magmoment, "Rthet", Rthet, code)

                    # Line 25-3
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 7:
                        warning.PCRFormatItemError(
                            "3", "25-3 Jbt=1", str(words))
                    Im = toFloat(words[0])
                    Iphi = toFloat(words[1])
                    Ithet = toFloat(words[2])
                    B11 = toFloat(words[3])
                    B22 = toFloat(words[4])
                    B33 = toFloat(words[5])
                    MagPh = toFloat(words[6])
                    # Line 25-4
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 7:
                        warning.PCRFormatItemError(
                            "3", "25-4 Jbt=1", str(words))
                    code = toFloat(words[0])
                    self.setRefine(fit, magmoment, "IM", Im, code)
                    code = toFloat(words[1])
                    self.setRefine(fit, magmoment, "Iphi", Iphi, code)
                    code = toFloat(words[2])
                    self.setRefine(fit, magmoment, "Ithet", Ithet, code)
                    code = toFloat(words[3])
                    self.setRefine(fit, atom, "B11", B11, code)
                    code = toFloat(words[4])
                    self.setRefine(fit, atom, "B22", B22, code)
                    code = toFloat(words[5])
                    self.setRefine(fit, atom, "B33", B33, code)
                    code = toFloat(words[6])
                    self.setRefine(fit, atom, "MagPh", MagPh, code)

            elif phase.get("Jbt") == -1 and phase.get("Isy") == -2:

                for at in xrange(0, phase.get("Nat")):
                    # object init
                    atom = AtomModule.AtomMagneticBasisfunction(None)
                    phase.set("Atom", atom)
                    magmoment = AtomModule.MagneticMomentBasisfunction(None)
                    atom.set("MagneticMoment", magmoment)
                    # Line 25-1
                    C = {}
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 12:
                        warning.PCRFormatItemError(
                            "3", "25-1 Jbt=1", str(words))
                    atom.set("Name", words[0])
                    atom.set("Typ",  words[1])
                    atom.set("Mag",  int(words[2]))
                    atom.set("Vek",  int(words[3]))
                    X = toFloat(words[4])
                    Y = toFloat(words[5])
                    Z = toFloat(words[6])
                    Biso = toFloat(words[7])
                    Occ = toFloat(words[8])
                    for c in xrange(1, 3+1):
                        C[c] = toFloat(words[8+c])
                    # Line 25-2
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 8:
                        warning.PCRFormatItemError(
                            "3", "25-2 Jbt=-1", str(words))
                    code = toFloat(words[0])
                    self.set(fit, atom, "X", X, code)
                    code = toFloat(words[1])
                    self.set(fit, atom, "Y", Y, code)
                    code = toFloat(words[2])
                    self.set(fit, atom, "Z", Z, code)
                    code = toFloat(words[3])
                    self.set(fit, atom, "Biso", Biso, code)
                    code = toFloat(words[4])
                    self.set(fit, atom, "Occ", Occ, code)
                    for c in xrange(1, 3+1):
                        code = toFloat(words[4+c])
                        param_name = "C"+str(i)
                        self.setRefine(fit, magmoment, param_name, C[c], code)
                    # Line 25-3
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 7:
                        warning.PCRFormatItemError(
                            "3", "25-3 Jbt=-1", str(words))
                    for c in xrange(4, 9+1):
                        C[c] = toFloat(words[c-4])
                    MagPh = toFloat(words[6])
                    # Line 25-4
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 7:
                        warning.PCRFormatItemError(
                            "3", "25-4 Jbt=1", str(words))
                    for c in xrange(4, 9+1):
                        code = toFloat(words[c-4])
                        param_name = "C"+str(c)
                        self.setRefine(fit, magmoment, param_name, C[c], code)
                    code = toFloat(words[6])
                    self.set(fit, atom, "MagPh", MagPh, code)

            elif phase.get("Jbt") == -4:

                raise NotImplementedError("Jbt=-4 Not Implemented yet")

                for at in xrange(0, phase.get("Nat")):
                    # init object
                    atom = AtomModule.AtomRigid()
                    # Line 25
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 10:
                        warning.PCRFormatItemError(
                            "3", "25-1 Jbt=-4", str(words))
                    atom.Atom = words[0]
                    atom.Typ = words[1]
                    nP = {}
                    for p in xrange(1, 8+1):
                        nP[p] = toFloat(words[p+1])
                    # Line 25-2
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 8:
                        warning.PCRFormatItemError(
                            "3", "25-2 Jbt=-4", str(words))
                    for p in xrange(1, 8+1):
                        code = toFloat(words[p-1])
                        codeindex = self.CodeWord(nP[p], code, fit)
                        atom.P[p] = (nP[p], codeindex)
                    # Line 25-3
                    if len(words) != 7:
                        warning.PCRFormatItemError(
                            "3", "25-3 Jbt=-4", str(words))
                    nP = {}
                    for p in xrange(9, 15):
                        nP[p] = toFloat(words[p-9])
                    # Line 25-2
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 7:
                        warning.PCRFormatItemError(
                            "3", "25-4 Jbt=-4", str(words))
                    for p in xrange(9, 15+1):
                        code = toFloat(words[p-9])
                        codeindex = self.CodeWord(nP[p], code, fit)
                        atom.P[p] = (nP[p], codeindex)

            elif phase.get("Jbt") == 4:  # this is one figured out from file

                print("Jbt = 4 not implemented yet, Error, error, ERROR")
                return
                raise NotImplementedError("Jbt=4 not implemented yet")

                for at in xrange(0, phase.get("Nat")):
                    atom = AtomModule.Atom()
                    """
                    print "Atom " + str(at)
                    print self.LineContent[index+1]
                    print self.LineContent[index+2]
                    """
                    # Line 25
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 11:
                        warning.PCRFormatItemError(
                            "3", "25-1 Jbt=4", str(words))
                        raise NotImplementedError("")
                    atom.Atom = words[0]
                    atom.Typ = words[1]
                    X = toFloat(words[2])
                    Y = toFloat(words[3])
                    Z = toFloat(words[4])
                    Biso = toFloat(words[5])
                    Occ = toFloat(words[6])
                    P6 = toFloat(words[7])
                    THETA = toFloat(words[8])
                    PHI = toFloat(words[9])
                    atom.Spc = int(words[10])
                    # Line 25-1
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 5 and len(words) != 8:
                        warning.PCRFormatItemError(
                            "3", "25-2 Jbt=4", str(words))
                    code = toFloat(words[0])
                    codeindex = self.CodeWord(X, code, fit)
                    atom.X = (X, codeindex)
                    code = toFloat(words[1])
                    codeindex = self.CodeWord(Y, code, fit)
                    atom.Y = (Y, codeindex)
                    code = toFloat(words[2])
                    codeindex = self.CodeWord(Z, code, fit)
                    atom.Z = (Z, codeindex)
                    code = toFloat(words[3])
                    codeindex = self.CodeWord(Biso, code, fit)
                    atom.Biso = (Biso, codeindex)
                    code = toFloat(words[4])
                    codeindex = self.CodeWord(Occ, code, fit)
                    atom.Occ = (Occ, codeindex)
                    if len(words) == 8:
                        code = toFloat(words[5])
                        codeindex = self.CodeWord(P6, code, fit)
                        atom.P6 = (P6, codeindex)
                        code = toFloat(words[6])
                        codeindex = self.CodeWord(THETA, code, fit)
                        atom.THETA = (THETA, codeindex)
                        code = toFloat(words[7])
                        codeindex = self.CodeWord(PHI, code, fit)
                        atom.PHI = (PHI, codeindex)
                    else:
                        code = 0.0
                        codeindex = self.CodeWord(P6, code, fit)
                        atom.P6 = (P6, codeindex)
                        code = 0.0
                        codeindex = self.CodeWord(THETA, code, fit)
                        atom.THETA = (THETA, codeindex)
                        code = 0.0
                        codeindex = self.CodeWord(PHI, code, fit)
                        atom.PHI = (PHI, codeindex)
                    # Line 25-3
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 8 and len(words) != 3:
                        warning.PCRFormatItemError(
                            "3", "25-2 Jbt=4", str(words))
                    d = toFloat(words[0])
                    theta = toFloat(words[1])
                    phi = toFloat(words[2])
                    if len(words) == 8:
                        X0 = toFloat(words[3])
                        Y0 = toFloat(words[4])
                        Z0 = toFloat(words[5])
                        CHI = toFloat(words[6])
                        atom.P16 = toFloat(words[7])
                    # Line 25-4
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 3 and len(words) != 7:
                        warning.PCRFormatItemError(
                            "3", "25-2 Jbt=4", str(words))
                    code = toFloat(words[0])
                    codeindex = self.CodeWord(d, code, fit)
                    atom.d = (d, codeindex)
                    code = toFloat(words[1])
                    codeindex = self.CodeWord(theta, code, fit)
                    atom.theta = (theta, codeindex)
                    code = toFloat(words[2])
                    codeindex = self.CodeWord(phi, code, fit)
                    atom.phi = (phi, codeindex)
                    if len(words) == 7:
                        code = toFloat(words[3])
                        codeindex = self.CodeWord(X0, code, fit)
                        atom.X0 = (X0, codeindex)
                        code = toFloat(words[4])
                        codeindex = self.CodeWord(Y0, code, fit)
                        atom.Y0 = (Y0, codeindex)
                        code = toFloat(words[5])
                        codeindex = self.CodeWord(Z0, code, fit)
                        atom.Z0 = (Z0, codeindex)
                        code = toFloat(words[6])
                        codeindex = self.CodeWord(CHI, code, fit)
                        atom.CHI = (CHI, codeindex)
                    elif len(words) == 3:
                        code = 0.0
                        codeindex = self.CodeWord(X0, code, fit)
                        atom.X0 = (X0, codeindex)
                        code = 0.0
                        codeindex = self.CodeWord(Y0, code, fit)
                        atom.Y0 = (Y0, codeindex)
                        code = 0.0
                        codeindex = self.CodeWord(Z0, code, fit)
                        atom.Z0 = (Z0, codeindex)
                        code = 0.0
                        codeindex = self.CodeWord(CHI, code, fit)
                        atom.CHI = (CHI, codeindex)

            elif phase.get("Jbt") == 5 or phase.get("Jbt") == -5:

                for at in xrange(0, phase.get("Nat")):
                    # init atom
                    atom = AtomModule.AtomMagneticUserModel(None)
                    phase.set("Atom", atom)
                    # read
                    P = {}
                    # Line 25-1
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 12:
                        warning.PCRFormatItemError(
                            "3", "25-1 Jbt=1", str(words))
                    atom.set("Name", words[0])
                    atom.set("Typ",  words[1])
                    atom.set("Mag",  int(words[2]))
                    atom.set("Vek",  int(words[3]))
                    for p in xrange(1, 8+1):
                        P[p] = toFloat(words[p+3])
                    # Line 25-2
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 8:
                        warning.PCRFormatItemError(
                            "3", "25-2 Jbt=-1", str(words))
                    for p in xrange(1, 8+1):
                        code = toFloat(words[p-1])
                        param_name = "P"+str(p)
                        self.setRefine(fit, atom, param_name, P[p], code)
                    # Line 25-3
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 7:
                        warning.PCRFormatItemError(
                            "3", "25-3 Jbt=-1", str(words))
                    for p in xrange(9, 15+1):
                        P[p] = toFloat(words[p-9])
                    # Line 25-4
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 7:
                        warning.PCRFormatItemError(
                            "3", "25-4 Jbt=1", str(words))
                    for p in xrange(9, 15+1):
                        code = toFloat(words[p-9])
                        param_name = "P"+str(p)
                        self.setRefine(fit, atom, param_name, P[p], code)

            elif phase.get("Jbt") == 10 or phase.get("Jbt") == -10:

                # Line 25b Suite
                for at in xrange(0, phase.get("Nat")):
                    # init object
                    atom = AtomModule.AtomCombined(None)
                    phase.set("Atom", atom)
                    # 25b-1
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 11:
                        print("bugged line:\t" + str(words))
                        warning.PCRFormatItemError("3", "25b-1", str(words))
                        raise NotImplementedError("")
                    atom.set("Name", words[0])
                    atom.set("Typ",  words[1])
                    atom.set("Mag",  int(words[2]))
                    atom.set("Vek",  int(words[3]))
                    X = toFloat(words[4])
                    Y = toFloat(words[5])
                    Z = toFloat(words[6])
                    Biso = toFloat(words[7])
                    Occ = toFloat(words[8])
                    atom.set("N_t", int(words[9]))
                    # debut output print "read N_t = " + str(int(words[9]))
                    atom.set("Spc", int(words[10]))
                    # 25b-2
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 5:
                        warning.PCRFormatItemError("3", "25b-2", str(words))
                    code = toFloat(words[0])
                    self.setRefine(fit, atom, "X", X, code)
                    code = toFloat(words[1])
                    self.setRefine(fit, atom, "Y", Y, code)
                    code = toFloat(words[2])
                    self.setRefine(fit, atom, "Z", Z, code)
                    code = toFloat(words[3])
                    self.setRefine(fit, atom, "Biso", Biso, code)
                    code = toFloat(words[4])
                    self.setRefine(fit, atom, "Occ", Occ, code)
                    # 25b-3
                    # debut output print "starting... 25b-3:\tN_t = " + str(atom.get("N_t")) + "\tIsy = " + str(phase.get("Isy"))
                    if (atom.get("N_t") == 1 or atom.get("N_t") == 3) and phase.get("Isy") != -2:
                        # set magnetic moment
                        magmoment = AtomModule.MagneticMomentCartesian(None)
                        atom.set("MagneticMoment", magmoment)
                        # read
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            print("bugged line:\t" + str(words))
                            warning.PCRFormatItemError4(
                                "3", "25b-3", str(words), 7, "MagPar")
                        RX = toFloat(words[0])
                        RY = toFloat(words[1])
                        RZ = toFloat(words[2])
                        IX = toFloat(words[3])
                        IY = toFloat(words[4])
                        IZ = toFloat(words[5])
                        MagPh = toFloat(words[6])
                        # 25b-4
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            print("Error Line:\t" + self.LineContent[index])
                            warning.PCRFormatItemError(
                                "3", "25b-4", str(words))
                        code = toFloat(words[0])
                        self.setRefine(fit, magmoment, "RX", RX, code)
                        code = toFloat(words[1])
                        self.setRefine(fit, magmoment, "RY", RY, code)
                        code = toFloat(words[2])
                        self.setRefine(fit, magmoment, "RZ", RZ, code)
                        code = toFloat(words[3])
                        self.setRefine(fit, magmoment, "IX", IX, code)
                        code = toFloat(words[4])
                        self.setRefine(fit, magmoment, "IY", IY, code)
                        code = toFloat(words[5])
                        self.setRefine(fit, magmoment, "IZ", IZ, code)
                        code = toFloat(words[6])
                        self.setRefine(fit, magmoment, "MagPh", MagPh, code)

                    elif (atom.get("N_t") == -1 or atom.get("N_t") == -3):
                        # set magnetic moment
                        magmoment = AtomModule.MagneticMomentSpherical(None)
                        atom.set("MagneticMoment", magmoment)
                        # read
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError4(
                                "3", "25b-3", (words), 7, "MagPar")
                        RM = toFloat(words[0])
                        Rphi = toFloat(words[1])
                        Rthet = toFloat(words[2])
                        Im = toFloat(words[3])
                        Iphi = toFloat(words[4])
                        Ithet = toFloat(words[5])
                        MagPh = toFloat(words[6])
                        # Line 25b-4
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "25b-4", str(words))
                        code = toFloat(words[0])
                        self.setRefine(fit, magmoment, "RM", RM, code)
                        code = toFloat(words[1])
                        self.setRefine(fit, magmoment, "Rphi", Rphi, code)
                        code = toFloat(words[2])
                        self.setRefine(fit, magmoment, "Rthet", Rthet, code)
                        code = toFloat(words[3])
                        self.setRefine(fit, magmoment, "IM", Im, code)
                        code = toFloat(words[4])
                        self.setRefine(fit, magmoment, "Iphi", Iphi, code)
                        code = toFloat(words[5])
                        self.setRefine(fit, magmoment, "Ithet", Ithet, code)
                        code = toFloat(words[6])
                        self.setRefine(fit, magmoment, "MagPh", MagPh, code)

                    elif (atom.get("N_t") == 1 or atom.get("N_t") == 3) and phase.get("Isy") == -2:
                        # init
                        magmoment = AtomModule.MagneticMomentBasisfunction(
                            None)
                        atom.set("MagneticMoment", magmoment)
                        # read
                        C = {}
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError4(
                                "3", "25b-3", (words), 7, "MagPar")
                        for c in xrange(1, 6+1):
                            C[c] = toFloat(words[c-1])
                        # Line 25b-4
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "3", "25b-4", str(words))
                        for c in xrange(1, 6+1):
                            code = toFloat(words[c-1])
                            self.setRefine(fit, magmoment, C[c], code)

                    # 25b-5~6
                    if (atom.get("N_t") == 2 or atom.get("N_t") == 3 or atom.get("N_t") == -3) and phase.get("Isy") == -2:
                        # init
                        atomicdisplace = AtomModule.AtomicDisplacementFactorAnisotropic(
                            None)
                        atom.set("AtomicDisplacementFactor", atomicdisplace)
                        # read
                        B = {}
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "3", "25b-5", str(words))
                        counter = 0
                        for b in [(1, 1), (2, 2), (3, 3), (1, 2), (1, 3), (2, 3)]:
                            B[b] = toFloat(words[counter])
                            counter = counter + 1
                        # Line 25b-6
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "3", "25b-6", str(words))
                        counter = 0
                        for b in [(1, 1), (2, 2), (3, 3), (1, 2), (1, 3), (2, 3)]:
                            code = toFloat(words[counter])
                            param_name = "B"+str(b[0])+str(b[1])
                            self.setRefine(fit, atomicdisplace,
                                           param_name, B[b], code)
                    # 25b-7~8
                    if atom.get("N_t") == 4:
                        # init
                        atomicdisplace = AtomModule.AtomicDisplacementFactorFormfactor(
                            None)
                        atom.set("AtomicDisplacementFactor", atomicdisplace)
                        # read
                        f = {}
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "25b-7", str(words))
                        for i in xrange(1, 7+1):
                            f[i] = toFloat(words[i-1])
                        # Line 25b-8
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "25b-8", str(words))
                        for i in xrange(1, 7+1):
                            code = toFloat(words[i-1])
                            param_name = "f"+str(i)
                            self.setRefine(fit, atomicdisplace,
                                           param_name, f[i], code)
                        # Line 25b-9
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "25b-9", str(words))
                        for i in xrange(8, 14+1):
                            f[i] = toFloat(words[i-8])
                        # Line 25b-10
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "25b-10", str(words))
                        for i in xrange(8, 14+1):
                            code = toFloat(words[i-8])
                            param_name = "f"+str(i)
                            self.setRefine(fit, atomicdisplace,
                                           param_name, f[i], code)

            elif phase.get("Jbt") == 15 or phase.get("Jbt") == -15:

                raise NotImplementedError("Jbt = 15 not implemented yet")
                # Line 25b Suite
                for at in xrange(0, phase.get("Nat")):
                    atom = AtomModule.Atom()

                    # 25b-1
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 11:
                        warning.PCRFormatItemError("3", "25b-1", str(words))
                        raise NotImplementedError("")
                    atom.Atom = words[0]
                    atom.Typ = words[1]
                    atom.Mag = words[2]
                    atom.Vek = words[3]
                    X = toFloat(words[4])
                    Y = toFloat(words[5])
                    Z = toFloat(words[6])
                    Biso = toFloat(words[7])
                    Occ = toFloat(words[8])
                    atom.set("N_t", int(words[9]))
                    atom.Ndvk = int(words[10])
                    # 25b-2
                    index = index + 1
                    words = self.SplitNewLine(index)
                    if len(words) != 5:
                        warning.PCRFormatItemError("3", "25b-2", str(words))
                    code = toFloat(words[0])
                    codeindex = self.CodeWord(X, code, fit)
                    atom.X = (X, codeindex)
                    code = toFloat(words[1])
                    codeindex = self.CodeWord(Y, code, fit)
                    atom.Y = (Y, codeindex)
                    code = toFloat(words[2])
                    codeindex = self.CodeWord(Z, code, fit)
                    atom.Z = (Z, codeindex)
                    code = toFloat(words[3])
                    codeindex = self.CodeWord(Biso, code, fit)
                    atom.Biso = (Biso, codeindex)
                    code = toFloat(words[4])
                    codeindex = self.CodeWord(Occ, code, fit)
                    atom.Occ = (Occ, codeindex)
                    # 25b-3~4
                    if (atom.get("N_t") == 1 or atom.get("N_t") == 3):
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError4(
                                "3", "25b-3", (words), 7, "MagPar")
                        RX = toFloat(words[0])
                        RY = toFloat(words[1])
                        RZ = toFloat(words[2])
                        IX = toFloat(words[3])
                        IY = toFloat(words[4])
                        IZ = toFloat(words[5])
                        MagPh = toFloat(words[6])
                        # 25b-4
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError4(
                                "3", "25b-4", str(words))
                        code = toFloat(words[0])
                        codeindex = self.CodeWord(RX, code, fit)
                        atom.RX = (RX, codeindex)
                        code = toFloat(words[1])
                        codeindex = self.CodeWord(RY, code, fit)
                        atom.RY = (RY, codeindex)
                        code = toFloat(words[2])
                        codeindex = self.CodeWord(RZ, code, fit)
                        atom.RZ = (RZ, codeindex)
                        code = toFloat(words[3])
                        codeindex = self.CodeWord(IX, code, fit)
                        atom.IX = (IX, codeindex)
                        code = toFloat(words[4])
                        codeindex = self.CodeWord(IY, code, fit)
                        atom.IY = (IY, codeindex)
                        code = toFloat(words[5])
                        codeindex = self.CodeWord(IZ, code, fit)
                        atom.IZ = (IZ, codeindex)
                        code = toFloat(words[6])
                        codeindex = self.CodeWord(MagPh, code, fit)
                        atom.Magph = (MagPh, codeindex)
                    elif (atom.get("N_t") == -1 or atom.get("N_t") == -3):
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError4(
                                "3", "25b-3", (words), 7, "MagPar")
                        RM = toFloat(words[0])
                        Rphi = toFloat(words[1])
                        Rthet = toFloat(words[2])
                        Im = toFloat(words[3])
                        Iphi = toFloat(words[4])
                        Ithet = toFloat(words[5])
                        MagPh = toFloat(words[6])
                        # Line 25b-4
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "25b-4", str(words))
                        code = toFloat(words[0])
                        codeindex = self.CodeWord(RM, code, fit)
                        atom.RM = (RM, codeindex)
                        code = toFloat(words[1])
                        codeindex = self.CodeWord(Rphi, code, fit)
                        atom.Rphi = (Rphi, codeindex)
                        code = toFloat(words[2])
                        codeindex = self.CodeWord(Rthet, code, fit)
                        atom.Rthet = (Rthet, codeindex)
                        code = toFloat(words[3])
                        codeindex = self.CodeWord(Im, code, fit)
                        atom.Im = (Im, codeindex)
                        code = toFloat(words[4])
                        codeindex = self.CodeWord(Iphi, code, fit)
                        atom.Iphi = (Iphi, codeindex)
                        code = toFloat(words[5])
                        codeindex = self.CodeWord(Ithet, code, fit)
                        atom.Ithet = (Ithet, codeindex)
                        code = toFloat(words[6])
                        codeindex = self.CodeWord(MagPh, code, fit)
                        atom.Magph = (MagPh, codeindex)
                    elif atom.Ndvk != 0:
                        for dvk in xrange(1, abs(Ndvk)+1):
                            # 25-3 25b-3
                            # FIXME: never called, and can not find the definition of this function
                            newdp = DisplacementParameter()
                            index = index + 1
                            words = self.SplitNewLine(index)
                            if len(words) != 9:
                                warning.PCRFormatItemError4(
                                    "3", "25b-3: Jbt=+/-15 Ndvk!=0 " + "Line " + str(dvk), (words), 7, "MagPar")
                                raise NotImplementedError("Manual Error")
                            Dx = toFloat(words[0])
                            Dy = toFloat(words[1])
                            Dz = toFloat(words[2])
                            Dxi = toFloat(words[3])
                            Dyi = toFloat(words[4])
                            Dzi = toFloat(words[5])
                            Dphas = toFloat(words[6])
                            Dep = toFloat(words[6])
                            Dvek = toFloat(words[6])
                            # 25b-4
                            index = index + 1
                            words = self.SplitNewLine(index)
                            if len(words) != 7:
                                warning.PCRFormatItemError(
                                    "3", "25b-4", str(words))
                            code = toFloat(words[0])
                            codeindex = self.CodeWord(Dx, code, fit)
                            newdp.Dx = (Dx, codeindex)
                            code = toFloat(words[1])
                            codeindex = self.CodeWord(Dy, code, fit)
                            newdp.Dy = (Dy, codeindex)
                            code = toFloat(words[2])
                            codeindex = self.CodeWord(Dz, code, fit)
                            newdp.Dz = (Dz, codeindex)
                            code = toFloat(words[3])
                            codeindex = self.CodeWord(Dxi, code, fit)
                            newdp.Dxi = (Dxi, codeindex)
                            code = toFloat(words[4])
                            codeindex = self.CodeWord(Dyi, code, fit)
                            newdp.Dyi = (Dyi, codeindex)
                            code = toFloat(words[5])
                            codeindex = self.CodeWord(Dzi, code, fit)
                            newdp.Dzi = (Dzi, codeindex)
                            code = toFloat(words[6])
                            codeindex = self.CodeWord(Dphas, code, fit)
                            newdp.Dphas = (Dphas, codeindex)
                            # add new displacement parameter to atom
                            atom.Displacement[dvk] = newdp
                        # -- end for dvk
                    # Line 25-5~6
                    if (atom.get("N_t") == 2 or atom.get("N_t") == 3 or atom.get("N_t") == -3) and phase.get("Isy") == -2:
                        B = {}
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "3", "25b-5", str(words))
                        counter = 0
                        for b in [(1, 1), (2, 2), (3, 3), (1, 2), (1, 3), (2, 3)]:
                            B[b] = toFloat(words[counter])
                            counter = counter + 1
                        # Line 25b-6
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "3", "25b-6", str(words))
                        counter = 0
                        for b in [(1, 1), (2, 2), (3, 3), (1, 2), (1, 3), (2, 3)]:
                            code = toFloat(words[counter])
                            codeindex = self.CodeWord(B[b], code, fit)
                            atom.B[b] = (B[b], codeindex)
                    # 25b-7~10
                    if atom.get("N_t") == 4:
                        f = {}
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "25b-7", str(words))
                        for i in xrange(1, 7+1):
                            f[i] = toFloat(words[i-1])
                        # Line 25b-8
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "25b-8", str(words))
                        for i in xrange(1, 7+1):
                            code = toFloat(words[i-1])
                            codeindex = self.CodeWord(f[i], code, fit)
                            atom.f[i] = (f[i], codeindex)
                        # Line 25b-9
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "25b-9", str(words))
                        for i in xrange(8, 14+1):
                            f[i] = toFloat(words[i-8])
                        # Line 25b-10
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "25b-10", str(words))
                        for i in xrange(8, 14+1):
                            code = toFloat(words[i-8])
                            codeindex = self.CodeWord(f[i], code, fit)
                            atom.f[i] = (f[i], codeindex)
                    # 25b-11

                    # add atom
                    phase.AtomList[at] = atom
            elif phase.get("Jbt") == 2:
                pass
            else:
                errmsg = "No Atom To Read In.  Condition Unknown"
                raise RietError(errmsg)

            # Line 25.11
            if phase.get("Jdi") == 2:
                index = self.Line25_11Reader(index, phase)

            # Line 26-46
            # 1. Single crystal data or powder data
            powdersinglecrystal = "powder"
            for pattern in fit.get("Pattern"):
                contribution = fit.getContribution(pattern, phase)
                if contribution is not None and contribution.get("Irf") == 4:
                    powdersinglecrystal = "single"
                    break

            if powdersinglecrystal == "single":

                """
                Line 26 - 30
                """

                errormsg = "Single crystal is not supported at this moment (Line 26-30)"
                raise NotImplementedError(errormsg)

                # FIXME - The following codes for single crystal were implemented seriously, but not tested
                # SC  = {}
                # EXT = {}
                # Par = {}
                # SCC = fit.Patterns[1].ContributionList[phase.PHSNM]

                # # Line 26
                # index = index+1
                # words = self.SplitNewLine(index)
                # if len(words) != 6:
                #     warning.PCRFormatItemError("3", "26 Irf=4", str(words))
                # for sc in xrange(1, 6+1):
                #     SC[sc] = toFloat(words[sc-1])
                # # Line 26-1
                # index = index+1
                # words = self.SplitNewLine(index)
                # if len(words) != 6:
                #     warning.PCRFormatItemError("3", "26-1 Irf=4", str(words))
                # for sc in xrange(1, 6+1):
                #     code      = toFloat(words[sc-1])
                #     codeindex = self.CodeWord(SC[sc], code, fit)
                #     SCC.SC[sc]   = (SC[sc], codeindex)
                #
                # # Line 27
                # index = index+1
                # words = self.SplitNewLine(index)
                # if len(words) != 7 and len(words) != 8:
                #     warning.PCRFormatItemError("3", "27 Irf=4", str(words))
                # for sc in xrange(1, 7+1):
                #     EXT[sc] = toFloat(words[sc-1])
                # if len(words) == 8:
                #     SCC.ExtModel = int(words[7])
                # # Line 27-1
                # index = index+1
                # words = self.SplitNewLine(index)
                # if len(words) != 7:
                #     warning.PCRFormatItemError("3", "27-1 Irf=4", str(words))
                # for sc in xrange(1, 7+1):
                #     code      = toFloat(words[sc-1])
                #     codeindex = self.CodeWord(EXT[sc], code, fit)
                #     SCC.EXT[sc]   = (EXT[sc], codeindex)

                # # Line 29
                # index = index+1
                # words = self.SplitNewLine(index)
                # if len(words) != 6:
                #     warning.PCRFormatItemError("3", "29 Irf=4", str(words))
                # af = toFloat(words[0])
                # bf = toFloat(words[1])
                # cf = toFloat(words[2])
                # alphaf = toFloat(words[3])
                # betaf  = toFloat(words[4])
                # gammaf = toFloat(words[5])
                # # Line 29-1
                # index = index+1
                # words = self.SplitNewLine(index)
                # if len(words) != 6:
                #     warning.PCRFormatItemError("3", "29-1 Irf=4", str(words))
                # code      = toFloat(words[0])
                # codedinex = self.CodeWord(af, code, fit)
                # SCC.a = (af, codeindex)
                # code      = toFloat(words[1])
                # codedinex = self.CodeWord(bf, code, fit)
                # SCC.b = (bf, codeindex)
                # code      = toFloat(words[2])
                # codedinex = self.CodeWord(cf, code, fit)
                # SCC.c = (cf, codeindex)
                # code      = toFloat(words[3])
                # codedinex = self.CodeWord(alphaf, code, fit)
                # SCC.alpha = (alphaf, codeindex)
                # code      = toFloat(words[4])
                # codedinex = self.CodeWord(betaf, code, fit)
                # SCC.beta  = (betaf, codeindex)
                # code      = toFloat(words[5])
                # codedinex = self.CodeWord(gammaf, code, fit)
                # SCC.gamma = (gammaf, codeindex)

                # # Line 30
                # index = index+1
                # words = self.SplitNewLine(index)
                # if len(words) != 5:
                #     warning.PCRFormatItemError("3", "30 Irf=4", str(words))
                # for sc in xrange(1, 5+1):
                #     Par[sc] = toFloat(words[sc-1])
                # # Line 30-1
                # index = index+1
                # words = self.SplitNewLine(index)
                # if len(words) != 5:
                #     warning.PCRFormatItemError("3", "30-1 Irf=4", str(words))
                # for sc in xrange(1, 5+1):
                #     code      = toFloat(words[sc-1])
                #     codeindex = self.CodeWord(Par[sc], code, fit)
                #     SCC.Par[sc]   = (Par[sc], codeindex)

            else:
                # Powder Data:  Line 26 - 38

                for pattern in fit.get("Pattern"):

                    # get contribution  for this pattern and phase
                    contribution = fit.getContribution(pattern, phase)
                    if contribution is None:
                        # allow some contribution to be None
                        continue

                    # initalize and set up the profile
                    if pattern.get("Uni") == 0:
                        if contribution.get("Npr") != 11:
                            profile = ContributionModule.Profile2ThetaNonSPV(
                                None)
                        else:
                            profile = ContributionModule.Profile2ThetaSPV(None)
                    else:
                        profile = ContributionModule.ProfileTOF(None)
                    contribution.set("Profile", profile)

                    strainparameter = contribution.get("StrainParameter")

                    # Line 26, 26-1 and 27
                    index = index+1
                    words = self.SplitNewLine(index)
                    if pattern.get("Uni") == 0:    # 2theta
                        # Line 26
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "26 2theta", str(words))
                        try:
                            Scale = toFloat(words[0])
                            Shape1 = toFloat(words[1])
                            Bov = toFloat(words[2])
                            Str1 = toFloat(words[3])
                            Str2 = toFloat(words[4])
                            Str3 = toFloat(words[5])
                        except RietPCRError as err:
                            errmsg = "PCR File Error at Line 26: %-60s\n" % (
                                self.LineContent[index])
                            errmsg += "  Line 26 Content:  %-40s" % \
                                ("Scale, Shape1, Bov, Str1, Str2, Str3, Strain-Model")
                            errmsg += str(err)
                            raise RietPCRError(errmsg)
                        strainparameter.set(
                            "StrainModelSelector", int(words[6]))
                        # Line 26-1
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "3", "26-1 2theta", str(words))
                        code = toFloat(words[0])
                        self.setRefine(fit, contribution, "Scale", Scale, code)
                        code = toFloat(words[1])
                        self.setRefine(fit, profile, "Shape1", Shape1, code)
                        code = toFloat(words[2])
                        self.setRefine(fit, contribution, "Bov", Bov, code)
                        code = toFloat(words[3])
                        self.setRefine(fit, strainparameter,
                                       "Str1", Str1, code)
                        code = toFloat(words[4])
                        self.setRefine(fit, strainparameter,
                                       "Str2", Str2, code)
                        code = toFloat(words[5])
                        self.setRefine(fit, strainparameter,
                                       "Str3", Str3, code)

                        # Line 27
                        if contribution.get("Npr") != 11:
                            # Line 27
                            index = index + 1
                            words = self.SplitNewLine(index)
                            if len(words) != 8:
                                warning.PCRFormatItemError(
                                    "3", "27 2theta", str(words))
                            U = toFloat(words[0])
                            V = toFloat(words[1])
                            W = toFloat(words[2])
                            X = toFloat(words[3])
                            Y = toFloat(words[4])
                            GausSiz = toFloat(words[5])
                            LorSiz = toFloat(words[6])
                            contribution.set(
                                "SizeModelSelector", int(words[7]))
                            # debug output print "Size Model Line " + self.LineContent[index]
                            # Line 27-1
                            index = index+1
                            words = self.SplitNewLine(index)
                            if len(words) != 7:
                                warning.PCRFormatItemError(
                                    "3", "27-1 2theta", str(words))
                            code = toFloat(words[0])
                            self.setRefine(fit, profile, "U", U, code)
                            code = toFloat(words[1])
                            self.setRefine(fit, profile, "V", V, code)
                            code = toFloat(words[2])
                            self.setRefine(fit, profile, "W", W, code)
                            code = toFloat(words[3])
                            self.setRefine(fit, profile, "X", X, code)
                            code = toFloat(words[4])
                            self.setRefine(fit, profile, "Y", Y, code)
                            code = toFloat(words[5])
                            self.setRefine(
                                fit, profile, "GausSiz", GausSiz, code)
                            code = toFloat(words[6])
                            self.setRefine(
                                fit, profile, "LorSiz", LorSiz, code)
                        else:
                            # Line 27
                            index = index + 1
                            words = self.SplitNewLine(index)
                            if len(words) != 8:
                                warning.PCRFormatItemError("3", "27 2theta Npr = 11", str(
                                    words))                                           # read
                            UL = toFloat(words[0])
                            VL = toFloat(words[1])
                            WL = toFloat(words[2])
                            XL = toFloat(words[3])
                            Y = toFloat(words[4])
                            GausSiz = toFloat(words[5])
                            LorSiz = toFloat(words[6])
                            contribution.set(
                                "SizeModelSelector", int(words[7]))
                            # Line 27-1
                            index = index+1
                            words = self.SplitNewLine(index)
                            if len(words) != 7:
                                warning.PCRFormatItemError(
                                    "3", "27-1 2theta", str(words))
                            code = toFloat(words[0])
                            self.setRefine(fit, profile, "UL", UL, code)
                            code = toFloat(words[1])
                            self.setRefine(fit, profile, "VL", VL, code)
                            code = toFloat(words[2])
                            self.setRefine(fit, profile, "WL", WL, code)
                            code = toFloat(words[3])
                            self.setRefine(fit, profile, "XL", XL, code)
                            code = toFloat(words[4])
                            # FIXME - Figure out whether Y is useful or not
                            # self.setRefine(fit, profile, "Y", Y, code)
                            code = toFloat(words[5])
                            self.setRefine(
                                fit, profile, "GausSiz", GausSiz, code)
                            code = toFloat(words[6])
                            self.setRefine(
                                fit, profile, "LorSiz", LorSiz, code)
                            # Line 27-3
                            index = index + 1
                            words = self.SplitNewLine(index)
                            if len(words) != 5:
                                warning.PCRFormatItemError(
                                    "3", "27-3 2theta Npr = 11", str(words))
                            Ur = toFloat(words[0])
                            Vr = toFloat(words[1])
                            Wr = toFloat(words[2])
                            Eta0r = toFloat(words[3])
                            Xr = toFloat(words[4])
                            # Line 27-4
                            index = index+1
                            words = self.SplitNewLine(index)
                            if len(words) != 5:
                                warning.PCRFormatItemError(
                                    "3", "27-4 2theta", str(words))
                            code = toFloat(words[0])
                            self.setRefine(fit, profile, "UR", Ur, code)
                            code = toFloat(words[1])
                            self.setRefine(fit, profile, "VR", Vr, code)
                            code = toFloat(words[2])
                            self.setRefine(fit, profile, "WR", Wr, code)
                            code = toFloat(words[3])
                            self.setRefine(fit, profile, "Eta0r", Eta0r, code)
                            code = toFloat(words[4])
                            self.setRefine(fit, profile, "XR", Xr, code)
                    else:
                        # T.O.F and energy dispersive
                        # Line 26
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "26 TOF", str(words))
                            print("Line 26---:\t" + self.LineContent[index-1])
                            print("Line 26   :\t" + self.LineContent[index])
                            print("Line 26+++:\t" + self.LineContent[index+1])
                        # print "length of words: " + str(len(words))
                        Scale = toFloat(words[0])
                        Extinc = toFloat(words[1])
                        Bov = toFloat(words[2])
                        Str1 = toFloat(words[3])
                        Str2 = toFloat(words[4])
                        Str3 = toFloat(words[5])
                        strainparameter.set(
                            "StrainModelSelector", int(words[6]))
                        # debug output print "Line for Strain Model " + self.LineContent[index]
                        # Line 26-1
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "3", "26-1 2theta", str(words))
                        code = toFloat(words[0])
                        self.setRefine(fit, contribution, "Scale", Scale, code)
                        code = toFloat(words[1])
                        self.setRefine(fit, contribution,
                                       "Extinct", Extinc, code)
                        code = toFloat(words[2])
                        self.setRefine(fit, contribution, "Bov", Bov, code)
                        code = toFloat(words[3])
                        self.setRefine(fit, strainparameter,
                                       "Str1", Str1, code)
                        code = toFloat(words[4])
                        self.setRefine(fit, strainparameter,
                                       "Str2", Str2, code)
                        code = toFloat(words[5])
                        self.setRefine(fit, strainparameter,
                                       "Str3", Str3, code)

                        # Line 27
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 8:
                            warning.PCRFormatItemError(
                                "3", "27 TOF", str(words))
                        Sig2 = toFloat(words[0])
                        Sig1 = toFloat(words[1])
                        Sig0 = toFloat(words[2])
                        Xt = toFloat(words[3])
                        Yt = toFloat(words[4])
                        Z1 = toFloat(words[5])
                        Zo = toFloat(words[6])
                        contribution.set("SizeModelSelector", int(words[7]))

                        # Line 27-1
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 7:
                            warning.PCRFormatItemError(
                                "3", "27-1 TOF", str(words))
                        # Read
                        code = toFloat(words[0])
                        self.setRefine(fit, profile, "Sig2", Sig2, code)
                        code = toFloat(words[1])
                        self.setRefine(fit, profile, "Sig1", Sig1, code)
                        code = toFloat(words[2])
                        self.setRefine(fit, profile, "Sig0", Sig0, code)
                        code = toFloat(words[3])
                        # self.setRefine(fit, profile, "Xt", Xt, code)
                        code = toFloat(words[4])
                        # self.setRefine(fit, profile, "Yt", Yt, code)
                        code = toFloat(words[5])
                        self.setRefine(fit, profile, "Z1", Z1, code)
                        code = toFloat(words[6])
                        # self.setRefine(fit, profile, "Z0", Z0, code)
                        # Line 27-2
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 5:
                            warning.PCRFormatItemError(
                                "3", "27-2 TOF", str(words))
                        Gam2 = toFloat(words[0])
                        Gam1 = toFloat(words[1])
                        Gam0 = toFloat(words[2])
                        LStr = toFloat(words[3])
                        LSiz = toFloat(words[4])
                        # Line 27-3
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 5:
                            warning.PCRFormatItemError(
                                "3", "27-1 TOF", str(words))
                        code = toFloat(words[0])
                        self.setRefine(fit, profile, "Gam2", Gam2, code)
                        code = toFloat(words[1])
                        self.setRefine(fit, profile, "Gam1", Gam1, code)
                        code = toFloat(words[2])
                        self.setRefine(fit, profile, "Gam0", Gam0, code)
                        code = toFloat(words[3])
                        self.setRefine(fit, contribution, "LStr", LStr, code)
                        code = toFloat(words[4])
                        self.setRefine(fit, contribution, "LSiz", LSiz, code)

                    # END-IF pattern.get("Uni") == 0:    # 2theta

                    # Line 29
                    index = index + 1
                    # print "Line 29: a b c. ...: " + self.LineContent[index]
                    words = self.SplitNewLine(index)
                    if len(words) != 6:
                        warning.PCRFormatItemError("3", "29", str(words))
                    a = toFloat(words[0])
                    b = toFloat(words[1])
                    c = toFloat(words[2])
                    alpha = toFloat(words[3])
                    beta = toFloat(words[4])
                    gamma = toFloat(words[5])
                    # Line 29-1
                    index = index+1
                    words = self.SplitNewLine(index)
                    if len(words) != 6:
                        warning.PCRFormatItemError("3", "29-1", str(words))
                    code = toFloat(words[0])
                    self.setRefine(fit, phase, "a", a, code)
                    code = toFloat(words[1])
                    self.setRefine(fit, phase, "b", b, code)
                    code = toFloat(words[2])
                    self.setRefine(fit, phase, "c", c, code)
                    code = toFloat(words[3])
                    self.setRefine(fit, phase, "alpha", alpha, code)
                    code = toFloat(words[4])
                    self.setRefine(fit, phase, "beta", beta, code)
                    code = toFloat(words[5])
                    self.setRefine(fit, phase, "gamma", gamma, code)

                    # Line 30-33
                    if pattern.get("Uni") == 0:    # 2theta
                        # init object
                        asymparam = contribution.get("AsymmetryParameter")
                        # Line  30: read and process
                        preferorient = contribution.get("PreferOrient")
                        PA = {}
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 6 and len(words) != 8:
                            warning.PCRFormatItemError(
                                "3", "30 2theta", str(words))
                        Pref1 = toFloat(words[0])
                        Pref2 = toFloat(words[1])
                        for pa in xrange(1, 4+1):
                            PA[pa] = toFloat(words[1+pa])
                        # optional terms
                        if contribution.get("Npr") == 7:
                            if len(words) >= 8:
                                S_L = toFloat(words[6])
                                D_L = toFloat(words[7])
                            else:
                                S_L = 0.0
                                D_L = 0.0
                                print("Line 30 Term 7 and 8 missing: %-20s" % (words))
                        # Line 30-1: code
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 6 and len(words) != 8:
                            warning.PCRFormatItemError(
                                "3", "30-1 2theta", str(words))
                        code = toFloat(words[0])
                        self.setRefine(fit, preferorient, "Pref1", Pref1, code)
                        code = toFloat(words[1])
                        self.setRefine(fit, preferorient, "Pref2", Pref2, code)
                        for pa in xrange(1, 4+1):
                            code = toFloat(words[1+pa])
                            param_name = "PA"+str(pa)
                            self.setRefine(
                                fit, asymparam, param_name, PA[pa], code)
                        # optional terms
                        if contribution.get("Npr") == 7:
                            # read
                            if len(words) >= 8:
                                code1 = toFloat(words[6])
                                code2 = toFloat(words[7])
                            else:
                                code1 = 0.0
                                code2 = 0.0
                            self.setRefine(fit, asymparam, "S_L", S_L, code1)
                            self.setRefine(fit, asymparam, "D_L", D_L, code2)

                        # Line  32
                        if pattern.get("Ratio") < 0:
                            # init 2ndWave
                            wave2nd = ContributionModule.Profile2ndWave(None)
                            profile = contribution.get("Profile")
                            profile.set("Profile2ndWave", wave2nd)
                            # read
                            index = index + 1
                            words = self.SplitNewLine(index)
                            if len(words) != 3:
                                warning.PCRFormatItemError4(
                                    "3", "32 2theta", (words), 3, "<-")
                            U2 = toFloat(words[0])
                            V2 = toFloat(words[1])
                            W2 = toFloat(words[2])
                            # Line 32-1
                            index = index+1
                            words = self.SplitNewLine(index)
                            if len(words) != 3:
                                warning.PCRFormatItemError4(
                                    "3", "30-1 2theta", (words), 3, "<-")
                            code = toFloat(words[0])
                            self.setRefine(fit, wave2nd, "U2", U2, code)
                            code = toFloat(words[1])
                            self.setRefine(fit, wave2nd, "V2", V2, code)
                            code = toFloat(words[2])
                            self.setRefine(fit, wave2nd, "W2", W2, code)

                        # Line  33
                        if contribution.get("Npr") == 4 or contribution.get("Npr") > 7:
                            # init object AdditionProfileParameter
                            profileadd = contribution.get("Profile")
                            # read
                            index = index+1
                            words = self.SplitNewLine(index)
                            if len(words) != 4:
                                warning.PCRFormatItemError(
                                    "3", "33 2theta", str(words))
                            SHP1 = toFloat(words[0])
                            code = toFloat(words[1])
                            self.setRefine(fit, profileadd, "SHP1", SHP1, code)
                            SHP2 = float(words[1])
                            code = toFloat(words[3])
                            self.setRefine(fit, profileadd, "SHP2", SHP2, code)
                        # 2theta -- Line 30 ~ Line 33

                    elif pattern.get("Uni") == 1:  # T.O.F

                        # init object
                        expdecay = contribution.get("ExpDecayFunction")
                        preferorient = contribution.get("PreferOrient")
                        # Line  30
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "3", "30 T.O.F.", str(words))
                        Pref1 = toFloat(words[0])
                        Pref2 = toFloat(words[1])
                        ALPH0 = toFloat(words[2])
                        BETA0 = toFloat(words[3])
                        ALPH1 = toFloat(words[4])
                        BETA1 = toFloat(words[5])
                        # Line 30-1
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "3", "30-1 T.O.F.", str(words))
                        code = toFloat(words[0])
                        self.setRefine(fit, preferorient, "Pref1", Pref1, code)
                        code = toFloat(words[1])
                        self.setRefine(fit, preferorient, "Pref2", Pref2, code)
                        code = toFloat(words[2])
                        self.setRefine(fit, expdecay, "ALPH0", ALPH0, code)
                        code = toFloat(words[3])
                        self.setRefine(fit, expdecay, "BETA0", BETA0, code)
                        code = toFloat(words[4])
                        self.setRefine(fit, expdecay, "ALPH1", ALPH1, code)
                        code = toFloat(words[5])
                        self.setRefine(fit, expdecay, "BETA1", BETA1, code)

                        # Line 31
                        if contribution.get("Npr") == 10:
                            # read
                            index = index + 1
                            words = self.SplitNewLine(index)
                            if len(words) != 4:
                                warning.PCRFormatItemError(
                                    "3", "31 T.O.F.", str(words))
                            ALPH0T = toFloat(words[0])
                            BETA0T = toFloat(words[1])
                            ALPH1T = toFloat(words[2])
                            BETA1T = toFloat(words[3])
                            # Line 31-1
                            index = index+1
                            words = self.SplitNewLine(index)
                            if len(words) != 4:
                                warning.PCRFormatItemError(
                                    "3", "31-1 T.O.F.", str(words))
                            code = toFloat(words[0])
                            self.setRefine(
                                fit, expdecay, "ALPH0T", ALPH0T, code)
                            code = toFloat(words[1])
                            self.setRefine(
                                fit, expdecay, "BETA0T", BETA0T, code)
                            code = toFloat(words[2])
                            self.setRefine(
                                fit, expdecay, "ALPH1T", ALPH1T, code)
                            code = toFloat(words[3])
                            self.setRefine(
                                fit, expdecay, "BETA1T", BETA1T, code)
                        # Line 33
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 4:
                            warning.PCRFormatItemError4(
                                "3", "33 T.O.F", (words), 4, "ABS")
                        ABS1 = toFloat(words[0])
                        code = toFloat(words[1])
                        self.setRefine(fit, contribution, "ABS1", ABS1, code)
                        ABS2 = toFloat(words[2])
                        code = toFloat(words[3])
                        self.setRefine(fit, contribution, "ABS2", ABS2, code)

                    else:
                        pass
                    # -- end if : Line 30-33

                    # Line 34 - 35
                    if phase.get("Sol") != 0:
                        # base class init
                        shiftmodel = ContributionModule.ShiftParameter(None)
                        contribution.set("ShiftParameter", shiftmodel)
                        # read
                        SHF = {}
                        # Line 34
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 4:
                            warning.PCRFormatItemError("3", "34", str(words))
                        for shf in xrange(1, 3+1):
                            SHF[shf] = toFloat(words[shf-1])
                        shiftmodel.set("ModS", int(words[3]))
                        # debug output
                        if shiftmodel.get("ModS") > 100:
                            raise NotImplementedError("this is example of Laue class shift model")
                        # Line 34-1
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 3:
                            warning.PCRFormatItemError(
                                "3", "31-1 T.O.F.", str(words))
                        for shf in xrange(1, 3+1):
                            code = toFloat(words[shf-1])
                            param_name = "SHF"+str(shf)
                            self.setRefine(fit, shiftmodel,
                                           param_name, SHF[shf], code)
                        # Line 35
                        ModS = shiftmodel.get("ModS")
                        if ModS == 1 or ModS == -1:

                            # extend
                            shiftmodelangle = ContributionModule.ShiftParameterAngle(
                                None)
                            shiftmodelangle.extend(shiftmodel)
                            shiftmodel = shiftmodelangle
                            # read
                            index = index+1
                            words = self.SplitNewLine(index)
                            if len(words) != 3:
                                warning.PCRFormatItemError(
                                    "3", "35 (1)", str(words))
                            for s in xrange(1, 3+1):
                                param_name = "Sh"+str(s)
                                shiftmodel.set(param_name, toFloat(words[s-1]))

                        elif ModS >= -10 and ModS < -1:

                            # extend
                            shiftmodeluser = ContributionModule.ShiftParameterUserdefined(
                                None)
                            shiftmodeluser.extend(shiftmodel)
                            shiftmodel = shiftmodeluser
                            # read
                            for m in xrange(-ModS):
                                # init
                                shift = ContributionModule.SelectiveShift(None)
                                shiftmodel.set("SelectiveShift", shift)
                                # read
                                index = index+1
                                words = self.SplitNewLine(index)
                                if len(words) != 7:
                                    warning.PCRFormatItemError(
                                        "3", "35 (2)", str(words))
                                for s in xrange(1, 5+1):
                                    param_name = "n"+str(s)
                                    shift.set(param_name, int(words[s-1]))
                                Shift = toFloat(words[5])
                                code = toFloat(words[6])
                                self.setRefine(
                                    fit, shift, "Shift", Shift, code)

                        elif ModS == 101:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "-1")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [6, 5, 5, 5])

                        elif ModS == 102:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "1 2/m 1")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [4, 5, 4])

                        elif ModS == -102:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "1 1 2/m")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [4, 5, 4])

                        elif ModS == 103:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "mmm")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [3, 6])

                        elif ModS == 104:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "4/m")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [2, 4])

                        elif ModS == 105:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "4/mmm")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [2, 4])

                        elif ModS == 106:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "-3 R")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [2, 4])

                        elif ModS == 107:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "-3m R")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [2, 4])

                        elif ModS == 108:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "-3 H")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [2, 3])

                        elif ModS == 109:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "-3m1")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [2, 3])

                        elif ModS == 110:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "-31m")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [2, 3])

                        elif ModS == 111:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "6/m")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [2, 3])

                        elif ModS == 112:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "6/mmm")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [2, 3])

                        elif ModS == 113:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "m3")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [1, 2])

                        elif ModS == 114:

                            # extend
                            shiftmodellaue = ContributionModule.ShiftParameterLaue(
                                None, "m3m")
                            shiftmodellaue.extend(shiftmodel)
                            shiftmodel = shiftmodellaue
                            # read
                            index = self.Line35ReadLaueClass(
                                fit, shiftmodel, index, [1, 2])

                        raise NotImplementedError("Line 35 Not Debugged")

                    # end --- if phase.Sol != 0 Line 34-35

                    # Line 36
                    SizeModel = contribution.get("SizeModelSelector")
                    if SizeModel == 1 or SizeModel == -1:

                        # init
                        sizemodel = ContributionModule.SizeModelCylindrical(
                            None)
                        contribution.set("SizeModel", sizemodel)
                        # read
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 3:
                            warning.PCRFormatItemError(
                                "3", "36 Size-Model = +/-1", str(words))
                        for shf in xrange(1, 3+1):
                            param_name = "Sz"+str(shf)
                            contribution.set(param_name, toFloat(words[shf-1]))

                    elif SizeModel < -1:

                        # init
                        sizemodel = ContributionModule.SizeModelDefect(None)
                        contribution.set("SizeModel", sizemodel)
                        # read
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "6", "36 Size-Model < -1", str(words))
                        df = ContributionModule.DefectSizeBroaden(None)
                        sizemodel.set("DefectSizeBroaden", df)
                        for shf in xrange(1, 5+1):
                            param_name = "n"+str(shf)
                            df.set(param_name, int(words[shf-1]))
                        SZ = toFloat(words[5])
                        code = toFloat(words[6])
                        self.setRefine(fit, df, "SZ", SZ, code)

                    elif SizeModel == 15:

                        sizemodel = ContributionModule.SizeModelSpherical(
                            None, "2/m")
                        contribution.set("SizeModel", sizemodel)
                        shlist = [["Y00", "Y22+", "Y22-", "Y20",
                                   "Y44+", "Y44-"], ["Y42+", "Y42-", "Y40"]]
                        index = self.Line36ReadSphericalSizeModel(
                            fit, sizemodel, index, shlist)
                        # index = self.Line36ReadLaueClass(fit, sizemodel, index, [6, 3])

                    elif SizeModel == 16:

                        sizemodel = ContributionModule.SizeModelSpherical(
                            None, "-3 m H")
                        contribution.set("SizeModel", sizemodel)
                        index = self.Line36ReadLaueClass(
                            fit, sizemodel, index, [6, 1])

                    elif SizeModel == 17:

                        sizemodel = ContributionModule.SizeModelSpherical(
                            None, "m3")
                        contribution.set("SizeModel", sizemodel)
                        index = self.Line36ReadLaueClass(
                            fit, sizemodel, index, [5])

                    elif SizeModel == 18:

                        sizemodel = ContributionModule.SizeModelSpherical(
                            None, "mmm")
                        contribution.set("SizeModel", sizemodel)
                        index = self.Line36ReadLaueClass(
                            fit, sizemodel, index, [6])

                    elif SizeModel == 19:

                        sizemodel = ContributionModule.SizeModelSpherical(
                            None, "6/m")
                        contribution.set("SizeModel", sizemodel)
                        index = self.Line36ReadLaueClass(
                            fit, sizemodel, index, [6])

                    elif SizeModel == 20:

                        sizemodel = ContributionModule.SizeModelSpherical(
                            None, "-3")
                        contribution.set("SizeModel", sizemodel)
                        index = self.Line36ReadLaueClass(
                            fit, sizemodel, index, [5])

                    elif SizeModel == 21:

                        sizemodel = ContributionModule.SizeModelSpherical(
                            None, "4/m")
                        contribution.set("SizeModel", sizemodel)
                        index = self.Line36ReadLaueClass(
                            fit, sizemodel, index, [6, 2])

                    elif SizeModel == 22:

                        sizemodel = ContributionModule.SizeModelSpherical(
                            None, "-1")
                        contribution.set("SizeModel", sizemodel)
                        index = self.Line36ReadLaueClass(
                            fit, sizemodel, index, [6])

                    else:
                        if SizeModel != 0:
                            raise NotImplementedError(
                                "ModelSize Not Defined " + str(SizeModel))

                    # end --- if SizeModel != 0 Line 36

                    # Line 37
                    meet = 0
                    StrainModelType = strainparameter.get(
                        "StrainModelSelector")
                    Str = phase.get("Str")

                    # debug output print "Reading Strain Model = " + str(StrainModel)

                    if StrainModelType == 7:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAxial()
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 3:
                            warning.PCRFormatItemError(
                                "3", "37 StrainModel == 7", str(words))
                        for shf in xrange(1, 3+1):
                            param_name = "St"+str(shf)
                            strainmodel.set(param_name, toFloat(words[shf-1]))

                    if StrainModelType > 8 and Str == 0:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelMicro(None)
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        STR = {}
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 5:
                            warning.PCRFormatItemError(
                                "5", "37 StrainModel > 8 & Str = 0", str(words))
                        for shf in xrange(4, 8+1):
                            STR[shf] = toFloat(words[shf-4])
                        # 37-1
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 5:
                            warning.PCRFormatItemError(
                                "5", "37-1 StrainModel > 8 & Str = 0", str(words))
                        for shf in xrange(4, 8+1):
                            code = toFloat(words[shf-4])
                            param_name = "Str"+str(shf)
                            self.setRefine(fit, strainmodel,
                                           param_name, STR[shf], code)

                    if Str == -1 or Str == 2 or Str == 3:

                        meet = meet+1
                        # init
                        sizemodel = ContributionModule.SizeModelGeneral(None)
                        contribution.set("SizeModel", sizemodel)
                        # read
                        SZ = {}
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "5", "37 Str = -1, 2, 3", str(words))
                        for shf in xrange(1, 6+1):
                            SZ[shf] = words[shf-1]
                        # 37-1
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "5", "37-1 Str = -1, 2, 3", str(words))
                        for shf in xrange(1, 6+1):
                            code = toFloat(words[shf-1])
                            param_name = "SZ"+str(shf)
                            self.setRefine(
                                fit, sizemodel, param_name, SZ[shf], code)

                    if abs(Str) == 1 and StrainModelType == 1:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "-1")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [5, 5, 5])

                    if abs(Str) == 1 and StrainModelType == 2:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "1 2/m 1")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [5, 4])

                    if abs(Str) == 1 and StrainModelType == -2:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "1 1 2/m")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [5, 4])

                    if abs(Str) == 1 and StrainModelType == 3:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "mmm")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [6])

                    if abs(Str) == 1 and StrainModelType == 4:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "4/m")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [4])

                    if abs(Str) == 1 and StrainModelType == 5:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "4/mmm")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [4])

                    if abs(Str) == 1 and StrainModelType == 6:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "-3 R")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [4])

                    if abs(Str) == 1 and StrainModelType == 7:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "-3m R")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [4])

                    if abs(Str) == 1 and StrainModelType == 8:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "-3")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [3])

                    if abs(Str) == 1 and StrainModelType == 9:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "-3m1")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [3])

                    if abs(Str) == 1 and StrainModelType == 10:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "-31m")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [3])

                    if abs(Str) == 1 and StrainModelType == 11:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "6/m")
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [3])
                        strainparameter.set("StrainModel", strainmodel)
                        # read

                    if abs(Str) == 1 and StrainModelType == 12:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "6/mmm")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [3])

                    if abs(Str) == 1 and StrainModelType == 13:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "m3")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [2])

                    if abs(Str) == 1 and StrainModelType == 14:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelAnisotropic(
                            None, "m3m")
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        index = self.Line37ReadLaueClass(
                            fit, strainmodel, index, [2])

                    if (Str == 1 and StrainModelType == 0) or Str == 3:

                        meet = meet+1
                        # init
                        strainmodel = ContributionModule.StrainModelGeneral(15)
                        strainparameter.set("StrainModel", strainmodel)
                        # read
                        STR = {}
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "6", "37 Str=1 and Strain-model = 0, or Str = 3", str(words))
                        for shf in xrange(4, 9+1):
                            STR[shf] = words[shf-4]
                        # 37-1
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "6", "37-1 Str=1 and Strain-model = 0, or Str = 3", str(words))
                        for shf in xrange(4, 9+1):
                            code = toFloat(words[shf-4])
                            param_name = "STR"+str(shf)
                            self.setRefine(fit, strainmodel,
                                           param_name, STR[shf], code)

                        # 37-2
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "6", "37-2 Str=1 and Strain-model = 0, or Str = 3", str(words))
                        for shf in xrange(10, 15+1):
                            STR[shf] = words[shf-10]
                        # 37-3
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 6:
                            warning.PCRFormatItemError(
                                "3", "37-3 Str=1 and Strain-model = 0, or Str = 3", str(words))
                        for shf in xrange(10, 15+1):
                            code = toFloat(words[shf-10])
                            param_name = "STR"+str(shf)
                            self.setRefine(fit, strainmodel,
                                           param_name, STR[shf], code)

                    if meet > 1:
                        raise NotImplementedError(
                            "Line 37:  confusion... meet = " + str(meet))

                    # Line 38
                    if (contribution.get("Npr") >= 7 and strainparameter.get("StrainModelSelector") != 0) or Str == 1 or Str == 3:
                        # init
                        lorstrain = ContributionModule.LorentzianStrain(None)
                        strainparameter.set("LorentzianStrain", lorstrain)
                        # read
                        index = index+1
                        words = self.SplitNewLine(index)
                        if len(words) != 2:
                            warning.PCRFormatItemError("2", "38", str(words))
                        XI = toFloat(words[0])
                        code = toFloat(words[1])
                        self.setRefine(fit, lorstrain, "XI", XI, code)

                    # Line New 1: This is a new line not described in manual
                    for line in xrange(1, contribution.get("Nsp_Ref")+1):
                        # init
                        spref = ContributionModule.SpecialReflection(None)
                        contribution.set("SpecialReflection", spref)
                        # read
                        index = index + 1
                        words = self.SplitNewLine(index)
                        if len(words) != 10:
                            warning.PCRFormatItemError(
                                "3", "Line h k l nvk D-HG^2 Cod_D-HG^2 D-HL Cod_D-HL Shift Cod_Shif", str(words))
                        spref.set("h",   int(words[0]))
                        spref.set("k",   int(words[1]))
                        spref.set("l",   int(words[2]))
                        spref.set("nvk", int(words[3]))
                        dhg2 = toFloat(words[4])
                        codedhg = toFloat(words[5])
                        dhl = toFloat(words[6])
                        codedhl = toFloat(words[7])
                        shift = toFloat(words[8])
                        codeshift = toFloat(words[9])

                        self.setRefine(fit, spref, "D_HG2", dhg2, code)
                        self.setRefine(fit, spref, "D_HL",  dhl,  code)
                        self.setRefine(fit, spref, "Shift", shift, code)

                # end -- for pat in xrange (1, fit.NPATT+1)

            # end -- if Single Crysal -- elif Powder

            # print "--- Line 26 - 38 [for pat] is over ---"

            # Line 43
            index = self.Line43ReadFurth(fit, phase, index)

            # Line 44
            # debug output print "Line 44:\tNvk = " + str(phase.Nvk)
            index = self.Line44ReadNvk(fit, phase, index)

            # Line 45
            index = self.Line45ReadDis(fit, phase, index)

            """
            For 45-1 and 46, Meed to Know Mom is Mom for moments (magnetic) or angle:
            My rule is that:
            if Phase is a magnetic phase, i.e., Jbt = +/-1, +/-5, +/-10, +/-15,
            then it is a 'Magnetic Phase',
            and it has and can only have moments for magnetic MomMangetic;
            otherwise, it has and can only have moments for soft angle constraints
            """
            Jbt = phase.get("Jbt")
            if abs(Jbt) == 1 or abs(Jbt) == 5 or abs(Jbt) == 10 or abs(Jbt) == 15:
                phase.set("MomMoment", phase.get("MomMA"))
                phase.set("MomAngles", 0)
            else:
                phase.set("MomMoment", 0)
                phase.set("MomAngles", phase.get("MomMA"))

            # Line 45-1
            if phase.get("MomAngles") != 0:
                index = self.Line45_1ReadMomAngle(phase, fit, index)

            # Line 46
            if phase.get("MomMoment") != 0:
                index = self.Line46ReadMomMoment(phase, fit, index)

            # synchronize ionList with atom
            for ion in self.ionList[:]:
                # get information
                symbol = ion.get("Symbol")
                number = ion.get("number")

                # loop over atom
                count = 0
                for atom in phase.get("Atom"):
                    atomsymbol = atom.get("Typ")
                    ionsymbol = symbol+str(number)
                    if symbol == atomsymbol:
                        atom.set("IonNumber", number)
                        atom.set("Symbol",    symbol)
                        count += 1
                    elif atomsymbol.count(ionsymbol) > 0:
                        atom.set("IonNumber", number)
                        atom.set("Symbol",    symbol)
                        count += 1
                        messagespecial = "Special:  Atom Symbol = %-10s  Ion = %-10s" % (
                            atomsymbol, symbol)
                        print(messagespecial)

                # --- end for atom in phase ...
                # check
                if count == 0:
                    errmsg = "pcrFileReader... Block 3 synchronizing ion list with atom... Ion %-10s doesn't have a match\n" % (
                        symbol)
                    raise RietError(errmsg)

                # remove from list
                self.ionList.remove(ion)

            # --- end for ion in self.ionList

        """ -- end for phase in ... ---"""

        self.ReadIndex = index

        # debug output print "End of Block 3\n\n"

        return True

    """ --- End of method ReadBlock3 (Block 3) --- """

    #
    # Block 4
    #
    def ReadBlock4(self, fit):
        """
        Line 47 only: Parameter Limit
        """

        index = self.ReadIndex
        refine = fit.get("Refine")

        for line in xrange(0, fit.get("Nre")):

            # read 1 line and check
            index = index + 1
            words = self.SplitNewLine(index)
            Cry = fit.get("Cry")

            if Cry != 3 and (len(words) != 3 and len(words) != 6):
                warning.PCRFormatItemError(
                    "4", "Line 47 Cry != 3 - " + str(line), str(words))
            if Cry == 3 and len(words) != 6:
                warning.PCRFormatItemError(
                    "4", "Line 47 Cry == 3 - " + str(line), str(words))

            # first 3
            NUMPAR = int(words[0])
            codename = "Code"+str(NUMPAR)
            variable = refine.findVariable(codename)

            if variable is None:
                raise RietError("Block 4: Key " + str(NUMPAR) +
                                "  Doesn't Exit in RefineList")
            variable.set("min", toFloat(words[1]))
            variable.set("max", toFloat(words[2]))

            # second 3 for Cry = 3 case
            if Cry == 3 or len(words) == 6:
                variable.set("Step",     toFloat(words[3]))
                variable.set("Ibound",   int(words[4]))
                variable.set("name", words[5])

        self.ReadIndex = index

        return True

    # --- end ReadBlock4 (Block 4) ---

    #
    # Block 5
    #
    def ReadBlock5(self, fit):
        """
        Reading Inputs for Monte Carlo or Simulated Annealing
        Line 48, 49
        """

        index = self.ReadIndex

        # Line 48
        if fit.get("Cry") == 2:
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 4:
                warning.PCRFormatItemError("5", "48", str(words))
            NCONF = int(words[0])
            NSOLU = int(words[1])
            NREFLEX = int(words[2])
            NSCALEF = int(words[3])

        # Line 49
        if fit.get("Cry") == 3:
            # debug output print "Line 49: " + self.LineContent[index+1]
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6 and len(words) != 7:
                warning.PCRFormatItemError("5", "49", str(words))
            T_INI = toFloat(words[0])
            ANNEAL = toFloat(words[1])
            ACCEPT = toFloat(words[2])
            NUMTEMPS = int(words[3])
            NUMTHCYC = int(words[4])
            INITCONF = int(words[5])
            if len(words) == 7:
                fit.SEED_Random = int(words[6])
            # 49-1
            # debug output
            print("Line 49-1: " + self.LineContent[index+1])
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 5:
                warning.PCRFormatItemError("5", "49-1", str(words))
            NCYCLM = int(words[0])
            NSOLU = int(words[1])
            NREFLEX = int(words[2])
            NSCALEF = int(words[3])
            NALGOR = int(words[4])
            # 49-2
            print("Line 49-2: " + self.LineContent[index+1])
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 2:
                warning.PCRFormatItemError("5", "49", str(words))
            ISWAP = int(words[0])
            MCOMPL = int(words[1])
            # 49-3
            if MCOMPL != 0:
                # debug output
                print("Raise Error")
                raise NotImplementedError("Line 49-3")
            """ Next step to read Line 49-3 Not Implemented Yet """
            # index = index + 1
            # words = self.SplitNewLine(index)

        self.ReadIndex = index

        return True

    # --- end ReadBlock5  ---

    #
    # Read Block 6
    #

    def ReadBlock6(self, fit):
        """
        Line Printer Plot and Reflection List Output
        """
        index = self.ReadIndex

        # Line 50
        for pattern in fit.get("pattern"):
            if pattern.get("Ppl") == 1:
                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != 2:
                    raise NotImplementedError(
                        "6", "50-" + str(pat), str(words))
                pattern.get("ISCALE", int(words[0]))
                pattern.get("IDIF",   int(words[1]))

        # Line 51
        if fit.get("Rpa") == 2 or abs(fit.get("Rpa")) == 1 or fit.get("Rpa") == 0:
            index = index + 1
            if index < len(self.LineContent):
                words = self.SplitNewLine(index)
                if len(words) != 2:
                    warning.PCRFormatItemError("6", "51", str(words))
                fit.set("THET1", toFloat(words[0]))
                fit.set("THET2", toFloat(words[1]))
                if abs(fit.get("Rpa")) == 1 or fit.get("Rpa") == 0:
                    pass
            else:
                index = index - 1

        self.ReadIndex = index

        return True

    # -- end of ReadBlock6 --

    #

    # -- Secondary Service Functions --

    def SplitNewLine(self, index):
        try:
            newline = self.LineContent[index]
        except KeyError as err:
            for line in xrange(0, 200):
                if line in self.LineContent:
                    print(str(line) + ":\t" + self.LineContent[line])
            print("index = " + str(index))
            raise KeyError
        words = StringOP.SplitString(newline, ',')

        return words

    # end of SplitNewLine

    def ReadByItem(self, itemno, emptylist, index, allowednumber=None):
        """
        Read itemno of elements from line index to index + ?
        put the items in empylist
        return the line number where the last item is read
        """

        searching = True
        counter = 0
        while searching:
            try:
                index = index + 1
                words = self.SplitNewLine(index)
            except KeyError as err:
                print(str(err)+":\t" + self.LineContent[index])
            itemread = len(words)
            # print "-----------------------------------------------------> len = " + str(itemread)
            if itemread == 3:
                itemread = itemread - 1    # reason see pseudocode Line 10
                # print "---------------------------------------------------------> Find it  " + str(counter)
            for i in xrange(0, itemread):
                emptylist[counter] = words[i]
                counter = counter + 1
            if counter == itemno:
                searching = False
            elif counter > itemno:
                searching = False
                if counter != allowednumber:
                    print("----------------------------------------------------------------------------------------------------> ")
                    print("Item Number is Strange:  Intend to read = " + str(itemno) + "\t  exact number = " + str(counter))
                    print("Line -1: " + self.LineContent[index-1])
                    print("Line   : " + self.LineContent[index])

        # print "Counter = " + str(counter)
        return index

    # end of ReadByItem

    def isDataFile(self, tempname):
        """
        Line 5 may be omitted if the data file name
        Line 6 (optional) is an "...irf" file
        Line 7 (compulsory) starts with integer 0, 1 or 2
        """

        # 1. line 6
        test6 = tempname.split(".")
        if len(test6) >= 2:
            if test6[1] == "irf":
                return False

        # 2. line 7
        if len(tempname) >= 3:
            return True
        else:
            return False

    def useDefaultDataFile(self):
        tempname = self.PCR
        index = tempname.rfind('/')
        if index < 0:
            index = tempname.rfind('\\')
        if index > 0:
            tempname = tempname[index+1:]
        # generate name
        templist = tempname.split('.')
        tempname = templist[0] + ".dat"
        # print("***********"+tempname+"**************")
        return tempname

    # end -- useDefaultDataFile

    def CodeWord(self, value, code, fit):
        """
        add a refinable to FitTable
        add a relation to FitTable
        """

        result = fit.FitTable.addRefine(code, value)
        if type(result) == type(True):
            if result is False:    # not to refine
                return False
            else:
                raise NotImplementedError("Cannot be True")
        else:
            fittableindex = fit.FitTable.addRelation(result, code)
            return fittableindex

    # end -- CodeWord

    def Line12ReadTable(self, index, formfactortable):
        reading = True
        while reading:
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) == 2:
                A = toFloat(words[0])
                a = toFloat(words[1])
                ffu = PatternModule.FormfactorUserdefined(None)
                ffu.set("A", A)
                ffu.set("a", a)
                formfactortable.set("FormfactorUserdefined", ffu)
            elif len(words) == 1:
                mark = int(toFloat(words[0]))
                if mark == -100:
                    reading = False
                else:
                    print("Reading wrong line in Line12 table\t"+str(words))
                    raise NotImplementedError("")
            else:
                print("Reading wrong line in Line12 table\t"+str(words))
                raise NotImplementedError("")

        return index

    # end -- Line12ReadTable

    def Line17Read(self, fit, pattern, index):
        """
        Read Line 17
        """

        # debug output print "\nReading Line 17\n"

        # 12-2theta  CHECK NEED TO ASK A QUESTION
        if pattern.get("Nba") == -3 or pattern.get("Nba") == -4:

            # debug output print "Read Line 17"

            background = PatternModule.BackgroundPolynomial(None)
            background.extend(pattern.get("Background"))
            pattern.get("Background").set("Bkpos", pattern.get("Bkpos"))

            tempvalues = {}
            tempcodes = {}
            # 17-1
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6:
                warning.PCRFormatItemError("2", "17-1: 12 coeff", str(words))
            for i in xrange(0, 6):
                tempvalues[i] = toFloat(words[i])
            # 17-2
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6:
                warning.PCRFormatItemError("2", "17-2: 12 coeff", str(words))
            for i in xrange(0, 6):
                tempcodes[i] = toFloat(words[i])
            # 17-3
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6:
                warning.PCRFormatItemError("2", "17-3: 12 coeff", str(words))
            for i in xrange(0, 6):
                tempvalues[i+6] = toFloat(words[i])
            # 17-4
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6:
                warning.PCRFormatItemError("2", "17-4: 12 coeff", str(words))
            for i in xrange(0, 6):
                tempcodes[i+6] = toFloat(words[i])
            # combine codes ...
            for i in xrange(0, 12):
                param_name = "BACK"
                self.setRefine(fit, background, param_name,
                               tempvalues[i], tempcodes[i], i)
            # xpc add new code start:
            if (pattern.get("Nba") == -4):
                # 17-5
                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != 6:
                    warning.PCRFormatItemError(
                        "2", "17-5: 12 coeff", str(words))
                for i in xrange(0, 6):
                    tempvalues[i] = toFloat(words[i])
                # 17-6
                index = index + 1
                words = self.SplitNewLine(index)
                if len(words) != 6:
                    warning.PCRFormatItemError(
                        "2", "17-6: 12 coeff", str(words))
                for i in xrange(0, 6):
                    tempcodes[i] = toFloat(words[i])
                # combine codes ...
                for i in xrange(0, 6):
                    param_name = "BACK"
            # xpc end
        elif pattern.get("Nba") == -2:    # Fourier filtering

            # fit.Patterns[pat].setAnalyticalBackgound("filter", 0)
            background = PatternModule.BackgroundFourierwindow(None)
            background.extend(pattern.get("Background"))
            # 17
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 1:
                warning.PCRFormatItemError("2", "17: Fwindow", str(words))
            background.set("FWINDOW", int(words[0]))

        elif pattern.get("Nba") == -1:    # Poly + Debye

            background = PatternModule.BackgroundDebye(None)
            background.extend(pattern.get("Background"))
            tempvalues = {}
            tempcodes = {}
            # 17-1
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6:
                warning.PCRFormatItemError("2", "17-1: 6 coeff", str(words))
            for i in xrange(0, 6):
                tempvalues[i] = toFloat(words[i])
            # 17-2
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6:
                warning.PCRFormatItemError("2", "17-2: 6 coeff", str(words))
            for i in xrange(0, 6):
                tempcodes[i] = toFloat(words[i])
            # combine
            for i in xrange(0, 6):
                # codeindex = self.CodeWord(tempvalues[i], tempcodes[i], fit)
                # fit.Patterns[pat].AnalyBackground.BACK[i+1] = (tempvalues[i], codeindex)
                param_name = "BACK"+str(i+1)
                self.setRefine(fit, background, param_name,
                               tempvalues[i], tempcodes[i])
            # 17-3
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6:
                warning.PCRFormatItemError("2", "17-3: 6 coeff", str(words))
            for i in xrange(0, 6):
                tempvalues[i] = toFloat(words[i])
            # 17-4
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6:
                warning.PCRFormatItemError("2", "17-4: 6 coeff", str(words))
            for i in xrange(0, 6):
                tempcodes[i] = toFloat(words[i])
            # combine
            for i in xrange(0, 6):
                # codeindex = self.CodeWord(tempvalues[i], tempcodes[i], fit)
                # fit.Patterns[pat].AnalyBackground.Bc[i+1] = (tempvalues[i], codeindex)
                param_name = "Bc"+str(i+1)
                self.setRefine(fit, background, param_name,
                               tempvalues[i], tempcodes[i])
            # 17-5
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6:
                warning.PCRFormatItemError("2", "17-5: 6 coeff", str(words))
            for i in xrange(0, 6):
                tempvalues[i] = toFloat(words[i])
            # 17-6
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6:
                warning.PCRFormatItemError("2", "17-6: 12 coeff", str(words))
            for i in xrange(0, 6):
                tempcodes[i] = toFloat(words[i])
            # combine
            for i in xrange(0, 6):
                # codeindex = self.CodeWord(tempvalues[i], tempcodes[i], fit)
                # fit.Patterns[pat].AnalyBackground.D[i+1] = (tempvalues[i], codeindex)
                param_name = "D"+str(i+1)
                self.setRefine(fit, background, param_name,
                               tempvalues[i], tempcodes[i])

        elif pattern.get("Nba") == 0:

            # debug output print "Set Nba = 0   -----------> "

            # fit.Patterns[pat].setAnalyticalBackgound("poly", 6)
            background = PatternModule.BackgroundPolynomial(None)
            background.extend(pattern.get("Background"))
            pattern.get("Background").set("Bkpos", pattern.get("Bkpos"))

            # debug output test
            background2 = pattern.get("Background")
            if not isinstance(background2, PatternModule.Background):
                raise NotImplementedError("Nba == 0")

            tempvalues = {}
            tempcodes = {}
            # 17-1
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6:
                warning.PCRFormatItemError("2", "17-1: 12 coeff", str(words))
            for i in xrange(0, 6):
                tempvalues[i] = toFloat(words[i])
            # 17-2
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 6:
                warning.PCRFormatItemError("2", "17-2: 12 coeff", str(words))
            for i in xrange(0, 6):
                tempcodes[i] = toFloat(words[i])
            # combine codes ...
            for i in xrange(0, 6):
                param_name = "BACK"
                self.setRefine(fit, background, param_name,
                               tempvalues[i], tempcodes[i], i)

        elif pattern.get("Nba") == 1:

            # fit.Patterns[pat].setAnalyticalBackgound("poly", 4)
            background = PatternModule.BackgroundPolynomial(None)
            background.extend(pattern.get("Background"))
            pattern.get("Background").set("Bkpos", pattern.get("Bkpos"))

            tempvalues = {}
            tempcodes = {}
            # 17-1
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 4:
                warning.PCRFormatItemError("2", "17-1: 12 coeff", str(words))
            for i in xrange(0, 4):
                tempvalues[i] = toFloat(words[i])
            # 17-2
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 4:
                warning.PCRFormatItemError("2", "17-2: 12 coeff", str(words))
            for i in xrange(0, 4):
                tempcodes[i] = toFloat(words[i])
            # combine codes ...
            for i in xrange(0, 4):
                param_name = "BACK"
                self.setRefine(fit, background, param_name,
                               tempvalues[i], tempcodes[i], i)

        """ end if """

        return index

    # end -- Line17Read

    def Line22Read(self, index):
        words = {}
        theline = self.LineContent[index]

        if theline.count("<-") == 0:
            """ magnetic  """

            words = theline.split("Mag")
            if len(words) == 2:
                words[0] = words[0].strip()
                words[1] = "Mag"+words[1].strip()
            else:
                print("Error -- Line 22-1\t" + self.LineContent[index-1])
                print("Error -- Line 22: \t" + self.LineContent[index])
                raise NotImplementedError("Line 22: Contain more than 1 Mag")

        elif theline.count("<-") == 1:
            """ space group """

            words = theline.split("<-")

            if len(words) == 2:
                words[0] = words[0].strip()
                words[1] = words[1].strip()
            else:
                raise NotImplementedError("Line 22: Contain more than 1 <-")

        else:
            """ exception """
            raise NotImplementedError("Line 22: Exception")

        return words

    # end -- Line22Read(index)

    def Line24Read3x3(self, index, operatorcombo, MagMat, DepMat):
        """
        Read 1 block of symmetry operator, including
        1      line  of 3x3 symmetry operator
        DepMat lines of 3x3 Fourier displacement 
        MagMat lines of 3x3 magnetic operator

        operatorcombo:  operatorcombo object
        MagMat:         integer
        DepMat:         integer
        """
        Sop = {}
        # 1. symmetry operator
        index = index + 1
        words = self.SplitNewLine(index)
        if len(words) != 12:
            warning.PCRFormatItemError("3", "24 - Isy=-1  Symm", str(words))
        count = 0
        # init object
        symop = PhaseModule.SymmetryMatrix33(operatorcombo)
        operatorcombo.set("SymmetryMatrix", symop)
        # read
        for i in xrange(1, 4):
            for j in xrange(1, 4):
                param_name = "S"+str(i)+str(j)
                symop.set(param_name, int(words[count]))
                count = count + 1
            param_name = "T"+str(i)
            symop.set(param_name, toFloat(words[count]))
            count = count + 1
        # 2. Fourier component of displacement
        for dp in xrange(1, DepMat+1):
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 10:
                warning.PCRFormatItemError("3", "24 - Isy=-1  Mag", str(words))
            count = 0
            # init object
            depop = PhaseModule.RotationalMatrix33(None)
            operatorcombo.set("DisplacementMatrix", depop)
            # read
            for i in xrange(1, 4):
                for j in xrange(1, 4):
                    param_name = "R"+str(i)+str(j)
                    depop.set(param_name, int(words[count]))
                    count = count + 1
            depop.set("Phase", toFloat(words[count]))
        # 3. magnetic operator
        for mg in xrange(1, MagMat+1):
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 10:
                warning.PCRFormatItemError("3", "24 - Isy=-1  Mag", str(words))
            count = 0
            # init object
            magop = PhaseModule.RotationalMatrix33(None)
            operatorcombo.set("MagneticMatrix", magop)
            # read
            for i in xrange(1, 4):
                for j in xrange(1, 4):
                    param_name = "R"+str(i)+str(j)
                    magop.set(param_name, int(words[count]))
                    count = count + 1
            magop.set("Phase", toFloat(words[count]))

        return

    def Line24ReadAlpha(self, index, operatorcombo, MagMat, DepMat):
        """
        Read 1 block of symmetry operator, including
        1      line  of alpha-numeric symmetry operator
        DepMat lines of alpha-numeric Fourier displacement 
        MagMat lines of alpha-numeric magnetic operator

        operatorcombo:  operatorcombo object
        MagMat:         integer
        DepMat:         integer
        """
        # 1. symmetry operator
        index = index + 1
        words = self.SplitNewLine(index)
        if len(words) != 4:
            warning.PCRFormatItemError(
                "3", "24 - Isy=-1  Symm alpha", str(words))
        # init object
        symop = PhaseModule.SymmetryMatrixAlpha(None)
        operatorcombo.set("SymmetryMatrix", symop)
        # debug
        """
        testmatrix = operatorcombo.get("SymmetryMatrix")
        if not isinstance(testmatrix, SymmetryMatrixAlpha):
            raise NotImplementedError, "Line24ReadAlpha"
        else:
            print "set operator OK"
        """
        # read
        symop.set("X", words[1])
        symop.set("Y", words[2])
        symop.set("Z", words[3])
        # 2. Fourier component of displacement
        for dp in xrange(1, DepMat+1):
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 5:
                warning.PCRFormatItemError(
                    "3", "24 - Isy=-1  Mag alpha", str(words))
            # init object
            depop = PhaseModule.RotationalMatrixAlpha()
            operatorcombo.set("DisplaceMatrix", depop)
            # read
            depop.set("X", words[1])
            depop.set("Y", words[2])
            depop.set("Z", words[3])
            depop.set("Phase", toFloat(words[4]))
        # 3. magnetic operator
        for mg in xrange(1, MagMat+1):
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 5:
                warning.PCRFormatItemError("3", "24 - Isy=-1  Mag", str(words))
            # init object
            magop = PhaseModule.RotationalMatrixAlpha(None)
            operatorcombo.set("MagneticMatrix", magop)
            # read
            magop.set("X", words[1])
            magop.set("Y", words[2])
            magop.set("Z", words[3])
            magop.set("Phase", toFloat(words[4]))

        return

    def Line25_11Reader(self, index, phase):
        """
        Read Line 25b-11

        index: previous line index
        """
        # debug output print "Reading Line 25..........."

        transformation = PhaseModule.TransformationMatrixSet(None)
        phase.set("TransformationMatrixSet", transformation)

        # Line 25b-11-1
        index += 1
        words = self.SplitNewLine(index)
        if len(words) != 4:
            warning.PCRFormatItemError("3", "25-11-1, Jbt=+/-15", str(words))
        for i in xrange(1, 3+1):
            param_name = "T1"+str(i)
            transformation.set(param_name, toFloat(words[i-1]))
        transformation.set("Or_sh1", toFloat(words[3]))
        # Line 25b-11-1
        index += 1
        words = self.SplitNewLine(index)
        if len(words) != 4:
            warning.PCRFormatItemError("3", "25-11-2, Jbt=+/-15", str(words))
        for i in xrange(1, 3+1):
            param_name = "T2"+str(i)
            transformation.set(param_name, toFloat(words[i-1]))
        transformation.set("Or_sh2", toFloat(words[3]))
        # Line 25b-11-1
        index += 1
        words = self.SplitNewLine(index)
        if len(words) != 4:
            warning.PCRFormatItemError("3", "25-11-3, Jbt=+/-15", str(words))
        for i in xrange(1, 3+1):
            param_name = "T3"+str(i)
            transformation.set(param_name, toFloat(words[i-1]))
        transformation.set("Or_sh3", toFloat(words[3]))

        return index

    #
    # Read Line 35: Laue

    def Line35ReadLaueClass(self, fit, shiftmodel, index, LineItemList):
        """
        Read Line 35 (3) LaueClass

        fit:    fit reference
        shiftmodel: shiftmodel reference
        laueclass:  
        index:  line of index
        LineItemList: a list of number of items in a line
        """
        count = 0
        laue = LaueShiftParameter(shiftmodel.get("Laueclass"))
        for l in xrange(len(LineItemList)):
            # read file
            index = index + 1
            words1 = self.SplitNewLine(index)
            if len(words1) != LineItemList[l]:
                warning.PCRFormatItemError(
                    "3", "35 (3) - Line " + str(index) + " laue: " + laue.Name, str(words1))
            index = index + 1
            words2 = self.SplitNewLine(index)
            if len(words2) != LineItemList[l]:
                warning.PCRFormatItemError(
                    "3", "35 (3) - Line " + str(index) + " laue: " + laue.Name, str(words2))

            # set value to fit-suite
            for r in xrange(LineItemList[l]):
                # init
                hkl = laue.get()
                shift = ContributionModule.GeneralShift(None, hkl)
                shiftmodel.set("GeneralShift", shift)
                # read and set
                Ditem = toFloat(words1[r])
                code = toFloat(words2[r])
                self.setRefine(fit, shift, "D", Ditem, code)

        return index

    #
    # Read Line 36: Laue

    def Line36ReadLaueClass(self, fit, sizemodel, index, LineItemList):
        """
        Read Line 36 LaueClass:  Size Model
        """
        count = 0
        for l in xrange(len(LineItemList)):
            index = index + 1
            words1 = self.SplitNewLine(index)
            if len(words1) != LineItemList[l]:
                # warning.PCRFormatItemError("3", "35 (3) - Line " + str(index) + " laue: " + laue.Name, str(words1))
                warning.PCRFormatItemError(
                    "3", "35 (3) - Line " + str(index) + " laue: ", str(words1))
            index = index + 1
            words2 = self.SplitNewLine(index)
            if len(words2) != LineItemList[l]:
                # warning.PCRFormatItemError("3", "35 (3) - Line " + str(index) + " laue: " + laue.Name, str(words2))
                warning.PCRFormatItemError(
                    "3", "35 (3) - Line " + str(index) + " laue: ", str(words2))
            for r in xrange(LineItemList[l]):
                # init
                shcoeff = ContributionModule.SHcoefficient(None)
                sizemodel.set("SHcoefficient", shcoeff)
                # read
                KYitem = toFloat(words1[r])
                code = toFloat(words2[r])
                self.setRefine(fit, shcoeff, "K", KYitem, code)

        return index

    def Line36ReadSphericalSizeModel(self, fit, sizemodel, index, shlist):
        """
        Read Line 36 for Size Model of Spherical Harmonics
        (this will substitute the above methods lately)

        Arguement:
        fit             :   Fit instance
        sizemodel       :   SizeModelSpherical instance
        shlist          :   list of spherical harmonic

        Return          --  index, line index
        """
        # 1. line amount
        lineamount = len(shlist)

        # 2. start to read
        for l in xrange(lineamount):

            # increment line number
            index = index + 1

            # init and check
            itemamount = len(shlist[l])
            words1 = self.SplitNewLine(index)
            if len(words1) != itemamount:
                # warning.PCRFormatItemError("3", "35 (3) - Line " + str(index) + " laue: " + laue.Name, str(words1))
                warning.PCRFormatItemError(
                    "3", "35 (3) - Line " + str(index) + " laue: ", str(words1))
            index = index + 1
            words2 = self.SplitNewLine(index)
            if len(words2) != itemamount:
                # warning.PCRFormatItemError("3", "35 (3) - Line " + str(index) + " laue: " + laue.Name, str(words2))
                warning.PCRFormatItemError(
                    "3", "35 (3) - Line " + str(index) + " laue: ", str(words2))

            # read
            for r in xrange(itemamount):

                # init SHcoefficent
                spname = shlist[l][r]
                shcoeff = sizemodel.addSphericalHarmonic(spname)

                # read and write
                KYitem = toFloat(words1[r])
                code = toFloat(words2[r])
                if shcoeff.isKY() == "K":
                    self.setRefine(fit, shcoeff, "K", KYitem, code)
                else:
                    self.setRefine(fit, shcoeff, "Y", KYitem, code)

            # END -- for r in xrange(itemamount):

        return index

    #
    # Read Line 37: Laue

    def Line37ReadLaueClass(self, fit, strainmodel, index, LineItemList):
        """
        Read Line 37 LaueClass:  Strain Model
        """
        # check
        if not isinstance(strainmodel, ContributionModule.StrainModelAnisotropic):
            raise_(NotImplementedError, "Line 37 Incorrect Type: " + strainmodel.__class__.__name__)
        # read
        count = 0
        laue = LaueModule.LaueStrainModel(strainmodel.get("Laueclass"))
        for l in xrange(len(LineItemList)):
            # debug output print "Line Numbe = " + str(len(LineItemList))
            index = index + 1
            words1 = self.SplitNewLine(index)
            if len(words1) != LineItemList[l]:
                warning.PCRFormatItemError(
                    "3", "35 (3) - Line " + str(index) + " laue: " + laue.Name, str(words1))
            index = index + 1
            words2 = self.SplitNewLine(index)
            if len(words2) != LineItemList[l]:
                warning.PCRFormatItemError(
                    "3", "35 (3) - Line " + str(index) + " laue: " + laue.Name, str(words2))
            for r in xrange(LineItemList[l]):
                # init
                hkl = laue.get()
                quartic = ContributionModule.QuarticCoefficient(None, hkl)
                strainmodel.set("QuarticCoefficient", quartic)
                # read
                Sitem = toFloat(words1[r])
                code = toFloat(words2[r])
                self.setRefine(fit, quartic, "S", Sitem, code)

        return index

    #
    # Read Line 43

    def Line43ReadFurth(self, fit, phase, index):
        """
        read Furth lines for user defined parameters
        still use the convention(value, refinecode, name)
        """
        if phase.get("Furth") > 0:
            raise NotImplementedError("This is example for Furth != 0")

        for line in xrange(0, phase.get("Furth")):
            # read
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 3:
                warning.PCRFormatItemError(
                    "3", "Line 43 - " + str(line), str(words))
            namep = words[0]
            valuep = toFloat(words[1])
            codep = toFloat(words[2])
            # setup refine
            raise NotImplementedError("Line 43 is to be setup with all RefineClass")
            codeindex = self.CodeWord(valuep, codep, fit)
            phase.UserDefinedParameterList[line] = (valuep, codeindex, namep)

        return index

    #
    # Read Line 44

    def Line44ReadNvk(self, fit, phase, index):
        """
        read Nvk pairs of 2-lines for PVKX, PVKY, PVKZ 
        indexed as '1', '2', '3'
        """

        for line in xrange(0, abs(phase.get("Nvk"))):

            # init
            pvector = PhaseModule.PropagationVector(None)
            phase.set("PropagationVector", pvector)
            # read
            index = index + 1
            words1 = self.SplitNewLine(index)
            index = index + 1
            words2 = self.SplitNewLine(index)

            pvkx = toFloat(words1[0])
            pvky = toFloat(words1[1])
            pvkz = toFloat(words1[2])

            codex = toFloat(words2[0])
            codey = toFloat(words2[1])
            codez = toFloat(words2[2])

            self.setRefine(fit, pvector, "X", pvkx, codex)
            self.setRefine(fit, pvector, "Y", pvky, codey)
            self.setRefine(fit, pvector, "Z", pvkz, codez)

        return index

    #
    # Read Line 45

    def Line45ReadDis(self, fit, phase, index):
        """
        read Dis Lines of distant constraints
        """
        for line in xrange(0, phase.get("Dis")):
            # init
            soft = PhaseModule.DistanceRestraint(None)
            phase.set("DistanceRestraint", soft)
            # read
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 8:
                warning.PCRFormatItemError(
                    "3", "Line 45 - " + str(line), str(words))
            soft.set("CATOD1", (words[0]))
            soft.set("CATOD2", (words[1]))
            soft.set("ITnum",  int(words[2]))
            soft.set("T1",     toFloat(words[3]))
            soft.set("T2",     toFloat(words[4]))
            soft.set("T3",     toFloat(words[5]))
            soft.set("Dist",   toFloat(words[6]))
            soft.set("Sigma",  toFloat(words[7]))

        return index

    #
    # Read Line 45

    def Line45_1ReadMomAngle(self, fit, phase, index):
        """
        read Dis Lines of distant constraints
        """
        for line in xrange(1, phase.MomAngles+1):
            # init
            soft = PhaseModule.AngleRestraint()
            phase.set("AngleRestraint", soft)
            #
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 13:
                warning.PCRFormatItemError(
                    "3", "Line 45-1 - " + str(line), str(words))
            soft.set("CATOD1", (words[0]))
            soft.set("CATOD2", (words[1]))
            soft.set("CATOD3", (words[2]))
            soft.set("ITnum1", int(words[3]))
            soft.set("ITnum2", int(words[4]))
            soft.set("T1",     toFloat(words[5]))
            soft.set("T2",     toFloat(words[6]))
            soft.set("T3",     toFloat(words[7]))
            soft.set("t1",     toFloat(words[8]))
            soft.set("t2",     toFloat(words[9]))
            soft.set("t3",     toFloat(words[10]))
            soft.set("Angle",  toFloat(words[11]))
            soft.set("Sigma",  toFloat(words[12]))

        return index

    #
    # Read Line 45

    def Line46ReadMomMoment(self, phase, fit, index):
        """
        read Dis Lines of distant constraints
        """
        for line in xrange(1, phase.MomMoment+1):
            # FIXME: no such method definition
            soft = PhaseModule.Phase.SoftMomentContrain()
            index = index + 1
            words = self.SplitNewLine(index)
            if len(words) != 3:
                warning.PCRFormatItemError(
                    "3", "Line 46 - " + str(line), str(words))
            soft.CATOD1 = (words[0])
            soft.Moment = toFloat(words[1])
            soft.Sigma = toFloat(words[2])
            phase.SoftMomentContrainList[line] = soft

        return index

    """     Helping Functions   """

    def setRefine(self, fit, objref, param_name, init_value, refinecode, index=None):
        """
        description:
                    set a parameter (param_name) in an object (objref) with an initial value and refine code 
                    with FullProf standard;
                    the refine code is to be separated into two parts (1) code and (2) deviation;
                    (1) the code is to be formatted accroding to a standard;  
                    (a) if the code doesn't exist in Refine container, then a new Variable will be generated
                    (2) create a Constraint object with the deviation
                    (3) link the Variable and Constraint object

        fit:        fit object reference
        objref:     reference to a Rietveldclass refernece
        param_name: parameter name belonging to objref
        init_value: initial value
        refinecode: FullProf Code
        indedx:     if the objref.param_name is a parameter list, this indicates the location
        """
        # print("read:"+param_name+" value: "+str(init_value)+" CodeWord:"+str(refinecode))
        codeword_tmp = refinecode
        if True:
            # refine
            # understand the code Cx = sign(a)(10p + |a|),
            # the equation = init_value + a*variable; init value of variable = 0

            # 1. get (a) integer code (b) devpart ... dev (c) Code
            codepart = abs(refinecode/10)
            code = int(codepart)
            if toFloat(code) > codepart:
                code = code - 1
            devpart = abs(refinecode)-toFloat(code)*10
            if refinecode < 0:
                devpart = -1*devpart

            # construct a name using the code
            name = "Code"+str(code)          # convention
            variablevalue = 0.0

            # 3. setup constraint formula
            if devpart >= 0:
                refinefunction = "+" + str(devpart)+"*" + name
            else:
                refinefunction = "-" + str(-devpart)+"*" + name

            # 4. Link
            constraint = objref.setConstraint(param_name, refinefunction, codeword_tmp,
                                              value=init_value, damping=None, index=index)
        else:
            objref.set(param_name, init_value, index=index)

        return


"""     External Functions      """


class TimeReversalLookupTable:
    """
    A Lookup Table for Time Reversal Operation
    """

    def __init__(self):
        pass

    def lookUpNS(spacegroup):
        """
        static: use space group to find NS
        """

        if spacegroup == "P 6/m m m":
            return 12
        else:
            raise NotImplementedError(
                "TimeReversalLookupTable lookUpNS cannot find " + spacegroup)

    lookUpNS = staticmethod(lookUpNS)

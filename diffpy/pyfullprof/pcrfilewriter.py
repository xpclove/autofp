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

"""PCR File Writer:
  
    Internal Methods List:
    1. ValidateFitFP(fit)
    2. printLines(Line)
    3. StringOutput(value)
    4. getRefine(objref, param_name)
"""
from __future__ import print_function

from future.utils import raise_
__id__ = "$Id: pcrfilewriter.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.utilfunction import verifyType
from diffpy.pyfullprof.exception import RietError
from diffpy.pyfullprof.pattern import PatternTOF
from diffpy.pyfullprof.pattern import Background
from diffpy.pyfullprof.atom import AtomicDisplacementFactorIsotropic
from diffpy.pyfullprof.contribution import Profile
from diffpy.pyfullprof.contribution import StrainModelAnisotropic
from diffpy.pyfullprof.laue import LaueStrainModel



class RefineCode:
    """
    a simple data structure to hold information for a Constraint data to write to FullProf pcr file
    """
    def __init__(self):
        """
        initialization to define 2 parameters
        """
        self.value = 0.0
        self.code  = 0.0

        return

    def __str__(self):
        """
        customerized output
        """
        rstring  = ""
        rstring += str(self.value) + "   " + str(self.code)

        return rstring

    def getValue(self):
        """
        return value of this FullProf parameter

        return  --  float
        """
        return self.value


    def getCode(self):
        """
        return code of this FullProf parameter

        return  --  float
        """
        return self.code


def pcrFileWriter(fit, filename, userinfo=None, srtype="r"):
    """
    convert a fit object to FullProf pcr file in Multipattern format

    Arguments:
    - fit       :   a fit object
    - filename  :   pcr filename;
    - srtype    :   string, either "r" (Rietveld) or "l" (Lebail)

    Return      :   Boolean
    """
    if userinfo is not None:
        verifyType(userinfo, list)
    else:
        userinfo = []

    validateConstraints(fit)

    Line = {}  # a dictionary for line number

    Line = writeBlock1(fit, Line)

    Line = writeBlock2(fit, Line)
    
    Line = writeBlock3(fit, Line, srtype)

    Line = writeBlock4(fit, Line)

    Line = writeBlock5(fit, Line)

    Line = writeBlock6(fit, Line)

    if isinstance(filename, str):
        printLineToFile(Line, filename, userinfo)
    elif filename is not None:
        raise NotImplementedError("filename is not a string nor None")

    return True


def writeBlock1(fit, Line):
    """
    convert the first part of pcr file

    fit:
    Line:   dictionary 
    """

    # Line 1 and comment chi^2
    Line[1]  = "COMM   %-50s"% (fit.get("Information"))
    Line[1] += "\n! Current global Chi2 (Bragg contrib.) =      %-10s"% (1.0E15)

    # Line 2
    Line[2] = "NPATT  %5s    "% (StringOutput(len(fit.get("Pattern"))))
    # add bank number (1) determine whether the list is necessary  (2) construct the list
    # note:  bank: from 1 --- max. 
    allbanklist = []
    bankcount   = 0
    for p in xrange(len(fit.get("Pattern"))):
        allbanklist.append(0)
    for p in xrange(len(fit.get("Pattern"))):
        pattern = fit.get("Pattern")[p] 
        if isinstance(pattern, PatternTOF):
            bank = pattern.get("Bank")
            if bank > 0:
                allbanklist[p] = 1
                bankcount += 1
    if bankcount > 0:
        for bank in allbanklist:
            Line[2] += "  %-3s"% (StringOutput(bank))
        Line[2] += "   <- Flags for patterns (1:refined, 0: excluded)"

    # Line 3
    Line[3] = "W_PAT "
    for pattern in fit.get("Pattern"):
        Line[3] += StringOutput(pattern.get("W_PAT")) + " "


    return Line


def writeBlock2(fit, Line):

    # Line 4
    commline = "! %-8s %-8s %-8s %-8s %-8s %-8s %-8s" % \
            ("Nph",  "Dum",  "Ias",  "Nre",  "Cry", "Opt",  "Aut")
    if fit.get("Opt"):
        opt = 1
    else:
        opt = 0
    if fit.get("Aut"):
        aut = 1
    else:
        aut = 0
    dataline =  "  %-8s %-8s %-8s %-8s %-8s %-8s %-8s"% \
                (StringOutput(len(fit.get("Phase"))), StringOutput(fit.get("Dum")), 
                 StringOutput(fit.get("Ias")), 
                 StringOutput(fit.get("Nre"))       , StringOutput(fit.get("Cry")), 
                 StringOutput(opt),                   StringOutput(aut))
    Line [4] = commline + "\n" + dataline

    # Line 4n
    #commline = "! Job Npr Nba Nex Nsc Nor Iwg Ilo Res Ste Uni Cor"
    commline = "! %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s"% \
               ("Job", "Npr", "Nba", "Nex", "Nsc", "Nor", "Iwg", "Ilo", "Res", "Ste", "Uni", "Cor")
    Line[4]  += "\n" + commline 
    for pattern in fit.get("Pattern"):
        # prepare:
        lpfactor = pattern.get("LPFactor")
        # determine Nba
        Nba = pattern.get("Nba")
        if Nba == 2:
            Nba = pattern.get("NbaPoint")
        elif Nba == -5:
            Nba = -1*pattern.get("NbaPoint")      
        # print
        nor = pattern.get("Nor")
        if nor != 0 and nor != 1:
            nor = 1
        infoline = "  %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s %-8s"% \
                     (StringOutput(pattern.get("Job")), StringOutput(pattern.get("Npr")), 
                      StringOutput(Nba), \
                      StringOutput(pattern.get("Nex")), StringOutput(pattern.get("Nsc")), \
                      StringOutput(nor)               , StringOutput(pattern.get("Iwg")),  
                      StringOutput(lpfactor.get("Ilo")), \
                      StringOutput(pattern.get("Res")), StringOutput(pattern.get("Ste")), \
                      StringOutput(pattern.get("Uni")), StringOutput(pattern.get("Cor")))
        Line[4] += "\n" + infoline 

    # Line 5
    Line[5] = "! Datafile"
    for pattern in fit.get("Pattern"):
        Line[5] += "\n" + pattern.get("Datafile") 

    # Line 6
    infoline = "! Resolution file"
    dataline = ""
    for pattern in fit.get("Pattern"):
        if pattern.get("Res") != 0:
            dataline += "\n" + pattern.get("Resofile") 
    if dataline != "":
        Line[6] = infoline + dataline

    # Line 7
    commline  = "! %-5s %-5s %-5s %-5s %-5s %-5s" \
                % ("Mat", "Pcr", "Syo", "Rpa", "Sym", "Sho")
    if (fit.get("Sym")==1):
        sym = 1
    else:
        sym = 0
    if fit.get("Sho"):
        sho = 1
    else:
        sho = 0
    infoline  = "  %-5s %-5s %-5s %-5s %-5s %-5s" \
                % (StringOutput(fit.get("Mat")), StringOutput(fit.get("Pcr")), StringOutput(fit.get("Syo")),
                   StringOutput(fit.get("Rpa")), StringOutput(sym)           , StringOutput(sho))
    commlinen = "! %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s" \
                % ("Ipr", "Ppl", "Ioc", "Ls1", "Ls2", "Ls3", "Prf", "Ins", "Hkl", "Fou", "Ana")
    
    Line[7]   = commline + "\n" + infoline + "\n" + commlinen 

    for pattern in fit.get("Pattern"):
        # Hacking
        ls1 = pattern.get("Ls1")
        ls3 = pattern.get("Ls3")
        infoline = "  %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s"% \
                    (StringOutput(pattern.get("Ipr")), StringOutput(pattern.get("Ppl")), 
                     StringOutput(pattern.get("Ioc")),
                     StringOutput(ls1               ), StringOutput(pattern.get("Ls2")), 
                     StringOutput(ls3               ),
                     StringOutput(pattern.get("Prf")), StringOutput(pattern.get("Ins")), 
                     StringOutput(pattern.get("Hkl")),
                     StringOutput(pattern.get("Fou")), StringOutput(pattern.get("Ana")))
        Line[7] += "\n" + infoline 

    # Line 8
    if fit.get("Cry") == 0:
        Line[8] = ""
        indexpattern = 1
        for pattern in fit.get("Pattern"):
            if indexpattern > 1:
                Line[8] += "\n"

            if pattern.get("Uni") == 0:
                # 2theta
                lpfactor = pattern.get("LPFactor")
                commline = "! %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s -> Patt %-5s"% \
                          ("lambda1", "lambda2", "Ratio", "Bkpos", "Wdt", "Cthm", "muR", \
                           "AsymLim", "Rpolarz", int(indexpattern))
                dataline = "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s"% \
                          (StringOutput(pattern.get("Lambda1")), StringOutput(pattern.get("Lambda2")),  
                           StringOutput(pattern.get("Ratio")),  
                           StringOutput(pattern.get("Bkpos"))  , StringOutput(pattern.get("Wdt"))    ,  
                           StringOutput(lpfactor.get("Cthm")) ,  
                           StringOutput(pattern.get("muR"))    , StringOutput(pattern.get("AsymLim")),  
                           StringOutput(lpfactor.get("Rpolarz")))
                Line[8] += commline + "\n" + dataline
            else:
                # TOF and ED
                commline =  "! %-15s %-15s %-15s for Pattern %-4s"\
                            %("Bkpos", "Wdt", "Iabscor", str(indexpattern))
                dataline =  "  %-15s %-15s %-15s"\
                            %(StringOutput(pattern.get("Bkpos")), StringOutput(pattern.get("Wdt")), 
                              StringOutput(pattern.get("Iabscor")))
                Line[8] += commline + "\n" + dataline

            indexpattern += 1
        """ end for pattern """

    # Line 9
    commline =  "! %-5s %-15s %-15s %-15s %-15s %-15s"\
                %("NCY", "Eps", "R_at", "R_an", "R_pr", "R_gl")
    infoline =  "  %-5s %-15s %-15s %-15s %-15s %-15s"\
                %(StringOutput(fit.get("NCY")) , StringOutput(fit.get("Eps")) , StringOutput(fit.get("R_at")),
                  StringOutput(fit.get("R_an")), StringOutput(fit.get("R_pr")), StringOutput(fit.get("R_gl")))
    Line[9] =   commline + "\n" + infoline + "\n"
    patternindex = 1
    for pattern in fit.get("Pattern"):
        # prepare
        commline = ""
        if patternindex > 1:
            commline += "\n"
        # output
        if pattern.get("Uni") == 0:
            # 2theta
            commline +=  "! %-15s %-15s %-15s %-15s %-15s -> Patt # %-5s" \
                        %("Thmin", "Step", "Thmax", "PSD", "Sent0", str(patternindex))
            infoline =  "  %-15s %-15s %-15s %-15s %-15s" \
                        %(StringOutput(pattern.get("Thmin")), StringOutput(pattern.get("Step")), 
                          StringOutput(pattern.get("Thmax")),
                          StringOutput(pattern.get("PSD"))  , StringOutput(pattern.get("Sent0"))) 

        elif pattern.get("Uni") == 1:
            # TOF
            commline +=  "! %-15s %-15s %-15s PSD Sent0 -> Patt # %-5s" \
                        %("Thmin", "<Step>", "TOF-max", str(patternindex))
            infoline =  "  %-15s %-15s %-15s" \
                        %(StringOutput(pattern.get("Thmin")), StringOutput(pattern.get("Step")), 
                          StringOutput(pattern.get("Thmax")))

        elif pattern.get("Uni") == 2:
            # ED
            commline +=  "! Emin <Step> Emax -> Patt #N"
            infoline =  StringOutput(pattern.get("Thmin")) + " " + StringOutput(pattern.get("Step")) + \
                        " " + StringOutput(pattern.get("Thmax"))
        else:
            raise NotImplementedError("Line 9 Uni Error")
        
        Line[9] += commline + "\n" + infoline
        # advance
        patternindex += 1
    """ end - for pattern in fit.get() """

    # Line 10 and Line 11 should be grouped with number "10"
    Line[10] = ""
    patternindex = 1
    for pattern in fit.get("Pattern"):

        # Line 10
        if pattern.get("Nba") < -4 or pattern.get("Nba") >= 2:
            # instruction line (comment line)
            commline   = "!  2Theta/TOF/E(Kev) Background for Pattern # %-5s"% (patternindex)
            if Line[10] != "":
                commline = "\n"+commline
            Line[10]  += commline
            # data line
            background = pattern.get("Background")
            poslist  = background.get("POS")
            bcklist  = background.get("BCK")
            i = 0
            for pos, bck in zip(poslist, bcklist):
                bkgdpt   = getRefine(background, "BCK", i)
                dataline = "%-5s %-15s %-15s %-15s"% \
                           ("", StringOutput(pos), StringOutput(bkgdpt.value), StringOutput(bkgdpt.code))
                Line[10] += "\n"+dataline
                i += 1
            # flag
        
        # Line 11:  excluded region
        # 11.1 get list
        regionlist = pattern.get("ExcludedRegion")
        # 11.2 comment line
        if len(regionlist) > 0:
            commline  = "! Excluded regions (LowT, HighT) for Pattern # %-5s"%(patternindex)
            if Line[10] != "":
                commline = "\n" + commline
            Line[10] += commline
        # read regions
        for region in regionlist:
            dataline  =  "%-5s %-15s %-15s"%("", StringOutput(region.get("begin")), StringOutput(region.get("end")))
            Line[10] += "\n"+dataline
        
        # count increment
        patternindex += 1
 
    # End -- for pattern in fit.get("Pattern"):
 
    if Line[10] == "":
        del Line[10]

    # Line 12
    Line[12] = ""
    for pattern in fit.get("Pattern"):
        for scatter in pattern.get("ScatterFactor"):
            # scatter factor
            formfactor = scatter.get("FormFactor")
            commline  = "! Additional scattering factor for Pattern #N"
            dataline1 = "  %-15s %-15s %-15s %-15s"% \
                        (StringOutput(scatter.get("NAM")) , StringOutput(scatter.get("DFP")),
                         StringOutput(scatter.get("DFPP")), StringOutput(scatter.get("ITY")))
                        
            dataline2 = ""
            # formfactor
            if pattern.get("Nsc") > 0:

                if (pattern.get("Job") == 0 or pattern.get("Job") == 2) and scatter.get("ITY") == 0:
                    # 2theta
                    dataline2 += "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s "% \
                                 (StringOutput(formfactor.get("A1")), StringOutput(formfactor.get("B1")),
                                  StringOutput(formfactor.get("A2")), StringOutput(formfactor.get("B2")),
                                  StringOutput(formfactor.get("A3")), StringOutput(formfactor.get("B3")),
                                  StringOutput(formfactor.get("A4")), StringOutput(formfactor.get("B4")),
                                  StringOutput(formfactor.get("C")))

                elif (pattern.get("Job") == 1 or pattern.get("Job") == 3) and scatter.get("ITY") == 1:
                    # TOF
                    dataline2 += "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s "% \
                                 (StringOutput(formfactor.get("A")), StringOutput(formfactor.get("a")), 
                                  StringOutput(formfactor.get("B")), StringOutput(formfactor.get("b")),
                                  StringOutput(formfactor.get("C")), StringOutput(formfactor.get("c")),
                                  StringOutput(formfactor.get("D")))

            elif pattern.get("Nsc") < 0:

                if ((pattern.get("Job") == 0 or pattern.get("Job") == 2) and scatter.get("ITY") == 1) or \
                    ((pattern.get("Job") == 1 or pattern.get("Job") == 3) and scatter.get("ITY") == 0):
                    tablelist = formfactor.get("FormfactorUserdefined")
                    for table in tablelist:
                        dataline2 += StringOutput(table.get("A")) + " " + StringOutput(table.get("a")) + "\n"
                    dataline2 += "-100"
            # chain
            Line[12] += commline + "\n" + dataline1 + "\n" + dataline2 + "\n"

    if Line[12] == "":
        del Line[12]


    # Line 13
    _dbline13 = False
    refine = fit.get("Refine")
    variablelist = refine.get("Variable")
    param_listnum=refine.constraints
    Maxs=0
    for param_tmp in param_listnum:
        if abs(param_tmp.codeWord)>1E-9:
            Maxs+=1
    #Maxs = len(variablelist)
    Line[13] = "  %-5s ! Number of refined parameters"%(StringOutput(Maxs))
    if _dbline13:
        dbgmsg  = "\n--------  Print Line 13  --------------"
        dbgmsg += refine.simpleInformation()
        dbgmsg += "---------- End Line 13 -----------------\n"
        print(dbgmsg)

    # Line 14-17
    if fit.get("Cry") == 0:
        Line[14] = ""
        patternindex = 1
        for pattern in fit.get("Pattern"):

            if patternindex > 1:
                Line[14] += "\n"

            if pattern.get("Uni") == 0:

                # microabsorption
                micabslist = pattern.get("MicroAbsorption")
                if len(micabslist) == 1:
                    more = True
                elif len(micabslist) > 1:
                    errmsg = "pcrfilewrite() @ Line 15:  Not Allowed Number of MicroAbsorption = %-10s"% (len(micabslist))
                    raise RietError(errmsg)
                else:
                    more = False   
                if more:
                    intmore = 1
                else:
                    intmore = 0

                # Line 14
                commline = "! %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-5s -> Patt # %-5s"\
                            %("Zero", "Code", "Sycos", "Code", "Sysin", "Code", "Lambda", "Code", "More", \
                              str(patternindex))
                zero   = getRefine(pattern, "Zero")
                Sycos  = getRefine(pattern, "Sycos")
                Sysin  = getRefine(pattern, "Sysin")
                Lambda = getRefine(pattern, "Lambda")
                dataline =  "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s"% \
                            (StringOutput(zero.value),  StringOutput(zero.code), \
                            StringOutput(Sycos.value),  StringOutput(Sycos.code), 
                            StringOutput(Sysin.value),  StringOutput(Sysin.code), \
                            StringOutput(Lambda.value), StringOutput(Lambda.code), 
                            StringOutput(intmore))
                Line[14] += commline + "\n" + dataline 
                
                # Line 15
                if more:
                    micabs = micabslist[0]
                    commline = "! %-15s %-15s %-15s %-15s %-15s %-15s"% \
                               ("P0", "Cod_P0", "Cp", "Cod_Cp", "Tau", "Cod_Tau")
                    p0  = getRefine(micabs, "P0")
                    cp  = getRefine(micabs, "CP")
                    tau = getRefine(micabs, "TAU")
                    dataline = "  %-15s %-15s %-15s %-15s %-15s %-15s"% \
                               (StringOutput(p0.value), StringOutput(p0.code)  , StringOutput(cp.value), 
                                StringOutput(cp.code) , StringOutput(tau.value), StringOutput(tau.code))
                    Line[14] += "\n" + commline + "\n" + dataline

            elif pattern.get("Uni") == 1:
                # Line 14
                commline =  "! %-15s %-15s %-15s %-15s %-15s %-15s %-15s -> Patt #%-5s"% \
                            ("Zero", "code", "Dtt1", "Code", "Dtt2", "Code", "2SinTh", str(patternindex))
                zero = getRefine(pattern, "Zero")
                dtt1 = getRefine(pattern, "Dtt1")
                dtt2 = getRefine(pattern, "Dtt2")
                dataline =  "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s"% \
                             (StringOutput(zero.value), StringOutput(zero.code),
                              StringOutput(dtt1.value), StringOutput(dtt1.code), 
                              StringOutput(dtt2.value), StringOutput(dtt2.code),
                              StringOutput(pattern.get("TwoSinTh"))) 
                Line[14] += commline + "\n" + dataline

                # Line 16
                if pattern.get("Npr") == 10:
                    commline = "! %-15s %-15s %-15s %-15s %-15s"% \
                               ("Zerot/Code", "Dtt1t/Code", "Dtt2t/Code", "x-cross/Code", "Width/Code")
                    zerot  = getRefine(pattern, "Zerot")
                    dtt1t  = getRefine(pattern, "Dtt1t")
                    dtt2t  = getRefine(pattern, "Dtt2t")
                    xcross = getRefine(pattern, "xcross")
                    width  = getRefine(pattern, "Width")
                    dataline = "  %-15s %-15s %-15s %-15s %-15s"% \
                               (StringOutput(zerot.value),  StringOutput(dtt1t.value) ,
                                StringOutput(dtt2t.value),  StringOutput(xcross.value),
                                StringOutput(width.value))  
                    codeline = "  %-15s %-15s %-15s %-15s %-15s"% \
                               (StringOutput(zerot.code), StringOutput(dtt1t.code),
                                StringOutput(dtt2t.code), StringOutput(xcross.code),
                                StringOutput(width.code))
                    Line[14] += "\n" + commline + "\n" + dataline+"\n"+codeline

            elif pattern.get("Uni") == 2:
                commline = "! Zero Code StE1 Code StE2 Code 2SinTh -> Patt #N"
                zero  = getRefine(pattern, "Zero")
                ste1  = getRefine(pattern, "StE1")
                ste2  = getRefine(pattern, "StE2")
                dataline =  StringOutput(zero.value) + " " + StringOutput(zero.code) + \
                            " " + StringOutput(ste1.value) + " " + StringOutput(ste1.code) + " " + \
                            StringOutput(ste2.value) + " " + StringOutput(ste2.code) 
                Line[14] += commline + "\n" + dataline

            else:
                raise NotImplementedError("Line14-17: Uni not defined")

            # Line 17
            Nba = pattern.get("Nba")
            if Nba == -3 or Nba == -4:

                background = pattern.get("Background")
                # 1-6
                commline = "! Background coefficients/codes for Pattern # %-5s"%(int(patternindex))
                Line[14] += "\n"+commline
                dataline = "  "
                codeline = "  "
                for i in xrange(1, 6+1):
                    param_name = "BACK"
                    backpos    = getRefine(background, param_name, i-1)
                    dataline += "%-15s "% (StringOutput(backpos.value))
                    codeline += "%-15s "% (StringOutput(backpos.code))
                Line[14] += "\n" + dataline
                Line[14] += "\n" + codeline
                # 7-12
                dataline = "  "
                codeline = "  "
                for i in xrange(7, 12+1):
                    param_name = "BACK"
                    backpos    = getRefine(background, param_name, i-1)
                    dataline += "%-15s "% (StringOutput(backpos.value))
                    codeline += "%-15s "% (StringOutput(backpos.code))
                Line[14] += "\n" + dataline
                Line[14] += "\n" + codeline

            elif Nba == -2:

                background = pattern.get("Background")
                dataline = StringOutput(background.get("FWINDOW"))
                commline = "! Window ofr Fourier Filter for Pattern # %-5s"% (patternindex)
                Line[14] += "\n" + dataline + "\n" + commline

            elif Nba == -1:

                background = pattern.get("Background")
                # BACK 1-6
                dataline = ""
                codeline = ""
                for i in xrange(1, 6+1):
                    param_name = "BACK"+StringOutput(i)
                    bkgd       = getRefine(background, param_name)
                    dataline  += "%-15s "% (StringOutput(bkgd.value))
                    codeline  += "%-15s "% (StringOutput(bkgd.code))
                Line[14] += "\n" + dataline + "\n" + codeline
                # Bc 1-6
                dataline = ""
                codeline = ""
                for i in xrange(1, 6+1):
                    param_name = "Bc"+StringOutput(i)
                    bkgd       = getRefine(background, param_name)
                    dataline  += "%-15s "% (StringOutput(bkgd.value))
                    codeline  += "%-15s "% (StringOutput(bkgd.code))
                Line[14] += "\n" + dataline + "\n" + codeline
                # D 1-6
                dataline = ""
                codeline = ""
                for i in xrange(1, 6+1):
                    param_name = "D"+StringOutput(i)
                    bkgd       = getRefine(background, param_name)
                    dataline  += "%-15s "% (StringOutput(bkgd.value))
                    codeline  += "%-15s "% (StringOutput(bkgd.code))
                Line[14] += "\n" + dataline + "\n" + codeline

                commline = "! Additional Background coefficients/Codes for Pattern # %-5s"% \
                    (patternindex)
                Line[14] += "\n" + commline

            elif Nba == 0:

                background = pattern.get("Background")
                if not isinstance(background, Background):
                    raise NotImplementedError("Nba == 0, not get a background")
                # BACK 1-6
                commline = "! Background coefficients/Codes for Pattern # %-5s"% (patternindex)
                dataline = "  "
                codeline = "  "
                for i in xrange(1, 6+1):
                    param_name = "BACK"
                    bkgd       = getRefine(background, param_name, i-1)
                    dataline  += "%-15s "% (StringOutput(bkgd.value))
                    codeline  += "%-15s "% (StringOutput(bkgd.code))
                Line[14] += "\n" + commline + "\n" + dataline + "\n" + codeline
                
            elif Nba == 1:

                background = pattern.get("Background")
                # BACK 1-4
                dataline = ""
                codeline = ""
                for i in xrange(1, 4+1):
                    param_name = "BACK"
                    bkgd       = getRefine(background, param_name, i-1)
                    dataline  += StringOutput(bkgd.value) + " "
                    codeline  += StringOutput(bkgd.code)  + " "
                Line[14] += "\n" + dataline + "\n" + codeline

                commline = "! Background Trans_coefficients/Codes for Pattern #N"
                Line[14] += "\n" + commline

            patternindex += 1
        """ end -- for pattern in fit.get() """

    return Line


def writeBlock3(fit, Line, srtype="r"):
    """
    write Phase-loop Line 18-46 to Line
    

    Arguments:
    - fit   :   fit object
    - Line  :   dictionary for line
    - srtype:   string, refinement type, "r" (Rietveld) or "l" (Lebail)
    """
    
    # initialization
    for line in xrange(18, 46+1):
        Line[line] = {}
    count = 1

    # phase loop 
    for phase in fit.get("Phase"):

        # Line 18
        Line[18][count] = StringOutput(phase.get("Name"))

        # Line 19
        commline =  "! %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-15s %-5s %-5s"% \
                    ("Nat", "Dis", "Ang", "Jbt", "Isy", "Str", "Furth", "ATZ", "Nvk", "More")
        if srtype == "r":
            Nat = len(phase.get("Atom"))
        elif srtype == "l":
            Nat = 0
        else:
            errmsg = "Block 3, Structure Solution Type (srtype) = %-5s Unrecognized (either r or l)"% \
                (srtype)
            raise RietError(errmsg)
        str_more = 0
        if phase.get("More"):
            str_more = 1
        dataline =  "  %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-15s %-5s %-5s"% \
                     (StringOutput(Nat)               , StringOutput(phase.get("Dis")), 
                      StringOutput(phase.get("MomMA")),
                      StringOutput(phase.get("Jbt"))  , StringOutput(phase.get("Isy")), 
                      StringOutput(phase.get("Str"))  ,
                      StringOutput(phase.get("Furth")), StringOutput(phase.get("ATZ")), 
                      StringOutput(phase.get("Nvk"))  , StringOutput(str_more))
        #dataline =  "  %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s"\ 
        Line[19][count] = commline + "\n" + dataline

        # Line 19-1
        if phase.get("More"):
            mom = 0
            ter = 0
            hel = phase.get("Hel")
            if hel:
                hel = 1
            else:
                hel = 0
            sol = phase.get("Sol")
            if sol:
                sol = 1
            else:
                sol = 0

            commline =  "! %-5s %-5s %-5s %-5s %-5s %-5s"% ("Jvi", "Jdi", "Hel", "Sol", "Mom", "Ter")
            dataline =  "  %-5s %-5s %-5s %-5s %-5s %-5s"% \
                         (StringOutput(phase.get("Jvi")), StringOutput(phase.get("Jdi")), StringOutput(hel),
                          StringOutput(sol             ), StringOutput(mom)             , StringOutput(ter))
            Line[19][count] += "\n" + commline + "\n" + dataline

        # Line 19-2
        commline = "! Contribution (0/1) of this phase to the #N pattern"
        dataline = ""
        for pattern in fit.get("Pattern"):
            if fit.getContribution(pattern, phase) is not None:
                dataline += "1 "
            else:
                dataline += "0 "
        Line[19][count] += "\n" + commline + "\n" + dataline

        patternindex = 1
        for pattern in fit.get("Pattern"):
            # setup
            contribution = fit.getContribution(pattern, phase)

            if contribution is not None:
                # Line 19-3
                commline =  "! %-5s %-5s %-5s %-5s %-5s     for pattern # %-5s"% \
                           ("Irf", "Npr", "Jtyp", "Nsp_Ref", "Ph_Shift", str(patternindex))
                dataline =  "  %-5s %-5s %-5s %-5s %-5s"% \
                           (StringOutput(contribution.get("Irf")) , StringOutput(contribution.get("Npr"))    ,
                            StringOutput(contribution.get("Jtyp")), StringOutput(contribution.get("Nsp_Ref")),
                            StringOutput(contribution.get("Ph_Shift")))
                Line[19][count] += "\n" + commline + "\n" + dataline

                # Line19-4
                prvector = getPreferredOrientationVector(contribution)
                pr1      = prvector[0]
                pr2      = prvector[1]
                pr3      = prvector[2]
                commline = "! %-15s %-15s %-15s %-15s %-15s %-15s %-15s    for Pattern # %-5s"% \
                           ("Pr1", "Pr2", "Pr3", "Brind", "Rmua", "Rmub", "Rmuc", str(patternindex))
                dataline = "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s"% \
                           (StringOutput(pr1),                       StringOutput(pr2),                      
                            StringOutput(pr3),  
                            StringOutput(contribution.get("Brind")), StringOutput(contribution.get("Rmua")), 
                            StringOutput(contribution.get("Rmub")) , StringOutput(contribution.get("Rmuc")))
                Line[19][count] += "\n" + commline + "\n" + dataline

                # To implement in Future
                if contribution.get("Irf") == 4:
                    errmsg = "pcrFileWriter() @ Line 19: Irf == 4 is not supported by pcrfilewriter.py"
                    raise RietError(errmsg)
            
            patternindex += 1
        # --- end for pattern  in fit.get("Pattern") .. 

        Jdi = phase.get("Jdi")
        if Jdi == 3 or Jdi == 4:
            # Line 20
            commline = "! %-15s %-15s %-15s"% ("Max_dst(dist)", "(angles)", "Bond-Valence Calc.")
            dataline = "  %-15s %-15s %-15s"% \
                       (StringOutput(phase.get("Dis_max")), StringOutput(phase.get("Ang_max")),
                        StringOutput(phase.get("BVS")))
            Line[20][count] = commline +"\n" + dataline

            # Line 21 Suite
            # 1. geneate a list for cation's and a list for anion's
            cationdict = {}
            aniondict  = {}
            atomslist = phase.get("Atom")
            for atomindex in xrange(Nat):
                atom = atomslist[atomindex]
                elecnumber = atom.get("IonNumber")
                symbol     = atom.get("Typ")
                if elecnumber > 0 :
                    # cation
                    if symbol in cationdict:
                        # check only purpse
                        if cationdict[symbol] != elecnumber:
                            errmsg = "method writePCRFile Line 21, same atom has inconsistent electron number"
                            raise RietError(errmsg)
                    elif symbol in aniondict:
                        errmsg = "method writePCRFile Line 21, same atom has inconsistent electron number"
                        raise RietError(errmsg)
                    else:
                        cationdict[symbol] = elecnumber
                elif elecnumber < 0:
                    # anion
                    if symbol in aniondict:
                        # check only purpse
                        if aniondict[symbol] != elecnumber:
                            errmsg = "method writePCRFile Line 21, same atom has inconsistent electron number"
                            raise RietError(errmsg)
                    elif symbol in cationdict:
                        # check only purpse
                        errmsg = "method writePCRFile Line 21, same atom has inconsistent electron number"
                        raise RietError(errmsg)
                    else:
                        aniondict[symbol] = elecnumber
                    
            if phase.get("BVS") == "BVS":
                # Line 21
                commline = "! %-15s %-15s %-15s /Name cations /Name Anions" % \
                           ("N_cations",  "N_anions",  "Tolerance(\%)") 
                dataline = "  %-15s %-15s %-15s"% \
                           (StringOutput(len(cationdict.keys())), StringOutput(len(aniondict.keys())), 
                            StringOutput(phase.get("Tolerance")))
                Line[21][count] = commline + "\n" + dataline
                # Line 21-1: Cation
                dataline = ""
                for symbol in cationdict.keys():
                    cation = symbol+"+"+str(cationdict[symbol])
                    dataline += "%-15s "% (cation)
                if dataline != "":
                    Line[21][count] += "\n" + "   " + dataline 

                # Line 21-2: Anion
                dataline = ""
                for symbol in aniondict.keys():
                    anion = symbol+str(aniondict[symbol])
                    dataline += "%-15s "% (anion)
                if dataline != "":
                    Line[21][count] += "\n" + "   " + dataline 

        # Line 22
        comment = phase.get("Comment")
        if comment.count("Mag") != 0:
            Line[22][count] = StringOutput(phase.get("Spacegroup")) + "      " + StringOutput(phase.get("Comment"))
        else:
            Line[22][count] = StringOutput(phase.get("Spacegroup")) + "    <-" + StringOutput(phase.get("Comment"))

        # Line 23
        Line[23][count] = ""
        commline = "! Time Reversal Operations on Crystal Space Group"
        dataline = ""
        timereversallist = phase.get("TimeRev")
        if len(timereversallist) == 1:
            timereversal = timereversallist[0]
            for ti in xrange(timereversal.get("NS")+1):
                param_name = "TimeRev"+StringOutput(ti)
                dataline += StringOutput(timereversal.get(param_name)) + " "
            if dataline != "":
                Line[23][count] = commline + "\n" + dataline

        # Line 23b
        Isy = phase.get("Isy")
        Jbt = phase.get("Jbt")
        operatorset = phase.get("OperatorSet")
        if Isy != 0 and Jbt != 15:
            commline =  "! Nsym Cen Laue MagMat"
            dataline =  StringOutput(operatorset.get("Nsym")) + " " + StringOutput(operatorset.get("Cen")) + " " + \
                        StringOutput(operatorset.get("Laue")) + " " + StringOutput(operatorset.get("MagMat"))
            Line[23][count] += commline + "\n" + dataline

        elif Isy != 0 and Jbt == 15:
            commline = "! Nsym Cen Laue DepMat MagMat"
            dataline =  StringOutput(operatorset.get("Nsym")) + " " + StringOutput(operatorset.get("Cen")) + " " + StringOutput(operatorset.get("Laue")) + " " + \
                        StringOutput(operatorset.get("DepMat")) + " " + StringOutput(operatorset.get("MagMat"))
            Line[23][count] += commline + "\n" + dataline

        elif Isy == -2 and (Jbt == 1 or Jbt == -1):
            commline = "! Nsym Cen Laue Ireps N_Bas"
            dataline =  StringOutput(operatorset.get("Nsym")) + " " + StringOutput(operatorset.get("Cen")) + " " + StringOutput(operatorset.get("Laue")) + " " + \
                        StringOutput(operatorset.get("Ipres")) + " " + StringOutput(operatorset.get("N_Bas"))
            Line[23][count] += commline + "\n" + dataline

            # Line 23-1
            commline = "! Real(0)-Imaginary(1) indicator for Ci"
            dataline = ""
            raise NotImplementedError("Line 23-1 not implemented")
            # The following code is temporary design, subject to be developed
            #for icompl in operatorset.get("Icompl"):
            #    dataline += StringOutput(icompl.get("Ireps"))

        if Line[23][count] == "":
            del Line[23][count]

        # Line 24
        Line[24][count] = ""
        if Isy == 1:
            # Nsym x (1+MagMat+DepMat) Lines
            commline =  "!S11 S12 S13     T1        S21 S22 S23     T2    S31 S32 S33       T3\n" + \
                        "!M11 M12 M13  M21 M22 M23  M31 M32 M33     Ph"
            Line[24][count] += commline
            for combo in operatorset.get("OperatorCombo"):
                # SymmetryrMatrix
                dataline = ""
                smatrix = combo.get("SymmetryMatrix")
                for i in xrange(1, 3+1):
                    for j in xrange(1, 3+1):
                        param_name = "S"+StringOutput(i)+StringOutput(j)
                        dataline  += StringOutput(smatrix.get(param_name)) + " "
                    param_name = "T"+StringOutput(i)
                    dataline  += StringOutput(smatrix.get(param_name)) + " "
                Line[24][count] += "\n" + dataline

                # DisplaceMatrix
                for matrix in combo.get("DisplaceMatrix"):
                    dataline = ""
                    for i in xrange(1, 3+1):
                        for j in xrange(1, 3+1):
                            param_name = "R"+StringOutput(i)+StringOutput(j)
                            dataline  += StringOutput(matrix.get(param_name)) + " "
                    dataline += StringOutput(matrix.get("Phase")) 
                    Line[24][count] += "\n" + dataline

                # MagneticMatrix
                for matrix in combo.get("MagneticMatrix"):
                    dataline = ""
                    for i in xrange(1, 3+1):
                        for j in xrange(1, 3+1):
                            param_name = "R"+StringOutput(i)+StringOutput(j)
                            dataline  += StringOutput(matrix.get(param_name)) + " "
                    dataline += StringOutput(matrix.get("Phase")) 
                    Line[24][count] += "\n" + dataline

        elif Isy == -1:
            # Nsym x (1+MagMat+DepMat) Lines
            Line[24][count] += "! Symmetry Operators"
            for combo in operatorset.get("OperatorCombo"):
                dataline = ""
                # SymmetryMatrix
                smatrix = combo.get("SymmetryMatrix")
                dataline = "SYMM     " + " " + StringOutput(smatrix.get("X")) + " " + StringOutput(smatrix.get("Y")) + " " + \
                            StringOutput(smatrix.get("Z")) 
                Line[24][count] += "\n" + dataline
                # DisplaceMatrix
                for matrix in combo.get("DisplaceMatrix"):
                    dataline = ""
                    dataline = "DSYM     " + " " + StringOutput(matrix.get("X")) + " " + StringOutput(matrix.get("Y")) + " " + \
                               StringOutput(matrix.get("Z")) + " " + StringOutput(matrix.get("Phase"))
                    Line[24][count] += "\n" + dataline
                # MagneticMatrix
                for matrix in combo.get("MagneticMatrix"):
                    dataline = ""
                    dataline = "MSYM     " + " " + StringOutput(matrix.get("X")) + " " + StringOutput(matrix.get("Y")) + " " + \
                               StringOutput(matrix.get("Z")) + " " + StringOutput(matrix.get("Phase"))
                    Line[24][count] += "\n" + dataline

        elif Isy == -2:
            # basis function
            Line[24][count] += "! Symmetry Operators"
            for combo in operatorset.get("OperatorCombo"):
                # symmetry operator
                smatrix  = combo.get("SymmetryMatrix")
                dataline = "SYMM     " + " " + StringOutput(smatrix.get("X")) + " " + StringOutput(smatrix.get("Y")) + " " + \
                            StringOutput(smatrix.get("Z")) 
                Line[24][count] += "\n" + dataline
                # basis function
                if operatorset.get("Ireps") == 1:
                    dataliner = "BASR   "
                    for bf in combo.get("BasisFunction"):
                        dataliner += StringOutput(bf.get("R1")) + " " + StringOutput(bf.get("R2")) + " " + StringOutput(bf.get("R3"))  
                    Line[24][count] += dataliner
                if operatorset.get("Ireps") == -1:
                    dataliner = "BASR   "
                    datalinei = "BASI   "
                    for bf in combo.get("BasisFunction"):
                        dataliner += StringOutput(bf.get("R1")) + " " + StringOutput(bf.get("R2")) + " " + StringOutput(bf.get("R3"))  
                        datalinei += StringOutput(bf.get("I1")) + " " + StringOutput(bf.get("I2")) + " " + StringOutput(bf.get("I3"))  
                    Line[24][count] += dataliner
                    Line[24][count] += datalinei
        
        else:
            pass

        if Line[24][count] == "":
            del Line[24][count]
       
        # Line 25 Atom Suite
        Jbt = phase.get("Jbt")
        Isy = phase.get("Isy")

        # bug to fix
        if Jbt == 4:
            print("Jbt == 4 is not supported yet")
            return Line


        Line[25][count] = ""
        if Jbt == 0:
            commline =  "! %-8s %-8s %-15s %-15s %-15s %-15s %-15s %-5s %-5s %-5s %-15s"\
                        %("Atom", "Typ", "X", "Y", "Z", "Biso", "Occ", "In", "Fin", "N_t", "Spc/Codes")
            Line[25][count] += commline
            atomslist = phase.get("Atom")
            for atomindex in xrange(Nat):
                atom = atomslist[atomindex]
                dfactor  = atom.get("AtomicDisplacementFactor")
                # 25-1 25-2
                x = getRefine(atom, "X")
                y = getRefine(atom, "Y")
                z = getRefine(atom, "Z")
                b = RefineCode()
                if isinstance(dfactor, AtomicDisplacementFactorIsotropic):
                    b = getRefine(dfactor, "Biso")
                else:
                    b.value = 0.0
                    b.code  = 0
                o = getRefine(atom, "Occ")
                dataline =  "  %-8s %-8s %-15s %-15s %-15s %-15s %-15s %-5s %-5s %-5s %-5s"% \
                             (StringOutput(atom.get("Name")), StringOutput(atom.get("Typ")), StringOutput(x.value),
                              StringOutput(y.value)         , StringOutput(z.value)        , StringOutput(b.value),
                              StringOutput(o.value)         , StringOutput(atom.get("In")) , StringOutput(atom.get("Fin")),
                              StringOutput(atom.get("N_t")) , StringOutput(atom.get("Spc")))
                codeline =  "  %-8s %-8s %-15s %-15s %-15s %-15s %-15s %-5s %-5s %-5s %-5s"% \
                             (""                  , ""                  , StringOutput(x.code),
                              StringOutput(y.code), StringOutput(z.code), StringOutput(b.code),
                              StringOutput(o.code), ""                  , "",
                              ""                  , "")
                Line[25][count] += "\n" + dataline + "\n" + codeline

                # Line 25-3 25-4 25-5 25-6
                if atom.get("N_t") == 2:
                    commline = "! %-17s %-15s %-15s %-15s %-15s %-15s %-15s \ Codes"% \
                               ("", "beta11", "beta22", "beta33", "beta12", "beta13", "beta23")
                    b11 = getRefine(dfactor, "B11") 
                    b22 = getRefine(dfactor, "B22") 
                    b33 = getRefine(dfactor, "B33") 
                    b12 = getRefine(dfactor, "B12") 
                    b13 = getRefine(dfactor, "B13") 
                    b23 = getRefine(dfactor, "B23") 
                    dataline = "  %-17s %-15s %-15s %-15s %-15s %-15s %-15s"% \
                               ("",
                                StringOutput(b11.value), StringOutput(b22.value), StringOutput(b33.value),
                                StringOutput(b12.value), StringOutput(b13.value), StringOutput(b23.value))
                    codeline = "  %-17s %-15s %-15s %-15s %-15s %-15s %-15s"% \
                               ("",
                                StringOutput(b11.code), StringOutput(b22.code), StringOutput(b33.code),
                                StringOutput(b12.code), StringOutput(b13.code), StringOutput(b23.code))
                    Line[25][count] += "\n" + commline + "\n" + dataline + "\n" + codeline

                elif atom.get("N_t") == 4:
                    commline = "! Form-factor refinable parameters"
                    f = {}
                    for i in xrange(1, 14+1):
                        param_name = "f"+StringOutput(i)
                        f[i] = getRefine(dfactor, param_name)
                    dataline = ""
                    codeline = ""
                    for i in xrange(1, 7+1):
                        dataline += StringOutput(f[i].value) + " "
                        codeline += StringOutput(f[i].code)  + " "
                    Line[25][count] += commline + "\n" + dataline + "\n" + codeline
                    for i in xrange(8, 14+1):
                        dataline += StringOutput(f[i].value) + " "
                        codeline += StringOutput(f[i].code)  + " "
                    Line[25][count] += "\n" + dataline + "\n" + codeline

                # Line 25-7 25-8
                if atom.get("Typ") == "SASH":
                    raise NotImplementedError("Line 25-7 25-8 Not Implemented")

        elif Jbt == 4 or Jbt == -4:
            commline =  "!Atom Typ      p1       p2       p3      p4     p5      p6     p7     p8"
            Line[25][count] += commline
            atomslist = phase.get("Atom")
            for atomindex in xrange(Nat):
                atom = atomslist[atomindex]
                # rigid body
                P = {}
                for i in xrange(1, 8+1):
                    param_name = "P"+StringOutput(i)
                    P[i] = getRefine(atom, param_name)
                # Line 25-1 25-2
                dataline = StringOutput(atom.get("Name")) + " " + StringOutput(atom.get("Typ")) + " " 
                codeline = ""
                for i in xrange(1, 8+1):
                    dataline += StringOutput(P[i].value) + " " 
                    codeline += StringOutput(P[i].code)  + " "
                Line[25][count] += commline + "\n" + dataline + "\n" + codeline 
                # Line 25-3 25-4
                commline = "P9, P10, P11, P12, P13, P14, P15"
                dataline = ""
                codeline = ""
                for i in xrange(9, 15+1):
                    dataline += StringOutput(P[i].value) + " " 
                    codeline += StringOutput(P[i].code)  + " "
                Line[25][count] += "\n" + dataline + "\n" + codeline 

                if Jbt == 4:
                    print("Jbt == 4:  not implemented pcrfilewriter.py")
                    return Line

        elif Jbt == 1:
                # magnetic
            commline = "!Atom Typ  Mag Vek    X      Y      Z       Biso   Occ      Rx    Ry    Rz"
            Line[25][count] += commline
            atomslist = phase.get("Atom")
            for atomindex in xrange(Nat):
                atom = atomslist[atomindex]
                x = getRefine(atom, "X")
                y = getRefine(atom, "Y")
                z = getRefine(atom, "Z")
                b = getRefine(atom, "Biso")
                o = getRefine(atom, "Occ")
                magmoment = atom.get("MagneticMoment")
                rx = getRefine(magmoment, "RX")
                ry = getRefine(magmoment, "RY")
                rz = getRefine(magmoment, "RZ")
                ix = getRefine(magmoment, "IX")
                iy = getRefine(magmoment, "IY")
                iz = getRefine(magmoment, "IZ")
                b11 = getRefine(atom, "B11")
                b22 = getRefine(atom, "B22")
                b33 = getRefine(atom, "B33")
                mph = getRefine(atom, "MagPh")
                # 25-1 25-2
                dataline =  StringOutput(atom.get("Name")) + " " + StringOutput(atom.get("Typ")) + " " + StringOutput(atom.get("Mag")) + " " + \
                            StringOutput(atom.get("Vek")) + " " + StringOutput(x.value) + " " + StringOutput(y.value) + " " + \
                            StringOutput(z.value) + " " + \
                            StringOutput(b.value) + " " + StringOutput(o.value) + " " + StringOutput(rx.value) + " " + StringOutput(ry.value) + " " + \
                            StringOutput(rz.value)
                codeline =  StringOutput(x.code) + " " + StringOutput(y.code) + " " + StringOutput(z.code) + " " + StringOutput(b.code) + " " + \
                            StringOutput(o.code) + " " + StringOutput(rx.code) + " " + StringOutput(ry.code) + " " + StringOutput(rz.code)
                Line[25][count] += "\n" + dataline + "\n" + codeline
                # 25-3 25-4
                commline = "! IX, IY, IZ, B11, B22, B33, MagPh"
                dataline =  StringOutput(ix.value) + " " + StringOutput(iy.value) + " " + StringOutput(iz.value) + " " + \
                            StringOutput(b11.value) + " " + StringOutput(b22.value) + " " + StringOutput(b33.value) + " " + StringOutput(mph.value)
                codeline =  StringOutput(ix.code) + " " + StringOutput(iy.code) + " " + StringOutput(iz.code) + " " + \
                            StringOutput(b11.code) + " " + StringOutput(b22.code) + " " + StringOutput(b33.code) + " " + StringOutput(mph.code)
                Line[25][count] += "\n" + commline + "\n" + dataline + "\n" + codeline

        elif Jbt == -1 and Isy != -2:
            # magnetic
            commline  = "!Atom Typ  Mag Vek    X      Y      Z       Biso   Occ      Rm Rphi Rthet"
            commline2 = "!Im, Iphi, Ithet, B11, B22, B33, MagPh"
            Line[25][count] += commline + "\n" + commline2
            atomslist = phase.get("Atom")
            for atomindex in xrange(Nat):
                atom = atomslist[atomindex]
                x = getRefine(atom, "X")
                y = getRefine(atom, "Y")
                z = getRefine(atom, "Z")
                b = getRefine(atom, "Biso")
                o = getRefine(atom, "Occ")
                magmoment = atom.get("MagneticMoment")
                rm = getRefine(magmoment, "RM")
                rt = getRefine(magmoment, "Rthet")
                rp = getRefine(magmoment, "Rphi")
                im = getRefine(magmoment, "IM")
                it = getRefine(magmoment, "Ithet")
                ip = getRefine(magmoment, "Iphi")
                b11 = getRefine(atom, "B11")
                b22 = getRefine(atom, "B22")
                b33 = getRefine(atom, "B33")
                mph = getRefine(atom, "MagPh")
                # 25-1 25-2
                dataline =  StringOutput(atom.get("Name")) + " " + StringOutput(atom.get("Typ")) + " " + StringOutput(atom.get("Mag")) + " " + \
                            StringOutput(atom.get("Vek")) + " " + StringOutput(x.value) + " " + StringOutput(y.value) + " " + \
                            StringOutput(z.value) + " " + \
                            StringOutput(b.value) + " " + StringOutput(o.value) + " " + StringOutput(rm.value) + " " + \
                            StringOutput(rp.value) + " " + StringOutput(rt.value)
                codeline =  StringOutput(x.code) + " " + StringOutput(y.code) + " " + StringOutput(z.code) + " " + StringOutput(b.code) + " " + \
                            StringOutput(o.code) + " " + StringOutput(rm.code) + " " + StringOutput(rp.code) + " " + StringOutput(rt.code)
                Line[25][count] += "\n" + dataline + "\n" + codeline
                # 25-3 25-4
                dataline =  StringOutput(im.value) + " " + StringOutput(ip.value) + " " + StringOutput(it.value) + " " + \
                            StringOutput(b11.value) + " " + StringOutput(b22.value) + " " + StringOutput(b33.value) + " " + StringOutput(mph.value)
                codeline =  StringOutput(im.code) + " " + StringOutput(ip.code) + " " + StringOutput(it.code) + " " + \
                            StringOutput(b11.code) + " " + StringOutput(b22.code) + " " + StringOutput(b33.code) + " " + StringOutput(mph.code)
                Line[25][count] += "\n" + dataline + "\n" + codeline

        elif Jbt == -1 and Isy == -2:
            # basis function
            commline  = "! Atom Typ  Mag Vek    X      Y      Z       Biso   Occ      C1      C2      C3"
            commline2 = "! C4, C5, C6, C7, C8, C9, MagPh"
            Line[25][count] += commline + "\n" + commline2
            atomslist = phase.get("Atom")
            for atomindex in xrange(Nat):
                atom = atomslist[atomindex]
                x = getRefine(atom, "X")
                y = getRefine(atom, "Y")
                z = getRefine(atom, "Z")
                b = getRefine(atom, "Biso")
                o = getRefine(atom, "Occ")
                c = {}
                for i in xrange(1, 9+1):
                    param_name = "C"+StringOutput(i)
                    c[i] = getRefine(atom, param_name)
                mph = getRefine(atom, "MagPh")
                # 25-1 25-2
                dataline =  StringOutput(atom.get("Name")) + " " + StringOutput(atom.get("Typ")) + " " + StringOutput(atom.get("Mag")) + " " + \
                            StringOutput(atom.get("Vek")) + " " + StringOutput(x.value) + " " + StringOutput(y.value) + " " + \
                            StringOutput(z.value) + " " + StringOutput(b.value) + " " + StringOutput(o.value) + " " 
                for i in xrange(1, 3+1):
                    dataline += StringOutput(c[i].value) + " "
                codeline =  StringOutput(x.code) + " " + StringOutput(y.code) + " " + StringOutput(z.code) + " " + StringOutput(b.code) + " " + \
                            StringOutput(o.code) + " " 
                for i in xrange(1, 3+1):
                    codeline += StringOutput(c[i].code) + " "
                Line[25][count] += "\n" + dataline + "\n" + codeline
                # 25-3 25-4
                dataline = ""
                codeline = ""
                for i in xrange(4, 9+1):
                    dataline += StringOutput(c[i].value) + " "
                    codeline += StringOutput(c[i].code) + " "
                dataline += StringOutput(mph.value)
                codeline += StringOutput(mph.code)
                Line[25][count] += "\n" + "\n" + dataline + "\n" + codeline

        elif Jbt == 5 or Jbt == -5:
            # conical structure
            commline  = "!Atom Typ  Mag Vek    X      Y      Z       Biso   Occ    Mom   beta  Phase "
            commline2 = "!   Phi & Theta  of Cone-axis + unused params"
            Line[25][count] += commline + "\n" + commline2
            atomslist = phase.get("Atom")
            for atomindex in xrange(Nat):
                atom = atomslist[atomindex]
                p = {}
                for i in xrange(1, 15+1):
                    param_name = "P"+StringOutput(i)
                    p[i] = getRefine(atom, param_name)
                # 25-1 25-2
                dataline =  StringOutput(atom.get("Name")) + " " + StringOutput(atom.get("Typ")) + " " + StringOutput(atom.get("Mag")) + " " + \
                            StringOutput(atom.get("Vek"))  + " "
                codeline = ""
                for i in xrange(1, 8+1):
                    dataline += StringOutput(p[i].value) + " "
                    codeline += StringOutput(p[i].code ) + " "
                Line[25][count] += "\n" + dataline + "\n" + codeline
                # 25-3 25-4
                dataline = ""
                codeline = ""
                for i in xrange(9, 15+1):
                    dataline += StringOutput(p[i].value) + " "
                    codeline += StringOutput(p[i].code ) + " "
                Line[25][count] += "\n" + dataline + "\n" + codeline

        elif Jbt == 10 or Jbt == -10:
            # x-ray/neutron + magnetic neutron scattering
            # 25-1 25-2
            commline = "!Atom Typ Mag Vek X Y Z Biso Occ N_type Spc "
            Line[25][count] += commline
            atomslist = phase.get("Atom")
            for atomindex in xrange(Nat):
                atom = atomslist[atomindex]
                x = getRefine(atom, "X")
                y = getRefine(atom, "Y")
                z = getRefine(atom, "Z")
                b = getRefine(atom, "Biso")
                o = getRefine(atom, "Occ")
                dataline =  StringOutput(atom.get("Name")) + " " + StringOutput(atom.get("Typ")) + " " + StringOutput(atom.get("Mag")) + " " + \
                            StringOutput(atom.get("Vek")) + " " + StringOutput(x.value) + " " + StringOutput(y.value) + " " + StringOutput(z.value) + " " + \
                            StringOutput(b.value) + " " + StringOutput(o.value) + " " + StringOutput(atom.get("N_t")) + " " + StringOutput(atom.get("Spc"))
                codeline =  StringOutput(x.code) + " " + StringOutput(y.code) + " " + StringOutput(z.code) + " " + \
                            StringOutput(b.code) + " " + StringOutput(o.code) 
                Line[25][count] += "\n" + dataline + "\n" + codeline

                # 25-3 25-4
                if (atom.get("N_t") == 1 or atom.get("N_t") == 3) and Isy != -2:

                    magmoment = atom.get("MagneticMoment")
                    rx  = getRefine(magmoment, "RX")
                    ry  = getRefine(magmoment, "RY")
                    rz  = getRefine(magmoment, "RZ")
                    ix  = getRefine(magmoment, "IX")
                    iy  = getRefine(magmoment, "IY")
                    iz  = getRefine(magmoment, "IZ")
                    mph = getRefine(atom, "MagPh")
                    dataline =  StringOutput(rx.value) + " " + StringOutput(ry.value) + " " + StringOutput(rz.value) + " " + \
                                StringOutput(ix.value) + " " + StringOutput(iy.value) + " " + StringOutput(iz.value) + " " + StringOutput(mph.value)
                    codeline =  StringOutput(rx.code) + " " + StringOutput(ry.code) + " " + StringOutput(rz.code) + " " + \
                                StringOutput(ix.code) + " " + StringOutput(iy.code) + " " + StringOutput(iz.code) + " " + StringOutput(mph.code)
                    Line[25][count] += "\n" + dataline + "\n" + codeline

                elif atom.get("N_t") == -1 or atom.get("N_t") == -3:
                   
                    magmoment = atom.get("MagneticMoment")
                    rm = getRefine(magmoment, "RM")
                    rt = getRefine(magmoment, "Rthet")
                    rp = getRefine(magmoment, "Rphi")
                    im = getRefine(magmoment, "IM")
                    it = getRefine(magmoment, "Ithet")
                    ip = getRefine(magmoment, "Iphi")     
                    mph = getRefine(atom, "MagPh")
                    dataline =  StringOutput(rm.value) + " " + StringOutput(rp.value) + " " + StringOutput(rt.value) + " " + \
                                StringOutput(im.value) + " " + StringOutput(ip.value) + " " + StringOutput(it.value) + " " + StringOutput(mph.value)
                    codeline =  StringOutput(rm.code) + " " + StringOutput(rp.code) + " " + StringOutput(rt.code) + " " + \
                                StringOutput(im.code) + " " + StringOutput(ip.code) + " " + StringOutput(it.code) + " " + StringOutput(mph.code)
                    Line[25][count] += "\n" + dataline + "\n" + codeline

                elif (atom.get("N_t") == 1 or atom.get("N_t") == 3) and Isy == -2:

                    c = {}
                    dataline = ""
                    codeline = ""
                    for i in xrange(1, 6+1):
                        param_name = "C"+StringOutput(i)
                        c[i]       = getRefine(atom, param_name)
                        dataline  += StringOutput(c[i].value) + " "
                        codeline  += StringOutput(c[i].code ) + " "
                    mph = getRefine(atom, "MagPh")
                    dataline += StringOutput(mph.value)
                    dataline += StringOutput(mph.code )
                    Line[25][count] += "\n" + dataline + "\n" + codeline

                # Line 25-5 25-6
                N_t = atom.get("N_t")
                if (N_t == 2 or N_t == 3 or N_t == -3) and Isy == -2:
                    atomicfactor = atom.get("AtomicDisplacemenFactor")
                    b11 = getRefine(atomicfactor, "B11")
                    b22 = getRefine(atomicfactor, "B22")
                    b33 = getRefine(atomicfactor, "B33")
                    b12 = getRefine(atomicfactor, "B12")
                    b13 = getRefine(atomicfactor, "B13")
                    b23 = getRefine(atomicfactor, "B23")
                    dataline =  StringOutput(b11.value) + " " + StringOutput(b22.value) + " " + StringOutput(b33.value) + " " + \
                                StringOutput(b12.value) + " " + StringOutput(b13.value) + " " + StringOutput(b23.value)
                    codeline =  StringOutput(b11.code) + " " + StringOutput(b22.code) + " " + StringOutput(b33.code) + " " + \
                                StringOutput(b12.code) + " " + StringOutput(b13.code) + " " + StringOutput(b23.code)
                    Line[25][count] += "\n" + dataline + "\n" + codeline

                # Line 25-7 25-8 25-9 25-10
                if N_t == 4:
                    atomicfactor = atom.get("AtomicDisplacemenFactor")
                    f = {}
                    for i in xrange(1, 14+1):
                        param_name = "f"+StringOutput(i)
                        f[i]       = getRefine(atomicfactor, param_name)
                    # 25-7 25-8
                    dataline = ""
                    codeline = ""
                    for i in xrange(1, 7+1):
                        dataline += StringOutput(f[i].value) + " "
                        codeline += StringOutput(f[i].code ) + " "
                    Line[25][count] += "\n" + dataline + "\n" + codeline
                    # 25-9 25-10
                    dataline = ""
                    codeline = ""
                    for i in xrange(8, 14+1):
                        dataline += StringOutput(f[i].value) + " "
                        codeline += StringOutput(f[i].code ) + " "
                    Line[25][count] += "\n" + dataline + "\n" + codeline

        elif Jbt == 15 or Jbt == -15:
            # xray/nuclear + magnetic (modulated structure)
            errmsg = "Jbt=+/-15 not implemented yet"
            raise_(NotImplementedError, errmsg)

            atomslist = phase.get("Atom")
            for atomindex in xrange(Nat):
                atom = atomslist[atomindex]
                pass

        elif Jbt == 2:
            # Le-Bail
            pass

        else:
            errmsg = "Jbt = %-5s Found No Atom"% (Jbt)
            raise RietError(errmsg)


        # Line 25-11
        if phase.get("Jdi") == 2:
            transf   = phase.get("TransformationMatrixSet")[0]
            infoline = "! Multiple Cell Transformation"
            dataline = ""
            for i in xrange(1, 3+1):
                dataline += "\n"
                for j in xrange(1, 3+1):
                    param_name = "T"+StringOutput(i)+StringOutput(j)
                    dataline  += StringOutput(transf.get(param_name)) + " "
                param_name = "Or_sh"+StringOutput(i)
                dataline += StringOutput(transf.get(param_name))
            Line[25][count] += "\n" + infoline +  dataline

        # Line 26
        if fit.get("Cry") == 0:

            # single crystal
            for pattern in fit.get("Pattern"):

                contribution = fit.getContribution(pattern, phase)
                if contribution is None:
                    continue
                else:
                    if contribution.get("Irf") == 4:
                        print("Single Crystal is not supported.... For debug purpose, return an incomplete Line")
                        return Line
                    # raise NotImplementedError, "Single crystal is not supporrted at this moment"

            # powder

            # index initialization:  patcount is the count for contributions from 1 continuously
            for line in xrange(26, 42+1):
                Line[line][count] = {}
            patcount = 1

            for pattern in fit.get("Pattern"):
                
                contribution = fit.getContribution(pattern, phase)
                if contribution is None:
                    continue
                strainparameter = contribution.get("StrainParameter")

                # Line 26 and 27
                if pattern.get("Uni") == 0:

                    profile = contribution.get("Profile")

                    # Line 26
                    scale  = getRefine(contribution, "Scale")
                    shape1 = getRefine(profile     , "Shape1")
                    bov    = getRefine(contribution, "Bov")
                    str1   = getRefine(strainparameter, "Str1")
                    str2   = getRefine(strainparameter, "Str2")
                    str3   = getRefine(strainparameter, "Str3")
                    # commline = "! Scale        Shape1      Bov     Str1     Str2     Str3    Strain-Model"
                    commline = "! %-15s %-15s %-15s %-15s %-15s %-15s %-15s"%("Scale", "Shape1", "Bov", "Str1", "Str2", "Str3", "StrainModel")
                    dataline = "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s"%(StringOutput(scale.value), StringOutput(shape1.value),\
                                StringOutput(bov.value),  StringOutput(str1.value), StringOutput(str2.value), StringOutput(str3.value),\
                                StringOutput(strainparameter.get("StrainModelSelector")))
                    codeline = "  %-15s %-15s %-15s %-15s %-15s %-15s"%(StringOutput(scale.code), StringOutput(shape1.code), \
                                StringOutput(bov.code), StringOutput(str1.code), StringOutput(str2.code), StringOutput(str3.code))

                    Line[26][count][patcount] = commline + "\n" + dataline + "\n" + codeline

                    # Line 27
                    if contribution.get("Npr") != 11:

                        if not isinstance(profile, Profile):
                            print("profile: " + StringOutput(profile))
                            raise RietError("pcrfilewriter.Line 27")
                        u = getRefine(profile, "U")
                        v = getRefine(profile, "V")
                        w = getRefine(profile, "W")
                        x = getRefine(profile, "X")
                        y = getRefine(profile, "Y")
                        g = getRefine(profile, "GausSiz")
                        l = getRefine(profile, "LorSiz")
                        commline = "! %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s"%\
                                  ("U", "V", "W", "X", "Y", "GauSiz", "LorSiz", "Size-Model") 
                        dataline = "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s"%\
                                  (StringOutput(u.value), StringOutput(v.value), StringOutput(w.value),
                                   StringOutput(x.value), StringOutput(y.value), StringOutput(g.value),
                                   StringOutput(l.value), StringOutput(contribution.get("SizeModelSelector")))
                        codeline = "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s"%\
                                   (StringOutput(u.code), StringOutput(v.code), StringOutput(w.code),
                                    StringOutput(x.code), StringOutput(y.code), StringOutput(g.code),
                                    StringOutput(l.code)) 
                        Line[27][count][patcount] =  commline + "\n" + dataline + "\n" + codeline

                    else:
                        
                        profile = contribution.get("Profile")
                        # 27 27-1
                        u = getRefine(profile, "UL")
                        v = getRefine(profile, "VL")
                        w = getRefine(profile, "WL")
                        x = getRefine(profile, "XL")
                        y = RefineCode()
                        g = getRefine(profile, "GausSiz")
                        l = getRefine(profile, "LorSiz")
                        commline = "! %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-10s" % \
                                ("U1", "V1", "W1", "X1", "Y", "GauSiz", "LorSiz", "Size-Mode")
                        dataline = "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-10s" % \
                                (StringOutput(u.value), StringOutput(v.value), StringOutput(w.value), 
                                        StringOutput(x.value), StringOutput(y.value), StringOutput(g.value), 
                                        StringOutput(l.value), StringOutput(contribution.get("SizeModelSelector")))
                        codeline = "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s" % \
                                (StringOutput(u.code), StringOutput(v.code), StringOutput(w.code), 
                                        StringOutput(x.code), StringOutput(y.code), StringOutput(g.code), 
                                        StringOutput(l.code))
                        Line[27][count][patcount] =  commline + "\n" + dataline + "\n" + codeline
                        # 27-2 27-3
                        u = getRefine(profile, "UR")
                        v = getRefine(profile, "VR")
                        w = getRefine(profile, "WR")
                        e = getRefine(profile, "Eta0r")
                        x = getRefine(profile, "XR")
                        commline = "! %-15s %-15s %-15s %-15s %-15s" % \
                                ("Ur", "Vr", "Wr", "Eta0r", "Xr") 
                        dataline = "  %-15s %-15s %-15s %-15s %-15s" % \
                                (StringOutput(u.value), StringOutput(v.value), StringOutput(w.value), 
                                        StringOutput(e.value), StringOutput(x.value))
                        codeline = "  %-15s %-15s %-15s %-15s %-15s" % \
                                (StringOutput(u.code), StringOutput(v.code), StringOutput(w.code), 
                                        StringOutput(e.code), StringOutput(x.code))
                        Line[27][count][patcount] += "\n" + commline + "\n" + dataline + "\n" + codeline

                elif pattern.get("Uni") == 1:

                    profile = contribution.get("Profile")

                    # Line 26
                    scale  = getRefine(contribution, "Scale")
                    extinc = getRefine(contribution, "Extinct")
                    bov    = getRefine(contribution, "Bov")
                    str1   = getRefine(strainparameter, "Str1")
                    str2   = getRefine(strainparameter, "Str2")
                    str3   = getRefine(strainparameter, "Str3")
                    commline =  "! %-15s %-15s %-15s %-15s %-15s %-15s %-15s"\
                                %("Scale", "Extinc", "Bov", "Str1", "Str2", "Str3", "Strain-Model")
                    dataline =  "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s"\
                              %(StringOutput(scale.value), StringOutput(extinc.value), StringOutput(bov.value) ,
                                StringOutput(str1.value) , StringOutput(str2.value)  , StringOutput(str3.value),
                                StringOutput(strainparameter.get("StrainModelSelector")))
                    codeline =  "  %-15s %-15s %-15s %-15s %-15s %-15s"\
                              %(StringOutput(scale.code), StringOutput(extinc.code), StringOutput(bov.code) ,
                                StringOutput(str1.code) , StringOutput(str2.code)  , StringOutput(str3.code))
                    Line[26][count][patcount] =  commline + "\n" + dataline + "\n" + codeline

                    # Line 27
                    # 27 27-1
                    s2 = getRefine(profile, "Sig2")
                    s1 = getRefine(profile, "Sig1")
                    s0 = getRefine(profile, "Sig0")
                    #xt = getRefine(profile, "Xt")
                    xt = RefineCode()
                    #yt = getRefine(profile, "Yt")
                    yt = RefineCode()
                    z1 = getRefine(profile, "Z1")
                    #z0 = getRefine(profile, "Z0")
                    z0 = RefineCode()
                    commline =  "! %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-5s"\
                                %("Sig-2", "Sig-1", "Sig-0", "Xt", "Yt", "Z1", "Zo", "Size-Model")
                    dataline =  "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-5s"\
                              %(StringOutput(s2.value), StringOutput(s1.value), StringOutput(s0.value),
                                StringOutput(xt.value), StringOutput(yt.value), StringOutput(z1.value),
                                StringOutput(z0.value), StringOutput(contribution.get("SizeModelSelector")))
                    codeline =  "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s"\
                              %(StringOutput(s2.code), StringOutput(s1.code), StringOutput(s0.code),
                                StringOutput(xt.code), StringOutput(yt.code), StringOutput(z1.code),
                                StringOutput(z0.code)) 
                    Line[27][count][patcount] =  commline + "\n" + dataline + "\n" + codeline
                    # 27-2 27-3
                    g2 = getRefine(profile, "Gam2")
                    g1 = getRefine(profile, "Gam1")
                    g0 = getRefine(profile, "Gam0")
                    lt = getRefine(contribution, "LStr")
                    ls = getRefine(contribution, "LSiz")
                    commline = "! %-15s %-15s %-15s %-15s %-15s"% ("Gam-2", "Gam-1", "Gam-0", "LStr", "Lsiz") 
                    dataline = "  %-15s %-15s %-15s %-15s %-15s"% \
                               (StringOutput(g2.value), StringOutput(g1.value), StringOutput(g0.value),
                                StringOutput(lt.value), StringOutput(ls.value))
                    codeline = "  %-15s %-15s %-15s %-15s %-15s"% \
                               (StringOutput(g2.code), StringOutput(g1.code), StringOutput(g0.code),
                                StringOutput(lt.code), StringOutput(ls.code))
                    Line[27][count][patcount] += "\n" + commline + "\n" + dataline + "\n" + codeline

                # Line 29
                a = getRefine(phase, "a")
                b = getRefine(phase, "b")
                c = getRefine(phase, "c")
                alpha = getRefine(phase, "alpha")
                beta  = getRefine(phase, "beta" )
                gamma = getRefine(phase, "gamma")

                commline =  "! %-15s %-15s %-15s %-15s  %-15s %-15s"\
                            % ("a", "b", "c", "alpha", "beta", "gamma")
                dataline =  "  %-15s %-15s %-15s %-15s  %-15s %-15s"\
                          % (StringOutput(a.value    ), StringOutput(b.value   ), StringOutput(c.value    ),
                             StringOutput(alpha.value), StringOutput(beta.value), StringOutput(gamma.value))
                codeline =  "  %-15s %-15s %-15s %-15s  %-15s %-15s"\
                          %(StringOutput(a.code    ), StringOutput(b.code   ), StringOutput(c.code    ),
                            StringOutput(alpha.code), StringOutput(beta.code), StringOutput(gamma.code))
                Line[29][count][patcount] =  commline + "\n" + dataline + "\n" + codeline

                # Line 30 - 33  Preferred Orientation
                if pattern.get("Uni") == 0:
                    po = contribution.get("PreferOrient")
                    asymparam = contribution.get("AsymmetryParameter")

                    # Line 30
                    if contribution.get("Npr") != 7:

                        prefertuple = getPreferredOrientation(pattern, po)
                        pref1 = prefertuple[0]
                        pref2 = prefertuple[1]

                        pa1   = getRefine(asymparam, "PA1")
                        pa2   = getRefine(asymparam, "PA2")
                        pa3   = getRefine(asymparam, "PA3")
                        pa4   = getRefine(asymparam, "PA4")

                        commline = "! %-15s %-15s %-15s %-15s %-15s %-15s"% \
                                    ("Pref1", "Pref2", "Asy1", "Asy2", "Asy3", "Asy4") 
                        dataline = "  %-15s %-15s %-15s %-15s %-15s %-15s"% \
                                    (StringOutput(pref1.value), StringOutput(pref2.value), StringOutput(pa1.value), \
                                     StringOutput(pa2.value)  , StringOutput(pa3.value)   , StringOutput(pa4.value))
                        codeline = "  %-15s %-15s %-15s %-15s %-15s %-15s"% \
                                   (StringOutput(pref1.code), StringOutput(pref2.code), StringOutput(pa1.code),
                                    StringOutput(pa2.code)  , StringOutput(pa3.code)  , StringOutput(pa4.code))
                        Line[30][count][patcount] = commline + "\n" + dataline + "\n" + codeline

                    else:

                        prefertuple = getPreferredOrientation(pattern, po)
                        pref1 = prefertuple[0]
                        pref2 = prefertuple[1]

                        pa1   = getRefine(asymparam, "PA1")
                        pa2   = getRefine(asymparam, "PA2")
                        pa3   = getRefine(asymparam, "PA3")
                        pa4   = getRefine(asymparam, "PA4")
                        sl    = getRefine(asymparam, "S_L")
                        dl    = getRefine(asymparam, "D_L")

                        commline = "! %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s"% \
                                   ("Pref1", "Pref2", "Asy1", "Asy2", "Asy3", "Asy4", "S_L", "D_L")
                        dataline = "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s"% \
                                   (StringOutput(pref1.value), StringOutput(pref2.value), 
                                    StringOutput(pa1.value), StringOutput(pa2.value), 
                                    StringOutput(pa3.value)  , StringOutput(pa4.value)  ,
                                    StringOutput(sl.value) , StringOutput(dl.value))
                        codeline = "  %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s"% \
                                   (StringOutput(pref1.code), StringOutput(pref2.code), 
                                    StringOutput(pa1.code), StringOutput(pa2.code),
                                    StringOutput(pa3.code)  , StringOutput(pa4.code)  , 
                                    StringOutput(sl.code) , StringOutput(dl.code))
                        Line[30][count][patcount] = commline + "\n" + dataline + "\n" + codeline

                    # Line 32
                    if pattern.get("Ratio") < 0:
                        wave2nd = profile.get("Profile2ndWave")[0]

                        u2 = getRefine(wave2nd, "U2")
                        v2 = getRefine(wave2nd, "V2")
                        w2 = getRefine(wave2nd, "W2")

                        commline = "! Additional U,V,W parameters for Lambda2"
                        dataline =  StringOutput(u2.value) +  " " +StringOutput(v2.value) + " " + StringOutput(w2.value)
                        codeline =  StringOutput(u2.code) +  " " +StringOutput(v2.code) + " " + StringOutput(w2.code)

                        Line[32][count][patcount] = commline + "\n" + dataline + "\n" + codeline

                    # Line 33
                    if contribution.get("Npr") == 4 or contribution.get("Npr") > 7:
                        profileadd   = contribution.get("Profile")
                        shp1 = getRefine(profileadd, "SHP1")
                        shp2 = getRefine(profileadd, "SHP2")
                        
                        commline = "! Additional shape parameters"
                        dataline = "  %-15s %-15s %-15s %-15s"%\
                                   (StringOutput(shp1.value), StringOutput(shp1.code),
                                    StringOutput(shp2.value), StringOutput(shp2.code))

                        Line[33][count][patcount] = commline + "\n" + dataline

                elif pattern.get("Uni") == 1:

                    po = contribution.get("PreferOrient")
                    expdecay = contribution.get("ExpDecayFunction")

                    prefertuple = getPreferredOrientation(pattern, po)
                    pref1 = prefertuple[0]
                    pref2 = prefertuple[1]
                    alph0 = getRefine(expdecay, "ALPH0")
                    beta0 = getRefine(expdecay, "BETA0")
                    alph1 = getRefine(expdecay, "ALPH1")
                    beta1 = getRefine(expdecay, "BETA1")

                    if pattern.get("Npr") == 13:
                        commline = "! %-15s %-15s %-15s %-15s %-15s %-15s"% \
                                    ("Pref1", "Pref2", "alph0", "beta0", "alph1", "Kappa") 
                    else:
                        commline = "! %-15s %-15s %-15s %-15s %-15s %-15s"% \
                                 ("Pref1", "Pref2", "alph0", "beta0", "alph1", "beta1") 
                    dataline = "  %-15s %-15s %-15s %-15s %-15s %-15s"% \
                               (StringOutput(pref1.value), StringOutput(pref2.value), 
                                StringOutput(alph0.value), StringOutput(beta0.value),
                                StringOutput(alph1.value), StringOutput(beta1.value))
                    codeline = "  %-15s %-15s %-15s %-15s %-15s %-15s"% \
                               (StringOutput(pref1.code), StringOutput(pref2.code), 
                                StringOutput(alph0.code), StringOutput(beta0.code),
                                StringOutput(alph1.code), StringOutput(beta1.code))

                    Line[30][count][patcount] = commline + "\n" + dataline + "\n" + codeline

                    # Line 31 31-1
                    if contribution.get("Npr") == 10:
                        alph0 = getRefine(expdecay, "ALPH0T")
                        beta0 = getRefine(expdecay, "BETA0T")
                        alph1 = getRefine(expdecay, "ALPH1T")
                        beta1 = getRefine(expdecay, "BETA1T")

                        commline = "! %-15s %-15s %-15s %-15s"% ("alph0t", "beta0t", "alph1t", "beta1")
                        dataline = "  %-15s %-15s %-15s %-15s"% \
                                   (StringOutput(alph0.value), StringOutput(beta0.value), 
                                    StringOutput(alph1.value), StringOutput(beta1.value))
                        codeline = "  %-15s %-15s %-15s %-15s"% \
                                   (StringOutput(alph0.code) , StringOutput(beta0.code) ,
                                    StringOutput(alph1.code)  , StringOutput(beta1.code))
                        Line[31][count][patcount] = commline + "\n" + dataline + "\n" + codeline

                    # Line 33
                    abs1 = getRefine(contribution, "ABS1")
                    abs2 = getRefine(contribution, "ABS2")

                    commline = "! Absorption correction parameters"
                    dataline = "  %-15s %-15s %-15s %-15s"% \
                               (StringOutput(abs1.value), StringOutput(abs1.code),
                                StringOutput(abs2.value), StringOutput(abs2.code))
                    Line[33][count][patcount] = commline + "\n" + dataline

                # Line 34 - 35
                if phase.get("Sol") != 0:
                    # 34 34-1
                    shift = contribution.get("ShiftParameter")
                    shf1 = getRefine(shift, "SHF1")
                    shf2 = getRefine(shift, "SHF2")
                    shf3 = getRefine(shift, "SHF3")
                    ModS = shift.get("ModS")

                    commline = "!   Shift1    Shift2    Shift3    ModS"
                    dataline = StringOutput(shf1.value) + " " + StringOutput(shf2.value) + " " + StringOutput(shf3.value) + " " + StringOutput(ModS)
                    codeline = StringOutput(shf1.code) + " " + StringOutput(shf2.code) + " " + StringOutput(shf3.code) 
                    Line[34][count][patcount] = commline + "\n" + dataline + "\n" + codeline

                    # 35 Suite
                    if ModS == 1 or ModS == -1:
                        # shift parameter angle
                        commline = "! Shift-cos(1) or Shift-sin(-1) axis"
                        dataline = StringOutput(shift.get("Sh1")) + " " + StringOutput(shift.get("Sh2")) + " " + StringOutput(shift.get("Sh3"))
                        Line[35][count][patcount] = commline + "\n" + dataline

                    elif ModS < -1 and ModS >= 10:
                        # shift parameter user defined selective shift
                        commline = "! Shift integers (n1.h + n2.k + n3.l = n4.n + n5)   Shift-par    Code"
                        dataline = ""
                        for ss in shift.get("SelectiveShift"):
                            st = getRefine(ss, "Shift")
                            dataline += StringOutput(ss.get("n1")) + " " + StringOutput(ss.get("n2")) + " " + StringOutput(ss.get("n3")) + " " + \
                                        StringOutput(ss.get("n4")) + " " + StringOutput(ss.get("n5")) + " " + StringOutput(st.value) + " " + StringOutput(st.code)
                        Line[35][count][patcount] = commline + "\n" + dataline

                    elif ModS == 101:
                        Line[35][count][patcount] = PrintShiftLaue(shift, [6, 5, 5, 5])

                    elif ModS == 102:
                        Line[35][count][patcount] = PrintShiftLaue(shift, [4, 5, 5])

                    elif ModS == -102:
                        Line[35][count][patcount] = PrintShiftLaue(shift, [4, 5, 5])

                    elif ModS == 103:
                        Line[35][count][patcount] = PrintShiftLaue(shift, [4, 6])

                    elif ModS == 104 or ModS == 105:
                        Line[35][count][patcount] = PrintShiftLaue(shift, [2, 4])

                    elif ModS == 106 or ModS == 107:
                        Line[35][count][patcount] = PrintShiftLaue(shift, [2, 4])

                    elif ModS >= 108 and ModS <= 112:
                        Line[35][count][patcount] = PrintShiftLaue(shift, [2, 3])

                    elif ModS == 113 or ModS == 114:
                        Line[35][count][patcount] = PrintShiftLaue(shift, [1, 2])

                    else:
                        raise_(NotImplementedError, "ModS = " + StringOutput(ModS) + " not defined")

                # Line 36   SizeModel

                SizeModelSelector = contribution.get("SizeModelSelector")
                sizemodel         = contribution.get("SizeModel")

                if SizeModelSelector == 1 or SizeModelSelector == -1:
                    # cylindrical
                    commline = "! Platelet-Needle vector (Size)"
                    dataline = "  %-15s %-15s %-15s"% \
                               (StringOutput(sizemodel.get("Sz1")), StringOutput(sizemodel.get("Sz2")),
                                StringOutput(sizemodel.get("Sz3")))

                    Line[36][count][patcount] = commline + "\n" + dataline

                elif SizeModelSelector < -1:
                    # due to defects
                    sizebroaden = sizemodel.get("DefectSizeBroaden")
                    sz          = getRefine(sizebroaden, "SZ")

                    commline = "! Size-Broadening (n1.h + n2.k + n3.l=n n4 +/- n5)   Size-par    Code"
                    dataline =  StringOutput(sizebroaden.get("n1")) + " " + StringOutput(sizebroaden.get("n2")) + " " + \
                                StringOutput(sizebroaden.get("n3")) + " " + StringOutput(sizebroaden.get("n4")) + " " + \
                                StringOutput(sizebroaden.get("n5")) + " " + StringOutput(sz.value) + " " + StringOutput(sz.code)

                    Line[36][count][patcount] = commline + "\n" + dataline

                elif SizeModelSelector == 15:

                    shlist = [ ["Y00" , "Y22+", "Y22-", "Y20", "Y44+", "Y44-"], ["Y42+", "Y42-", "Y40"] ]
                    wbuf   = printLine36SizeModelSphericalHarmonic(sizemodel, shlist)
                    Line[36][count][patcount] = wbuf


                    shcoefficients = sizemodel.get("SHcoefficient")
                    
                elif SizeModelSelector == 16:
                    raise NotImplementedError("size model = 16 is not implemented")
                elif SizeModelSelector == 17:
                    raise NotImplementedError("size model = 17 is not implemented")
                elif SizeModelSelector == 18:
                    raise NotImplementedError("size model = 18 is not implemented")
                elif SizeModelSelector == 19:
                    raise NotImplementedError("size model = 19 is not implemented")
                elif SizeModelSelector == 20:
                    raise NotImplementedError("size model = 20 is not implemented")
                elif SizeModelSelector == 21:
                    raise NotImplementedError("size model = 21 is not implemented")
                elif SizeModelSelector == 22:
                    raise NotImplementedError("size model = 22 is not implemented")
                else:
                    pass

                # Line 37
                strainmodellist     = strainparameter.get("StrainModel")
                if len(strainmodellist) == 1:
                    strainmodel = strainmodellist[0]
                else:
                    strainmodel = None
                StrainModelSelector = strainparameter.get("StrainModelSelector")
                Str                 = phase.get("Str")


                if StrainModelSelector == 7:
                    commline = "! Axial vector Microstrain"
                    dataline = "  %-15s %-15s %-15s"% \
                               (StringOutput(strainmodel.get("St1")), StringOutput(strainmodel.get("St2")),
                                StringOutput(strainmodel.get("St3")))
                    Line[37][count][patcount] = commline + "\n" + dataline

                elif StrainModelSelector > 8 and Str == 0:
                    commline = "! 5 additional strain parameters"
                    dataline = ""
                    codeline = ""
                    for i in xrange(4, 8+1):
                        param_name = "Str"+StringOutput(i)
                        strmodel  = getRefine(strainmodel, param_name)
                        dataline  += StringOutput(strmodel.value) + " "
                        codeline  += StringOutput(strmodel.code ) + " "
                    Line[37][count][patcount] = commline + "\n" + dataline + "\n" + codeline

                elif Str == -1 and Str == 2 and Str == 3:
                    raise NotImplementedError("Line 37: Str == -1 and Str == 2 and Str == 3")

                elif abs(Str) == 1 and StrainModelSelector == 1:
                    lineitems = [5, 5, 5]
                    Line[37][count][patcount] = PrintStrainLaue(strainmodel, lineitems)

                elif abs(Str) == 1 and StrainModelSelector == 2:
                    lineitems = [5, 4]
                    Line[37][count][patcount] = PrintStrainLaue(strainmodel, lineitems)

                elif abs(Str) == 1 and StrainModelSelector == -2:
                    lineitems = [5, 4]
                    Line[37][count][patcount] = PrintStrainLaue(strainmodel, lineitems)

                elif abs(Str) == 1 and StrainModelSelector == 3:
                    lineitems = [6]
                    Line[37][count][patcount] = PrintStrainLaue(strainmodel, lineitems)

                elif abs(Str) == 1 and (StrainModelSelector == 4 or StrainModelSelector == 5):
                    lineitems = [4]
                    Line[37][count][patcount] = PrintStrainLaue(strainmodel, lineitems)

                elif abs(Str) == 1 and (StrainModelSelector == 6 or StrainModelSelector == 7):
                    lineitems = [4]
                    Line[37][count][patcount] = PrintStrainLaue(strainmodel, lineitems)

                elif abs(Str) == 1 and (StrainModelSelector >= 8 or StrainModelSelector <= 12):
                    lineitems = [3]
                    Line[37][count][patcount] = PrintStrainLaue(strainmodel, lineitems)

                elif abs(Str) == 1 and (StrainModelSelector == 13 or StrainModelSelector == 14):
                    lineitems = [2]
                    Line[37][count][patcount] = PrintStrainLaue(strainmodel, lineitems)

                elif (Str == 1 and StrainModelSelector == 0) or Str == 3:
                    pass
                    commline = "! Lorentzian strain coeff. + code"
                    dataline = ""


                # Line 38
                if (contribution.get("Npr") >= 7 and StrainModelSelector != 0) or Str == 1 or Str == 3:
                    commline    = "!  Lorentzian strain coeff.+ code"
                    lorstrain   = (strainparameter.get("LorentzianStrain"))[0]
                    xi          = getRefine(lorstrain, "XI")
                    dataline    = StringOutput(xi.value) + "   " + StringOutput(xi.code)
                    Line[38][count][patcount] = commline + "\n" + dataline 
     
                # Line 39 -- New Line
                commline =  "! Special reflections:\n" + \
                            "!  h   k   l  nvk       D-HG^2  Cod_D-HG^2      D-HL      Cod_D-HL      Shift    Cod_Shift"
                dataline = ""
                for spref in contribution.get("SpecialReflection"):
                    dhg2  = getRefine(spref, "D_HG2")
                    dhl   = getRefine(spref, "D_HL")
                    shift = getRefine(spref, "Shift")
                    dataline += "\n" + \
                                StringOutput(spref.get("h")  ) + " " + StringOutput(spref.get("k")) + " " + StringOutput(spref.get("l")) + " " + \
                                StringOutput(spref.get("nvk")) + " " + StringOutput(dhg2.value    ) + " " + StringOutput(dhg2.code     ) + " " + \
                                StringOutput(dhl.value       ) + " " + StringOutput(dhl.code      ) + " " + StringOutput(shift.value   ) + " " + \
                                StringOutput(shift.code      )
                if dataline != "":
                    Line[39][count][patcount] = commline + dataline

                # control parameter
                patcount += 1

            # end of pattern loop
                    
        # end if cry


        # Line 43
        if phase.get("Furth") > 0:
            raise NotImplementedError

        # Line 44
        for pvector in phase.get("PropagationVector"):
            vx = getRefine(pvector, "X")
            vy = getRefine(pvector, "Y")
            vz = getRefine(pvector, "Z")
            commline = "! Propagation vectors"
            dataline = StringOutput(vx.value) + " " + StringOutput(vy.value) + " " + StringOutput(vz.value)
            codeline = StringOutput(vx.code ) + " " + StringOutput(vy.code ) + " " + StringOutput(vz.code )
            Line[44][count] = commline + "\n" + dataline + "\n" + codeline

        # Line 45
        Line[45][count] = ""
        for soft in phase.get("DistanceRestraint"):
            dataline =  StringOutput(soft.get("CATOD1")) + " " + StringOutput(soft.get("CATOD2")) + " " + StringOutput(soft.get("ITnum")) + " " + \
                        StringOutput(soft.get("T1")) + " " + StringOutput(soft.get("T2")) + " " + StringOutput(soft.get("T3")) + " " + \
                        StringOutput(soft.get("Dist")) + " " + StringOutput(soft.get("Sigma"))
            Line[45][count] += "\n" + dataline
        if Line[45][count] == "":
            del Line[45][count]
        else:
            commline = "! Soft distance constraints"
            Line[45][count] = commline + "\n" + Line[45][count]


        count += 1

    # end of phase loop


    return Line

""" --- end of method ... """


def writeBlock4(fit, Line):
    """
    write Block4:  Line 47

    fit:    fit reference
    Line:   reference to list - Line
    """
    refine   = fit.get("Refine")
    commline = "! Limits for selected parameters"
    dataline = ""
    for variable in refine.get("Variable"):
        if variable.get("usemin") is True:
            templist  = variable.get("code").split("Code")
            if len(templist) > 1:
                numpar    = templist[1]
            else:
                numpar    = variable.get("ID").split("c")[1]
            dataline += "\n" + numpar + " " + StringOutput(variable.get("min")) + " " + StringOutput(variable.get("max")) + " " + \
                        StringOutput(variable.get("Step")) + " " + StringOutput(variable.get("Ibound")) + " " + StringOutput(variable.get("name"))
    if dataline != "":
        Line[47] = commline + dataline

    return Line


def writeBlock5(fit, Line):
    """
    write Block 5: Line 48, 49 for (1) Monte Carlo or (2) Simulated annearling
    """
    Cry = fit.get("Cry") 
    
    if Cry == 2:
        # Line 48:  Monte Carlo
        mc = fit.get("MonteCarlo")
        
        commline = "! %-10s %-10s %-10s %-10s"% \
            ("NCONF", "NSOLU", "NREFLEX", "NSCALEF")
        dataline = "  %-10s %-10s %-10s %-10s"% \
            (mc.get("NCONF"),   mc.get("NSOLU"), 
             mc.get("NREFLEX"), mc.get("NSCALEF"))
        Line[48] = commline+"\n"+dataline
    
    
    elif Cry == 3:
        # Line 49:  Simulate Annealing
        sa = fit.get("SimulatedAnnealing")

        commline = {}
        dataline = {}

        # Line 49-0
        commline[0] = "! %-15s %-15s %-15s %-10s %-10s %-10s"% \
            ("T_INI", "ANNEAL", "ACCEPT", "NUMTEMPS", "NUMTHCYC", "INITCONF")
        dataline[0] = "  %-15s %-15s %-15s %-10s %-10s %-10s"% \
            (sa.get("T_INI"),       sa.get("ANNEAL"),   sa.get("ACCEPT"), 
             sa.get("NUMTEMPS"),    sa.get("NUMTHCYC"), sa.get("INITCONF"))

        # Line 49-1
        commline[1] = "! %-10s %-10s %-10s %-10s %-10s"% \
            ("NCYCLM", "NSOLU", "NREFLEX", "NSCALEF", "NALGOR")
        dataline[1] = "  %-10s %-10s %-10s %-10s %-10s"% \
            (sa.get("NCYCLM"),  sa.get("NSOLU"),    sa.get("NREFLEX"), 
             sa.get("NSCALEF"), sa.get("NALGOR"))

        # Line 49-2
        commline[2] = "! %-10s %-10s"% ("ISWAP", "MCOMPL")
        dataline[2] = "  %-10s %-10s"% (sa.get("ISWAP"), sa.get("MCOMPL"))

        # Line 49-3
        for phase in fit.get("Phase"):
            if phase.get("Isy") == -2:
                errmsg = "Line 49-3 Isy = -2 Is Not Implemented Yet"
                raise NotImplementedError(errmsg)

        # Write All Information to Line
        Line[49] = ""
        if 4 in commline:
            lastline = 3
        else:
            lastline = 2
        for lno in xrange(lastline+1):
            Line[49] += commline[lno] + "\n"
            Line[49] += dataline
            if lno != lastline:
                Line[49] += "\n"

    return Line


def writeBlock6(fit, Line):
    """
    write Block 6 for a quick/problematic hack on Line of "! 2Th1/TOF1   2Th2/TOF2 Pattern #1

    Treat this line as Line 100
    """
    patternindex = 1
    for pattern in fit.get("Pattern"):
        thmin = pattern.get("Thmin")
        thmax = pattern.get("Thmax")
        commline = "! 2Th1/TOF1   2Th2/TOF2 Pattern # %-5s"% (patternindex)
        dataline = "  %-15s   %-15s"% (StringOutput(thmin), StringOutput(thmax))
        Line["ext"] = "\n"+commline + "\n" + dataline
        patternindex += 1
    # end -- for pattern in ...

    return Line


def getRefine(objref, param_name, index=None):
    """
    read object (objref) 's parameter (param_name) 

    (1) if this parameter is not be refined, constructure its value and codeword as 0.0000
    (2) if this parameter is to be refined, then go to the related Varaible (must be one and only one), 
        a. read the code and decode to p
        b. read the deviation and decode to a
        c. build Cx
        and the related Constraint object to
        d. calculate the init value of this parameter

    objref:     reference to an object inheriting from RietveldClass
    param_name: parameter name
    index:      an index for a parameter list

    return  --  RefineCode instance, 
    """
    constraint = objref.getConstraint(param_name, index)

    if constraint is None:
        # 3A float-mode
        refinecode      = RefineCode()
        refinecode.code = 0.0000
        refinecode.value= objref.get(param_name, index)

    elif not constraint.on:
        # 3C constraint-mode, turned off   worked only with Constraint
        refinecode       = RefineCode()
        refinecode.value = constraint.getValue()
        refinecode.code  = 0.0

    else:
        #NOTE: a constraint in Fullprof can only have one variable.

        # a. code is set to the position of the variable in the refinelist
        # the index should always succeed, which is guranteed by the constrution
        # of constraint/variable/refine.
        code = constraint.refine.get('Variable').index(constraint.variable)

        # b.1 deviation check
        if abs(constraint.dev) >= 10.0:
            raise RietError("deviation of constraint cannot be out of range (-10, 10); Correct it")

        # c. decompose original_formula for parameter-code
        refinecode      = RefineCode()
  
        if constraint.dev>=0:
            refinecode.code = code*10.0 + constraint.dev
        else:
            refinecode.code = -10.0*code + constraint.dev

        # e. parameter-value
        refinecode.value = constraint.getValue()

    refinecode.code=constraint.codeWord
    
    refinecode.value=constraint.realvalue
    #print("write:"+param_name+" value: "+str(refinecode.value)+" CodeWord:"+str(refinecode.code))
    return refinecode


def getPreferredOrientationVector(contribution):
    """
    print the information of preferred orientation vector (pr1, pr2, pr3)
    in case there is no preferred orienation defined

    return  --  3-tuple of float (Pr1, Pr2, Pr3)

    contribution
            --  Contribution instance
    """
    preferorient = contribution.get("PreferOrient")
    
    pr1 = preferorient.get("Pr1")
    pr2 = preferorient.get("Pr2")
    pr3 = preferorient.get("Pr3")

    rvalue = (pr1, pr2, pr3)

    return rvalue


def getPreferredOrientation(pattern, preferorient):
    """
    print the information of preferred orientation parameter 
    'pref1' and 'pref2'

    Convention
    1. if there is no preferred orientation, 
       the default Nor = 0.0 (such that Nor != 0 or 1)
       i.e., output Nor = 0.0 by default

    return  --  2-tuple of RefineCodes, (pref1, pref2)

    pattern         --  Pattern instance
    preferorient    --  PreferOrient instance or None
    """
    if preferorient is not None:
        pref1 = getRefine(preferorient, "Pref1")
        pref2 = getRefine(preferorient, "Pref2")
    else:
        # special handling for no preferred orientation
        # pref1 = G1
        nor   = pattern.get("Nor")
        pref1 = RefineCode()
        pref2 = RefineCode()
        if nor == 0:
            pref1.value = 0.0
        elif nor == -1:
            # no prefer orient, output choose Nor = 0, Pref = 0.0 from two choices
            pref1.value = 0.0
        else:
            pref1.value = 1.0
    # End -- if po is not None  

    rvalue = (pref1, pref2)

    return rvalue


def PrintShiftLaue(shiftmodel, lineitems):
    """
    print a ShiftParameterLaue object to FullProf pcr file, i.e, return a string

    shiftmodel: a reference to a ShiftParameterLaue object
    lineitems:  a list of integers, each corresponding to the number of items in a line

    Example:
    PrintShiftLuae(shiftmodel, [4, 5]):  print 4 lines, 2 for codes and 2 for value
    """
    from diffpy.pyfullprof.contribution import ShiftParameterLaue
    from diffpy.pyfullprof.laue import LaueShiftParameter
    # check
    if not isinstance(shiftmodel, ShiftParameterLaue):
        raise_(NotImplementedError, "PrintShiftLaue:  wrong shiftmodel object of type " + shiftmodel.__class__.__name__)

    # init
    laue = LaueShiftParameter(shiftmodel.get("Laueclass"))
    rstr = "! Luae class shift parameter"

    for line in lineitems:
        vstr = ""
        cstr = ""
        for item in xrange(line):
            hkl    = laue.get()
            gshift = shiftmodel.get("hkl", hkl)
            refine = getRefine(gshift, "D")
            vstr  += refine.value + " " 
            cstr  += refine.code  + " "
        rstr += "\n" + vstr + "\n" + cstr

    return rstr
        

def PrintStrainLaue(strainmodel, lineitems):
    """
    print a ShiftParameterLaue object to FullProf pcr file, i.e, return a string

    shiftmodel: a reference to a ShiftParameterLaue object
    lineitems:  a list of integers, each corresponding to the number of items in a line

    Example:
    PrintShiftLuae(shiftmodel, [4, 5]):  print 4 lines, 2 for codes and 2 for value
    """

    # check
    if not isinstance(strainmodel, StrainModelAnisotropic):
        raise_(NotImplementedError, "PrintStrainLaue:  wrong shiftmodel object of type " + strainmodel.__class__.__name__)

    # init
    laue = LaueStrainModel(strainmodel.get("Laueclass"))
    rstr = "! Luae class strain parameter"

    for line in lineitems:
        vstr = ""
        cstr = ""
        for item in xrange(line):
            hkl     = laue.get()
            gstrain = strainmodel.get("hkl", hkl)
            refine  = getRefine(gstrain, "S")
            vstr   += StringOutput(refine.value) + " " 
            cstr   += StringOutput(refine.code)  + " "
        rstr += "\n" + vstr + "\n" + cstr

    return rstr
        
   
def printLine36SizeModelSphericalHarmonic(sizemodel, shlist):
    """
    generate the block in PCR file for Line 36 Spherical Harmonic Size-Model

    Arguements
    sizemodel   :   SizeModelSpherical instance
    shlist      :   list of list of string, each string is a Spherical name

    Return      --  string, block of data in pcr file
    """
    wbuf = ""
   
    lineamount = len(shlist)

    for lindex in xrange(lineamount):

        # 1. init
        commline = "! "
        dataline = "  "
        codeline = "  "

        # 2. read through the list
        for spname in shlist[lindex]:
            # comment line
            commline += "%-15s "% (spname)
            # prepare data
            shc       = sizemodel.getSphericalHarmonic(spname)
            if shc.isKY() == "K":
                kyrefine = getRefine(shc, "K")
            else:
                kyrefine = getRefine(shc, "Y")
            # data line
            dataline += "%-15s "% (StringOutput(kyrefine.value))
            codeline += "%-15s "% (StringOutput(kyrefine.code ))
        # END -- for spname in shlist[lindex]:

        # 3. add to write buffer
        if lindex > 0:
            wbuf += "\n"
        wbuf += commline+"\n"+dataline+"\n"+codeline

    # END -- for lindex in xrange(lineamount):

    return wbuf


def StringOutput(value):
    """
    convert value to string;
    if value is float, then the format is 1.6

    value: any value, can be string, int, float
    """

    rstring = ""
    if isinstance(value, float):
        if abs(value) < 10000 and abs(value) > 1.0E-4:
            rstring = '%1.10f'% (value)
        elif abs(value) < 1.0E-18:
            rstring = '%1.10f'% (value)
        else:
            rstring = "%1.7E"% (value)
    else:
        rstring = str(value)

    return rstring



def printLines(Line):
    """
    print all Lines to screen in pcr file formate
    
    Line:   dictionary for all lines
    """

    # determine phase loop number
    block1_i  = 1
    block1_f  = 3
    block2_i  = 4
    block2_f  = 17
    block3_i  = 18
    block3_f  = 46
    #block4_i  = 47
    #block4_f  = 50

    # print

    # print "PrintLines: " + StringOutput(Line.keys())

    for l in xrange(block1_i, block1_f+1):
        if l in Line.keys():
            print(Line[l])

    for l in xrange(block2_i, block2_f+1):
        if l in Line.keys():
            print("Line " + StringOutput(l))
            print(Line[l])

    phaseloop = len(Line[18])
    for phasecount in xrange(1, phaseloop+1):
        # determine contribution loop --- phase related
        if 26 in Line and phasecount in Line[26]:
            contribloop = len(Line[26][phasecount])
        else:
            contribloop = 0
        # write
        for l in xrange(block3_i, block3_f+1):
            print("Line " + StringOutput(l))
            try:

                if l < 26 and l in Line and phasecount in Line[l]:
                    print(Line[l][phasecount])
                elif l >= 26 and l <= 42:
                    for n in xrange(1, contribloop+1):
                        if l in Line and phasecount in Line[l] and contribloop in Line[l][phasecount]:
                            print(Line[l][phasecount][contribloop])
                elif l >= 43 and l in Line and phasecount in Line[l]:
                    print(Line[l][phasecount])

            except AttributeError as err:
                print("Error reading Line:")
                print(StringOutput(Line[l]))
                raise_(AttributeError, StringOutput(err))

    return
    
    

def printLineToFile(Line, filename, userinfo):
    """
    print a list of lines to a file

    Line:       a list of string;
    filename:   name of the file for output
    userinfo:   list, each element in userinfo is a line for comments from user
    """

    fout = open(filename, "w")

    # determine phase loop number
    block1_i  = 1
    block1_f  = 3
    block2_i  = 4
    block2_f  = 17
    block3_i  = 18
    block3_f  = 46
    block4_i  = 47
    block4_f  = 50

    for l in xrange(block1_i, block1_f+1):
        if l in Line.keys():
            fout.write(Line[l]+"\n")
    fout.write("!\n")

    for l in xrange(block2_i, block2_f+1):
        if l in Line.keys():
            fout.write(Line[l]+"\n")
        fout.write("!\n")

    phaseloop = len(Line[18])
    for phasecount in xrange(1, phaseloop+1):
        # determine contribution loop --- phase related
        if 26 in Line and phasecount in Line[26]:
            contribloop = len(Line[26][phasecount])
        else:
            contribloop = 0

        # write:  line for phase only < 26
        for l in xrange(block3_i, 25+1):
            if l in Line and phasecount in Line[l]:
                fout.write(Line[l][phasecount]+"\n")
                fout.write("!\n")

        # write:  contribution
        for n in xrange(1, contribloop+1):
            for l in xrange(26, 42+1):
                if l in Line and phasecount in Line[l] and n in Line[l][phasecount]:
                    fout.write(Line[l][phasecount][n]+"\n")
                    fout.write("!\n")

        # write:  line for phase only > 43
        for l in xrange(43, block3_f+1):
            if l in Line and phasecount in Line[l]:
                fout.write(Line[l][phasecount]+"\n")
                fout.write("!\n")
    # end -for phasecount 

    # write block 4
    for l in xrange(block4_i, block4_f+1):
        if l in Line.keys():
            fout.write(Line[l]+"\n")
            fout.write("!\n")

    # write extra problemaic block 6
    if "ext" in Line:
        fout.write(Line["ext"]+"\n")

    # write extra user information
    for line in userinfo:
        content = line.split(".")[0]
        fout.write("! %-60s\n"%(content))

    fout.close()
                
    return


def validateConstraints(fit):
    """Check the validity of constraints in a Fit object before generating a 
    Fullprof pcr file.
    
    fit -- a Fit object.
    """
    for variable in fit.get("Refine").get("Variable"):
        if len(variable.constraints) < 1:
            raise RietError("Variable '%s' has no constraints."%str(variable.name))
        
    #other validation can be added in future
    return 
# EOF

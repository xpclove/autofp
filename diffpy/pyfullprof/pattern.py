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

__id__ = "$Id: pattern.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.rietveldclass import RietveldClass
from diffpy.pyfullprof.infoclass import ParameterInfo
from diffpy.pyfullprof.infoclass import BoolInfo
from diffpy.pyfullprof.infoclass import EnumInfo
from diffpy.pyfullprof.infoclass import FloatInfo
from diffpy.pyfullprof.infoclass import IntInfo
from diffpy.pyfullprof.infoclass import RefineInfo
from diffpy.pyfullprof.infoclass import StringInfo
from diffpy.pyfullprof.infoclass import ObjectInfo
from diffpy.pyfullprof.utilfunction import verifyType
from diffpy.pyfullprof.exception import RietError

class Pattern(RietveldClass):
    """
    Pattern contains all the information for a single pattern 
    for Rietveld refinement

    attributes:
    _contributionlist   --  list, containing related Contribution instance
    """

    ParamDict = {
        "Name":     StringInfo("Name", "Name", "Pattern"),
        "W_PAT":    FloatInfo("W_PAT", "Pattern Weight", 1.0, "", 0.0, 1.0),
        #"Chi2":     FloatInfo("Chi2", "Chi^2", 1.0E+8),
        "Scale":    RefineInfo("Scale", "Scale factor", 1.0E-3),
        "Rp":       FloatInfo("Rp", "Rp", 1.0E+8),
        "Rwp":      FloatInfo("Rwp", "Rwp", 1.0E+8),
        "Bkpos":    FloatInfo("Bkpos", "Origin of Polynomial Background", 47.0, "", 1.0E-8, None),
        "Wdt":      FloatInfo("Wdt", "Cut-off of the peak profile tails", 8.0),
        "Job":      EnumInfo("Job", "Radiation Type", -1,
                    {0: "X-ray",
                    1:  "Neutron Constant Wave",
                    -1: "Neutron T.O.F. and Magnetic",
                    -3: "Pattern Calculation Neutron T.O.F",
                    2:  "Pattern Calculation X-ray",
                    3:  "Pattern Calculation Neutron Constant Wavelength"},
                    [-1, 1, 0, -3, 2, 3]), 
        "Nba":      EnumInfo("Nba", "Background Type", 0,
                    {0: "Polynomial",
                    1:  "From CODFIL.bac",
                    -1: "Debye-like Polynomial",
                    -2: "Fourier Filtering",
                    -3: "Read 6 Additional Polynomial Coefficients",
                    2:  "Linear Interpolation with given background",
                    -4: "Polynomial",
                    -5: "Cubic Spline Interpolation"},
                    [0, -1, -3, -2, 2, -4, 1, -5]),
        "NbaPoint": IntInfo("NbaPoint", "number of points for user-defined background", 0, 0, None),
        "Nor":      EnumInfo("Nor", "Preferred Orientation Function", -1,
                    {0: "Preferred Orientation No.1",
                    1:  "Preferred Orientation No.2",
                    -1: "No preferred orientation"},
                    [0, 1, -1]),
        "Iwg":      EnumInfo("Iwg", "Refinement Weight Scheme", 0,
                    {0: "Standard Least Square Refinement",
                    1:  "Maximum Likelihood Refinement",
                    2:  "Unit Weights"},
                    [0, 1, 2]),
        "Res":      EnumInfo("Res", "Resolution Function", 0,
                    {0: "Not Given",
                    1:  "Given by File with Resolution Function 1",
                    2:  "Given by File with Resolution Function 2",
                    3:  "Given by File with Resolution Function 3",
                    4:  "List of value 2theta, H_G(2theta), H_L(2theta)",
                    5:  "User Input Resolution File",},
                    [0, 1, 2, 3, 4, 5]),
        "Ste":      IntInfo("Ste", "Number of data points reduction factor in powder data", 0, 0, None),
        "Uni":      EnumInfo("Uni", "Scattering Variable Unit", 1,
                    {0: "2theta degree",
                    1:  "T.O.F in microseconds",
                    2:  "Energy in keV"},
                    [1, 0, 2]),
        "Cor":      EnumInfo("Cor", "Intensity Correction", 0,
                    {0: "No Correction",
                    1:  "file with intensity correction is read",
                    2:  "file with coefficients of empirical function"},
                    [0, 1, 2]),
        "Datafile": StringInfo("Datafile", "Powder Data File", ""),
        "Instrumentfile":     StringInfo("InstrumentFile", "Instrument file fullpath", ""),
        "Resofile": StringInfo("Resofile", "Resolution File", ""),
        # output
        "Ipr":      EnumInfo("Ipr", "Profile integrated intensities output", 3,
                    {0: "no action",
                    1:  "observed and calculated proile intensities written in CODFIL.out",
                    2:  "CODFILn.sub with the calculated profile for each phase are generated",
                    3:  "CODFILn.sub with the calculated profile for each phase are generated, background added to each file"},
                    [0, 1, 2, 3]),
        "Ppl":      EnumInfo("Ppl", "Various types of calculated output - I", 0,
                    {0: "No action",
                    1:  "MORE TO ADD",
                    2:  "MORE TO ADD",
                    3:  "MORE TO ADD"},
                    [0, 1, 2, 3]),
        "Ioc":      EnumInfo("Ioc", "Various types of calculated outpout - II", 0,
                    {0: "No action",
                    1:  "MORE TO ADD",
                    2:  "MORE TO ADD"},
                    [0, 1, 2]),
        "Ls1":      EnumInfo("Ls1", "Various types of calculated outpout - III", 0,
                    {0: "No action",
                    1:  "MORE TO ADD"},
                    [0, 1]),
        "Ls2":      EnumInfo("Ls2", "Various types of calculated outpout - IV", 0,
                    {0: "No action",
                    1:  "MORE TO ADD",
                    4:  "MORE TO ADD",
                    5:  "unknown operation"},
                    [0, 1, 4, 5]),
        "Ls3":      EnumInfo("Ls3", "Various types of calculated outpout - V", 0,
                    {0: "No action",
                    1:  "MORE TO ADD"},
                    [0, 1]),
        "Prf":      EnumInfo("Prf", "Output Format of Rietveld Plot File CODFIL.prf", 0,
                    {
                    0: "no action",
                    -3: "WinPlot Output",
                    1:  "MORE TO ADD",
                    2:  "MORE TO ADD",
                    3:  "MORE TO ADD",
                    4:  "pl1 File Output"},
                    [0, -3, 1, 2, 3, 4]),
        "Ins":      EnumInfo("Ins", "Data File Format", 0,
                    {0: "Data in free format",
                    1: "D1A/D2B format",
                    2: "D1B old format",
                    3: "Format corresponding to the ILL instruments D1B and D20",
                    4: "Brookaven synchrotron data",
                   -4: "Brookaven synchrotron data given by DBWS program",
                    5: "GENERAL FORMAT for TWO AXIS instrument",
                    6: "D1A/D2B standard format prepared by D1A(D2B) SUM (ILL), ADDET(LLB), MIPDSUM(LLB) or equivalent programs",
                    7: "Files from D4 or D20L",
                    8: "Data from DMC at Paul Scherrer Institute",
                   10: "X, Y, Sigma format with header lines",
                   11: "Data from varaible time X-ray collection",
                   12: "data file conforming to GSAS standard data file",
                   14: "multiple bank data file from GEM (ISIS).gss file"},
                    [0, 1, 2, 3, 4, -4, 5, 6, 7, 8, 10, 11, 12, 14]),
        "Hkl":      EnumInfo("Hkl", "Output of Reflection List in CODFIL.hkl", 0, 
                    {0: "no action",
                    1:  "MORE TO ADD",
                    2:  "MORE TO ADD",
                    -2: "xpc add",
                    3:  "MORE TO ADD",
                    -3: "MORE TO ADD",
                    4:  "MORE TO ADD",
                    5:  "MORE TO ADD"},
                    [0, 1, 2, 3, -3, 4, 5]),
        "Fou":      EnumInfo("Fou", "Output of CODEFILE.fou Files", 0,
                    {0: "no action",
                    1:  "MORE TO ADD",
                    2:  "MORE TO ADD",
                    3:  "MORE TO ADD",
                    4:  "MORE TO ADD"},
                    [0, 1, 2, 3, 4]),
        "Ana":      EnumInfo("Ana", "Reliability of the refinement analysis", 0,
                    {0: "no action",
                    1:  "provides an analysis of the refinement at the end of summary file"},
                    [0, 1]),
        "Nex":      IntInfo("Nex", "Excluded Region Number", 0),
        "Nsc":      IntInfo("Nsc", "Scatteirng Factor Number", 0),
        
        # Histogram usage flag, this flag is added here to be compatible with GSAS
        "ISUSED" : BoolInfo("ISUSED",
                'True if pattern is used in the refinement',
                default=True),
    }

    ObjectDict  = {
        "LPFactor":     ObjectInfo("LPFactor", "LPFactor"),
        "Background":   ObjectInfo("Background", "Background"),
    }

    ObjectListDict = {
        "ExcludedRegion":   ObjectInfo("SetExcludedRegion", "ExcludedRegion", 0, None),
        "ScatterFactor":    ObjectInfo("SetScatterFactor", "ScatterFactor", 0, None),
    }

    def __init__(self, Parent):
        RietveldClass.__init__(self, Parent)

        """
        init subclass
        """
        background = Background(None)
        self.set("Background", background)

        lpfactor = LPFactor(None)
        self.set("LPFactor", lpfactor)

        # init attributes

        self._contributionlist = []
        self._reflections = {} 
        return


    def set(self, param_name, value,  index=None):
        """
        function:    set value to parameter 'param'

        param_name:  parameter name, can be (1) parameter name (2) subclass name
        value     :  (1) corresponding python build-in type
                     (2) an object reference
        index:       for the location in ObjectListDict/ParamListDict
        """

        rvalue = RietveldClass.set(self, param_name, value, index)

        if param_name == "Nba":
           
            nba = self.get(param_name)
            background = None

            if nba == 0:
                background = BackgroundPolynomial(self)
                background.set("Order", 6)
            elif nba == 1:
                background = BackgroundPolynomial(self)
                background.set("Order", 4)
            elif nba == -1:
                background = BackgroundDebye(self)
            elif nba == -2:
                background = BackgroundFourierwindow(self)
            elif nba == -3:
                background = BackgroundPolynomial(self)
                background.set("Order", 12)
            elif nba == -4:
                background = BackgroundPolynomial(self)
                background.set("Order", 12)
            elif nba == 2:
                background = BackgroundUserDefinedLinear(self)
            elif nba == -5:
                background = BackgroundUserDefinedCubic(self)
            else:
                errmsg = "Nba = %-10s is not supported" % (nba)
                raise RietError, errmsg

            if background is not None:
                self.set("Background", background)

        else:
            pass

        return rvalue

    def addBackgroundPoints(self, bkgdpointlist):
        """
        add Background point (x, intensity) to this InterpolatedBackground instance

        Arguments:
        bkgdpointlist   --  list of 2-tuple(x, intensity) for pre-selected background points

        Return          --  None
        """
        background = self.get("Background")
        for bkgdtup in bkgdpointlist:
            # 1. verify the input list term
            try: 
                pos = bkgdtup[0]
                bck = bkgdtup[1]
            except IndexError, err:
                errmsg = "%-30s:  Input Error!  Element in input bkgdpointlist is not 2-tuple\n"% \
                    (self.__class__.__name__+"addBackgroundPoints()")
                errmsg += "Error message:  %-40s"% (err)
                raise RietError(errmsg)

            # 2. make Core objects 
            background.set("POS", pos)
            background.set("BCK", bck)
            
        # END -- for bkgdtup in bkgdpointlist:

        return

    def validate(self):
        """
        validate the parameters, subclass and container to meet the refinement requirement of 
        class Pattern

        Return  --  bool
        """
        from diffpy.pyfullprof.utilfunction import checkFileExistence
        rvalue = RietveldClass.validate(self)

        errmsg = ""

        # type check: virtual base class
        name = self.__class__.__name__
        if name == "Pattern":
            errmsg += "%-30s: %-40s"%("Pattern.validate()", "virtual base Pattern")
            print errmsg
            rvalue = False

        # FullProf Parameter Synchronization
        # 1. Excluded Region
        nex = len(self.get("ExcludedRegion"))
        self.set("Nex", nex)

        # 2. Scttering Factor
        nsc = len(self.get("ScatterFactor"))
        self.set("Nsc", nsc)

        # 3. background
        background = self.get("Background")

        if isinstance(background, BackgroundUserDefinedLinear):
            #NOTE: avoid using self.set('Nba', 2)
            self.Nba = 2
        elif isinstance(background, BackgroundUserDefinedCubic):
            #NOTE: avoid using self.set('Nba', -5)
            self.Nba = -5
        elif isinstance(background, BackgroundFourierwindow):
            #NOTE: avoid using self.set('Nba', -2)
            self.Nba = -2

        elif isinstance(background, BackgroundPolynomial):
            if background.get("Order") == 6:
                #NOTE: avoid using self.set('Nba', 0)
                self.Nba = 0
            elif background.get("Order") == 12:
                #NOTE: avoid using self.set('Nba', -4)
                self.Nba = -4
            else:
                errmsg = "Polynomial Order = %-4s Is Not Supported"% (background.get("Order"))
                raise NotImplementedError(errmsg)
        else:
            pass       

        if self.get("Nba") <= -5 or self.get("Nba") >= 2:
            self.set('NbaPoint', self.get("Background").size())

        if background.ParamDict.has_key("Bkpos"):
            self.set('Bkpos', self.get("Background").get("Bkpos"))

        # 4. output 
        self.set("Ipr", 3)
        if self.get("Prf") == 0:
            self.set("Prf", 3)

        # 5. peak profile Npr
        for contribution in self._contributionlist:
            npr = contribution.get("Npr")
            self.set("Npr", npr)

        # WZ: this section (item 6) is removed as all wdt from fit should be trustful
        # 6. Peak range
        # for contribution in self._contributionlist:
        #     wdt = contribution.get("Profile").get("PeakRange")
        #     if wdt > 0.0:
        #         self.set("Wdt", wdt)
        wdt = self.get("Wdt")
        if wdt <= 0.0:
            errmsg = String.Format("Pattern has Wdt (peak range) = %f <= 0") % (wdt)
            raise RietError(errmsg)

        # Check Valid
        # 1. resolution file
        if self.get("Res") != 0:
            exist = checkFileExistence(self.get("Resofile"))
            if not exist:
                rvalue = False
                errmsg += "Resolution File %-10s Cannot Be Found\n"% (self.get("Resofile"))

        # 2. data file.... ->  moved to Fit.validate()
        
        if rvalue is not True:
            print "Invalidity Detected In %-10s: %-60s"% (self.__class__.__name__, errmsg)

        return rvalue


    def importPrfFile(self, prffname):
        """
        read a prf file as the calculated pattern data

        Return      --  dictionary 
                        key:   2Theta/TOF/..., Yobs, Ycalc, 
                        value: list of float

        Argument
        prffname    --  string, name of the corresponding prf file
        """
        # import file
        try:
            pfile = open(prffname, "r")
            lines = pfile.readlines()
            pfile.close()
        except IOError, err:
            errmsg = "Prf File: %-15s Cannot be Located"%(prffname)
            print "pyfullprof.Pattern.importPrfFile(): %40s"%(errmsg)
            rdict = {}
            return rdict

        # read information
        contents = []
        for line in lines:
            content = line.split("\n")[0].strip() 
            if content != "":
                contents.append(content.split())
        # LOOP-OVER: for line in lines

        # check Line 0:
        terms = content[0].split()
        if len(terms) <= 1:
            contents.remove(contents[0]) 

        # length/amount of data point
        try:
            datalength = int(contents[0][1])
        except ValueError, err:
            pass
        except IndexError, err:
            print contents[0]
            raise IndexError(err)
        # title line
        titleline  = -1
        for index in xrange(len(contents)):
            for term in contents[index]:
                if term == "Ycal":
                    titleline = index
                    break
            if titleline >= 0:
                break
        if titleline < 0:
            errmsg = "Pattern.importPrfFile():  File %-10s Format Error!  Cannot Locate Title-Line ... Yobs Ycal ..."%(prffname)
            raise RietError(errmsg)

        # init return list
        self._xobs = []
        self._yobs = []
        self._ycal = []

        #for index in xrange(titleline+1, titleline+1+datalength):
        index    = titleline+1
        maxindex = len(contents)-1
        STOP     = False
        startvalue = -1.0E20
        while not STOP:
            xvalue = float(contents[index][0])
            # incrementing sequence?
            if xvalue < startvalue:
                STOP = True
            else:
                self._xobs.append(float(contents[index][0]))
                try:
                    self._yobs.append(float(contents[index][1]))
                    self._ycal.append(float(contents[index][2]))
                except ValueError, err:
                    errmsg = "Reading Prf %-20s Meeting\n%-60s"% (prffname, err)
                    raise RietError(errmsg)
            # end of file
            if index == maxindex:
                STOP = True
            else:
                index += 1
                startvalue = xvalue
            
        return 

    def setDataProperty(self, datalist, radiationtype):
        """ Set Datafile and Job for FullProf """
        self.set("Datafile", datalist[1])
        if radiationtype == "Xray":
            self.set("Job", 0)
        elif radiationtype == "NeutronCW":
            self.set("Job", 1)
        elif radiationtype == "NeutronTOF":
            self.set("Job", -1)
        else:
            self.set("Job", radiationtype)
        self.set("Ins", 10)
        return



class Pattern2Theta(Pattern):
    """ Pattern with Xray Unit
    """

    ParamDict = {
        # experiment set
        "Npr":      EnumInfo("Npr", "Default Profile", 0,
                    {
                        0:  "Gaussian",
                        1:  "Cauchy",
                        2:  "Modified 1 Lorentzian",
                        3:  "Modified 2 Lorentzian",
                        4:  "Tripled Pseudo-Voigt",
                        5:  "Psuedo-Voigt",
                        6:  "Pearson VII",
                        7:  "Thompson-Cox-Hastings",
                        8:  "Numerical Profile given in CODFIL.shp",
                        11: "Split Psuedo-Voigt Function",
                        12: "Pseudo-Voigt function convoluted with axial divergence asymmetry function",
                    },
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12]),       
        "Lambda1":  FloatInfo("Lambda1", "Wavelength lambda_1", -0.0, "A", 0.0, None),
        "Lambda2":  FloatInfo("Lambda2", "Wavelength lambda_2", -0.0, "A", 0.0, None),
        "Ratio":    FloatInfo("Ratio", "I_1/I_2", 1.0),
        "muR":      FloatInfo("muR", "Absorption Correction", 0.0),
        "2nd-muR":  FloatInfo('2nd-muR', 'Second Absorption Correction', 0.0), # new in 2011 
        "AsymLim":  FloatInfo("AsymLim", "Limit Angle for Asymmetry correction", 1.0, "2theta degree"),
        # refinement parameters and powder data range
        "Thmin":    FloatInfo("Thmin", "Starting Scattering Variable", 0.0, "2theta degree"),
        "Step":     FloatInfo("Step", "Step of Scattering Variable", 1.0, "2theta degree"),
        "Thmax":    FloatInfo("Thmax", "Ending Scattering Variable", 90.0, "2theta degree"),
        "PSD":      FloatInfo("PSD", "Incident Beam Angle", 45.0, "degree"),
        "Sent0":    FloatInfo("Sent0", "Maximum Angle To Where Primary Beam", 0.0, "degree"),
        # experiment set II: refinable parameters
        "More":     BoolInfo("More", "More Options", True),
        "Zero":     RefineInfo("Zero", "Zero Point", 0.0, unit="degree"), 
        "Sycos":    RefineInfo("Sycos", "Sycos", 0.0),
        "Sysin":    RefineInfo("Sysin", "Sysin", 0.0),
        "Lambda":   RefineInfo("Lambda", "Wavelength \lambda", 0.0),
    }

    ObjectDict  = { }

    ObjectListDict = {
        "MicroAbsorption":   ObjectInfo("SetMicroAbsorption", "MicroAbsorption", 0, 1),
    }

    def __init__(self, Parent=None):
        """ initialize:  combine dictionaries

        Argument:
          - Parent  :   Rietveld object

        Return      :   None
        """
        Pattern.__init__(self, Parent)

        return


    def setCalculation(self):
        """
        set this instance to pattern calculation mode

        return  --  None
        """
        thisjob = self.get("Job")

        if thisjob == 0:
            self.set("Job", 2)
        elif thisjob == 1:
            self.set("Job", 3)
        elif thisjob == 2 or thisjob == 3:
            pass
        else:
            errmsg = "Job = %-10s Is Not In Class %-20s Object" % \
                    (self.get("Job"), self.__class__.__name__)
            raise RietError(errmsg)
        # END-IF-ELSE

        return


    def addContribution(self, contribution):
        """
        add a Contribution pertinent to this phase

        return  --  None

        contribution  --  Contribution instance
        """
        from diffpy.pyfullprof.contribution import Contribution2Theta
        verifyType(contribution, Contribution2Theta)
        self._contributionlist.append(contribution)
        return


    def getUnitString(self):
        """
        provide a string to the unit of this pattern

        return  --  string, unit of this type of pattern 2theta
        """
        rstring = "2-theta (degree)"

        return rstring


    def validate(self):
        """
        validate the parameters, subclass and container to meet the refinement requirement
        """
        rvalue = Pattern.validate(self)

        # Set: Uni
        self.set("Uni", 0)


        return rvalue


Pattern2Theta.ParamDict.update(Pattern.ParamDict)
Pattern2Theta.ObjectDict.update(Pattern.ObjectDict)
Pattern2Theta.ObjectListDict.update(Pattern.ObjectListDict)


class PatternTOF(Pattern):
    """ Class for Time-of-flight Pattern
    """
    ParamDict = {
        # experiment set
        "Bank":     IntInfo("Bank", "Bank Index In Pattern File", 1),
        "Npr":      EnumInfo("Npr", "Default Profile", 0,
                    {
                        0:  "Gaussian",
                        1:  "Cauchy",
                        2:  "Modified 1 Lorentzian",
                        3:  "Modified 2 Lorentzian",
                        4:  "Tripled Pseudo-Voigt",
                        5:  "Psuedo-Voigt",
                        6:  "Pearson VII",
                        7:  "Thompson-Cox-Hastings",
                        8:  "Numerical Profile given in CODFIL.shp",
                        9:  "T.O.F. Convolution Pseudo-Voigt",
                        10: "T.O.F. Convolution Pseudo-Voigt versus d-spacing",
                        11: "Split Psuedo-Voigt Function",
                        12: "Pseudo-Voigt function convoluted with axial divergence asymmetry function",
                        13: "T.O.F. Pseudo-Voigt function convoluted with Ikeda-Carpenter function"
                    },
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]),           
        "Iabscor":  EnumInfo("Iabscor", "Absorption Correction", 3,
                    {1: "Flat Plate Perpendicular to Incident Beam",
                    2:  "Cylindrical Sample",
                    3:  "Exponential correction"},
                    [1, 2, 3]),
        # refinement parameters and powder data range
        "Thmin":    FloatInfo("Thmin", "Starting Scattering Variable", 0.0, "micro-second"),
        "Step":     FloatInfo("Step", "Step of Scattering Variable", 1.0, "micro-second"),
        "Thmax":    FloatInfo("Thmax", "Ending Scattering Variable", 0.0, "micro-second"),
        "TwoSinTh": FloatInfo("TwoSinTh", "2*sin(theta)", 0.0, "degree", 0, 360),         # 2SinTh
        # experiment set II: refinable parameters
        "Zero":     RefineInfo("Zero", "Zero Point", 0.0, unit="microsecond"),
        "Dtt1":     RefineInfo("Dtt1", "Dtt1", 0.0),
        "Dtt2":     RefineInfo("Dtt2", "Dtt2", 0.0),
        "Width":    RefineInfo("Width", "Width of the crossover region", 0.0),
        "xcross":   RefineInfo("xcross", "position of center of the crossover region", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, Parent=None):
        """ initialize:  combine dictionaries
        """
        Pattern.__init__(self, Parent)

        return


    def addContribution(self, contribution):
        """ add a Contribution pertinent to this phase

        return  --  None

        contribution  --  Contribution instance
        """
        from diffpy.pyfullprof.contribution import ContributionTOF
        verifyType(contribution, ContributionTOF)

        self._contributionlist.append(contribution)

        return


    def setCalculation(self):
        """
        set this instance to pattern calculation mode

        return  --  None
        """
        self.set("Job", -3)

        return


    def getUnitString(self):
        """
        provide a string to the unit of this pattern

        return  --  string, unit of this type of pattern TOF
        """
        rstring = "Time-of-Flight (micro-second)"

        return rstring


    def validate(self):
        """
        validate the parameters, subclass and container to meet the refinement requirement
        """
        rvalue = Pattern.validate(self)

        # Set:  Uni
        self.set("Uni", 1)

        # Check: TwoSinTh
        if abs(self.get("TwoSinTh")) < 1.0E-7:
            print "Not Allowed:  TwoSinTh = 0.0"
            rvalue = False

        return rvalue

PatternTOF.ParamDict.update(Pattern.ParamDict)
PatternTOF.ObjectDict.update(Pattern.ObjectDict)
PatternTOF.ObjectListDict.update(Pattern.ObjectListDict)


class PatternTOFThermalNeutron(PatternTOF):
    
    ParamDict = {
        # experiment set
        "Npr":      EnumInfo("Npr", "Default Profile", 10,
                    {
                        10: "T.O.F. Convolution Pseudo-Voigt versus d-spacing",
                    },
                    [10]),           
        "Zerot":    RefineInfo("Zerot", "Zero shift for thermal neutrons", 0.0),
        "Dtt1t":    RefineInfo("Dtt1t", "coefficient 1 for d-spacing calculation", 0.0),
        "Dtt2t":    RefineInfo("Dtt1t", "coefficient 2 for d-spacing calculation", 0.0),
    }

    ObjectDict  = {}

    ObjectListDict = {
    }

    def validate(self):
        """
        validate the parameters, subclass and container to meet the refinement requirement
        """
        rvalue = PatternTOF.validate(self)

        if self.get("Npr") != 10:
            rvalue = False
            errmsg = "PyFullProf.Core.PatternTOFNeutronThermal:  Npr = %-10 (Must Be 10)"% \
                self.get("Npr")
            print errmsg

        return rvalue

PatternTOFThermalNeutron.ParamDict.update(PatternTOF.ParamDict)
PatternTOFThermalNeutron.ObjectDict.update(PatternTOF.ObjectDict)
PatternTOFThermalNeutron.ObjectListDict.update(PatternTOF.ObjectListDict)


class PatternED(Pattern):


    ParamDict = {
        "TwoSinTh": FloatInfo("TwoSinTh", "2*sin(theta)", 0.0, "degree", 0, 360),         # 2SinTh
        "Npr":      EnumInfo("Npr", "Default Profile", 0,
                    {
                        0:  "Gaussian",
                        1:  "Cauchy",
                        2:  "Modified 1 Lorentzian",
                        3:  "Modified 2 Lorentzian",
                        4:  "Tripled Pseudo-Voigt",
                        5:  "Psuedo-Voigt",
                        6:  "Pearson VII",
                        7:  "Thompson-Cox-Hastings",
                        8:  "Numerical Profile given in CODFIL.shp",
                        9:  "T.O.F. Convolution Pseudo-Voigt",
                        10: "T.O.F. Convolution Pseudo-Voigt versus d-spacing",
                        11: "Split Psuedo-Voigt Function",
                        12: "Pseudo-Voigt function convoluted with axial divergence asymmetry function",
                        13: "T.O.F. Pseudo-Voigt function convoluted with Ikeda-Carpenter function"
                    },
                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]),     

    }
                    
                    
    def __init__(self, Parent=None):
        """
        initialize:  combine dictionaries
        """
        Pattern.__init__(self, Parent)

        return


    def validate(self):
        """
        validate the parameters, subclass and container to meet the refinement requirement
        """
        rvalue = Pattern.validate(self)

        # Uni
        self.set("Uni", 2)

        # Check:  TwoSinTh
        if abs(self.get("TwoSinTh")) < 1.0E-7:
            print "Not Allowed:  TwoSinTh = 0.0"
            rvalue = False

        return rvalue

PatternED.ParamDict.update(Pattern.ParamDict)
PatternED.ObjectDict.update(Pattern.ObjectDict)
PatternED.ObjectListDict.update(Pattern.ObjectListDict)



class MicroAbsorption(RietveldClass):
    """
    MicroAbsorption constains the parameters for optional microabsorption 
    for Bragg-Brentao geometry
    """


    ParamDict = {
        "P0":       RefineInfo("P0", "P0", 0.0),
        "CP":       RefineInfo("CP", "CP", 0.0),
        "TAU":      RefineInfo("TAU", "TAU", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization

        parent: None of real parent class
        """
        RietveldClass.__init__(self, parent)

        return




class TOFdspacing(RietveldClass):
   


    ParamDict = {

    }

    ObjectDict  = {}

    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return


"""
Background Suite
"""


class Background(RietveldClass):
    """
    Background is an interface
    """

    ParamDict = {}
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, Parent):
        """
        initialization:
        """
        RietveldClass.__init__(self, Parent)
       
        return

    
    def validate(self):
        """
        validate the parameters, subclass and container to meet the refinement requirement
        """ 
        rvalue = RietveldClass.validate(self)

        name = self.__class__.__name__
        if name == "Background":
            print "base class of Background is not allowed"
            rvalue = False

        return rvalue


class BackgroundUserDefined(Background):
    """
    Background with user specified/defined background points

    attributes:
    - Interpolation type
    """
    #FIXME: Not Sure Whether Bkpos Makes Sense In Physics For This Background

    Interoplation = "None"

    ParamDict = {
        "Bkpos":    FloatInfo("Bkpos", "Origin of Polynomial Background", 1.0, 
            "", 1.0E-8, None),
    }
    ParamListDict = {}
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, Parent = None):
        """ initialization

        Argument:
          - Parent  : Rietveld object the reference to its component-parent

        Return      :   None
        """
        Background.__init__(self, Parent)

        return


    def size(self):
        """
        return number of background points
        """
        return len(self.POS)


    def validate(self):
        """
        validating before refinement
        """
        rvalue = Background.validate(self)
        
        if (len(self.BCK)!=len(self.POS)):
            print "'%s': the number of BCK is not equal to the number of POS"\
                  % (self.name)
            rvalue = False
        
        return rvalue

BackgroundUserDefined.ParamDict.update(Background.ParamDict)
BackgroundUserDefined.ParamListDict.update(Background.ParamListDict)
BackgroundUserDefined.ObjectDict.update(Background.ObjectDict)
BackgroundUserDefined.ObjectListDict.update(Background.ObjectListDict)

"""   end of class BackgroundUserDefined  """



class BackgroundUserDefinedLinear(BackgroundUserDefined):
    """
    SetBackgroundUserDefined: user-defined background
    """

    Interoplation = "Linear"

    ParamDict = {}
    ParamListDict = {
         "POS":    FloatInfo("POS", "Background point position", 0.0, minsize=2, maxsize=None), 
         "BCK":    RefineInfo("BCK", "Background point intensity", 0.0, minsize=2, maxsize=None)
        }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, Parent=None):
        """
        initialzation
        """
        BackgroundUserDefined.__init__(self, Parent)

        return

BackgroundUserDefinedLinear.ParamDict.update(BackgroundUserDefined.ParamDict)
BackgroundUserDefinedLinear.ParamListDict.update(BackgroundUserDefined.ParamListDict)
BackgroundUserDefinedLinear.ObjectDict.update(BackgroundUserDefined.ObjectDict)
BackgroundUserDefinedLinear.ObjectListDict.update(BackgroundUserDefined.ObjectListDict)


class BackgroundUserDefinedCubic(BackgroundUserDefined):
    """
    SetBackgroundUserDefined: user-defined background
    """
    Interoplation = "Cubic"

    ParamDict = {}
    ParamListDict = {
         "POS":    FloatInfo("POS", "Background point position", 0.0, minsize=4, maxsize=None), 
         "BCK":    RefineInfo("BCK", "Background point intensity", 0.0, minsize=4, maxsize=None)
        }
    ObjectDict  = {}
    ObjectListDict = {}
                    
    def __init__(self, Parent=None):
        """
        initialization
        """
        BackgroundUserDefined.__init__(self, Parent)

        return


    def validate(self):
        """
        validating before refinement
        """
        rvalue = BackgroundUserDefined.validate(self)

        if self.size() < 4:
            errmsg = "BackgroundUserDefinedCubic  number of background point = %-5s < 4"% \
                (self.size())
            raise RietError(errmsg)

        return rvalue


BackgroundUserDefinedCubic.ParamDict.update(BackgroundUserDefined.ParamDict)
BackgroundUserDefinedCubic.ParamListDict.update(BackgroundUserDefined.ParamListDict)
BackgroundUserDefinedCubic.ObjectDict.update(BackgroundUserDefined.ObjectDict)
BackgroundUserDefinedCubic.ObjectListDict.update(BackgroundUserDefined.ObjectListDict)



class BackgroundPolynomial(Background):
    """ BackgroundPolynomial is for background represented in polynomial functions
    """


    ParamDict = {
        "Order":    IntInfo("Order", "polynomial order", 0),
        "Bkpos":    FloatInfo("Bkpos", "Origin of Polynomial Background", 1.0, "", 1.0E-8, None),

    }
    ParamListDict = {
        "BACK":    RefineInfo("BACK", "Polynomial Background coefficient", 0.0, minsize=0, maxsize=12),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initalization
        """
        Background.__init__(self, parent)

        return

    def set(self, name, value, index=None):
        """Set the value for a member.

        name  --  a key in ParamDict, ParamListDict, ObjectDict or ObjectListDict
        value --  the value/object to be set
        index --  only for ObjectListDict object, to give the location of the object
        """
        Background.set(self, name, value, index)
        
        if name == 'Order':
            n  = len(self.BACK)
            if value > n:
                for i in range(n, value):
                    self.set('BACK', 0.0)
            elif value < n:
                for i in range(n-1, value-1, -1):
                    self.delete('BACK', i)
            

    def validate(self):
        """
        check whether the setup meets the requirement according to ObjectListDict and ObjectDict

        1. Check the order to be 6 or 12

        2. If order = 6, get rid of last 6 parameters from ParamDict
        """
        rvalue = True

        order = self.get("Order")
        if not (order == 6 or order == 12):
            print "%s '%s': The order=%i is invalid."\
                   %(self.path, self.__class__.__name__, self.Order)
            rvalue = False
            
        if len(self.BACK) != self.Order:
            print "%s '%s': The order=%i and the number of coefficients=%i do not match."\
                   %(self.path, self.__class__.__name__, self.Order, len(self.BACK))
            rvalue = False

        return rvalue         



class BackgroundDebye(Background):
    """
    Background with Debye-like function and order-6 background
    """


    ParamDict = {
        "BACK1":    RefineInfo("BACK1", "Polynomial Back 1", 0.0),
        "BACK2":    RefineInfo("BACK2", "Polynomial Back 2", 0.0),
        "BACK3":    RefineInfo("BACK3", "Polynomial Back 3", 0.0),
        "BACK4":    RefineInfo("BACK4", "Polynomial Back 4", 0.0),
        "BACK5":    RefineInfo("BACK5", "Polynomial Back 5", 0.0),
        "BACK6":    RefineInfo("BACK6", "Polynomial Back 6", 0.0),
        "Bc1":      RefineInfo("Bc1", "Back 1", 0.0),
        "Bc2":      RefineInfo("Bc2", "Back 2", 0.0),
        "Bc3":      RefineInfo("Bc3", "Back 3", 0.0),
        "Bc4":      RefineInfo("Bc4", "Back 4", 0.0),
        "Bc5":      RefineInfo("Bc5", "Back 5", 0.0),
        "Bc6":      RefineInfo("Bc6", "Back 6", 0.0),
        "D1":       RefineInfo("D1", "Debye Back 1", 0.0),
        "D2":       RefineInfo("D2", "Debye Back 2", 0.0),
        "D3":       RefineInfo("D3", "Debye Back 3", 0.0),
        "D4":       RefineInfo("D4", "Debye Back 4", 0.0),
        "D5":       RefineInfo("D5", "Debye Back 5", 0.0),
        "D6":       RefineInfo("D6", "Debye Back 6", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        Background.__init__(self, parent)

        return




class BackgroundFourierwindow(Background):
    """
    Background with Fourier window filtering
    """


    ParamDict = {
        "FWINDOW":  IntInfo("FWINDOW", "Fourier window filtering number", 0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        Background.__init__(self, parent)

        return





class BkgdPoly(RietveldClass):
    """
    one order of polynomial background: 
    designed for flexible order of polynomial background calculation
    NOT USED NOW
    """


    ParamDict = {
        "order":    IntInfo("order", "polynomial term order", 0),
        "Bkgd":     RefineInfo("Bkgd", "background value", 0.0),
    }    
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, Parent, order=None, value=None):
        """
        initialization
        order:  polynomial order
        value:  Bkgd
        """
        RietveldClass.__init__(self, Parent)
        if order is not None:
            self.set("order", order)
        if value is not None:
            self.set("Bkgd", value)

        return



"""
Excluded Region Suite
"""

class ExcludedRegion(RietveldClass):
    """
    A single excluded region
    """

    ParamDict = {
        "begin":    FloatInfo("begin", "excluded region begin position", 0.0),
        "end":      FloatInfo("end",   "excluded region begin position", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return



"""
Scattering Factor Suite
"""

class ScatterFactor(RietveldClass):
    """
    Scattering Factor base class
    """

    ParamDict = {}
    ObjectDict  = {
        "FormFactor":   ObjectInfo("FormFactor", "FormFactor"),
    }
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)
        
        return


    def validate(self):
        """
        validate the parameters, subclass and container to meet the refinement requirement
        """ 
        rvalue = RietveldClass.validate(self)

        if self.__class__.__name__ == "ScatterFactor":
            print "base class ScatterFactor is not allowed"
            rvalue = False

        return rvalue




class ScatterFactorXray(ScatterFactor):
    """
    scattering factor for x-ray
    """

    ParamDict = {
        "NAM":  StringInfo("NAM", "name of chemical element", ""),
        "DFP":  FloatInfo("DFP", "Df'", 0.0),
        "DFPP": FloatInfo("DFPP", "Df''", 0.0),
        "ITY":  EnumInfo("ITY", "form factor definition", 0,
                    {0: "user providing sin(theta)/lambda dependent part of X-rays form factor",
                    -1: "user defining a table of form factor sin(theta)/lambda - f",
                    2:  "using tabulated coefficient for sin(theta)/lambda - f"},
                    [0, -1, 2]),
    }       
   
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        inheriting initialization
        """
        ScatterFactor.__init__(self, parent)

        formfactorxray = FormFactorXray(None)
        self.set('FormFactor', formfactorxray)


        return

ScatterFactorXray.ParamDict.update(ScatterFactor.ParamDict)
ScatterFactorXray.ObjectDict.update(ScatterFactor.ObjectDict)
ScatterFactorXray.ObjectListDict.update(ScatterFactor.ObjectListDict)



class ScatterFactorNeutron(ScatterFactor):
    """
    scattering factor for neutron
    """

    ParamDict = {
        "NAM":  StringInfo("NAM", "name of chemical element", ""),
        "b":    FloatInfo("b", "b", 0.0),
        "ITY":  EnumInfo("ITY", "form factor definition", 0,
                    {0: "only read a user defined atomic Fermi length b",
                    1:  "user providing magnetic form factor",
                    -1: "user defining a table of sin(theta)/lambda - f"},
                    [0, 1, -1]),
    }       
   
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        inheriting initialization
        """
        ScatterFactor.__init__(self, parent)
        
        formfactor = FormFactorNeutron(None)
        self.set('FormFactor', formfactor)


        return

ScatterFactorNeutron.ParamDict.update(ScatterFactor.ParamDict)
ScatterFactorNeutron.ObjectDict.update(ScatterFactor.ObjectDict)
ScatterFactorNeutron.ObjectListDict.update(ScatterFactor.ObjectListDict)



class FormFactor(RietveldClass):
    """
    Form factor interface
    """

    ParamDict = {}
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        interface initialization
        """
        RietveldClass.__init__(self, parent)

        return


    def validate(self):
        """
        validate the parameters, subclass and container to meet the refinement requirement
        """ 
        rvalue = RietveldClass.validate(self)

        if self.__class__.__name__ == "FormFactor":
            print "base class FormFactor is not allowed"
            rvalue = False

        return rvalue




class FormFactorXray(FormFactor):
    """
    Form factor for X-ray
    """
    ParamDict = {
        "A1":   FloatInfo("A1", "A1", 0.0),
        "B1":   FloatInfo("B1", "B1", 0.0),
        "A2":   FloatInfo("A2", "A2", 0.0),
        "B2":   FloatInfo("B2", "B2", 0.0),
        "A2":   FloatInfo("A3", "A3", 0.0),
        "B3":   FloatInfo("B3", "B3", 0.0),
        "A4":   FloatInfo("A4", "A4", 0.0),
        "B4":   FloatInfo("B4", "B4", 0.0),
        "C":    FloatInfo("C",  "C",  0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        inheriting initialization
        """
        FormFactor.__init__(self, parent)

        return

FormFactorXray.ParamDict.update(FormFactor.ParamDict)
FormFactorXray.ObjectDict.update(FormFactor.ObjectDict)
FormFactorXray.ObjectListDict.update(FormFactor.ObjectListDict)



class FormFactorNeutron(FormFactor):
    """
    Form factor for X-ray
    """
    ParamDict = {
        "A":    FloatInfo("A", "A", 0.0),
        "B":    FloatInfo("B", "B", 0.0),
        "C":    FloatInfo("C", "C",  0.0),
        "D":    FloatInfo("D", "D",  0.0),
        "a":    FloatInfo("a", "a",  0.0),
        "b":    FloatInfo("b", "b",  0.0),
        "c":    FloatInfo("c", "c",  0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        inheriting initialization
        """
        FormFactor.__init__(self, parent)

        return

FormFactorNeutron.ParamDict.update(FormFactor.ParamDict)
FormFactorNeutron.ObjectDict.update(FormFactor.ObjectDict)
FormFactorNeutron.ObjectListDict.update(FormFactor.ObjectListDict)



class FormFactorTable(FormFactor):
    """
    Form factor for X-ray
    """
    ParamDict = {}
    ObjectDict  = {}
    ObjectListDict = {
        "FormfactorUserdefined":    ObjectInfo("SetFormfactorUserdefined", "FormfactorUserdefined", 0, None),
    }

    def __init__(self, parent):
        """
        inheriting initialization
        """
        FormFactor.__init__(self, parent)

        return

FormFactorTable.ParamDict.update(FormFactor.ParamDict)
FormFactorTable.ObjectDict.update(FormFactor.ObjectDict)
FormFactorTable.ObjectListDict.update(FormFactor.ObjectListDict)



class FormfactorUserdefined(RietveldClass):
    """
    a single set of user-defined form factor in form factor table
    """
    ParamDict = {
        "A":    FloatInfo("A", "A = sin(theta)/lambda", 0.0),
        "a":    FloatInfo("a", "a = form formfactor", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initalization
        """
        RietveldClass.__init__(self, parent)

        return



# LP factor
class LPFactor(RietveldClass):
    """
    class to handle all the related parameters for Lorentz polarization

    attributes
    Ilo
    Cthm
    Rpolarz
    """
    ParamDict = {
        "Ilo":      EnumInfo("Ilo", "Lorentz and polarization corrections", 0,
                    {0: "Standard Debye-Scherrer Geometry",
                    1:  "Flat Plate PSD Geometry",
                    -1: "No Correction",
                    2:  "Transmission Geometry",
                    3:  "Special Polarization Correction"},
                    [-1, 0, 1, 2, 3]),
        "Cthm":     FloatInfo("Cthm", "Monochromator Polarization Correction", 0.0),
        "Rpolarz":  FloatInfo("Rpolarz", "Polarization Factor", 0.0),
    }
    ObjectDict  = {}
    ConstrainDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return

# End of class LPFactor

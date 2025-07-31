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
from builtins import str
__id__ = "$Id: contribution.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.rietveldclass import RietveldClass
from diffpy.pyfullprof.infoclass import EnumInfo
from diffpy.pyfullprof.infoclass import FloatInfo
from diffpy.pyfullprof.infoclass import IntInfo
from diffpy.pyfullprof.infoclass import RefineInfo
from diffpy.pyfullprof.infoclass import ObjectInfo
from diffpy.pyfullprof.infoclass import StringInfo
from diffpy.pyfullprof.exception import RietError

class Contribution(RietveldClass):
    """
    Class Contribution is a short for "phase contribution to pattern"
    It is an semi-independent class to Phases and Patterns

    attributes list:
    - _ParentPattern
    - _ParentPhase
    """


    ParamDict = {
        "Irf":      EnumInfo("Irf", "reflection generation", 0,
                    {0: "automatically generated from space group",
                    1:  "list (h,k,l, Mult) read from file CODFILn.hkl",
                    -1: "satellite reflections generated automatically from the given space group symbol",
                    2:  "list (h,k,l,Mult,Intensity) is read from file CODFILn.hkl",
                    3:  "list (h,k,l,Mult,F_real,F_imag) read from file CODFILn.hkl",
                    4:  "a list of integrated intensities given as observatoins",
                    -4: "a list of integrated intensities given as observatoins"},
                    [0, 1, -1, 2, 3, 4, -4]),
         "Jtyp":     EnumInfo("Jtyp", "Job type of phase (model)", 0,
                    {0: "treated with Rietveld method, refining a given structural model",
                    1:  "treated with Rietveld method, pure magnetic",
                    -1: "treated with Rietveld method, pure magentic with magnetic moments",
                    2:  "profile matching method with constant scale factor",
                    -2: "profile matching method with constant scale factor and given CODFiln.hkl",
                    3:  "profile matching method with constant relative intensities for the current phase",
                    -3: "profile matching method with given structure factor in CODFiln.hkl",
                    4:  "intensities of nuclear reflection from Rigid body groups",
                    5:  "intensities of magnetic reflection from conical magnetic structure in real space",
                    10: "nuclear and magnetic phase with Cartesian magnetic moment",
                    -10:"nuclear and magnetic phase with spherical magnetic moment",
                    15: "commensurate modulated crystal structure with Cartesian magnetic components",
                    -15:"commensurate modulated crystal structure with spherical magnetic components"},
                    [0,1,-1,2,-2,3,-3,4,5,10,-10,15,-15]),
        "Rmua":     FloatInfo("Rmua", "integrated intensity data weight", 1.0, "%"),
        "Rmub":     FloatInfo("Rmub", "exclusion of low statistic reflection in integrated inetensity data sets", 1.0),
        "Rmuc":     FloatInfo("Rmuc", "Chi2 dependent weighting of integrated data sets", 1.0,),
        "Brind":    FloatInfo("Brind", "Brindley coefficient", 0.0),
        "Scale":    RefineInfo("Scale", "Scale factor", 1.0E-3),
        "Bov":      RefineInfo("Bov", "Overall isotropic displacement parameter", 0.0),
        "SizeModelSelector":    EnumInfo("SizeModelSelector", "Size Model Selector", 0,
                        {0: "No Specific Size",
                        -1: "",
                        1:  "",
                        -2: "",
                        15: "Laue class 2/m", 
                        16: "Laue class -3 m H",
                        17: "Laue class m3, m3m, Cubic harmonics", 
                        18: "Laue class mmm",
                        19: "Laue classes: 6/m, 6/mmm. For 6/mmm Y66-=0, not implemented yet",
                        20: "Laue class: -3 H, not implemented",
                        21: "Laue classes: 4/m, 4/mmm. For 4/mmm Y44-=0 and Y64=0, not implemented",
                        22: "Laue class: -1, not implemented",
                        },
                        [0, 1, -1, -2, 15, 16, 17, 18, 19, 20, 21, 22]),
        "Nsp_Ref":  IntInfo("Nsp_Ref", "NSP reference...", 0),
        "Ph_Shift": IntInfo("Ph_Shift", "phase shift", 0),
    }

    ObjectDict  = {
        "PreferOrient":     ObjectInfo("PreferOrient", "PreferOrient"),
        "Profile":          ObjectInfo("Profile", "Profile"),
        "SizeModel":        ObjectInfo("SizeModel", "SizeModel"),
        "ShiftParameter":   ObjectInfo("ShiftParameter", "ShiftParameter"),
        "StrainParameter":  ObjectInfo("StrainParameter", "StrainParameter"),
    }

    ObjectListDict = {
        "SpecialReflection":    ObjectInfo("SetSpecialReflection", "SpecialReflection", 0, None),
    }


    def __init__(self, parent, parentpattern=None, parentphase=None):
        """
        initialization
        """
        from diffpy.pyfullprof.pattern import Pattern
        from diffpy.pyfullprof.phase import Phase

        RietveldClass.__init__(self, parent)

        # parent check
        if parentpattern is not None:
            self.setParentPattern(parentpattern)
        else:
            self._ParentPattern = None

        if parentphase is not None:
            self.setParentPhase(parentphase)
        else:
            self._ParentPhase = None

        # init subclass 
        profile = Profile(self)
        self.set("Profile", profile)

        shiftparameter = ShiftParameter(self)
        self.set("ShiftParameter", shiftparameter)

        strainparameter = StrainParameter(self)
        self.set("StrainParameter", strainparameter)

        sizemodel = SizeModel(self)
        self.set("SizeModel", sizemodel)

        preferorient = PreferOrient(self)
        self.set("PreferOrient", preferorient)

        return


    def extendOrphan(self, baseobj):
        """ extend a base-object to 'self', and replace base-object with 'self' in 
        Rietveld-class hierachy
        baseobj = base object
        this object or the baseobj may be Orphan, since its Parent is allowed to be None
        some manual setup is required later

        Extending the base class: RietveldClass.extendOrphan()

        Argument:
          - baseobj :  a referenc to an instance which is of the base class of current instance

        Return  :   Rietveld object
        """
        if baseobj._ParentPattern != None:
            baseobj._ParentPattern._contributionlist.remove(baseobj)

        if baseobj._ParentPhase != None:
            baseobj._ParentPhase._contributionlist.remove(baseobj)

        rvalue = RietveldClass.extendOrphan(self, baseobj)

        return rvalue


    def getParentPhase(self):
        """
        return the parent phase of this contribution
        """

        return self._ParentPhase


        RietveldClass.extendOrphan(self, baseobj)



    def validate(self):
        """
        validate the parameters, subclass and container to meet the refinement requirement
        """
        rvalue = RietveldClass.validate(self)
        
        # parent check
        if self._ParentPattern is None:
            raise RietError("Contribution.validate()   _ParentPattern = None")

        if self._ParentPhase   is None:
            raise RietError("Contribution.validate()   _ParentPhase   = None")

        # type check
        name = self.__class__.__name__
        if name == "Contribution":
            errmsg =  "base class Contribution is not allowed"
            raise NotImplementedError(errmsg)

        if rvalue is not True:
            print("Invalidity Deteced In %-10s"% (self.__class__.__name__))

        return rvalue


    def getParentPattern(self):
        """
        return the parent pattern of this contribution
        """
        
        return (self._ParentPattern)


    def getParentPhase(self):
        """
        return the parent phase of this contribution
        """

        return self._ParentPhase

    def getPhaseIndex(self):
        """return the phase index of the contribution.
        """
        phaselist = self.parent.get("Phase")
        phaseindex = phaselist.index(self._ParentPhase)
        return phaseindex

    def getPatternIndex(self):
        """return the pattern index of the contribution.
        """
        patternlist = self.parent.get("Pattern")
        patternindex = patternlist.index(self._ParentPattern)
        return patternindex

    def setParentPattern(self, parentpattern):
        """
        return the parent pattern of this contribution
        """
        from diffpy.pyfullprof.pattern import Pattern

        if isinstance(parentpattern, Pattern):
            self._ParentPattern = parentpattern
            self._ParentPattern.addContribution(self)
        else:
            raise RietError("Contribution.setParentPattern(): incorrect input pattern")

        # synchronize Jtyp
        self.set("Jtyp", self._ParentPattern.get("Job"))

        return 


    def setParentPhase(self, parentphase):
        """
        return the parent phase of this contribution
        """
        from diffpy.pyfullprof.phase import Phase
        if isinstance(parentphase, Phase):
            self._ParentPhase = parentphase
            parentphase.addContribution(self)
        else:
            raise RietError("Contribution.setParentPhase(): incorrect input phase")

        return 


    def setPhaseFraction(self, phasefraction, uncertainty):
        """ Set the phase fraction of the phase related to this Contribution
        to all the phases related to the Pattern related to this Contribution

        Phase fraction here is the fraction of phase weight

        Argument
          - phasefraction   :   float (0 < X < 100) as percent
          - uncertainty     :   float
        
        Return  :   None
        """
        if phasefraction >= 0.0 and phasefraction <= 100.0:
            self._phasefraction = phasefraction
            self._phasefractionuncertainty = uncertainty
        else:
            errmsg = "Not allowed to set up a phase fraction %-15s out of range [0.0, 1.0]" \
                    % phasefraction
            raise_(RietError, errmsg)

        return


    def getPhaseFraction(self):
        """ Get the fraction of the phase as the parent of this Contribution
        to all the phases related to a Pattern as the parent of this Contribution
        
        Phase fraction here is the fraction of phase weight

        Return  :   2-tuple of float
        """
        return ( (self._phasefraction, self._phasefractionuncertainty) )




class Contribution2Theta(Contribution):
    """
    Contribution2Theta inherits from Contribution, applied dedicated to 2theta data
    """

    ParamDict = {
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
    }
    ObjectDict  = {
        "AsymmetryParameter":   ObjectInfo("AsymmetryParameter", "AsymmetryParameter"),
    }

    def __init__(self, parent, parentpattern=None, parentphase=None):
        """
        initialization
        """
        Contribution.__init__(self, parent, parentpattern, parentphase)

        asymmetryparameter = AsymmetryParameter(self)
        self.set("AsymmetryParameter", asymmetryparameter)

        return


    def set(self, param_name, value, index=None):
        """
        override the base class's set() method in order to make 
        (1) AsymmetryParameter is in accordance with self.Npr

        return  --  bool, True/False
        """
        # call base class method
        rvalue = Contribution.set(self, param_name, value, index)
        
        # 0. set Profile
        if param_name == "Profile":
            if isinstance(value, Profile2ThetaNonSPV):
                self.set("Npr", 7)
        # 1. initialize AsymmetryParameter
        if param_name == "Npr":
            asymparam = self.get("AsymmetryParameter")
            if value != 7:
                if asymparam is None or isinstance(asymparam, AsymmetryParameterTCH):
                    newasymparam = AsymmetryParameter(self)
                    self.set("AsymmetryParameter", newasymparam)
            else:
                if asymparam is None:
                    newasymparam = AsymmetryParameterTCH(self)
                    self.set("AsymmetryParameter", newasymparam)
                elif not isinstance(asymparam, AsymmetryParameterTCH):
                    newasymparam = AsymmetryParameterTCH(self)
                    newasymparam.extend(asymparam)
            """ --- end if value != 7  """
        """ --- end if param_name == Npr """

        return rvalue

Contribution2Theta.ParamDict.update(Contribution.ParamDict)
Contribution2Theta.ObjectDict.update( Contribution.ObjectDict)
Contribution2Theta.ObjectListDict.update(Contribution.ObjectListDict)


class ContributionTOF(Contribution):
    """
    ContributionTOF inherits from Contribution, applied dedicated to T.O.F data
    """

    ParamDict = {
        "LStr":     RefineInfo("LStr", "Lorentzian isotropic strain", 0.0),
        "LSiz":     RefineInfo("LSiz", "LSiz", 0.0),
        "Extinct":  RefineInfo("Extinct", "extinction parameter for powders", 0.0),
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
        "ABS1":     RefineInfo("ABS1", "ABS1 absorption correction parameter", 0.0),
        "ABS2":     RefineInfo("ABS2", "ABS2 absorption correction parameter", 0.0),
    }
    ObjectDict  = {
        "ExpDecayFunction": ObjectInfo("ExpDecayFunction", "ExpDecayFunction"),
    }
    ObjectListDict = {}

    def __init__(self, parent, parentpattern=None, parentphase=None):
        """
        initialization
        """
        Contribution.__init__(self, parent, parentpattern, parentphase)

        # initialize subclass
        expdecayfunction = ExpDecayFunction(self)
        self.set("ExpDecayFunction", expdecayfunction)

        return


    def set(self, param_name, value, index=None):
        """
        override the base class's set() method in order to cooperate
        some features in this class

        1. if Npr = 10, then initialize ExpDecayFunction

        """
        # call base class set()
        rvalue = Contribution.set(self, param_name, value, index)
        # set Profile
        # wz: do not know why needs to set up Npr while setting "Profile"
        #     temporarily turn off this function for POWGEN data 
        # if param_name == "Profile":
        #     mypattern = self.getPattern()
        #     if isinstance(mypattern, PatternTOFThermalNeutron)
        #         self.set("Npr", 10)
        #     elif isinstance(mypattern, PatternTOF)
        #         self.set("Npr", 9)
        
        # special handling
        if param_name == "Npr":
            # expnential decay
            expdecay = self.get("ExpDecayFunction")

            if value != 10:
                # general case
                if expdecay is None or isinstance(expdecay, ExpDecayFunctionThermo):
                    newexpdecay = ExpDecayFunction(self)
                    self.set("ExpDecayFunction", newexpdecay)

            else:
                # special case
                if expdecay is None:
                    newexpdecay = ExpDecayFunctionThermo(self)
                    self.set("ExpDecayFunction", newexpdecay)
                elif not isinstance(expdecay, ExpDecayFunctionThermo):
                    newexpdecay = ExpDecayFunctionThermo(self)
                    newexpdecay.extend(expdecay)

            """ --- if value != 10 """
        """ --- if param_name == "Npr" ... """

        return rvalue

ContributionTOF.ParamDict.update(Contribution.ParamDict)
ContributionTOF.ObjectDict.update( Contribution.ObjectDict)
ContributionTOF.ObjectListDict.update(Contribution.ObjectListDict)


"""
Profile Suite
"""

class Profile(RietveldClass):
    """
    base class for profile
    """

    ParamDict = {
        "Shape1":   RefineInfo("Shape1", "profile shape parameter",  0.0),
        "Wdt":      FloatInfo("Wdt", "Cut-off of the peak profile tails", 8.0),
    }
    ObjectDict  = {}
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

        # type check
        name = self.__class__.__name__
        if name == "Profile":
            print("base class Profile is not allowed")
            rvalue = False

        return rvalue



class Profile2Theta(Profile):
    """
    extending profile, 
    base class for profile of 2theta data
    contribution 
    - container to 2ndWave object
    """
    ParamDict = {"Shape1":   RefineInfo("Shape1", "profile shape parameter", 0.0),
                 "GausSiz":  RefineInfo("GausSiz", "isotropic size parameter of Gaussian character", 0.0),
                 "LorSiz":   RefineInfo("LorSiz", "anisotropic Lorentzian contribution of particle size", 0.0),
                    
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
                    
    }
    ObjectDict  = {}
    ObjectListDict = {
        "Profile2ndWave":   ObjectInfo("SetProfile2ndWave", "Profile2ndWave", 0, 1),
    }


    def __init__(self, parent):
        """
        initialization
        """

        Profile.__init__(self, parent)

        return

Profile2Theta.ParamDict.update(Profile.ParamDict)
Profile2Theta.ObjectDict.update( Profile.ObjectDict)
Profile2Theta.ObjectListDict.update(Profile.ObjectListDict)



class ProfileTOF(Profile):
    """
    extending profile for time-of-flight pattern, 
    base class for profile of TOF data
    contribution 
    - container to 2ndWave object
    """
    ParamDict = {
        "Sig2": RefineInfo("Sig2", "variance Sig2", 0.0),
        "Sig1": RefineInfo("Sig1", "variance Sig1", 0.0),
        "Sig0": RefineInfo("Sig0", "variance Sig0", 0.0),
        "Z1":   RefineInfo("Z1", "Gaussian isotropic size", 0.0),
        "Gam2": RefineInfo("Gam2", "FWHM Gam2", 0.0),
        "Gam1": RefineInfo("Gam1", "FWHM Gam1", 0.0),
        "Gam0": RefineInfo("Gam0", "FWHM Gam0", 0.0),
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
    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """
        initialization
        """
        Profile.__init__(self, parent)

        return

ProfileTOF.ParamDict.update(Profile.ParamDict)
ProfileTOF.ObjectDict.update( Profile.ObjectDict)
ProfileTOF.ObjectListDict.update(Profile.ObjectListDict)


class Profile2ThetaNonSPV(Profile2Theta):
    """
    extending profile2theta for Npr = 7
    attributes
    - U
    - V
    - W
    """
    ParamDict = {
        "U":    RefineInfo("U", "U", 0.0),
        "V":    RefineInfo("V", "V", 0.0),
        "W":    RefineInfo("W", "W", 0.0),
        "X":    RefineInfo("X", "X Lorentzian isotropic strain", 0.0),
        "Y":    RefineInfo("Y", "Y Lorentzian isotropic strain", 0.0),
        "SHP1": RefineInfo("SHP1", "Additional Peak Profile Parameter 1", 0.0),
        "SHP2": RefineInfo("SHP2", "Additional Peak Profile Parameter 2", 0.0),
        "Parameters": StringInfo("Parameters", "The list of parameter names in this profile function", 
                                 "U V W X Y SHP1 SHP2"),
    }
    ObjectDict  = {}
    ObjectListDict = {
    }


    def __init__(self, parent):
        """
        initialization
        """
        Profile2Theta.__init__(self, parent)

        return

Profile2ThetaNonSPV.ParamDict.update(Profile2Theta.ParamDict)
Profile2ThetaNonSPV.ObjectDict.update( Profile2Theta.ObjectDict)
Profile2ThetaNonSPV.ObjectListDict.update(Profile2Theta.ObjectListDict)



class Profile2ThetaSPV(Profile2Theta):
    """
    extending profile2theta
    attributes
    - U
    - V
    - W
    """
    ParamDict = {
        "UL":    RefineInfo("UL", "UL", 0.0),
        "VL":    RefineInfo("VL", "VL", 0.0),
        "WL":    RefineInfo("WL", "WL", 0.0),
        "XL":    RefineInfo("XL", "XL", 0.0),
        "UR":    RefineInfo("UR", "UR", 0.0),
        "VR":    RefineInfo("VR", "VR", 0.0),
        "WR":    RefineInfo("WR", "WR", 0.0),
        "XR":    RefineInfo("XR", "XR", 0.0),
        "Eta0r": RefineInfo("Eta0r", "Eta0r", 0.0),
        "SHP1":  RefineInfo("SHP1", "Shape1 in Split PseudoVoigt", 0.0),
        "SHP2":  RefineInfo("SHP2", "Shape2 in Split PseudoVoigt", 0.0),
        "Parameters": StringInfo("Parameters", "The list of parameter names in this profile function", 
                                 "UL VL WL XL UR VR WR Eta0r SHP1 SHP2"),
    }
    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """
        initialization
        """
        Profile.__init__(self, parent)

        return

Profile2ThetaSPV.ParamDict.update(Profile2Theta.ParamDict)
Profile2ThetaSPV.ObjectDict.update( Profile2Theta.ObjectDict)
Profile2ThetaSPV.ObjectListDict.update(Profile2Theta.ObjectListDict)



class Profile2ndWave(RietveldClass):
    """
    for 2nd wavelength, optional
    attributes
    - U2
    - V2
    - W2
    """


    ParamDict = {
        "U2":   RefineInfo("U2", "U2", 0.0), 
        "V2":   RefineInfo("V2", "V2", 0.0), 
        "W2":   RefineInfo("W2", "W2", 0.0),
        "Parameters": StringInfo("Parameters", "The list of parameter names in this profile function", 
                                 "U2 V2 W2"),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        
        RietveldClass.__init__(self, parent)

        return


"""     Preferred Orientation Suite     """

class PreferOrient(RietveldClass):
    """
    base class for preferred orientatation
    attributes:
    - Pref1
    - Pref2
    """
    

    ParamDict = {
        "Pr1":      FloatInfo("Pr1", "preferred orientation direction - 1", 1.0),
        "Pr2":      FloatInfo("Pr1", "preferred orientation direction - 2", 0.0),
        "Pr3":      FloatInfo("Pr1", "preferred orientation direction - 3", 0.0),
        "Pref1":    RefineInfo("Pref1", "G1", 0.0),
        "Pref2":    RefineInfo("Pref2", "G2", 0.0),
        "Parameters": StringInfo("Parameters", "The list of parameter names in this profile function", 
                                 "Pr1 Pr2 Pr3 Pref1 Pref2"),
    }

    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        
        RietveldClass.__init__(self, parent)

        return


    def validate(self):
        """
        validate the parameters, subclass and container to meet the refinement requirement
        """
        rvalue = RietveldClass.validate(self)

        # make Nor consistent
        pattern = self.parent.getParentPattern()
        if pattern.get("Nor") != 0 and pattern.get("Nor") != 1:
            self.set("Pref1", 1.0)

        return rvalue



class AsymmetryParameter(RietveldClass):
    """
    asymmetry parameters for 2theta pattern
    attribute:
    - PA1
    - PA2
    - PA3
    - PA4
    """

    ParamDict = {
        "PA1":  RefineInfo("PA1", "P_1", 0.0),
        "PA2":  RefineInfo("PA2", "P_2", 0.0),
        "PA3":  RefineInfo("PA3", "P_3", 0.0),
        "PA4":  RefineInfo("PA4", "P_4", 0.0),
    }

    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return




class AsymmetryParameterTCH(AsymmetryParameter):
    """
    preferred orientation for 2theta pattern with the profile
    Thompson-Cox-Hastings pseudo-Voigt convoluted with axial divergence asymmetry function

    TCV = Thompson-Cox-Hasting

    attribute:
    S_L --  RefineData
    D_L --  RefineData
    """

    ParamDict = {
        "S_L":  RefineInfo("S_L", "S_L", 0.00),
        "D_L":  RefineInfo("D_L", "D_L", 0.00),
    }

    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        AsymmetryParameter.__init__(self, parent)

        return

AsymmetryParameterTCH.ParamDict.update(AsymmetryParameter.ParamDict)
AsymmetryParameterTCH.ObjectDict.update( AsymmetryParameter.ObjectDict)
AsymmetryParameterTCH.ObjectListDict.update(AsymmetryParameter.ObjectListDict)



class ExpDecayFunction(RietveldClass):
    """
    Exponential decay function for T.O.F.

    attributes:
    - ALPH0
    - ALPH1
    - BETA0
    - BETA1
    """

    ParamDict = {
        "ALPH0":    RefineInfo("ALPH0", "Alaph0, exponential decay", 0.0), 
        "ALPH1":    RefineInfo("ALPH1", "Alaph1, exponential decay", 0.0), 
        "BETA0":    RefineInfo("BETA0", "Beta0,  exponential decay", 0.0), 
        "BETA1":    RefineInfo("BETA1", "Beta1,  exponential decay", 0.0), 
    }
    
    ObjectDict  = {}
    ObjectListDict = {}
    
    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return




class ExpDecayFunctionThermo(ExpDecayFunction):
    """
    Exponential decay function for T.O.F. with Npr=10, considering thermo neutrons

    attributes:
    - ALPH0T
    - ALPH1T
    - BETA0T
    - BETA1T
    """

    ParamDict = {
        "ALPH0T":   RefineInfo("ALPH0T", "Alaph0, exponential decay for thermal component", 0.0), 
        "ALPH1T":   RefineInfo("ALPH1T", "Alaph1, exponential decay for thermal component", 0.0), 
        "BETA0T":   RefineInfo("BETA0T", "Beta0,  exponential decay for thermal component", 0.0), 
        "BETA1T":   RefineInfo("BETA1T", "Beta1,  exponential decay for thermal component", 0.0), 
    }
    
    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        initialization
        """
        ExpDecayFunction.__init__(self, parent)

        return

ExpDecayFunctionThermo.ParamDict.update(ExpDecayFunction.ParamDict)
ExpDecayFunctionThermo.ObjectDict.update( ExpDecayFunction.ObjectDict)
ExpDecayFunctionThermo.ObjectListDict.update(ExpDecayFunction.ObjectListDict)



"""     Shift Model Suite   """

class ShiftParameter(RietveldClass):
    """
    base class of shift parameter

    attribute
    - ModS
    - ModSType
    - SHF1
    - SHF2
    - SHF3
    """


    ParamDict = {
        "ModS":     IntInfo("ModS", "hkl-dependent model", 0),
        "ModSType": EnumInfo("ModSType", "hkl-dependent shift parameter", 1,
                    {1: "shift due to a specific reciprocal direction - cos(phi) dependence",
                    -1: "shift due to a specific reciprocal direction - sin(phi) dependence",
                    -2: "user defined selective shift for specific (hkl) reflection",
                    101:"generalized shift formulation up to quartic form"},
                    [1, -1, -2, 101]),
        "SHF1":     RefineInfo("SHF1", "SHF1", 0.0),
        "SHF2":     RefineInfo("SHF2", "SHF2", 0.0),
        "SHF3":     RefineInfo("SHF3", "SHF3", 0.0),
    }

    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        initialization

        - parent
        """
        RietveldClass.__init__(self, parent)

        return



class ShiftParameterAngle(ShiftParameter):
    """
    shift parameter with angle

    attributes 
    - sh1
    - sh2
    - sh3
    """

    ParamDict = {
        "Function": EnumInfo("Function", "function for phi", "cos",
                            {"cos": "cos(phi)",
                            "sin":  "sin(phi)"},
                            ["cos", "sin"]),
        "Sh1":      FloatInfo("Sh1", "Sh1", 0.0),
        "Sh2":      FloatInfo("Sh2", "Sh2", 0.0),
        "Sh3":      FloatInfo("Sh3", "Sh3", 0.0),
    }
   
    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """
        initialization
        """

        ShiftParameter.__init__(self, parent)

        return


ShiftParameterAngle.ParamDict.update(ShiftParameter.ParamDict)
ShiftParameterAngle.ObjectDict.update( ShiftParameter.ObjectDict)
ShiftParameterAngle.ObjectListDict.update(ShiftParameter.ObjectListDict)


class ShiftParameterUserdefined(ShiftParameter):
    """
    shift parameter with user defined selective shifts for specific (hkl) reflections
    """

    ParamDict = {}

    ObjectDict  = {}
    ObjectListDict = {
        "SelectiveShift":   ObjectInfo("SetSelectiveShift", "SelectiveShift", 0, None),
    }

    def __init__(self, parent):
        """
        initialization
        """

        ShiftParameter.__init__(self, parent)

        return

ShiftParameterUserdefined.ParamDict.update(ShiftParameter.ParamDict)
ShiftParameterUserdefined.ObjectDict.update( ShiftParameter.ObjectDict)
ShiftParameterUserdefined.ObjectListDict.update(ShiftParameter.ObjectListDict)



class ShiftParameterLaue(ShiftParameter):
    """
    shift parameter with user defined selective shifts for specific (hkl) reflections
    """

    ParamDict = {
        "Laueclass":    EnumInfo("Laueclass", "Laue class", "-1",
                            {"-1":      "-1",
                            "1 2/m 1":  "1 2/m 1",
                            "1 1 2/m":  "1 1 2/m",
                            "mmm":      "mmm",
                            "4/m":      "4/m",
                            "4/mmm":    "4/mmm",
                            "-3R":      "-3R",
                            "-3m R":    "-3m R",
                            "-3H":      "-3H",
                            "-3m1":     "-3m1",
                            "-31m":     "-31m"},
                            ["-1", "1 2/m 1", "1 1 2/m", "mmm", "4/m", "4/mmm", "-3R", "-3m R", "-3H", "-3m1", "-31m"]),
    }

    ObjectDict  = {}
    ObjectListDict = {
        "GeneralShift":   ObjectInfo("SetGeneralShift", "GeneralShift", 0, None),
    }

    def __init__(self, parent, laueclass=None):
        """
        initialization

        laueclass:  candidate laue class
        """

        ShiftParameter.__init__(self, parent)

        if laueclass is not None:
            self.set("Laueclass", laueclass)

        return

   
    def get(self, param_name, condition=None):
        """
        extending base class's get(), but treat a special parameter (h, k, l) as "hkl"

        param_name: parameter name
        condition:  a value for a param_name to be equal to

        Example:
        get("hkl", (0, 2, 2)):  return a GeneralShift with (0, 2, 2) as HKL
        """
        if param_name == "hkl":
            for gshift in self.get("GeneralShift"):
                if gshift.get("H") == condition[0] and gshift.get("K") == condition[1] \
                        and gshift.get("L") == condition[2]:
                    return gshift
            print("this shift parameter doesn't contain a general shift (%-10s)"%(condition))
            return None
        else:
            return ShiftParameter.get(self, param_name)


ShiftParameterLaue.ParamDict.update(ShiftParameter.ParamDict)
ShiftParameterLaue.ObjectDict.update( ShiftParameter.ObjectDict)
ShiftParameterLaue.ObjectListDict.update(ShiftParameter.ObjectListDict)


class SelectiveShift(RietveldClass):
    """
    selective shfit for specific (hkl) reflection

    attribute:
    - Shift
    - n1
    - n2
    - n3
    - n4
    - n5
    """


    ParamDict = {
        "Shift":    RefineInfo("Shift", "shift parameter", 0.0),
        "n1":        IntInfo("n1", "user-defined shift rule n1", 0),
        "n2":        IntInfo("n2", "user-defined shift rule n2", 0),
        "n3":        IntInfo("n3", "user-defined shift rule n3", 0),
        "n4":        IntInfo("n4", "user-defined shift rule n4", 0),
        "n5":        IntInfo("n5", "user-defined shift rule n5", 0),
    }

    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        initialization
        """

        RietveldClass.__init__(self, parent)

        return



class GeneralShift(RietveldClass):
    """
    general shift due to laue class

    attribute
    - D
    - N
    - H
    - K
    - L
    """


    ParamDict = {
        "D":    RefineInfo("D", "shift value", 0.0),
        "N":    EnumInfo("N", "N", 2,
                        {2: "2",
                        4:  "4"},
                        [2, 4]),
        "H":    IntInfo("H", "H", 0),
        "K":    IntInfo("K", "K", 0),
        "L":    IntInfo("L", "L", 0),
    }

    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent, hkl = None):
        """
        initialization

        hkl:  a 3-integer-tuple (h, k, l)
        """

        RietveldClass.__init__(self, parent)

        if hkl is not None:
            self.set("H", hkl[0])
            self.set("K", hkl[1])
            self.set("L", hkl[2])

        return
        


"""     Size Model Suite    """

class SizeModel(RietveldClass):
    """
    base class for SizeModel
    
    attribute
    """


    ParamDict = {}
    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return



class SizeModelCylindrical(SizeModel):
    """
    size model for cylindrical sample

    attribute
    - Sz1
    - Sz2
    - Sz3
    """


    ParamDict = {
        "Sz1":  RefineInfo("Sz1", "vector defined the platelet Sz1", 0.0),
        "Sz2":  RefineInfo("Sz2", "vector defined the platelet Sz2", 0.0),
        "Sz3":  RefineInfo("Sz3", "vector defined the platelet Sz3", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        SizeModel.__init__(self, parent)

        return

SizeModelCylindrical.ParamDict.update(SizeModelCylindrical.ParamDict)
SizeModelCylindrical.ObjectDict.update( SizeModelCylindrical.ObjectDict)
SizeModelCylindrical.ObjectListDict.update(SizeModelCylindrical.ObjectListDict)


class SizeModelGeneral(SizeModel):
    """
    size model for cylindrical sample

    attribute
    - Sz1
    - Sz2
    - Sz3
    """


    ParamDict = {
        "SZ1":  RefineInfo("SZ1", "vector defined the platelet SZ1", 0.0),
        "SZ2":  RefineInfo("SZ2", "vector defined the platelet SZ2", 0.0),
        "SZ3":  RefineInfo("SZ3", "vector defined the platelet SZ3", 0.0),
        "SZ4":  RefineInfo("SZ4", "vector defined the platelet SZ4", 0.0),
        "SZ5":  RefineInfo("SZ5", "vector defined the platelet SZ5", 0.0),
        "SZ6":  RefineInfo("SZ6", "vector defined the platelet SZ6", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        SizeModel.__init__(self, parent)

        return

SizeModelGeneral.ParamDict.update(SizeModelGeneral.ParamDict)
SizeModelGeneral.ObjectDict.update( SizeModelGeneral.ObjectDict)
SizeModelGeneral.ObjectListDict.update(SizeModelGeneral.ObjectListDict)


class SizeModelDefect(SizeModel):
    """
    size model for user-defined selective (hkl) size broadening due to defects
    """

    ParamDict = {}
    ObjectDict  = {}
    ObjectListDict = {
        "DefectSizeBroaden":    ObjectInfo("SetDefectSizeBroaden", "DefectSizeBroaden", 1, 9),
    }

    
    def __init__(self, parent):
        """
        initalization
        """
        SizeModel.__init__(self, parent)

        return
    
SizeModelDefect.ParamDict.update(SizeModelDefect.ParamDict)
SizeModelDefect.ObjectDict.update( SizeModelDefect.ObjectDict)
SizeModelDefect.ObjectListDict.update(SizeModelDefect.ObjectListDict)


class SizeModelSpherical(SizeModel):
    """
    spherical harmonics expansion of the crystallites shape
    """

    ParamDict = {
        "Laueclass":    EnumInfo("Laueclass", "Laue class", "2/m",
                        {"2/m":     "2/m",
                        "-3 m H":   "-3 m H",
                        "m3m":      "m3m",
                        "mmm":      "mmm",
                        "6/m":      "6/m",
                        "6/mmm":    "6/mmm",
                        "-3H":      "-3H",
                        "4/mmm":    "4/mmm",
                        "4/m":      "4/m",
                        "-1":       "-1"},
                        ["2/m", "-3 m H", "m3m", "mmm", "6/m", "6/mmm", "-3H", "4/mmm", "4/m", "-1"]),
    }
    ObjectDict  = {}
    ObjectListDict = {
        "SHcoefficient":    ObjectInfo("SetSHcoefficient", "SHcoefficient", 1, None),
    }

    
    def __init__(self, parent, laueclass=None):
        """
        initalization
        """
        SizeModel.__init__(self, parent)

        if laueclass is not None:
            self.set("Laueclass", laueclass)

        return


    def addSphericalHarmonic(self, name):
        """
        generate a spherical harmonic coefficent value 
        and add to this size model 

        Arguements:
        name    :   string, name of this spherical harmonic KLM[+/-] or YLM[+/-]

        Return  --  SHcoefficient instance
        """
        #  1. get name
        ky = name[0]
        l  = int(name[1])
        m  = int(name[2])
        if len(name) > 3 and (name[3] == "+" or name[3] == "-"):
            s = name[3]
        else:
            s = ""

        #  2. check exist
        if self._getSHC(ky, l, m, s) is not None:
            errmsg = "addSphericalHarmonic():  Spherical Harmonic %-10s Has Existed"% (name)
            raise RietError(errmsg)

        #  3. generate SHcoefficient object
        shc = SHcoefficient(None)
        self.set("SHcoefficient", shc)

        # 4. setK or setY
        if ky == "K":
            shc.setK(l, m)
        elif ky == "Y":
            shc.setY(l, m, s)
        else:
            errmsg = "addSphericalHarmonic():  Invalid name not staring with Y or K.  name = %-5s"% (name)
            raise RietError(errmsg)

        return shc


    def _getSHC(self, ky, l, m, sign=""):
        """
        to check whether the same Spherical Harmonic has existed

        Arguments
        ky  :   string, K or Y
        l   :   integer
        m   :   integer
        sign:   string, "+" or "-" or ""

        Return  --  (1) SHcoefficient object
                    (2) None, if not exist
        """
        for shc in self.get("SHcoefficient"):
            if shc.isKY() == ky and shc.get("L") == l and shc.get("M") == m and shc.get("sign") == sign:
                return shc
        
        return None


    def getSphericalHarmonic(self, name):
        """
        get a spherical harmonic instance with such name

        Arguements:
        name    --  string, spherical harmonic name

        Return  --  SHcoefficent object

        Exception:  not exist
        """
        #  1. get name
        ky = name[0]
        l  = int(name[1])
        m  = int(name[2])
        if len(name) > 3 and (name[3] == "+" or name[3] == "-"):
            s = name[3]
        else:
            s = "" 

        #  2. get SHC
        shc = self._getSHC(ky, l, m, s)

        #  3. exception?
        if shc is None:
            errmsg = "getSphericalHarmonic():  Cannot Find Spherical Harmonic %-10s In Size-Model"% (name)
            raise RietError(shc)

        return shc

SizeModelSpherical.ParamDict.update(SizeModelSpherical.ParamDict)
SizeModelSpherical.ObjectDict.update( SizeModelSpherical.ObjectDict)
SizeModelSpherical.ObjectListDict.update(SizeModelSpherical.ObjectListDict)


class DefectSizeBroaden(RietveldClass):
    """
    single defect size broaden

    attribute
    - n1
    - n2
    - n3
    - n4
    - n5
    - SZ
    """


    ParamDict = {
        "n1":   IntInfo("n1", "user-dfeined selective hkl size broadening n1", 0), 
        "n2":   IntInfo("n2", "user-dfeined selective hkl size broadening n1", 0), 
        "n3":   IntInfo("n3", "user-dfeined selective hkl size broadening n1", 0), 
        "n4":   IntInfo("n4", "user-dfeined selective hkl size broadening n1", 0), 
        "n5":   IntInfo("n5", "user-dfeined selective hkl size broadening n1", 0), 
        "SZ":   RefineInfo("SZ", "SZ", 0.0),
    }

    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """initialization"""

        RietveldClass.__init__(self, parent)

        return



class SHcoefficient(RietveldClass):
    """
    SH coefficient

    attribute
    - Y
    - K
    - L
    - M
    """


    ParamDict = {
        "Y":    RefineInfo("Y", "spherical harmonics", 0.0),
        "K":    RefineInfo("K", "cubic harmonics", 0.0),
        "L":    IntInfo("L", "orbit quantum number", 0),
        "M":    IntInfo("M", "spin quantum number", 0),
        "sign": EnumInfo("sign", "sign of the spherical harmonic Y_lm^(+/-)", "", 
                        {"": "no sign",
                        "+": "+",
                        "-": "-"},
                        ["", "+", "-"]),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """initialization"""
        RietveldClass.__init__(self, parent)

        # set up some initial value
        self._yk = "Y"

        return


    def _setKY(self, l, m, sign=""):
        """
        set up Y_lm^+/-  or K_lm

        Arguemnts:
        L       :   ingter, l
        M       :   integer, m
        sign    :   string, for sign   
        
        return  --  None
        """
        self._yk = "Y"

        self.set("L", l)
        self.set("M", m)
        self.set("sign", sign)

        return


    def setK(self, l, m):
        """
        set up Y_lm^+/-

        Arguemnts:
        L       :   ingter, l
        M       :   integer, m
        sign    :   string, for sign   
        
        return  --  None
        """
        self._yk = "K"

        self._setKY(l, m)

        return


    def setY(self, l, m, sign=""):
        """
        set up Y_lm^+/-

        Arguemnts:
        L       :   ingter, l
        M       :   integer, m
        sign    :   string, for sign   
        
        return  --  None
        """
        self._yk = "Y"

        self._setKY(l, m, sign)

        return


    def getSphericalName(self):
        """
        return the spherical harmonic name

        Return  --  string, name
        """
        name = ""
        
        name += self._yk
        name += str(self.get("L"))
        name += str(self.get("M"))
        name += str(self.get("sign"))

        return name


    def isKY(self):
        """
        return  is in K-mode or Y-mode

        Return  --  String, "K" or "Y"
        """
        return self._yk




"""     Strain Model Suite  """

class StrainParameter(RietveldClass):
    """
    class for simulating strain effect on the profile
    StrainParameter includes 
    1. basic 3 strain parameters
    2. an optional strain model
    3. an optional LorentzianStrainBroadening

    """
    ParamDict = {
        "Str1":                 RefineInfo("Str1", "microstructure strain parameter 1", 0.0),
        "Str2":                 RefineInfo("Str1", "microstructure strain parameter 2", 0.0),
        "Str3":                 RefineInfo("Str1", "microstructure strain parameter 3", 0.0),
        "StrainModelSelector":  IntInfo("StrainModelSelector", "strain model selector", 0),
        "StrainModelType":      EnumInfo("Model", "strain model type", 7,
                            {7: "Axial vector strain",
                            9:  "other microstrain model",
                            1:  "anistropic strain broadening",
                            0:  "with Str=0, generalized strain model"},
                            [7, 9, 1, 0]),
    }
    ObjectDict = {}
    ObjectListDict = {
        "StrainModel":      ObjectInfo("StrainModel", "StrainModel", 0, 1),
        "LorentzianStrain": ObjectInfo("LorentzianStrain", "LorentzianStrain", 0, 1)
    }

    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return


    def validate(self):
        """
        validation
        """
        rvalue = RietveldClass.validate(self)

        # synchronization strain model
        strainmodels = self.get("StrainModel")
        if len(strainmodels) > 0:
            strainmodel = strainmodels[0]
        else:
            strainmodel = None
        phase        = self.parent.getParentPhase()
        Str          = phase.get("Str")

        if strainmodel is None:
            pass

        elif isinstance(strainmodel, StrainModelAnisotropic):
            if strainmodel.get("Laueclass") == "mmm":
                if abs(Str) != 1:
                    phase.set("Str", 1)
                self.set("StrainModelSelector", 3)
                self.set("StrainModelType",     1)

            elif strainmodel.get("Laueclass") == "1 2/m 1":
                if abs(Str) != 1:
                    phase.set("Str", 1)
                self.set("StrainModelSelector", 2)
                self.set("StrainModelType",     1)
            
            elif strainmodel.get("Laueclass") == "4/m":
                if abs(Str) != 1:
                    phase.set("Str", 1)
                self.set("StrainModelSelector", 4)
                self.set("StrainModelType",     1)

            else:
                errmsg = "StrainModel.validate():  "+strainmodel.get("Laueclass")
                raise NotImplementedError(errmsg)

        elif isinstance(strainmodel, StrainModelMicro):
            pass

        else:
            errmsg = "StrainParameter.validate()  StrainModel = %-15s has not been implemented"%(strainmodel.__class__.__name__)
            raise_(NotImplementedError, errmsg)

        return rvalue

# End of class StrainParameter


class StrainModel(RietveldClass):
    """
    base class of strain model
    
    attribute
    - StrainModel
    """


    ParamDict = {}
    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return


# End of class StrainModel


class StrainModelAxial(StrainModel):
    """
    strain model with axial microstrain vector
    
    attribute
    - St1
    - St2
    - St3
    """

    ParamDict = {
        "St1":  RefineInfo("St1", "axial microstrain vector St1", 0.0),
        "St2":  RefineInfo("St2", "axial microstrain vector St2", 0.0),
        "St3":  RefineInfo("St3", "axial microstrain vector St3", 0.0),
    }

    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """
        initialization
        """
        StrainModel.__init__(self, parent)

        return

StrainModelAxial.ParamDict.update(StrainModel.ParamDict)
StrainModelAxial.ObjectDict.update( StrainModel.ObjectDict)
StrainModelAxial.ObjectListDict.update(StrainModel.ObjectListDict)
# End of class StrainModel


class StrainModelMicro(StrainModel):
    """
    strain model for microstrain with additional parameters

    attribute
    -Str4
    -Str5
    -Str6
    -Str7
    -Str8
    """

    ParamDict = {
        "Str4":  RefineInfo("Str4", "additional strain parameter Str4", 0.0),
        "Str5":  RefineInfo("Str5", "additional strain parameter Str5", 0.0),
        "Str6":  RefineInfo("Str6", "additional strain parameter Str6", 0.0),
        "Str7":  RefineInfo("Str7", "additional strain parameter Str7", 0.0),
        "Str8":  RefineInfo("Str8", "additional strain parameter Str8", 0.0),
    }
    
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """

        StrainModel.__init__(self, parent)

        return

StrainModelMicro.ParamDict.update(StrainModel.ParamDict)
StrainModelMicro.ObjectDict.update( StrainModel.ObjectDict)
StrainModelMicro.ObjectListDict.update(StrainModel.ObjectListDict)
# End of class StrainModelMicro



class StrainModelAnisotropic(StrainModel):    
    """
    strain model with quartic form - laue class
    
    attribute
    - Laueclass
    """

    ParamDict = {
        "Laueclass":    EnumInfo("Laueclass", "Laue class", "-1",
                            {"-1":      "-1",
                            "1 2/m 1":  "1 2/m 1",
                            "1 1 2/m":  "1 1 2/m",
                            "mmm":      "mmm",
                            "4/m":      "4/m",
                            "4/mmm":    "4/mmm",
                            "-3 R":     "-3 R",
                            "-3m R":    "-3m R",
                            "-3":       "-3",
                            "-3m1":     "-3m1",
                            "-31m":     "-31m",
                            "6/m":      "6/m",
                            "6/mmm":    "6/mmm",
                            "m3":       "m3",
                            "m3m":      "m3m"},
                            ["-1", "1 2/m 1", "1 1 2/m", "mmm", "4/m", "4/mmm", "-3 R", "-3m R", "-3", "-3m1", "-31m", "6/m", "6/mmm", "m3", "m3m"]),
    }

    ObjectDict  = {}
    ObjectListDict = {
        "QuarticCoefficient":   ObjectInfo("SetQuarticCoefficient", "QuarticCoefficient", 0, None),
    }

    
    def __init__(self, parent, laueclass=None):
        """
        initialization
        """
        StrainModel.__init__(self, parent)

        if (laueclass is not None):
            self.set("Laueclass", laueclass)

        return

    
    def __copy__(self):
        """
        re-defined shallow-copy but including all Quartic coefficient

        return  --  StrainModelAnisotropic
        """
        newcopy = self.duplicate()

        return newcopy


    def get(self, param_name, condition=None):
        """
        extending base class's get(), but treat a special parameter (h, k, l) as "hkl"

        return      --  value of parameter
                        None

        param_name: parameter name
                    list of possible parameter:
                    hkl:
                    Laueclass:

        condition:  a value for a param_name to be equal to

        Example:
        get("hkl", (0, 2, 2)):  return a GeneralShift with (0, 2, 2) as HKL
        """
        if param_name == "hkl":
            for quartic in self.get("QuarticCoefficient"):
                if quartic.get("H") == condition[0] and quartic.get("K") == condition[1] and quartic.get("L") == condition[2]:
                    return quartic
            return None
        else:
            return StrainModel.get(self, param_name)


StrainModelAnisotropic.ParamDict.update(StrainModel.ParamDict)
StrainModelAnisotropic.ObjectDict.update( StrainModel.ObjectDict)
StrainModelAnisotropic.ObjectListDict.update(StrainModel.ObjectListDict)
# End of class StrainModelMicro


class StrainModelGeneral(StrainModelMicro):
    """
    strain model for microstrain with additional parameters

    attribute
    -Str9
    -Str10
    -Str11
    -Str12
    -Str13
    -Str14
    -Str15
    """

    ParamDict = {
        "Str9":  RefineInfo("Str9", "additional strain parameter Str9", 0.0),
        "Str10": RefineInfo("Str10", "additional strain parameter Str10", 0.0),
        "Str11": RefineInfo("Str11", "additional strain parameter Str11", 0.0),
        "Str12": RefineInfo("Str12", "additional strain parameter Str12", 0.0),
        "Str13": RefineInfo("Str13", "additional strain parameter Str13", 0.0),
        "Str14": RefineInfo("Str14", "additional strain parameter Str14", 0.0),
        "Str15": RefineInfo("Str15", "additional strain parameter Str15", 0.0),
    }
    
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        StrainModelMicro.__init__(self, parent)

        return

StrainModelGeneral.ParamDict.update(StrainModelMicro.ParamDict)
StrainModelGeneral.ObjectDict.update( StrainModelMicro.ObjectDict)
StrainModelGeneral.ObjectListDict.update(StrainModelMicro.ObjectListDict)
# End of class StrainModelGeneral



class QuarticCoefficient(RietveldClass):
    """
    a single quartic coefficient 

    attribute
    - S
    - H
    - K
    - L
    """


    ParamDict = {
        "S":    RefineInfo("S", "S", 0.0),
        "H":    IntInfo("H", "H", 0),
        "K":    IntInfo("K", "K", 0),
        "L":    IntInfo("L", "L", 0),
    }

    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent, hkl=None):
        """
        initialization

        hkl:  (h, k, l) 3-integer-tuple
        """
        RietveldClass.__init__(self, parent)

        if hkl is not None:
            self.set("H", hkl[0])
            self.set("K", hkl[1])
            self.set("L", hkl[2])

        return

# End of class QuarticCoefficient


class LorentzianStrain(RietveldClass):
    """
    Lorentzian strain
    """


    ParamDict = {
        "XI":   RefineInfo("XI", "Lorentzian anisotropic strain parameter", 0.0),
    }

    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return


# End of LorentzianStrain


class SpecialReflection(RietveldClass):
    """
    special reflection
    
    attributes:
    - h
    - k
    - l
    - nvk
    - dhg2 refine
    - dhl
    """


    ParamDict = {
        "h":    IntInfo("h", "h", 0),
        "k":    IntInfo("k", "k", 0),
        "l":    IntInfo("l", "l", 0),
        "nvk":  IntInfo("nvk", "nvk", 0),
        "D_HG2": RefineInfo("D_HG2", "D_HG2", 0.0),
        "D_HL":  RefineInfo("D_HL", "D_HL", 0.0),
        "Shift":RefineInfo("Shift", "Shift", 0.0),
    }

    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return

# End of SpecialReflection

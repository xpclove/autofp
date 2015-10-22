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

__id__ = "$Id: phase.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.rietveldclass import RietveldClass
from diffpy.pyfullprof.utilfunction import verifyType
from diffpy.pyfullprof.infoclass import BoolInfo
from diffpy.pyfullprof.infoclass import EnumInfo
from diffpy.pyfullprof.infoclass import FloatInfo
from diffpy.pyfullprof.infoclass import IntInfo
from diffpy.pyfullprof.infoclass import RefineInfo
from diffpy.pyfullprof.infoclass import StringInfo
from diffpy.pyfullprof.infoclass import ObjectInfo

class Phase(RietveldClass):
    """
    Phase contains all the information only belongs to  a single phase

    attributes

    _contributionlist --  list instance containing all the contribution related to this Phase
    """


    ParamDict = {
        "Name":     StringInfo("Name", "Phase Name", ""),
        "Jbt":      EnumInfo("Jbt", "Structure factor model and refinement method", 0,
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
        "Comment":  StringInfo("Comment", "Allowed Options", ""),
        "a":        RefineInfo("a", "a", 1.0),
        "b":        RefineInfo("b", "b", 1.0),
        "c":        RefineInfo("c", "c", 1.0),
        "alpha":    RefineInfo("alpha", "alpha", 90.0),
        "beta":     RefineInfo("beta", "beta", 90.0),
        "gamma":    RefineInfo("gamma", "gamma", 90.0),
        "Spacegroup":   StringInfo("Spacegroup", "Space group", ""),
        "ATZ":      FloatInfo("ATZ", "weight percent coefficient", 1.0, "", 0.0, None),
        "Isy":      EnumInfo("Isy", "Symmetry opertor reading control", 0,
                    {0: "symmetry operators generated automatically from the space group symbol",
                    1:  "user-input symmetry operator",
                    -1: "user-input symmetry operator",
                    2:  "basis function"},
                    [0, 1, -1, 2]),
        "Str":      EnumInfo("Str", "size strain reading control", 0,
                    {0: "using selected models",
                    1:  "generalized formulation of strains parameters be used",
                    -1: "using selected models and generalized formulation of strains parameters be used",
                    2:  "generalized formulation of size parameters be used",
                    3:  "generalized formulation of strain and size parameters be used"},
                    [0, 1, -1, 2, 3]),
        "Jvi":      EnumInfo("Jvi", "Output options", 0,
                    {0: "no operation",
                    3:  "unknow operation",
                    1: "",
                    2:  "",
                    11: ""},
                    [0, 3, 1, 2, 11]),
        "Jdi":      EnumInfo("Jdi", "Crystallographic output options", 0,
                    {0: "",
                    1:  "",
                    -1: "",
                    2:  "",
                    3:  "",
                    4:  ""},
                    [0, 1, -1, 2, 3, 4]),
        "Dis_max":  FloatInfo("Dis_max", "maximum distance between atoms to output", 0.0),
        "Ang_max":  FloatInfo("Ang_max", "maximum angle between atoms to output", 0.0),
        "BVS":      StringInfo("BVS", "BVS calculation flag", ""),
        "Tolerance":    FloatInfo("Tolerance", "Tolerance for the ionic radius", 0.0, "%"),
        "Hel":      BoolInfo("Hel", "Control to constrain a magnetic structure to be helicoidal", False),
        "Sol":      BoolInfo("Sol", "Additional hkl-dependent shifts reading control", False),
        "Nat":      IntInfo("Nat", "Atom Number", 0, 0, None),
        "Dis":      IntInfo("Dis", "distance restraint number", 0, 0, None),
        "MomMA":    IntInfo("MomMA", "number of angle/magnetic restraint", 0, 0, None),
        "MomMoment":    IntInfo("MomMoment", "number of magnetic restraints", 0, 0, None),
        "MomAngles":    IntInfo("MomAngles", "number of angle restraints", 0, 0, None),
        "Furth":    IntInfo("Furth", "user defined parameter number", 0, 0, None),
        "Nvk":      IntInfo("Nvk", "number of propagation vector", 0),
        "More":     BoolInfo("More", "flag for using Jvi, Jdi, Hel, Sol, Mom and Ter", False),
        "N_Domains":IntInfo("N_Domains", "Number of Domains/twins", 0, 0, None), 
    }

    ObjectDict = {
        "OperatorSet": ObjectInfo("OperatorSet", "OperatorSet"),
    }

    ObjectListDict = {
        "TimeRev":  ObjectInfo("TimeRev", "TimeRev", 0, 1),
        "Atom"  :   ObjectInfo("SetAtom", "Atom", 0, None),
        "PropagationVector":    ObjectInfo("SetPropagationVector", "PropagationVector", 0, None),
        "DistanceRestraint":    ObjectInfo("SetDistanceRestraint", "DistanceRestraint", 0, None),
        "AngleRestraint":       ObjectInfo("SetAngleRestraint", "AngleRestraint", 0, None),
        "MomentRestraint":      ObjectInfo("SetMomentRestraint", "MomentRestraint", 0, None),
        "TransformationMatrixSet":  ObjectInfo("TransformationMatrixSet", "TransformationMatrixSet", 0, 1),
    }



    def __init__(self, parent):
        """
        initialization:
        """
        RietveldClass.__init__(self, parent)

        # initialize subclass-object
        operatorset = OperatorSet(self)
        self.set("OperatorSet", operatorset)

        # initialize attributes
        self._contributionlist = []

        return


    def isCrystalPhase(self):
        """
        tell the user whether this phase is a crystal phase or not

        Return  --  True/False
        """
        jbt = self.get("Jbt")

        if jbt == 0 or jbt == 2:
            rvalue = True
        else:
            rvalue = False

        return rvalue

    def needAtoms(self):
        jbt = self.get("Jbt")
        if jbt==2:
            return False
        else:
            return True

    
    def addContribution(self, contribution):
        """
        add a Contribution pertinent to this phase

        return  --  None

        contribution  --  Contribution instance
        """
        from diffpy.pyfullprof.contribution import Contribution
        verifyType(contribution, Contribution)

        self._contributionlist.append(contribution)

        return


    def getContribution(self):
        """
        get the list of Contribution of this phase

        return  --  list of Contribution 
        """
        return self._contributionlist


    def delContribution(self, contribution):
        """
        remove the Contribution instance from the Contribution-list

        return  --  None

        contribution    --  instance of Contribution

        Exception   
        1. if contribution is not in self._contributionlist
        """
        verifyType(contribution, Contribution)

        self._contributionlist.remove(contribution)

        return


    def shiftOrigin(self, dx, dy, dz):
        """
        for the Space group with multiple origin, the implementation in FullProf
        is to shift the position of each atom by a specified amount
        
        return  --  None

        dx      --  float, -1 < dx < 1
        dy      --  float, -1 < dy < 1
        dz      --  float, -1 < dz < 1
        """
        verifyType(dx, float)
        verifyType(dy, float)
        verifyType(dz, float)

        # check range
        if abs(dx)>1 or abs(dy)>1 or abs(dz)>1:
            errmsg = "Phase.shiftOrigin(%-5s, %-5s, %-5s), Shift amount our of range"\
                     (str(dx), str(dy), str(dz))
            raise RietError(errmsg)

        # set shift
        for atom in self.get("Atom"):
            atom.shiftPosition(dx, dy, dz)

        return


    def set(self, param_name, value, index=None):
        """
        Phase extending RietveldClass.set() method

        Arguments:
        param_name  --  string, parameter name
        value       --  instance, value to set
        """
        rvalue = RietveldClass.set(self, param_name, value, index=index)


        if param_name == "Jvi":
            self.set("More", True)
        elif param_name == "Jdi":
            self.set("More", True)
        elif param_name == "Hel":
            self.set("More", True)
        elif param_name == "Sol":
            self.set("More", True)
        elif param_name == "Mom":
            self.set("More", True)
        elif param_name == "Ter":
            self.set("More", True)

        return rvalue


    def validate(self):
        """
        validate of class Phase
        """
        rvalue = RietveldClass.validate(self)

        errmsg = ""

        # FullProf parameter synchronization
        # atom
        nat = len(self.get("Atom"))
        self.set("Nat", nat)
        # dis
        dis = len(self.get("DistanceRestraint"))
        self.set("Dis", dis)
        # momma
        ang = len(self.get("AngleRestraint"))
        mom = len(self.get("MomentRestraint"))
        if ang != 0 and mom != 0:
            raise NotImplementedError, "Angular Restraint and Moment Restraint cannot be used simultaneously"
        self.set("MomMA", ang+mom)
        # nvk
        nvk = len(self.get("PropagationVector"))
        self.set("Nvk", nvk)

        # Situation validation
        # 1. Jbt and Atom Number
        jbt = self.get("Jbt")
        if abs(jbt) != 2 and nat == 0:
            # not Le-Bail (profile match)
            rvalue = False
            errmsg += "No Atom is defined while Jbt = %-5s (Not Le-Bail)"% (jbt)

        # error message output
        if errmsg != "":
            prtmsg = "Phase Invalid Setup: %-60s"% (errmsg)
            print prtmsg

        if rvalue is not True:
            print "Invalidity Deteced In %-10s"% (self.__class__.__name__)

        return rvalue




class TimeRev(RietveldClass):
    """
    Time revolving of magnetic

    attribute:
    - NS:       independent symmetry operator number
    - TimeRev_1
    - ...
    - TimeRev_NS
    """

    ParamDict = {
        "NS":   IntInfo("NS", "independent symmetry operator number", 6),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent, ns):
        """
        initialization
        ns = NS
        """
        # PJ: data module does not exist dead code, commented out
        '''
        import data

        RietveldClass.__init__(self, parent)

        if ns > 0:
            self.set("NS", ns)
        else:
            raise NotImplementedError, "NS = " + str(ns) + " cannot be 0"

        for i in xrange(0, self.get("NS")+1):
            param_name = "TimeRev"+str(i)
            TimeRev.__dict__[param_name] = data.IntData(self.ParamDict[param_name].get("default"))

        '''
        return

# make doc string
MaxNS = 20
for i in xrange(0, MaxNS+1):
    param_name = "TimeRev"+str(i)
    TimeRev.ParamDict[param_name] = EnumInfo(param_name, "time reversal operator", -1,
                                            {1: "1",
                                            -1: "-1"},
                                            [1, -1])



"""     OperatorSet Suite   """
class OperatorSet(RietveldClass):
    """
    base class for operator set including symmetry operator set and basis function set
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



class OperatorSetSymmetry(OperatorSet):
    """
    the main container of a set of symmetry operators
    """


    ParamDict = {
        "Nsym": IntInfo("Nsym", "crystallographic symmetry operators number", 0, 0, None),
        "Cen":  EnumInfo("Cen", "centrosymmetry flag", 1,
                        {1: "1",
                        2:  "2"},
                        [1, 2]),
        "Laue": EnumInfo("Laue", "Laue class for magnetic symmetry", 1,
                        {1: "1",
                        2:  "",
                        3:  "",
                        4:  "",
                        5:  "",
                        6:  "",
                        7:  "",
                        8:  "",
                        9:  "",
                        10: "",
                        11: "",
                        12: "",
                        13: "",
                        14: ""},
                        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]),
        "Nsym":     IntInfo("Nsym", "symmetry operator number", 0),
        "MagMat":   IntInfo("MagMat", "magnetic matrix number", 0),
        "DepMat":   IntInfo("DepMat", "displacement matrix number", 0),
    }

    ObjectDict  = {}

    ObjectListDict = {
        "OperatorCombo": ObjectInfo("SetOperatorCombo", "OperatorCombo", 0, None),
    }


    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return


 
class OperatorSetBasisFunction(OperatorSet):


    ParamDict = {
        "Ireps":    IntInfo("Ireps", "number of irreducible representation", 0, 0, None),
        "Complex":  EnumInfo("Complex", "atomic basis funtion complex number or not", 0,
                    {0: "real",
                    1:  "complex"},
                    [0, 1]),
    }

    ObjectDict  = {}
    
    ObjectListDict = {
        "Icompl":       ObjectInfo("SetIcompl", "Icompl", 0, 1),
    }


    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return




"""     Operator Combo Suite        """

class OperatorCombo(RietveldClass):


    ParamDict = {}
    ObjectDict  = {
        "SymmetryMatrix":   ObjectInfo("SymmetryMatrix", "SymmetryMatrix"),
    }
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        initalization
        """
        RietveldClass.__init__(self, parent)

        return



class OperatorComboSymmetry(OperatorCombo):

    ParamDict = {}
    ObjectDict  = {}
    ObjectListDict = {
        "MagneticMatrix":   ObjectInfo("SetMagneticMatrix", "RotationalMatrix", 0, None),
        "DisplaceMatrix":   ObjectInfo("SetDisplaceMatrix", "RotationalMatrix", 0, None),
    }

    def __init__(self, parent):
        """
        initialization: extending
        """
        OperatorCombo.__init__(self, parent)

        return

OperatorComboSymmetry.ParamDict.update(OperatorCombo.ParamDict)
OperatorComboSymmetry.ObjectDict.update(OperatorCombo.ObjectDict)
OperatorComboSymmetry.ObjectListDict.update(OperatorCombo.ObjectListDict)



class OperatorComboBasisFunction(OperatorCombo):
    
    ParamDict = {}
    ObjectDict  = {}
    ObjectListDict = {
        "BasisFunction":    ObjectInfo("SetBasisFunction", "BasisFunction", 0, None),
    }

    def __init__(self, parent):
        """
        initialization: extending
        """
        OperatorCombo.__init__(self, parent)

        return

OperatorComboBasisFunction.ParamDict.update(OperatorCombo.ParamDict)
OperatorComboBasisFunction.ObjectDict.update(OperatorCombo.ObjectDict)
OperatorComboBasisFunction.ObjectListDict.update(OperatorCombo.ObjectListDict)



"""     Icompl Suite    """
class Icompl(RietveldClass):
    """
    ICOMPL up to 9 integers
    Isy = -2
    """

    ParamDict = {
    }
    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent, nbas):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        for i in xrange(0, nbas):
            param_name = "Ireps"+str(i)
            self.ParamDict[param_name] = IntInfo(param_name, "real/pure imaginary BSF coefficient flags"+str(i), 0)
            self.__dict__[param_name] = self.ParamDict[param_name].get("Default")

        return




"""     Basis Function Suite    """

class BasisFunction(RietveldClass):
    

    ParamDict = {
        "R1":   IntInfo("R1", "basis function real component 1", 0),
        "R2":   IntInfo("R2", "basis function real component 1", 0),
        "R3":   IntInfo("R3", "basis function real component 1", 0),
    }

    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return



class BasisFunctionComplex(BasisFunction):

    ParamDict = {
        "I1":   IntInfo("I1", "basis function complex component 1", 0),
        "I2":   IntInfo("I2", "basis function complex component 1", 0),
        "I3":   IntInfo("I3", "basis function complex component 1", 0),
    }
    ObjectDict  = {}
    ObjectListDict = {}  
   

    def __init__(self, parent):
        """
        initialization: extending
        """
        BasisFunction.__init__(self, parent)

        return

BasisFunctionComplex.ParamDict.update(BasisFunction.ParamDict)
BasisFunctionComplex.ObjectDict.update(BasisFunction.ObjectDict)
BasisFunctionComplex.ObjectListDict.update(BasisFunction.ObjectListDict)



"""     SymmetryMatrix Suite    """

class SymmetryMatrix(RietveldClass):
    

    ParamDict = {}
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return



class  SymmetryMatrix33(SymmetryMatrix):

    ParamDict = {
        "S11":  IntInfo("S11", "S[1, 1]", 0),
        "S12":  IntInfo("S12", "S[1, 2]", 0),
        "S13":  IntInfo("S13", "S[1, 3]", 0),
        "S21":  IntInfo("S21", "S[2, 1]", 0),
        "S22":  IntInfo("S22", "S[2, 2]", 0),
        "S23":  IntInfo("S23", "S[2, 3]", 0),
        "S31":  IntInfo("S31", "S[3, 1]", 0),
        "S32":  IntInfo("S32", "S[3, 2]", 0),
        "S33":  IntInfo("S33", "S[3, 3]", 0),
        "T1":   FloatInfo("T1", "T[1]", 0.0),
        "T2":   FloatInfo("T2", "T[2]", 0.0),
        "T3":   FloatInfo("T3", "T[3]", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        initialization: extending
        """
        SymmetryMatrix.__init__(self, parent)

        return

SymmetryMatrix33.ParamDict.update(SymmetryMatrix.ParamDict)
SymmetryMatrix33.ObjectDict.update(SymmetryMatrix.ObjectDict)
SymmetryMatrix33.ObjectListDict.update(SymmetryMatrix.ObjectListDict)       




class  SymmetryMatrixAlpha(SymmetryMatrix):

    ParamDict = {
        "X":  StringInfo("X", "X-component", ""),
        "Y":  StringInfo("Y", "Y-component", ""),
        "Z":  StringInfo("Z", "Z-component", ""),
    }

    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        initialization: extending
        """
        SymmetryMatrix.__init__(self, parent)

        return

SymmetryMatrixAlpha.ParamDict.update(SymmetryMatrix.ParamDict)
SymmetryMatrixAlpha.ObjectDict.update(SymmetryMatrix.ObjectDict)
SymmetryMatrixAlpha.ObjectListDict.update(SymmetryMatrix.ObjectListDict)       



"""     RotationalMatrix Suite """

class RotationalMatrix(RietveldClass):


    ParamDict = {}
    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return



class RotationalMatrix33(RotationalMatrix):

    ParamDict = {
        "R11":  IntInfo("R11", "R[1, 1]", 0),
        "R12":  IntInfo("R12", "R[1, 2]", 0),
        "R13":  IntInfo("R13", "R[1, 3]", 0),
        "R21":  IntInfo("R21", "R[2, 1]", 0),
        "R22":  IntInfo("R22", "R[2, 2]", 0),
        "R23":  IntInfo("R23", "R[2, 3]", 0),
        "R31":  IntInfo("R31", "R[3, 1]", 0),
        "R32":  IntInfo("R32", "R[3, 2]", 0),
        "R33":  IntInfo("R33", "R[3, 3]", 0),
        "Phase":    FloatInfo("Phase", "Phase", 0.0, "2PI"),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        initialization: extending
        """
        RotationalMatrix.__init__(self, parent)

        return

RotationalMatrix.ParamDict.update(RotationalMatrix.ParamDict)
RotationalMatrix.ObjectDict.update(RotationalMatrix.ObjectDict)
RotationalMatrix.ObjectListDict.update(RotationalMatrix.ObjectListDict)       



class  RotationalMatrixAlpha(RotationalMatrix):

    ParamDict = {
        "X":  StringInfo("X", "X-component", ""),
        "Y":  StringInfo("Y", "Y-component", ""),
        "Z":  StringInfo("Z", "Z-component", ""),
        "Phase":    FloatInfo("Phase", "Phase", 0.0, "2PI"),
    }

    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        initialization: extending
        """
        RotationalMatrix.__init__(self, parent)

        return

RotationalMatrixAlpha.ParamDict.update(RotationalMatrix.ParamDict)
RotationalMatrixAlpha.ObjectDict.update( RotationalMatrix.ObjectDict)
RotationalMatrixAlpha.ObjectListDict.update(RotationalMatrix.ObjectListDict)       



"""     Restraint Suite     """

class DistanceRestraint(RietveldClass):
    """
    soft distance contraints

    attribute:
        - CATOD1:   StringInfo("CATOD1", "Atom 1", ""), 
        - CATOD2:   StringInfo("CATOD2", "Atom 2", ""), 
        - ITnum:    IntInfo("ITnum", "symmetry operator number", 0),
        - T1:       FloatInfo("T1", "translation part 1 of symmetry operator", 0.0),     
        - T2:       FloatInfo("T2", "translation part 2 of symmetry operator", 0.0),
        - T3:       FloatInfo("T3", "translation part 3 of symmetry operator", 0.0),
        - Dist:     FloatInfo("Dist", "required distance", 1.0),   
        - Sigma:    FloatInfo("Sigma", "required distance deviation", 1.0),  
    """


    ParamDict = {
        "CATOD1":   StringInfo("CATOD1", "Atom 1", ""), 
        "CATOD2":   StringInfo("CATOD2", "Atom 2", ""), 
        "ITnum":    IntInfo("ITnum", "symmetry operator number", 0),
        "T1":       FloatInfo("T1", "translation part 1 of symmetry operator", 0.0),     
        "T2":       FloatInfo("T2", "translation part 2 of symmetry operator", 0.0),
        "T3":       FloatInfo("T3", "translation part 3 of symmetry operator", 0.0),
        "Dist":     FloatInfo("Dist", "required distance", 1.0),   
        "Sigma":    FloatInfo("Sigma", "required distance deviation", 1.0),  
    }

    def __init__(self, parent):
        """initialization"""

        RietveldClass.__init__(self, parent)

        return



class AngleRestraint(RietveldClass):
    """
    soft distance contraints

    attribute:
        - CATOD1 = ""
        - CATOD2 = ""
        - Itnum1 = 0
        - Itnum2 = 0
        - T1     = 0.0
        - T2     = 0.0
        - T3     = 0.0
        - t1     = 0.0
        - t2     = 0.0
        - t3     = 0.0
        - Angl   = 0.0
        - Sigma  = 0.0
    """


    ParamDict = {
        "CATOD1":   StringInfo("CATOD1", "Atom 1", ""), 
        "CATOD2":   StringInfo("CATOD2", "Atom 2", ""), 
        "CATOD3":   StringInfo("CATOD3", "Atom 3", ""), 
        "ITnum1":   IntInfo("ITnum1", "symmetry operator number 1", 0),
        "ITnum2":   IntInfo("ITnum2", "symmetry operator number 2", 0),
        "T1":       FloatInfo("T1", "translation part 1 of symmetry operator of ITnum1", 0.0),     
        "T2":       FloatInfo("T2", "translation part 2 of symmetry operator of ITnum1", 0.0),
        "T3":       FloatInfo("T3", "translation part 3 of symmetry operator of ITnum1", 0.0),
        "t1":       FloatInfo("t1", "translation part 1 of symmetry operator of ITnum2", 0.0),     
        "t2":       FloatInfo("t2", "translation part 2 of symmetry operator of ITnum2", 0.0),
        "t3":       FloatInfo("t3", "translation part 3 of symmetry operator of ITnum2", 0.0),
        "Angle":    FloatInfo("Angle", "required angle", 1.0),   
        "Sigma":    FloatInfo("Sigma", "required angle deviation", 1.0),           

    }

    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self):
        """
        initalization
        """
        RietveldClass.__init__(self, parent)

        return


class MomentRestrain:
    """
    soft moment constraints
    """

    def __init__(self):
        self.CATOM  = ""
        self.Moment = 0.0
        self.Sigma  = 0.0



class PropagationVector(RietveldClass):
    """
    a single propagation vector
    
    attribute
    - PVK_X
    - PVK_Y
    - PVK_Z
    """



    ParamDict = {
        "X":    RefineInfo("X", "propagation vector - x", 0.0),
        "Y":    RefineInfo("Y", "propagation vector - y", 0.0),
        "Z":    RefineInfo("Z", "propagation vector - z", 0.0),
    }

    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return



class TransformationMatrixSet(RietveldClass):
    """
    a class to hold a set including a transformation matrix and a origin shift vector

    attribute
     - T11... T33
     - Or_sh1...Or_sh3
    """


    ParamDict = {
        "T11":      FloatInfo("T11", "Tranformation Matrix Element 1 1", 0.0),
        "T12":      FloatInfo("T12", "Tranformation Matrix Element 1 2", 0.0),
        "T13":      FloatInfo("T13", "Tranformation Matrix Element 1 3", 0.0),
        "T21":      FloatInfo("T21", "Tranformation Matrix Element 2 1", 0.0),
        "T22":      FloatInfo("T22", "Tranformation Matrix Element 2 2", 0.0),
        "T23":      FloatInfo("T23", "Tranformation Matrix Element 2 3", 0.0),
        "T31":      FloatInfo("T31", "Tranformation Matrix Element 3 1", 0.0),
        "T32":      FloatInfo("T32", "Tranformation Matrix Element 3 2", 0.0),
        "T33":      FloatInfo("T33", "Tranformation Matrix Element 3 3", 0.0),
        "Or_sh1":   FloatInfo("Or_sh1", "Origin Shift Vector 1 ", 0.0),
        "Or_sh2":   FloatInfo("Or_sh2", "Origin Shift Vector 2", 0.0),
        "Or_sh3":   FloatInfo("Or_sh3", "Origin Shift Vector 3", 0.0),
    }

    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return

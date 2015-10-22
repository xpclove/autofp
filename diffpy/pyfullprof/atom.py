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

'''class Atom -- includes all atom information such as
    1. regular atom
    2. rigid body
    3. magnetic
'''

__id__ = "$Id: atom.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.rietveldclass import RietveldClass
from diffpy.pyfullprof.infoclass import *

class Atom(RietveldClass):
    """
    Atom contains the basic information for an atom
    """


    ParamDict = {
        "Name":     StringInfo("Name", "User-providing atom name", ""),
        "Symbol":   StringInfo("Symbol", "atom's chemical symbol", ""),
        "Typ":      StringInfo("Typ", "atom type", ""),
        "IonNumber":IntInfo("IonNumber", "Ions of ths atom", 0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        intialization
        """
        RietveldClass.__init__(self, parent)

        return

    
    def shiftPosition(self, dx, dy, dz):
        """
        shift the position of an atom by an amount (dx, dy, dz)

        return  --  None

        dx      --  float, -1 < dx < 1
        dy      --  float, -1 < dy < 1
        dz      --  float, -1 < dz < 1
        """
        def shift(self, param_name, dv):
            """
            shift a position in either constraint-model or float-mode

            return      --  None
            
            param_name  --  string, name of parameter
            dv          --  amount of shift
            """
            def checkboundary(pos):
                """
                check whether pos is out of boundary (PBC)
                
                return  --  float, position
                
                pos     --  float, position
                """
                if pos > 1.0:
                    cpos = pos-2.0
                elif pos < -1.0:
                    cpos = pos+2.0
                else:
                    cpos = pos

                return cpos

            v = self.get(param_name)
            if isinstance(v, float):
                # float mode
                vf = checkboundary(v + dv)
                self.set(param_name, vf)
            else:
                # constraint mode
                vi = v.getinitVal()
                vf = checkboundary(vi + dv)
                v.setinitVal(vf)

            return

        verifyType(dx, float)
        verifyType(dy, float)
        verifyType(dz, float)

        # check range
        if abs(dx)>1 or abs(dy)>1 or abs(dz)>1:
            errmsg = "Phase.shiftOrigin(%-5s, %-5s, %-5s), Shift amount our of range"\
                     (str(dx), str(dy), str(dz))
            raise RietError(errmsg)

        # change position
        shift(self, "X", dx)
        shift(self, "Y", dy)
        shift(self, "Z", dz)

        return


    def validate(self):
        """
        validate the parameters, subclass and container to meet the refinement requirement
        """
        rvalue = RietveldClass.validate(self)

        # type check
        name = self.__class__.__name__
        if name == "Atom":
            print "base class Atom is not allowed"
            rvalue = False

        return rvalue



class AtomCrystal(Atom):
    """
    crystal atom
    """

    ParamDict = {
        "X":    RefineInfo("X", "fractional position x", 0.0),
        "Y":    RefineInfo("Y", "fractional position y", 0.0),
        "Z":    RefineInfo("Z", "fractional position z", 0.0),
        "Occ":  RefineInfo("Occ", "occupancy", 1.0),
        "Mul":  FloatInfo("Mul", "Multiplicity number", 1.0),
        "Spc":  IntInfo("Spc", "chemical species", 0),
        "In":   IntInfo("In", "start of symmetry operator", 0),
        "Fin":  IntInfo("Fin", "end of symmetry operator", 0),
        "N_t":  EnumInfo("N_t", "atomic displacement type", 0,
                {0: "Isotropic",
                2:  "anisotropic",
                4:  "form factor of this atom is calculated"},
                [0, 2, 4]),
    }

    ObjectDict  = {
        "AtomicDisplacementFactor": ObjectInfo("AtomicDisplacementFactor", "AtomicDisplacementFactor"),
    }

    ObjectListDict = {
        "SASH": ObjectInfo("SetSASH", "SASH", 0, None),
    }


    def __init__(self, parent):
        """
        initialization
        """
        Atom.__init__(self, parent)

        return


    def validate(self):
        """
        validate and synchronization
        
        return  --  boolean
        """
        rvalue = Atom.validate(self)

        if isinstance(self.get("AtomicDisplacementFactor"), AtomicDisplacementFactorAnisotropic):
            self.set("N_t", 2)
        else:
            self.set("N_t", 0)

        return rvalue

AtomCrystal.ParamDict.update(Atom.ParamDict)
AtomCrystal.ObjectDict.update(Atom.ObjectDict)
AtomCrystal.ObjectListDict.update(Atom.ObjectListDict)



class AtomRigid(Atom):
    """
    AtomRigit is for structural model supplied by user (Rigid body refinement)
    """

    ParamDict = {}
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self):
        """
        initialization
        """
        Atom.__init__(self, parent)     
        for i in xrange(1, 15+1):
            param_name = "P"+str(i)
            self.__dict__[param_name] = RefineData(self.ParamDict[param_name].get("default"))

        return

AtomRigid.ParamDict.update(Atom.ParamDict)
AtomRigid.ObjectDict.update(Atom.ObjectDict)
AtomRigid.ObjectListDict.update(Atom.ObjectListDict)



class AtomMagnetic(Atom):
    """
    AtomMagnetic is for magnetic neutron scattering
    """
    ParamDict = {
        "Mag":  IntInfo("Mag", "ordinal number of magnetic rotation matrix", 0),
        "Vek":  IntInfo("Vek", "propagation vector indentificator", 0),
    }
    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """
        initialization
        """
        Atom.__init__(self, parent)     

        return

AtomMagnetic.ParamDict.update(Atom.ParamDict)
AtomMagnetic.ObjectDict.update(Atom.ObjectDict)
AtomMagnetic.ObjectListDict.update(Atom.ObjectListDict)



class AtomMagneticScatter(AtomMagnetic):
    
    ParamDict = {
        "X":    RefineInfo("X", "fractional position x", 0.0),
        "Y":    RefineInfo("Y", "fractional position y", 0.0),
        "Z":    RefineInfo("Z", "fractional position z", 0.0),
        "Occ":  RefineInfo("Occ", "occupancy number", 0.0),
        "Biso": RefineInfo("Biso", "Biso", 0.0),
        "B11":  RefineInfo("B11", "B11", 0.0),
        "B22":  RefineInfo("B22", "B22", 0.0),
        "B33":  RefineInfo("B33", "B33", 0.0),
        "MagPh":    RefineInfo("MagPh", "Magnetic phase", 0.0, unit="2 PI"),
        "Coordinate":   EnumInfo("Coordinate", "coordinate system of magnetic moment", 0,
                        {0: "Cartesian",
                        1:  "Spherical"},
                        [0, 1]),
    }

    ObjectDict  = {
        "MagneticMoment":   ObjectInfo("MagneticMoment", "MagneticMoment"),
    }

    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        AtomMagnetic.__init__(self, parent)     

        # initialize magnetic moment
        magneticmoment = MagneticMoment(self)
        self.set("MagneticMoment", magneticmoment)

        return

AtomMagneticScatter.ParamDict.update(AtomMagnetic.ParamDict)
AtomMagneticScatter.ObjectDict.update(AtomMagnetic.ObjectDict)
AtomMagneticScatter.ObjectListDict.update(AtomMagnetic.ObjectListDict)



class AtomMagneticBasisfunction(AtomMagnetic):
    """
    magnetic atom using basis function
    """

    ParamDict = {
        "X":    RefineInfo("X", "fractional position x", 0.0),
        "Y":    RefineInfo("Y", "fractional position y", 0.0),
        "Z":    RefineInfo("Z", "fractional position z", 0.0),
        "Occ":  RefineInfo("Occ", "occupancy", 0.0),
        "Biso": RefineInfo("Biso", "Biso", 0.0),
        "C1":   RefineInfo("C1", "C1", 0.0),
        "C2":   RefineInfo("C2", "C2", 0.0),
        "C3":   RefineInfo("C3", "C3", 0.0),
        "C4":   RefineInfo("C4", "C4", 0.0),
        "C5":   RefineInfo("C5", "C5", 0.0),
        "C6":   RefineInfo("C6", "C6", 0.0),
        "C7":   RefineInfo("C7", "C7", 0.0),
        "C8":   RefineInfo("C8", "C8", 0.0),
        "C9":   RefineInfo("C9", "C9", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        initialization
        """
        AtomMagnetic.__init__(self, parent)     

        return 

AtomMagneticBasisfunction.ParamDict.update(AtomMagnetic.ParamDict)
AtomMagneticBasisfunction.ObjectDict.update(AtomMagnetic.ObjectDict)
AtomMagneticBasisfunction.ObjectListDict.update(AtomMagnetic.ObjectListDict)



class AtomMagneticUserModel(AtomMagnetic):
    """
    magnetic atom using basis function
    """

    ParamDict = {}
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        initialization
        """
        # PJ: there is no data module, commented out
        '''
        import data
        # base class
        AtomMagnetic.__init__(self, parent)    
       
        # define this class's variable 
        for i in xrange(1, 15+1):
            param_name = "P"+str(i)
            self.__dict__[param_name] = data.RefineData\
                            (self.ParamDict[param_name].get("default"))
        '''
        return 

AtomMagneticUserModel.ParamDict.update(AtomMagnetic.ParamDict)
AtomMagneticUserModel.ObjectDict.update(AtomMagnetic.ObjectDict)
AtomMagneticUserModel.ObjectListDict.update(AtomMagnetic.ObjectListDict)



class AtomCombined(AtomMagneticScatter):
    """
    combined work for atom
    """

    ParamDict = {
        "Spc":  IntInfo("Spc", "chemical species", 0),
        "N_t":  EnumInfo("N_t", "atomoic displacement type", 0,
                {0: "Isotropic",
                2:  "anisotropic",
                4:  "form factor of this atom is calculated",
                1:  "using Cartesian magnetic moment",
                3:  "using Cartesian magnetic moment",
                -1: "using spherical magnetic moment",
                -3: "using spherical magnetic moment"},
                [0, 2, 4, 1, 3, -1, -3]),
    }
    ObjectDict  = {}
    ObjectListDict = {
        "AtomicDisplacementFactor": ObjectInfo("AtomicDisplacementFactor", "AtomicDisplacementFactor", 0, 1),
    }

    def __init__(self, parent):
        """
        initialization
        """
        AtomMagneticScatter.__init__(self, parent)

        # set up AtomDisplacementFactor

        return

AtomCombined.ParamDict.update(AtomMagneticScatter.ParamDict)
AtomCombined.ObjectDict.update( AtomMagneticScatter.ObjectDict)
AtomCombined.ObjectListDict.update(AtomMagneticScatter.ObjectListDict)



class AtomModule(AtomMagneticScatter):
    """
    combined work for atom
    """

    ParameeterDict = {
        "Spc":  IntInfo("Spc", "chemical species", 0),
        "N_t":  EnumInfo("N_t", "atomoic displacement type", 0,
                {0: "Isotropic",
                2:  "anisotropic",
                4:  "form factor of this atom is calculated"},
                [0, 2, 4]),
        "Ndvk": IntInfo("Ndvk", "displacement parameter flag", 0),
    }
    ObjectDict  = {}
    ObjectListDict = {
        "AtomicDisplacementFactor": ObjectInfo("AtomicDisplacementFactor", "AtomicDisplacementFactor", 0, 1),
        "ModulateParameter":        ObjectInfo("SetModulateParameter", "ModulateParameter", 0, None),
    }

    def __init__(self, parent):
        """
        initialization
        """
        AtomMagneticScatter.__init__(self, parent)

        return

AtomModule.ParamDict.update(AtomMagneticScatter.ParamDict)
AtomModule.ObjectDict.update( AtomMagneticScatter.ObjectDict)
AtomModule.ObjectListDict.update(AtomMagneticScatter.ObjectListDict)


"""     Magnetic Moment Suite   """
class MagneticMoment(RietveldClass):
    """
    base class for magnetic moment
    """
    

    ParamDict = {
        "MagPh":    RefineInfo("MagPh", "magnetic phase", 0.0, unit="2 PI"),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return




class MagneticMomentCartesian(MagneticMoment):
    """
    magnetic moment in cartesian coordinate
    """
    
    ParamDict = {
        "RX":   RefineInfo("RX", "real x-component", 0.0),
        "RY":   RefineInfo("RY", "real y-component", 0.0),
        "RZ":   RefineInfo("RZ", "real z-component", 0.0),
        "IX":   RefineInfo("IX", "imagniary x-component", 0.0),
        "IY":   RefineInfo("IY", "imagniary y-component", 0.0),
        "IZ":   RefineInfo("IZ", "imagniary z-component", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        intialization
        """
        MagneticMoment.__init__(self, parent)

        return

MagneticMomentCartesian.ParamDict.update(MagneticMoment.ParamDict)
MagneticMomentCartesian.ObjectDict.update( MagneticMoment.ObjectDict)
MagneticMomentCartesian.ObjectListDict.update(MagneticMoment.ObjectListDict)



class MagneticMomentSpherical(MagneticMoment):
    """
    magnetic moment in spherical coordinate
    """
    
    ParamDict = {
        "RM":       RefineInfo("RM", "real radius-component", 0.0),
        "Rphi":     RefineInfo("Rphi", "real phi-component", 0.0),
        "Rthet":    RefineInfo("Rthet", "real theta-component", 0.0),
        "IM":       RefineInfo("IM", "imagniary radious-component", 0.0),
        "Iphi":     RefineInfo("Iphi", "imagniary phi-component", 0.0),
        "Ithet":    RefineInfo("Ithet", "imagniary theta-component", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        intialization
        """
        MagneticMoment.__init__(self, parent)

        return

MagneticMomentSpherical.ParamDict.update(MagneticMoment.ParamDict)
MagneticMomentSpherical.ObjectDict.update( MagneticMoment.ObjectDict)
MagneticMomentSpherical.ObjectListDict.update(MagneticMoment.ObjectListDict)



class MagneticMomentBasisfunction(MagneticMoment):
    """
    magnetic moment in basis function formation
    """

    ParamDict = {
        "C1":    RefineInfo("C1", "C1", 0.0),
        "C2":    RefineInfo("C2", "C2", 0.0),
        "C3":    RefineInfo("C3", "C3", 0.0),
        "C4":    RefineInfo("C4", "C4", 0.0),
        "C5":    RefineInfo("C5", "C5", 0.0),
        "C6":    RefineInfo("C6", "C6", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    
    def __init__(self, parent):
        """
        intialization
        """
        MagneticMoment.__init__(self, parent)

        return

MagneticMomentBasisfunction.ParamDict.update(MagneticMoment.ParamDict)
MagneticMomentBasisfunction.ObjectDict.update( MagneticMoment.ObjectDict)
MagneticMomentBasisfunction.ObjectListDict.update(MagneticMoment.ObjectListDict)



"""     Atomic Displacement Suite (Thermo factor)   """

class AtomicDisplacementFactor(RietveldClass):
    """
    base class for atomic displacement suite
    attributes:
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


    def validate(self):
        """
        validate the parameters, subclass and container to meet the refinement requirement
        """
        rvalue = RietveldClass.validate(self)

        # type check
        name = self.__class__.__name__
        if name == "AtomicDisplacementFactor":
            print "base class AtomicDisplacementFactor is not allowed"
            rvalue = False

        return rvalue



class AtomicDisplacementFactorIsotropic(AtomicDisplacementFactor):
    """
    isotropic atomic displacement factor
    attribute:
    - B/Uiso
    """

    ParamDict = {
        "Biso": RefineInfo("Biso", "Biso", 0.0),
        "Uiso": RefineInfo("Uiso", "Uiso", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        intialization
        """
        AtomicDisplacementFactor.__init__(self, parent)

        return

    def set(self, paramname, value, index=None):
        """ Set Uiso/Biso simutaneously"""
        from math import pi
        if paramname == "Uiso":
            pass
        elif paramname == "Biso":
            self.Biso = value
            self.Uiso = value/(8*pow(pi,2))
        return
AtomicDisplacementFactorIsotropic.ParamDict.update(AtomicDisplacementFactor.ParamDict)
AtomicDisplacementFactorIsotropic.ObjectDict.update( AtomicDisplacementFactor.ObjectDict)
AtomicDisplacementFactorIsotropic.ObjectListDict.update(AtomicDisplacementFactor.ObjectListDict)



class AtomicDisplacementFactorAnisotropic(AtomicDisplacementFactorIsotropic):
    """
    anisotropic atomic displacement factor
    attribute:
    - B/U11
    - B/U22
    - B/U33
    - B/U12
    - B/U13
    - B/U23
    """

    ParamDict = {
        "B11": RefineInfo("B11", "B11", 0.0),
        "B22": RefineInfo("B22", "B22", 0.0),
        "B33": RefineInfo("B33", "B33", 0.0),
        "B12": RefineInfo("B12", "B12", 0.0),
        "B13": RefineInfo("B13", "B13", 0.0),
        "B23": RefineInfo("B23", "B23", 0.0),
        #"U11": RefineInfo("U11", "U11", 0.0),
        #"U22": RefineInfo("U22", "U22", 0.0),
        #"U33": RefineInfo("U33", "U33", 0.0),
        #"U12": RefineInfo("U12", "U12", 0.0),
        #"U13": RefineInfo("U13", "U13", 0.0),
        #"U23": RefineInfo("U23", "U23", 0.0),
        }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        intialization
        """
        AtomicDisplacementFactor.__init__(self, parent)

        return

    def set(self, paramname, value, index=None):
        """ Set Uiso/Biso simutaneously"""
        from math import pi
        setattr(self, paramname, value)
        if paramname.startswith("U"):            
            setattr(self, paramname.replace("U", "B"), value*8*pow(pi,2))
        elif paramname.startswith("B"):
            setattr(self, paramname.replace("B", "U"), value/(8*pow(pi,2)))
        return

AtomicDisplacementFactorAnisotropic.ParamDict.update(AtomicDisplacementFactorIsotropic.ParamDict)
AtomicDisplacementFactorAnisotropic.ObjectDict.update( AtomicDisplacementFactorIsotropic.ObjectDict)
AtomicDisplacementFactorAnisotropic.ObjectListDict.update(AtomicDisplacementFactorIsotropic.ObjectListDict)



class AtomicDisplacementFactorFormfactor(AtomicDisplacementFactor):
    """
    formfactor atomic displacement factor
    attribute:
    - f11 ~ f14:    
    """

    ParamDict = {
        "f1": RefineInfo("f1", "f1", 0.0),
        "f2": RefineInfo("f2", "f2", 0.0),
        "f3": RefineInfo("f3", "f3", 0.0),
        "f4": RefineInfo("f4", "f4", 0.0),
        "f5": RefineInfo("f5", "f5", 0.0),
        "f6": RefineInfo("f6", "f6", 0.0),
        "f7": RefineInfo("f7", "f7", 0.0),
        "f8": RefineInfo("f8", "f8", 0.0),
        "f9": RefineInfo("f9", "f9", 0.0),
        "f10": RefineInfo("f10", "f10", 0.0),
        "f11": RefineInfo("f11", "f11", 0.0),
        "f12": RefineInfo("f12", "f12", 0.0),
        "f13": RefineInfo("f13", "f13", 0.0),
        "f14": RefineInfo("f14", "f14", 0.0),
    }
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent):
        """
        intialization
        """
        AtomicDisplacementFactor.__init__(self, parent)

        return
        
AtomicDisplacementFactorFormfactor.ParamDict.update(AtomicDisplacementFactor.ParamDict)
AtomicDisplacementFactorFormfactor.ObjectDict.update( AtomicDisplacementFactor.ObjectDict)
AtomicDisplacementFactorFormfactor.ObjectListDict.update(AtomicDisplacementFactor.ObjectListDict)

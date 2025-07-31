#!/usr/bin/env python
##############################################################################
#
# diffpy.pyfullprof by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Jiwu Liu, Wenduo Zhou and Peng Tian
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

__id__ = "$Id: refine.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.baseclass import BaseClass
from diffpy.pyfullprof.infoclass import *
from diffpy.pyfullprof.exception import *

class Constraint(object):
    """Constraint binds a parameter to a refined variable by a formula.
    The parameter relies on the constraint to obtain its refined value.
    The Fit instance utilizes the constraint to set up the refine engine.
    
    Data members:
    
    parname -- the name of the parameter being constrained.
    owner -- the RietveldClass object which owns this constraint.
    formula -- the origianl constraint formula
    sigma -- deviation
    damping -- damping
    varName -- variable name 
    dev -- the multiplier to the variable
    """
    def __init__(self, name, owner, formula, value=None, damping=0.0, index=None):
        """Initialization.
        
        parname -- the name of the parameter being constrained.
        owner -- the RietveldClass object which owns this constraint.
        formula -- the origianl constraint formula
        value   -- the initial value of the constrained parameter.
        damping -- damping    
        index  -- if the parameter is an array, this index gives the position
        """
        # basic settings
        self.parname = name 
        self.owner = owner
        self.index = index
        self.codeWord=0.0
        self.realvalue=0.0
        self.temprealvalue=value
        self.type=owner.name
        # adjustable settings
        self.variable=None
        self.refine=None
        self.clear()
        self.apply(formula=formula, value=value, damping=damping)
        return

    def clear(self):
        """Remove self from all the variables and refine. Reset all member variables.
        """
        # clean up the Fit setting.
        if self.variable and self in self.variable.constraints:
            self.variable.constraints.remove(self)
            self.variable.remove()
            self.variable = None
        if self.refine and self in self.refine.constraints:
            self.refine.constraints.remove(self)
            self.refine = None
                
        # reset variables
        self.on = False
        self.formula = ""
        self.damping = 0.0
        self.varName = ""
        self.dev = 0
        self.sigma = 0.0
        return
    
    def setCodeWord(codeword):
        self.codeWord=codeWord

    def getCodeWord():
        return self.codeWord    

    def apply(self, formula=None, value=None, damping=None):
        """Apply the adjustable settings.
        
        formula -- the origianl constraint formula
        val   -- the initial value of the constrained parameter.
        damping -- damping    
        """
        #1. check if new setting is ready 
        fit = self.owner.getFit()
        if fit and fit.get("Refine"):
            self.refine = fit.get("Refine")
        else:
            raise RietError("The refine is not available.")

        #2. parse the formula
        if formula is not None:
            self.formula = formula
            
        if not self.formula:
            # make an empty constraint simply for updating another fit
            return
            
        # break the formula
        try:
            dev, varName = self.formula.split('*')
            self.dev = int(dev)
            self.varName = varName
        except: 
            self.dev = 1.0
            self.varName = self.formula
        #NOTE: should check the validity of the varName
        
        #3. set value
        if value is not None:
            self.setValue(value)

        #4. set damping
        if damping is not None:
            self.damping = damping
            
        #5. create an instance of variable
        self.variable = self.refine.findVariable(self.varName)
        if self.variable is None:
            self.variable = Variable(self.refine)  
            self.variable.set('name', self.varName)          
            self.refine.set("Variable", self.variable)
        
        #6. link variable and constraint
        if self not in self.variable.constraints:
            self.variable.constraints.append(self)
        if self not in self.refine.constraints:
            self.refine.constraints.append(self)

        #4. turn on refine
        self.on = True

        return 


    def __str__(self):
        """Format output
        
        return: a string
        """
        rstring  = "%-10s  %-20s %-30s %-20s %15.6f\n"\
                   %(self.name, "Original Constraint", self.formula,  "Value", self.getValue())
        rstring += "Turned On = %-10s\n"%(str(self.on))
        rstring += "%-10s %-20s "%("", "Variable Name")
        rstring += "%-10s "%(str(self.variable.get("name")))
        return rstring


    def turnRefineOff(self):
        """Turn off the refinement of this constraint
        """
        self.on = False
        return

    
    def turnRefineOn(self):
        """Turn on the refinement of this constraint
        """
        self.on = True
        return


    def validate(self):
        """
        validate whether a constraint is allowed to put into refinement

        return:   True/False
        raise: RietError ( when data is inconsistent )
        """
        from diffpy.pyfullprof.rietveldclass import RietveldClass

        # 1. Verify the data consistency
        verifyType(self.owner, RietveldClass)
        verifyType(self.refine, Refine)
        if self.name not in self.owner.ParamDict:
            raise RietError("Incorrect ParentParameterName")

        # 2. Verify the data 
        if self.formula is None:
            return False

        return True


    def getValue(self):
        """Obtain the up-to-date value for the constrained parameter.
        
        return: float number.
        """
        return self.owner.get(self.parname, self.index)
        
        
    def setValue(self, value):
        """Set the value to the parameter
        
        value -- a float number.
        """
        self.owner.set(self.parname, value, self.index)
        

    def makeFormula(self):
        """make the constraint formula for fullprof program
        
        return: a formula string
        """
        if self.variable is None:
            raise RietError('Constraint "%s" has no variable.'%self.name)
            
        return "%20.10f+%20.10f*%s"%(self.getValue(), self.dev,  self.variable.ID)
        
    @property
    def path(self):
        """Get the full path of the constraint.
        
        return: Dot separated string.
        """
        return self.owner.path+'.'+self.name
        
    @property
    def name(self):
        """Get the full name of the constraint, with index
        
        return: a string
        """
        if self.index is None:
            return self.parname
        
        return self.parname+'[%i]'%self.index    

    @name.setter
    def name(self, v):
        """Get the full name of the constraint, with index
        
        return: a string
        """
        self.parname = v  
                      
class Variable(BaseClass):
    """Variable represents a float value to be refined. Variables are 
    independent of each other.
    """
    ParamDict = {
        "name":     StringInfo("name", "name given by user",  ""), 
        "value":    FloatInfo("value", "value", 0.0),
        "usemin":   BoolInfo("usemin", "use min limit", False),
        "usemax":   BoolInfo("usemax", "use max limit", False),
        "min":      FloatInfo("min", "min", 0.0),
        "max":      FloatInfo("max", "max", 0.0),
        "IBound":   EnumInfo("IBound", "boundary condition type", 0, 
                    {0: "hard boundary",
                    1:  "periodic boundary"},
                    [0, 1]),
        "Step":     FloatInfo("Step", "step size for simulated annealing", 1.0),
    }

    def __init__(self, parent):
        """Initialization.
        
        parent -- the owner of the variable ( must be a refine ).
        """
        if not isinstance(parent, Refine):
            raise RietError("The parent class of a variable has to be a refine.")
        BaseClass.__init__(self, parent)
        self.constraints = []

        return


    def __str__(self):
        """Form a string representation.
        
        return: a string
        """
        s  = ""
        s += "%-10s: %-10s\n"%("name", self.get("name"))
        s += "%-20s: %-10s     %-10s: %-15s     "%("Use Lower Boundary", self.get("usemin"), "Min", self.get("min"))
        s += "%-20s: %-10s     %-10s: %-15s   \n"%("Use Upper Boundary", self.get("usemax"), "Max", self.get("max"))
        s += "%-10s: %-15s     %-10s: %-15s\n"%("bound", self.get("IBound"), "step", self.get("Step"))

        index = 1
        for constraint in self.constraints:
            s += "%-10s %-5s: %-30s\n"%("Constraint", index, constraint.formula)
            index += 1

        return s

    def remove(self):
        """Delete self if there is no associated constraints.
        """
        if len(self.constraints) == 0:
            self.parent.delete("Variable", self)

        return

    
    def set(self, name, value, index=None):
        """Set the member variable.
        
        name  --  a key in ParamDict, ParamListDict, ObjectDict or ObjectListDict
        value --  the value/object to be set
        index --  only for ObjectListDict object, to give the location of the object        
        """
        # simply call the base class set
        BaseClass.set(self,name,value,index)

        # set min and max and value
        if name == "min":
            self.set("usemin", True)
        elif name == "max":
            self.set("usemax", True)

        return


class Refine(BaseClass):
    """
    Refine is a special ensemble container for Constraints and Variables
    """
    ParamDict = {}
    ObjectDict = {}
    ObjectListDict = {
        "Variable":     ObjectInfo("Variable"  , "Variable", 0, None),
    }

    def __init__(self, Parent):
        """
        initialzation
        """
        BaseClass.__init__(self, Parent) 
        self.constraints = []
        return


    def __str__(self):
        """
        print a Refine object;
        override BaseClass.__str__()
        """
        index_num=0
        s  = "+++++++++++++++this is start of Refine++++++++++++++\n"
        s += "Constraints to Refine:\n"
        for constraint in self.constraints:
            if constraint.variable is not None:
                s += ("["+str(index_num)+"]"+str(constraint)+"\n")
                index_num+=1

        s += "\nConstraints NOT to Refine:\n"
        for constraint in self.constraints:
            if constraint.variable is None:
                s += "["+str(index_num)+"]"+str(constraint)+"\n"
                index_num+=1

        s += "\nVariables:\tNumber = " + str(len(self.get("Variable"))) + "\n"
        for variable in self.get("Variable"):
            s += "Name : " + str(variable.get("name")) + "\t\tvalue = " + str(variable.get("value")) + "\n"
            s += "\tconstraints:  + number = " + str(len(variable.constraints)) + "\n"
            for constraint in variable.constraints:
                s += "\t" + constraint.name + "\t\t" + constraint.formula + "\n"
            

        return s
        

    def findVariable(self, name):
        """find a variable by its name 

        name -- the variable name
        
        return: a Variable instance or None
        """
        for object in self.get("Variable"):
            if name == object.get("name"):
                return object

        # Not found
        return None


# EOF

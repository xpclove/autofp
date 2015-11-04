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

__id__ = "$Id: rietveldclass.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.refine import Constraint
from diffpy.pyfullprof.baseclass import BaseClass
from diffpy.pyfullprof.exception import RietError

class RietveldClass(BaseClass):
    """RietveldClass extends BaseClass, and serves as the base class for all
    classes designed for Rietveld refinement.
    
    Data members:
    
    constraints -- a dictionary stores mapping from (name,index) to constarint.
    """
    def __init__(self, parent):
        """Initialization.
        """
        BaseClass.__init__(self, parent)
        self.constraints = {}
        return


    def duplicate(self):
        """
        duplicate self object to a exact copy
        (1) parameter...(copy)
        (2) subclass... (copy)
        (3) container... (copy)

        For Constraint object, only the pattern_range, phase_range and parname are copied;
        No link to Refine is established!

        scenario    --  After duplicate() and the corresponding linking work by Rietveld.set()
                        method 'RietveldClass.linkConstraint()' is always called

        return  --  the new generated twin object
        """
        try:
            newobject = self.__class__(None)
        except TypeError, err:
            errmsg  = "RietveldClass.duplicate():  instantiated as %-20s\n"%(self.__class__.__name__)
            errmsg += str(err)
            raise RietError(errmsg)

        for param_name in self.ParamDict.keys():
            #newobject.__dict__[param_name] = self.__dict__[param_name].duplicate()
            paramobj = self.get(param_name)
            if not isinstance(paramobj, Constraint):
                newobject.set(param_name, paramobj)
            else:
                newobject.set(param_name, paramobj.copy())

        for classtype in self.ObjectDict.keys():
            subobject = self.ObjectDict[classtype].get("name")
            newobject.__dict__[subobject] = self.__dict__[subobject].duplicate(self)

        for classtype in self.ObjectListDict.keys():
            subcontainer = self.ObjectListDict[classtype].get("name")
            newobject.__dict__[subcontainer] = self.__dict__[subcontainer].duplicate(self)

        return newobject


    def extend(self, baseobj):
        """
        extend a base-object to 'self', and replace base-object with 'self' in 
        Rietveld-class hierachy
        baseobj = base object
        """

        def class_in_list(classname, classnamelist):
            """
            identify whether a class_name is one in classnamelist
            class_name can be extended class while the name in classnamelist is base class
            classname -
            classnamelist -
            """
            for basename in classnamelist:
                if classname.count(basename) == 1:
                    return True
            
            return False


        def getClassName(classname, classnamelist):
            """
            if classname is an extended class name, then return the base class name

            class_name can be extended class while the name in classnamelist is base class
            classname -
            classnamelist -
            """
            for basename in classnamelist:
                if classname.count(basename) == 1:
                    return basename
           
            raise RietError, "rietveldclass.extend - getClassName"
            return

        from diffpy.pyfullprof.contribution import Contribution
        if isinstance(baseobj, Contribution):
            errmsg = "Contribution should extend this function because of its dual parent"
            raise RietError(errmsg)

        # 1 check
        if not isinstance(self, baseobj.__class__):
            return False

        # 2 copy
        for name in baseobj.ParamDict.keys():
            self.__dict__[name] = baseobj.__dict__[name]
        
        for name in baseobj.ParamListDict.keys():
            for i in range(len(baseobj.__dict__[name])):
                self.__dict__[name].set(baseobj.__dict__[name].get(i))

        for name in baseobj.ObjectDict.keys():
            self.__dict__[name] = baseobj.__dict__[name]
            # set parent
            self.__dict__[name].parent = self
            self.__dict__[name].parent = self
        
        for name in baseobj.ObjectListDict.keys():
            self.__dict__[name] = baseobj.__dict__[name]
            # set parent
            self.__dict__[name].parent = self
            for objref in self.get(name):
                objref.parent = self

        # 3 find and set parent
        parentobj = baseobj.parent
        self.parent = parentobj

        # 4 replace from the parent class view
        # if baseobj.__class__.__name__ in parentobj.ObjectDict.keys():
        if class_in_list(baseobj.__class__.__name__, parentobj.ObjectDict.keys()):
            classname = getClassName(baseobj.__class__.__name__, parentobj.ObjectDict.keys())
            parentobj.set(classname, self)
        # elif baseobj.__class__.__name__ in parentobj.ObjectListDict.keys():
        elif class_in_list(baseobj.__class__.__name__, parentobj.ObjectListDict.keys()):
            classname = getClassName(baseobj.__class__.__name__, parentobj.ObjectListDict.keys())
            for i,obj in enumerate(parentobj.get(classname)):
                if baseobj == obj:
                    parentobj.set(classname, self, i)
                    break
            else:
                raise RietError("RietveldClass.extend(): Can not find the ")
        else:
            print "base obj:\t" + baseobj.__class__.__name__
            print "parent obj:\t" + str(parentobj.ObjectDict.keys())
            raise RietError("RietveldClass.extend(): Parent Class Cannot Locate Object")

        return True


    def clear(self):
        """Clear myself completely.
        """
        for constraint in self.constraints.values():
            constraint.clear()
            
        self.constraints = {}
        
        
    def getFit(self):
        """Get the owner Fit instance.
        
        return: a Fit instance
        """
        from diffpy.pyfullprof.fit import Fit
        root = self
        while not isinstance(root,  Fit):
            root = root.parent
            if root is None:
                return None
                
        return root


    def set(self, name, value, index=None):
        """Set the value for a member and link constraints.
        
        name  --  a key in ParamDict, ObjectDict or ObjectListDict
        value --  the value/object to be set
        index --  only for ObjectListDict object, to give the location of the object
        """
        BaseClass.set(self, name, value, index)
        #NOTE: linkConstraint is quite useless, becaue if the constraint is set
        #      before a refine is assigned to it, an exception is thrown.
        #      It is only useful when a RietveldClass object is set to another Fit.
        if isinstance(value, RietveldClass) and self.getFit() is not None:
            value.linkConstraint()

        return


    def linkConstraint(self):
        """Link all the constraints to the fit object.
        called after duplicate() when a new-object is added to the Fit regime

        refine:  Refine object 
        """
        from diffpy.pyfullprof.fit import Fit
        if isinstance(self, Fit):
            _fit = self
        else:
            _fit = self.getFit()
        if _fit:
            refine = _fit.get("Refine")
        else:
            # Should not happen, this is checked in the "set" function
            # which is the only one calling this function.
            raise RietError("No Fit is created.")
        
        for constraint in self.constraints.values():
            constraint.refine = refine
            constraint.apply()
        
        for name in self.ObjectDict.keys():
            o = self.__dict__[name]
            if o: # it may be None
                o.linkConstraint()
                        
        for name in self.ObjectListDict.keys():
            for o in self.__dict__[name]._list:
                o.linkConstraint()

        return
    
    
    def _checkNameIndex(self, name, index):
        """check the validity of the name and index passed to set/get/remove constraints
        
        name   -- the parameter name
        index -- the index in the parameter list  
      
        raise: RietError if name or index is not right.
        """  
        if self.ParamDict.has_key(name):
            if index is not None:
                raise RietError('The parameter "%s" is not a list.'%name)
            return
            
        
        if self.ParamListDict.has_key(name):
            if not isinstance(index, int):
                raise RietError('The parameter list needs an int for index, but "%s"=%s is received.' 
                                %(type(index), str(index)))
                                
            return
    
        # otherwise, there is no key.
        raise RietError("Class %s does not have a  parameter or parameter list: %s"%(
                  self.__class__.__name__, name) )
        
        return
        

    def setConstraintByPath(self, path, formula, value=None, damping=None, varIndex=None):
        """Constrain a parameter by path

        path  -- a full path,  e.g., x.y.z[i].a
        formula -- a formula to be applied to the parameter
        value   -- the initial value of the constrained parameter.
        damping -- damping    
        varIndex -- if it is not None, append it to the formula; if the path 
                    corresponds to multiple parameters, varIndex will increase
                    by one for each parameter. 
 
        return: the newly created constraint object
        """
        if path.count('.') > 0:
            try:
                objpath,paramname = path.rsplit('.',1)
            except:
                raise RietError('Invalid format for a parameter name: ' + path)

            objects = self.getByPath(objpath)

            # There are multiple objects
            if isinstance(objects,  list):
                constraints = []
                for i, object in enumerate(objects):
                    _constraints = object.setConstraintByPath(paramname, formula, 
                                                           value, damping, varIndex)
                    # Append results to the result constraint list,
                    # and increase the varIndex accordingly if it is not None.
                    if isinstance(_constraints, list):
                        constraints.extend(_constraints)
                        if varIndex is not None:
                            varIndex += len(_constraints)
                    else:
                        constraints.append(_constraints)
                        if varIndex is not None:
                            varIndex += 1
                return constraints

            # else it is a single object
            return objects.setConstraintByPath(paramname, formula, value, damping, varIndex)

        name, index = self._parseIndex(path)
        
        # If index is a slice, we need set constraint one by one
        if isinstance(index, slice):
            constraints = []
            indices = self._rangeParam(name, index)
            for i in indices:
                if varIndex is not None:
                    _formula = formula+'%i'%(varIndex+i)
                else:
                    _formula = formula
                constraints.append(
                   self.setConstraint(name, _formula, value, damping, index=i))                
            return constraints
                
        
        # else the index is an int or None
        if varIndex is not None:
            formula = formula + '%i'%varIndex
        return self.setConstraint(name, formula, value=value, damping=damping, index=index)


    def setConstraint(self, name, formula, value=None, damping=None, index=None):
        """Constrain a parameter to a formula

        name   -- the parameter name
        formula -- the formula that the parameter to be constrained to
        value   -- the initial value of the constrained parameter.
        damping -- damping       
        index -- the index in the parameter list 
        
        return: the newly created constraint object
        """
        self._checkNameIndex(name, index)
        constraint = Constraint(name,self,formula,value=value,damping=damping, index=index)
        constraint.codeWord=damping
        constraint.realvalue=value
        try:
            oldconstraint = self.constraints[(name, index)]
            oldconstraint.clear()
        except KeyError:
            pass
            
        self.constraints[(name, index)] = constraint
        return constraint
                
    def setConstraint(self, name, formula, tpcowdWord,value=None, damping=None, index=None):
        """Constrain a parameter to a formula

        name   -- the parameter name
        formula -- the formula that the parameter to be constrained to
        value   -- the initial value of the constrained parameter.
        damping -- damping       
        index -- the index in the parameter list 
        
        return: the newly created constraint object
        """
        self._checkNameIndex(name, index)
        constraint = Constraint(name,self,formula,value=value,damping=damping, index=index)
        constraint.codeWord=tpcowdWord
        constraint.realvalue=value
        try:
            oldconstraint = self.constraints[(name, index)]
            oldconstraint.clear()
        except KeyError:
            pass
            
        self.constraints[(name, index)] = constraint
        return constraint
    def getConstraint(self,  name,  index=None):
        """Get a constraint by name.
        
        name -- a parameter name in ParamDict
        index -- the index in the parameter list 
        
        return: a constraint object
        """
        self._checkNameIndex(name, index)
        try:
            return self.constraints[(name, index)]
        except KeyError:
            return None
            
            
    def getConstraintByPath(self, path):
        """Get a constraint by path
        
        path -- a full path,  e.g., x.y.z[i].a
        return: a constraint object
        """
        if path.count('.') > 0:
            try:
                objpath,paramname = path.rsplit('.',1)
            except:
                raise RietError('Invalid format for a parameter name: ' + path)

            objects = self.getByPath(objpath)
            if isinstance(objects,  list):
                constraints = []
                for object in objects:
                    _constraints=object.getConstraintByPath(paramname)
                    if isinstance(_constraints, list):
                        constraints.extend(_constraints)
                    else:
                        constraints.append(_constraints)   
                return constraints
            
            # else it is a single object
            return objects.getConstraintByPath(paramname)

        name, index = self._parseIndex(path)
        
        # If index is a slice, we need get constraint one by one 
        if isinstance(index, slice):
            constraints = []
            indices = self._rangeParam(name, index)
            for i in indices:
                constraints.append(self.getConstraint(name, i))
            return constraints
        
        # else the index is an int or None
        return self.getConstraint(name, index)
        
        
    def removeConstraint(self, name, index=None):
        """Remove a constraint by name.
        
        name -- a parameter name in ParamDict
        index -- the parameter index in the parameter list
        """
        self._checkNameIndex(name, index)
        try:
            constraint = self.constraints[(name, index)]
            constraint.clear()
            
            del self.constraints[(name, index)]
        except KeyError:
            pass
            
        return constraint

# EOF

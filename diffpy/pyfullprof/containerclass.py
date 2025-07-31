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

from builtins import str
from builtins import range
from builtins import object
from future.utils import raise_
__id__ = "$Id: containerclass.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.exception import *

class ObjectList(object):
    """ObjectList stores a list of BaseClass objects.
    
    Data members:
    min -- the minimal number of objects in the list
    max -- the maximal number of objects in the list (None means unlimited)
    key -- the corresponding key in its parent object
    _list -- the data storate, a list
    """
    def __init__(self, parent, min, max, key):
        """Initialization.
        
        parent -- the parent BaseClass object
        min -- integer indicate the minimal number of objects
        max -- integer indicate the maximal number of objects (None means unlimited)
        key -- the corresponding key in its parent class
        """
        self.parent = parent
        self.min    = min
        self.max    = max
        self.key    = key
        self._list  = []
        return


    def __str__(self):
        """Format the string representation.
        
        return: a string
        """
        rstring  = ""
        objcount = 0
        i=0
        for obj in self._list:
            rstring  +='<'+str(i)+'>\n'+ obj.__class__.__name__ + " : " + str(objcount) + "\n"
            rstring  += str(obj)
            objcount += 1

        if rstring == "":
            rstring += "Empty ObjectList\n"

        return rstring


    def __len__(self):
        """Get the number of objects
        
        return: an integer (the number of objects)
        """
        return len(self._list)


    def clear(self):
        """Clear myself completely
        """
        for obj in self._list:
            obj.clear()

        self._list = []
        return


    def delete(self, index=None):
        """Delete an object by id.
        
        index -- a general index:
                 if it is a integer, it gives the exact location
                 if it is None, all objects will be selected
                 if it is a slice object, the slice will be selected
                 if it is a BaseClass object, the object will be selected.
        """
        indices = self._range(index)
        indices.sort(reverse=True)
        for i in indices:
            self._list[i].clear()
            self._list.pop(i)
        
        return


    def duplicate(self, parentobj):
        """Duplicate this ObjectList object
        
        parentobj:  reference to parent object
        """
        newcontainer = ObjectList(parentobj)

        for object in self._list:
            newobject = object.duplicate()
            newcontainer.set(newobject)

        return newcontainer


    def get(self, index=None):
        """Get an object in its object list.

        index -- a general index:
                 if it is a integer, it gives the exact location
                 if it is None, all objects will be selected
                 if it is a slice object, the slice will be selected
                 if it is a BaseClass object, the object will be selected.
        return: the object(s) 
        """

        # to return a list or a value depends on what the index is
        if isinstance(index, int):
            return self._list[index]        
        if index is None:
            return self._list
            
        indices = self._range(index)
        
        # treat the case when a Baseclass object is passed in specially
        # return the results as a single object
        from diffpy.pyfullprof.baseclass import BaseClass
        if isinstance(index, BaseClass):
            return self._list[indices[0]]
            
        return [self._list[i] for i in indices]


    def _range(self, index):
        """Produce a true list of indices
        None:  all indices
        int:  single index
        slice: a slice of indices
        BaseClass: the exact location of the object.
        
        return: a list of indices
        """
        if index is None:
            return list(range(len(self._list)))
        
        if isinstance(index, int):
            return [index]
            
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self._list))
            return list(range(start, stop, step))
        
        from diffpy.pyfullprof.baseclass import BaseClass
        if isinstance(index, BaseClass):
            try:
                i = self._list.index(index)
            except:
                raise RietError("%s.%s has no object :\n%s\n\n"%
                                (self.parent.__class__.__name__, self.key, str(index)))
            return [i]
            
        raise RietError("An integer, slice, BaseClass or None is required to specify the object(s), but a '%s'=%s is received."%(type(index), str(index)))
        
        
    def set(self, obj, index=None):
        """Set a new object in the list.
        
        obj   -- the object reference(s)
        index -- a general index:
                 if it is a integer, it gives the exact location
                 if it is None, a new object will be added
                 if it is a slice object, the slice will be selected  
                 if it is a BaseClass object, the object will be selected.
        """
        if index is None:
            if self.max is None or len(self) < self.max:
                self._list.append(obj)
            else:
                raise_(RietError, "The size exceeds the limit: " + str(self.max))
            return

        indices = self._range(index)
        for i in indices:
            oldobj = self._list[i]
            self._list[i] = obj
            
            # remove the old object.
            if oldobj is not obj:
                oldobj.clear()
        return
    
    
    def listParameters(self, prefix):
        """List the paths to all the Rietveld parameters. '[%i]' is appended for an 
        object with index 'i'.

        prefix -- a prefix string to be appended
        return: a list of strings
        """
        pathlist = []
        for i, obj in enumerate(self._list):
            paramlist = obj.listParameters()
            pathlist.extend([prefix+self.key+"[%i]."%i+param for param in paramlist])

        return pathlist


class ParamList(object):
    '''ParamList stores parameter in a list. 

    Data members:
    min -- the minimal number of parameters in the list
    max -- the maximal number of parameters in the list(None means no limit)
    key -- the corresponding key in its parent class
    _list -- the data storate, a list
    '''
    def __init__(self, parent, min, max, key):
        """Initialization.
        
        parent -- the owner BaseClass object
        min -- integer indicate the minimal number of parameters
        max -- integer indicate the maximal number of parameters (None means unlimited)
        key -- the corresponding key in its parent class
        """
        self.parent = parent
        self.min    = min
        self.max    = max
        self.key    = key
        self._list  = []
        return

    def __str__(self):
        """Format the string representation.
        
        return: a string
        """
        rstring  = ""
        paramcount = 0
        
        for param in self._list:
            rstring  += str(paramcount) + ":" + str(param) + "\n"
            paramcount += 1

        if rstring == "":
            rstring += "Empty ParamList\n"

        return rstring


    def __len__(self):
        """Get the number of parameters
        
        return: an integer(the number of parameters)
        """
        return len(self._list)


    def clear(self):
        """Clear myself completely
        """
        for param in self._list:
            param.clear()

        self._list = []
        return


    def delete(self, index=None):
        """Delete parameter(s).

        index -- a general index:
                 if it is an integer, it gives the exact location
                 if it is None, all parameters will be selected
                 if it is a slice parameter, the slice will be selected
        """
        indices = self._range(id)
        indices.sort(reverse=True)
        for i in indices:
            self.owner.removeConstraint(self.key, i)
            self._list.pop(id)
                
        return


    def duplicate(self, parent):
        """Duplicate this ParamList.

        parent:  reference to the new parent 
        """
        import copy
        newcontainer = ParamList(parentparam)

        for parameter in self._list:
            newparameter = parameter.duplicate()
            newcontainer.set(newparameter)

        return newcontainer


    def get(self, index=None):
        """Get an parameter in its parameter list.

        index -- a general index:
                 if it is an integer, it gives the exact location
                 if it is None, all parameters will be selected
                 if it is a slice parameter, the slice will be selected
        return: the parameter(s) 
        """
        # to return a list or a value depends on what the index is
        if isinstance(index, int):
            return self._list[index]        
        if index is None:
            return self._list
        
        # otherwise, it is a slice
        indices = self._range(index)
        return [self._list[i] for i in indices]


    def _range(self, index):
        """Produce a true list of indices.
        None:  all indices
        int:  single index
        slice: a slice of indices
        
        return: a list of indices
        """
        if index is None:
            return list(range(len(self._list)))
        
        if isinstance(index, int):
            return [index]
            
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self._list))
            return list(range(start, stop, step))
            
        raise RietError("An integer, slice or None is required to specify the indices to the parameter(s), but a '%s'=%s is received."%(type(index), str(index)))
        
            
    def set(self, value, index=None):
        """Set the value for parameter(s).
        
        value -- the new value to be set
        index -- a general index:
                 if it is a integer, it gives the exact location
                 if it is None, a new parameter will be added
                 if it is a slice parameter, the slice will be selected        
        """
        if index is None:
            if self.max is None or len(self) < self.max:
                self._list.append(value)
            else:
                raise_(RietError, "The size exceeds the limit: " + str(self.max))
            return
        
        # index has a value
        indices = self._range(index)
        for i in indices:
            # change value and also apply to the constraint
            self._list[i] = value
            
            # Note: Do not set constraint value here!
            # Instead, constraint.setValue will change value here.

        return
    
    
    def listParameters(self, prefix):
        """List the paths to all the Rietveld parameters. '[%i]' is appended for
        a parameter with index 'i'.

        prefix -- a prefix string to be appended
        return: a list of strings
        """
        pathlist = []
        pathlist.extend([prefix+self.key+"[%i]"%i for i in range(len(self._list))])

        return pathlist


# EOF

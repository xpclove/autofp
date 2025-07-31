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

__id__ = "$Id: infoclass.py 6843 2013-01-09 22:14:20Z juhas $"

import numpy

class ParameterInfo:
    """ParameterInfo desribes a paramter or a parameter list.
    
    Data member:
    name        -- the name of the parameter
    description -- the detailed description of the parameter
    default     -- the default value for the parameter
    unit        -- the unit of the parameter
    min         -- the minimal value (None means unlimited)
    max         -- the maximal value (None means unlimited)
    minsize     -- the minimal number of parameters in a parameter list (None means unlimited)
    maxsize     -- the maximal number of parameters in a parameter list (None means unlimited)
    """
    def __init__(self, name, description, default, unit='', min=None, max=None, minsize=1, maxsize=1):
        """Initialization.
        
        name        -- the name of the parameter
        description -- the detailed description of the parameter
        default     -- the default value for the parameter
        unit        -- the unit of the parameter
        min         -- the minimal value (None means unlimited)
        max         -- the maximal value (None means unlimited)
        minsize     -- the minimal number of parameters in a parameter list (None means unlimited)
        maxsize     -- the maximal number of parameters in a parameter list (None means unlimited)
        """
        # check the argument validity
        if minsize is not None and minsize < 0:
            raise ValueError("%s '%s' receives an invalide minsize(%i)."
                            %(self.__class__.__name__, name, minsize))
        if maxsize is not None and maxsize < 0:
            raise ValueError("%s '%s' receives an invalide maxsize(%i)."
                            %(self.__class__.__name__, name, maxsize))
        if minsize is not None and maxsize is not None and minsize > maxsize:
            raise ValueError("%s '%s' receives a minsize(%i) that is greater than the maxsize(%i)."
                            %(self.__class__.__name__, name, minsize, maxsize))
        if min is not None and max is not None and min>max:
            raise ValueError("%s '%s' receives a min(%) that is greater than the max(%s)."
                            %(self.__class__.__name__, name, str(min), str(max)))
                            
        self.name        = name
        self.description = description
        self.unit        = unit
        self.min         = min
        self.max         = max
        self.minsize     = minsize
        self.maxsize     = maxsize

        # convert value in the end.
        self.default     = self.convert(default)

        return


    def __str__(self):
        """Form a string representation.
        
        return: a string
        """
        s =  "name:           " + self.name + "\n"
        s += "description:    " + self.description + "\n"
        s += "type:           " + type(self.default) + "\n"
        s += "default:        " + str(self.default)  + "\n"
        if self.unit:
            s += "unit:           " + self.unit + "\n"
        if self.minsize is not None or self.max is not None:
            # it has min and max value
            s += "range of value: (%s, %s)"%(str(self.minsize), str(self.maxsize)) + "\n"
        if self.minsize != 1 or self.maxsize != 1:
            # it is a list
            s += "range of size:  (%i, %i)"%(self.minsize, self.maxsize) + "\n"
        return s


    def fromStr(self, s):
        """Translate the value from a string or a unicode string.
        
        s    -- a string or a unicode string
        return: a value 
        """
        return s
        

    def convert(self, value):
        """Validate the type of the value and convert the value.
        
        value -- a value to be checked
        
        return: the converted value
        raise: ValueError if the object has the wrong type
        """
        # By default, a parameter can take any value
        return value
        

class BoolInfo(ParameterInfo):
    """BoolInfo desribes a bool paramter or a bool parameter list.
    
    Data members that are inherited from ParameterInfo:
    
    name, description, default, minsize, maxsize
    """
    def __init__(self, name, description, default, minsize=1, maxsize=1):
        """Initialization.
        
        name        -- the name of the parameter
        description -- the detailed description of the parameter
        default     -- the default value for the parameter
        minsize     -- the minimal number of parameters in a parameter list (None means unlimited)
        maxsize     -- the maximal number of parameters in a parameter list (None means unlimited)
        """
        ParameterInfo.__init__(self, name, description, default, minsize=minsize, maxsize=maxsize)
        return


    def fromStr(self, s):
        """Translate the value from a string or a unicode string.
        
        s    -- a string or a unicode string
        return: a value 
        """
        return self.convert(bool(s))
        
        
    def convert(self, value):
        """Validate the type of the value and convert the value.
        
        value -- a value to be checked
        
        return: the converted value
        raise: ValueError if the object has the wrong type
        """
        if not isinstance(value, (numpy.bool_, bool)):
            raise ValueError("'%s' expects an 'bool', but a '%s' is received."%
                            (self.name, type(value)))
        return bool(value)
    
        
class EnumInfo(ParameterInfo):
    """EnumInfo desribes an enumerate paramter or an enumerate parameter list.
    
    Data members that are inherited from ParameterInfo:
    
    name, description, default, minsize, maxsize
    
    Data members that are new:
    
    rangedict: a dictionary that translate a value to a string
    """
    def __init__(self, name, description, default, rangedict, rangelist=None, minsize=1, maxsize=1):
        """Initialization.
        
        name        -- the name of the parameter
        description -- the detailed description of the parameter
        default     -- the default value for the parameter
        rangedict   -- a dictionary that translate a value to a string
        minsize     -- the minimal number of parameters in a parameter list (None means unlimited)
        maxsize     -- the maximal number of parameters in a parameter list (None means unlimited)
        """
        #FIXME: rangelist is not in use, but there are too much hard coded code using this arg.
        # for validate.
        self.rangedict = rangedict
        
        ParameterInfo.__init__(self, name, description, default, minsize=minsize, maxsize=maxsize)
        
        return


    def fromStr(self, s):
        """Translate the value from a string or a unicode string.
        
        s    -- a string or a unicode string
        return: a value 
        """
        return self.convert(int(s))
        

    def convert(self, value):
        """Validate the type of the value and convert the value.
        
        value -- a value to be checked
        
        return: the converted value
        raise: ValueError if the value is not in the list of values
        """
        if value not in self.rangedict:
            raise ValueError("'%s' can only take a value in '%s', but '%s' is received."%
                            (self.name, str(self.rangedict.keys()),  str(value)))
        
        return value


    def getValueStr(self, value):
        """Get the value name.
        
        return: a string
        """
        return self.rangedict[value]


class FloatInfo(ParameterInfo):
    """FloatInfo desribes a float paramter or a float parameter list.
    
    Data members that are inherited from ParameterInfo:
    
    name, description, default, unit, min, max, minsize, maxsize
    """
    def __init__(self, name, description, default, unit='', min=None, max=None, minsize=1, maxsize=1):
        """Initialization.
        
        name        -- the name of the parameter
        description -- the detailed description of the parameter
        default     -- the default value for the parameter
        unit        -- the unit of the parameter
        min         -- the minimal value (None means unlimited)
        max         -- the maximal value (None means unlimited)
        minsize     -- the minimal number of parameters in a parameter list (None means unlimited)
        maxsize     -- the maximal number of parameters in a parameter list (None means unlimited)
        """
        ParameterInfo.__init__(self, name, description, default, unit, min, max, minsize, maxsize)

        return


    def fromStr(self, s):
        """Translate the value from a string or a unicode string.
        
        s    -- a string or a unicode string
        return: a value 
        """
        return self.convert(float(s))
        

    def convert(self, value):
        """Validate the type of the value and convert the value.
        
        value -- a value to be checked
        
        return: the converted value
        raise: ValueError if the value has the wrong type or it is not in the range.
        """
        if not isinstance(value, float) and not isinstance(value, int)\
           and not isinstance(value, long):
            raise ValueError("'%s' expects a'float', but a '%s'=%s is received."%
                            (self.name, type(value), str(value)))
        if ((self.min is not None and value < self.min) or 
            (self.max is not None and value > self.max) ):
            raise ValueError("'%s' receives a value %f out of range (%s, %s)."%
                            (self.name, value, str(self.min), str(self.max)))
                            
        return float(value)



class IntInfo(ParameterInfo):
    """IntInfo desribes an int paramter or an int parameter list.
    
    Data members that are inherited from ParameterInfo:
    
    name, description, default, unit, min, max, minsize, maxsize
    """
    def __init__(self, name, description, default, min=None, max=None, minsize=1, maxsize=1):
        """Initialization.
        
        name        -- the name of the parameter
        description -- the detailed description of the parameter
        default     -- the default value for the parameter
        unit        -- the unit of the parameter
        min         -- the minimal value (None means unlimited)
        max         -- the maximal value (None means unlimited)
        minsize     -- the minimal number of parameters in a parameter list (None means unlimited)
        maxsize     -- the maximal number of parameters in a parameter list (None means unlimited)
        """
        # except for unit, it matches the ParameterInfo arguments, set unit=''
        ParameterInfo.__init__(self, name, description, default, '', min, max, minsize, maxsize)

        return


    def fromStr(self, s):
        """Translate the value from a string or a unicode string.
        
        s    -- a string or a unicode string
        return: a value 
        """
        return self.convert(int(s))
        

    def convert(self, value):
        """Validate the type of the value and convert the value.
        
        value -- a value to be checked
        
        return: the converted value
        raise: ValueError if the object has the wrong type
        """
        if not isinstance(value, int) and not isinstance(value, long):
            raise ValueError("'%s' expects an 'int', but a '%s'=%s is received."%
                            (self.name, type(value), str(value)))
        if ( (self.min is not None and value < self.min) or
             (self.max is not None and value > self.max) ):
            raise ValueError("'%s' receives a value %i out of range (%i, %i)"%
                            (self.name, value, self.min, self.max))
        return int(value)


class RefineInfo(FloatInfo):
    """RefineInfo describes a refinable parameter or a refinable parameter list.
    
    Data members that are inherited from FloatInfo:
    
    name, description, default, unit, min, max, minsize, maxsize

    Data members that are new:
    
    damping
    """
    def __init__(self, name, description, default, damping=0.0, unit='', min=None, max=None, minsize=1, maxsize=1):
        """Initialization.
        
        name        -- the name of the parameter
        description -- the detailed description of the parameter
        default     -- the default value for the parameter
        unit        -- the unit of the parameter
        min         -- the minimal value (None means unlimited)
        max         -- the maximal value (None means unlimited)
        minsize     -- the minimal number of parameters in a parameter list (None means unlimited)
        maxsize     -- the maximal number of parameters in a parameter list (None means unlimited)
        damping     -- the damping 
        """
        FloatInfo.__init__(self, name, description, default, unit, min, max, minsize, maxsize)
        self.damping = damping
        return



class StringInfo(ParameterInfo):
    """StringInfo describes an ascii string parameter or a ascii string parameter list.
    
    Data members that are inherited from FloatInfo:
    
    name, description, default, minsize, maxsize
    
    Data members that are new:
    
    fixlen -- the fixed length measured in bytes
    """
    def __init__(self, name, description, default, fixlen=None, minsize=1, maxsize=1):
        """Initialization.
        
        name        -- the name of the parameter
        description -- the detailed description of the parameter
        default     -- the default value for the parameter
        minsize     -- the minimal number of parameters in a parameter list (None means unlimited)
        maxsize     -- the maximal number of parameters in a parameter list (None means unlimited)
        """
        # self.fixlen is needed by ParameterInfo.__init__ which calls convert
        self.fixlen = fixlen
        
        ParameterInfo.__init__(self, name, description, default, minsize=minsize, maxsize=maxsize)
        
        return


    def fromStr(self, s):
        """Translate the value from a string or a unicode string.
        
        s    -- a string or a unicode string
        return: a value 
        """
        return self.convert(s)
        

    def convert(self, value):
        """Validate the type of the value and convert the value.
        
        value -- a value to be checked
        
        return: the converted value
        raise: ValueError if the object has the wrong type
        """
        import sys

        if sys.version_info.major >= 3:
            if isinstance(value, str):
                # encode using ascii, an error will be thrown in case it is not an ascii.
                value = value.encode()
            elif not isinstance(value, str):
                raise ValueError("'%s' expects a 'str', but a '%s'=%s is received"%
                                (self.name, type(value), repr(value)))


            if self.fixlen and len(value) != self.fixlen:
                raise ValueError("'%s' receives a value '%s' does not match the length."%
                                    (self.name, repr(value)) )
            
        if sys.version_info.major < 3:
            if isinstance(value, unicode):
                # encode using ascii, an error will be thrown in case it is not an ascii.
                value = value.encode()
            elif not isinstance(value, str):
                raise ValueError("'%s' expects a 'str', but a '%s'=%s is received"%
                                (self.name, type(value), repr(value)))


            if self.fixlen and len(value) != self.fixlen:
                raise ValueError("'%s' receives a value '%s' does not match the length."%
                                    (self.name, repr(value)) )
        return value


class UnicodeInfo(ParameterInfo):
    """UnicodeInfo describes a unicode parameter or a unicode parameter list.
    
    Data members that are inherited from FloatInfo:
    
    name, description, default, minsize, maxsize
    """
    def __init__(self, name, description, default, minsize=1, maxsize=1):
        """Initialization.
        
        name        -- the name of the parameter
        description -- the detailed description of the parameter
        default     -- the default value for the parameter
        minsize     -- the minimal number of parameters in a parameter list (None means unlimited)
        maxsize     -- the maximal number of parameters in a parameter list (None means unlimited)
        """
        ParameterInfo.__init__(self, name, description, default, minsize=minsize, maxsize=maxsize)

        return


    def fromStr(self, s):
        """Translate the value from a string or a unicode string.
        
        s    -- a string or a unicode string
        return: a value 
        """
        return self.convert(s)
        

    def convert(self, value):
        """Validate the type of the value and convert the value.
        
        value -- a value to be checked
        
        return: the converted value
        raise: ValueError if the object has the wrong type
        """
        if isinstance(value, str):
            # assume it is an ascii and convert it to unicode
            #NOTE: we may assume it is in other encoding, but it is not essential
            value = unicode(value)
        elif not isinstance(value, unicode):
            raise ValueError("'%s' expects a 'unicode', but a '%s'=%s is received"%
                            (self.name, type(value), repr(value)))

        return value


class ObjectInfo:
    """ObjectInfo describes a BaseClass object or an object list.
    
    Data member:
    name        -- the name of the parameter
    classtype   -- the base class name of this object
    minsize     -- for an object list, it is the minimal number of objects
    maxsize     -- for an object list, it is the maximal number of objects
    
    The current naming scheme requires that the name of a derived class has to 
    start with the name of its base class. This is used to check the validity.
    """
    def __init__(self, name, classtype, minsize=1, maxsize=1):
        """Initialization.
        
        name        -- the name of the parameter
        classtype   -- the base class name of this object
        minsize     -- for an object list, it is the minimal number of objects
        maxsize     -- for an object list, it is the maximal number of objects
        """
        # check the argument validity
        if minsize is not None and minsize < 0:
            raise ValueError("%s '%s' receives an invalide minsize(%i)."
                            %(self.__class__.__name__, name, minsize))
        if maxsize is not None and maxsize < 0:
            raise ValueError("%s '%s' receives an invalide maxsize(%i)."
                            %(self.__class__.__name__, name, maxsize))
        if minsize is not None and maxsize is not None and minsize > maxsize:
            raise ValueError("%s '%s' receives a minsize(%i) that is greater than the maxsize(%i)."
                            %(self.__class__.__name__, name, minsize, maxsize))
        self.name      = name
        self.classtype = classtype
        self.minsize   = minsize
        self.maxsize   = maxsize
    
        return


    def __str__(self):
        """Form a string representation.
        
        return: a string.
        """
        s =  "name:           " + self.name + "\n"
        s += "type:           " + self.classtype + "\n"
        
        if self.minsize != 1 or self.maxsize != 1:
            # it is a list
            s += "range of size:  (%i,%i)"%(self.minsize, self.maxsize) + "\n"

        return s


    def validate(self, obj):
        """Validate the object type.
        
        obj -- object reference
        raise: ValueError if the object has the wrong type.
        """
        classname = obj.__class__.__name__
        if not classname.startswith(self.classtype):
            raise ValueError("%s '%s' expects a '%s', but a '%s' is received."
                            %(self.__class__.__name__, self.name, self.classtype, classname))
        
        return


# EOF

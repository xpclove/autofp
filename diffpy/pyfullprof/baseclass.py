# -*- coding: utf-8 -*-
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

from __future__ import print_function
__id__ = "$Id: baseclass.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.containerclass import *
from diffpy.pyfullprof.exception import *

class BaseClass:
    """BaseClass defines the basic parameters and objects(i.e., subclasses in the 
    SubClassDict and ObjectListDict). The definition can be used for initializing
    and configuring.

    Data member:
    parent  --  the reference to the owner
    """

    ParamDict = {} 
    ParamListDict = {}
    ObjectDict  = {}
    ObjectListDict = {}

    def __init__(self, parent=None):
        """
        Initialization.
        
        parent -- the reference to the owner object.
        """
        # parent and key record the location of the object
        self.parent = parent

        for name,info in self.ParamDict.items():
            self.__dict__[name] = info.default

        for name,info in self.ParamListDict.items():
            self.__dict__[name] = ParamList(self, info.minsize, info.maxsize, name)

        for name in self.ObjectDict.keys():
            self.__dict__[name] = None

        for name,info in self.ObjectListDict.items():
            self.__dict__[name] = ObjectList(self, info.minsize, info.maxsize, name)

        return


    def __str__(self):
        """Form a string representation.
        
        return: a string object
        """
        from diffpy.pyfullprof.infoclass import EnumInfo
        s = "object of class %-10s: \n"%(self.__class__.__name__)
        for name in sorted(self.ParamDict.keys()):
            s += "%-15s: "%(name)
            val = self.__dict__[name]
            info = self.ParamDict[name]
            if isinstance(info, EnumInfo):
                s += "%-20s %-5s\n"%(str(info.getValueStr(val)), str(val))
            else:
                s += "%-20s\n"%(str(self.__dict__[name]))

        for name in sorted(self.ParamListDict.keys()):
            s += name + ":\n"
            subcontainer = self.__dict__[name]
            s += str(subcontainer) + "\n"

        for name in sorted(self.ObjectDict.keys()):
            s += name + ":\n"
            subobject = self.__dict__[name]
            s += str(subobject) + "\n"

        for name in sorted(self.ObjectListDict.keys()):
            s += name + ":\n"
            subcontainer = self.__dict__[name]
            s += str(subcontainer) + "\n"

        return s


    def clear(self):
        """Clear myself completely.
        """
        for v in self.ObjectDict.keys():
            self.__dict__[v].clear()

        for v in self.ObjectListDict.keys():
            self.__dict__[v].clear()

        return


    def delete(self, name, id=None):
        """Delete a parameter(s) or an object(s). 

        name -- the key name in ParamDict/ParamListDic/ObjectDict/ObjectListDict
        id   -- additional object id to delete it from the ObjectListDict
        """
        if name in self.ParamDict:
            self.__dict__[name].clear()
        elif name in self.ParamListDict:
            self.__dict__[name].delete(id)
        elif name in self.ObjectDict:
            self.__dict__[name].clear()
        elif name in self.ObjectListDict:
            self.__dict__[name].delete(id)
            
        return


    def duplicate(self):
        """Make a deep copy of this BaseClass instance and return the copy

        return:  BaseClass instance 
        """
        errmsg = "BaseClass.duplicate is virtual"
        raise NotImplementedError(errmsg)
        return

    @property
    def path(self):
        """Get the full path of the object
        
        return: Dot separated string.
        """
        name  = self.name
        if self.parent:
            path  = self.parent.path
            
            if path:
                return path +'.'+name
            else:
                return name
        
        return name
        
    @property
    def name(self):
        """Get the full name of the constraint, with index
        
        return: a string
        """
        # an object with empty key has no name.
        if not self.key:
            return ''
            
        if self.key in self.parent.ObjectDict:
            return self.key
        if self.key in self.parent.ObjectListDict:
            index = getattr(self.parent, self.key)._list.index(self)
            return '%s[%i]'%(self.key, index)
        
        # else an internal bug
        raise RietError("'%s' is not a valid object of '%s'."%(self.key, self.parent.path), 
                        'Internal Error')
        return 
          

    def getByPath(self, path):
        """Get a value by path
        
        path -- a full path,  e.g., x.y.z[i].a
        return: the value/object corresponding to this address
        """
        # In the case a None or an empty string is passed in
        if not path:
            return self
            
        # If the name has hierarchy, keep breaking it to the end
        if path.count('.') > 0:
            try:
                objpath,paramname = path.rsplit('.',1)
            except ValueError:
                raise RietError('Invalid format for a parameter name: ' + path)

            # The code below check if the return is a list or a single object
            # and handle it accordingly.
            objects = self.getByPath(objpath)
            if isinstance(objects,  list):
                results = []
                for object in objects:
                    result = object.getByPath(paramname)
                    if isinstance(result, list):
                        results.extend(result)
                    else:
                        results.append(result)
                return results
            
            # else it is a single object
            return objects.getByPath(paramname)
 
        # check if the path contains [], i.e., for ObjectListDict or ParamListDict
        name, index = self._parseIndex(path)

        return self.get(name, index)
         

    def setByPath(self, path, value):
        """Set a value by path

        path  -- a full path,  e.g., x.y.z[i].a
        value -- the value/object corresponding to this address
        """
        if not path:
            raise RietError("Path is empty")
            
        if path.count('.') > 0:
            try:
                objpath,paramname = path.rsplit('.',1)
            except:
                raise RietError('Invalid format for a parameter name: ' + path)

            objects = self.getByPath(objpath)
            if isinstance(objects,  list):
                for object in objects:
                    object.setByPath(paramname,  value)
            else:
                objects.setByPath(paramname, value)
            return 

        # check if the path contains [], i.e., for ObjectListDict or ParamListDict
        name, index = self._parseIndex(path)

        self.set(name, value, index)

        return


    def _parseIndex(self, path):
        """Parse a path having a form as ABC[1], without '.'

        path -- the name
        return: name and index
        """
        if path.count('[')==1 and path.count(']')==1:
            import re
            res = re.search(r'([^][]+)\[([0-9:]+)\]',path)
            if res and len(res.groups()) == 2:
                name,index= res.groups()
                
                # The code below build either a slice or an int from the string
                if index.count(':') > 0:
                    # try to make a slice
                    index = slice(*[{True: lambda n: None, False: int}[x == ''](x) 
                                    for x in (index.split(':') + ['', '', ''])[:3]])
                else:
                    index = int(index)
                    
                return name,index
            else:
                raise RietError('Invalid format for a parameter name: ' + name)

        return path, None


    def _rangeParam(self, name, index):
        """Generate a range of indices for the parameter list
        
        name  -- the name in the ParamListDict
        index -- a slice object 
        
        return: a range of slices
        """
        if name not in self.ParamListDict:
            raise RietError('The parameter "%s" is not a list.'%name)
        
        n = len(getattr(self,  name))
        start, stop, step = index.indices(n)
        return range(start, stop, step)     
        

    def get(self, name, index=None):
        """Get a value

        name  --  a key in ParamDict, ParamListDict, ObjectDict or ObjectListDict
        index --  only for ObjectListDict object, to give the location of the object

        return: 1. ParamDict: return the value
                2. ObjectDict: return the RietveldClass object
                3. ObjectListDict: return the RietveldClass object(s)
        """
        if name in self.ParamDict:
            if index is not None:
                raise RietError('The parameter "%s" is not a list.'%name)
            value = self.__dict__[name]
        elif name in self.ParamListDict:
            value = self.__dict__[name].get(index)
        elif name in self.ObjectDict:
            if index is not None:
                raise RietError('The object "%s" is not a list.'%name)
            value = self.__dict__[name]
        elif name in self.ObjectListDict:
            value = self.__dict__[name].get(index)
        else:
            errmsg = "Class '%-15s' does not have '%-15s'"%\
                     (self.__class__.__name__, str(name))
            raise RietError(errmsg)

        # begin python 2 -> python 2 + 3
        import sys
        v  = value
        if sys.version_info[0] >= 3:
            if isinstance(v,bytes):
                v = value.decode("utf-8")
        # return value
        return v
        #end 


    def set(self, name, value, index=None):
        import sys
        """Set the value for a member.

        name  --  a key in ParamDict, ParamListDict, ObjectDict or ObjectListDict
        value --  the value/object to be set
        index --  only for ObjectListDict object, to give the location of the object
        """
        if name in self.ParamDict:
            if index is not None:
                raise RietError('The parameter "%s" is not a list.'%name)

            # begin python 2 - > python 2 + 3
            # To resolve the conflict between Python 2 and Python 3, Python 3 imposes stricter restrictions on attributes, prohibiting the use of setters to access read-only attributes and preventing conflicts in variable names.
            # setattr(self, name, self.ParamDict[name].convert(value))
            if sys.version_info[0] >= 3 and hasattr(type(self), name):
                self.__dict__[name] = self.ParamDict[name].convert(value)  # Python 3
            else:
                setattr(self, name, self.ParamDict[name].convert(value))  # Python 2
            # end

        elif name in self.ParamListDict:
            getattr(self, name).set(self.ParamListDict[name].convert(value),index)
        elif name in self.ObjectDict:
            if index is not None:
                raise RietError('The object "%s" is not a list.'%name)
            self.ObjectDict[name].validate(value)
            object = getattr(self, name)
            if object is not None:
                object.clear()
            
            # setattr(self, name, value)
            if sys.version_info[0] >= 3 and hasattr(type(self), name):
                self.__dict__[name] = value  # Python 3
            else:
                setattr(self, name, value)  # Python 2

            value.parent = self
            value.key = name
            _param_indices = getattr(self.getRoot(), '_param_indices',  None)
            if  _param_indices is not None:
                value.updateParamIndices(_param_indices)
        elif name in self.ObjectListDict:
            self.ObjectListDict[name].validate(value)
            getattr(self, name).set(value, index)
            value.parent = self
            value.key = name
            _param_indices = getattr(self.getRoot(), '_param_indices',  None)
            if  _param_indices is not None:
                value.updateParamIndices(_param_indices)
        else:
            raise RietError("%s does not have the parameter '%s'\n" % \
                     (self.__class__.__name__, name))

        return
        

    def validate(self):
        """Check if the object are valid.
        
        return: True for valid, otherwise False.
        """
        rvalue = True
        
        # 1. check subclass
        for name in self.ObjectDict.keys():
            obj = self.__dict__[name]
            if obj is None:
                rvalue = False
                wmsg = "Warning! Class %-20s: UniObjectList %-20s Not Set-Up"%\
                       (self.__class__.__name__, name)
                print(wmsg)
            else:
                if not obj.validate():
                    rvalue = False

        # 2. check container
        for name in self.ObjectListDict.keys():
            containerobj  = self.__dict__[name]
            objlen = len(containerobj)
            minlen = self.ObjectListDict[name].minsize
            maxlen = self.ObjectListDict[name].maxsize
            if (objlen < minlen):
                print("class " + self.__class__.__name__ + ":\tcontainer " + name + "\t not set-up\n")
                rvalue = False
            for obj in containerobj.get():
                if not obj.validate():
                    rvalue = False

        return rvalue

    
    def getRoot(self):
        '''Get the root object.
        
        return: the root BaseClass object
        '''
        root = self
        while root.parent is not None:
            root = root.parent
        
        return root
        

    def isDescendant(self, object):
        '''Check if it is a descendant of the object, or is the object.
        
        object: a baseclass object
        return: True or False
        ''' 
        node = self
        while node is not object:
            node = node.parent
            if node is None:
                return False
        
        return True
            
        
    def updateParamIndices(self, indices):
        '''Update the global index dictionary to incorporate my parameters.        
        
        indices -- an indexing dictionary 
        '''
        # obtain an index dictionary 

                    
        # update the root index dictionary with child
        for name in self.ParamDict:
            try:
                indices[name.lower()].append((self, name))
            except:
                indices[name.lower()] = [(self, name)]
        
        for name in self.ParamListDict:
            try:
                indices[name.lower()].append((self, name))
            except:
                indices[name.lower()] = [(self, name)]
 
        for name in self.ObjectDict:
            o = getattr(self, name)
            if o:
                o.updateParamIndices(indices)
        
        for name in self.ObjectListDict:
            for p in getattr(self, name)._list:
                p.updateParamIndices(indices)
        
        return
        
                
    def listParameters(self, prefix=''):
        """List the paths to all the Rietveld parameters. 

        prefix -- a prefix string to be appended
        return:  list of strings
        """
        from diffpy.pyfullprof.refine import Refine
        pathlist = []
        for name in sorted(self.ParamDict.keys()):
            pathlist.append(prefix+name)

        for name in sorted(self.ParamListDict.keys()):
            paramlist = self.__dict__[name].listParameters(prefix)
            pathlist.extend(paramlist)

        for name in sorted(self.ObjectDict.keys()):
            if isinstance(self.__dict__[name], Refine):
                continue
            paramlist = self.__dict__[name].listParameters(prefix+name+'.')
            pathlist.extend(paramlist)

        for name in sorted(self.ObjectListDict.keys()):
            paramlist = self.__dict__[name].listParameters(prefix)
            pathlist.extend(paramlist)

        return pathlist


    def locateParameter(self,  name):
        """Find a parameter under this object with the given name.
        
        name -- the parameter name
        return: 1. (None, name) if the name is not found 
                2. (owner, key) where key is the strict name
                3. (owners, keys) where owners is a list of owner and key is a list of keys
        """
        index = getattr(self.getRoot(), '_param_indices',  None)
        if index is not None:
            try:
                values = index[name.lower()]
            except KeyError:
                return None,  name
            
            if self.parent is None:
                # all the values should be under self
                results = values
            else:
                # also check if the results belong to self
                results = []
                for object, name in values:
                    if object.isDescendant(self):
                        results.append((object, name))
                    
            if len(results) < 1:
                return None, name
            elif len(results) == 1:
                return results[0]
            else:
                return ([result[0] for result in results], [result[1] for result in results])
            
        # when there is no global index
        parameters = self.listParameters()

        for parameter in parameters:
            if parameter.count('.') == 0:
                # it is a parameter under fit
                parpath, parname = '', parameter
            else:
                parpath, parname = parameter.rsplit('.', 1)

            if parname.lower() == name.lower():
                return self.getByPath(parpath), parname
        
        return None, name
        
# EOF

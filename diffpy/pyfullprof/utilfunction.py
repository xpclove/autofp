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

__id__ = "$Id: utilfunction.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.exception import RietError

"""
Suite 1:  Utility functions for checking type
"""
def verifyType(value, type, classinstance=None):
    """
    check whether a value is of a certain type

    classinstance   --  an instance of a class has such value
    value           --  a value
    type            --  a built-in data or a class instance
    """
    errortype = False

    if not isinstance(value, type):
        errortype = True

        # an exception for 'float'
        if type == float:
            if isinstance(value, int):
                errortype = False

    if errortype:
        if classinstance is not None:
            estring = classinstance.__class__.__name__
        else:
            estring = ""
        estring += ":  "+str(value)+" is not required type "+str(type)
        raise NotImplementedError(estring)

    return True

"""
Suite 2:    List Operation
"""

"""
Suite 3: Documentation Related
"""
def DocMake(classinstance):
    """
    modify a class variable __doc__ for format output
    the information should include all the parameter, subclass and container information
    
    classinstance:  a class, such as Fit, Phase
    """

    s  = classinstance.__doc__
    if s is None:
        s = classinstance.__name__ 

    s += "\nParameters: \n"
    s += "%-20s %-40s %-10s %-10s\n" % ("Name", "Description", "Type", "Default Value")
    #for info in classinstance.ParamDict.values():
    for key in sorted(classinstance.ParamDict.keys()):
        info = classinstance.ParamDict[key]
        s += info.concise() + "\n"
    s += "\nUniContaineres (1-to-1 relation): \n"
    s += "%-20s %-20s %-10s %-10s\n" % ("Name", "Type", "Min Amount", "Max Amount")
    for key in sorted(classinstance.ObjectDict.keys()):
        info = classinstance.ObjectDict[key]
        s += info.concise() + "\n"
    s += "\nContainers (1-to-n relation): \n"
    s += "%-20s %-20s %-10s %-10s\n" % ("Name", "Type", "Min Amount", "Max Amount")
    for key in sorted(classinstance.ObjectListDict.keys()):
        info = classinstance.ObjectListDict[key]
        s += info.concise() + "\n"

    classinstance.__doc__ = s

    return s


"""
Suite 4: I/O
"""
def checkFileExistence(filename):
    """
    check whether a file does exist in the designated location

    filename:  file name
    """
    try:
        cfile = open(filename, 'r')
        cfile.close()
    except IOError, err:
        print "File << %-20s >> Do NOT Exist:  %-30s"% (filename, err)
        return False

    return True
  
"""
Suite 5: Path Finder
"""
def locateParameterByPath(rietobj, parfullname, srtype="r"):
    """
    according to the parameter's name and path and input Rietveld instance reference,
    locate the Rietveld class instance has this parameter and the name of the parameter

    return  --  2-tuple (RietveldClass_Instance_Refernece, Parameter_Name)

    Arguments:
    - rietobj       :   reference to a RietveldClass object
    - parfullname   :   string of the parameter with full path to locate this parameter from rietobj
    - srtype        :   string, "r" for Rietveld, "l" for Lebail

    Exception
    (1) If cannot find the  next RietveldClass to hold the parameter
    """

    # get path-list
    pathlist = GetPathListFromString(parfullname)

    parName   = pathlist[-1]
    retObj    = rietobj

    index     = 0
    Continue  = True

    returntuple = None

    while Continue:

        # progress
        name   = pathlist[index]
        index += 1

        if name == parName and retObj.ParamDict.has_key(parName):
            # ending case
            returntuple = (retObj, parName)
            Continue    = False             

        elif index == len(pathlist):
            # error case 1:  cannot find parName in the final RietveldClass object
            estring = "utilfunction.locateParameterByPath()   cannot locate parameter " + parfullname
            raise RietError(estring)

        elif retObj.ObjectDict.has_key(name):
            # progress case: subclass
            retObj = retObj.get(name)

        elif retObj.ObjectListDict.has_key(name):
            # progress case: container 
            try:
                seq    = int(pathlist[index])
                retObj = retObj.get(name)[seq]
                index += 1
            except IndexError, err:
                estring  = "utilfunction.locateParameterByPath() Locate parameter " + parfullname + " Error!"
                estring += "RietveldClass "+retObj.__class__.__name__+" has no "+str(seq)+"-th "+name
                estring += str(err)
                raise RietError(estring)
        else:
            print "Parameter with Path and Name:  " + str(parfullname)
            print retObj.ParamDict.keys()
            print "Parameter Name: " + name + "    doesn't match input parameter name " + parName
            print "Last object: " + retObj.__class__.__name__ + "  name = " + str(name)
            #print retObj
            raise NotImplementedError, "path_list: "+str(pathlist)+ " incorrect"

    return returntuple

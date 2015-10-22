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

'''customerized exception definition and handling
'''

__id__ = "$Id: exception.py 6843 2013-01-09 22:14:20Z juhas $"

class RietException(Exception):
    """
    RietException is the virtual base class for all exceptions raised from pyfullprof.core

    Attributes:
    - message:  error message provided from code
    - errortyp: reason for error (standarized)
    """
    def __init__(self, message, errortype, errorId = ""):
        """
        initialization of RietException's derived class;
        but raising an excpetion if any attempt to raise this virtual base class

        message:   string to describe the reason of this exception
        errortype: standard reason for errortype
        errorId: used to identify specific errors, especially when the errors
            are processed in other packages
        """
        if self.__class__.__name__ == "RietException":
            raise NotImplementedError
        else:
            self.message   = message
            self.errortype = errortype
            self.errorId = ""
       
        return


    def __str__(self):
        """
        print out the message and reason of Exception
        """
        rstring  = ""
        rstring += "\nError Type:  %-20s  Message:  %-30s"% (self.errortype, self.message)
        return rstring


class RietError(RietException):
    """
    rietError is all the standard error usually indicating 
    that there must be something wrong in the python scripts

    Attributes:
    - message:  error message provided from code
    - errortyp: reason for error (standarized)
    """
    def __init__(self, message, errortype="Standard Error", errorId = ""):
        """
        initialization
        """
        RietException.__init__(self, message, errortype, errorId)
        
        return

    
class RietPCRError(RietException):
    """
    RietPCRError is the exception raised if the input FullProf pcr is not in good shape

    Attributes:
    - message:  error message provided from code
    - errortyp: reason for error (standarized)
    """
    def __init__(self, message, errortype="RietPCRError", errorId = ""):
        """
        initialization
        """
        RietException.__init__(self, message, errortype, errorId)
        
        return

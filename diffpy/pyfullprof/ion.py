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

'''class Ion - description of anions or cations in the Phase
'''

# NOTE: currently it is only used for pcrFileReader,
# ion information is merged into Atom

__id__ = "$Id: ion.py 6843 2013-01-09 22:14:20Z juhas $"

from diffpy.pyfullprof.rietveldclass import RietveldClass
from diffpy.pyfullprof.infoclass import IntInfo
from diffpy.pyfullprof.infoclass import StringInfo
from diffpy.pyfullprof.utilfunction import verifyType

class Ion(RietveldClass):
    """
    Ion for anion or cation
    """

    ParamDict = {
        "Symbol":   StringInfo("Symbol", "Ion's symbol",  ""),
        "number":   IntInfo("number", "number of ion", 0),
    }
    ObjectDict  = {}
    ObjectListDict = {}


    def __init__(self, parent):
        """
        initialization
        """
        RietveldClass.__init__(self, parent)

        return


    def setIon(self, symnum):
        """
        set ion's information 

        synumber    --  string, the symbol+number, such as O+2
        
        return      --  None
        """
        verifyType(symnum, str)

        # split by + or -
        if symnum.count("+") == 1:
            terms  = symnum.split("+")
            number = int(terms[1])
        elif symnum.count("-") == 1:
            terms = symnum.split("-")
            number = -1*int(terms[1])
        else:
            errmsg = "%-30s: Input parameter 'symnum' is invalid! symnum = %-15s"%\
                     (self.__class__.__name___+".setIon( )", symnum)
            raise RietError, errmsg

        self.set("Symbol", terms[0])
        self.set("number", number)

        return

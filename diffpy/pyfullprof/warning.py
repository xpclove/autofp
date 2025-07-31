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

'''Shared routines that output warnings and error messages.
'''
from __future__ import print_function

__id__ = "$Id: warning.py 6843 2013-01-09 22:14:20Z juhas $"

def warning(message):
    """
    warning:  standard warning

    message:  message to print
    """

    print("%-15s %-40s"%("Warning:", message))

    return


def SystemErrorStyle(block, line, style):
    """
    PCR File Style Error:  Shouldn't Happen
    """
    print("PCR File Style Error at Block " + block + " Line " + line)
    print("Present Style: " + style + " Should be new or old")

    return
    

def PCRFormatItemError(block, line, errmsg):
    """
    PCR File Format Error related with Items in a such line

    block   :   integer for block ordinal number
    line    :   integer for line number in pcr file
    errmsg  :   customized error message
    """
    wstring = "PCR File Format Error Related with Wrong Item Number at Block [%-5s] Line [%-5s]"% \
            (str(block), str(line))
    print("Warning: %-40s"% (wstring))
    print("  Customized Error Message: " + errmsg)

    return

    
def PCRFormatItemError4(block, line, words, itemnumber, flagword):
    """
    PCR File Format Error related with Items in a such line:
    Error if and only the extra number are not number
    """
    # check extra item in words[] is number or not
    exactnumber = len(words)
    if itemnumber >= exactnumber:
        print("No Extra: Less or Equal")
        return False
    # check
    error = False
    for i in xrange(itemnumber, exactnumber):
        if words[i].count(flagword) < 1:
            error = True
        else:
            break;
    if error:
        print("PCR File Format Error Related with Wrong Item Number at Block %-5s Line %-5s"% \
              (block, line))
        print("Error Message: " + str(words))
        print("---5---")

    return


def PCRFormatValueError(block, line, err):
    """
    PCR File Format Error related to Value
    """
    print("PCR File Format Error Related to Value at Block %-5s Line %-5s"% \
          (block, line))
    print("Error Message: " + str(err))

    return

    
def PCRFormatErrorUnknown(block, line, errmsg):
    """
    PCR File Format Error Due to some UNKNONW reason 
    """
    print("PCR File Format Error Due to some UNKNONW reason at Block " + block + " Line " + line)
    print("Error Message: " + errmsg)

    return


def PrintError(err, lineno, linecontent):
    """
    print error message for a certain line in pcr file

    err     :   user-provided error message
    lineno  :   number of line in pcr file where the error is found
    linecontent:    string for the content in this line
    """
    print("Error Message: " + str(err))
    print("Input file format error at Line " + str(lineno) + ": " + str(linecontent))

    return

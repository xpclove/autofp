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

'''Information for all Laue class related
'''

__id__ = "$Id: laue.py 6843 2013-01-09 22:14:20Z juhas $"


class LaueShiftParameter:
    """

    attributes:
    - __laue__
    - __index__
    - __lauelist__
    """

    LaueDict = {
            "-1":   [(2, 0, 0), (0, 2, 0), (0, 0, 2), (0, 1, 1), (1, 0, 1), (1, 1, 0),
                    (4, 0, 0), (0, 4, 0), (0, 0, 4), (2, 2, 0), (2, 0, 2), (0, 2, 2),
                    (2, 1, 1), (1, 2, 1), (1, 1, 2), (3, 0, 1), (3, 1, 0), (1, 3, 0),
                    (1, 0, 3), (0, 1, 3), (0, 3, 1)],
            "-1 2/m 1":
                    [(2, 0, 0), (0, 2, 0), (0, 0, 2), (1, 0, 1),
                    (4, 0, 0), (0, 4, 0), (0, 0, 4), (2, 2, 0), (2, 0, 2), 
                    (0, 2, 2), (1, 2, 1), (1, 0, 3), (0, 1, 3), (0, 3, 1)],
        }

    
    def __init__(self, laue):
        """
        initialization and set the laue class 

        laue: a valid laue class symbol
        """

        self.__laue__ = None
        for name in self.LaueDict.keys():
            if laue == name:
                __laue__ = name
                break;

        if __laue__ is None:
            raise NotImplementedError, "LaueShiftParameter"

        self.__index__    = 0
        self.__lauelist__ = self.LaueDict[__laue__] 

        return


    def get(self):
        """
        return the current __index__ general shift

        return = a 3-int-tuple (h, k, l)
        """

        if self.__index__ < 0:
            raise NotImplementedError, "LaueShiftParameter.get()"

        inttuple = self.__lauelist__[self.__index__]

        self.__index__ += 1

        if self.__index__ >= self.size():
            self.__index__ = -1

        return inttuple


    def reset(self):
        """
        reset the index in the list of generalized shift
        """

        self.__index__ = 0

        return


    def size(self):
        """
        return the size of all generalized shift
        """

        return len(self.__lauelist__)



class LaueStrainModel:
    """

    attributes:
    - __laue__
    - __index__
    - __lauelist__
    """

    LaueDict = {
            "-1":       [(4, 0, 0), (0, 4, 0), (0, 0, 4), (2, 2, 0), (2, 0, 2),
                         (0, 2, 2), (2, 1, 1), (1, 2, 1), (1, 1, 2), (3, 0, 1),
                         (3, 1, 0), (1, 3, 0), (1, 0, 3), (0, 1, 3), (0, 3, 1)],
            "1 2/m 1":  [(4, 0, 0), (0, 4, 0), (0, 0, 4), (2, 2, 0), (2, 0, 2),
                         (0, 2, 2), (1, 2, 1), (3, 0, 1), (1, 0, 3)],
            "1 1 2/m":  [(4, 0, 0), (0, 4, 0), (0, 0, 4), (2, 2, 0), (2, 0, 2),
                        (0, 2, 2), (1, 1, 2), (3, 1, 0), (1, 3, 0)],
            "mmm":      [(4, 0, 0), (0, 4, 0), (0, 0, 4), (2, 2, 0), (2, 0, 2), (0, 2, 2)],
            "4/m":      [(4, 0, 0), (0, 0, 4), (2, 2, 0), (2, 0, 2)],
            "4/mmm":    [(4, 0, 0), (0, 0, 4), (2, 2, 0), (2, 0, 2)],
            "-3R":      [(4, 0, 0), (0, 0, 4), (1, 2, 1), (2, 1, 1)],
            "-3m R":    [(4, 0, 0), (0, 0, 4), (1, 2, 1), (2, 1, 1)],
            "-3":       [(4, 0, 0), (0, 0, 4), (1, 1, 2)],
            "-3m1":     [(4, 0, 0), (0, 0, 4), (1, 1, 2)],
            "-31m":     [(4, 0, 0), (0, 0, 4), (1, 1, 2)],
            "6/m":      [(4, 0, 0), (0, 0, 4), (1, 1, 2)],
            "6/mmm":    [(4, 0, 0), (0, 0, 4), (1, 1, 2)],
            "m3":       [(4, 0, 0), (2, 2, 0)],
            "m3m":      [(4, 0, 0), (2, 2, 0)],
        }

    
    def __init__(self, laue):
        """
        initialization and set the laue class 

        laue: a valid laue class symbol
        """

        self.__laue__ = None
        for name in self.LaueDict.keys():
            if laue == name:
                __laue__ = name
                break;

        if __laue__ is None:
            raise NotImplementedError, "LaueShiftParameter"

        self.__index__    = 0
        self.__lauelist__ = self.LaueDict[__laue__] 

        return


    def get(self):
        """
        return the current __index__ general shift

        return = a 3-int-tuple (h, k, l)
        """

        if self.__index__ < 0:
            raise NotImplementedError, "LaueShiftParameter.get()"

        inttuple = self.__lauelist__[self.__index__]

        self.__index__ += 1

        if self.__index__ >= self.size():
            self.__index__ = -1

        return inttuple


    def reset(self):
        """
        reset the index in the list of generalized shift
        """

        self.__index__ = 0

        return


    def size(self):
        """
        return the size of all generalized shift
        """

        return len(self.__lauelist__)

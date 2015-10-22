#!/usr/bin/env python
##############################################################################
#
# diffpy.pyfullprof by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################


"""Definition of __version__ and __date__ for diffpy.pyfullprof.
"""

# module version
__id__ = "$Id: version.py 6843 2013-01-09 22:14:20Z juhas $"

# obtain version information
from pkg_resources import get_distribution
__version__ = get_distribution('diffpy.pyfullprof').version

# we assume that tag_date was used and __version__ ends in YYYYMMDD
__date__ = __version__[-8:-4] + '-' + \
           __version__[-4:-2] + '-' + __version__[-2:]


# End of file

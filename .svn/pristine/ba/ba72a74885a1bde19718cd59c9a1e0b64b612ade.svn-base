#!/usr/bin/env python
##############################################################################
#
# diffpy.pyfullprof by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 trustees of the Columbia University.
#                   All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""Setup FullProf environment variable if it does not exist yet.
Constants:

FULLPROF         -- absolute path to the FULLPROF installation directory
FULLPROF_PATH    -- system PATH used for executing FULLPROF commands
FULLPROF_ENV     -- system environment dictionary suitable for executing
                FULLPROF commands
"""

# module version
__id__ = "$Id: environment.py 5959 2010-10-29 22:49:43Z yshang $"

import os
import sys
import subprocess
from diffpy.pyfullprof.which import whichall
from diffpy.pyfullprof.exception import RietError

# copy the system environment
FULLPROF_ENV = dict(os.environ)

_mswindows = sys.platform.startswith("win")

# make sure "gsas" variable exists in FULLPROF_ENV and is not empty
if not FULLPROF_ENV.get('FullProf'):
    _gsas_executables = whichall('fp2k')
    if not _gsas_executables:
        emsg = "Fullprof can not find the excutable, please check the system path"
        raise RietError(emsg, errorId = "CANNOT_FIND_EXECUTABLE")
    
    _gsas_real_path = os.path.realpath(_gsas_executables[0])
    FULLPROF_ENV['FullProf'] = os.path.dirname(_gsas_real_path)
FULLPROF_ENV['FULLPROF'] = FULLPROF_ENV['FullProf']

# make sure its exe directory is first in the path
FULLPROF = FULLPROF_ENV['FullProf']

_path_org = FULLPROF_ENV.get('PATH', '').split(os.pathsep)
_path_new = [FULLPROF] + filter(lambda d: d != FULLPROF, _path_org)

FULLPROF_ENV['PATH'] = os.pathsep.join(_path_new)
FULLPROF_PATH = FULLPROF_ENV['PATH']


if _mswindows:
    _startupinfo = subprocess.STARTUPINFO()
    # The attribute STARTF_USESHOWWINDOW is moved under _subprocess in newer
    # version of subprocess package
    flag = []
    try:
        flag.append(subprocess.STARTF_USESHOWWINDOW)
        flag.append(subprocess.SW_HIDE)
    except AttributeError:
        flag.append(subprocess._subprocess.STARTF_USESHOWWINDOW)
        flag.append(subprocess._subprocess.SW_HIDE)
    
    _startupinfo.dwFlags |= flag[0]
    _startupinfo.wShowWindow = flag[1]
else:
    _startupinfo = None


def FullProfSubprocessArgs(**kw):
    '''Return keyword arguments for subprocess calls that run FULLPROF commands.
    By default this defines 'env' and 'startupinfo' arguments.

    kw   -- optional arguments to be added to the returned dictionary

    Return keyword arguments suitable for calling subprocess Popen or call.
    '''
    rv = { 'env' : FULLPROF_ENV,
           'startupinfo' : _startupinfo,
    }
    rv.update(kw)
    return rv

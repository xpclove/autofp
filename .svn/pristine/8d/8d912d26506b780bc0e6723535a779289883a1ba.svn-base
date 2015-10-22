from newversion import *
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from diffpy.pyfullprof.refine import Constraint
from run import Run
from paramlist import ParamList
import paramgroup
from auto import autorun
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class Ui_version(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Ui_version, self).__init__(parent)
        self.ui = Ui_newversion()
        self.ui.setupUi(self)
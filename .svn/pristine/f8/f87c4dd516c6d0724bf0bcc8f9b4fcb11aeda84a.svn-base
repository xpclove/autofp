from ui_output import Ui_output
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import QCheckBox
import setting
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class Ui_output_Form(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Ui_output_Form, self).__init__(parent)
        self.pcr_yorn=False
        self.ui = Ui_output()
        self.ui.setupUi(self)
        self.button_ok=self.ui.pushButton_OK
        self.checkbox_cif=self.ui.checkBox_cif
        self.checkbox_hkl=self.ui.checkBox_hkl
        self.checkbox_fou=self.ui.checkBox_fou
        self.checkbox_list={"Hkl":self.checkbox_hkl,"Cif":self.checkbox_cif,"Fou":self.checkbox_fou}
        self.checklist=setting.run_set.output
        QtCore.QObject.connect(self.button_ok,QtCore.SIGNAL(_fromUtf8("clicked()")),self.ok)   
        self.init(0)
    def init(self,job):
        qc=QCheckBox()
        for i in self.checklist:
            qc=self.checkbox_list[i]
            print self.checklist[i]
            qc.setChecked(self.checklist[i])
        return
    def reset(self):
        return
    def ok(self):
        qc=QCheckBox()
        for i in self.checklist:
            qc=self.checkbox_list[i]
            self.checklist[i]=qc.isChecked()        
        return
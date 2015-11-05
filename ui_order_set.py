from ui_order import Ui_Order
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from diffpy.pyfullprof.refine import Constraint
from run import Run
from paramlist import ParamList
import paramgroup
from auto import autorun
import os
import com
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class Ui_order(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Ui_order, self).__init__(parent)
        self.pcr_yorn=False
        self.ui = Ui_Order()
        self.ui.setupUi(self)
        self.button_up=self.ui.button_up
        self.button_down=self.ui.button_down
        self.buttonreset=self.ui.buttonreset
        self.table=self.ui.table
        self.table.setColumnWidth(0,self.table.width()/1.5)
        self.table.setColumnWidth(1,self.table.width()/3)
        QtCore.QObject.connect(self.button_up,QtCore.SIGNAL(_fromUtf8("clicked()")),self.up)  
        QtCore.QObject.connect(self.button_down,QtCore.SIGNAL(_fromUtf8("clicked()")),self.down)  
        QtCore.QObject.connect(self.buttonreset,QtCore.SIGNAL(_fromUtf8("clicked()")),self.reset)  
        QtCore.QObject.connect(self.ui.button_configure,QtCore.SIGNAL(_fromUtf8("clicked()")),self.set_configure)  
        QtCore.QObject.connect(self.ui.button_save,QtCore.SIGNAL(_fromUtf8("clicked()")),self.set_save)  
        self.init(0)
    def init(self,job):
        self.Pg=paramgroup.Pgs[job]
        self.list=self.Pg.Param_Order_Group_Name
        self.order=range(0,len(self.list))
        self.update_table()
        self.set_save()
    def set_configure(self):
        edit="notepad"
        os.system("notepad "+os.path.join(com.root_path,"setting.txt"))
    def reset(self):
        self.order=range(0,len(self.list))
        self.update_table()
    def update_table(self):
        tablep=self.table
        tablep.setRowCount(0)
        for i in self.order:
            print self.list[i]
            rowcount = tablep.rowCount()
            print rowcount
            tablep.insertRow(rowcount)
            tablep.setCellWidget(rowcount,0,QtGui.QLabel(self.list[i]))
            tablep.setCellWidget(rowcount,1,QtGui.QLabel("parameter"))
    def up(self):
        current_rowcount=self.table.currentIndex().row()
        tmp=self.order[current_rowcount-1]
        print current_rowcount
        self.order[current_rowcount-1]=self.order[current_rowcount]
        self.order[current_rowcount]=tmp
        self.update_table()
    def down(self):
        current_rowcount=self.table.currentIndex().row()
        next=current_rowcount+1
        if(next>=len(self.list)):next=0
        tmp=self.order[next]
        print current_rowcount
        self.order[next]=self.order[current_rowcount]
        self.order[current_rowcount]=tmp
        self.update_table()
    def set_save(self):
        com.run_set.load_setting(path=os.path.join(com.root_path,"setting.txt"))
        self.ui.text_origin_path.setText(com.run_set.origin_path)
        com.origin_path=com.run_set.origin_path
        self.ui.text_asylim.setText(str(com.run_set.AsymLim))
        self.ui.spinbox_ncy.setValue(com.run_set.NCY)
        self.ui.spinbox_eps.setValue(com.run_set.eps*100)
        self.ui.text_fp2k_path.setText(com.run_set.fp2k_path)
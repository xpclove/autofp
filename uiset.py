from ui import Ui_Form
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from diffpy.pyfullprof.refine import Constraint
from run import Run
from paramlist import ParamList
from subauto import SubAutoRun
from ui_order_set import Ui_order
from ui_output_set import Ui_output_Form
from ui_cif2pcr import Ui_makepcr
import copy
import com
import prf2origin.prf2origin.python.prf2origin
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class Ui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Ui, self).__init__(parent)
        self.pcr_yorn=False
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.paramSelect=[]
        self.paramSelect_group=[]
        self.run=Run()
        self.state=0
	self.setAcceptDrops(True)
        #
        self.button_params_ok=self.ui.button_params_ok
        self.tabwidget_run=self.ui.tabwidget_run
        self.params_panel=self.ui.params_widget
        self.control_panel=self.ui.widget
        self.buttonauto=self.ui.Buttonautorun
        self.buttonorder=self.ui.buttonorder
        self.buttonstart = self.ui.buttonrun
        self.buttonback=self.ui.buttonback
        self.button_autoselect=self.ui.buttonautoselect
        self.button_refineall=self.ui.buttonrefineall
        self.button_clearall=self.ui.buttonclearall
        self.button_output=self.ui.buttonoutput
        self.button_fold_paramstable=self.ui.buttonfold
        self.textshow = self.ui.texteditshow
        self.textrwp=self.ui.textrwp
        self.tableprofile = self.ui.tableWidgetprofile
        self.tableatom=self.ui.tableWidgetatom
        self.tableatombiso=self.ui.tableWidgetatombiso
        self.tableins=self.ui.tableWidgetins
        self.tableother=self.ui.tableWidgetother
        self.tableocc=self.ui.tableWidgetocc
        self.tab_refine=self.ui.tabWidgettable
        self.table=[]
        self.table.append(self.tableprofile)
        self.table.append(self.tableins)
        self.table.append(self.tableatom)
        self.table.append(self.tableatombiso)
        self.table.append(self.tableother)
        self.table.append(self.tableocc)
        self.buttonopen=self.ui.buttonopen
        self.window_order=Ui_order()
        self.window_output=Ui_output_Form()
        self.text_path=self.ui.text_path
	self.table_phase=self.ui.spinbox_phase.value()
	icon = QtGui.QIcon()
	icon.addPixmap(QtGui.QPixmap(_fromUtf8("autofp.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	icon.addPixmap(QtGui.QPixmap(_fromUtf8("autofp.ico")), QtGui.QIcon.Normal, QtGui.QIcon.On)
	icon.addPixmap(QtGui.QPixmap(_fromUtf8("autofp.ico")), QtGui.QIcon.Active, QtGui.QIcon.On)
	self.setWindowIcon(icon)
	
        

        self.ui.splitter.resize(self.size())
        self.params_fold=False
        self.show()
        self.fold_paramstable()
        #
        QtCore.QObject.connect(self.ui.pushButton_prf2origin,QtCore.SIGNAL(_fromUtf8("clicked()")),self.prf2origin)
        QtCore.QObject.connect(self,QtCore.SIGNAL(_fromUtf8("close()")),self.stop_autofp)
        QtCore.QObject.connect(self.buttonauto,QtCore.SIGNAL(_fromUtf8("clicked()")),self.autorunfp)
        QtCore.QObject.connect(self.button_autoselect,QtCore.SIGNAL(_fromUtf8("clicked()")),self.auto_select)
        QtCore.QObject.connect(self.button_refineall,QtCore.SIGNAL(_fromUtf8("clicked()")),self.table_select_all)#select all params
        QtCore.QObject.connect(self.button_clearall,QtCore.SIGNAL(_fromUtf8("clicked()")),self.table_clear_all)#clear all params        
        QtCore.QObject.connect(self.buttonstart, QtCore.SIGNAL(_fromUtf8("clicked()")), self.runfullprof)
        QtCore.QObject.connect(self.buttonback, QtCore.SIGNAL(_fromUtf8("clicked()")), self.back)
        QtCore.QObject.connect(self.buttonopen,QtCore.SIGNAL(_fromUtf8("clicked()")),self.openfile)
        QtCore.QObject.connect(self.buttonorder,QtCore.SIGNAL(_fromUtf8("clicked()")),self.open_order)     
        QtCore.QObject.connect(self.button_output,QtCore.SIGNAL(_fromUtf8("clicked()")),self.outputset)      
        QtCore.QObject.connect(self.button_fold_paramstable,QtCore.SIGNAL(_fromUtf8("clicked()")),self.fold_paramstable)        
        QtCore.QObject.connect(self.button_params_ok,QtCore.SIGNAL(_fromUtf8("clicked()")),self.fold_paramstable)
        QtCore.QObject.connect(self.ui.spinbox_phase,QtCore.SIGNAL(_fromUtf8("valueChanged(int)")),self.phase_change)
        QtCore.QObject.connect(self.ui.button_stop,QtCore.SIGNAL(_fromUtf8("clicked()")),self.stop_autofp)
        self.txt_signal.connect(self.showMsg)
        self.autofp_done_signal.connect(self.autorunfp_result)
	self.status_signal.connect(self.showMsg)
        return    
    def fold_paramstable(self):
        if self.params_fold == False:
            control_geo=self.control_panel.geometry();
            self.params_panel_width=control_geo.x();
            form_geo=self.geometry();
            form_geo.setX(form_geo.x()+control_geo.x())
            self.setGeometry(form_geo)
            self.params_panel.hide();
            self.button_fold_paramstable.setText(_fromUtf8("<"))
            self.params_fold=True;
        else:
            form_geo=self.geometry();
            form_geo.setX(form_geo.x()-self.params_panel_width)
            self.setGeometry(form_geo)            
            self.params_panel.show();
            self.button_fold_paramstable.setText(_fromUtf8(">"))
            self.params_fold=False;
    def outputset(self):
        self.window_output.show()
        return
    def prf2origin(self):
	path=self.run.codefile+".prf"
	prf2origin.prf2origin.python.prf2origin.origin=com.origin_path
	self.write(com.origin_path+" "+path)
	prf2origin.prf2origin.python.prf2origin.prf_to_origin(path)
    def open_order(self):
        self.window_order.show()
    def auto_select(self):
	j=0
        for i in self.paramSelect:
            qr=QCheckBox()
            qr=i
            qr.setChecked(True)
	    if self.run.params.get_param_fullname(j).find("_L")!=-1:
		qr.setChecked(False)
	    j+=1
        self.showMsg("Autoselect ok!")
	if self.params_fold==True :
	    self.fold_paramstable()
    def table_clear_all(self):
        self.table_select_all(0)
    def table_select_all(self,arg=1):
        tab=QTabWidget()
        tab=self.tab_refine
        index=tab.currentIndex()
        s=True
        table_select=QTableWidget()
        table_select=self.table[index]
        string="select all param of table " +str(index)
        if arg==0:
            s=False
            string="clear all param of table "+str(index)
        for i in range(0,len(self.paramSelect_group)):
            if self.paramSelect_group[i]==index:
                self.paramSelect[i].setChecked(s)
        self.showMsg(string)
    def phase_change(self,p):
	self.table_phase=self.ui.spinbox_phase.value()
	paramSelect_backup=self.paramSelect
	param_state=[]
	for i in self.paramSelect:
	    param_state.append(i.isChecked())
	self.updateTable()
	for n in range(0,len(self.paramSelect)):
	    self.paramSelect[n].setChecked(param_state[n])
		
	
    def insertParam(self,param_index):
        param=self.run.params.paramlist[param_index]
        table_index=self.run.params.get_param_group(param_index)
        tablep=self.table[table_index]
        qr=QtGui.QCheckBox()
	qr.setStyleSheet("QCheckBox::indicator { width:16px; height:16px; }");
	if self.run.params.get_phase(param_index)==self.table_phase:
	    rowcount = tablep.rowCount()
	    tablep.insertRow(rowcount)
	    tablep.setCellWidget(rowcount,0, QtGui.QLabel(self.run.params.alias[param_index]))
	    tablep.setCellWidget(rowcount,2,QtGui.QLabel(str(param.realvalue)) )
	    tablep.setCellWidget(rowcount,3,qr)        
	if param.codeWord>0:
	    qr.setChecked(True)
        self.paramSelect.append(qr)
        self.paramSelect_group.append(table_index)
        return  
    def autorunfp(self):
        if self.state==0:
            self.write("No Pcr file!")
            return -1
        if self.params_fold==False:
            self.fold_paramstable()
	    
        self.cycle=self.ui.spinBox.value()
	com.run_set.output["Cif"]=self.window_order.ui.checkBox_cif.isChecked()
	com.run_set.eps=self.window_order.ui.spinbox_eps.value()/100.0
	com.run_set.NCY=self.window_order.ui.spinbox_ncy.value()
        self.textrwp.clear()
        self.updateFit(True)
        self.run.writepcr()
        
        self.showMsg("start!")
	com.autofp_running=True;
        subautorun=SubAutoRun()
        subautorun.reset(self.run.pcrfilename,self.param_switch,self.run,self.window_order.order,self.textshow)
        subautorun.run();
    def done_output(self): # auto refinement over!
	rpa_raw=0
	com.des=False
	self.write(" ")
	self.write("weight of phase [phase1, phase2, phase3 ... ]:",style="ok")
	wp=com.wphase.get_w(self.run)
	self.write(str(wp),style="ok")
	self.write("AutoFP version: v_"+com.run_set.setjson["version"])
	if com.run_set.output["Cif"]==True:
	    rpa_raw=self.run.fit.get("Rpa")
	    self.run.fit.set("Rpa",-1)
	    self.run.writepcr()
	    self.run.runfp()
	    self.run.fit.set("Rpa",rpa_raw)
	    self.run.writepcr()
    def autorunfp_result(self,r):
        rwp=r
        self.write("end! \n Rwp="+str(rwp),"ok")
        self.textrwp.setText(str(rwp))
        self.run.resetLoad()
        self.run.push()
	
	# cycles loop
	if com.autofp_running == True:
	    if com.cycle>=self.cycle:
		if self.cycle>0:
		    com.cycle=1
		    self.updateTable()
		    self.done_output()
		if self.cycle==0:
		    if com.des==True or com.cycle>100:
			com.cycle=1
			self.updateTable()
			self.done_output()
			com.des=False
		    else:
			com.cycle=com.cycle+1
			self.autorunfp()		    
	    else:
		com.cycle=com.cycle+1
		self.autorunfp()
	else:
	    self.write("autofp has been stoped by user!",style="warning")
	    com.cycle=1
	    self.updateTable()
	    self.done_output()
	
        self.showMsg(str(com.cycle)+" ok!")
        return
    def closeEvent(self,event):
        result = QtGui.QMessageBox.question(self,
                      "Confirm Exit...",
                      "Are you sure you want to exit ?",
                      QtGui.QMessageBox.Yes| QtGui.QMessageBox.No)
        event.ignore()

        if result == QtGui.QMessageBox.Yes:
	    self.stop_autofp()
	    for p in com.plot.jobs_s:
		p.terminate()
            event.accept()	
    def stop_autofp(self):
	com.autofp_running=False;
	
    def updateFit(self,auto=False):
        self.param_switch=[]
        qr=QCheckBox()
        for i in range(0,self.run.params.param_num):
            qr=self.paramSelect[i]
            self.param_switch.append(qr.isChecked())#for the autorun paramorder
	    print qr.isChecked(),self.run.params.get_param_fullname(i)
            if(auto==False):
                self.run.setParam(i,qr.isChecked())
            else:
                if(qr.isChecked()==False):
                    self.run.setParam(i,qr.isChecked())
                
    def runfullprof(self):
        self.updateFit()
        self.run.writepcr()
        self.run.runfp()
        self.textrwp.setText(str(self.run.Rwp))
        self.showMsg(str(self.run.Rwp))
        self.showMsg("run ok!")
        self.updateTable()
        return
    def openfile(self):
        selectFileNames=QtGui.QFileDialog.getOpenFileNames(None,
                          _fromUtf8("Choose a file name"), ".",
                          _fromUtf8("FullProf PCR File(*.pcr)"))
        if len(selectFileNames)<=0:
            return
	print "open *.pcr: ",selectFileNames[0].toLocal8Bit();path="";
	path=str(selectFileNames[0].toLocal8Bit())#,'gbk',"ignore")
        self.open(path)
    def open(self,path):
        self.state=1
        self.run=Run() # get a new Run() 
        self.showMsg(path+" open")
        self.run.reset(path)
        self.text_path.setText(unicode(path,"gbk","ignore"))
        self.updateTable()
        self.pcr_yorn=True
        self.window_order.init(self.run.job);self.window_order.ui.combobox_job.currentIndex=self.run.job;
        self.tabwidget_run.setEnabled(True)
        return
    txt_signal = QtCore.pyqtSignal(str)
    autofp_done_signal=QtCore.pyqtSignal(float)
    status_signal=QtCore.pyqtSignal(str,str)
    def write(self,s,style="normal"):
	s=com.text_style[style]+s;
        self.txt_signal.emit(s)
    def flush(self):
	return 0
    def write_status(self,s,style="normal"):
        self.status_signal.emit(s,"status")
    def showMsg(self,s,strrwp=" "):
        self.textshow.append(s)
	if strrwp == "status":
	    s=str(s)
	    msg=s.split(':')
	    self.ui.labelpar.setText(msg[1])
	    self.ui.progress.setValue(int(msg[2]))
    def showRwp(self,str):
        self.textrwp.append(str)
    def back(self):
        self.showMsg("back!")
        self.run.back() 
        self.showMsg("step="+str(self.run.step_index))
        self.updateTable()
        self.textrwp.setText(str(self.run.Rwp))
        return
    def updateTable(self):
        for i in range(0,len(self.table)):
            self.table[i].setRowCount(0);
        self.showMsg("update table ok!")
        self.paramSelect=[]
        self.paramSelect_group=[]
        for i in range(0,self.run.params.param_num):
            self.insertParam(i)
                    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()	
    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            newText = ""
            for url in event.mimeData().urls():
                newText +=str(url.toLocalFile())
            self.text_path.setText(newText)
            self.open(newText)
            self.emit(QtCore.SIGNAL("dropped"))
        else:
            event.ignore()
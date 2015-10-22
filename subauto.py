import os
import subprocess
import threading
import auto
from auto import *
#from PyQt4 import QtCore
#from PyQt4.QtCore import *
#import plot
import setting
import params
    
class SubAutoRun(object):
    def __init__(self):
        super(SubAutoRun,self).__init__()
        return
    def reset(self,pcrname,param_switch=None,r=None,param_order_num=None,ui=None):
        self.pcrname=pcrname
        self.param_switch=param_switch
        self.r=r
        self.param_order_num=param_order_num
        self.result=0
        auto.option_this["alt"]=self
        # QtCore.QObject.connect(self,QtCore.SIGNAL(_fromUtf8("complete()")),com.ui,SLOT(_fromUtf8("autorunfp_result()")))
        return
    def complete(self):
        return
    def run(self):
	path=os.path.dirname(self.pcrname)
	pathdes=path+"/backup_"+str(params.getnowtime())
	if os.path.exists(pathdes):
	    shutil.rmtree(pathdes)
        shutil.copytree(path,pathdes,ignore=shutil.ignore_patterns("backup*","tmp*"))
	lists=os.listdir(path)
	for i in lists:
	    if os.path.splitext(i)[1]==".dat":
		shutil.copy(path+"/"+i,path+"/tmp/"+i)
        self.result=0
	if com.run_mode!=0:
	    setting.run_set.show_rwp=com.ui.ui.check_show_rwp.isChecked()
	    setting.run_set.show_log_FP=com.ui.ui.check_show_fp.isChecked()
        if(setting.run_set.show_rwp==True):
            plot.showrwp()
        if(setting.run_set.show_log_FP==True):
            sys.stdout=com.ui
        else:
            sys.stdout=com.sys_stdout
        auto.rwplist=[]
	auto.rwplist_all=[];
        self.result=threading.Thread(target=autorun,args=(self.pcrname,self.param_switch,self.r,self.param_order_num))
        self.result.start()
        return self.result
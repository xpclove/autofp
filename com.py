import sys
import os
import setting
# import plot
import wphase
import prf2origin.prf2origin.python.prf2origin
import paramgroup
run_set=setting.run_set
plot=None
show_plot=plot
sys_stdout=sys.stdout
ui=None
cycle=1 
run_mode=1;
des=False;Rwplist=[];wait=0;
autofp_running=False;
origin_path=setting.run_set.origin_path;root_path=os.getcwd()
mode="ui";
log=None;logstr=""
text_style={"normal":"<font color=blue>",
            "ok":"<font color=green>",
            "warning":"<font color=purple>",
            "error":"<font color=brown>"
            }
def com_init(m):
    global root_path,origin_path,run_set,plot,mode,show_plot,log
    mode=m
    if mode=="ui":
        plot=__import__("plot")
        show_plot=plot
    root_path=os.path.abspath(os.getcwd())
    prf2origin.prf2origin.python.prf2origin.prf2origin_path=os.path.abspath('prf2origin/prf2origin')    
    run_set.load_setting()
    origin_path=run_set.origin_path
    paramgroup.load_strategy()
    #log=open("log.txt","w")
    
    print origin_path,root_path
def com_exit():
    if log!=None:
        log.close()
        log=None
def com_log_write(s):
    global logstr,log
    if log!=None:
        log.write(s+"<br/>")
def com_log_open(path):
    global log
    log=open(path,"w")
def autofp_init():
    plot.jobs_s=[]
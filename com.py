import sys
import os
import setting
# import plot
import wphase
import prf2origin.prf2origin.python.prf2origin
run_set=setting.run_set
plot=None
show_plot=plot
sys_stdout=sys.stdout
ui=None
cycle=1 
run_mode=1;
des=False;Rwplist=[];wait=0;
autofp_running=False;
origin_path=setting.run_set.origin_path;root_path="./"
mode="ui"
text_style={"normal":"<font color=blue>",
            "ok":"<font color=green>",
            "warning":"<font color=purple>",
            "error":"<font color=brown>"
            }
def com_init(m):
    global root_path,origin_path,run_set,plot,mode,show_plot
    mode=m
    if mode=="ui":
        plot=__import__("plot")
        show_plot=plot
    root_path=os.getcwd()    
    prf2origin.prf2origin.python.prf2origin.prf2origin_path=os.path.abspath('prf2origin/prf2origin')    
    run_set.load_setting()
    origin_path=run_set.origin_path
    print origin_path,root_path
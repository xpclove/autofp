import sys
import os
import setting
import plot
import prf2origin.prf2origin.python.prf2origin
import wphase

run_set = setting.run_set
R = {"Rp": 100, "Rwp": 100, "Re": 100, "Chi2": 100}
target = {"string": 'com.R["Rwp"]', "name": 'Rwp'}
plot = None
show_plot = plot
sys_stdout = sys.stdout
ui = None
cycle = 1
run_mode = 1
des = False
Rwplist = []
wait = 0
autofp_running = False
origin_path = setting.run_set.origin_path
root_path = os.getcwd()
mode = "ui"
log = None
logstr = ""
debug = False
autofp_delay = 0
text_style = {"normal": "<font color=blue>",
              "ok": "<font color=green>",
              "rwp": "<font color=green>",
              "warning": "<font color=purple>",
              "error": "<font color=brown>"
              }

import paramgroup
def com_init(m, root=os.getcwd()):
    global root_path, origin_path, run_set, plot, mode, show_plot, log
    mode = m
    if mode == "ui":
        plot = __import__("plot")
        show_plot = plot
    root_path = os.path.abspath(root)
    prf2origin.prf2origin.python.prf2origin.prf2origin_path = os.path.join(
        root_path, 'prf2origin/prf2origin')
    run_set.load_setting(path=os.path.join(root_path, "setting.txt"))
    origin_path = run_set.origin_path
    paramgroup.load_strategy(os.path.join(root_path, "strategy"))
    # log=open("log.txt","w")

    print (origin_path, root_path)


def com_exit():
    if log != None:
        log.close()
        log = None


def com_log_write(s):
    global logstr, log
    if log != None:
        log.write(s+"<br/>")


def com_log_open(path):
    global log
    log = open(path, "w")


def autofp_init():
    plot.jobs_s = []


def debug_print():
    if debug == True:
        0 == 0


def is_file_locked(filepath):
    try:
        fd = os.open(filepath, os.O_WRONLY)
        os.close(fd)
        return False
    except OSError as e:
        return True


def release_process(rp):
    if os.name == "nt":
        # os.system("taskkill /IM fp2k.exe /F")
        os.system("taskkill /PID {} /F".format(rp.pid))
    if os.name == "posix":
        os.system("kill -s 9 ".format(rp.pid))

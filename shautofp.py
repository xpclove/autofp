import cmd
import sys
import subauto
import com
import setting
import threading
import Queue
import doc
import run
import os
import json
tag = "shautofp->"


def cmd_run(argv, argn):
    root_path_abs = os.path.abspath(argv[0])
    root_dir = os.path.split(root_path_abs)
    print root_dir[0]
    cur_dir = os.getcwd()
    os.chdir(root_dir[0])
    # os.chdir("../")
    print "current_dir: ", os.getcwd()
    com.com_init("cmd", os.getcwd())
    os.chdir(cur_dir)
    com.run_mode = 0
    com.ui = com.sys_stdout
    setting.run_set.show_log_FP = False
    setting.run_set.show_rwp = False
    com.mode = "cmd"
    com.autofp_running = True
    if os.name == "nt":
        com.run_set.fp2k_path = "fp2k"
    if os.name == "posix":
        com.run_set.fp2k_path = "./fp2k"

    print argv
    if argn < 2:
        print("Error: the arguments is too few")
        doc.show()
        return
    r = run.Run()
    r.reset(argv[-1])
    flag_autoselect = False
    cycle = 0
    for index, s in enumerate(argv):
        if s == "-c":
            cycle = int(argv[index+1])
            if cycle < 0:
                cycle = 0
            print tag, "cylce=", cycle
        if s == "-a":
            flag_autoselect = True
        if s == "-d":
            n = int(argv[index+1])
            com.wait = n
    print argv[-1]

    autoeng = subauto.SubAutoRun()
    pl = []
    for i in r.params.paramlist:
        if i.name.find("_L") == -1:
            pl.append(True)
        else:
            pl.append(False)
    if flag_autoselect == False:
        for i, p in enumerate(r.params.paramlist):
            pl[i] = False
    print tag, pl
    autoeng.reset(r.pcrfilename, pl, r)
    core = Autofp_Core()
    core.reset(r, pl, autoeng, cycle)
    core.autorunfp()
    params_dic = {}
    print_json(r)
    print tag, "Rwp=", r.Rwp


def print_json(r):
    params_dic = {}
    for p in r.params.paramlist:
        params_dic[p.parname] = p.realvalue
    params_dic["Rwp"] = r.Rwp
    pjson = json.dumps(params_dic)
    out = open("par.txt", "w")
    out.write(pjson)
    out.close()
    # print tag,"Rwp=",r.Rwp
########################################################################


class Autofp_Core:
    """"""
    # ----------------------------------------------------------------------

    def __init__(self):
        """Constructor"""

    def write(self, msg, mode=""):
        print "=>cycle "+str(com.cycle)+": ", msg

    def reset(self, run, pl, subautorun, cycle=0):
        # run=Run(),pl=param_switch,subautorun=SubAutoRun(run),cycle=0
        self.run = run
        self.param_switch = pl
        self.subthread = subautorun
        self.cycle = cycle

    def autorunfp(self):
        thread_wait = self.subthread.run()
        thread_wait.join()
        self.autorunfp_result()

    def done_output(self):
        return

    def autorunfp_result(self):
        self.rwp = self.run.Rwp
        self.write("end! \n Rwp="+str(self.rwp), "ok")
        self.run.resetLoad()
        self.run.push()

        # cycles loop
        if com.autofp_running == True:
            if com.cycle >= self.cycle:
                if self.cycle > 0:
                    com.cycle = 1
                if self.cycle == 0:
                    if com.des == True or com.cycle > 100:
                        com.cycle = 1
                        com.des = False
                    else:
                        com.cycle = com.cycle+1
                        self.autorunfp()
            else:
                com.cycle = com.cycle+1
                self.autorunfp()
        else:
            self.write("autofp has been stoped by user!", style="warning")
            com.cycle = 1
            self.done_output()

        self.write("complete!")
        return


if __name__ == "__main__":
    argv = sys.argv
    argn = len(sys.argv)
    # os.chdir("test")
    # os.system("test.bat")
    # os.chdir("../")
    print(argv)
    cmd_run(argv, argn)

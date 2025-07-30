# -*- coding: utf-8 -*
import paramgroup
from diffpy.pyfullprof.exception import *
from run import *
import shutil
import numpy
import os
import com
# from PyQt4 import QtCore
rwplist = []
rwplist_all = []
rwp_all = []
tag = "auto->"
option_this = {"label": 1,
               "path": "tmp",
               "clear_one": False,
               "clear_all": True,
               "alt": None,
               "rwp": rwplist
               }
# auto rietveld


def autorun(pcrname, param_switch=None, r=None, param_order_num=None, option=option_this):

    if r == None:
        r = Run()
        r.reset(pcrname, "tmp")

    r.fit.set("NCY", com.run_set.NCY)  # set number of circle is NCY
    # sys.stdout=com.ui;
    # print tag,param_switch
    job = r.job  # get the job type of the Run,job=0 Xray; job=1 CW
    Pg = paramgroup.Pgs[job]
    com.target = Pg.target

    # get the order of the params
    if param_order_num == None:
        param_order_num = Pg.Param_Num_Order
    print(param_switch)
    if param_switch == None:
        param_switch = []
        for i in r.params.paramlist:
            param_switch.append(True)

    Pg.get_order(r.params, param_switch, param_order_num)
    order = Pg.order

    tmp_r = 10000
    goodr = 10000
    error = 0
    # print out messenge
    out = open(r.pcrfilename+"_order_out.txt", "w")
    rwplist_out = open(r.pcrfilename+"_rwplist.txt", "w")

    step = 0
    # rietveld according to the order
    for i in order:
        error = 0
        out.write(r.params.get_param_fullname(i)+"\n")
        out.flush()
        r.setParam(i, True)
        r.writepcr()
        param_name = r.params.get_param_fullname(i)

        # try catch the error of the pcr file
        try:
            r.runfp()
            if (option["clear_one"] == True):
                r.setParam(i, False)
            r.writepcr()
        except RietPCRError:
            r.err = 11    # err=11 pcrfile error
        except RietError:
            r.err = 12
        except Exception:
            r.err = 13

        # check error
        com.R = r.R   # target funcrion setting
        exec(com.target["string"])
        target_r = MIN
        if r.err != 0:
            error += 0x01
        if target_r > goodr or target_r != target_r:
            error += 0x10

        # if error back()
        if error > 0:
            # 精修无错误,rwp没减小
            if r.err == 0:
                rwplist_all.append(target_r)
                r.back()
            # 精修有错误,没有保存,故不改变step_index
            if r.err != 0:
                r.back_no_step()

        # if no error
        step += 1
        progress = step*1.0/len(order)*100
        progress = int(progress)
        out_str = "autofp_status:"+param_name+":"+str(progress)
        out_str = com.text_style["normal"]+out_str

        if com.mode == "ui":
            com.ui.write_status(out_str)
        if error == 0:
            goodr = target_r
            if com.mode == "ui":
                com.ui.write("step = "+str(r.step_index))
                com.ui.write(param_name)
                com.ui.write(com.target["name"]+": " +
                             str(target_r)+"\n", style="ok")
                com.ui.write("Rwp= "+str(r.R["Rwp"]), style="ok")
                com.ui.write(str(r.R), style="ok")
                if com.autofp_delay > 0:
                    com.time.sleep(com.autofp_delay)
            Rwp = r.R["Rwp"]
            rwplist.append(Rwp)
            rwplist_all.append(Rwp)
            com.Rwplist.append(Rwp)
            numpy.savetxt("rwp.txt", numpy.array(rwplist))
            numpy.savetxt("rwp_all.txt", numpy.array(rwplist_all))
            numpy.savetxt("rwplist.txt", numpy.array(com.Rwplist))
            out.write("step:    "+str(r.step_index)+"\n")

        out.write(str(error)+"\n")
        out.write(str(target_r)+"\n")
        out.flush()
        tmp_r = target_r

        # autofp is stoped ?
        if com.autofp_running == False:
            break
        if com.wait > 0:
            time = __import__("time")
            time.sleep(com.wait)

    out.close()

    print(goodr)
    option["alt"].complete()
    com.ui.write("complete !\n")

    if (option["clear_all"] == True):
        for i in order:
            r.setParam(i, False)
        r.writepcr()

    r.runfp()  # run FP to create the PRF
    
    print("rwp:", rwplist)
    for i in rwplist:
        rwplist_out.write(str(i)+"\n")
    rwplist_out.close()
    numpy.savetxt("OK.txt", rwplist)

    if rwplist != []:
        if abs(rwplist[-1]-rwplist[0]) < setting.run_set.eps:
            com.des = True
    if rwplist == []:
        com.des = True
    if (com.run_set.rm_tmp_done == True):
        shutil.rmtree(r.tmpdir)
    if (com.run_set.show_rwp == True):
        com.show_plot.show_stable(rwplist)
    if com.run_mode > 0:
        com.ui.autofp_done_signal.emit(goodr)
    rwp_all.append(rwplist)

    print(rwp_all)  # The good Rwp of all cycles
    # numpy.savetxt("rwp_all_cycles.txt",numpy.array(rwp_all))

    return goodr


if __name__ == "__main__":
    pcr = "y2o3"
    copyfile(pcr+"/"+pcr+".pcr", "auto/"+pcr+".pcr")
    copyfile(pcr+"/"+pcr+".dat", "auto/"+pcr+".dat")
    copyfile(pcr+"/"+pcr+".out", "auto/"+pcr+".out")
    autorun("auto/"+pcr+".pcr")

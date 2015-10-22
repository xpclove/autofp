# -*- coding: utf-8 -*
import paramgroup
from diffpy.pyfullprof.exception import *
from run import *
import shutil
import numpy
import os
import com
from PyQt4 import QtCore
rwplist=[];
rwplist_all=[];
rwp_all=[];
option_this={ "label": 1,
         "path" : "tmp",
         "clear_one": False,
         "clear_all": True,
         "alt":None,
         "rwp":rwplist
}
#auto rietveld
def autorun(pcrname,param_switch=None,r=None,param_order_num=None,option=option_this):
    if r == None:
       r = Run()
       r.reset(pcrname, "tmp")
    r.fit.set("NCY",15) #set number of circle is 15
    # sys.stdout=com.ui;

    job=r.job #get the job type of the Run,job=0 Xray; job=1 CW
    Pg=paramgroup.Pgs[job]
    
    # get the order of the parameters
    if param_order_num==None:
       param_order_num=Pg.Param_Num_Order   
    print param_switch
    if param_switch==None:
        param_switch=[]  
        for i in r.params.paramlist:
            param_switch.append(True)
    
    Pg=paramgroup
    Pg.get_order(r.params,param_switch,param_order_num,job)
    order=Pg.order
    
    tmprwp=10000
    goodrwp=10000
    error=0
    
    # the out messenge
    out=open(r.pcrfilename+"_order_out.txt","w")
    rwplist_out=open(r.pcrfilename+"_rwplist.txt","w")
    step=0;
    
    # rietveld refinement according to the order
    for g_n in range(len(order)):
        n_param=len(order[g_n])
        for i in order[g_n]:
            error=0
            out.write(r.params.get_param_fullname(i)+"\n")
            out.flush() 
            r.setParam(i,True)
            r.writepcr()
            param_name=r.params.get_param_fullname(i)
            #try catch the error of the pcr file
            try:
                r.runfp()
                if(option["clear_one"]==True):r.setParam(i,False)
                r.writepcr()
            except RietPCRError:
                r.err=11    # err=11 pcrfile error
            except RietError:
                r.err=12
            except Exception:
                r.err=13
                
            #check error
            if r.err!=0:
                error+=0x01
            if r.Rwp>goodrwp or r.Rwp !=r.Rwp:
                error+=0x10
                
            #if error back()
            if error > 0:
                # 精修无错误,rwp没减小
                if r.err == 0 :
                    rwplist_all.append(r.Rwp)
                    r.back()
                # 精修有错误,没有保存,故不改变step_index
                if r.err != 0 :
                    r.back_no_step()
                    
            #if no error
            step+=1
            progress=step*1.0/len(order)*100
            progress=int(progress)
            #com.ui.write_status("autofp_status:"+param_name+":"+str(progress))
            if error==0:
                if com.ui != None:
                    goodrwp=r.Rwp
                    com.ui.write("step = "+str(r.step_index))
                    com.ui.write(param_name)
                    com.ui.write("Rwp="+str(r.Rwp)+"\n")
                rwplist.append(r.Rwp);
                rwplist_all.append(r.Rwp);
                numpy.savetxt("rwp.txt",numpy.array(rwplist))
                numpy.savetxt("rwp_all.txt",numpy.array(rwplist_all))
                out.write("step:    "+str(r.step_index)+"\n") 
                
            out.write(str(error)+"\n")
            out.write(str(r.Rwp)+"\n")
            out.flush()
            tmprwp=r.Rwp
    # end refinement
    
    # rwplist 
    out.close()
    print(goodrwp)
    option["alt"].complete()
    #com.ui.write("complete !\n")
    if(option["clear_all"]==True):
        for i in order:
            r.setParam(i,False)
        r.writepcr()
    r.runfp() # run FP to create the PRF
    print "rwp:",rwplist
    for i in rwplist:
        rwplist_out.write(str(i)+"\n")
    rwplist_out.close()
    numpy.savetxt("OK.txt",rwplist)
    
    # ui show
    if rwplist!=[]:
        if abs(rwplist[-1]-rwplist[0])<setting.run_set.eps:
            com.des=True
    if rwplist==[]:
        com.des=True
    if(com.run_set.rm_tmp_done==True):
        shutil.rmtree(r.tmpdir)
    if(com.run_set.show_rwp==True):
        com.show_plot.show_stable(rwplist)
    #if com.run_mode>0:
        #com.ui.autofp_done_signal.emit(goodrwp)
    rwp_all.append(rwplist)
    print rwp_all # The good Rwp of all cycles
    
    return goodrwp
if __name__ == "__main__":
    pcr="y2o3"
    copyfile(pcr+"/"+pcr+".pcr","auto/"+pcr+".pcr")
    copyfile(pcr+"/"+pcr+".dat","auto/"+pcr+".dat")
    copyfile(pcr+"/"+pcr+".out","auto/"+pcr+".out")    
    autorun("auto/"+pcr+".pcr")
    
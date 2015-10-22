import os
import run
########################################################################
class setting:
    """"""
    show_rwp=True
    show_log_FP=True
    AsymLim=60
    NCY=10                          # NCY: cycle in edpcr
    eps=0.1                         # eps: limit of zero
    Atom_Aniso_Temp_Enable=False
    Atom_Aniso_Temp=True
    rm_tmp_done=False
    origin_path="";
    output={"Hkl":False,
            "Cif":False,
            "Fou":False
           }

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
    def load_setting(self,path="setting.txt"):
        setting_file=open(path,"r")
        context_set=setting_file.readlines()
        context=[]
        i=""
        for i in context_set:
            value=i.split('=')[1]
            context.append(value)
        
        setting_file.close()
        i=0
        self.show_rwp=(bool)(context[i]);i+=1;
        self.show_log_FP=(bool)(context[i]);i+=1;
        self.AsymLim=(int)(context[i]);i+=1;
        self.origin_path=context[i];i+=1;
        return
    def save_setting(self,path="setting.txt"):
        setting_file=open(path,"w")
        setting_file.write(str(self.show_rwp)+"\n")
        setting_file.write(str(self.show_log_FP)+"\n")
        setting_file.write(str(self.AsymLim)+"\n")
        setting_file.close()
run_set=setting()        
        
    
    
import os
import sys
import paramgroup
class ParamList:
    '''
    Param_Dict = [
        ["Scale", "BACK", "Shape1", "Bov", "U", "V", "W", "GausSiz", "LorSiz", "Pref1", "Pref2"], 
        ["Zero", "Sycos", "Sysin", "Lambda"],
        ["X","Y","Z","Occ","Biso","B11","B22","B33","B13","B23", "B12", "a", "b", "c", "alpha", "beta", "gamma"],
        ["Str1","Str2","Str3","PA1","PA2","PA3","PA4","S_L","D_L"]
        
    ] # now don't use Param_Dict ,now use paramgroup.Param_Group
    '''
    def __init__(self,paramlist,job=0,fit=None):
        self.paramlist= None
        self.fullname=[]
        self.alias=[]
        self.param_group = []
        self.param_phase=[]
        self.paramlist=paramlist
        self.param_num=len(self.paramlist)
        self.Pg=paramgroup.Pgs[job] #?paramgroup_job
        self.fit=fit
        phase=0
        atom_sig=0
        for i in self.paramlist:
            varfullname=i.name+"-"+i.type
            if varfullname.find("X-Atom[0]")!=-1:
                atom_sig+=1
                if atom_sig>1:
                    phase+=1
            # varfullname+="-phase["+str(phase)+"]"
            self.fullname.append(varfullname)
            self.param_phase.append(phase)
        
        self.param_onoff_list=[]
        self.get_all_param_onoff()
        self.get_all_alias()
        self.subgroup()
        return
    def get_phase(self,index):
        varfn=self.param_phase[index]
        return varfn
    def get_param_group(self, index):
        return self.param_group[index]
    def get_param_fullname(self,index):
        return self.fullname[index]
    def get_param_value(self,index):
        value=self.paramlist[index].getValue()
        return value
    def get_all_alias(self):
        Pg=paramgroup
        for i in range(0,len(self.paramlist)):
            name=""
            name=self.get_param_fullname(i)
            name=Pg.name_to_alias(name,self.get_phase(i),self.fit)
            self.alias.append(name)
        Pg.atom=-1
        Pg.back=-1
            
    def subgroup(self):
        group=self.Pg.Param_Group #get group
        for i in range(0,self.param_num):
            tmp = False
            for j in range(0, len(group)):
                if str(self.paramlist[i].parname) == "Occ":
                    if "Atom_Occ" in group[j]:
                        self.param_group.append(j)
                        tmp=True
                        # print "select parameter: ",self.paramlist[i].parname,j #print debug msg
                else:
                    if self.paramlist[i].type.split('[')[0] in group[j]:
                        self.param_group.append(j)
                        tmp = True
            if tmp ==  False:
                self.param_group.append(len(group)-2)
    def get_param_onoff(self,index):
        if self.paramlist[index].codeWord>0:
            return 1#1 is on
        else:
            return 0#0 is off
            
    def get_all_param_onoff(self):
        i=0
        while(i<self.param_num):
            self.param_onoff_list.append(self.get_param_onoff(i))
            i=i+1
        return    
    def set_all_param_onoff(self,boollist):
        i=0
        while (i<self.param_num):
            if boollist[i]==True:
                self.turnon_param(i)
            else:
                self.turnoff_param(i)
            i=i+1
        self.get_all_param_onoff()
        return
    def get_param_codeword(self,index):
        if index>self.param_num or index<0:
            return -1
        codeword=self.paramlist[index].codeWord
        return codeword
    def set_param_codeword(self,index,codeword):
        if index>self.param_num or index<0:
            return -1
        self.paramlist[index].codeWord=codeword
        return 
    def turnon_param(self,index):
        if self.get_param_onoff(index)==0:
            self.set_param_codeword(index,1.0)
        self.get_all_param_onoff()
        return
    def turnoff_param(self,index):
        if self.get_param_onoff(index)==1:
            self.set_param_codeword(index,0.0)
        self.get_all_param_onoff()
        return
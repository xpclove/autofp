import sys
import os
import shutil
from run import Run
from pcrfilehelper import pcrFileHelper
def get(a=100):
    print a
ss="./test/pbso_cw_back/pbso4a.pcr"
sp="./test/pbso_cw/pbso4a.pcr"
pf="./test/pf/y2o3_2.pcr"
pp="./test/cvo/cvo.pcr"
s=pp
r=pcrFileHelper()
r.readFromPcrFile(s)
params=r.fit.getParamList()
for i in params:
    print i.parname,i.type,i.name,i.getValue(),"=",i.realvalue
    
#ri=Run()
#ri.reset(ss)
#print ri.params.fullname
#print "phase num=",len(r.fit.get("Phase"))
#print r.fit.get("Phase")[1].get("Jbt")
#print r.fit.get("Contribution")[0]
#for i in ri.fit.get("Pattern"):
    #print i.get("Job")
#print ri.fit.get("Sho")
#print ri.params.alias
#print ri.fit.get("Phase")[0].get("ATZ")
import os
import shutil
import format
script_path=os.path.abspath("../origin/script/")
def prf_xy(path,des):
    file=open(path);
    outfile=open(des,"w")
    outfile.write(format.xy_head+"\n")
    outlines=[]
    context=file.readlines()
    line=""
    for n,line in enumerate(context):
        pos=line.find("2Theta");
        if pos!=-1:
            break
    n_start=n+1
    line=context[n_start]
    line_data=line.split()
    brag_pos=float(line_data[-2])/3
    for n in range(n_start,len(context)):
        line=context[n]
        if line.find("(")!=-1:
            break
        line_data=line.split()
        linestr=""
        for i,num in enumerate(line_data):
            if i>0 and i < len(line_data)-1:
                linestr+=line_data[0]+"  "+line_data[i]+"  "
        outlines.append(linestr)
    j=0
    while n < len(context):
        line=context[n]
        line_data=line.split()
        if line_data[1]!="1":
            phase=int(line_data[-1])
            phase_magnetic=int(line_data[-2])
            bragg=int(line_data[1])
            #bragg=bragg*phase+phase_magnetic*0.5*bragg
            bragg=brag_pos+bragg
            linestr=" "+line_data[0]+"  "+str(bragg)+"  "
        outlines[j]+=linestr
        j+=1
        n+=1
    for line in outlines:
        outfile.write(line+"\n")
    outfile.close()
def prf2origin_(prf,origin):
    prfdir=os.path.dirname(prf)
    datpath=prfdir+"/origin.dat"
    prf_xy(prf,datpath)
    
    cur_path=os.getcwd()
    path=script_path+"/prf_one.cpp"
    path=os.path.abspath(path)
    datepath=os.path.abspath(datpath)    
    os.chdir(script_path)
    cmd="start "+origin+" -RS run.loadOC("+path+", 16);;stringarray aa;aa.Add("+datepath+");test(aa)"
    os.system(cmd)
    # os.system("test.bat \""+datepath+"\" \""+path+"\" \""+origin+"\"")
    print cmd
    print "prf2origin complete!"
    os.chdir(cur_path)
if __name__=="__main__":
    prf2origin_("tmp/test.prf")
import os
import shutil
import sys
def release(option=["pyc"]):
    arglen=len(sys.argv)
    outdir="release"
    if(os.path.exists("release")):       
        shutil.rmtree("release")  
    os.mkdir("release")
    os.mkdir("release/auto")
    infile=open("release.ini","r")
    line=""
    all_line=infile.readlines()
    for line in all_line:
        linec=line.strip('\n')
        ss=linec.split("@");
        if (ss[0] == "d"):
            shutil.copytree(ss[1],outdir+"/"+ss[1])
            continue
        if (ss[0] == "f"):
            shutil.copyfile(ss[1],outdir+"/"+ss[1])
            continue
        linepy=line.strip('\n')+".py"
        line=linepy+"c"
        print(line)
        if("src" in option):
            shutil.copyfile(linepy,"release/"+linepy)
        shutil.copyfile(line, "release/"+line)
    infile.close()
if __name__ == "__main__":
    release()
    
    
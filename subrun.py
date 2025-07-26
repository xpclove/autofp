import subprocess
import os
import com
class SubRun:
    def __init__(self):
        return
    def reset(self,ins,arg,err):
        self.ins=ins
        self.arg=arg
        self.err_string=err
        self.result=0
        return
    
    def run(self):
        self.result=0
        print("OS, mode=",os.name, com.mode)

        if com.mode == "ui":
            if os.name=="nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                self.rp=subprocess.Popen([self.ins,self.arg],stdout=subprocess.PIPE,startupinfo=startupinfo)
            else:
                self.rp=subprocess.Popen([self.ins,self.arg],stdout=subprocess.PIPE)
        if com.mode == "cmd":
            if os.name=="nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE        
                self.rp=subprocess.Popen([self.ins,self.arg],stdout=subprocess.PIPE,startupinfo=startupinfo, shell=True)
            else:
                self.rp=subprocess.Popen([self.ins,self.arg],stdout=subprocess.PIPE)

        outstr="q";
        while self.rp.poll()==None: 
            outstr=self.rp.stdout.readline()
            if outstr.find(self.err_string)!=-1:
                self.rp.kill()
                self.result=-30
            if outstr.find("Rwp")!=-1:
                print(">>>"+outstr)

        
        print("fp2k is finished")
        return self.result
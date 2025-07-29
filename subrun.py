import subprocess
import signal
import time
import os
import com


class SubRun:
    def __init__(self):
        return

    def reset(self, ins, arg, err):
        self.ins = ins
        self.arg = arg
        self.err_string = err
        self.result = 0
        return

    def run(self):
        self.result = 0
        print("OS, mode=", os.name, com.mode)

        if com.mode == "ui":
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                self.rp = subprocess.Popen(
                    [self.ins, self.arg], stdout=subprocess.PIPE, startupinfo=startupinfo)
            else:
                self.rp = subprocess.Popen(
                    [self.ins, self.arg], stdout=subprocess.PIPE)

        if com.mode == "cmd":
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                self.rp = subprocess.Popen(
                    [self.ins, self.arg], stdout=subprocess.PIPE, startupinfo=startupinfo, shell=True, bufsize=1)
            else:
                self.rp = subprocess.Popen(
                    [self.ins, self.arg], stdout=subprocess.PIPE)

        while self.rp.poll() == None:
            outstr = self.rp.stdout.readline()
            if outstr.find(self.err_string) != -1:
                self.result = -30
            if outstr.find("Rwp") != -1:
                print(">>>"+outstr)
                if outstr.find("NaN") != -1:
                    self.result = -34
            # kill subprocess and fp2k when meet error
            if self.result != 0:
                self.rp.terminate()
                self.rp.kill()
                fp2k_name = os.path.basename(self.ins)
                if os.name =="nt":
                    os.system("taskkill /IM {} /F".format(fp2k_name))
                if os.name =="posix":
                    os.system("pkill -f {}".format(fp2k_name))
        self.rp.wait()

        print("fp2k is finished with error {}".format(self.result))
        return self.result

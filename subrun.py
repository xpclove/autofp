import subprocess
import signal
import time
import os
import com
import sys

n_debug = 0

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
        try:
            if com.mode == "cmd":
                if os.name == "nt":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    
                    if sys.version_info[0] >= 3:
                        self.rp = subprocess.Popen(
                            [self.ins, self.arg], stdout=subprocess.PIPE, startupinfo=startupinfo, shell=True,  universal_newlines=True)
                    else:
                        self.rp = subprocess.Popen(
                        [self.ins, self.arg], stdout=subprocess.PIPE, startupinfo=startupinfo, shell=True, bufsize=1)
                else:
                    self.rp = subprocess.Popen(
                        [self.ins, self.arg], stdout=subprocess.PIPE)

            
            while self.rp.poll() == None:

                if sys.version_info[0] >= 3:
                    outstr = self.rp.stdout.readline()
                else:
                    outstr = self.rp.stdout.readline().decode("utf-8")

                if outstr.find(self.err_string) != -1:
                    self.result = -30
                if outstr.find("Rwp") != -1:
                    print(">>>"+outstr)
                    if outstr.find("NaN") != -1:
                        self.result = -34
                # kill subprocess and fp2k when meet error
                if self.result != 0:
                    print("fp2k meet error, please wait fp2k exit ... ")
                    self.rp.terminate()
                    self.rp.kill()
                    fp2k_name = os.path.basename(
                        self.ins)  # get fp2k prcocess name
                    if os.name == "nt":
                        # os.system("taskkill /PID {} /F".format(self.rp.pid))
                        os.system("taskkill /IM {} /F".format(fp2k_name))
                        # os.system(u"taskkill /IM {}(32 *) /F".format(fp2k_name).encode("gbk"))
                    if os.name == "posix":
                        os.system("pkill -f {}".format(fp2k_name))
                    break

            self.rp.wait()

        except Exception as e:
            print("rp error!")
            sys.exit(-1)
        
        print(">>> fp2k is finished.")
        if self.result != 0:
            print(">>> fp2k error {}".format(self.result))
        
        # global n_debug
        # n_debug += 1
        # if n_debug >= 30  :
        #     sys.exit(0)

        return self.result

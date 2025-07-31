import sys
import os
import shutil
from pcrfilehelper import pcrFileHelper
from diffpy.pyfullprof.fpoutputfileparsers import FPOutFileParser
from diffpy.pyfullprof.fit import Fit
from paramlist import ParamList
from outfilecheckerror import check
from subrun import SubRun
import setting
import com

# Define the errors during the fullprof refinement process of autofp.
error_info = {
    1: "out file error",
    0: "no error",
    -1: "no out file",
    -30: "error in run and break",
    -31: "asym error",
    -32: "no rwp in out file",
    -33: "Singular matrix",
    -34: "Rwp = NaN",
    -10:  "no rwp task"
}


class Run:
    def __init__(self):
        return
    # reset Run

    def reset(self, pcrfilename, tmp_dir_path="tmp"):
        self.tmp_path = "/"+tmp_dir_path+"/"
        self.pcrRW = None
        self.outR = None
        self.fit = None
        self.params = None
        self.err = 0
        self.step_index = -1
        self.errmsg = ""
        self.job_name = pcrfilename
        self.Rwp = 10000
        self.R = {"Rp": 0, "Rwp": 0, "Re": 0, "Chi2": 0}

        # file pcr and out
        self.pcrfilename = os.path.realpath(pcrfilename)
        self.outfilename = os.path.splitext(self.pcrfilename)[0]+".out"
        self.codefile = os.path.splitext(self.pcrfilename)[0]
        self.dirname = os.path.dirname(self.pcrfilename)
        self.base_pcrfilename = os.path.basename(self.pcrfilename)
        self.base_outfilename = os.path.basename(self.outfilename)
        self.tmpdir = os.path.dirname(self.pcrfilename)+self.tmp_path
        shutil.copyfile(self.pcrfilename, self.pcrfilename+"_back")

        if os.path.exists(self.tmpdir) == False:
            os.mkdir(self.tmpdir)
        os.chdir(self.dirname)  # change the dir to the pcr dir
        self.resetLoad()

        if self.err != 0:
            print(error_info[self.err])

        self.runfp()
        self.push()  # the number 0 version
        shutil.copy(self.pcrfilename, self.pcrfilename +
                    "_back")  # backup the pcrfile
        return

    def resetLoad(self):
        self.pcrRW = pcrFileHelper()

        try:
            self.pcrRW.readFromPcrFile(self.pcrfilename)
        except Exception as e:
            print(Exception, ":", e, "in run.py resetload")
            return -0x80

        self.fit = self.pcrRW.fit
        self.job = self.fit.get("Pattern")[0].get("Job")  # get the type of job
        self.datafile = self.fit.get("Pattern")[0].get(
            "Datafile")  # the name of data file
        self.phase_num = len(self.fit.get("Phase"))

        if self.job == 0:
            asylim = self.fit.get("Pattern")[0].get("AsymLim")
            if asylim < 5:
                asylim = setting.run_set.AsymLim
            self.fit.get("Pattern")[0].set("AsymLim", asylim)

        if self.job == 2:
            self.err = -10  # no Rwp task

        if setting.run_set.Atom_Aniso_Temp_Enable == True:
            for atom_i in self.fit.get("Phase")[0].get("Atom"):
                atom_i.set("N_t", 2)

        # the absolute path of the data file
        self.real_datafile = os.path.splitext(self.pcrfilename)[0]+".dat"

        # read outfile and get Rwp
        if os.path.exists(self.outfilename) == False:
            self.throwerr(-1, "no out file ")
        elif self.err >= 0:
            self.outR = FPOutFileParser(self.pcrRW.fit, self.outfilename)
            if self.outR.getStatus() == False:
                self.throwerr(1, "out file error")
            elif self.err == 0:
                self.Rwp = self.getRwp()
        # end read outfile

        self.params = ParamList(self.fit.getParamList(), self.job, self.fit)

        return self.err

    def runfp(self):
        self.err = 0
        subrun = SubRun()
        fp2k_path = com.run_set.fp2k_path
        subrun.reset(fp2k_path, self.base_pcrfilename,
                     "not saved to the current PCR file:")
        self.err = subrun.run()

        if self.err == 0:
            self.err += check(self.outfilename)
            self.err += self.resetLoad()
            print("test1")

        # only save the right result
        if (self.err == 0):
            self.push()

    # get the Rwp
    def getRwp(self, num=-1):
        if num < 0:
            num = self.getCycleNum()+num+1
        if self.err == 0:
            Rwp = self.outR.getResidues(num)[0][1]
            r_factor = self.outR.getResidues(num)[0]
            self.R = {"Rp": r_factor[0], "Rwp": r_factor[1],
                      "Re": r_factor[2], "Chi2": r_factor[3]}
            return Rwp

    def getCycleNum(self):
        if self.err == 0:
            Num = self.outR.getNumCycles()
            return Num

    # ----------------------------------------------------------------------
    def back_no_step(self):
        self.back(0)
        #   step=0 represent only pop but step_index don't change

    def back(self, step=1):
        self.err = 0
        if self.step_index < 0:
            return
        if self.step_index-step < 0:
            step = self.step_index
        print("back", self.step_index, step)
        self.pop(step)
        self.resetLoad()
        return

    def push(self):
        self.step_index += 1
        tmp = self.tmpdir+"step="+str(self.step_index)
        copyfile(self.pcrfilename, tmp+".pcr")
        copyfile(self.outfilename, tmp+".out")
        return

    def pop(self, step=1):
        n = step
        if self.step_index == 0:
            n = 0
        tmp = self.tmpdir+"step="+str(self.step_index-n)

        print(">>> pop <<<", tmp)
        if com.is_file_locked(self.outfilename):
            print("file is use[pop]", self.outfilename)
            input()
        if (os.path.exists(tmp+".pcr")):
            copyfile(tmp+".pcr", self.pcrfilename)
        if (os.path.exists(tmp+".out")):
            copyfile(tmp+".out", self.outfilename)
        else:
            self.throwerr(-1, "no out file")
        self.step_index -= step

        if self.step_index < 0:
            self.step_index = 0
            
        return 1

    # write to pcr
    def writepcr(self):
        self.pcrRW.writeToPcrFile(self.pcrfilename)
        return

    def setParam(self, index, code=False):
        if code == False:
            self.params.turnoff_param(index)
        else:
            self.params.turnon_param(index)
        return

    def throwerr(self, errcode, str):
        self.err = errcode
        self.errmsg = str
        print(self.errmsg)


def copyfile(source, destin):
    shutil.copyfile(source, destin)

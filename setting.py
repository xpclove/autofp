import os
import run
import json
import re
########################################################################


class setting:
    """"""
    show_rwp = True
    show_log_FP = True
    AsymLim = 60
    NCY = 10                          # NCY: cycle in edpcr
    eps = 0.1                         # eps: limit of zero
    Atom_Aniso_Temp_Enable = False
    Atom_Aniso_Temp = True
    rm_tmp_done = False
    origin_path = ""
    setjson = {}
    fp2k_path = "./fp2k"
    output = {"Hkl": False,
              "Cif": False,
              "Fou": False
              }
    show_rwp_limit = 0
    # ----------------------------------------------------------------------

    def __init__(self):
        """Constructor"""

    def load_setting(self, path="setting.txt"):
        '''
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
        '''
        try:
            setting_file = open(path, "r")
            setstr = setting_file.read()
            setstr = re.sub(r"\b\\\b", r"\\\\", setstr)
            setstr = re.sub(r":\\\b", r":\\\\", setstr)
            self.setjson = json.loads(setstr)
            setting_file.close()
        except Exception, e:
            print "setting.txt error! load setting_default.txt."
            path = "setting_default.txt"
            setting_file = open(path, "r")
            self.setjson = json.load(setting_file)
            setting_file.close()
        self.show_rwp = self.setjson["show_rwp"]
        self.show_log_FP = self.setjson["show_log_FP"]
        self.NCY = self.setjson["NCY"]
        self.AsymLim = self.setjson["AsymLim"]
        self.eps = self.setjson["eps"]
        self.fp2k_path = self.setjson["fp2k_path"]

        # Set the default location of fp2k.
        if self.fp2k_path == "fp2k":
            script_dir = os.path.dirname(os.path.abspath(__file__))
            print("Current dir of fp2k: ", script_dir)
            if os.name == "nt":
                self.fp2k_path = "fp2k.exe"
            if os.name == "posix":
                self.fp2k_path = "fp2k"
            self.fp2k_path = os.path.join(script_dir,self.fp2k_path)


        self.origin_path = self.setjson["origin_path"]

        return

    def save_setting(self, path="setting.txt"):
        setting_file = open(path, "w")
        '''
        setting_file.write(str(self.show_rwp)+"\n")
        setting_file.write(str(self.show_log_FP)+"\n")
        setting_file.write(str(self.AsymLim)+"\n")
        '''
        json.dump(self.setjson, setting_file, indent=1)
        setting_file.close()


run_set = setting()

import os
import json
setting_file_name="setting_release.txt"
msifolder="AutoFP-SetupFiles"
setting_file=open(setting_file_name)
setting=json.load(setting_file)
print setting["version"]
version=setting["version"]
os.chdir(msifolder)
os.system("zip.bat "+version)
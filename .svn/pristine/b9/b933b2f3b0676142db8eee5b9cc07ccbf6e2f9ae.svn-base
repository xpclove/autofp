import shutil
import time
import os
import release_core
if __name__ == "__main__":
    print("prepare autofp_pkg .")
    os.mkdir("autofp_pkg")
    shutil.copytree("dist","autofp_pkg/dist")
    shutil.copytree("example","autofp_pkg/example")
    shutil.copytree("imageformats","autofp_pkg/dist/imageformats")
    shutil.copy("readme.txt","autofp_pkg/readme.txt")
    shutil.copy("fp2k.exe","autofp_pkg/dist/fp2k.exe")
    shutil.copy("convert.exe","autofp_pkg/dist/")
    shutil.copy("ffmpeg.exe","autofp_pkg/dist/")
    shutil.copy("msvcp90.dll","autofp_pkg/dist/")
    shutil.copy("msvcr90.dll","autofp_pkg/dist/")
    shutil.copy("autofp.ico","autofp_pkg/dist/")
    shutil.copy("setting_release.txt","autofp_pkg/dist/setting.txt")
    shutil.copytree("prf2origin/prf2origin/origin","autofp_pkg/dist/prf2origin/prf2origin/origin")
    t=time.time()
    print("copy autofp_pkg to autofp_date ... ")
    s=time.strftime("autofp_%Y_%m_%d",time.localtime(t))
    if(os.path.exists(s)):       
        shutil.rmtree(s)      
    os.rename("autofp_pkg",s)
    print("copyt autofp_date/dist to AutoFP/dist ...... ")
    if(os.path.exists("AutoFP/dist")):shutil.rmtree("AutoFP/dist")
    shutil.copytree(s+"/dist","AutoFP/dist")
    
    
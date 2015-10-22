import os
import prf2xy
origin='F:\OriginLabOriginPro\Origin9.exe'
prf2origin_path='F:\prf2origin\prf2origin'
def prf_to_origin(prf):
    prf2xy.script_path=prf2origin_path+'/origin/script'
    prf2xy.prf2origin_(prf,origin)
if __name__=="__main__":
	prf_to_origin("tmp/test.prf")
    
import time

outdata_time=0

def gettime():
    t=time.time()
    s=time.strftime("%Y%m%d",time.localtime(t))
    timenow=int(s)
    return timenow

def getnowtime():
    t=time.time()
    s=time.strftime("%Y-%m-%d/%H-%M-%S",time.localtime(t))
    return s    
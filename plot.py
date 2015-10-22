import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy
import os
import multiprocessing
import com
fig = plt.figure("Rwp")
#fig.suptitle("Rwp")
axes1 = fig.add_subplot(111)
axes1.set_xlabel("step");axes1.set_ylabel("Rwp");axes1.set_title(" Rwp curve")
job=None
ani=None
rwpdata=None
jobs_s=[]
def update(d):
    #line.set_xdata(data[0])
    #line.set_ydata(data[1])
    line, = axes1.plot(d[1],'go-',linewidth=0.3,markersize=10,markerfacecolor='red')
    if os.path.exists("ok.txt"):
        os.remove("ok.txt")
        plt.close()
    return line,
def data_gen():
    #n=len(auto.rwplist)
    #data=[n,auto.rwplist]
    if os.path.exists("rwp.txt"):
        data=numpy.loadtxt("rwp.txt")
        data=data.tolist()
    else:
        data=[0]
    data=[data,data]
    rwpdata=data
    yield data
def show(dg=None,cycle=1):
    global data,ani;
    global axes1;
    #fig = plt.figure()
    #axes1 = fig.add_subplot(111)
    axes1.set_xlabel("step");axes1.set_ylabel("Rwp");axes1.set_title("Cycle "+str(cycle)+" Rwp curve")    
    if(dg==None):dg=data_gen
    ani = FuncAnimation(fig, update, dg, interval=100)
    plt.show()
def showrwp(s=None):
    global axes1
    global fig
    if s == None: s="."
    os.chdir(s);
    cycle=com.cycle;
    axes1.set_xlabel("step");axes1.set_ylabel("Rwp");axes1.set_title("Cycle "+str(cycle)+" Rwp curve")
    job=multiprocessing.Process(target=show,args=(None,cycle))
    job.start()
    jobs_s.append(job)
def show_stable(data):
    job=multiprocessing.Process(target=show_data,args=(data,com.cycle))
    job.start()
    jobs_s.append(job)
def show_data(rwplist,cycle=1):
    line, = axes1.plot(rwplist,'go-',linewidth=0.3,markersize=10,markerfacecolor='red')
    axes1.set_xlabel("step");axes1.set_ylabel("Rwp");axes1.set_title("Cycle "+str(cycle)+" Rwp curve")        
    plt.show()
if __name__=="__main__":
    multiprocessing.freeze_support()
    show()


import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy
import os
import multiprocessing
import com
import json
import textwrap

plt.rcParams['text.antialiased'] = True
rwpdata = None

g_figs={}
g_stop_events={}
jobs_s = []

'''
(1) Rwp dynamic image
'''
def update(data):
    key = multiprocessing.current_process().name
    cycle,fig,axes1,ani,stop_event = g_figs[key]
    
    if data != None:
        line, = axes1.plot(data[1], 'go-', linewidth=0.3,
                        markersize=10, markerfacecolor='red')
        '''plot good param mark'''
        if com.run_set.show_rwp_param == True:
            for index, value in enumerate(data[0]):
                mark = value
                offset = len(mark) * 5
                pos_x = index
                pos_y = 0
                if index <len(data[1]):
                    pos_y = data[1][index]
                an = axes1.annotate(mark,  
                            xy=(pos_x, pos_y),
                            xytext=(0, offset,),  
                            textcoords='offset points',
                            fontsize= 8,
                            family="monospace",
                            color='black',
                            rotation=90,
                            multialignment='center'
                            )
                an.set_fontstyle('italic')
                an.set_fontweight('light')
        ''''''
    if stop_event.is_set():
        ani.event_source.stop()

    return line,

def data_gen():
    key = multiprocessing.current_process().name
    cycle,fig,axes1,ani,stop_event = g_figs[key]
    data = None
    key = "cycle_{}".format(cycle)
    js = json.load(open("autofp.log"))
    if key in js:
        data_rwplist = js[key]["rwplist"]
        data_rwplist_param = js[key]["rwplist_param"]
        data = [ data_rwplist_param, data_rwplist]
    yield data


def show(stop_event, cycle=1):
    fig = plt.figure("Rwp Cycle {}".format(cycle))
    axes1 = fig.add_subplot(111)
    
    axes1.set_xlabel("Step")
    axes1.set_ylabel("Rwp")
    axes1.set_title("Cycle "+str(cycle)+" Rwp curve")
    ani = FuncAnimation(fig, update, data_gen, interval=100)

    key = multiprocessing.current_process().name
    g_figs[key] = (cycle, fig, axes1, ani, stop_event)

    plt.show()
    
    return

def showrwp(s=None):
    if s == None:
        s = "."
    os.chdir(s)
    cycle = com.cycle
    stop_event = multiprocessing.Event()
    job = multiprocessing.Process(target=show, args=(stop_event, cycle))
    job.start()
    jobs_s.append(job)
    g_stop_events[cycle]=stop_event


'''
(2) Rwp static image
'''
def show_stable(data):
    job = multiprocessing.Process(target=show_data, args=(data, com.cycle))
    job.start()
    jobs_s.append(job)


def show_data(rwplist, cycle=1):
    fig_static = plt.figure("Rwp Cycle {}".format(cycle))
    axes1 = fig_static.add_subplot(111)
    line, = axes1.plot(rwplist, 'go-', linewidth=0.3,
                       markersize=10, markerfacecolor='red')
    axes1.set_xlabel("step")
    axes1.set_ylabel("Rwp")
    axes1.set_title("Cycle "+str(cycle)+" Rwp curve")

    '''
    plot good param mark
    '''
    js = json.load(open("autofp.log"))
    key = "cycle_{}".format(com.cycle)
    if key in js:
        data_rwp_param = js[key]["rwplist_param"]
        d=[ data_rwp_param, rwplist]
        if com.run_set.show_rwp_param == True:
            for index, value in enumerate(d[0]):
                mark = value
                offset = len(mark) * 5
                pos_x = index
                pos_y = 0
                if index <len(d[1]):
                    pos_y = d[1][index]
                an = axes1.annotate(mark,  
                            xy=(pos_x, pos_y),
                            xytext=(0, offset,),  
                            textcoords='offset points',
                            fontsize= 8,
                            family="monospace",
                            color='black',
                            rotation=90,
                            multialignment='center'
                            )
                an.set_fontstyle('italic')
                an.set_fontweight('light')
    ''''''

    plt.show()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    show()

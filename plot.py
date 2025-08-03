import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy
import os
import multiprocessing
import com
import json
import textwrap
import time

plt.rcParams["text.antialiased"] = True
rwpdata = None

g_stop_events = {}
jobs_s = []

"""
(1) Rwp dynamic image
"""


def update(data, axes1, cycle):

    if len(data) > 0:
        (line,) = axes1.plot(
            data[1], "go-", linewidth=0.3, markersize=10, markerfacecolor="red"
        )
        """plot good param mark"""
        if com.run_set.show_rwp_param == True:
            for index, value in enumerate(data[0]):
                mark = value
                offset = len(mark) * 5
                pos_x = index
                pos_y = 0
                if index < len(data[1]):
                    pos_y = data[1][index]
                an = axes1.annotate(
                    mark,
                    xy=(pos_x, pos_y),
                    xytext=(
                        0,
                        offset,
                    ),
                    textcoords="offset points",
                    fontsize=8,
                    family="monospace",
                    color="black",
                    rotation=90,
                    multialignment="center",
                )
                an.set_fontstyle("italic")
                an.set_fontweight("light")
        """"""
    return axes1.lines or []


def data_gen(stop_event, cycle):
    data = []
    while not stop_event.is_set():
        try:
            with open("autofp.log") as f:
                js = json.load(f)
                key = "cycle_{}".format(cycle)
                if key in js:
                    data_rwplist = js[key]["rwplist"]
                    data_rwplist_param = js[key]["rwplist_param"]
                    data = [data_rwplist_param, data_rwplist]
                yield data
        except Exception as e:
            print("error: {}".format(e))
            yield data
        time.sleep(0.05)


def show(stop_event, cycle=1):
    fig = plt.figure("Rwp Cycle {}".format(cycle))
    axes1 = fig.add_subplot(111)
    axes1.set_xlabel("Step")
    axes1.set_ylabel("Rwp")
    axes1.set_title("Cycle " + str(cycle) + " Rwp curve")

    ani = FuncAnimation(
        fig,
        update,
        frames=data_gen(stop_event, cycle),
        fargs=(axes1, cycle),
        interval=100,
    )

    plt.show(block=False)
    plt.pause(0.1)
    while not stop_event.is_set():
        fig.canvas.flush_events()
        time.sleep(0.01)
    ani.event_source.stop()
    plt.show()
    # plt.close(fig)
    return


def show_Rwp_animation(dir=None):
    if dir == None:
        dir = "."
    os.chdir(dir)
    cycle = com.cycle
    stop_event = multiprocessing.Event()
    job = multiprocessing.Process(target=show, args=(stop_event, cycle))
    job.start()
    jobs_s.append(job)
    g_stop_events[cycle] = stop_event


"""
(2) Rwp static image
"""


def show_stable(data):
    job = multiprocessing.Process(target=show_data, args=(data, com.cycle))
    job.start()
    jobs_s.append(job)


def show_data(rwplist, cycle=1):
    fig_static = plt.figure("Rwp Cycle {}".format(cycle))
    axes1 = fig_static.add_subplot(111)
    (line,) = axes1.plot(
        rwplist, "go-", linewidth=0.3, markersize=10, markerfacecolor="red"
    )
    axes1.set_xlabel("step")
    axes1.set_ylabel("Rwp")
    axes1.set_title("Cycle " + str(cycle) + " Rwp curve")

    """
    plot good param mark
    """
    js = json.load(open("autofp.log"))
    key = "cycle_{}".format(com.cycle)
    if key in js:
        data_rwp_param = js[key]["rwplist_param"]
        d = [data_rwp_param, rwplist]
        if com.run_set.show_rwp_param == True:
            for index, value in enumerate(d[0]):
                mark = value
                offset = len(mark) * 5
                pos_x = index
                pos_y = 0
                if index < len(d[1]):
                    pos_y = d[1][index]
                an = axes1.annotate(
                    mark,
                    xy=(pos_x, pos_y),
                    xytext=(
                        0,
                        offset,
                    ),
                    textcoords="offset points",
                    fontsize=8,
                    family="monospace",
                    color="black",
                    rotation=90,
                    multialignment="center",
                )
                an.set_fontstyle("italic")
                an.set_fontweight("light")
    """"""

    plt.show()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    g_figs = multiprocessing.Manager().dict()
    show()

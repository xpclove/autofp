from queue import Empty
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import multiprocessing
import com
import json
import time

plt.rcParams["text.antialiased"] = True

g_stop_events = {}
jobs_s = []

"""
(1) Rwp dynamic image
"""


def update(data, axes1, run_set, cycle):

    if len(data) > 0:
        (line,) = axes1.plot(
            data[1], "go-", linewidth=0.3, markersize=10, markerfacecolor="red"
        )
        """plot good param mark"""
        if run_set.show_rwp_param == True:
            for index, value in enumerate(data[0]):
                mark = value
                offset = +10
                pos_x = index
                pos_y = data[1][index] if index < len(data[1]) else 0
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
                    verticalalignment="bottom",
                    # textcoords="data",
                    fontsize=9,
                    family="sans-serif",
                    color="#333366",
                    rotation=90,
                    multialignment="center",
                )
                an.set_fontstyle("italic")
                an.set_fontweight("light")
        """"""
    return axes1.lines or []


def parse_json(js, cycle):
    data = []
    key = "cycle_{}".format(cycle)
    if key in js:
        data_rwplist = js[key]["good_rwplist"]
        data_rwplist_param = js[key]["good_rwplist_param"]
        data = [data_rwplist_param, data_rwplist]
    return data


# This function is used to generate data from a log josn file
def data_gen_file(stop_event, cycle):
    data = []
    while not stop_event.is_set():
        try:
            with open("autofp.log") as f:
                js = json.load(f)
                data = parse_json(js, cycle)
                yield data
        except Exception as e:
            print("error: {}".format(e))
            yield data
        time.sleep(0.05)


# using multi process queue communication to enhance data interaction
def data_gen_queue(stop_event, queue, cycle):
    data = []
    old_data = data
    while not stop_event.is_set():
        try:
            js_txt = queue.get(timeout=0.01)
            js = json.loads(js_txt)
            data = parse_json(js, cycle)
            old_data = data
            yield old_data
        except Empty:
            # print("com.mp_queue: empty")
            yield old_data
        time.sleep(0.01)
    max = 5
    while max > 0:
        yield old_data
        time.sleep(0.2)
        max -= 1


def show(stop_event, com_var, cycle=1):
    fig = plt.figure("Rwp Cycle {}".format(cycle))
    axes1 = fig.add_subplot(111)
    axes1.set_xlabel("Step")
    axes1.set_ylabel("Rwp")
    axes1.set_title("Cycle " + str(cycle) + " Rwp curve")

    ani = FuncAnimation(
        fig,
        update,
        # frames=data_gen_file(stop_event, cycle),
        frames=data_gen_queue(stop_event, com_var["queue"], cycle),
        fargs=(axes1, com_var["run_set"], cycle),
        interval=200,
    )

    plt.show(block=False)
    plt.pause(0.1)
    while not stop_event.is_set():
        plt.pause(0.1)
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
    com_var = {"queue": com.mp_queue, "run_set": com.run_set}
    job = multiprocessing.Process(target=show, args=(stop_event, com_var, cycle))
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

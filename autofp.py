import os
# Solve the scaling issue for high DPI displays
import ctypes
if os.name == "nt":
    ctypes.windll.shcore.SetProcessDpiAwareness(0)

from uiset import Ui
from run import Run
import sys
import com
import params
import newversion_set
import thread
import time
import multiprocessing
import shautofp
import plot
from PyQt4 import QtCore, QtGui


def start_autofp():
    app = QtGui.QApplication(sys.argv)
    com.com_init("ui")
    if (params.gettime() > 21160831):
        print("Find a new version , please download ...  ")
        p = newversion_set.Ui_version()
        p.show()
        sys.exit(app.exec_())
    r = Run()
    window = Ui()
    com.ui = window
    window.run = r
    window.show()
    sys.exit(app.exec_())


def showmsg(msg):
    window.showMsg(msg)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    if len(sys.argv) > 1:
        shautofp.cmd_run(sys.argv, len(sys.argv))
        sys.exit()
    start_autofp()

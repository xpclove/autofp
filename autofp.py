# Solve the scaling issue for high DPI displays
from PyQt4 import QtCore, QtGui
import plot
import shautofp
import multiprocessing
import time
import thread
import newversion_set
import params
import com
import sys
from run import Run
from uiset import Ui
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(0)


def start_autofp():
    app = QtGui.QApplication(sys.argv)
    com.com_init("ui")
    if (params.gettime() > 21160831):
        print "find a new version , please download ...  "
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

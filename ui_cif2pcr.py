# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cif2pcr.ui'
#
# Created: Mon May 02 16:36:04 2016
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_makepcr(object):
    def setupUi(self, makepcr):
        makepcr.setObjectName(_fromUtf8("makepcr"))
        makepcr.resize(500, 300)
        self.centralwidget = QtGui.QWidget(makepcr)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 461, 141))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_1 = QtGui.QWidget()
        self.tab_1.setObjectName(_fromUtf8("tab_1"))
        self.tabWidget.addTab(self.tab_1, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(390, 230, 91, 31))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.comboBox = QtGui.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(10, 160, 131, 22))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        makepcr.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(makepcr)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 500, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        makepcr.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(makepcr)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        makepcr.setStatusBar(self.statusbar)

        self.retranslateUi(makepcr)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(makepcr)

    def retranslateUi(self, makepcr):
        makepcr.setWindowTitle(_translate("makepcr", "MainWindow", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("makepcr", "1->1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("makepcr", "n->1", None))
        self.pushButton.setText(_translate("makepcr", "make", None))
        self.comboBox.setItemText(0, _translate("makepcr", "Xray", None))
        self.comboBox.setItemText(1, _translate("makepcr", "Neutron", None))


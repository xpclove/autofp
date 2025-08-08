# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cif2pcr.ui'
#
# Created: Fri Aug  8 12:05:06 2025
#      by: PyQt4 UI code generator 4.11
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
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Noto Sans SC"))
        makepcr.setFont(font)
        self.centralwidget = QtGui.QWidget(makepcr)
        self.centralwidget.setGeometry(QtCore.QRect(0, 0, 491, 261))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 461, 141))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Noto Sans SC"))
        font.setPointSize(10)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_1 = QtGui.QWidget()
        self.tab_1.setObjectName(_fromUtf8("tab_1"))
        self.tabWidget.addTab(self.tab_1, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(390, 210, 91, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Noto Sans SC"))
        font.setPointSize(10)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.comboBox = QtGui.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(10, 160, 131, 22))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Noto Sans SC"))
        font.setPointSize(10)
        self.comboBox.setFont(font)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.menubar = QtGui.QMenuBar(makepcr)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 500, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.statusbar = QtGui.QStatusBar(makepcr)
        self.statusbar.setGeometry(QtCore.QRect(0, 0, 3, 21))
        self.statusbar.setObjectName(_fromUtf8("statusbar"))

        self.retranslateUi(makepcr)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(makepcr)

    def retranslateUi(self, makepcr):
        makepcr.setWindowTitle(_translate("makepcr", "MainWindow", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("makepcr", "1->1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("makepcr", "n->1", None))
        self.pushButton.setText(_translate("makepcr", "Make", None))
        self.comboBox.setItemText(0, _translate("makepcr", "Xray", None))
        self.comboBox.setItemText(1, _translate("makepcr", "Neutron", None))


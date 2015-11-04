# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'output.ui'
#
# Created: Sun Feb 08 01:57:25 2015
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

class Ui_output(object):
    def setupUi(self, output):
        output.setObjectName(_fromUtf8("output"))
        output.resize(510, 296)
        output.setStyleSheet(_fromUtf8(""))
        self.pushButton_OK = QtGui.QPushButton(output)
        self.pushButton_OK.setGeometry(QtCore.QRect(430, 260, 75, 23))
        self.pushButton_OK.setObjectName(_fromUtf8("pushButton_OK"))
        self.tab_widget = QtGui.QTabWidget(output)
        self.tab_widget.setGeometry(QtCore.QRect(0, 20, 511, 251))
        self.tab_widget.setObjectName(_fromUtf8("tab_widget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.checkBox_hkl = QtGui.QCheckBox(self.tab)
        self.checkBox_hkl.setGeometry(QtCore.QRect(30, 40, 151, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Segoe UI"))
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.checkBox_hkl.setFont(font)
        self.checkBox_hkl.setObjectName(_fromUtf8("checkBox_hkl"))
        self.checkBox_cif = QtGui.QCheckBox(self.tab)
        self.checkBox_cif.setGeometry(QtCore.QRect(30, 80, 151, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Segoe UI"))
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.checkBox_cif.setFont(font)
        self.checkBox_cif.setObjectName(_fromUtf8("checkBox_cif"))
        self.checkBox_fou = QtGui.QCheckBox(self.tab)
        self.checkBox_fou.setGeometry(QtCore.QRect(30, 120, 151, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Segoe UI"))
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.checkBox_fou.setFont(font)
        self.checkBox_fou.setObjectName(_fromUtf8("checkBox_fou"))
        self.tab_widget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tab_widget.addTab(self.tab_2, _fromUtf8(""))

        self.retranslateUi(output)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QObject.connect(self.pushButton_OK, QtCore.SIGNAL(_fromUtf8("clicked()")), output.close)
        QtCore.QMetaObject.connectSlotsByName(output)

    def retranslateUi(self, output):
        output.setWindowTitle(_translate("output", "output", None))
        self.pushButton_OK.setText(_translate("output", "OK", None))
        self.checkBox_hkl.setText(_translate("output", "Hkl", None))
        self.checkBox_cif.setText(_translate("output", "Cif", None))
        self.checkBox_fou.setText(_translate("output", "Fou", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab), _translate("output", "output", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_2), _translate("output", "other", None))


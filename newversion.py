# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newversion.ui'
#
# Created: Fri Nov 21 23:54:30 2014
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

class Ui_newversion(object):
    def setupUi(self, newversion):
        newversion.setObjectName(_fromUtf8("newversion"))
        newversion.resize(419, 236)
        self.buttonBox = QtGui.QDialogButtonBox(newversion)
        self.buttonBox.setGeometry(QtCore.QRect(40, 180, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(newversion)
        self.label.setGeometry(QtCore.QRect(10, 30, 391, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("SimSun-ExtB"))
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(newversion)
        self.label_2.setGeometry(QtCore.QRect(10, 100, 321, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(newversion)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), newversion.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), newversion.reject)
        QtCore.QMetaObject.connectSlotsByName(newversion)

    def retranslateUi(self, newversion):
        newversion.setWindowTitle(_translate("newversion", "New version", None))
        self.label.setText(_translate("newversion", "<html><head/><body><p><span style=\" color:#ff0000;\">Find a new version , please download ... </span></p><p><a href=\"http://autofp.sinaapp.com\"><span style=\" text-decoration: underline; color:#0000ff;\">http://autofp.sinaapp.com</span></a></p></body></html>", None))
        self.label_2.setText(_translate("newversion", "Email: autofp@163.com", None))


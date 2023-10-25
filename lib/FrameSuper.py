import glob
import os

from PyQt5 import QtWidgets, uic
from lib.CallMessageBox import CallMessageBox
from lib.FDCMgr import FCDMgr


class FrameSuper(QtWidgets.QFrame):
    def __init__(self, frame):
        super().__init__()
        uic.loadUi(frame, self)

        self.mgr = FCDMgr()

        files = ["---"]
        files += glob.glob("*.db")
        self.comboBoxDB.addItems(files)

        self.textEditResult.setReadOnly(True)

        self.pushButtonAction.clicked.connect(self.performAction)
        self.pushButtonConnect.clicked.connect(self.connectDB)
    
    def connectDB(self):
        db = self.comboBoxDB.currentText()
        res = self.mgr.connectDataBase(database = db)
        if res == 1:
            CallMessageBox("Не удается найти БД!")
            return False
        elif res == 2:
            CallMessageBox("БД должна иметь данные!")
            return False
        else:
            CallMessageBox("БД успешно подключена!")
            return True

    def performAction(self):
        if not self.mgr.isConnected():
            CallMessageBox("Подключите непустую БД!")
            return False
        return True

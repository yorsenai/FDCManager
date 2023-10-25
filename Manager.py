import sys

from PyQt5 import QtWidgets, uic

from lib.CallMessageBox import CallMessageBox
from lib.FrameSuper import FrameSuper

class comboItem(QtWidgets.QComboBox):
    def __init__(self, parent, items):
        super().__init__(parent)
        self.setStyleSheet('font-size: 14px')
        self.addItems(items)
        self.currentIndexChanged.connect(self.getComboValue)

    def getComboValue(self):
        return self.currentText()


class FrameFD(FrameSuper):
    def __init__(self):
        super().__init__(frame = 'ui\\FrameFD.ui')
    
    def performAction(self):
        if not super().performAction():
            return
        dependencies = self.mgr.getFunctionalDependencies()

        self.textEditResult.setText("")
        self.textEditResult.append("НАЙДЕННЫЕ ЗАВИСИМОСТИ:\n")
        for line in dependencies:
            self.textEditResult.append(line)


class FrameC(FrameSuper):
    def __init__(self):
        super().__init__(frame = 'ui\\FrameC.ui')
        attrs = ["---"]
        self.comboBoxAtribute.addItems(attrs)
    
    def performAction(self):
        if not super().performAction():
            return
        attribute = self.comboBoxAtribute.currentText()
        if attribute == "---":
            CallMessageBox("Подключите БД и выберите атрибут!")
            return
        closure = self.mgr.getClosure(attribute = attribute)
        # self.textEditResult.setText("")
        self.textEditResult.setText(f"ЗАМЫКАНИЕ ДЛЯ {attribute}:\n")
        for attr in closure:
            self.textEditResult.append(attr)

    def connectDB(self):
        if super().connectDB():
            attrs = self.mgr.getAllAttributes()
            self.comboBoxAtribute.addItems(attrs)



class ManagerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('ui\\AppWindow.ui', self)

        self.frameFD = FrameFD()
        self.frameC  = FrameC()

        self.setCentralWidget(self.frameFD) 
        

        self.ActionFD.triggered.connect(self.setFD)
        self.ActionC.triggered.connect(self.setC)
    
    def setFD(self):
        if self.centralWidget() == self.frameFD:
            pass
        else:
            self.setCentralWidget(self.frameFD) 
    
    def setC(self):
        if self.centralWidget() == self.frameC:
            pass
        else:
            self.setCentralWidget(self.frameC) 
    
    def performAction(self):
        db = self.comboBox.currentText()
        self.mgr.connectDataBase(database = db)
        if not self.mgr.isConnected():
            CallMessageBox("Ошибка базы данных!")
            return

        if self.current_action == "FD":
            dependencies = self.mgr.getFunctionalDependencies()
            self.textEditResult.append("НАЙДЕННЫЕ ЗАВИСИМОСТИ:\n")
            for dep in dependencies:
                self.textEditResult.append(dep)
            pass
        elif self.current_action == "C":
            pass
        else:
            CallMessageBox("Ошибка выбора действия!")
            return
        pass
        

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ManagerApp()  # Создаём объект класса ManagerApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение



if __name__ == "__main__":
    main()
import sys
from mainWindow import MainWindow
from PyQt5 import QtWidgets

import consts

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    consts.DPM_X = 8 #app.primaryScreen().physicalDotsPerInchX() / 0.39370 / 10
    consts.DPM_Y = 8 #app.primaryScreen().physicalDotsPerInchY() / 0.39370 / 10
    
    print(consts.DPM_X, consts.DPM_Y)
    
    mainWindow = MainWindow()
    mainWindow.show()
    
    sys.exit(app.exec_())

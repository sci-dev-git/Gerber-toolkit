from PyQt5.QtWidgets import QApplication, QAction, QWidget, QHBoxLayout, QMainWindow, QTreeWidget, QTreeWidgetItem, QMessageBox, QDesktopWidget, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from gerberWidget import GerberWidget
from gerberParser import GerberParser

LAYOUTS = (('GTL', 'Top Cu Layout'),
           ('GTS', 'Top Mask Layout'),
           ('GTP', 'Top Paste Layour'),
           ('GTO', 'Top Silk Layout'),
           ('GBL', 'Bottom Cu Layout'),
           ('GBS', 'Bottom Mask Layout'),
           ('GBP', 'Bottom Paste Layour'),
           ('GBO', 'Bottom Silk Layout'),
           ('GKO', 'Keep-out Layout')
           )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Gerber Toolkit V1.0.0')
        
        actionOpen = QAction(QIcon('resources/fileopen.png'), '&Open Gerber File', self)
        actionOpen.setShortcut('Ctrl+O')
        actionOpen.setStatusTip('Open a gerber file')
        actionOpen.triggered.connect(self.slotOpen)
        
        actionQuit = QAction('&Exit', self)
        actionQuit.setShortcut('Ctrl+Q')
        actionQuit.setStatusTip('Exit application')
        actionQuit.triggered.connect(self.slotQuit)
        
        actionCompile = QAction(QIcon('resources/projectcompile.png'), '&Compile scale image File', self)
        actionCompile.setShortcut('Ctrl+C')
        actionCompile.setStatusTip('Compile scale image File')
        actionCompile.triggered.connect(self.slotCompile)
 
        self.statusBar()
 
        menubar = self.menuBar()
        menuFile = menubar.addMenu('&File')
        menuFile.addAction(actionOpen)
        menuFile.addAction(actionQuit)
        
        menuProject = menubar.addMenu('&Project')
        menuProject.addAction(actionCompile)
        
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(actionOpen)
        self.toolbar.addAction(actionQuit)
         
        self.setGeometry(300, 300, 1600, 800)
        self.center()
        
        self.gerberWidget = GerberWidget()
        self.gerberParser = GerberParser(self.gerberWidget.plotOutline, self.gerberWidget.plotAperture)
        
        self.layoutTreeWidget = QTreeWidget()
        self.layoutTreeWidget.setColumnCount(2)
        self.layoutTreeWidget.setHeaderLabels(['Code','Name'])
        self.layoutTreeRoot = QTreeWidgetItem(self.layoutTreeWidget)
        self.layoutTreeRoot.setText(0,'Gerber Layouts')
        self.layoutTreeRoot.setExpanded(True)
        for code, name in LAYOUTS:
            node = QTreeWidgetItem(self.layoutTreeRoot)
            node.setText(0, code)
            node.setText(1, name)
            node.setCheckState(0, Qt.Unchecked)
        
        self.layoutTreeWidget.addTopLevelItem(self.layoutTreeRoot)

        self.centralWidget = QWidget(self)
        self.centralLayout = QHBoxLayout(self.centralWidget)
        self.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.centralLayout.setSpacing(0)
        self.centralLayout.addWidget(self.layoutTreeWidget)
        self.centralLayout.addWidget(self.gerberWidget)
        self.setCentralWidget(self.centralWidget)
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    #
    # Slot Processing
    #
    def slotOpen(self, event):
        filename = QFileDialog.getOpenFileName(self,'Open a gerber file')
        stream = open(filename[0], 'r')
        self.gerberParser.parse(stream)
        stream.close()
        
        self.layoutTreeRoot.setText(0, filename[0])
        
    def slotQuit(self, event):
        self.close()
        
    def slotCompile(self, event):
        pass
        
    def closeEvent(self, event):
        if QMessageBox.warning(self, 'Message', "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QPolygonF, QPen, QColor
from PyQt5.QtCore import QRectF, QPointF

from gerberView import GerberView
import consts

class GerberWidget(QWidget):
    def __init__(self):
        super().__init__()
    
        self.view = GerberView()
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)

        self.verticalLayout.addWidget(self.view)
        self.vertex = []
        
        self.clear()
        
    def clear(self):
        self.view.clear()
        self.vertex = []
        
    def plotOutline(self, vertexs):
        scene = self.view.getScene()
        
        polygon = QPolygonF()
        polygon.clear()
        for point in vertexs:
            polygon.append(QPointF(point[0] * consts.DPM_X, point[1] * consts.DPM_Y))
        scene.addPolygon(polygon, QColor(0,0,128))
    
    def plotAperture(self, atype, modifier, modifier_x, addr_x, addr_y):
        print('==========', atype, modifier, modifier_x)
    
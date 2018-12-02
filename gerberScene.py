from PyQt5.QtWidgets import QWidget, QGraphicsScene
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QRectF

class GerberScene(QGraphicsScene):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.setSceneRect( QRectF(x, y, width, height) );

    def drawBackground(self, painter, rect ):
        painter.setBrush( QColor( 255, 255, 255 ) )
        painter.drawRect( self.sceneRect() )
        painter.setPen( QColor( 0, 0, 0 ) )
        
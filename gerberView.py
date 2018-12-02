from PyQt5.QtWidgets import QWidget, QGraphicsView
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter

from gerberScene import GerberScene

class GerberView(QGraphicsView):
    def __init__(self):
        super().__init__()
        
        self.scene = None
        
        self.clear()
        
        self.viewport().setFixedSize( 1600, 1200 )
        self.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOff )
        self.setViewportUpdateMode( QGraphicsView.MinimalViewportUpdate )
        self.setRenderHint( QPainter.HighQualityAntialiasing )
        self.setCacheMode( QGraphicsView.CacheBackground )
        self.setTransformationAnchor( QGraphicsView.AnchorUnderMouse )
        self.setResizeAnchor( QGraphicsView.AnchorUnderMouse )
        self.setDragMode( QGraphicsView.RubberBandDrag )
        
        self.setAcceptDrops( False )
    
    def clear(self):
        if self.scene != None:
          self.scene.deleteLater()
          
        self.scene = GerberScene(-1600, -1200, 6200, 3400)
        self.scene.update()
    
        self.setScene( self.scene )
        self.gotoCenter();
    
    
    def gotoCenter(self):
        self.centerOn( self.mapFromScene( -(self.width()/2), -(self.height()/2 )) )

    def getScene(self):
        return self.scene
    

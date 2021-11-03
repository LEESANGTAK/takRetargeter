from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *


class SceneSwitcher(QGraphicsPixmapItem):
    def __init__(self, parent, name, view, scene, image, size, posX, posY):
        super(SceneSwitcher, self).__init__()

        self.parent = parent
        self.name = name
        self.view = view
        self.scene = scene
        self.image = image
        self.size = size

        self.__globalRec = QRectF(0, 0, self.size, self.size)

        self.setPixmap(QPixmap(self.image))
        self.setPos(posX-(self.size*0.5), posY-(self.size*0.5))
        self.setToolTip('Go to {0}'.format(self.name))

    def boundingRect(self):
        return self.__globalRec

    def mousePressEvent(self, event):
        self.view.setScene(self.scene)

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import maya.cmds as cmds
import maya.OpenMaya as om


class Brush:
    DEFAULT = QBrush(QColor(150, 150, 150))
    HOVER = QBrush(QColor(255, 255, 255))
    ASSIGN = QBrush(QColor(0, 220, 0))


class CharDefItem(QGraphicsItem):
    # Constants
    BRUSH = Brush()
    MIRROR_STR_TABLE = {
        'L': 'R', 'R': 'L',
        'l': 'r', 'r': 'l',
        'LF': 'RT', 'RT': 'LF',
        'Left': 'Right', 'Right': 'Left'
    }

    def __init__(self, parent, name, charDef, size, posX, posY):
        super(CharDefItem, self).__init__()

        # Public Attributes
        self.parent = parent
        self.charDefAttr = name
        self.size = size
        self.charDef = charDef
        self.assignObj = None
        self.toolTip = None

        # Private Attributes
        self.__globalRect = QRectF(0, 0, self.size, self.size)
        self.__hover = False

        self.setPos(posX-(self.size*0.5), posY-(self.size*0.5))
        self.setAcceptHoverEvents(True)
        self.setInitialState()
        self.updateToolTip()

    def paint(self, painter, option, widget):
        painter.setPen(Qt.NoPen)

        if not self.assignObj:
            painter.setBrush(self.BRUSH.DEFAULT)
            if self.__hover:
                painter.setBrush(self.BRUSH.HOVER)
        else:
            painter.setBrush(self.BRUSH.ASSIGN)

        painter.drawEllipse(self.__globalRect)

    def updateToolTip(self):
        if not self.charDef:
            self.toolTip = self.charDefAttr + ' : None'
            self.setToolTip(self.toolTip)
        else:
            self.toolTip = '{0} : {1}'.format(self.charDefAttr, self.assignObj)
            self.setToolTip(self.toolTip)

    def setInitialState(self):
        if not self.charDef:
            return

        assignObjName = getattr(self.charDef, self.charDefAttr).get('name')
        if assignObjName and cmds.objExists(assignObjName):
            self.assignObj = assignObjName
        else:
            self.assignObj = None

    def mousePressEvent(self, event):
        if not self.charDef:
            om.MGlobal.displayError('Please select character.')
            return

        mirrorMatchMode = self.parent.mirrorMatchBtn.isChecked()
        leftButtonPressed = event.button() == Qt.LeftButton

        if self.assignObj:
            if leftButtonPressed:
                if cmds.objExists(self.assignObj):
                    cmds.select(self.assignObj, r=True)
                else:
                    cmds.displayWarning('{0} object not exists.'.format(self.assignObj))
            else:
                self.removeAssignObj()
                if mirrorMatchMode:
                    self.removeMirror()
        else:  # In case empty char item
            if leftButtonPressed:
                return
            selObjs = cmds.ls(sl=True)
            if selObjs:
                # Check selection count
                if len(selObjs) >= 2:
                    om.MGlobal.displayError('Please select only one object.')
                    return

                assignObj = selObjs[0]
                valid, assignedCharDefItem = self.isValid(assignObj)  # Check if already assigned
                if valid:
                    self.setAssignObj(assignObj)
                    if mirrorMatchMode:
                        self.assignMirror()
                else:
                    result = QMessageBox.question(self.parent,
                                              'Already Assigned',
                                              '"{0}" assigned to "{1}".\nChange to "{2}"?'.format(assignObj, assignedCharDefItem.charDefAttr, self.charDefAttr),
                                              QMessageBox.Yes,
                                              QMessageBox.No)
                    if result == QMessageBox.Yes:
                        self.setAssignObj(assignObj)
                        assignedCharDefItem.removeAssignObj()
                        if mirrorMatchMode:
                            self.assignMirror()
                            assignedCharDefItem.removeMirror()
                    else:
                        return

    def setAssignObj(self, assignObj):
        self.assignObj = assignObj
        setattr(self.charDef, self.charDefAttr, self.assignObj)
        self.update()
        self.updateToolTip()

    def removeAssignObj(self):
        self.assignObj = None
        setattr(self.charDef, self.charDefAttr, self.assignObj)
        self.update()
        self.updateToolTip()

    def assignMirror(self):
        mirrorCharItem = self.parent.mirrorInfo.get(self)
        if mirrorCharItem:
            mirrorObj = self.getMirrorObj(self.assignObj)
            if mirrorObj:
                if cmds.objExists(mirrorObj):
                    mirrorCharItem.setAssignObj(mirrorObj)
                else:
                    om.MGlobal.displayWarning('"{0}"s mirror object "{1}" does not exists.'.format(self.assignObj, mirrorObj))
            else:
                om.MGlobal.displayWarning('"{0}"s mirror object does not exists.'.format(self.assignObj))

    def removeMirror(self):
        mirrorCharItem = self.parent.mirrorInfo.get(self)
        if mirrorCharItem:
            mirrorCharItem.removeAssignObj()

    def getMirrorObj(self, assignObj):
        mirrorObj = None
        searchStrs = assignObj.split('_')
        for searchStr in searchStrs:
            mirrorStr = self.MIRROR_STR_TABLE.get(searchStr)
            if mirrorStr:
                searchStr = '_' + searchStr
                mirrorStr = '_' + mirrorStr
                mirrorObj = assignObj.replace(searchStr, mirrorStr)
        return mirrorObj

    def isValid(self, obj):
        charDefItems = []
        for scene in self.parent.view.scenes:
            charDefItems.extend([item for item in scene.items() if isinstance(item, CharDefItem)])

        valid = True
        assignedCharDefItem = None
        for item in charDefItems:
            if item.assignObj == obj:
                valid = False
                assignedCharDefItem = item
                break

        return valid, assignedCharDefItem

    def boundingRect(self):
        return self.__globalRect

    def hoverEnterEvent(self, event):
        self.__hover = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.__hover = False
        self.update()

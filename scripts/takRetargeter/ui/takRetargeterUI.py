from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import os

import maya.OpenMayaUI as omui
import maya.cmds as cmds

from shiboken2 import wrapInstance

from .. import charDefinition
from .. import retargeter
from . import charDefItem
from . import sceneSwitcher


def getMayaMainWin():
    mayaWinPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mayaWinPtr), QWidget)


class TakRetargeterUI(QDialog):
    NAME = 'Tak Retargeter'
    VERSION = '1.1.1'

    ICON_DIR_PATH = __file__.rsplit('scripts', 1)[0] + 'icons'
    ICON_SIZE = 30
    FILE_FILTERS = 'Character Definition (*.cd);;All Files (*.*)'
    FULLBODY_IMAGE_WIDTH = 379
    HAND_IMAGE_WIDTH = 250

    instance = None

    def __init__(self, parent=getMayaMainWin()):
        super(TakRetargeterUI, self).__init__(parent)

        self.selectedFilter = 'Character Definition (*.cd)'
        self.retargeter = retargeter.Retargeter()

        self.geo = None

        self.setWindowTitle('{0} - {1}'.format(TakRetargeterUI.NAME, TakRetargeterUI.VERSION))
        self.setWindowIcon(QIcon(os.path.join(self.ICON_DIR_PATH, 'takRetargeterIcon.png')))

        self.mirrorInfo = {}

        self.createWidgets()
        self.createLayouts()
        self.createConnections()

        self.refreshComboBox()

    def createWidgets(self):
        self.charComboBox = QComboBox()
        self.charComboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.srcComboBox = QComboBox()
        self.srcComboBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.createCharDefBtn = QAction(QIcon(':addCreateGeneric.png'), 'Create Character Definition', self)
        self.loadCharDefBtn = QAction(QIcon(':fileOpen.png'), 'Load Character Definition', self)
        self.saveCharDefBtn = QAction(QIcon(':fileSave.png'), 'Save Character Definition', self)
        self.delCharDefBtn = QAction(QIcon(':deleteGeneric.png'), 'Delete Character Definition', self)
        self.stancePoseBtn = QAction(QIcon(':HIKCharacterToolStancePose.png'), 'Stance Pose', self)
        self.connectBtn = QAction(QIcon(os.path.join(self.ICON_DIR_PATH, 'connectToCharacter.png')), 'Connect Source to Character', self)
        self.disconnectBtn = QAction(QIcon(os.path.join(self.ICON_DIR_PATH, 'disconnectFromCharacter.png')), 'Disconnect Source from Character', self)
        self.bakeBtn = QAction(QIcon(':bakeAnimation.png'), 'Bake Animation', self)
        self.deleteKeyframesBtn = QAction(QIcon(':nClothCacheDelete.png'), 'Delete Animation', self)
        self.mirrorMatchBtn = QAction(QIcon(':HIKmirror.png'), 'Mirror Matching', self)
        self.mirrorMatchBtn.setCheckable(True)
        self.mirrorMatchBtn.setChecked(True)

        self.fullBodyScene = QGraphicsScene()
        self.leftHandScene = QGraphicsScene()
        self.rightHandScene = QGraphicsScene()
        self.view = QGraphicsView()
        self.view.scenes = [self.fullBodyScene, self.leftHandScene, self.rightHandScene]

    def createLayouts(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setMargin(5)

        trgSrcDefFormLayout = QFormLayout()
        trgSrcDefFormLayout.addRow('Character: ', self.charComboBox)
        trgSrcDefFormLayout.addRow('Source: ', self.srcComboBox)

        btnToolBar = QToolBar()
        btnToolBar.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
        btnToolBar.addAction(self.createCharDefBtn)
        btnToolBar.addAction(self.loadCharDefBtn)
        btnToolBar.addAction(self.saveCharDefBtn)
        btnToolBar.addAction(self.delCharDefBtn)
        btnToolBar.addAction(self.stancePoseBtn)
        btnToolBar.addAction(self.connectBtn)
        btnToolBar.addAction(self.disconnectBtn)
        btnToolBar.addAction(self.bakeBtn)
        btnToolBar.addAction(self.deleteKeyframesBtn)
        btnToolBar.addAction(self.mirrorMatchBtn)

        mainLayout.addLayout(trgSrcDefFormLayout)
        mainLayout.addWidget(btnToolBar)
        mainLayout.addWidget(self.view)

    def createConnections(self):
        self.charComboBox.currentTextChanged.connect(self.setCharDef)
        self.srcComboBox.currentTextChanged.connect(self.setSrcDef)
        self.createCharDefBtn.triggered.connect(self.createCharDef)
        self.loadCharDefBtn.triggered.connect(self.loadCharDef)
        self.saveCharDefBtn.triggered.connect(self.saveCharDef)
        self.delCharDefBtn.triggered.connect(self.delCharDef)
        self.stancePoseBtn.triggered.connect(self.stancePose)
        self.connectBtn.triggered.connect(self.retargeter.connect)
        self.disconnectBtn.triggered.connect(self.retargeter.disconnect)
        self.bakeBtn.triggered.connect(self.retargeter.bake)
        self.deleteKeyframesBtn.triggered.connect(self.retargeter.deleteKeyframes)

    def setCharDef(self, text):
        charDef = self.retargeter.charDefs.get(text)
        if charDef:
            self.retargeter.targetCharDef = charDef
        self.refreshCharItems()

    def setSrcDef(self, text):
        srcDef = self.retargeter.charDefs.get(text)
        if srcDef:
            self.retargeter.sourceCharDef = srcDef

    def createCharDef(self):
        newCharName, ok = QInputDialog.getText(self, 'Input Dialog', 'Character Definition Name:')
        if not newCharName or not ok:
            return False
        newCharDef = charDefinition.CharDefinition()
        newCharDef.name = newCharName
        self.retargeter.charDefs[newCharName] = newCharDef
        self.refreshComboBox()
        self.charComboBox.setCurrentText(newCharName)

    def loadCharDef(self):
        filePaths, self.selectedFilter = QFileDialog.getOpenFileNames(self, 'Select File', '', self.FILE_FILTERS, self.selectedFilter)
        if not filePaths:
            return False
        for filePath in filePaths:
            charDef = charDefinition.CharDefinition()
            charDef.load(filePath)
            self.retargeter.charDefs[charDef.name] = charDef
            self.refreshComboBox()
            self.charComboBox.setCurrentText(charDef.name)

    @ staticmethod
    def getNamespaces():
        allRefs = cmds.ls(type='reference')
        namespaces = ['']
        for ref in allRefs:
            try:
                ns = cmds.referenceQuery(ref, namespace=True)
            except:
                pass
            nsSplit = ns.split(':')
            if len(nsSplit) > 2:
                continue
            namespaces.append(nsSplit[-1])

        return namespaces

    def saveCharDef(self):
        charDefName = self.charComboBox.currentText()
        charDef = self.retargeter.charDefs.get(charDefName)
        filename, self.selectedFilter = QFileDialog.getSaveFileName(self, 'Save As', '', self.FILE_FILTERS, self.selectedFilter)
        if not filename:
            return False
        charDef.save(filename)

    def delCharDef(self):
        selCharDef = self.charComboBox.currentText()
        if selCharDef == 'None':
            return
        self.retargeter.charDefs.pop(selCharDef)
        self.refreshComboBox()

    def stancePose(self):
        srcDef = self.srcComboBox.currentText()
        srcDef = self.retargeter.charDefs.get(srcDef)
        if srcDef:
            srcDef.stancePose()

        selCharDef = self.charComboBox.currentText()
        charDef = self.retargeter.charDefs.get(selCharDef)
        if charDef:
            charDef.stancePose()

    def refreshComboBox(self):
        # Remember current text
        selCharText = self.charComboBox.currentText()
        selSrcText = self.srcComboBox.currentText()

        # Clear all items
        self.charComboBox.clear()
        self.srcComboBox.clear()

        # Add current char definitions
        for charDefName in self.retargeter.charDefs.keys():
            self.charComboBox.addItem(charDefName)
            self.srcComboBox.addItem(charDefName)

        # Select the text before updated
        if self.charComboBox.findText(selCharText):
            self.charComboBox.setCurrentText(selCharText)
        else:
            self.charComboBox.setCurrentText('None')  # When delete char definition, selected text not exists
        if self.srcComboBox.findText(selSrcText):
            self.srcComboBox.setCurrentText(selSrcText)
        else:
            self.srcComboBox.setCurrentText('None')

    def refreshCharItems(self):
        selCharDefName = self.charComboBox.currentText()
        charDef = self.retargeter.charDefs.get(selCharDefName)

        self.view.setScene(self.fullBodyScene)

        self.fullBodyScene.clear()
        self.fullBodyScene.addPixmap(QPixmap(os.path.join(self.ICON_DIR_PATH, 'FullBody_T.png')))
        self.fullBodyScene.addItem(charDefItem.CharDefItem(self, 'root', charDef, 20, 190, 360))
        self.fullBodyScene.addItem(charDefItem.CharDefItem(self, 'pelvis', charDef, 15, 190, 170))
        self.fullBodyScene.addItem(charDefItem.CharDefItem(self, 'spine_01', charDef, 12, 190, 150))
        self.fullBodyScene.addItem(charDefItem.CharDefItem(self, 'spine_02', charDef, 12, 190, 130))
        self.fullBodyScene.addItem(charDefItem.CharDefItem(self, 'spine_03', charDef, 12, 190, 110))
        self.fullBodyScene.addItem(charDefItem.CharDefItem(self, 'neck_01', charDef, 12, 190, 70))
        self.fullBodyScene.addItem(charDefItem.CharDefItem(self, 'head', charDef, 12, 190, 40))

        clavicleLItem = charDefItem.CharDefItem(self, 'clavicle_l', charDef, 12, 205, 85)
        upperarmLItem = charDefItem.CharDefItem(self, 'upperarm_l', charDef, 12, 230, 80)
        lowerarmLItem = charDefItem.CharDefItem(self, 'lowerarm_l', charDef, 12, 270, 85)
        handLItem = charDefItem.CharDefItem(self, 'hand_l', charDef, 12, 320, 80)
        thighLItem = charDefItem.CharDefItem(self, 'thigh_l', charDef, 12, 210, 190)
        calfLItem = charDefItem.CharDefItem(self, 'calf_l', charDef, 12, 215, 260)
        footLItem = charDefItem.CharDefItem(self, 'foot_l', charDef, 12, 220, 340)
        ballLItem = charDefItem.CharDefItem(self, 'ball_l', charDef, 12, 230, 360)
        clavicleRItem = charDefItem.CharDefItem(self, 'clavicle_r', charDef, 12, rightSideItemPos(205, self.FULLBODY_IMAGE_WIDTH), 85)
        upperarmRItem = charDefItem.CharDefItem(self, 'upperarm_r', charDef, 12, rightSideItemPos(230, self.FULLBODY_IMAGE_WIDTH), 80)
        lowerarmRItem = charDefItem.CharDefItem(self, 'lowerarm_r', charDef, 12, rightSideItemPos(270, self.FULLBODY_IMAGE_WIDTH), 85)
        handRItem = charDefItem.CharDefItem(self, 'hand_r', charDef, 12, rightSideItemPos(320, self.FULLBODY_IMAGE_WIDTH), 80)
        thighRItem = charDefItem.CharDefItem(self, 'thigh_r', charDef, 12, rightSideItemPos(210, self.FULLBODY_IMAGE_WIDTH), 190)
        calfRItem = charDefItem.CharDefItem(self, 'calf_r', charDef, 12, rightSideItemPos(215, self.FULLBODY_IMAGE_WIDTH), 260)
        footRItem = charDefItem.CharDefItem(self, 'foot_r', charDef, 12, rightSideItemPos(220, self.FULLBODY_IMAGE_WIDTH), 340)
        ballRItem = charDefItem.CharDefItem(self, 'ball_r', charDef, 12, rightSideItemPos(230, self.FULLBODY_IMAGE_WIDTH), 360)
        self.fullBodyScene.addItem(clavicleLItem)
        self.fullBodyScene.addItem(upperarmLItem)
        self.fullBodyScene.addItem(lowerarmLItem)
        self.fullBodyScene.addItem(handLItem)
        self.fullBodyScene.addItem(thighLItem)
        self.fullBodyScene.addItem(calfLItem)
        self.fullBodyScene.addItem(footLItem)
        self.fullBodyScene.addItem(ballLItem)
        self.fullBodyScene.addItem(clavicleRItem)
        self.fullBodyScene.addItem(upperarmRItem)
        self.fullBodyScene.addItem(lowerarmRItem)
        self.fullBodyScene.addItem(handRItem)
        self.fullBodyScene.addItem(thighRItem)
        self.fullBodyScene.addItem(calfRItem)
        self.fullBodyScene.addItem(footRItem)
        self.fullBodyScene.addItem(ballRItem)
        self.fullBodyScene.addItem(sceneSwitcher.SceneSwitcher(self,
                                                               'LeftHand',
                                                               self.view,
                                                               self.leftHandScene,
                                                               os.path.join(self.ICON_DIR_PATH, 'GoToArrow.png'),
                                                               20, 350, 50))
        self.fullBodyScene.addItem(sceneSwitcher.SceneSwitcher(self,
                                                               'RightHand',
                                                               self.view,
                                                               self.rightHandScene,
                                                               os.path.join(self.ICON_DIR_PATH, 'GoToArrow.png'),
                                                               20, rightSideItemPos(350, self.FULLBODY_IMAGE_WIDTH), 50))

        self.leftHandScene.clear()
        self.leftHandScene.addPixmap(QPixmap(os.path.join(self.ICON_DIR_PATH, 'LeftHand.png')))
        index01LItem = charDefItem.CharDefItem(self, 'index_01_l', charDef, 15, 137, 223)
        index02LItem = charDefItem.CharDefItem(self, 'index_02_l', charDef, 15, 175, 160)
        index03LItem = charDefItem.CharDefItem(self, 'index_03_l', charDef, 15, 193, 127)
        middle01LItem = charDefItem.CharDefItem(self, 'middle_01_l', charDef, 15, 109, 198)
        middle02LItem = charDefItem.CharDefItem(self, 'middle_02_l', charDef, 15, 130, 137)
        middle03LItem = charDefItem.CharDefItem(self, 'middle_03_l', charDef, 15, 145, 93)
        ring01LItem = charDefItem.CharDefItem(self, 'ring_01_l', charDef, 15, 78, 190)
        ring02LItem = charDefItem.CharDefItem(self, 'ring_02_l', charDef, 15, 90, 127)
        ring03LItem = charDefItem.CharDefItem(self, 'ring_03_l', charDef, 15, 95, 95)
        pinky01LItem = charDefItem.CharDefItem(self, 'pinky_01_l', charDef, 15, 48, 190)
        pinky02LItem = charDefItem.CharDefItem(self, 'pinky_02_l', charDef, 15, 52, 142)
        pinky03LItem = charDefItem.CharDefItem(self, 'pinky_03_l', charDef, 15, 52, 113)
        thumb01LItem = charDefItem.CharDefItem(self, 'thumb_01_l', charDef, 15, 125, 325)
        thumb02LItem = charDefItem.CharDefItem(self, 'thumb_02_l', charDef, 15, 172, 300)
        thumb03LItem = charDefItem.CharDefItem(self, 'thumb_03_l', charDef, 15, 210, 265)
        self.leftHandScene.addItem(index01LItem)
        self.leftHandScene.addItem(index02LItem)
        self.leftHandScene.addItem(index03LItem)
        self.leftHandScene.addItem(middle01LItem)
        self.leftHandScene.addItem(middle02LItem)
        self.leftHandScene.addItem(middle03LItem)
        self.leftHandScene.addItem(ring01LItem)
        self.leftHandScene.addItem(ring02LItem)
        self.leftHandScene.addItem(ring03LItem)
        self.leftHandScene.addItem(pinky01LItem)
        self.leftHandScene.addItem(pinky02LItem)
        self.leftHandScene.addItem(pinky03LItem)
        self.leftHandScene.addItem(thumb01LItem)
        self.leftHandScene.addItem(thumb02LItem)
        self.leftHandScene.addItem(thumb03LItem)
        self.leftHandScene.addItem(sceneSwitcher.SceneSwitcher(self,
                                                               'FullBody',
                                                               self.view,
                                                               self.fullBodyScene,
                                                               os.path.join(self.ICON_DIR_PATH, 'ReturnToArrow.png'),
                                                               50, 25, 25))

        self.rightHandScene.clear()
        self.rightHandScene.addPixmap(QPixmap(os.path.join(self.ICON_DIR_PATH, 'RightHand.png')))
        index01RItem = charDefItem.CharDefItem(self, 'index_01_r', charDef, 15, rightSideItemPos(137, self.HAND_IMAGE_WIDTH), 223)
        index02RItem = charDefItem.CharDefItem(self, 'index_02_r', charDef, 15, rightSideItemPos(175, self.HAND_IMAGE_WIDTH), 160)
        index03RItem = charDefItem.CharDefItem(self, 'index_03_r', charDef, 15, rightSideItemPos(193, self.HAND_IMAGE_WIDTH), 127)
        middle01RItem = charDefItem.CharDefItem(self, 'middle_01_r', charDef, 15, rightSideItemPos(109, self.HAND_IMAGE_WIDTH), 198)
        middle02RItem = charDefItem.CharDefItem(self, 'middle_02_r', charDef, 15, rightSideItemPos(130, self.HAND_IMAGE_WIDTH), 137)
        middle03RItem = charDefItem.CharDefItem(self, 'middle_03_r', charDef, 15, rightSideItemPos(145, self.HAND_IMAGE_WIDTH), 93)
        ring01RItem = charDefItem.CharDefItem(self, 'ring_01_r', charDef, 15, rightSideItemPos(78, self.HAND_IMAGE_WIDTH), 190)
        ring02RItem = charDefItem.CharDefItem(self, 'ring_02_r', charDef, 15, rightSideItemPos(90, self.HAND_IMAGE_WIDTH), 127)
        ring03RItem = charDefItem.CharDefItem(self, 'ring_03_r', charDef, 15, rightSideItemPos(95, self.HAND_IMAGE_WIDTH), 95)
        pinky01RItem = charDefItem.CharDefItem(self, 'pinky_01_r', charDef, 15, rightSideItemPos(48, self.HAND_IMAGE_WIDTH), 190)
        pinky02RItem = charDefItem.CharDefItem(self, 'pinky_02_r', charDef, 15, rightSideItemPos(52, self.HAND_IMAGE_WIDTH), 142)
        pinky03RItem = charDefItem.CharDefItem(self, 'pinky_03_r', charDef, 15, rightSideItemPos(52, self.HAND_IMAGE_WIDTH), 113)
        thumb01RItem = charDefItem.CharDefItem(self, 'thumb_01_r', charDef, 15, rightSideItemPos(125, self.HAND_IMAGE_WIDTH), 325)
        thumb02RItem = charDefItem.CharDefItem(self, 'thumb_02_r', charDef, 15, rightSideItemPos(172, self.HAND_IMAGE_WIDTH), 300)
        thumb03RItem = charDefItem.CharDefItem(self, 'thumb_03_r', charDef, 15, rightSideItemPos(210, self.HAND_IMAGE_WIDTH), 265)
        self.rightHandScene.addItem(index01RItem)
        self.rightHandScene.addItem(index02RItem)
        self.rightHandScene.addItem(index03RItem)
        self.rightHandScene.addItem(middle01RItem)
        self.rightHandScene.addItem(middle02RItem)
        self.rightHandScene.addItem(middle03RItem)
        self.rightHandScene.addItem(ring01RItem)
        self.rightHandScene.addItem(ring02RItem)
        self.rightHandScene.addItem(ring03RItem)
        self.rightHandScene.addItem(pinky01RItem)
        self.rightHandScene.addItem(pinky02RItem)
        self.rightHandScene.addItem(pinky03RItem)
        self.rightHandScene.addItem(thumb01RItem)
        self.rightHandScene.addItem(thumb02RItem)
        self.rightHandScene.addItem(thumb03RItem)
        self.rightHandScene.addItem(sceneSwitcher.SceneSwitcher(self,
                                                               'FullBody',
                                                               self.view,
                                                               self.fullBodyScene,
                                                               os.path.join(self.ICON_DIR_PATH, 'ReturnToArrow.png'),
                                                               50, 25, 25))

        self.mirrorInfo.clear()
        self.mirrorInfo = {
            clavicleLItem: clavicleRItem,
            upperarmLItem: upperarmRItem,
            lowerarmLItem: lowerarmRItem,
            handLItem: handRItem,
            thighLItem: thighRItem,
            calfLItem: calfRItem,
            footLItem: footRItem,
            ballLItem: ballRItem,
            index01LItem: index01RItem,
            index02LItem: index02RItem,
            index03LItem: index03RItem,
            middle01LItem: middle01RItem,
            middle02LItem: middle02RItem,
            middle03LItem: middle03RItem,
            ring01LItem: ring01RItem,
            ring02LItem: ring02RItem,
            ring03LItem: ring03RItem,
            pinky01LItem: pinky01RItem,
            pinky02LItem: pinky02RItem,
            pinky03LItem: pinky03RItem,
            thumb01LItem: thumb01RItem,
            thumb02LItem: thumb02RItem,
            thumb03LItem: thumb03RItem,
            clavicleRItem: clavicleLItem,
            upperarmRItem: upperarmLItem,
            lowerarmRItem: lowerarmLItem,
            handRItem: handLItem,
            thighRItem: thighLItem,
            calfRItem: calfLItem,
            footRItem: footLItem,
            ballRItem: ballLItem,
            index01RItem: index01LItem,
            index02RItem: index02LItem,
            index03RItem: index03LItem,
            middle01RItem: middle01LItem,
            middle02RItem: middle02LItem,
            middle03RItem: middle03LItem,
            ring01RItem: ring01LItem,
            ring02RItem: ring02LItem,
            ring03RItem: ring03LItem,
            pinky01RItem: pinky01LItem,
            pinky02RItem: pinky02LItem,
            pinky03RItem: pinky03LItem,
            thumb01RItem: thumb01LItem,
            thumb02RItem: thumb02LItem,
            thumb03RItem: thumb03LItem
        }

    ### Publish Methods ###
    @classmethod
    def showUI(cls):
        if not cls.instance:
            cls.instance = TakRetargeterUI()
        if cls.instance.isHidden():
            cls.instance.show()
        else:
            cls.instance.raise_()
            cls.instance.activateWindow()

    def showEvent(self, event):
        if self.geo:
            super(TakRetargeterUI, self).showEvent(event)
            self.restoreGeometry(self.geo)

    def closeEvent(self, event):
        if isinstance(self, TakRetargeterUI):
            super(TakRetargeterUI, self).closeEvent(event)
            self.geo = self.saveGeometry()

def rightSideItemPos(posX, imageWidth):
    rightSidePos = None

    middle = imageWidth * 0.5
    offset = posX-middle
    rightSidePos = middle - offset

    return rightSidePos

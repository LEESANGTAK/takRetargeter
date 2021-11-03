from weakref import WeakKeyDictionary
import types

import maya.cmds as cmds
import pymel.core as pm

from charDefinition import CharDefinition


class CharDefProperty(object):
    def __init__(self):
        self.__val = WeakKeyDictionary()

    def __get__(self, obj, objType):
        return self.__val.get(obj)

    def __set__(self, obj, val):
        if not isinstance(val, CharDefinition):
            raise ValueError('Value type is should be CharDefinition')
        self.__val[obj] = val

    def __delete__(self, obj):
        del self.__val[obj]


class Retargeter(object):
    PLUG_IN = 'poleVector'

    targetCharDef = CharDefProperty()
    sourceCharDef = CharDefProperty()

    def __init__(self):
        super(Retargeter, self).__init__()

        self.charDefs = {'None': None}
        self.limbInfo = {
            'arm_l': ['upperarm_l', 'lowerarm_l', 'hand_l'],
            'arm_r': ['upperarm_r', 'lowerarm_r', 'hand_r'],
            'leg_l': ['thigh_l', 'calf_l', 'foot_l'],
            'leg_r': ['thigh_r', 'calf_r', 'foot_r']
        }

        if not cmds.pluginInfo(Retargeter.PLUG_IN, q=True, loaded=True):
            cmds.loadPlugin(Retargeter.PLUG_IN)

    def connect(self):
        self.targetCharDef.setTPose()
        self.sourceCharDef.setTPose()

        publicAttrs = [member for member in dir(self.sourceCharDef) if not member.startswith('_')]
        for attr in publicAttrs:
            targetAttrVal = getattr(self.targetCharDef, attr)
            sourceAttrVal = getattr(self.sourceCharDef, attr)
            if isinstance(sourceAttrVal, dict):
                src = sourceAttrVal.get('name')
                trg = targetAttrVal.get('name')
                if src and cmds.objExists(src) and trg and cmds.objExists(trg):
                    if attr == 'root':
                        cmds.parentConstraint(src, trg, mo=True)
                    else:
                        try:
                            cmds.orientConstraint(src, trg, mo=True)
                            if attr == 'pelvis':
                                cmds.pointConstraint(src, trg, mo=True)
                        except:
                            pass

        # Connect ik limb controllers
        for limb in self.limbInfo:
            limbAttrs = self.limbInfo.get(limb)
            limbStartAttr = limbAttrs[0]
            limbMiddleAttr = limbAttrs[1]
            limbEndAttr = limbAttrs[2]

            limbStartCtrlInfo = getattr(self.targetCharDef, limbStartAttr)
            if not limbStartCtrlInfo.get('name'):  # When limb start controller does not exists, ik controllers assigned
                ctrl = getattr(self.targetCharDef, limbEndAttr).get('name')
                poleVectorCtrl = getattr(self.targetCharDef, limbMiddleAttr).get('name')
                srcStartObj = getattr(self.sourceCharDef, limbStartAttr).get('name')
                srcMiddleObj = getattr(self.sourceCharDef, limbMiddleAttr).get('name')
                srcEndObj = getattr(self.sourceCharDef, limbEndAttr).get('name')

                Retargeter.connectIkLimbCtrls(srcStartObj, srcMiddleObj, srcEndObj, ctrl, poleVectorCtrl)

        # # Display warning for failed connection
        # for src, trg in connectionFailInfo.items():
        #     cmds.warning('"{0} -> {1}" connetion failed.'.format(src, trg))

    def disconnect(self):
        publicAttrs = [member for member in dir(self.targetCharDef) if not member.startswith('_')]
        for attr in publicAttrs:
            targetAttrVal = getattr(self.targetCharDef, attr)
            if isinstance(targetAttrVal, dict):
                trg = targetAttrVal.get('name')
                if trg and cmds.objExists(trg):
                    cmds.select(trg, r=True)
                    cmds.DeleteConstraints(trg)
                    poleVectorNodes = cmds.listConnections(trg, d=False, type='poleVector')
                    if poleVectorNodes:
                        cmds.delete(poleVectorNodes)

    @staticmethod
    def connectIkLimbCtrls(startObj, middleObj, endObj, ctrl, poleVectorCtrl):
        # Convert to pymel node object
        startObj = pm.PyNode(startObj) if isinstance(startObj, basestring) else startObj
        middleObj = pm.PyNode(middleObj) if isinstance(middleObj, basestring) else middleObj
        endObj = pm.PyNode(endObj) if isinstance(endObj, basestring) else endObj
        ctrl = pm.PyNode(ctrl) if isinstance(ctrl, basestring) else ctrl
        poleVectorCtrl = pm.PyNode(poleVectorCtrl) if isinstance(poleVectorCtrl, basestring) else poleVectorCtrl

        poleVectorCtrl.inheritsTransform.set(False)
        pm.pointConstraint(endObj, ctrl, mo=True)

        poleVectorNode = pm.createNode('poleVector')

        startObj.worldMatrix >> poleVectorNode.startWorldMatrix
        middleObj.worldMatrix >> poleVectorNode.middleWorldMatrix
        endObj.worldMatrix >> poleVectorNode.endWorldMatrix
        poleVectorNode.outVector >> poleVectorCtrl.translate

    def bake(self):
        bakeCtrls = []

        publicAttrs = [member for member in dir(self.targetCharDef) if not member.startswith('_')]
        for attr in publicAttrs:
            targetAttrVal = getattr(self.targetCharDef, attr)
            if isinstance(targetAttrVal, dict):
                trg = targetAttrVal.get('name')
                if trg and cmds.objExists(trg):
                    bakeCtrls.append(trg)

        cmds.select(bakeCtrls, r=True)
        minFrame = cmds.playbackOptions(q=True, min=True)
        maxFrame = cmds.playbackOptions(q=True, max=True)
        cmds.bakeResults(simulation=True, t=(minFrame, maxFrame))

        self.disconnect()
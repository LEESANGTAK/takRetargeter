from weakref import WeakKeyDictionary
import maya.cmds as cmds
from .charDefinition import CharDefinition


PLUG_IN = 'poleVector'
if not cmds.pluginInfo(PLUG_IN, q=True, loaded=True):
    cmds.loadPlugin(PLUG_IN)


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

    def connect(self):
        self.targetCharDef.stancePose()
        self.sourceCharDef.stancePose()

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

    def disconnect(self):
        publicAttrs = [member for member in dir(self.targetCharDef) if not member.startswith('_')]
        for attr in publicAttrs:
            targetAttrVal = getattr(self.targetCharDef, attr)
            if isinstance(targetAttrVal, dict):
                trg = targetAttrVal.get('name')
                if trg and cmds.objExists(trg):
                    constraints = cmds.listConnections(trg, d=False, type='constraint') or []
                    if constraints:
                        cmds.delete(constraints)

    @staticmethod
    def connectIkLimbCtrls(startObj, middleObj, endObj, ctrl, poleVectorCtrl):
        cmds.pointConstraint(endObj, ctrl, mo=True)

        # Pole vector connection
        poleVectorLocatorName = '{0}_poleVector_loc'.format(poleVectorCtrl)
        if not cmds.objExists(poleVectorLocatorName):
            poleVectorLocator = cmds.spaceLocator(n=poleVectorLocatorName)[0]
            poleVectorNode = cmds.createNode('poleVector')
            cmds.connectAttr('{}.worldMatrix[0]'.format(startObj), '{}.startWorldMatrix'.format(poleVectorNode))
            cmds.connectAttr('{}.worldMatrix[0]'.format(middleObj), '{}.middleWorldMatrix'.format(poleVectorNode))
            cmds.connectAttr('{}.worldMatrix[0]'.format(endObj), '{}.endWorldMatrix'.format(poleVectorNode))
            cmds.connectAttr('{}.outVector'.format(poleVectorNode), '{}.translate'.format(poleVectorLocator))
        else:
            poleVectorLocator = poleVectorLocatorName
        cmds.pointConstraint(poleVectorLocator, poleVectorCtrl, mo=False)

    def bake(self):
        bakeCtrls = self._getAllNamesInDefinition()

        # Get frame range
        minFrame = cmds.playbackOptions(q=True, min=True)
        maxFrame = cmds.playbackOptions(q=True, max=True)

        # Bake keyframes with viewport refresh off
        cmds.refresh(su=True)
        cmds.select(bakeCtrls, r=True)
        cmds.bakeResults(simulation=True, t=(minFrame, maxFrame))
        cmds.refresh(su=False)

        self.disconnect()

        # Apply euler filter
        cmds.select(bakeCtrls, r=True)
        cmds.filterCurve()
        cmds.select(cl=True)

    def deleteKeyframes(self):
        bakeCtrls = self._getAllNamesInDefinition()
        cmds.cutKey(bakeCtrls)

    def _getAllNamesInDefinition(self):
        allNames = []
        publicAttrs = [member for member in dir(self.targetCharDef) if not member.startswith('_')]
        for attr in publicAttrs:
            targetAttrVal = getattr(self.targetCharDef, attr)
            if isinstance(targetAttrVal, dict):
                trg = targetAttrVal.get('name')
                if trg and cmds.objExists(trg):
                    allNames.append(trg)
        return allNames

from weakref import WeakKeyDictionary
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

        if not pm.pluginInfo(Retargeter.PLUG_IN, q=True, loaded=True):
            pm.loadPlugin(Retargeter.PLUG_IN)

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
                if src and pm.objExists(src) and trg and pm.objExists(trg):
                    if attr == 'root':
                        pm.parentConstraint(src, trg, mo=True)
                    else:
                        try:
                            pm.orientConstraint(src, trg, mo=True)
                            if attr == 'pelvis':
                                pm.pointConstraint(src, trg, mo=True)
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
                if trg and pm.objExists(trg):
                    pm.delete(pm.listConnections(trg, d=False, type='constraint'))

    @staticmethod
    def connectIkLimbCtrls(startObj, middleObj, endObj, ctrl, poleVectorCtrl):
        # Convert to pymel node object
        startObj = pm.PyNode(startObj)
        middleObj = pm.PyNode(middleObj)
        endObj = pm.PyNode(endObj)
        ctrl = pm.PyNode(ctrl)
        poleVectorCtrl = pm.PyNode(poleVectorCtrl)

        pm.pointConstraint(endObj, ctrl, mo=True)

        # Pole vector connection
        poleVectorLocator = '{0}_poleVector_loc'.format(poleVectorCtrl.name())
        if not pm.objExists(poleVectorLocator):
            poleVectorLocator = pm.spaceLocator(n='{0}_poleVector_loc'.format(poleVectorCtrl.name()))
            poleVectorNode = pm.createNode('poleVector')
            startObj.worldMatrix >> poleVectorNode.startWorldMatrix
            middleObj.worldMatrix >> poleVectorNode.middleWorldMatrix
            endObj.worldMatrix >> poleVectorNode.endWorldMatrix
            poleVectorNode.outVector >> poleVectorLocator.translate
        pm.pointConstraint(poleVectorLocator, poleVectorCtrl, mo=False)

    def bake(self):
        bakeCtrls = []

        publicAttrs = [member for member in dir(self.targetCharDef) if not member.startswith('_')]
        for attr in publicAttrs:
            targetAttrVal = getattr(self.targetCharDef, attr)
            if isinstance(targetAttrVal, dict):
                trg = targetAttrVal.get('name')
                if trg and pm.objExists(trg):
                    bakeCtrls.append(trg)

        # Get frame range
        minFrame = pm.playbackOptions(q=True, min=True)
        maxFrame = pm.playbackOptions(q=True, max=True)

        # Bake keyframes with viewport refresh off
        pm.refresh(su=True)
        pm.select(bakeCtrls, r=True)
        pm.bakeResults(simulation=True, t=(minFrame, maxFrame))
        pm.refresh(su=False)

        self.disconnect()

        # Apply euler filter
        pm.select(bakeCtrls, r=True)
        pm.mel.filterCurve()
        pm.select(cl=True)

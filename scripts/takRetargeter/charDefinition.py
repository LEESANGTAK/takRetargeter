from weakref import WeakKeyDictionary
from collections import OrderedDict
import json
import types

import maya.cmds as cmds
import pymel.core as pm


class Property(object):
    def __init__(self):
        self.__name = WeakKeyDictionary()
        self.__translate = WeakKeyDictionary()
        self.__rotate = WeakKeyDictionary()

    def __get__(self, obj, objtype):
        returnVal = OrderedDict([
            ('name', self.__name.get(obj)),
            ('translate', self.__translate.get(obj)),
            ('rotate', self.__rotate.get(obj))
        ])
        return returnVal

    def __set__(self, obj, val):
        if isinstance(val, str):  # When set with name
            self.__name[obj] = val
            self.__translate[obj] = cmds.getAttr('%s.translate' % val)[0]
            self.__rotate[obj] = cmds.getAttr('%s.rotate' % val)[0]
        elif isinstance(val, dict):  # When set with loaded information
            self.__name[obj] = val.get('name')
            self.__translate[obj] = val.get('translate')
            self.__rotate[obj] = val.get('rotate')
        elif val == None:
            self.__name[obj] = None
            self.__translate[obj] = None
            self.__rotate[obj] = None

    def __delete__(self, obj):
        del self.__name[obj], self.__translate[obj], self.__rotate[obj]


class CharDefinition(object):
    namespace = ''
    root = Property()
    pelvis = Property()
    spine_01 = Property()
    spine_02 = Property()
    spine_03 = Property()
    neck_01 = Property()
    head = Property()

    clavicle_l = Property()
    upperarm_l = Property()
    lowerarm_l = Property()
    hand_l = Property()

    index_01_l = Property()
    index_02_l = Property()
    index_03_l = Property()
    middle_01_l = Property()
    middle_02_l = Property()
    middle_03_l = Property()
    ring_01_l = Property()
    ring_02_l = Property()
    ring_03_l = Property()
    pinky_01_l = Property()
    pinky_02_l = Property()
    pinky_03_l = Property()
    thumb_01_l = Property()
    thumb_02_l = Property()
    thumb_03_l = Property()

    clavicle_r = Property()
    upperarm_r = Property()
    lowerarm_r = Property()
    hand_r = Property()

    index_01_r = Property()
    index_02_r = Property()
    index_03_r = Property()
    middle_01_r = Property()
    middle_02_r = Property()
    middle_03_r = Property()
    ring_01_r = Property()
    ring_02_r = Property()
    ring_03_r = Property()
    pinky_01_r = Property()
    pinky_02_r = Property()
    pinky_03_r = Property()
    thumb_01_r = Property()
    thumb_02_r = Property()
    thumb_03_r = Property()

    thigh_l = Property()
    calf_l = Property()
    foot_l = Property()
    ball_l = Property()

    thigh_r = Property()
    calf_r = Property()
    foot_r = Property()
    ball_r = Property()

    def __init__(self):
        super(CharDefinition, self).__init__()

        self.name = None

    def save(self, filename):
        charDefInfo = OrderedDict()
        publicAttrs = [member for member in dir(self) if not member.startswith('_')]
        for attr in publicAttrs:
            attrVal = getattr(self, attr)
            if not isinstance(attrVal, types.MethodType):
                charDefInfo[attr] = attrVal

        with open(filename, 'w') as f:
            json.dump(charDefInfo, f, indent=4)

    def load(self, filename):
        with open(filename, 'r') as f:
            charDefInfo = json.load(f)

        for attr, attrInfo in charDefInfo.items():
            if not isinstance(attrInfo, types.MethodType):
                setattr(self, attr, attrInfo)

    def stancePose(self):
        publicAttrs = [member for member in dir(self) if not member.startswith('_')]
        pm.undoInfo(openChunk=True)
        for attr in publicAttrs:
            attrVal = getattr(self, attr)
            if isinstance(attrVal, dict):
                name = attrVal.get('name')
                translateVal = attrVal.get('translate')
                rotateVal = attrVal.get('rotate')
                if name:
                    name = self.namespace + name
                    if cmds.objExists(name):
                        trsf = pm.PyNode(name)
                        try:
                            trsf.translate.set(translateVal)
                        except:
                            pass
                        try:
                            trsf.rotate.set(rotateVal)
                        except:
                            pass
        pm.undoInfo(closeChunk=True)

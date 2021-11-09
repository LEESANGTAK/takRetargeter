"""
Author: Sangtak Lee
Website: https://tak.ta-note.com

Created: 03/16/2020
Updated: 05/09/2020

Description:
Sets pole vector value on "outVector" attribute from input "start/mid/end world matrix".
"length" attribute controls pole vector length.

If pole vector control connected from "outVector" attribute has parent transform node, turn off "inheritsTransform" option of the parent transform node.
"""

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys


class PoleVector(OpenMayaMPx.MPxNode):
    name = 'poleVector'
    id = OpenMaya.MTypeId(0x00002744)

    aStartWorldMatrix = OpenMaya.MObject()
    aMiddleWorldMatrix = OpenMaya.MObject()
    aEndWorldMatrix = OpenMaya.MObject()
    aLength = OpenMaya.MObject()
    aOutVectorX = OpenMaya.MObject()
    aOutVectorY = OpenMaya.MObject()
    aOutVectorZ = OpenMaya.MObject()
    aOutVector = OpenMaya.MObject()

    def __init__(self):
        super(PoleVector, self).__init__()

    @classmethod
    def creator(cls):
        return OpenMayaMPx.asMPxPtr(PoleVector())

    @classmethod
    def initialize(cls):
        mAttr = OpenMaya.MFnMatrixAttribute()
        nAttr = OpenMaya.MFnNumericAttribute()

        cls.aStartWorldMatrix = mAttr.create('startWorldMatrix', 'startWorldMatrix')
        mAttr.setStorable(True)
        mAttr.setReadable(False)

        cls.aMiddleWorldMatrix = mAttr.create('middleWorldMatrix', 'middleWorldMatrix')
        mAttr.setStorable(True)
        mAttr.setReadable(False)

        cls.aEndWorldMatrix = mAttr.create('endWorldMatrix', 'endWorldMatrix')
        mAttr.setStorable(True)
        mAttr.setReadable(False)

        cls.aLength = nAttr.create('length', 'length', OpenMaya.MFnNumericData.kFloat, 50.0)
        nAttr.setKeyable(True)
        nAttr.setStorable(True)
        nAttr.setReadable(False)

        cls.aOutVectorX = nAttr.create('outVectorX', 'outVectorX', OpenMaya.MFnNumericData.kDouble)
        cls.aOutVectorY = nAttr.create('outVectorY', 'outVectorY', OpenMaya.MFnNumericData.kDouble)
        cls.aOutVectorZ = nAttr.create('outVectorZ', 'outVectorZ', OpenMaya.MFnNumericData.kDouble)
        cls.aOutVector = nAttr.create('outVector', 'outVector', cls.aOutVectorX, cls.aOutVectorY, cls.aOutVectorZ)
        nAttr.setStorable(False)
        nAttr.setWritable(False)

        cls.addAttribute(cls.aStartWorldMatrix)
        cls.addAttribute(cls.aMiddleWorldMatrix)
        cls.addAttribute(cls.aEndWorldMatrix)
        cls.addAttribute(cls.aOutVector)
        cls.addAttribute(cls.aLength)

        cls.attributeAffects(cls.aStartWorldMatrix, cls.aOutVector)
        cls.attributeAffects(cls.aMiddleWorldMatrix, cls.aOutVector)
        cls.attributeAffects(cls.aEndWorldMatrix, cls.aOutVector)
        cls.attributeAffects(cls.aLength, cls.aOutVector)

    def compute(self, plug, dataBlock):
        startWorldMatrix = dataBlock.inputValue(PoleVector.aStartWorldMatrix).asMatrix()
        middleWorldMatrix = dataBlock.inputValue(PoleVector.aMiddleWorldMatrix).asMatrix()
        endWorldMatrix = dataBlock.inputValue(PoleVector.aEndWorldMatrix).asMatrix()

        startTransformMatrix = OpenMaya.MTransformationMatrix(startWorldMatrix)
        middleTransformMatrix = OpenMaya.MTransformationMatrix(middleWorldMatrix)
        endTransformMatrix = OpenMaya.MTransformationMatrix(endWorldMatrix)

        length = dataBlock.inputValue(PoleVector.aLength).asFloat()

        startVector = startTransformMatrix.translation(OpenMaya.MSpace.kWorld)
        middleVector = middleTransformMatrix.translation(OpenMaya.MSpace.kWorld)
        endVector = endTransformMatrix.translation(OpenMaya.MSpace.kWorld)

        halfVector = (startVector + endVector) * 0.5
        poleVector = middleVector - halfVector
        poleVector.normalize()
        outVector = (middleVector + (poleVector * length))

        outVectorHndl = dataBlock.outputValue(PoleVector.aOutVector)
        outVectorHndl.setMVector(outVector)
        dataBlock.setClean(plug)


def initializePlugin(pluginObj):
    pluginFn = OpenMayaMPx.MFnPlugin(pluginObj, 'Tak', '1.1.0')

    try:
        pluginFn.registerNode(PoleVector.name, PoleVector.id, PoleVector.creator, PoleVector.initialize, OpenMayaMPx.MPxNode.kDependNode)
    except:
        sys.stderr.write('Fail to register node {0}.'.format(PoleVector.name))
        raise

def uninitializePlugin(pluginObj):
    pluginFn = OpenMayaMPx.MFnPlugin(pluginObj)

    try:
        pluginFn.deregisterNode(PoleVector.id)
    except:
        sys.stderr.write('Fail to deregister node {0}.'.format(PoleVector.name))
        raise

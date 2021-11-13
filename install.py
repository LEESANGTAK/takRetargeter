"""
Author: TAK
Website: https://ta-note.com
Description:
    Drag and drop install.py file in maya viewport.
    Shelf button will added in the current shelf tab.
    "<moduleName>.mod" file will created in "Documents\maya\modules" directory automatically.
"""

import os
import sys

import maya.cmds as cmds
import maya.mel as mel


# Need to modify depend on module
MODULE_VERSION = '1.0.1'
MODULE_NAME = os.path.dirname(__file__).rsplit('/', 1)[-1]
MODULE_PATH = os.path.dirname(__file__)
SHELF_ICON_FILE = 'takRetargeterIcon.png'
SHELF_BUTTON_COMMAND = '''
import takRetargeter.ui as tru

try:
    trUI.close()
except:
    pass

trUI = tru.takRetargeterUI.TakRetargeterUI()
trUI.show()
'''


def onMayaDroppedPythonFile(*args, **kwargs):
    modulesDir = getModulesDirectory()
    createModuleFile(modulesDir)
    addScriptPath()
    loadPlugins()
    addShelfButtons()


def getModulesDirectory():
    modulesDir = None

    documentDir = os.path.expanduser('~')
    mayaAppDir = os.path.join(documentDir, 'maya')
    modulesDir = os.path.join(mayaAppDir, 'modules')

    if not os.path.exists(modulesDir):
        os.mkdir(modulesDir)

    return modulesDir


def createModuleFile(modulesDir):
    moduleFileName = '{0}.mod'.format(MODULE_NAME)

    contents = '+ {0} {1} {2}'.format(MODULE_NAME, MODULE_VERSION, MODULE_PATH)

    with open(os.path.join(modulesDir, moduleFileName), 'w') as f:
        f.write(contents)


def addScriptPath():
    scriptPath = MODULE_PATH + '/scripts'
    if not scriptPath in sys.path:
        sys.path.append(scriptPath)


def loadPlugins():
    pluginsPath = os.path.join(MODULE_PATH, 'plug-ins')
    if os.path.exists(pluginsPath):
        pluginFiles = os.listdir(pluginsPath)
        if pluginFiles:
            for pluginFile in pluginFiles:
                cmds.loadPlugin(os.path.join(pluginsPath, pluginFile))


def addShelfButtons():
    curShelf = getCurrentShelf()

    cmds.shelfButton(
        command=SHELF_BUTTON_COMMAND,
        annotation=MODULE_NAME,
        sourceType='Python',
        image=SHELF_ICON_FILE,
        image1=SHELF_ICON_FILE,
        parent=curShelf
    )


def getCurrentShelf():
    curShelf = None

    shelf = mel.eval('$gShelfTopLevel = $gShelfTopLevel')
    curShelf = cmds.tabLayout(shelf, query=True, selectTab=True)

    return curShelf

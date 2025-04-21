"""
Author: Tak
Website: https://ta-note.com
Description:
    Drag and drop this file to the maya viewport.
    "<ModuleName>.mod" file will be created in the "C:/Users/<UserName>/Documents/maya/modules" directory.
"""

import os
import sys
import imp

import maya.cmds as cmds
import maya.mel as mel


MODULE_PATH = os.path.dirname(__file__).replace('\\', '/')
MODULE_NAME = MODULE_PATH.rsplit('/', 1)[-1]
MAYA_VERSION = int(cmds.about(version=True))
AVAILABLE_VERSIONS = [2022, 2023, 2024]
MODULE_VERSION = 'any'
SHELF_ICON_FILE = 'takRetargeterIcon.png'
SHELF_BUTTON_COMMAND = '''import takRetargeter.ui as tru
try:
    trUI.close()
except:
    pass
trUI = tru.takRetargeterUI.TakRetargeterUI()
trUI.show()
'''


def onMayaDroppedPythonFile(*args, **kwargs):
    removeOldInstallModule()

    addEnvPaths()
    runScripts()

    addShelfButtons()
    createModuleFile()
    cmds.confirmDialog(
        title='Info',
        message='"{}" module is installed successfully.\nTool icon added in the "{}" shelf.'.format(MODULE_NAME, getCurrentShelf())
    )


def removeOldInstallModule():
    foundOldInstall = False
    for modName in sys.modules:
        if modName == 'install':
            foundOldInstall = True
            break
    if foundOldInstall:
        del(sys.modules[modName])


def addEnvPaths():
    # Add plug-ins paths
    pluginsPaths = mel.eval('getenv "MAYA_PLUG_IN_PATH";')
    pluginsPaths += ';{}/plug-ins'.format(MODULE_PATH)
    mel.eval('putenv "MAYA_PLUG_IN_PATH" "{}";'.format(pluginsPaths))

    # Add python script paths
    pythonPathes = [
        '{}/scripts'.format(MODULE_PATH),
    ]
    for pythonPath in pythonPathes:
        sys.path.append(pythonPath)

    # Add icon folder path
    iconPaths = mel.eval('getenv "XBMLANGPATH";')
    iconPaths += ';{}/icons'.format(MODULE_PATH)
    mel.eval('putenv "XBMLANGPATH" "{}";'.format(iconPaths))


def runScripts():
    # Install python packages
    # Packages will be installed in "C:\Users\<User Name>\AppData\Roaming\Python\<Python Version>\site-packages"
    os.putenv('MayaVersion', str(MAYA_VERSION))
    os.system('{}/install_python_packages.bat'.format(MODULE_PATH))


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


def createModuleFile():
    moduleFileName = '{}.mod'.format(MODULE_NAME)

    contentsBlock = '''+ MAYAVERSION:{3} {0} {1} {2}

'''
    contents = ''
    for availVersion in AVAILABLE_VERSIONS:
        contents += contentsBlock.format(MODULE_NAME, MODULE_VERSION, MODULE_PATH, availVersion)

    with open(os.path.join(getModulesDirectory(), moduleFileName), 'w') as f:
        f.write(contents)


def getModulesDirectory():
    modulesDir = None

    mayaAppDir = cmds.internalVar(uad=True)
    modulesDir = os.path.join(mayaAppDir, 'modules')

    if not os.path.exists(modulesDir):
        os.mkdir(modulesDir)

    return modulesDir

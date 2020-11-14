import os
import shutil

env = lux.getActiveEnvironment()
snode = lux.getSceneTree()

def screenshot_view():
    snode.centerAndFit()
    #lux.setCamera(camera="Free Camera")
    lux.setStandardView(lux.VIEW_ISOMETRIC)
    #lux.VIEW_FRONT，lux.VIEW_BACK，lux.VIEW_LEFT，lux.VIEW_RIGHT，lux.VIEW_TOP，lux.VIEW_BOTTOM，lux.VIEW_ISOMETRIC
    path = lux.screenshot()
    return path

def copyFileToDir(path,pathto):
    shutil.move(path,pathto)


def main():
    path=screenshot_view()
    print(os.getcwd())





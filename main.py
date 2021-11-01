import uiautomator2 as u2
from hierachySolver import *
import time
import os
from util import *
import multiprocessing
import timeout_decorator
from grantPermissonDetector import *
from uiautomator2 import Direction
# youtube package name: com.google.android.youtube
# 192.168.56.101:5555
# 192.168.56.102:5555


# return value 0 success, 1 install fail, 2 no the same texts, 3 time out
@timeout_decorator.timeout(480, timeout_exception=StopIteration)
def uiExplorer(apkPath, saveDir, phoneDevice, tabletDevice):
    # packageName = 'com.google.android.youtube'
    # packageName = 'com.tubitv'
    d1, d2, connectStatus = connectionAdaptor(phoneDevice, tabletDevice)
    while not connectStatus:
        d1, d2, connectStatus = connectionAdaptor(phoneDevice, tabletDevice)

    # 0 success, 1 install fail
    installed1, packageName, mainActivity = installApk(apkPath, device=phoneDevice)
    if installed1 != 0:
        print('install ' + apkPath + ' fail.')
        return 1
    print('start to explore: ' + packageName)
    d1.app_start(packageName, use_monkey=True)

    installed2, packageName, mainActivity = installApk(apkPath, device=tabletDevice)
    if installed2 != 0:
        print('install ' + apkPath + ' fail.')
        return 1
    d2.app_start(packageName, use_monkey=True)
    subSaveDir = os.path.join(saveDir, packageName)
    if not os.path.exists(subSaveDir):
        os.mkdir(subSaveDir)

    d1.sleep(5)
    d2.sleep(5)

    d1_activity, d1_package, d1_launcher = getActivityPackage(d1)
    d2_activity, d2_package, d2_launcher = getActivityPackage(d2)
    if d1_package != d2_package or d1_activity != d2_activity:
        print('wait, sleep 3 s')
        d1.sleep(3)
        d2.sleep(3)

    grantPermissinActivitySolver(d1)
    grantPermissinActivitySolver(d2)
    xml1 = d1.dump_hierarchy(compressed=True)
    xml2 = d2.dump_hierarchy(compressed=True)
    img1 = d1.screenshot()
    img2 = d2.screenshot()
    xmlScreenSaver(subSaveDir, xml1, xml2, img1, img2, d1_activity, d2_activity)
    clickBounds = hierachySolver(xml1, xml2)

    # swipe forward to collect more data
    d1.swipe_ext(Direction.FORWARD)
    d2.swipe_ext(Direction.FORWARD)
    xml1 = d1.dump_hierarchy(compressed=True)
    xml2 = d2.dump_hierarchy(compressed=True)
    img1 = d1.screenshot()
    img2 = d2.screenshot()
    xmlScreenSaver(subSaveDir, xml1, xml2, img1, img2, d1_activity, d2_activity)
    d1.swipe_ext(Direction.BACKWARD)
    d2.swipe_ext(Direction.BACKWARD)
    if clickBounds is None or len(clickBounds) == 0:
        print('no the same texts to click, exit')
        d1.app_stop(packageName)
        d2.app_stop(packageName)
        print('uninstall ' + packageName)
        d1.app_uninstall(packageName)
        d2.app_uninstall(packageName)
        return 2
    for i in clickBounds:
        # click the same text in two screens
        bounds1 = i[0]
        bounds2 = i[1]
        print('click: ' + str(i[-1]))
        d1.click((bounds1[0] + bounds1[2]) / 2, (bounds1[1] + bounds1[3]) / 2)
        d2.click((bounds2[0] + bounds2[2]) / 2, (bounds2[1] + bounds2[3]) / 2)
        d1.sleep(3)
        d2.sleep(3)
        xml11 = d1.dump_hierarchy(compressed=True)
        xml22 = d2.dump_hierarchy(compressed=True)
        img11 = d1.screenshot()
        img22 = d2.screenshot()
        xmlScreenSaver(subSaveDir, xml11, xml22, img11, img22, d1_activity, d2_activity)

        # swipe forward to collect more data
        d1.swipe_ext(Direction.FORWARD)
        d2.swipe_ext(Direction.FORWARD)
        xml11 = d1.dump_hierarchy(compressed=True)
        xml22 = d2.dump_hierarchy(compressed=True)
        img11 = d1.screenshot()
        img22 = d2.screenshot()
        xmlScreenSaver(subSaveDir, xml11, xml22, img11, img22, d1_activity, d2_activity)
        d1.swipe_ext(Direction.BACKWARD)
        d2.swipe_ext(Direction.BACKWARD)

        # back to the original page
        d1.press('back')
        d2.press('back')
        print('back')
        d1.app_start(packageName, use_monkey=True)
        d2.app_start(packageName, use_monkey=True)
        d1.sleep(3)
        d2.sleep(3)

    d1.app_stop(packageName)
    d2.app_stop(packageName)
    print('uninstall ' + packageName)
    d1.app_uninstall(packageName)
    d2.app_uninstall(packageName)
    return 0


def batchUiExplorer():
    apksDir = r'apks'
    saveDir = r'saveData'
    device1Id = '192.168.56.101:5555'
    device2Id = '192.168.56.102:5555'
    log = r'log.txt'
    # return value 0 success, 1 install fail, 2 no the same texts, 3 time out
    # read test apks
    lines = open(log, 'r').readlines()
    apks = {}
    for i in lines:
        i = i.replace('\n', '')
        apk, status = i.split(' ')
        apks[apk] = int(status)
    with open(log, 'a+') as f:
        for file in os.listdir(apksDir):
            if file.endswith('.apk') or file.endswith('.xapk'):
                filePath = os.path.join(apksDir, file)
                status = apks.get(file, None)
                if status == 0:
                    print(filePath + 'has been explored')
                    continue
                try:
                    ret = uiExplorer(filePath, saveDir, device1Id, device2Id)
                    apks[file] = ret
                    if ret == 0:
                        f.write(file + ' 0' + '\n')
                    elif ret == 1:
                        f.write(file + ' 1' + '\n')
                    elif ret == 2:
                        f.write(file + ' 2' + '\n')
                except StopIteration:
                    print('time out ' + file)
                    apks[file] = 3
                    f.write(file + ' 3' + '\n')


def singleTest():
    apkPath = 'apks/youtube.apk'
    saveDir = 'saveData'
    device1Id = '192.168.56.101:5555'
    device2Id = '192.168.56.102:5555'
    uiExplorer(apkPath, saveDir, device1Id, device2Id)


if __name__ == '__main__':
    #singleTest()
    batchUiExplorer()

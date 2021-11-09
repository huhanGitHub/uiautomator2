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
delimiter = ' ||| '
ignoreApkStatus = [0, 1, 2]
loadSleepTime = 8
switchSleepTime = 3


# return value 0 success, 1 install fail, 2 no the same texts, 3 time out, 4 fail others
@timeout_decorator.timeout(600, timeout_exception=StopIteration)
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

    # wait for opening apps on two devices
    d1.sleep(5)
    d2.sleep(5)

    dialogSolver(d1)
    dialogSolver(d2)

    d1_activity, d1_package, d1_launcher = getActivityPackage(d1)
    d2_activity, d2_package, d2_launcher = getActivityPackage(d2)
    if d1_package != d2_package or d1_activity != d2_activity:
        print('pls wait, load sleep time')
        d1.sleep(loadSleepTime)
        d2.sleep(loadSleepTime)

    xml1 = d1.dump_hierarchy(compressed=True)
    xml2 = d2.dump_hierarchy(compressed=True)
    img1 = safeScreenshot(d1)
    img2 = safeScreenshot(d2)
    clickBounds1 = hierachySolver(xml1, xml2)

    if clickBounds1 is None or len(clickBounds1) == 0:
        print('no the same texts to click, exit')
        d1.app_stop(packageName)
        d2.app_stop(packageName)
        print('uninstall ' + packageName)
        d1.app_uninstall(packageName)
        d2.app_uninstall(packageName)
        return 2
    else:
        subSaveDir = os.path.join(saveDir, packageName)
        if not os.path.exists(subSaveDir):
            os.mkdir(subSaveDir)
        xmlScreenSaver(subSaveDir, xml1, xml2, img1, img2, d1_activity, d2_activity)

    for i in clickBounds1:
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
        img11 = safeScreenshot(d1)
        img22 = safeScreenshot(d2)
        xmlScreenSaver(subSaveDir, xml11, xml22, img11, img22, d1_activity, d2_activity)

        # swipe forward to collect more data
        d1.swipe_ext(Direction.FORWARD)
        d2.swipe_ext(Direction.FORWARD)
        xml11 = d1.dump_hierarchy(compressed=True)
        xml22 = d2.dump_hierarchy(compressed=True)
        img11 = safeScreenshot(d1)
        img22 = safeScreenshot(d2)
        xmlScreenSaver(subSaveDir, xml11, xml22, img11, img22, d1_activity, d2_activity)
        d1.swipe_ext(Direction.BACKWARD)
        d2.swipe_ext(Direction.BACKWARD)

        # back to the original page
        d1.press('back')
        d2.press('back')
        print('back...')

        dialogSolver(d1)
        dialogSolver(d2)

        d1.app_start(packageName, use_monkey=True)
        d2.app_start(packageName, use_monkey=True)

        d1.sleep(switchSleepTime)
        d2.sleep(switchSleepTime)

    # swipe forward to collect more data
    d1.swipe_ext(Direction.FORWARD)
    d2.swipe_ext(Direction.FORWARD)
    xmla = d1.dump_hierarchy(compressed=True)
    xmlb = d2.dump_hierarchy(compressed=True)
    imga = safeScreenshot(d1)
    imgb = safeScreenshot(d2)
    xmlScreenSaver(subSaveDir, xmla, xmlb, imga, imgb, d1_activity, d2_activity)

    clickBounds2 = hierachySolver(xmla, xmlb)
    if clickBounds2 is None:
        return 0
    for i in clickBounds2:
        if i in clickBounds1:
            continue
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

        dialogSolver(d1)
        dialogSolver(d2)

        # back to the original page
        d1.press('back')
        d2.press('back')
        print('back...')
        d1.app_start(packageName, use_monkey=True)
        d2.app_start(packageName, use_monkey=True)
        d1.sleep(3)
        d2.sleep(3)

    # d1.swipe_ext(Direction.BACKWARD)
    # d2.swipe_ext(Direction.BACKWARD)
    d1.app_stop(packageName)
    d2.app_stop(packageName)
    print('uninstall ' + packageName)
    d1.app_uninstall(packageName)
    d2.app_uninstall(packageName)
    return 0


def batchUiExplorer():
    apksDir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks'
    # apksDir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/apks'
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
        if i == '':
            continue
        apk, status = i.split(delimiter)
        apks[apk] = int(status)

    index = 0
    with open(log, 'a+') as f:
        for root, dirs, files in os.walk(apksDir):
            for file in files:
                if file.endswith('.apk') or file.endswith('.xapk'):
                    print('apk ' + str(index))
                    index += 1
                    filePath = os.path.join(root, file)
                    status = apks.get(file, None)
                    if status in ignoreApkStatus:
                        print(filePath + 'has been explored')
                        continue
                    try:
                        ret = uiExplorer(filePath, saveDir, device1Id, device2Id)
                        apks[file] = ret
                        if ret == 0:
                            f.write(file + delimiter + '0' + '\n')
                        elif ret == 1:
                            f.write(file + delimiter + '1' + '\n')
                        elif ret == 2:
                            f.write(file + delimiter + '2' + '\n')
                    except StopIteration:
                        print('time out ' + file)
                        apks[file] = 3
                        f.write(file + delimiter + '3' + '\n')
                    except Exception:
                        print('fail other ' + file)
                        apks[file] = 4
                        f.write(file + delimiter + '4' + '\n')


def unitTest():
    apkPath = '/Users/hhuu0025/PycharmProjects/uiautomator2/apks/[PRODUCTIVITY]SendAnywhere _File Transfer_ by Estmob Inc.-com.estmob.android.sendanywhere.apk'
    saveDir = 'saveData'
    device1Id = '192.168.56.101:5555'
    device2Id = '192.168.56.102:5555'
    uiExplorer(apkPath, saveDir, device1Id, device2Id)


if __name__ == '__main__':
    # unitTest()
    batchUiExplorer()

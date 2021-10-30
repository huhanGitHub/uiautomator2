import uiautomator2 as u2
import time
from difflib import SequenceMatcher
import requests
import os
from pyaxmlparser import APK
import subprocess


def connectionAdaptor(phoneDevice, tabletDevice):
    try:
        d1 = u2.connect(phoneDevice)
        d2 = u2.connect(tabletDevice)
        return d1, d2, True
    except requests.exceptions.ConnectionError:
        print('requests.exceptions.ConnectionError')
        return None, None, False


def installApk(apkPath, device=None):
    packageName, mainActivity = getPackageByApk(apkPath)

    # check if installed
    prefixCmd = 'adb '
    if device is not None:
        print('device: ' + device)
        prefixCmd = prefixCmd + '-s ' + device

    command1 = prefixCmd + ' shell pm list packages -3'
    packages = subprocess.check_output(command1, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    packages = packages.replace('package:', '').strip()
    packages = packages.replace('\r', '').strip()
    packages = packages.split('\n')
    if packageName in packages:
        print(packageName + ' has installed, begin to uninstall it')
        command2 = prefixCmd + ' uninstall ' + packageName
        out = subprocess.check_output(command2, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
        print('uninstall success')

    # begin to install apk
    command3 = prefixCmd + ' install ' + apkPath
    # os.system(command3)
    try:
        out = subprocess.check_output(command3, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
        print('install ' + apkPath + ' success')
        return 0, packageName, mainActivity
    except subprocess.CalledProcessError as e:
        print('install apk error: ' + apkPath)
        out = e.output.decode('utf-8')
        print(out)
        # 'adb: failed to install apks/VidMate.apk: Failure [INSTALL_FAILED_ALREADY_EXISTS: Attempt to re-install com.nemo.vidmate without first uninstalling.]
        return 1, packageName, mainActivity
    except FileNotFoundError:
        print('file not found: ' + apkPath)
        return 1, packageName, mainActivity


def getPackageByApk(apkPath):
    apkf = APK(apkPath)
    package = apkf.get_package()
    mainActivity = apkf.get_main_activity()
    return package, mainActivity


def getActivityPackage(d):
    isLauncher = False
    d_current = d.app_current()
    d_package = d_current['package']
    d_activity = d_current['activity']
    if 'android' in d_activity and 'Launcher' in d_activity:
        isLauncher = True
    d_activity = d_activity[d_activity.rindex('.') + 1:]
    return d_activity, d_package, isLauncher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def xmlScreenSaver(saveDir, xml1, xml2, img1, img2, activity1, activity2):
    t = int(time.time())
    xml1Name = 'phone_' + str(t) + '_' + activity1 + '.xml'
    img1Name = 'phone_' + str(t) + '_' + activity1 + '.png'
    xml1Path = os.path.join(saveDir, xml1Name)
    img1Path = os.path.join(saveDir, img1Name)

    # name both with activity1
    xml2Name = 'tablet_' + str(t) + '_' + activity1 + '.xml'
    img2Name = 'tablet_' + str(t) + '_' + activity1 + '.png'
    xml2Path = os.path.join(saveDir, xml2Name)
    img2Path = os.path.join(saveDir, img2Name)
    with open(xml1Path, 'a') as f1, open(xml2Path, 'a') as f2:
        f1.write(xml1)
        f2.write(xml2)
        img1.save(img1Path)
        img2.save(img2Path)
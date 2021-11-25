import os
import uiautomator2 as u2
import requests
import time
from util import installApk, getActivityPackage
import subprocess


def read_deeplinks(path):
    links_dict = {}
    with open(path, 'r', encoding='utf8') as f:
        links = f.read().split('\n\n\n')

        for link in links:
            link = link.split('\n')
            package_name = link[0]
            deeplinks = link[1:]
            links_dict[package_name] = deeplinks

    return links_dict


# adb shell am start -W -a android.intent.action.VIEW -d amazonprime://ParentalControlsSettings
def unitTraverse(apkPath, deviceId, deeplinks_dict):
    try:
        d = u2.connect(deviceId)
    except requests.exceptions.ConnectionError:
        print('requests.exceptions.ConnectionError')
        return False

    installed1, packageName, mainActivity = installApk(apkPath, device=deviceId)
    if installed1 != 0:
        print('install ' + apkPath + ' fail.')
        return False

    links = deeplinks_dict.get(packageName, None)
    if links is None:
        print('no this package: ' + packageName)
        return False

    d1_activity, d1_package, d1_launcher = getActivityPackage(d)

    total = len(links)
    success = 0
    for link in links:
        cmd = 'adb shell am start -W -a android.intent.action.VIEW -d ' + link
        try:
            p = subprocess.run(cmd, shell=True, timeout=8)
        except subprocess.TimeoutExpired:
            print('cmd timeout')
            d.app_stop(packageName)
            time.sleep(1)
            continue
        time.sleep(5)
        d2_activity, d2_package, d2_launcher = getActivityPackage(d)
        if d1_activity != d2_activity:
            success += 1
        d.app_stop(packageName)
        time.sleep(1)
    d.app_uninstall(packageName)
    print('\n\n\n' + packageName + ':' + str(total) + ' ' + str(success) + '\n\n\n')
    return total, success


def batchTraverse(apkDir, deviceId, deeplinks_dict):
    total = 0
    success = 0
    for root, dirs, files in os.walk(apkDir):
        for file in files:
            if str(file).endswith('.apk'):
                file_path = os.path.join(root, file)
                ret = unitTraverse(file_path, deviceId, deeplinks_dict)
                if not ret:
                    continue
                curTotal, curSuccess = ret
                total = total + curTotal
                success = success + curSuccess

    print('\n\n\n total: ' + str(total) + ' success: ' + str(success) + '\n\n\n')


if __name__ == '__main__':
    path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/deeplinks.txt'
    deeplinks_dict = read_deeplinks(path)
    apkPath = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks/bilibili_v1.16.2_apkpure..apk'
    deviceId = '192.168.56.104'
    apkDir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks'
    batchTraverse(apkDir, deviceId, deeplinks_dict)











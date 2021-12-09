import os
import uiautomator2 as u2
import requests
import time
from util import installApk, getActivityPackage, safeScreenshot, xmlScreenSaver_single, xmlScreenSaver
import subprocess
from grantPermissonDetector import dialogSolver
from uiautomator2.exceptions import SessionBrokenError
from hierachySolver import full_UI_click_test


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
def unit_traverse(apkPath, d, deeplinks_dict, visited, save_dir):
    crash_position = {}
    installed1, packageName, mainActivity = installApk(apkPath, reinstall=False)
    if installed1 != 0:
        print('install ' + apkPath + ' fail.')
        return False
    if packageName in visited:
        print('visited ' + packageName)
        d.app_uninstall(packageName)
        return False

    links = deeplinks_dict.get(packageName, None)
    if links is None:
        print('no this package: ' + packageName)
        d.app_uninstall(packageName)
        return False

    total = len(links)
    success = 0
    # sess = d.session(packageName)
    d1_activity, d1_package, d1_launcher = getActivityPackage(d)

    if d1_activity is None:
        print('error in get activity')
        d.app_uninstall(packageName)
        return False

    for index, link in enumerate(links):
        cmd = 'adb -s ' + deviceId + ' shell am start -W -a android.intent.action.VIEW -d ' + link
        try:
            p = subprocess.run(cmd, shell=True, timeout=8)
        except subprocess.TimeoutExpired:
            print('cmd timeout')
            d.app_stop(packageName)
            d.sleep(1)
            continue

        d.sleep(3)
        dialogSolver(d)
        d2_activity, d2_package, d2_launcher = getActivityPackage(d)
        if d1_activity != d2_activity or index == 0:
            success += 1
            xml1 = d.dump_hierarchy(compressed=True)
            img1 = safeScreenshot(d)
            xmlScreenSaver_single(save_dir, xml1, img1, d2_activity)

            #crash = full_UI_click_test(sess, xml1, cmd)

            # if len(crash) != 0:
            #     crash_position[d2_activity] = crash
            #     print(d2_activity, str(crash))

            d.app_stop(packageName)
            d.sleep(1)

    d.app_uninstall(packageName)
    print('\n\n\n' + packageName + ':' + str(total) + ' ' + str(success) + '\n\n\n')
    return packageName, total, success, crash_position


def unit_traverse_phoTab(apkPath, d1, d2, deviceId1, deviceId2, deeplinks_dict, visited, save_dir, collected_packages):
    crash_position = {}
    installed1, packageName, mainActivity = installApk(apkPath, device=deviceId1, reinstall=True)
    if installed1 != 0:
        print('install ' + apkPath + ' fail.')
        return False
    if packageName in visited:
        print('visited ' + packageName)
        d1.app_uninstall(packageName)
        return False

    if packageName not in collected_packages:
        return
    else:
        save_dir_package = os.path.join(save_dir, packageName)

    installed2, packageName, mainActivity = installApk(apkPath, device=deviceId2, reinstall=True)
    if installed2 != 0:
        print('install ' + apkPath + ' fail.')
        return False
    if packageName in visited:
        print('visited ' + packageName)
        d2.app_uninstall(packageName)
        return False

    links = deeplinks_dict.get(packageName, None)
    if links is None:
        print('no this package: ' + packageName)
        d1.app_uninstall(packageName)
        d2.app_uninstall(packageName)
        return False

    total = len(links)
    success = 0
    # sess = d.session(packageName)
    d1_activity, d1_package, d1_launcher = getActivityPackage(d1)
    d2_activity, d2_package, d2_launcher = getActivityPackage(d2)

    if d1_activity is None:
        print('error in get activity')
        d1.app_uninstall(packageName)
        return False

    if d2_activity is None:
        print('error in get activity')
        d2.app_uninstall(packageName)
        return False

    for index, link in enumerate(links):
        cmd = 'adb -s ' + deviceId + ' shell am start -W -a android.intent.action.VIEW -d ' + link
        try:
            p = subprocess.run(cmd, shell=True, timeout=8)
        except subprocess.TimeoutExpired:
            print('cmd timeout')
            d1.app_stop(packageName)
            d1.sleep(1)

            d2.app_stop(packageName)
            d2.sleep(1)
            continue

        d1.sleep(3)
        d2.sleep(3)
        dialogSolver(d1)
        dialogSolver(d2)

        d11_activity, d11_package, d11_launcher = getActivityPackage(d1)
        d22_activity, d22_package, d22_launcher = getActivityPackage(d2)

        if (d1_activity != d11_activity and d2_activity != d22_activity) or index == 0:
            success += 1
            xml1 = d1.dump_hierarchy(compressed=True)
            img1 = safeScreenshot(d1)

            xml2 = d2.dump_hierarchy(compressed=True)
            img2 = safeScreenshot(d2)

            size = img2.size

            if size[0] < size[1]:
                print('no tablet adaption')
                d1.app_stop(packageName)
                d2.app_stop(packageName)
                print('uninstall ' + packageName)
                d1.app_uninstall(packageName)
                d2.app_uninstall(packageName)
                return

            xmlScreenSaver(save_dir_package, xml1, xml2, img1, img2, d11_activity, d22_activity)

            d1.app_stop(packageName)
            d1.sleep(1)

            d2.app_stop(packageName)
            d2.sleep(1)

    d1.app_uninstall(packageName)
    d2.app_uninstall(packageName)
    print('\n\n\n' + packageName + ':' + str(total) + ' ' + str(success) + '\n\n\n')
    return packageName, total, success, crash_position


def batch_traverse(apkDir, deviceId, deeplinks_dict, save_dir, log=r'log.txt'):
    total = 0
    success = 0
    index = 0
    visited = []
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    with open(log, 'r+', encoding='utf8') as f:
        logs = f.readlines()
        for line in logs:
            line = line.split(' ')
            visited.append(line[0])

    crash_positions = {}

    try:
        d = u2.connect(deviceId)
    except requests.exceptions.ConnectionError:
        print('requests.exceptions.ConnectionError')
        return False

    with open(log, 'a+', encoding='utf8') as f:
        for root, dirs, files in os.walk(apkDir):
            for file in files:
                if str(file).endswith('.apk'):
                    index += 1
                    if index <= 0:
                        continue
                    file_path = os.path.join(root, file)
                    ret = unit_traverse(file_path, d, deeplinks_dict, visited, save_dir)
                    if not ret:
                        continue
                    packageName, curTotal, curSuccess, crash_positions = ret
                    f.write(packageName + ' ' + str(curTotal) + ' ' + str(curSuccess) + ' ' + str(crash_positions) + '\n')
                    total = total + curTotal
                    success = success + curSuccess

                    print('index: ' + str(index))

        print('\n\n\n total: ' + str(total) + ' success: ' + str(success) + '\n\n\n')
        f.write('\n\n\n total: ' + str(total) + ' success: ' + str(success) + '\n\n\n')


def batch_traverse_phoTab(apkDir, deviceId1, deviceId2, deeplinks_dict, save_dir, log=r'log.txt'):
    total = 0
    success = 0
    index = 0
    visited = []
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    with open(log, 'r+', encoding='utf8') as f:
        logs = f.readlines()
        for line in logs:
            line = line.split(' ')
            visited.append(line[0])

    try:
        d1 = u2.connect(deviceId1)
        d2 = u2.connect(deviceId2)
    except requests.exceptions.ConnectionError:
        print('requests.exceptions.ConnectionError')
        return False

    crash_positions = {}

    collected_packages = [i for i in os.listdir(save_dir)]

    with open(log, 'a+', encoding='utf8') as f:
        for root, dirs, files in os.walk(apkDir):
            for file in files:
                if str(file).endswith('.apk'):
                    index += 1
                    file_path = os.path.join(root, file)
                    ret = unit_traverse_phoTab(file_path, d1, d2, deviceId1, deviceId2, deeplinks_dict, visited, save_dir, collected_packages)
                    if not ret:
                        continue
                    packageName, curTotal, curSuccess, crash_positions = ret
                    f.write(packageName + ' ' + str(curTotal) + ' ' + str(curSuccess) + ' ' + str(crash_positions) + '\n')
                    total = total + curTotal
                    success = success + curSuccess

                    print('index: ' + str(index))

        print('\n\n\n total: ' + str(total) + ' success: ' + str(success) + '\n\n\n')
        f.write('\n\n\n total: ' + str(total) + ' success: ' + str(success) + '\n\n\n')


if __name__ == '__main__':
    path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/unit_test.txt'
    deeplinks_dict = read_deeplinks(path)
    deviceId = '192.168.57.101'
    # deviceId = 'VEG0220B17010232'
    apkDir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks/unit_reapks'
    save_dir = r'unit_screen_sourcecode'
    batch_traverse(apkDir, deviceId, deeplinks_dict, save_dir)










from activity_traverse import unit_traverse_phoTab, batch_traverse_phoTab, read_deeplinks
import os
import uiautomator2 as u2
import requests


def unit_run():
    deeplinks_path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/deeplinks.txt'
    deeplinks_dict = read_deeplinks(deeplinks_path)

    log = r'pho_tab_log.txt'
    visited = []
    with open(log, 'a+', encoding='utf8') as f:
        logs = f.readlines()
        for line in logs:
            line = line.split(' ')
            visited.append(line[0])

    save_dir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/pho_tab_pair'
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    collceted_dir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/saveData'

    apk_path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks/fast_scanner_pdf_scan_app.apk'
    deviceId1 = '192.168.57.101'
    deviceId2 = '192.168.57.102'

    try:
        d1 = u2.connect(deviceId1)
        d2 = u2.connect(deviceId2)
    except requests.exceptions.ConnectionError:
        print('requests.exceptions.ConnectionError')
        return False

    crash_positions = {}

    collected_packages = [i for i in os.listdir(collceted_dir)]
    unit_traverse_phoTab(apk_path, d1, d2, deviceId1, deviceId2, deeplinks_dict, visited, save_dir, collected_packages)


def batch_run():
    deeplinks_path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/deeplinks.txt'
    deeplinks_dict = read_deeplinks(deeplinks_path)

    log = r'pho_tab_log.txt'
    save_dir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/pho_tab_pair'
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    package_dir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/saveData'

    apk_dir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks'
    deviceId1 = '192.168.57.101'
    deviceId2 = '192.168.57.102'

    batch_traverse_phoTab(apk_dir, deviceId1, deviceId2, deeplinks_dict, save_dir, package_dir, log=log)


if __name__ == '__main__':
    # unit_run()
    batch_run()
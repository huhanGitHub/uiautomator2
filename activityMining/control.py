from activityTraverse import read_deeplinks, batchTraverse


if __name__ == '__main__':
    path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/deeplinks.txt'
    deeplinks_dict = read_deeplinks(path)
    apkPath = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks/bilibili_v1.16.2_apkpure..apk'
    deviceId = '192.168.56.104'
    # batchTraverse(apkDir, deviceId, deeplinks_dict)

    deviceId2 = '192.168.56.101'
    con_apkDir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks'
    log = r'control.txt'
    batchTraverse(con_apkDir, deviceId2, deeplinks_dict, log)
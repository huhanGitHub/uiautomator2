from decompile_APK import unit_inject, unit_sign_APK


def unit_run_mining_tool():
    # apk_path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks/BUSINESS/com.coolmobilesolution.fastscannerfree/fast_scanner_pdf_scan_app.apk'
    # apk_path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks/BUSINESS/com.doft.android.carrier/doft_free_load_board_truc.apk'
    # apk_path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/apks/youtube.apk'
    # apk_path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/apks/Twitter_v9.22.0-release.0_apkpure.com.apk'
    apk_path = r'/Users/hhuu0025/PycharmProjects/uiautomator2/apks/app-debug.apk'
    app_save_dir = '/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks/unit_test'
    re_packaged_apk = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks/unit_reapks/unit.apk'
    deeplinks_path = r'./unit_test.txt'

    print('decompile APK...')
    unit_inject(apk_path, app_save_dir, re_packaged_apk, deeplinks_path)
    print('sign apk...')
    unit_sign_APK(re_packaged_apk)


if __name__ == '__main__':
    unit_run_mining_tool()
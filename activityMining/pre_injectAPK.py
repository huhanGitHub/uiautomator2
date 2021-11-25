import os
from injectApk import injectApk


def batchInject():
    apk_dir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks'
    save_dir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/data'
    re_packaged_apks = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks'
    for root, dirs, files in os.walk(apk_dir):
        for apk in files:
            if not str(apk).endswith('.apk'):
                continue

            apk_path = os.path.join(root, apk)
            app_save_dir = os.path.join(save_dir, apk)
            # if not os.path.exists(app_save_dir):
                # os.mkdir(app_save_dir)
            print('Start apktool')
            cmd1 = 'apktool d ' + apk_path + ' -f -o ' + app_save_dir
            os.system(cmd1)

            print('run inject apk')
            injectApk(app_save_dir)

            re_packaged_apk = os.path.join(re_packaged_apks, apk)
            cmd2 = 'apktool b ' + app_save_dir + ' --use-aapt2 -o ' + re_packaged_apk
            os.system(cmd2)


# /Users/hhuu0025/Downloads/SDK/build-tools/31.0.0/apksigner sign --ks /Users/hhuu0025/.android/debug.keystore /Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks/bilibili_v1.16.2_apkpure.com.apk

#  /Users/hhuu0025/Downloads/SDK/build-tools/31.0.0/apksigner sign --ks activityMining/apkSignedKey --ks-key-alias key0 --ks-pass pass:123456 --key-pass pass:123456 --v4-signing-enabled false  /Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks/youtube.apk

# /Users/hhuu0025/Downloads/SDK/build-tools/31.0.0/apksigner sign --ks /Users/hhuu0025/.android/debug.keystore --ks-pass pass:android --key-pass pass:android  /Users/h
# huu0025/PycharmProjects/uiautomator2/activityMining/re_apks/youtube.apk
def signApks(re_packaged_apks):
    for re_apk in os.listdir(re_packaged_apks):
        re_packaged_apk = os.path.join(re_packaged_apks, re_apk)
        print('sign ' + re_apk)
        cmd3 = '/Users/hhuu0025/Downloads/SDK/build-tools/31.0.0/apksigner sign --ks /Users/hhuu0025/.android/debug.keystore --ks-pass pass:android --key-pass pass:android ' + re_packaged_apk
        os.system(cmd3)


if __name__ == '__main__':
    re_packaged_apks = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/re_apks'
    # batchInject()
    signApks(re_packaged_apks)
import uiautomator2 as u2
from util import connectionAdaptor
import requests
import time


def launchActivity(device, package, activity):
    try:
        d = u2.connect(device)
    except requests.exceptions.ConnectionError:
        print('requests.exceptions.ConnectionError')
        return

    d.app_start(package, activity)
    print('sleep')
    time.sleep(5)
    # d.app_start(package)

# tips: need the full path of activity
#       convert shell to python
#       automatically sign and repackage apk

# adb shell am start -W -a android.intent.action.VIEW -d amazonprime://ParentalControlsSettings

if __name__ == '__main__':
    device = '192.168.56.101:5555'
    package = 'com_google_android_youtube'
    package = package.replace('_', '.')
    # activity = 'com.google.android.apps.youtube.app.watchwhile.WatchWhileActivity'
    activity = 'com.google.android.apps.youtube.app.settings.SettingsActivity'
    #activity = 'com.google.android.libraries.youtube.mdx.manualpairing.PairWithTvActivity'
    launchActivity(device, package, activity)

    device2 = '192.168.56.104:5555'
    launchActivity(device2, package, activity)
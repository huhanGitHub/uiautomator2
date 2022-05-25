from util import connectionAdaptor, getActivityPackage, xmlScreenSaver, safeScreenshot
import os


def screenCap():
    saveDir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/saveScreen'
    phoneDevice = '192.168.56.101'
    tabletDevice = '192.168.56.102'

    d1, d2, connectStatus = connectionAdaptor(phoneDevice, tabletDevice)
    while not connectStatus:
        d1, d2, connectStatus = connectionAdaptor(phoneDevice, tabletDevice)

    d1_activity, d1_package, d1_launcher = getActivityPackage(d1)
    d2_activity, d2_package, d2_launcher = getActivityPackage(d2)

    xml1 = d1.dump_hierarchy(compressed=True)
    xml2 = d2.dump_hierarchy(compressed=True)
    img1 = safeScreenshot(d1)
    img2 = safeScreenshot(d2)

    if not os.path.exists(saveDir):
        os.mkdir(saveDir)
    xmlScreenSaver(saveDir, xml1, xml2, img1, img2, d1_activity, d2_activity)


if __name__ == '__main__':
    screenCap()

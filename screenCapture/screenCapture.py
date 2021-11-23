import uiautomator2 as u2
from util import connectionAdaptor, getActivityPackage, xmlScreenSaver, safeScreenshot
import os


def screenCap():
    saveDir = r'save'
    phoneDevice = 'cb8c90f4'
    tabletDevice = 'R52RA0C2MFF'

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
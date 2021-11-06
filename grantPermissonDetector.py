import time

from util import *
import xml.etree.ElementTree as ET
from hierachySolver import *

grantPermissinActivityFieldList = ['grantpermissions', 'grantpermission']
textViewList = ['android.widget.TextView', 'android.widget.Button']
yesFields = ['allow', 'yes']
noFields = ['deny', 'no']
dialogField = ['ok', 'got it']

# com.android.packageinstaller.permission.ui.GrantPermissionsActivity deny allow
def grantPermissinActivityDetector(d):
    status = False
    d_activity, d_package, d_launcher = getActivityPackage(d)
    d_activity = str(d_activity).lower()
    for filed in grantPermissinActivityFieldList:
        if filed in d_activity:
            status = True
            break
    xml1 = d.dump_hierarchy(compressed=True)
    tree1 = ET.ElementTree(ET.fromstring(xml1))
    root1 = tree1.getroot()
    # find all textviews in two xml
    textViews = []
    for child in root1.iter():
        className = child.attrib.get('class', None)
        if className is None:
            continue
        if className in textViewList:
            textViews.append(child)

    yesStatus = False
    noStatus = False
    for textview in textViews:
        text = textview.attrib.get('text', None)
        text = text.lower()
        if text in yesFields:
            yesStatus = True
        elif text in noFields:
            noStatus = True

    if yesStatus and noStatus:
        status = True

    # check system dialog 'ok' in framelayout
    framelayoutList = ['android.widget.FrameLayout']
    framelayouts = []
    for child in root1.iter():
        className = child.attrib.get('class', None)
        if className is None:
            continue
        if className in framelayoutList:
            for widget in list(child):
                className = widget.attrib.get('class', None)
                if className is None:
                    continue
                if className in textViewList:
                    text = widget.attrib.get('text', None)
                    text = text.lower()
                    if text in dialogField:
                        bounds = widget.attrib.get('bounds')
                        bounds = bounds2int(bounds)
                        d.click((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2)
                        print('solve system dialog')
    return status


def grantPermissinActivityTasker(d):
    xml1 = d.dump_hierarchy(compressed=True)
    tree1 = ET.ElementTree(ET.fromstring(xml1))
    root1 = tree1.getroot()
    # find all textviews in two xml
    for child in root1.iter():
        className = child.attrib.get('class', None)
        if className is None:
            continue
        if className in textViewList:
            text = child.attrib.get('text', None)
            text = text.lower()
            if text in yesFields:
                bounds = child.attrib.get('bounds')
                bounds = bounds2int(bounds)
                if bounds[1] >= 200 and bounds[3] <= 1600:
                    d.click((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2)


def grantPermissinActivitySolver(d):
    while grantPermissinActivityDetector(d):
        grantPermissinActivityTasker(d)
        print('solve grant permission activity')
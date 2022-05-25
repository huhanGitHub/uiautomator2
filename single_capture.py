#!/usr/bin/env python3
import os
import time
import copy
import re
from typing import Union

from pyaxmlparser import APK
# import xml.etree as etree
from xml.etree import ElementTree
import uiautomator2 as u2

import definitions
from definitions import APK_DIR
from grantPermissonDetector import dialogSolver
# from util import getActivityPackage, installApk
from hierachySolver import bounds2int

TABLET = 'tablet'
PHONE = 'phone'
DEVICE_TYPE = list[Union[TABLET, PHONE]]
WAIT = 2  # second(s)


def getPackageByApk(apkPath):
    apkf = APK(apkPath)
    package = apkf.get_package()
    mainActivity = apkf.get_main_activity()
    return package, mainActivity


def xmlScreenSaver(saveDir, tabletActivity, tabletXml, tabletImg,
                   phoneActivity, phoneXml, phoneImg):
    if phoneImg is None or tabletImg is None:
        print('none img, save fail, return')
        return
    t = int(time.time())

    def getPath(device, filetype):
        act = phoneActivity if device == 'phone' else tabletActivity
        return os.path.join(saveDir, f"{t}_{device}_{act}.{filetype}")

    xml1Path = getPath('tablet', 'xml')
    img1Path = getPath('tablet', 'png')
    xml2Path = getPath('phone', 'xml')
    img2Path = getPath('phone', 'png')
    with open(xml1Path, 'a', encoding='utf8') as f1, open(
            xml2Path, 'a', encoding='utf8') as f2:
        f1.write(tabletXml)
        f2.write(phoneXml)
        tabletImg.save(img1Path)
        phoneImg.save(img2Path)


class Device(u2.Device):
    """
    Class for capture both phone and tablet UI data using only tablet device.

    Change density-independent pixels(dp)
    https://developer.android.com/training/multiscreen/screendensities
    """

    def __init__(self, *args):
        super().__init__(*args)
        super().settings['operation_delay'] = (0, 10)
        super().settings['operation_delay_methods'] = ['click', 'swipe', 'press']
        self.to_default()

    def to_default(self):
        # TODO disable animations, don't keep activities
        self.rotate("natural")
        self.font()
        self.to_tablet()

    def to_tablet(self):
        self.device_type = 'tablet'
        return self.res(1300, 800)

    def is_tablet(self):
        return self.info["displaySizeDpX"] == 1300

    def to_phone(self):
        self.device_type = 'phone'
        return self.res(400, 900)

    def is_phone(self):
        return self.info["displaySizeDpX"] == 400

    def font(self, scale=1.00):
        out, code = self.shell(f"settings put system font_scale {scale}")
        return self

    def res(self, w=None, h=None, reverse=False):
        """
        px = dp * (dpi / 160)
        NOTE: This is device dependent, sometimes w should be first, sometimes h should be first.
        TODO: no hard-coded sleep for wait activity change
        """
        if reverse:
            w, h = h, w
        if w is None and h is None:
            out, code = self.shell("wm size reset")
        else:
            out, code = self.shell(f"wm size {w}dpx{h}dp")
        time.sleep(WAIT)
        return self

    def rotate(self, dirt="natural"):
        """
        dirt=['left', 'right', 'natural', 'upsidedown']
        """
        self.set_orientation(dirt)
        self.shell("wm set-user-rotation free")
        return self

    def collect_one_activity(self):
        activity = self.app_current()['activity']
        xml = self.dump_hierarchy(compressed=True)
        img = self.screenshot()
        return activity, xml, img

    def change_device_type(self):
        if self.is_tablet():
            self.to_phone()
        elif self.is_phone():
            self.to_tablet()
        else:
            self.to_tablet()
        return self

    def collect_pair(self):
        """
        return: tablet data, phone data
        """
        pair = {}
        pair[self.device_type] = self.collect_one_activity()
        self.change_device_type()
        pair[self.device_type] = self.collect_one_activity()
        return *pair['tablet'], *pair['phone']

    def save(self, out_dir):
        # recording
        activity1 = self.app_current()['activity']
        xml1 = self.dump_hierarchy(False, True)
        img1 = self.screenshot()
        if self.is_tablet():
            self.to_phone()
            s1 = "tablet"
        else:
            self.to_tablet()
            s1 = "phone"
        activity2 = self.app_current()['activity']
        xml2 = self.dump_hierarchy(False, True)
        img2 = self.screenshot()

        # saving
        if s1 == "tablet":
            xmlScreenSaver(out_dir, xml2, xml1, img2, img1, activity2, activity1)
        else:
            xmlScreenSaver(out_dir, xml1, xml2, img1, img2, activity1, activity2)

    def install(self, apk_path):
        """
        Insatll all apk in path if is a directory
        else insatll and start if is a APK.
        """
        if os.path.isdir(apk_path):
            apk_paths = os.listdir(apk_path)
            apk_paths = map(lambda x: os.path.join(APK_DIR, x), apk_paths)
            apk_paths = [f for f in apk_paths if os.path.isfile(f)]
            for i in list(enumerate(apk_paths + ["exit"])):
                self.install(apk_paths[i])
        elif os.path.isfile(apk_path):
            # TODO: check is apk file
            self.app_install(apk_path)
            apk_name = APK(apk_path).get_package()
            self.app_start(apk_name)
        else:
            print("Is not a file or dir!")
            return

    def app_start_wait(self, package):
        self.app_start(package, wait=True)
        activity = self.app_info(package)['mainActivity']
        activity = f'.{activity}' if activity.find('.') == -1 else activity
        self.wait_activity(activity)
        return self


def is_attr_nq(attr_name, expect_value):
    def func(element):
        value = element.attrib.get(attr_name)
        return value is not None and value != expect_value
    return func


def is_attr_eq(attr_name, expect_value):
    def func(element: ElementTree.Element):
        value = element.attrib.get(attr_name)
        return value is not None and value == expect_value
    return func


def tree_to_list(tree: ElementTree):
    filter_sys_ui = is_attr_nq('package', 'com.android.systemui')

    tree.iter()
    elements = tree.findall('.//node')
    elements = filter(filter_sys_ui, elements)
    return elements


def clickable_bounds(tree: ElementTree):
    pass_clickable = is_attr_eq('clickable', 'true')
    elements = tree_to_list(tree)
    elements = filter(pass_clickable, elements)

    def to_bounds(element):
        return bounds2int(element.attrib.get('bounds'))
    bounds = map(to_bounds, elements)
    return bounds


def is_same_activity(xml1: str, xml2: str):
    bounds1 = re.findall(r'\[.*\]', xml1)
    bounds2 = re.findall(r'\[.*\]', xml2)
    count = 0
    for (a, b) in zip(bounds1, bounds2):
        if a == b:
            count += 1
    rate = count / len(bounds1)
    print(f'similar rate: {rate}')
    return rate > 0.75


# return value 0 success, 1 install fail, 2 no the same texts, 3 time out,
# 4 fail others, 5 no tablet adaption
# TODO: setting delay https://github.com/openatx/uiautomator2#global-settings
def uiExplorer(packageName, saveDir, device: Device):
    device.app_start_wait(packageName)

    info = device.app_info(packageName)
    activity = info['mainActivity']
    if activity.find(".") == -1:
        activity = "." + activity
    device.wait_activity(activity)
    dialogSolver(device)

    # save first pair
    t_act, t_xml, t_img, p_act, p_xml, p_img = device.collect_pair()
    device.to_tablet()
    subSaveDir = os.path.join(saveDir, packageName)
    if not os.path.exists(subSaveDir):
        os.mkdir(subSaveDir)
    print('save first pair')
    xmlScreenSaver(subSaveDir, t_act, t_xml, t_img, p_act, p_xml, p_img)

    t_tree = ElementTree.fromstring(t_xml)
    last_xml = copy.deepcopy(t_xml)
    bounds = clickable_bounds(t_tree)
    # reset and
    for bound in bounds:
        click_stack = []
        # click the same text in two screens
        (x1, y1, x2, y2) = bound
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        print(f'click: {x},{y}')
        device.click(x, y)
        # device.long_click(x, y, 3)
        click_stack.append((x, y))

        t_act, t_xml, t_img, p_act, p_xml, p_img = device.collect_pair()
        device.to_tablet()
        print('save a pair')
        xmlScreenSaver(subSaveDir, t_act, t_xml, t_img, p_act, p_xml, p_img)

        print('go back')
        device.press('back')
        # check if is in orignal activity
        # automative pop-ups (e.g. virtual keyboard) can cause such behaviour
        i = 0
        while not is_same_activity(last_xml, device.dump_hierarchy(compressed=True)):
            print(f'go back {i+2}th time')
            device.press('back')
            # if go back not work, restart
            if i == 1:
                print('recovering')
                # NOTE: not work if start exploring from MainActivity
                device.app_start_wait(packageName)
                last_xml = device.dump_hierarchy(compressed=True)

                click_stack.pop()
                for p in click_stack:
                    device.click(*p)
                print('recovering done')
                break
            i += 1
        print()

#         # swipe forward to collect more data
#         d1.swipe_ext(Direction.FORWARD)
#         d2.swipe_ext(Direction.FORWARD)
#         xml11 = d1.dump_hierarchy(compressed=True)
#         xml22 = d2.dump_hierarchy(compressed=True)
#         img11 = safeScreenshot(d1)
#         img22 = safeScreenshot(d2)
#         xmlScreenSaver(subSaveDir, xml11, xml22, img11, img22, d1_activity, d2_activity)
#         d1.swipe_ext(Direction.BACKWARD)
#         d2.swipe_ext(Direction.BACKWARD)

#         # back to the original page
#         d1.press('back')
#         d2.press('back')
#         print('back...')

#         dialogSolver(d1)
#         dialogSolver(d2)

#         d1.app_start(packageName, use_monkey=True)
#         d2.app_start(packageName, use_monkey=True)

#         dialogSolver(d1)
#         dialogSolver(d2)

#         d1.sleep(switchSleepTime)
#         d2.sleep(switchSleepTime)

#     # swipe forward to collect more data
#     d1.swipe_ext(Direction.FORWARD)
#     d2.swipe_ext(Direction.FORWARD)
#     xmla = d1.dump_hierarchy(compressed=True)
#     xmlb = d2.dump_hierarchy(compressed=True)
#     imga = safeScreenshot(d1)
#     imgb = safeScreenshot(d2)
#     xmlScreenSaver(subSaveDir, xmla, xmlb, imga, imgb, d1_activity, d2_activity)

#     clickBounds2 = hierachySolver(xmla, xmlb)
#     if clickBounds2 is None:
#         return 0
#     for i in clickBounds2:
#         if i in clickBounds1:
#             continue
#         # click the same text in two screens
#         bounds1 = i[0]
#         bounds2 = i[1]
#         print('click: ' + str(i[-1]))
#         d1.click((bounds1[0] + bounds1[2]) / 2, (bounds1[1] + bounds1[3]) / 2)
#         d2.click((bounds2[0] + bounds2[2]) / 2, (bounds2[1] + bounds2[3]) / 2)
#         d1.sleep(3)
#         d2.sleep(3)
#         xml11 = d1.dump_hierarchy(compressed=True)
#         xml22 = d2.dump_hierarchy(compressed=True)
#         img11 = d1.screenshot()
#         img22 = d2.screenshot()
#         xmlScreenSaver(subSaveDir, xml11, xml22, img11, img22, d1_activity, d2_activity)

#         # swipe forward to collect more data
#         d1.swipe_ext(Direction.FORWARD)
#         d2.swipe_ext(Direction.FORWARD)
#         xml11 = d1.dump_hierarchy(compressed=True)
#         xml22 = d2.dump_hierarchy(compressed=True)
#         img11 = d1.screenshot()
#         img22 = d2.screenshot()
#         xmlScreenSaver(subSaveDir, xml11, xml22, img11, img22, d1_activity, d2_activity)
#         d1.swipe_ext(Direction.BACKWARD)
#         d2.swipe_ext(Direction.BACKWARD)

#         dialogSolver(d1)
#         dialogSolver(d2)

#         # back to the original page
#         d1.press('back')
#         d2.press('back')
#         print('back...')
#         d1.app_start(packageName, use_monkey=True)
#         d2.app_start(packageName, use_monkey=True)
#         d1.sleep(3)
#         d2.sleep(3)

#     # d1.swipe_ext(Direction.BACKWARD)
#     # d2.swipe_ext(Direction.BACKWARD)
#     d1.app_stop(packageName)
#     d2.app_stop(packageName)
#     print('uninstall ' + packageName)
#     d1.app_uninstall(packageName)
#     d2.app_uninstall(packageName)
#     return 0


def interactive():
    # tablet = Device(definitions.TABLET_ID)
    tablet = Device(definitions.VM_ID)

    def install():
        apk_paths = sorted(os.listdir(definitions.APK_DIR))
        apk_paths = map(lambda x: os.path.join(APK_DIR, x), apk_paths)
        apk_paths = [f for f in apk_paths if os.path.isfile(f)]

        l = len(apk_paths)
        for i in list(enumerate(apk_paths + ["exit"])):
            print(i)
        i = int(input("Enter a index: "))
        if i == l:
            return
        else:
            tablet.install(apk_paths[i])

    def screenshots():
        t = str(int(time.time()))
        out_dir = os.path.join(definitions.OUT_DIR, t)
        tablet.save(out_dir)

    def cur():
        print(str(tablet.app_current()) + "\n")

    def nothing():
        pass

    d = {
        "refresh": nothing,
        "screenshot": screenshots,
        "install": install,
        "current": cur,
    }

    while True:
        cmds = list(d)
        for i in list(enumerate(cmds)):
            print(i)
        i = int(input("Enter a index: "))
        d[cmds[i]]()


def interactive_launch_activities():
    # https://weiwangqiang.github.io/2020/03/16/dumpsys-debug-detail/#2dumpsys-activity
    tablet = Device(definitions.VM_ID)
    apps = tablet.app_list('-3')
    # get all activities
    while True:
        for i in list(enumerate(apps)):
            print(i)
        i = int(input("Enter a index: "))
        output, code = tablet.shell(f"dumpsys package {apps[i]} | grep Activity")
        activities = list(set(re.findall(r'(?<=\/)[\S]+', output)))

        while True:
            for j in list(enumerate(activities)):
                print(j)
            j = int(input("Enter a index: "))
            tablet.app_start(apps[i], activities[j])


def main():
    tablet = Device(definitions.VM_ID)
    # print(tablet.settings)
    # tablet.implicitly_wait()
    # tablet.click(2438.0, 96.0)
    # tablet(text='Continue').click()
    package = 'com.google.android.youtube'
    # package = 'com.adobe.lrmobile'
    uiExplorer(package, definitions.OUT_DIR, tablet)


if __name__ == "__main__":
    main()
    # interactive()
    # interactive_launch_activities()

"""
problems:
1. Go back
   1. check if go back properly
2. uiautomator may crash
"""

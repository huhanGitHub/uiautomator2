import xml.etree.ElementTree as ET

viewList = ['android.widget.TextView', 'android.widget.ImageView', 'android.widget.Button']
removeView = ['']
textViewList = ['android.widget.TextView']


def nodeCompare(node1, node2):
    text1 = node1.attrib.get('text', None)
    text2 = node2.attrib.get('text', None)
    resourceId1 = node1.attrib.get('resourceId', None)
    resourceId2 = node2.attrib.get('resourceId', None)
    description1 = node1.attrib.get('description', None)
    description2 = node2.attrib.get('description', None)

    count = 0
    if text1 == text2:
        count += 1
    if resourceId1 == resourceId2:
        count += 1
    if description1 == description2:
        count += 1

    if count >= 2:
        return True
    else:
        return False


def pairTextview(phoneViews, tabletViews):
    pairs = []
    for textview1 in phoneViews:
        text1 = textview1.attrib.get('text', None)
        for textview2 in tabletViews:
            text2 = textview2.attrib.get('text', None)
            if text1 == text2:
                pair = [textview1, textview2, text1]
                pairs.append(pair)
                break

    if len(pairs) <= 0:
        return None, None, None

    # select possible top tablayout texts according to Y axis less than 200
    top = []
    # select possible bottom navigation texts according to the Y axis more than 1700
    bottom = []
    middle = []
    for i in pairs:
        view = i[0]
        bounds = view.attrib.get('bounds')
        bounds = bounds2int(bounds)
        bounds2 = bounds2int(i[1].attrib.get('bounds'))
        y1 = bounds[1]
        y2 = bounds[3]
        if y2 < 200:
            top.append([bounds, bounds2, i[-1]])
            continue
        elif y1 > 1700:
            bottom.append([bounds, bounds2, i[-1]])
            continue

        middle.append([bounds, bounds2, i[-1]])

    return top, bottom, middle


def bounds2int(bounds):
    bounds = bounds.replace('][', ',')
    bounds = bounds[1:-1]
    bounds = [int(i) for i in bounds.split(',')]
    return bounds


def hierachySolver(xml1, xml2):
    tree1 = ET.ElementTree(ET.fromstring(xml1))
    root1 = tree1.getroot()

    tree2 = ET.ElementTree(ET.fromstring(xml2))
    root2 = tree2.getroot()

    # find all textviews in two xml
    phoneViews = []
    tabletViews = []
    for child in root1.iter():
        className = child.attrib.get('class', None)
        if className is None:
            continue
        if className in textViewList:
            phoneViews.append(child)

    for child in root2.iter():
        className = child.attrib.get('class', None)
        if className is None:
            continue
        if className in textViewList:
            tabletViews.append(child)

    if len(phoneViews) <= 0:
        return False

    top, bottom, middle = pairTextview(phoneViews, tabletViews)
    if top is None and bottom is None and middle is None:
        return None

    clickBounds = []
    if len(top) != 0:
        clickBounds.extend(top)
    if len(bottom) != 0:
        clickBounds.extend(bottom)
    if len(middle) != 0:
        clickBounds.extend(middle)

    return clickBounds
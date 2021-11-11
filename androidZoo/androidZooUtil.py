import os
import csv
import time
import datetime


def time_cmp_bigger(first_time, second_time):
    first_time = datetime.datetime.strptime(first_time, '%Y-%m-%d %H:%M:%S')
    second_time = datetime.datetime.strptime(second_time, '%Y-%m-%d %H:%M:%S')
    return second_time > first_time



# https://androzoo.uni.lu/api/download?apikey=27787e752bcb4d015a9c2fe6fdaf0ef54a628ff16af1f19ef15ffc7fd0664fbc&sha256=0000003B455A6C7AF837EF90F2EAFFD856E3B5CF49F5E27191430328DE2FA670
# curl -O --remote-header-name -G -d apikey=27787e752bcb4d015a9c2fe6fdaf0ef54a628ff16af1f19ef15ffc7fd0664fbc -d sha256=0000003B455A6C7AF837EF90F2EAFFD856E3B5CF49F5E27191430328DE2FA670 \ https://androzoo.uni.lu/api/download

def findSha256(packagenames, shaFilePath = r'/Users/hhuu0025/PycharmProjects/uiautomator2/androidZoo/latest.csv'):
    packagenameDic = {}
    for i in packagenames:
        packagenameDic[i] = None

    with open(shaFilePath) as f:
        shas = csv.reader(f)
        headers = next(shas)
        for row in shas:
            rowPackge = row[5]
            if rowPackge in packagenames:
                # print(row)
                sha256 = row[0]
                rowTime = row[8]
                if sha256 == '' or rowTime == '':
                    continue
                # print(sha256)
                attr = packagenameDic.get(rowPackge)
                if attr is None:
                    packagenameDic[rowPackge] = [sha256, rowTime]
                else:
                    if time_cmp_bigger(attr[1], rowTime):
                        packagenameDic[rowPackge] = [sha256, rowTime]
                # if len(packagenames) == 0:
                #     break

    print(packagenameDic)
    return packagenameDic


if __name__ == '__main__':
    #packages = ['com.kuxun.scliang.plane', 'cfyazilim.com.cf_mobile', 'com.zte.bamachaye']
    packages = ['com.google.android.youtube']
    findSha256(packages)
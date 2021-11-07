import glob
import re
import subprocess
import os
import time
from apkizer import apkpureDownloader
saveDir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks'


if __name__ == '__main__':
	for path in glob.glob("jsons/*json"):
		f = open(path, 'r')
		cat=path.split("/")[1].split(".")[0]
		content = f.read()
		ids=re.findall(r"appId: '(.*?)',", content)
		index = 0
		print(path + ': ' + str(len(ids)))
		for id in ids:
			# google has updated the
			# os.system("pipenv run python ../PlaystoreDownloader/playstoredownloader/downloader/download.py \""+id +"\" -t \""+cat+"\"")

			# use apkpure to replace
			apkpureDownloader(cat, id, saveDir)
			time.sleep(5)
			index += 1
			print(id + ' ' + str(index) + '/' + str(len(ids)))
		f.close()



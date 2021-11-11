import requests
import bs4
import argparse
from requests.models import Response
import cloudscraper
import os
import timeout_decorator

collectExtentions = ['APK']


@timeout_decorator.timeout(300, timeout_exception=StopIteration)
def apkpureDownloader(cat, package_name, saveDir):
    # parser = argparse.ArgumentParser(description='Download all versions of an Android mobile application from apkpure.com')
    # required = parser.add_argument_group('required arguments')
    # required.add_argument('-p', required=True, metavar="packagename", help="example: com.twitter.android")
    # args = parser.parse_args()

    if not os.path.exists(saveDir):
        os.mkdir(saveDir)
    catDir = os.path.join(saveDir, cat)
    if not os.path.exists(catDir):
        os.mkdir(catDir)
    scraper = cloudscraper.create_scraper(delay=1000,
                                          browser='chrome'
                                          )

    base_url = "https://apkpure.com"
    # package_name = args.p
    package_url = ""
    download_version_list = []
    session = requests.session()
    response = scraper.get("https://apkpure.com/search?q=" + package_name).text
    # response = session.get("https://apkpure.com/tr/search?q=" + package_name).text
    # cfresponse = cfscraper.get("https://apkpure.com/tr/search?q=" + package_name).text
    soup = bs4.BeautifulSoup(response, "html.parser")
    a_elements = soup.find_all("a")

    for element in a_elements:
        # print(element.attrs["href"])
        if "href" in element.attrs and element.attrs["href"] != None and package_name in element.attrs["href"]:
            if "/" in element.attrs["href"] and element.attrs["href"].split("/")[-1] == package_name:
                package_url = element.attrs["href"]

    if package_url == "":
        if "Cloudflare Ray ID" in response:
            print("Cloudflare protection could not be bypassed, trying again..")
            apkpureDownloader(cat, package_name, saveDir)
        else:
            print("Package not found!")
        return

    """
    Here is full URL correlated with package name.
    """
    # here, click versions button not 'download apk' to see all app versions to find the suitable apk version.

    try:
        response = scraper.get(base_url + package_url + "/versions").text
        soup = bs4.BeautifulSoup(response, "html.parser")

        versions_elements_div = soup.find("ul", attrs={"class": "ver-wrap"})
        versions_elements_li = versions_elements_div.findAll("li", recursive=False)
    except Exception:
        print('raise exception when parse available apks, skip')
        return

    for list_item in versions_elements_li:
        # find suitable url
        apkTag = list_item.find("span", attrs={"class": "ver-item-t ver-apk"})
        if apkTag is None:
            continue

        tag = apkTag.text
        if tag in collectExtentions:
            url = list_item.find("a").attrs["href"]
            download_version_list.append(url)
            # only collect latest apk file
            break
    """
    Make a list of download pages.
    """

    def download_apk(download_page):
        try:
            soup = bs4.BeautifulSoup(download_page, "html.parser")
            download_link = soup.find("iframe", {"id": "iframe_download"}).attrs["src"]
            filename = soup.find("span", {"class": "file"}).text.rsplit(' ', 2)[0].replace(" ", "_").lower()
            print(filename + " is downloading, please wait..")
            file = scraper.get(download_link)
        except Exception:
            print('raise exception when download apk, skip')
            return

        # current_directory = os.getcwd()
        final_directory = os.path.join(catDir, package_name)
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
        savePath = os.path.join(final_directory, filename)
        if os.path.exists(savePath):
            print(filename + 'has been downloaded, skip.')
        else:
            open(savePath, "wb").write(file.content)

    for apk_url in download_version_list:
        download_page = scraper.get(base_url + apk_url).text
        if "Download Variant" in download_page:
            """
            There are sometimes APK variants in terms of architecture,
            we need to analyze it before getting download link.
            Getting first variant for now.
            """
            soup = bs4.BeautifulSoup(download_page, "html.parser")
            apk_url = soup.find("div", {"class": "table-cell down"}).find("a").attrs["href"]
            download_page = scraper.get(base_url + apk_url).text
        download_apk(download_page)
    print("All APK's are downloaded!")


if __name__ == '__main__':
    cat = 'network'
    package_name = 'com.twitter.android'
    saveDir = r'/Users/hhuu0025/PycharmProjects/uiautomator2/googleplay/apks'
    apkpureDownloader(cat, package_name, saveDir)

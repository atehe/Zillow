from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector
from csv import writer
import time, logging, sys, os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import pandas as pd
from scrapy.selector import Selector
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from concurrent.futures import ThreadPoolExecutor

# from random import

logging.basicConfig(level=logging.INFO)
DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"

# if __name__ == "__main__":


def click(element, driver):
    """Use javascript click if selenium click method fails"""
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)
    time.sleep(1.5)


options = Options()
# options.add_argument("--headless")
# options.add_argument(
#     f"user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36"
# )
# options.add_argument("--window-size=1920,1080")
# options.add_argument("--ignore-certificate-errors")
# options.add_argument("--allow-running-insecure-content")

service = Service(DRIVER_EXECUTABLE_PATH)
# driver = webdriver.Chrome(service=service, options=options)
driver = uc.Chrome(version_main=100, options=options)

# driver.get(
#     "https://www.zillow.com/jacksonville-fl/with-pool/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22Jacksonville%2C%20FL%22%2C%22mapBounds%22%3A%7B%22west%22%3A-82.43945654003906%2C%22east%22%3A-80.93844945996094%2C%22south%22%3A29.859958036203615%2C%22north%22%3A30.823497100921227%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A25290%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22pool%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%7D"
# )

# time.sleep(10)


def scroll_to_element(driver, house_element):
    action = ActionChains(driver)
    action.move_to_element(to_element=house_element)
    action.perform()


def parse_page(driver):
    house_elements = driver.find_elements(
        by=By.XPATH, value="//ul[contains(@class,'photo-cards_extra-attribution')]/li"
    )

    with open("house.csv", "a") as csv_file:
        csv_writer = writer(csv_file)
        if os.stat("house.csv").st_size == 0:
            csv_writer.writerow(("house_url", "address", "features", "price", "status"))
        response = Selector(text=driver.page_source.encode("utf8"))

        houses = response.xpath(
            "//ul[contains(@class,'photo-cards_extra-attribution')]/li"
        )

        for i, house in enumerate(houses):

            house_url = house.xpath(".//div[@class='list-card-info']/a/@href").get()
            address = house.xpath(
                ".//div[@class='list-card-info']/a/address/text()"
            ).get()
            price = house.xpath(".//div[@class='list-card-price']/text()").get()
            features = " ".join(
                house.xpath(".//ul[@class='list-card-details']/li//text()").getall()[
                    :-1
                ]
            )
            status = house.xpath(".//li[@class='list-card-statusText']/text()").get()

            if status:
                status = status.replace("-", "").strip()

            csv_writer.writerow((house_url, address, features, price, status))

            if i % 10 == 0:
                print("Slow_scroll")
                houses = response.xpath(
                    "//ul[contains(@class,'photo-cards_extra-attribution')]/li"
                )
                time.sleep(2)
                scroll_to_element(driver, house_elements[i])


# def scrape_zillow(zillow_url):
# while next:
# parse_page
# write to file
# click next


def navigate_pages(driver):

    next_page = driver.find_element(
        by=By.XPATH, value='//a[@title="Next page" and not(@disabled)]'
    )
    time.sleep(2)
    while next_page:
        # time.sleep(10)
        parse_page(driver)
        scroll_to_element(driver, next_page)
        click(next_page, driver)


def scrape_zillow(url):
    driver.get(url)

    navigate_pages(driver)


scrape_zillow(
    "https://www.zillow.com/jacksonville-fl/sold/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22Jacksonville%2C%20FL%22%2C%22mapBounds%22%3A%7B%22west%22%3A-81.78407294253334%2C%22east%22%3A-81.63816077212319%2C%22south%22%3A30.364398935551083%2C%22north%22%3A30.46210543991083%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A25290%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22pool%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A13%7D"
)
# def browse(url):
#     driver.get(url)
#     time.sleep(10)


# url_list = [
#     "https://www.zillow.com/homes/recently_sold/?searchQueryState=%7B%22usersSearchTerm%22%3A%22Jacksonville%2C%20FL%22%2C%22mapBounds%22%3A%7B%22west%22%3A-81.67966891516824%2C%22east%22%3A-81.27798129309792%2C%22south%22%3A30.07579154473679%2C%22north%22%3A30.294510776572167%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22pool%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%2C%22customRegionId%22%3A%221fd7762b9cX1-CRx4bwcau6j5ha_yor6e%22%7D",
#     "https://www.zillow.com/homes/recently_sold/?searchQueryState=%7B%22usersSearchTerm%22%3A%22Jacksonville%2C%20FL%22%2C%22mapBounds%22%3A%7B%22west%22%3A-81.67966891516824%2C%22east%22%3A-81.27798129309792%2C%22south%22%3A30.07579154473679%2C%22north%22%3A30.294510776572167%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22pool%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%2C%22customRegionId%22%3A%221fd7a62b9cX1-CRx4aigcxfnloe_yor6e%22%7D",
#     "https://www.zillow.com/homes/recently_sold/?searchQueryState=%7B%22mapBounds%22%3A%7B%22west%22%3A-81.68046527038125%2C%22east%22%3A-81.27877764831094%2C%22south%22%3A30.092142914808193%2C%22north%22%3A30.310825870774146%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22pool%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%2C%22customRegionId%22%3A%221fd8462b9cX1-CRx4bwcau5y2ym_yor6e%22%7D",
#     "https://www.zillow.com/homes/recently_sold/?searchQueryState=%7B%22mapBounds%22%3A%7B%22west%22%3A-81.68115191588906%2C%22east%22%3A-81.27946429381875%2C%22south%22%3A30.125109940858056%2C%22north%22%3A30.343719704790505%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22pool%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%2C%22customRegionId%22%3A%221fd8d62b9cX1-CRx4bwcau5v3i6_yor6e%22%7D",
#     "https://www.zillow.com/homes/recently_sold/?searchQueryState=%7B%22mapBounds%22%3A%7B%22west%22%3A-81.68115191588906%2C%22east%22%3A-81.27946429381875%2C%22south%22%3A30.125109940858056%2C%22north%22%3A30.343719704790505%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22pool%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%2C%22customRegionId%22%3A%221fd9062b9cX1-CRx4bwcau6bybi_yor6e%22%7D",
# ]
# with ThreadPoolExecutor(max_workers=3) as executor:
#     for _ in executor.map(browse, url_list):
#         pass


# scrape_zillow( "https://www.zillow.com/homes/recently_sold/?searchQueryState=%7B%22usersSearchTerm%22%3A%22Jacksonville%2C%20FL%22%2C%22mapBounds%22%3A%7B%22west%22%3A-81.67966891516824%2C%22east%22%3A-81.27798129309792%2C%22south%22%3A30.07579154473679%2C%22north%22%3A30.294510776572167%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22pool%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%2C%22customRegionId%22%3A%221fd7762b9cX1-CRx4bwcau6j5ha_yor6e%22%7D")

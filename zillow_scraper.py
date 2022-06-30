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


logging.basicConfig(level=logging.INFO)
DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"

service = Service(DRIVER_EXECUTABLE_PATH)

API_KEY = "3bd81392dadcc3f492720c4cbebd6a4f"

options = Options()
options.add_argument("--user-data-dir=/home/atehe/.config/google-chrome")
options.add_argument("--profile-directory=Profile 3")  # Path to your chrome profile

# proxy_options = {
#     "proxy": {
#         "http": f"http://scraperapi:{API_KEY}@proxy-server.scraperapi.com:8001",
#         "no_proxy": "localhost,127.0.0.1",
#     }
# }
# seleniumwire_options=proxy_options
driver = webdriver.Chrome(service=service, options=options)


def click(element, driver):
    """Use javascript click if selenium click method fails"""
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)
    time.sleep(1.5)


def scroll_to_element(driver, house_element):
    action = ActionChains(driver)
    action.move_to_element(to_element=house_element)
    action.perform()
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def load_all_elements(driver):
    print("loading")
    house_elements = driver.find_elements(
        by=By.XPATH, value="//ul[contains(@class,'photo-cards')]/li"
    )
    for i in range(40):

        try:
            scroll_to_element(driver, house_elements[i])
            if i % 5 == 0:
                time.sleep(0.2)
                print("scrolling...")
            house_elements = driver.find_elements(
                by=By.XPATH,
                value="//ul[contains(@class,'photo-cards')]/li",
            )
            print(len(house_elements))
        except Exception as e:
            print(e)
            print(i)
            break


def parse_page(driver):

    # load_all_elements(driver)
    print("loading all")
    time.sleep(3)

    with open("house.csv", "a") as csv_file:
        csv_writer = writer(csv_file)
        if os.stat("house.csv").st_size == 0:
            csv_writer.writerow(("house_url", "address", "features", "price"))
        response = Selector(text=driver.page_source.encode("utf8"))

        houses = response.xpath("//ul[contains(@class,'photo-cards')]/li")

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

            csv_writer.writerow((house_url, address, features, price))


def navigate_pages(driver):

    try:
        next_page = driver.find_element(
            by=By.XPATH, value='//a[@title="Next page" and not(@tabindex=-1)]'
        )
    except:
        next_page = None

    while next_page:
        print("click next_page")
        time.sleep(3)

        # scroll_to_element(driver, next_page)
        # click(next_page, driver)
        parse_page(driver)


def scrape_zillow(url):
    driver.get(url)
    parse_page(driver)
    navigate_pages(driver)


zillow_sold_url = 'https://www.zillow.com/jacksonville-fl-postal_code/sold/?searchQueryState={"pagination":{},"usersSearchTerm":"postal_code","mapZoom":12,"isMapVisible":true,"filterState":{"pool":{"value":true},"sort":{"value":"globalrelevanceex"},"rs":{"value":true},"fsba":{"value":false},"fsbo":{"value":false},"nc":{"value":false},"cmsn":{"value":false},"auc":{"value":false},"fore":{"value":false}},"isListVisible":true}'

url = zillow_sold_url.replace("postal_code", "32218")
scrape_zillow(url)

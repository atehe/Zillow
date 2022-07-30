from urllib.parse import urlencode
import requests, json
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
from selenium.webdriver.common.keys import Keys

DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"


def generate_api_url(page_num, for_sale=True):
    # API parameter <searchQueryState>
    search_query = {
        "pagination": {"currentPage": page_num},
        "usersSearchTerm": "Jacksonville, FL",
        "mapBounds": {
            "west": -82.8919559296875,
            "east": -80.4859500703125,
            "south": 29.090635517057596,
            "north": 31.57937245240447,
        },
        "regionSelection": [{"regionId": 25290, "regionType": 6}],
        "isMapVisible": True,
        "filterState": {
            "isAllHomes": {"value": True},
            "hasPool": {"value": True},
            "sortSelection": {"value": "globalrelevanceex"},
        },
        "isListVisible": True,
        "mapZoom": 9,
    }

    # API parameter <wants>
    wants = {
        "cat1": ["listResults", "mapResults"],
        "cat2": ["total"],
        "regionResults": ["total"],
    }

    params = {"searchQueryState": search_query, "wants": wants}
    encoded_params = urlencode(params)

    api_url = f"https://www.zillow.com/search/GetSearchPageState.htm?{encoded_params}"
    return api_url


def parse_api(api_json):
    search_result = api_json.get("cat1", {}).get("searchResults", {})

    listings = search_result.get("listResults", [])

    parsed_data = []
    for listing in listings:
        id = listing.get("id")
        street_address = listing.get("addressStreet")
        zip_code = listing.get("addressZipcode")
        city = listing.get("addressCity")
        state = listing.get("addressState")
        parsed_data.append(",".join((id, street_address, zip_code, city, state)))
    return parsed_data


def scrape_zillow(for_sale=True, filename="zillow.csv"):

    # create browser
    service = Service(DRIVER_EXECUTABLE_PATH)
    driver = webdriver.Chrome(
        service=service,
    )

    page = 1
    while True:
        if page == 6:
            break
        print(f">>> Parsing page {page}")
        api_url = generate_api_url(page)
        driver.get(api_url)
        api_response = json.loads(driver.find_element_by_tag_name("body").text)
        parsed_data = parse_api(api_response)

        with open(filename, "a") as file:
            file.write("\n".join(parsed_data))
            file.write("\n")

        page += 1

    driver.quit()


scrape_zillow()


#
# semd request
# parse response
# check date limit

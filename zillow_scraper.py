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
from datetime import date

DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"
options = Options()
options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--allow-running-insecure-content")


def generate_api_url(page_num, on_sale):
    # API parameter <searchQueryState>
    if on_sale:
        filter_state = {
            "isAllHomes": {"value": True},
            "hasPool": {"value": True},
            "sortSelection": {"value": "globalrelevanceex"},
        }
    else:
        filter_state = {
            "sort": {"value": "globalrelevanceex"},
            "ah": {"value": True},
            "pool": {"value": True},
            "rs": {"value": True},
            "fsba": {"value": False},
            "fsbo": {"value": False},
            "nc": {"value": False},
            "cmsn": {"value": False},
            "auc": {"value": False},
            "fore": {"value": False},
        }
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
        "filterState": filter_state,
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


def parse_api(api_json, on_sale):
    search_result = api_json.get("cat1", {}).get("searchResults", {})

    listings = search_result.get("listResults", [])
    end = False

    parsed_data = []
    for listing in listings:
        street_address = listing.get("addressStreet")
        zip_code = listing.get("addressZipcode")
        city = listing.get("addressCity")
        state = listing.get("addressState")

        if not on_sale:
            date_data = (
                listing.get("variableData", {})
                .get("text", "")
                .replace("Sold", "")
                .strip()
            )

            month = date_data.split("/")[0]
            if int(month) == date.today().month - 2:
                end = True

        parsed_data.append(",".join((street_address, zip_code, city, state)))

    return parsed_data, end


def scrape_zillow(on_sale=True):
    month = date.today().month
    if on_sale:
        filename = f"zillow_onsale_{month}.csv"
        page_limit = 8
    else:
        filename = f"zillow_sold_{month}.csv"
        page_limit = 20

    # create browser
    service = Service(DRIVER_EXECUTABLE_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    page = 1
    while True:
        print(f">>> Parsing page {page}")
        api_url = generate_api_url(page, on_sale)
        driver.get(
            api_url,
        )
        api_response = json.loads(driver.find_element(by=By.XPATH, value="//body").text)
        parsed_data, end = parse_api(api_response, on_sale)

        # write data to csv
        write_headers = not os.path.exists(filename)
        with open(filename, "a") as file:
            if write_headers:
                file.write(",".join(("street_address", "zip_code", "city", "state")))
                file.write("\n")

            file.write("\n".join(parsed_data))
            file.write("\n")

        if page >= page_limit or end:
            break

        page += 1

    df = pd.read_csv(filename)
    df.drop_duplicates(inplace=True, keep="first")
    df.to_csv(filename, index=None)

    driver.quit()


if __name__ == "__main__":
    # scrape_zillow(False)
    # scrape_zillow()

    response = requests.get("https://www.lowes.com/c/Appliances")
    with open("ANS.html", "a") as html_file:
        html_file.write(str(response.text))

    print(response.status_code)

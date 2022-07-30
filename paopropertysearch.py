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


from selenium.webdriver.support.ui import Select


logging.basicConfig(level=logging.INFO)
DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"


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
driver = webdriver.Chrome(service=service, options=options)


def fill_n_search(
    street_num="", street_name="", zip_code="", direction="", city="Jacksonville"
):
    driver.get("https://paopropertysearch.coj.net/Basic/Search.aspx")

    street_number_input = driver.find_element(
        by=By.XPATH, value='//input[contains(@id,"StreetNumber")]'
    )
    street_number_input.clear()
    street_number_input.send_keys(street_num)

    street_name_input = driver.find_element(
        by=By.XPATH, value='//input[contains(@id,"StreetName")]'
    )
    street_name_input.clear()
    street_name_input.send_keys(street_name)

    city_drop_down = Select(
        driver.find_element(by=By.XPATH, value='//select[contains(@id,"City")]')
    )
    city_drop_down.select_by_value(city)

    result_down = Select(
        driver.find_element(
            by=By.XPATH, value='//select[contains(@id,"ResultsPerPage")]'
        )
    )
    result_down.select_by_value("10000")

    street_direction = Select(
        driver.find_element(by=By.XPATH, value='//select[contains(@id,"Prefix")]')
    )

    street_direction.select_by_value(direction.strip().upper())
    zip_code_input = driver.find_element(
        by=By.XPATH, value='//input[contains(@id,"ZipCode")]'
    )

    zip_code_input.clear()
    zip_code_input.send_keys(zip_code)
    zip_code_input.send_keys(Keys.RETURN)


def parse_result(
    driver, output_csv, main_page, street_num, street_name, zip_code, error_file
):

    with open(output_csv, "a") as csv_file:
        csv_writer = writer(csv_file)
        headers = (
            "Real Estate Number",
            "Property URL",
            "Name",
            "Street Number",
            "Street Name",
            "Type",
            "Direction",
            "Unit",
            "City",
            "Zip",
        )

        print("switching")
        driver.switch_to.window(main_page)

        page_response = Selector(text=driver.page_source.encode("utf8"))

        table_rows = page_response.xpath('//table[contains(@id,"gridResults")]//tr')
        if len(table_rows) > 25:

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        no_result = page_response.xpath('//div[@id="noResults"]')
        if no_result:
            print("Found no owner information")
            error_file.write(" ".join((str(street_num), street_name, str(zip_code))))
            error_file.write("\n")

        for row in table_rows:
            RE_number = row.xpath("./td[1]//text()").get()
            RE_url = row.xpath("./td[1]//a/@href").get()
            if RE_url:
                RE_url = f"https://paopropertysearch.coj.net/{RE_url}"
            name = row.xpath("./td[2]//text()").get()
            street_num = row.xpath("./td[3]//text()").get()
            street_name = row.xpath("./td[4]//text()").get()
            type = row.xpath("./td[5]//text()").get()
            direction = row.xpath("./td[6]//text()").get()
            unit = row.xpath("./td[7]//text()").get()
            city = row.xpath("./td[8]//text()").get()
            zip = row.xpath("./td[9]//text()").get()

            csv_writer.writerow(
                (
                    RE_number,
                    RE_url,
                    name,
                    street_num,
                    street_name,
                    type,
                    direction,
                    unit,
                    city,
                    zip,
                )
            )


def get_property_info(
    output_csv,
    error_file,
    street_num="",
    street_name="",
    zip_code="",
    direction="",
    city="Jacksonville",
):
    # service = Service(DRIVER_EXECUTABLE_PATH)
    # driver = webdriver.Chrome(service=service, options=options)
    main_page = driver.current_window_handle
    print(main_page)

    fill_n_search(street_num, street_name, zip_code, direction)
    parse_result(
        driver, output_csv, main_page, street_num, street_name, zip_code, error_file
    )


import pandas as pd

service = Service(DRIVER_EXECUTABLE_PATH)
driver = webdriver.Chrome(service=service, options=options)

df = pd.read_csv("jacksonville.csv")
with open("error2.txt", "a") as error_file, open("error.txt", "r") as failed:
    street = failed.readlines()

    for street_address in street[235:]:
        street_address = street_address.strip("\n")
        street_no = street_address.split()[0]
        zip = street_address.split()[-1]
        street_name = " ".join(street_address.split()[1:-1])

        street_name = (
            street_name.lower()
            .replace(" unit", "")
            .replace(" blvd", "")
            .replace(" apt", "")
            .replace(" dr", "")
            .replace(" pkwy", "")
            .replace(" pkw", "")
            .replace(" st", "")
            .replace(" ln", "")
            .replace(" rd", "")
            .replace(" cir", "")
            .replace(" ave", "")
            .strip()
        )
        street_split_1 = street_name.split()
        street_split = []

        if len(street_split_1) > 1:

            for elem in street_split_1:
                elem = elem.lower().strip()
                if elem == "n" or elem == "w" or elem == "s" or elem == "e":
                    direction = elem
                    elem = ""

                else:
                    direction = ""

                if elem.startswith("#"):
                    elem = ""

                if elem.isnumeric():
                    elem = ""
                street_split.append(elem)

            street_name = " ".join(street_split)
        else:
            direction = ""

        if len(street_name.split()) >= 2 and len(street_name.split()[-1]) <= 3:
            street_name = " ".join(street_name.split()[:-1])
        print("-----------------------")
        print(street_no)
        print(street_name)
        print(direction)
        print(zip)
        print("------------------------")
        try:
            get_property_info(
                "info.csv", error_file, street_no, street_name, zip, direction
            )
        except:
            error_file.write(
                " ".join((str(street_no), direction, street_name, str(zip)))
            )
            error_file.write("\n")
            continue

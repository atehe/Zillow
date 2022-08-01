from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector
from csv import writer
import time, logging, sys, os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import pandas as pd
from datetime import date


logging.basicConfig(level=logging.INFO)
DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"

ERROR_FILE = "error.csv"
NO_RESULT_FILE = "no_result.csv"

options = Options()
# options.add_argument("--headless")
# options.add_argument("--ignore-certificate-errors")
# options.add_argument("--allow-running-insecure-content")


def click(element, driver):
    """Use javascript click if selenium click method fails"""
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)
    time.sleep(0.5)


service = Service(DRIVER_EXECUTABLE_PATH)
driver = webdriver.Chrome(service=service, options=options)


def fill_n_search(
    street_num="", street_name="", zip_code="", direction="", city="Jacksonville"
):
    driver.get("https://paopropertysearch.coj.net/Basic/Search.aspx")

    # fill street number
    street_number_input = driver.find_element(
        by=By.XPATH, value='//input[contains(@id,"StreetNumber")]'
    )
    street_number_input.clear()
    street_number_input.send_keys(street_num)

    # fill street name
    street_name_input = driver.find_element(
        by=By.XPATH, value='//input[contains(@id,"StreetName")]'
    )
    street_name_input.clear()
    street_name_input.send_keys(street_name)

    # select city
    city_drop_down = Select(
        driver.find_element(by=By.XPATH, value='//select[contains(@id,"City")]')
    )
    city_drop_down.select_by_value(city)

    # increase search result per page
    result_down = Select(
        driver.find_element(
            by=By.XPATH, value='//select[contains(@id,"ResultsPerPage")]'
        )
    )
    result_down.select_by_value("10000")

    # select street direction
    street_direction = Select(
        driver.find_element(by=By.XPATH, value='//select[contains(@id,"Prefix")]')
    )
    street_direction.select_by_value(direction.strip().upper())

    # fill zip code
    zip_code_input = driver.find_element(
        by=By.XPATH, value='//input[contains(@id,"ZipCode")]'
    )
    zip_code_input.clear()
    zip_code_input.send_keys(zip_code)

    # ENTER to search
    zip_code_input.send_keys(Keys.RETURN)


def parse_result(output_csv, main_page, street_num, street_name, zip_code):
    driver.switch_to.window(main_page)
    page_response = Selector(text=driver.page_source.encode("utf8"))

    no_result = page_response.xpath('//div[@id="noResults"]')

    if no_result:
        print("*** Found no Owner Information ***")
        no_result_header = not os.path.exists(NO_RESULT_FILE)
        with open(NO_RESULT_FILE, "a") as no_result_file:
            if no_result_header:
                no_result_file.write("street_no,street_name,zipcode\n")
            no_result_file.write(
                ",".join((str(street_num), street_name, str(zip_code)))
            )
            no_result_file.write("\n")
            return None

    write_headers = not os.path.exists(output_csv)
    with open(output_csv, "a") as csv_file:
        csv_writer = writer(csv_file)
        headers = (
            "Real Estate Number",
            "Property URL",
            "Name",
            "Last Name",
            "First Name",
            "Street Number",
            "Street Name",
            "Type",
            "Direction",
            "Unit",
            "City",
            "Zip",
        )
        if write_headers:
            csv_writer.writerow(headers)

        table_rows = page_response.xpath('//table[contains(@id,"gridResults")]//tr')
        if len(table_rows) > 25:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        for row in table_rows[1:]:
            RE_number = row.xpath("./td[1]//text()").get()
            RE_url = row.xpath("./td[1]//a/@href").get()
            if RE_url:
                RE_url = f"https://paopropertysearch.coj.net/{RE_url}"
            name = row.xpath("./td[2]//text()").get()
            print(f"Found Owner {name}")
            name_list = name.split()
            first_name = " ".join(name_list[1:]) if len(name_list) >= 1 else None
            last_name = name_list[0]
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
                    last_name,
                    first_name,
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
    street_num="",
    street_name="",
    zip_code="",
    direction="",
    city="Jacksonville",
):
    main_page = driver.current_window_handle

    fill_n_search(street_num, street_name, zip_code, direction)
    parse_result(output_csv, main_page, street_num, street_name, zip_code)


def main(on_sale=True):
    service = Service(DRIVER_EXECUTABLE_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    month = date.today().month
    if on_sale:
        output_csv = f"jacksonville_owners_info_{month}.csv"
        zillow_data = f"zillow_onsale_{month}.csv"
    else:
        output_csv = f"recently_sold_owners_{month}.csv"
        zillow_data = f"zillow_sold_{month}.csv"

    df = pd.read_csv(zillow_data)

    for street_add, zip, _, _ in df.values[::-1]:

        street_no = street_add.split()[0]
        street_name = " ".join(street_add.split()[1:-1])

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
        street_name_words = street_name.split()
        street_name_words_list = []

        if len(street_name_words) > 1:
            for word in street_name_words:
                word = word.lower().strip()

                # check if word is a direction
                if word == "n" or word == "w" or word == "s" or word == "e":
                    direction = word
                    word = ""
                else:
                    direction = ""

                # replace words that may interfer with search
                if word.startswith("#"):
                    word = ""

                if word.isnumeric():
                    word = ""
                street_name_words_list.append(word)

            street_name = " ".join(street_name_words_list)
        else:
            direction = ""

        if len(street_name.split()) >= 2 and len(street_name.split()[-1]) <= 3:
            street_name = " ".join(street_name.split()[:-1])
        print("----------------------------------")
        print("    Getting Owners Information    ")
        print(f"Street Number: {street_no}")
        print(f"Street Name: {street_name.title()}")
        print(f"Direction: {direction.upper()}")
        print(f"Zip: {zip}")
        print("---------------------------------")

        try:
            get_property_info(output_csv, street_no, street_name, zip, direction)
        except Exception as e:
            print(e)
            error_header = not os.path.exists(ERROR_FILE)
            with open(ERROR_FILE, "a") as error_file:
                if error_header:
                    error_file.write("street_no,street_name,zipcode\n")
                error_file.write(",".join((str(street_no), street_name, str(zip))))
                error_file.write("\n")
                continue
    driver.quit()



if __name__ == "__main__":
    main()
    main(False)

    
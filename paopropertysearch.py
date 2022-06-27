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
driver = webdriver.Chrome(service=service, options=options)


# driver = uc.Chrome(version_main=100, options=options)

driver.get("https://paopropertysearch.coj.net/Basic/Search.aspx")

# 6613 CARTIER CIR, Jacksonville, FL

street_number_input = driver.find_element(
    by=By.XPATH, value='//input[contains(@id,"StreetNumber")]'
)
street_number_input.clear()
street_number_input.send_keys("6613")

street_name_input = driver.find_element(
    by=By.XPATH, value='//input[contains(@id,"StreetName")]'
)
street_name_input.clear()
street_name_input.send_keys("CARTIER")
zip_code_input = driver.find_element(
    by=By.XPATH, value='//input[contains(@id,"ZipCode")]'
)
zip_code_input.clear()
zip_code_input.send_keys("32208")


city_drop_down = Select(
    driver.find_element(by=By.XPATH, value='//select[contains(@id,"City")]')
)
city_drop_down.select_by_value("Jacksonville")

zip_code_input.send_keys(Keys.RETURN)

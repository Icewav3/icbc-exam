import os
import random
import time

import telegram_send
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# User configs
last_name = ""
license_id = ""
code = ""

# Location and month
location = "Coquitlam"
month = "December"

# Delay between actions
time_waiting = 2

url = "https://onlinebusiness.icbc.com/webdeas-ui/home"
driver_path = os.path.join(APP_ROOT, 'chromedriver')
driver = webdriver.Chrome(executable_path=driver_path)


def footer_waiting():
    delay = 5
    try:
        WebDriverWait(driver, delay).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'footer-content')))
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")


def send_keys_delayed():
    for char in location:
        driver.find_element(By.ID, 'mat-input-3').send_keys(char)
        time.sleep(random.uniform(0.03, 0.2))


def waiting():
    time.sleep(time_waiting)


driver.get(url)
footer_waiting()
driver.maximize_window()
waiting()
driver.execute_script("document.body.scrollTo(0, document.body.scrollHeight);")
waiting()
driver.find_element(By.CLASS_NAME, 'mat-button-wrapper').click()
footer_waiting()
driver.find_element(By.ID, 'mat-input-0').send_keys(last_name)
driver.find_element(By.ID, 'mat-input-1').send_keys(license_id)
driver.find_element(By.ID, 'mat-input-2').send_keys(code)
driver.find_element(By.CLASS_NAME, 'mat-checkbox-inner-container').click()
driver.execute_script("document.body.scrollTo(0, document.body.scrollHeight);")
waiting()
driver.find_element(By.XPATH, "//*[contains(text(), 'Sign in')]").click()
time.sleep(5)
send_keys_delayed()

waiting()
driver.find_element(By.ID, 'mat-input-3').send_keys(Keys.ENTER)
waiting()
driver.find_element(By.CLASS_NAME, 'search-button').click()
waiting()

while True:
    elements = driver.find_elements(By.CLASS_NAME, "department-container")
    for element in elements:
        element.click()
        waiting()
        dt_elements = driver.find_elements(By.CLASS_NAME, 'date-title')
        for dt_element in dt_elements:
            if month in dt_element.text:
                print("Found month: " + month)
                print("Location: " + element.text)
                telegram_send.send(messages=["Month: {0}".format(month), "Location: {0}".format(element.text)])

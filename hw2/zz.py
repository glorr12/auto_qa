from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import pytest
import os


@pytest.fixture
def driver():
    service = Service("E:\geckodriver-v0.37.0-win64\geckodriver.exe")
    options = Options()
    driver = webdriver.Firefox(service=service, options=options)
    # driver = webdriver.Firefox()
    # driver.maximize_window()
    driver.set_window_size(640, 460)
    # driver = webdriver.Firefox(service=service)
    # driver = webdriver.Firefox(options=options)
    yield driver
    driver.quit()

def test_about_page(driver):
    driver.get("https://itcareerhub.de/ru")
    sleep(3)
    about_link = driver.find_element(By.LINK_TEXT, "О нас")
    about_link.click()
    sleep(3)

def test_berlin(driver):
    driver.get("https://itcareerhub.de/ru")
    driver.refresh()
    driver.get("https://www.berlin.de")
    driver.save_screenshot("./berlin_s.png")
    sleep(2)
    driver.refresh()
    driver.back()
    sleep(2)
    driver.forward()
    driver.refresh()
    sleep(2)
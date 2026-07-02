from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import pytest
import os


@pytest.fixture
def driver():
    service = Service("E:\\geckodriver-v0.37.0-win64\\geckodriver.exe")
    options = Options()
    driver = webdriver.Firefox(service=service, options=options)
    driver.maximize_window()
    yield driver
    driver.quit()


def test_payment_section_screenshot(driver):
    driver.get("https://itcareerhub.de/ru")
    sleep(3)
    try:
        cookie_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Подтвердить')]")
        cookie_button.click()
        sleep(1)
    except Exception:
        pass

    payment_link = driver.find_element(By.LINK_TEXT, "Способы оплаты")
    payment_link.click()
    sleep(2)

    section = driver.find_element(By.ID, "rec1921734713")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", section)
    sleep(2)

    os.makedirs("screenshots", exist_ok=True)
    section.screenshot("screenshots/payment_section.png")
    sleep(1)
import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

GECKODRIVER_PATH = r"E:\geckodriver-v0.37.0-win64\geckodriver.exe"


def build_driver():

    options = Options()

    service = Service(executable_path=GECKODRIVER_PATH)

    firefox_driver = webdriver.Firefox(service=service, options=options)
    firefox_driver.maximize_window()
    return firefox_driver


@pytest.fixture
def driver():
    firefox_driver = build_driver()
    yield firefox_driver
    firefox_driver.quit()
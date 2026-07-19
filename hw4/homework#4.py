import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# ------------------------------------------------------------------------------------


# TASK # 1



PAGE_URL = "http://uitestingplayground.com/textinput"
NEW_LABEL = "ITCH"
WAIT_TIMEOUT = 10


@pytest.fixture
def firefox_driver():
    browser_options = Options()
    browser_options.add_argument("--headless")
    browser = webdriver.Firefox(options=browser_options)
    yield browser
    browser.quit()


def navigate_to_page(browser: webdriver.Firefox):
    browser.get(PAGE_URL)


def fill_text_field(browser: webdriver.Firefox):
    field = WebDriverWait(browser, WAIT_TIMEOUT).until(
        EC.element_to_be_clickable((By.ID, "newButtonName"))
    )
    field.clear()
    field.send_keys(NEW_LABEL)


def press_update_button(browser: webdriver.Firefox):
    btn = WebDriverWait(browser, WAIT_TIMEOUT).until(
        EC.element_to_be_clickable((By.ID, "updatingButton"))
    )
    btn.click()


def test_button_label_updates(firefox_driver: webdriver.Firefox):
    navigate_to_page(firefox_driver)
    fill_text_field(firefox_driver)
    press_update_button(firefox_driver)
    WebDriverWait(firefox_driver, WAIT_TIMEOUT).until(
        EC.text_to_be_present_in_element((By.ID, "updatingButton"), NEW_LABEL)
    )
    result_text = firefox_driver.find_element(By.ID, "updatingButton").text
    assert result_text == NEW_LABEL, f"Ожидалось: '{NEW_LABEL}', получено: '{result_text}'"


# ------------------------------------------------------------------------------------

# TASK # 2

GALLERY_URL = "https://bonigarcia.dev/selenium-webdriver-java/loading-images.html"
IMAGE_WAIT_TIMEOUT = 15


@pytest.fixture
def gallery_driver():
    gallery_options = Options()
    gallery_options.add_argument("--headless")
    drv = webdriver.Firefox(options=gallery_options)
    yield drv
    drv.quit()


def wait_until_images_ready(browser, image_locator):
    WebDriverWait(browser, IMAGE_WAIT_TIMEOUT).until(
        lambda d: len(d.find_elements(*image_locator)) >= 5,
        message="<img> не появились в DOM за нужное время",
    )
    WebDriverWait(browser, IMAGE_WAIT_TIMEOUT).until(
        lambda d: all(
            d.execute_script(
                "return arguments[0].complete && arguments[0].naturalWidth > 0;", pic
            )
            for pic in d.find_elements(*image_locator)
        ),
        message="Картинки не прогрузились полностью!",
    )


def test_fourth_image_alt_text(gallery_driver):
    gallery_driver.get(GALLERY_URL)
    image_locator = (By.TAG_NAME, "img")
    wait_until_images_ready(gallery_driver, image_locator)
    picture_elements = gallery_driver.find_elements(*image_locator)
    alt_value = picture_elements[3].get_attribute("alt")
    assert alt_value == "award", f"Ожидали alt='award', а получили '{alt_value}'"
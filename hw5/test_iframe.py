import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PAGE_URL = "https://bonigarcia.dev/selenium-webdriver-java/iframes.html"
IFRAME_ID = "my-iframe"
EXPECTED_TEXT = "semper posuere integer et senectus justo curabitur."
WAIT_TIMEOUT = 10


@pytest.fixture
def browser():
    options = Options()
    options.add_argument("--headless")
    drv = webdriver.Firefox(options=options)
    yield drv
    drv.quit()


def open_page(driver):
    driver.get(PAGE_URL)


def switch_to_target_iframe(driver):
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, IFRAME_ID))
    )


def find_paragraph_with_text(driver, expected_text):
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "p"))
    )
    paragraphs = driver.find_elements(By.TAG_NAME, "p")
    for paragraph in paragraphs:
        if expected_text in paragraph.text:
            return paragraph
    return None


def test_text_present_inside_iframe(browser):
    open_page(browser)
    switch_to_target_iframe(browser)

    target_paragraph = find_paragraph_with_text(browser, EXPECTED_TEXT)

    assert target_paragraph is not None, f"Текст '{EXPECTED_TEXT}' не найден внутри iframe"
    assert target_paragraph.is_displayed(), "Найденный элемент с текстом не отображается на странице"

    browser.switch_to.default_content()
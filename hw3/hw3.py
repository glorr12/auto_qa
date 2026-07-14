import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)

from conftest import build_driver

BASE_URL = "https://itcareerhub.de/ru"
WAIT_TIMEOUT = 15
POPUP_TEXT = "Запишитесь на бесплатную карьерную консультацию"

_UPPER_RU = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
_LOWER_RU = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

def get_visible_elements(driver, by, value):
    return [el for el in driver.find_elements(by, value) if el.is_displayed()]


def wait_for_visible_element(driver, by, value, timeout=WAIT_TIMEOUT):
    def _condition(drv):
        visible = get_visible_elements(drv, by, value)
        return visible[0] if visible else False

    return WebDriverWait(driver, timeout).until(
        _condition, message=f"Не дождались видимого элемента: {by}={value}"
    )


def js_click(driver, element):
    driver.execute_script("arguments[0].click();", element)


def safe_click(driver, element):
    try:
        element.click()
    except ElementClickInterceptedException:
        js_click(driver, element)


def exact_text_xpath(tag, text):
    return f"//{tag}[normalize-space(.)='{text}']"


def case_insensitive_contains_xpath(tag, text_lower):
    return (
        f"//{tag}[contains(translate(normalize-space(.), "
        f"'{_UPPER_RU}', '{_LOWER_RU}'), '{text_lower}')]"
    )


def close_cookie_banner(driver):
    try:
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, case_insensitive_contains_xpath("*", "подтвердить"))
            )
        )
        js_click(driver, button)
    except TimeoutException:
        pass


def open_about_submenu(driver):
    about_link = wait_for_visible_element(driver, By.XPATH, exact_text_xpath("a", "О нас"))
    ActionChains(driver).move_to_element(about_link).perform()



class TestHomePageHeaderAndCallbackPopup:

    @pytest.fixture(scope="class")
    def driver(self):
        firefox_driver = build_driver()
        firefox_driver.get(BASE_URL)
        close_cookie_banner(firefox_driver)
        yield firefox_driver
        firefox_driver.quit()

    def test_01_logo_is_visible(self, driver):
        logo = wait_for_visible_element(driver, By.CSS_SELECTOR, "img[alt='IT Career Hub']")
        assert logo.is_displayed(), "Логотип ITCareerHub не отображается"

    def test_02_link_programs_is_visible(self, driver):
        visible = get_visible_elements(driver, By.XPATH, exact_text_xpath("a", "Программы"))
        assert visible, "Ссылка 'Программы' не отображается на странице"

    def test_03_link_payment_methods_is_visible(self, driver):
        visible = get_visible_elements(driver, By.XPATH, exact_text_xpath("a", "Способы оплаты"))
        assert visible, "Ссылка 'Способы оплаты' не отображается на странице"

    def test_04_link_about_is_visible(self, driver):
        visible = get_visible_elements(driver, By.XPATH, exact_text_xpath("a", "О нас"))
        assert visible, "Ссылка 'О нас' не отображается на странице"

    def test_05_link_reviews_is_visible(self, driver):
        visible = get_visible_elements(driver, By.XPATH, exact_text_xpath("a", "Отзывы"))
        assert visible, "Ссылка 'Отзывы' не отображается на странице"

    def test_06_link_blog_is_visible(self, driver):
        visible = get_visible_elements(driver, By.XPATH, exact_text_xpath("a", "Блог"))
        assert visible, "Ссылка 'Блог' не отображается на странице"

    def test_07_link_contacts_is_visible_in_submenu(self, driver):
        open_about_submenu(driver)
        visible = get_visible_elements(driver, By.XPATH, exact_text_xpath("a", "Контакты"))
        assert visible, "Ссылка 'Контакты' не отображается в подменю 'О нас'"

    def test_08_language_switch_buttons_are_visible(self, driver):
        lang_ru = get_visible_elements(driver, By.XPATH, exact_text_xpath("a", "ru"))
        lang_de = get_visible_elements(driver, By.XPATH, exact_text_xpath("a", "de"))
        assert lang_ru, "Кнопка переключения языка 'ru' не отображается"
        assert lang_de, "Кнопка переключения языка 'de' не отображается"

    def test_09_click_contacts_navigates_to_contact_page(self, driver):
        open_about_submenu(driver)
        contacts_link = wait_for_visible_element(driver, By.XPATH, exact_text_xpath("a", "Контакты"))
        safe_click(driver, contacts_link)

        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.url_contains("contact-us"))
        close_cookie_banner(driver)
        assert "contact-us" in driver.current_url, "Переход на страницу контактов не произошёл"

    def test_10_click_callback_button(self, driver):
        callback_button = wait_for_visible_element(
            driver, By.XPATH, case_insensitive_contains_xpath("a", "обратный звонок")
        )
        safe_click(driver, callback_button)

    def test_11_popup_shows_consultation_text(self, driver):
        popup_text_element = wait_for_visible_element(
            driver,
            By.XPATH,
            (
                f'//*[contains(normalize-space(.), "{POPUP_TEXT}")]'
                f'[not(.//*[contains(normalize-space(.), "{POPUP_TEXT}")])]'
            ),
        )
        assert POPUP_TEXT in popup_text_element.text, (
            "Текст 'Запишитесь на бесплатную карьерную консультацию' "
            "не отображается во всплывающем окне"
        )
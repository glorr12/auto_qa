import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class BasePage:
    TIMEOUT = 10

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.TIMEOUT)

    def open(self, url):
        self.driver.get(url)

    def find(self, locator):
        return self.wait.until(ec.visibility_of_element_located(locator))

    def find_all(self, locator):
        return self.wait.until(ec.presence_of_all_elements_located(locator))

    def click(self, locator):
        self.wait.until(ec.element_to_be_clickable(locator)).click()

    def type_text(self, locator, text):
        field = self.find(locator)
        field.clear()
        field.send_keys(text)

    def get_text(self, locator):
        return self.find(locator).text


class LoginPage(BasePage):
    URL = "https://www.saucedemo.com/"

    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")

    def open_page(self):
        self.open(self.URL)
        return self

    def login(self, username, password):
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)


class InventoryPage(BasePage):
    CART_ICON = (By.CSS_SELECTOR, ".shopping_cart_link")

    def add_product_to_cart(self, product_name):
        button_id = "add-to-cart-" + product_name.lower().replace(" ", "-")
        locator = (By.ID, button_id)
        self.click(locator)
        return self

    def go_to_cart(self):
        self.click(self.CART_ICON)

class CartPage(BasePage):
    CHECKOUT_BUTTON = (By.ID, "checkout")
    CART_ITEMS = (By.CSS_SELECTOR, ".cart_item")

    def checkout(self):
        self.click(self.CHECKOUT_BUTTON)

    def get_items_count(self):
        return len(self.find_all(self.CART_ITEMS))


class CheckoutStepOnePage(BasePage):
    FIRST_NAME_INPUT = (By.ID, "first-name")
    LAST_NAME_INPUT = (By.ID, "last-name")
    POSTAL_CODE_INPUT = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")

    def fill_info(self, first_name, last_name, postal_code):
        self.type_text(self.FIRST_NAME_INPUT, first_name)
        self.type_text(self.LAST_NAME_INPUT, last_name)
        self.type_text(self.POSTAL_CODE_INPUT, postal_code)
        self.click(self.CONTINUE_BUTTON)


class CheckoutStepTwoPage(BasePage):
    TOTAL_LABEL = (By.CSS_SELECTOR, ".summary_total_label")
    FINISH_BUTTON = (By.ID, "finish")

    def get_total(self):
        text = self.get_text(self.TOTAL_LABEL)
        return text.split(":")[1].strip()

    def finish(self):
        self.click(self.FINISH_BUTTON)


@pytest.fixture
def driver():
    options = webdriver.FirefoxOptions()
    drv = webdriver.Firefox(options=options)
    drv.maximize_window()
    yield drv
    drv.quit()


USERNAME = "standard_user"
PASSWORD = "secret_sauce"

PRODUCTS = [
    "Sauce Labs Backpack",
    "Sauce Labs Bolt T-Shirt",
    "Sauce Labs Onesie",
]

EXPECTED_TOTAL = "$58.29"


def test_checkout_total_is_correct(driver):
    login_page = LoginPage(driver)
    login_page.open_page()
    login_page.login(USERNAME, PASSWORD)

    inventory_page = InventoryPage(driver)
    for product in PRODUCTS:
        inventory_page.add_product_to_cart(product)

    inventory_page.go_to_cart()

    cart_page = CartPage(driver)
    assert cart_page.get_items_count() == len(PRODUCTS)
    cart_page.checkout()

    checkout_step_one = CheckoutStepOnePage(driver)
    checkout_step_one.fill_info("Adolf", "Kitler", "8200")

    checkout_step_two = CheckoutStepTwoPage(driver)
    total = checkout_step_two.get_total()

    assert total == EXPECTED_TOTAL, f"Ожидалась сумма {EXPECTED_TOTAL}, получена {total}"
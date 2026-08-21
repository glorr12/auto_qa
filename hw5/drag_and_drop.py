import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PAGE_URL = "https://www.globalsqa.com/demo-site/draganddrop/"
WAIT_TIMEOUT = 25
COOKIE_WAIT_TIMEOUT = 8
DEMO_FRAME_LOCATOR = (By.CSS_SELECTOR, "iframe.demo-frame")
GALLERY_LOCATOR = (By.CSS_SELECTOR, "#gallery li")
TRASH_LOCATOR = (By.ID, "trash")
TRASH_PHOTOS_LOCATOR = (By.CSS_SELECTOR, "#trash li")

COOKIE_ACCEPT_TEXTS = ["Соглашаюсь", "Согласен", "Принять", "Accept", "I Agree", "Agree"]

_FIND_BY_TEXT_JS = """
const texts = arguments[0].map(t => t.toLowerCase());

function isVisible(el) {
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    return rect.width > 0 && rect.height > 0 &&
           style.visibility !== 'hidden' && style.display !== 'none';
}

function matchIn(elements, texts) {
    for (const el of elements) {
        const label = (el.innerText || el.textContent || '').trim().toLowerCase();
        if (!label) continue;
        for (const t of texts) {
            if ((label === t || (label.length < 40 && label.includes(t))) && isVisible(el)) {
                return el;
            }
        }
    }
    return null;
}

function searchRoot(root, texts) {
    // Сначала ищем среди настоящих интерактивных элементов (кнопки/ссылки) —
    // это исключает случайные попадания на div/span-обёртки с тем же текстом,
    // клик по которым может привести не к нажатию кнопки, а к выделению текста.
    let found = matchIn(
        root.querySelectorAll('button, a, [role="button"], input[type="button"], input[type="submit"]'),
        texts
    );
    if (found) return found;

    // Резерв: div/span, если сайт не использует семантические кнопки
    found = matchIn(root.querySelectorAll('span, div, label'), texts);
    if (found) return found;

    // Рекурсивно спускаемся в shadow roots
    const all = root.querySelectorAll('*');
    for (const el of all) {
        if (el.shadowRoot) {
            const inner = searchRoot(el.shadowRoot, texts);
            if (inner) return inner;
        }
    }
    return null;
}

return searchRoot(document, texts);
"""


@pytest.fixture
def browser():
    options = Options()
    drv = webdriver.Firefox(options=options)
    drv.set_window_size(1280, 1024)
    yield drv
    drv.quit()


def _find_accept_button_in_current_context(driver):
    try:
        return driver.execute_script(_FIND_BY_TEXT_JS, COOKIE_ACCEPT_TEXTS)
    except Exception:
        return None


def close_cookie_banner(driver, timeout=COOKIE_WAIT_TIMEOUT):
    driver.switch_to.default_content()
    deadline = time.time() + timeout

    while time.time() < deadline:
        element = _find_accept_button_in_current_context(driver)
        if element is not None:
            try:
                element.click()
                driver.switch_to.default_content()
                print("[debug] cookie-баннер закрыт (основной документ)")
                return True
            except Exception:
                pass

        # 2) пробуем во всех iframe на странице (кроме demo-frame с галереей)
        driver.switch_to.default_content()
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                driver.switch_to.frame(iframe)
            except Exception:
                driver.switch_to.default_content()
                continue

            element = _find_accept_button_in_current_context(driver)
            if element is not None:
                try:
                    element.click()
                    driver.switch_to.default_content()
                    print("[debug] cookie-баннер закрыт (внутри iframe)")
                    return True
                except Exception:
                    pass

            driver.switch_to.default_content()

        time.sleep(0.5)

    driver.switch_to.default_content()
    print("[debug] cookie-баннер не найден (или уже закрыт)")
    return False


def open_page(driver):
    driver.get(PAGE_URL)
    close_cookie_banner(driver)
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.frame_to_be_available_and_switch_to_it(DEMO_FRAME_LOCATOR)
    )
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_all_elements_located(GALLERY_LOCATOR)
    )


def drag_first_photo_to_trash(driver):
    gallery_photos = driver.find_elements(*GALLERY_LOCATOR)
    first_photo = gallery_photos[0]
    trash_area = driver.find_element(*TRASH_LOCATOR)

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_photo)

    source_rect = first_photo.rect
    target_rect = trash_area.rect

    start_offset_x = source_rect["width"] // 2
    start_offset_y = source_rect["height"] // 2
    end_x = target_rect["x"] + target_rect["width"] // 2
    end_y = target_rect["y"] + target_rect["height"] // 2
    start_x = source_rect["x"] + start_offset_x
    start_y = source_rect["y"] + start_offset_y

    total_dx = end_x - start_x
    total_dy = end_y - start_y
    steps = 15

    actions = ActionChains(driver, duration=50)
    actions.move_to_element_with_offset(first_photo, start_offset_x, start_offset_y)
    actions.click_and_hold()
    actions.pause(0.3)

    for i in range(1, steps + 1):
        step_x = int(total_dx * i / steps)
        step_y = int(total_dy * i / steps)
        actions.move_by_offset(
            (start_x + step_x) - (start_x + int(total_dx * (i - 1) / steps)),
            (start_y + step_y) - (start_y + int(total_dy * (i - 1) / steps)),
        )
        actions.pause(0.05)

    actions.pause(0.3)
    actions.release()
    actions.perform()


def test_drag_photo_to_trash(browser):
    open_page(browser)

    initial_gallery_photos = browser.find_elements(*GALLERY_LOCATOR)
    initial_count = len(initial_gallery_photos)

    drag_first_photo_to_trash(browser)

    print(
        f"[debug] после drag: в галерее {len(browser.find_elements(*GALLERY_LOCATOR))}, "
        f"в корзине {len(browser.find_elements(*TRASH_PHOTOS_LOCATOR))}"
    )

    WebDriverWait(browser, WAIT_TIMEOUT).until(
        lambda d: len(d.find_elements(*TRASH_PHOTOS_LOCATOR)) == 1
    )

    trash_photos = browser.find_elements(*TRASH_PHOTOS_LOCATOR)
    remaining_gallery_photos = browser.find_elements(*GALLERY_LOCATOR)

    assert len(trash_photos) == 1, f"Ожидалась 1 фотография в корзине, найдено: {len(trash_photos)}"
    assert len(remaining_gallery_photos) == 3, (
        f"Ожидалось 3 фотографии в галерее, найдено: {len(remaining_gallery_photos)}"
    )
    assert len(remaining_gallery_photos) == initial_count - 1, (
        "Количество фотографий в галерее не уменьшилось ровно на одну"
    )

    browser.switch_to.default_content()
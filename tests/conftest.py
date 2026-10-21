import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = "https://www.saucedemo.com/"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")


@pytest.fixture
def driver(request):
    options = Options()
    if os.getenv("HEADLESS", "1") == "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,768")
    # Tắt popup "đổi mật khẩu" của Chrome làm che giao diện khi test
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(5)
    drv.get(BASE_URL)
    yield drv

    # Chụp màn hình cuối mỗi test làm minh chứng
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    drv.save_screenshot(os.path.join(SCREENSHOT_DIR, f"{request.node.name}.png"))
    drv.quit()


def login(driver, username="standard_user", password="secret_sauce"):
    driver.find_element("id", "user-name").send_keys(username)
    driver.find_element("id", "password").send_keys(password)
    driver.find_element("id", "login-button").click()

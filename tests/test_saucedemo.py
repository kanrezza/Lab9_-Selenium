"""Bộ test case tự động cho website https://www.saucedemo.com bằng Selenium WebDriver."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from conftest import login


def test_tc01_login_success(driver):
    """TC01 - Đăng nhập thành công với tài khoản hợp lệ."""
    login(driver)
    WebDriverWait(driver, 10).until(EC.url_contains("inventory.html"))
    assert driver.find_element(By.CLASS_NAME, "title").text == "Products"


def test_tc02_login_wrong_password(driver):
    """TC02 - Đăng nhập thất bại khi sai mật khẩu."""
    login(driver, password="wrong_password")
    error = driver.find_element(By.CSS_SELECTOR, "[data-test='error']").text
    assert "Username and password do not match" in error
    assert "inventory.html" not in driver.current_url


def test_tc03_login_locked_user(driver):
    """TC03 - Tài khoản bị khóa không thể đăng nhập."""
    login(driver, username="locked_out_user")
    error = driver.find_element(By.CSS_SELECTOR, "[data-test='error']").text
    assert "Sorry, this user has been locked out" in error


def test_tc04_login_empty_fields(driver):
    """TC04 - Bỏ trống username/password thì báo lỗi bắt buộc nhập."""
    driver.find_element(By.ID, "login-button").click()
    error = driver.find_element(By.CSS_SELECTOR, "[data-test='error']").text
    assert "Username is required" in error


def test_tc05_add_product_to_cart(driver):
    """TC05 - Thêm sản phẩm vào giỏ hàng, badge giỏ hàng hiển thị số lượng."""
    login(driver)
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    driver.find_element(By.ID, "add-to-cart-sauce-labs-bike-light").click()
    assert driver.find_element(By.CLASS_NAME, "shopping_cart_badge").text == "2"

    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    WebDriverWait(driver, 10).until(EC.url_contains("cart.html"))
    items = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".cart_item .inventory_item_name")))
    names = [e.text for e in items]
    assert names == ["Sauce Labs Backpack", "Sauce Labs Bike Light"]


def test_tc06_remove_product_from_cart(driver):
    """TC06 - Xóa sản phẩm khỏi giỏ hàng."""
    login(driver)
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    driver.find_element(By.ID, "remove-sauce-labs-backpack").click()
    assert not driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")


def test_tc07_sort_price_low_to_high(driver):
    """TC07 - Sắp xếp sản phẩm theo giá tăng dần."""
    login(driver)
    Select(driver.find_element(By.CLASS_NAME, "product_sort_container")).select_by_value("lohi")
    prices = [float(e.text.replace("$", ""))
              for e in driver.find_elements(By.CLASS_NAME, "inventory_item_price")]
    assert prices == sorted(prices)


def test_tc08_checkout_complete(driver):
    """TC08 - Thanh toán đơn hàng thành công."""
    login(driver)
    driver.find_element(By.ID, "add-to-cart-sauce-labs-onesie").click()
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    driver.find_element(By.ID, "checkout").click()
    driver.find_element(By.ID, "first-name").send_keys("Danh")
    driver.find_element(By.ID, "last-name").send_keys("Tran")
    driver.find_element(By.ID, "postal-code").send_keys("100000")
    driver.find_element(By.ID, "continue").click()
    driver.find_element(By.ID, "finish").click()
    header = driver.find_element(By.CLASS_NAME, "complete-header").text
    assert header == "Thank you for your order!"


def test_tc09_logout(driver):
    """TC09 - Đăng xuất quay về trang đăng nhập."""
    login(driver)
    driver.find_element(By.ID, "react-burger-menu-btn").click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "logout_sidebar_link"))).click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "login-button")))
    assert driver.current_url.rstrip("/") == "https://www.saucedemo.com"


def test_tc10_access_inventory_without_login(driver):
    """TC10 - Truy cập trực tiếp trang sản phẩm khi chưa đăng nhập bị chặn."""
    driver.get("https://www.saucedemo.com/inventory.html")
    error = driver.find_element(By.CSS_SELECTOR, "[data-test='error']").text
    assert "You can only access '/inventory.html' when you are logged in" in error

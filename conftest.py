
import pytest
import pickle
import os
import json
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from api.client import TandoorAPIClient
from pages.login_page import LoginPage
from selenium.webdriver.chrome.options import Options


# Фикстура только для UI
@pytest.fixture(scope="session")
def driver():
    options = Options()

    # 1. АВТОМАТИЧЕСКИЙ ВЫБОР РЕЖИМА
    # GitHub Actions всегда устанавливает переменную окружения CI=true
    if os.getenv('CI') == 'true':
        options.add_argument("--headless")  # Без окна
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")  # Дополнительная защита для Linux
    else:
        # Локально браузер будет открываться как обычно
        options.add_argument("--start-maximized")

    # 2. СТАБИЛЬНОСТЬ ОКНА

    options.add_argument("--window-size=1920,1080")

    # 3. АВТО-УСТАНОВКА ДРАЙВЕРА

    service = Service(ChromeDriverManager().install())

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        pytest.fail(f"Не удалось запустить WebDriver: {e}")

    yield driver

    # 4. БЕЗОПАСНОЕ ЗАКРЫТИЕ
    if driver:
        driver.quit()

# Фикстура только для API (Step #3 на вашем скрине)
@pytest.fixture(scope="session")
def api_client():
    # Для API браузер не нужен, создаем только клиент
    client = TandoorAPIClient()
    return client



@pytest.fixture
def created_recipe_ids():
    """Читает ID из твоего нового файла created_recipes_id.json"""
    file_path = 'created_recipes_id.json'
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def recipe_id(created_recipe_ids):
    """Берет первый ID из списка для тестов на удаление или план питания"""
    return created_recipe_ids[0]


@pytest.fixture(scope="session")
def setup_auth(driver):
    """Фикстура для авторизации и сохранения кук"""
    with allure.step("Авторизация и сохранение кук"):
        driver.get("https://app.tandoor.dev/accounts/login/")

        driver.find_element(By.NAME, "username").send_keys("Riccoragazzo77")
        driver.find_element(By.NAME, "password").send_keys("Digitalnomadtravelaroundtheworld$$$")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # Ожидаем успешного входа
        WebDriverWait(driver, 10).until(EC.url_contains("dashboard"))

        # Получаем и сохраняем куки
        cookies = driver.get_cookies()
        with open("user_cookies.pkl", "wb") as f:
            pickle.dump(cookies, f)

    # Передаем куки в тесты через yield
    yield cookies


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, _):
    outcome = yield
    report = outcome.get_result()

    # Проверяем, что тест упал во время выполнения
    if report.when == 'call' and report.failed:

        driver = item.funcargs.get('driver')

        if driver:

            if not os.path.exists('screenshots'):
                os.makedirs('screenshots')

            #  Делаем скриншот напрямую в Allure
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"Screenshot_{item.name}",
                attachment_type=allure.attachment_type.PNG
            )
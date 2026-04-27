
import pytest
import pickle
import os
import json
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
    # В headless режиме важно явно задать размер, иначе кнопки "слипнутся"
    options.add_argument("--window-size=1920,1080")

    # 3. АВТО-УСТАНОВКА ДРАЙВЕРА
    # Чтобы не мучиться с путями к chromedriver.exe на разных системах
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


# 2. Фикстура для загрузки твоих ID (Шаг №3)
@pytest.fixture
def created_recipe_ids():
    """Читает ID из твоего нового файла created_recipes_id.json"""
    file_path = 'created_recipes_id.json'
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        return json.load(f)

# 3. Фикстура для одного рецепта (Шаг №3)
@pytest.fixture
def recipe_id(created_recipe_ids):
    """Берет первый ID из списка для тестов на удаление или план питания"""
    return created_recipe_ids[0]



@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # Если тест упал именно во время выполнения (call)
    if report.when == 'call' and report.failed:
        # Достаем драйвер из фикстур теста
        driver = item.funcargs.get('driver')
        if driver:
            # Создаем папку, если её нет
            if not os.path.exists('screenshots'):
                os.makedirs('screenshots')

                # Сохраняем скриншот с именем теста
                driver.save_screenshot(f"screenshots/{item.name}.png")


@pytest.fixture(scope="function")
def setup_auth(driver):
    """Фикстура для выполнения логина и сохранения кук в файл"""
    cookie_file = "user_cookies.pkl"

    # 1. Заходим на страницу логина
    driver.get("https://app.tandoor.dev/login")

    # 2. Выполняем вход (используем твои данные)
    login_page = LoginPage(driver)
    login_page.login(username="Riccoragazzo77", password="Richman777$$$")

    # 3. Получаем список кук
    cookies = driver.get_cookies()

    # 4. Сохраняем их в файл через pickle
    with open(cookie_file, "wb") as f:
        pickle.dump(cookies, f)

    # Возвращаем именно список кук в тест
    yield cookies
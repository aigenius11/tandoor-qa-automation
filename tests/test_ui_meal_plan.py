from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
from pages.meal_plan_page import MealPlanPage



def test_login_and_open_dashboard(driver):
    login_page = LoginPage(driver)
    driver.get("https://app.tandoor.dev/accounts/login/")

    login_page.login("Riccoragazzo77", "Richman777$$$")


    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Vladislav Kochergin')]"))
    )

    # Проверяем, что мы зашли (имя отображается)
    assert "Vladislav" in driver.page_source
    print("Авторизация подтверждена по имени пользователя!")


def test_create_meal_plan_with_cookies(driver, setup_auth):
    # 1. Заходим на домен
    driver.get("https://app.tandoor.dev")

    # 2. Добавляем куки
    for cookie in setup_auth:
        driver.add_cookie(cookie)

    # 3. ПЕРЕХОДИМ СРАЗУ НА СТРАНИЦУ ПЛАНА (без промежуточного refresh)
    driver.get("https://app.tandoor.dev/mealplan")

    # Ждем, пока URL станет правильным (защита от редиректа на главную)
    WebDriverWait(driver, 10).until(EC.url_contains("/mealplan"))

    meal_plan_page = MealPlanPage(driver)

    # Используй сегодняшнюю дату со скриншота для теста стабильности
    target_date = "2026-04-26"
    recipe = "Паста в аэрогриле"

    # Кликаем и заполняем
    meal_plan_page.add_plan_on_date(target_date, recipe)

    # 5. Проверка (Assert)
    assert meal_plan_page.is_plan_displayed(target_date, recipe), f"План {recipe} не найден!"
    print(f"План '{recipe}' успешно создан!")


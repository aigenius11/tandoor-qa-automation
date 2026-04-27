from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import allure
import pytest


@allure.feature("Shopping List")
@allure.story("Integration API + UI")
def test_shopping_list_integration(driver, setup_auth, api_client):
    with allure.step("Синхронизация авторизации (Cookies & CSRF)"):
        for cookie in driver.get_cookies():
            api_client.session.cookies.set(cookie['name'], cookie['value'])
            if cookie['name'] == 'csrftoken':
                api_client.session.headers.update({'X-CSRFToken': cookie['value']})
        api_client.session.headers.update({'Referer': "https://app.tandoor.dev/"})

    with allure.step("Создание плана питания через API (Precondition)"):
        # Используем ваш ручной ID, так как среда ограничена
        recipe_id = 140618
        plan = api_client.create_meal_plan(recipe_id=recipe_id, date="2026-05-15")
        plan_id = plan.get("id")
        allure.attach(str(plan), name="API Response JSON", attachment_type=allure.attachment_type.JSON)

    try:
        with allure.step("Проверка отображения продуктов в UI"):
            driver.get("https://app.tandoor.dev/shopping")
            wait = WebDriverWait(driver, 15)
            # Ждем появления текста
            wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Паста"))
            assert "Паста" in driver.page_source

    finally:
        if plan_id:
            with allure.step("Очистка данных (TearDown)"):
                api_client.delete_meal_plan(plan_id)
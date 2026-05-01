import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.mark.ui
@pytest.mark.api
@allure.feature("Shopping List")
@allure.story("Integration API + UI")
@allure.title("E2E: Создание плана питания через API и проверка в UI")
def test_shopping_list_integration(driver, setup_auth, api_client):

    recipe_id = 140618
    plan_id = None

    with allure.step("Синхронизация авторизации (Cookies & CSRF)"):
        # Переносим токены из браузера в API-клиент для работы в одной сессии
        for cookie in driver.get_cookies():
            api_client.session.cookies.set(cookie['name'], cookie['value'])
            if cookie['name'] == 'csrftoken':
                api_client.session.headers.update({'X-CSRFToken': cookie['value']})
        api_client.session.headers.update({'Referer': "https://app.tandoor.dev/"})

    with allure.step("Предусловие: Создание плана питания через API"):
        # Создаем запись в календаре через API
        plan = api_client.create_meal_plan(recipe_id=recipe_id, date="2026-05-15")
        plan_id = plan.get("id")

        # Прикрепляем JSON ответа к отчету Allure для отладки
        allure.attach(str(plan), name="API Response JSON", attachment_type=allure.attachment_type.JSON)
        assert plan_id is not None, "Ошибка API: план питания не был создан"

    try:
        with allure.step("Проверка отображения продуктов в UI"):
            driver.get("https://app.tandoor.dev/shopping")
            wait = WebDriverWait(driver, 15)

            # Ждем появления текста рецепта на странице
            wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Паста"))

            # Финальная проверка наличия элемента в DOM
            assert "Паста" in driver.page_source, "Рецепт 'Паста' не появился в списке покупок UI"

    finally:
        # Блок очистки данных гарантирует удаление плана даже при падении теста
        if plan_id:
            with allure.step("Очистка данных (TearDown): Удаление плана через API"):
                api_client.delete_meal_plan(plan_id)
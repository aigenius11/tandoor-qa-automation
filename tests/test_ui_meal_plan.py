import pytest
import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
from pages.meal_plan_page import MealPlanPage


@pytest.mark.ui
@allure.feature("Meal Plan Management")
class TestMealPlanUI:

    @allure.story("Login and Dashboard")
    @allure.title("Проверка авторизации и открытия дашборда")
    def test_login_and_open_dashboard(self, driver):
        login_page = LoginPage(driver)

        with allure.step("Открытие страницы логина"):
            driver.get("https://app.tandoor.dev/accounts/login/")

        with allure.step("Ввод учетных данных и вход"):

            login_page.login(username="Riccoragazzo77", password="Digitalnomadtravelaroundtheworld$$$")

        with allure.step("Проверка успешной авторизации по имени пользователя"):
            # Ждем появления конкретного элемента с именем
            wait = WebDriverWait(driver, 10)
            user_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Vladislav Kochergin')]")))
            assert user_element.is_displayed(), "Имя пользователя не отображается на дашборде"
            assert "Vladislav" in driver.page_source, "Текст 'Vladislav' не найден в источнике страницы"

    @allure.story("Create Meal Plan")
    @allure.title("Создание плана питания с использованием cookies")
    def test_create_meal_plan_with_cookies(self, driver, setup_auth):
        meal_plan_page = MealPlanPage(driver)
        target_date = "2026-04-26"
        recipe_name = "Паста в аэрогриле"

        with allure.step("Загрузка домена и добавление кук"):
            driver.get("https://app.tandoor.dev")
            for cookie in setup_auth:
                driver.add_cookie(cookie)

        with allure.step("Переход на страницу плана питания"):
            driver.get("https://app.tandoor.dev/mealplan")
            WebDriverWait(driver, 10).until(EC.url_contains("/mealplan"))

        with allure.step(f"Добавление рецепта '{recipe_name}' на дату {target_date}"):
            meal_plan_page.add_plan_on_date(target_date, recipe_name)

        with allure.step("Проверка (Assert): отображается ли рецепт в плане"):

            is_displayed = meal_plan_page.is_plan_displayed(target_date, recipe_name)
            assert is_displayed, f"План с рецептом '{recipe_name}' не найден на дату {target_date}!"
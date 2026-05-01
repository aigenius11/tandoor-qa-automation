import pytest
import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.shopping_list_page import ShoppingListPage


@pytest.mark.ui
@allure.feature("Shopping List")
@allure.story("Full Cycle Shopping List")
@allure.title("Полный цикл: Создание рецепта -> Проверка ингредиентов -> Удаление")
def test_shopping_list_full_cycle(driver, setup_auth):
    shopping_page = ShoppingListPage(driver)
    recipe_name = "Паста в аэрогриле"
    ingredients = ["Макароны", "Помидоры"]

    with allure.step("Авторизация через Cookies"):
        driver.get("https://app.tandoor.dev")
        for cookie in setup_auth:
            driver.add_cookie(cookie)
        # Переходим сразу в Shopping, чтобы куки применились
        driver.get("https://app.tandoor.dev/shopping")

    with allure.step("Ожидание загрузки страницы Shopping List"):
        WebDriverWait(driver, 15).until(EC.url_contains("/shopping"))

    try:
        with allure.step(f"Добавление рецепта '{recipe_name}'"):
            shopping_page.open_recipes_tab()
            shopping_page.create_recipe(recipe_name)

        with allure.step("Выбор списка в модальном окне и подтверждение"):
            shopping_page.select_dinner_list_and_confirm()



        with allure.step(f"Критическая проверка: появление рецепта '{recipe_name}' в списке"):

            recipe_locator = (By.XPATH, f"//div[contains(@class, 'v-list-item')]//*[contains(., '{recipe_name}')]")


            recipe_element = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located(recipe_locator),
                message=f"FAILED: Рецепт '{recipe_name}' не найден в Shopping List"
            )

            assert recipe_element.is_displayed(), "Рецепт присутствует в DOM, но не отображается"

        with allure.step("Валидация состава ингредиентов"):
            # Вместо поиска по всей странице (page_source), проверяем каждый ингредиент отдельно
            for ing in ingredients:
                with allure.step(f"Проверка ингредиента: {ing}"):
                    ing_locator = (By.XPATH, f"//div[contains(@class, 'v-list-item')]//*[contains(., '{ing}')]")

                    # Пытаемся найти конкретный элемент ингредиента
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(ing_locator),
                        message=f"ОШИБКА: Ингредиент '{ing}' не найден!"
                    )

                    assert element is not None, f"Объект ингредиента {ing} не проинициализирован"



    finally:
        with allure.step("Очистка данных: удаление рецепта из списка"):
            shopping_page.delete_recipe()
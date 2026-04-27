from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.shopping_list_page import ShoppingListPage


def test_shopping_list_full_cycle(driver, setup_auth):
    """
    Полный цикл: Авторизация -> Переход в Shopping -> Создание рецепта ->
    Выбор списка в модальном окне -> Проверка -> Удаление.
    """
    # 1. Авторизация
    driver.get("https://app.tandoor.dev")
    for cookie in setup_auth:
        driver.add_cookie(cookie)
    driver.refresh()

    # 2. Переход на страницу Shopping
    driver.get("https://app.tandoor.dev/shopping")
    WebDriverWait(driver, 15).until(EC.url_contains("/shopping"))

    shopping_page = ShoppingListPage(driver)
    recipe_name = "Паста в аэрогриле"

    # 3. Добавление рецепта
    shopping_page.open_recipes_tab()
    shopping_page.create_recipe(recipe_name)

    # 4. Взаимодействие с модальным окном
    shopping_page.select_dinner_list_and_confirm()

    # 5. Проверка появления ингредиентов в Shopping List
    # Ждем, пока заголовок рецепта появится в основном списке
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{recipe_name}')]"))
    )

    # Проверяем наличие текста ингредиентов на странице
    assert "Макароны" in driver.page_source, "Ингредиент 'Макароны' не найден!"
    assert "Помидоры" in driver.page_source, "Ингредиент 'Помидоры' не найден!"

    # 6. Удаление рецепта (очистка данных после теста)
    shopping_page.delete_recipe()
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ShoppingListPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

        # Локаторы
        self.recipes_tab = (By.CSS_SELECTOR, "button[role='tab'][value='recipes']")
        self.recipe_input = (By.CSS_SELECTOR, "input.multiselect-search")
        self.add_button = (By.CSS_SELECTOR, "button.bg-create")
        self.dropdown_trigger = (By.XPATH, "//div[contains(@class, 'v-field__input')]")
        self.dinner_option = (By.XPATH, "//*[contains(text(), 'Ingridients for dinner')]")
        self.add_to_shopping_confirm = (By.XPATH, "//button[contains(., 'ADD TO SHOPPING')]")

    def open_recipes_tab(self):
        """Метод с использованием JS-клика для обхода блокировок фронтенда"""
        element = self.wait.until(EC.presence_of_element_located(self.recipes_tab))
        self.driver.execute_script("arguments[0].click();", element)

    def create_recipe(self, name):
        """Ввод названия рецепта с защитой от 'неинтерактивности'"""
        # 1. Ждем появления элемента в DOM
        input_el = self.wait.until(EC.presence_of_element_located(self.recipe_input))

        # 2. Принудительно кликаем через JS, чтобы поле точно стало активным
        self.driver.execute_script("arguments[0].click();", input_el)

        # 3. Небольшая пауза через JS, чтобы фронтенд успел 'проснуться'
        self.driver.execute_script("arguments[0].focus();", input_el)

        # 4. Очистка и ввод текста стандартным способом
        try:
            input_el.clear()
        except:
            # Если clear() падает, используем Keys для очистки
            input_el.send_keys(Keys.CONTROL + "a")
            input_el.send_keys(Keys.BACKSPACE)

        input_el.send_keys(name)

        # 5. Нажимаем Enter для выбора из выпадающего списка
        input_el.send_keys(Keys.ENTER)

        # 6. Нажимаем кнопку создания (ADD)
        self.wait.until(EC.element_to_be_clickable(self.add_button)).click()

    def select_dinner_list_and_confirm(self):
        """Выбор списка в модальном окне"""
        # Клик по триггеру (используем JS, если обычный клик падает)
        trigger = self.wait.until(EC.presence_of_element_located(self.dropdown_trigger))
        self.driver.execute_script("arguments[0].click();", trigger)

        # Клик по самому пункту
        option = self.wait.until(EC.element_to_be_clickable(self.dinner_option))
        option.click()

        # Финальное подтверждение
        self.wait.until(EC.element_to_be_clickable(self.add_to_shopping_confirm)).click()

    def delete_recipe(self):
        """Метод для удаления рецепта и подтверждения в модальном окне"""

        # 1. Локатор основной кнопки удаления (красная корзина)
        # Используем уникальный класс bg-delete из вашего скриншота
        delete_icon_xpath = "//button[contains(@class, 'bg-delete')]"

        # 2. Локатор кнопки подтверждения во всплывающем окне
        # Используем текст 'DELETE' и класс text-delete
        confirm_btn_xpath = "//div[contains(@class, 'v-card-actions')]//button[contains(., 'DELETE')]"

        try:
            # Нажимаем на корзину
            delete_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, delete_icon_xpath))
            )
            delete_btn.click()

            # Ждем появления модального окна и нажимаем красную кнопку DELETE
            confirm_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, confirm_btn_xpath))
            )
            confirm_btn.click()

            # Ждем, пока модальное окно исчезнет для стабильности следующего теста
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.XPATH, confirm_btn_xpath))
            )
        except Exception as e:
            print(f"Не удалось удалить рецепт: {e}")
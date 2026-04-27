from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

class MealPlanPage:
    def __init__(self, driver):
        self.driver = driver
        # Установлен таймаут 15 секунд для работы с тяжелым календарем
        self.wait = WebDriverWait(self.driver, 15)

    def add_plan_on_date(self, date_str, recipe_name, meal_type="Lunch"):
        """
        Метод с интеграцией всех предложенных подходов: data-date, Hover и клик по внутренней кнопке.
        """
        print(f"Начинаю поиск ячейки для даты: {date_str}")

        # 1. Поиск ячейки (Пробуем разные варианты структуры FullCalendar)
        date_xpath = f"//td[@data-date='{date_str}'] | //div[@data-date='{date_str}']"

        try:
            date_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, date_xpath)))
            print("Ячейка даты найдена")
        except Exception as e:
            print(f"Ошибка: Не удалось найти ячейку с датой {date_str}. Проверьте, отображается ли она на экране.")
            raise e

        # 2. Наведение мыши (Hover) для активации элементов управления ячейки
        actions = ActionChains(self.driver)
        actions.move_to_element(date_element).pause(1).perform()

        # 3. Поиск кнопки '+' внутри ячейки (согласно рекомендации куратора)
        add_btn_xpath = (
            f"//td[@data-date='{date_str}']//button | "
            f"//td[@data-date='{date_str}']//*[contains(@class, 'add')] | "
            f"//div[@data-date='{date_str}']//button"
        )

        try:
            print("Пытаюсь найти и кликнуть на кнопку добавления (+)")
            add_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, add_btn_xpath)))
            add_btn.click()
        except:
            print("Кнопка '+' не найдена, использую резервный метод (двойной клик)")
            actions.double_click(date_element).perform()

        # 4. Заполнение формы (Recipe)
        print("Ожидаю появления формы ввода...")
        recipe_input_xpath = "//input[@aria-placeholder='Recipe'] | //input[contains(@placeholder, 'Recipe')]"
        recipe_field = self.wait.until(EC.element_to_be_clickable((By.XPATH, recipe_input_xpath)))
        recipe_field.send_keys(recipe_name)
        time.sleep(0.5)
        recipe_field.send_keys(Keys.ENTER)

        # 5. Заполнение Meal Type
        meal_type_xpath = "//input[@aria-placeholder='Meal type'] | //input[contains(@placeholder, 'Meal type')]"
        type_field = self.wait.until(EC.element_to_be_clickable((By.XPATH, meal_type_xpath)))
        type_field.send_keys(meal_type)
        time.sleep(0.5)
        type_field.send_keys(Keys.ENTER)

        # 6. Сохранение плана
        self.driver.find_element(By.XPATH, "//button[contains(., 'CREATE')]").click()

        save_btn_xpath = "//button[contains(., 'Save')] | //button[contains(@class, 'btn-primary') and contains(., 'Save')]"
        save_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, save_btn_xpath)))
        save_btn.click()

        # Ожидание исчезновения модального окна
        self.wait.until(EC.invisibility_of_element_located((By.XPATH, save_btn_xpath)))
        print("План успешно сохранен")

    def is_plan_displayed(self, date_str, recipe_name):
        """Проверка наличия рецепта в ячейке"""
        label_xpath = f"//div[contains(@class, 'd{date_str}')]//div[contains(text(), '{recipe_name}')]"
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, label_xpath)))
            return True
        except:
            return False
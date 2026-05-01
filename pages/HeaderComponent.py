from selenium.webdriver.common.by import By
from pages.BasePage import BasePage

class HeaderComponent(BasePage):
    # Локаторы
    HOME_RECIPE_LINK = (By.CSS_SELECTOR, "a[href='/']") # Recipes
    MEAL_PLAN_LINK = (By.CSS_SELECTOR, "a[href='/mealplan']")
    SHOPPING_LINK = (By.CSS_SELECTOR, "a[href='/shopping']")
    USER_NAME_LABEL = (By.CSS_SELECTOR, ".v-list-item-title")

    def __init__(self, driver):
        super().__init__(driver)

    def navigate_to_home_recipes(self):
        """Переход на главную к рецептам через логотип"""
        self.click(self.HOME_RECIPE_LINK)

    def navigate_to_meal_plan(self):
        """Переход в План питания"""
        self.click(self.MEAL_PLAN_LINK)

    def navigate_to_shopping_list(self):
        """Переход в Список покупок"""
        self.click(self.SHOPPING_LINK)

    def get_authorized_user_name(self):
        """Получение имени для проверки авторизации (Шаг №2)"""
        return self.get_text(self.USER_NAME_LABEL)

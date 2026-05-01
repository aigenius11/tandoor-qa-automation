from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10) # Ожидание элементов до 10 секунд

    def open_url(self, url):
        """Открывает указанный URL"""
        self.driver.get(url)

    def find_element(self, locator):
        """Находит элемент, дождавшись его появления"""
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        """Дожидается кликабельности элемента и нажимает на него"""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def enter_text(self, locator, text):
        """Очищает поле и вводит текст"""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        """Возвращает текст элемента"""
        return self.find_element(locator).text
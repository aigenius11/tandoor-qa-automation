import requests
import os
from dotenv import load_dotenv
from requests.exceptions import JSONDecodeError


# Загружаем переменные окружения
load_dotenv()

class TandoorAPIClient:
    def __init__(self, base_url=None, token=None):
        if token:
            self.token = token
        else:
            self.token = token or  os.getenv("TANDOOR_TOKEN")
        # Подсказка Шаг №4: инициализация атрибутов
        self.base_url =  (base_url or os.getenv("BASE_URL", "")).strip("/")
        self.session = requests.Session()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }



    def import_recipe(self, recipe_url):
        endpoint = "recipe-from-source/"
        data = {
            "url": recipe_url,
            "data": "",
            "bookmarklet": 0
        }

        response = self._make_request(method="POST", endpoint=endpoint, data=data)

        if response and response.status_code in [200, 201]:
            result_data = response.json()

            # Шаг от куратора: сначала ищем в recipe_id
            recipe_id = result_data.get("recipe_id")

            # Если там пусто, ищем в списке duplicates
            if not recipe_id:
                duplicates = result_data.get("duplicates", [])
                if duplicates:
                    recipe_id = duplicates[0]  # Берем первый ID из списка

            if recipe_id:
                print(f"SUCCESS | ID: {recipe_id} | URL: {recipe_url}")
                return recipe_id

        print(f"FAILURE | Не удалось получить ID для: {recipe_url}")
        return None

    def _make_request(self, method, endpoint, data=None):
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"


        try:
            # Используем json=data для автоматической конвертации в JSON
            response = requests.request(method, url, json=data, headers=self.get_headers(), cookies={})
            print(f"DEBUG: Status: {response.status_code} | Body: {response.text}")

            return response
        except Exception as e:
            print(f"CRITICAL ERROR: Connection failed {e}")
            return None

    def get_all_recipes(self):
        """Запрашивает список рецептов (для проверки связи)."""
        return self._make_request("GET", "recipe/")

    def test_connection(self):
        """Метод из подсказки Шаг №4 для проверки работы"""
        print("Testing API connection...")
        recipes = self.get_all_recipes()
        if recipes is not None:
            print("STATUS: SUCCESS")
            # Если recipes — это список, выводим его длину
            count = recipes.get('count', len(recipes)) if isinstance(recipes, dict) else len(recipes)
            print(f"Recipes found: {count}")
        else:
            print("STATUS: FAILED")

    def get_recipe_by_id(self, recipe_id):
        """Получить конкретный рецепт по его ID"""
        endpoint = f"recipes/{recipe_id}/"
        # Используем твой базовый метод для запроса
        return self._make_request(method="GET", endpoint=endpoint)

    def delete_recipe(self, recipe_id):
        """Удалить рецепт по его ID (обязательно для Шага №5)"""
        endpoint = f"recipes/{recipe_id}/"
        url = f"{self.base_url}/{endpoint}"
        # Отправляем DELETE запрос
        return requests.delete(url, headers=self.get_headers())

    def get_headers(self):
        """Вспомогательная функция для формирования заголовков (Шаг №6)"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def create_meal_plan(self, recipe_id, date):
        # Данные строго по схеме из вашего OpenAPI файла
        payload = {
            "recipe": int(recipe_id),
            "date": date,
            "slot": 1,
            "servings": 1  # Добавили обязательное поле из схемы
        }

        response = self.session.post(f"{self.base_url}/api/mealplan/", json=payload)

        if response.status_code != 201:
            # Теперь мы выводим точный ответ сервера, если что-то не так
            print(f"Ошибка API Tandoor: {response.status_code}")
            print(f"Детали: {response.text}")
            response.raise_for_status()

        return response.json()

# В директории "main" создаем экземпляр и вызываем проверку
if __name__ == "__main__":
    client = TandoorAPIClient()
    client.test_connection()
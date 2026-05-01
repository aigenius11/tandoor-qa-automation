import requests
import os
import allure
from dotenv import load_dotenv


load_dotenv()


class TandoorAPIClient:
    def __init__(self, base_url=None, token=None):
        # Приоритет: аргументы функции -> переменные окружения
        self.token = token or os.getenv("TANDOOR_TOKEN")
        self.base_url = (base_url or os.getenv("BASE_URL", "")).strip("/")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _make_request(self, method, endpoint, data=None):
        """Вспомогательный метод для всех запросов"""
        with allure.step(f"API Request: {method} {endpoint}"):
            url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(method, url, json=data)
            print(f"DEBUG: {method} {url} | Status: {response.status_code}")
            return response
        except Exception as e:
            print(f"CRITICAL ERROR: Connection failed {e}")
            return None

    # --- РЕЦЕПТЫ ---
    def get_all_recipes(self):
        return self._make_request("GET", "recipe/recipes/")

    def get_recipe_by_id(self, recipe_id):
        return self._make_request("GET", f"recipe/recipes/{recipe_id}/")

    def import_recipe(self, recipe_url):
        """Импорт рецепта с обработкой дубликатов"""
        endpoint = "recipe/recipe-from-source/"
        data = {"url": recipe_url, "data": "", "bookmarklet": 0}
        response = self._make_request("POST", endpoint, data=data)

        if response and response.status_code in [200, 201]:
            result = response.json()
            # Пытаемся взять ID нового рецепта или первого из списка дубликатов
            recipe_id = result.get("recipe_id") or (result.get("duplicates") or [None])[0]
            if recipe_id:
                print(f"SUCCESS | ID: {recipe_id} | URL: {recipe_url}")
                return recipe_id
        print(f"FAILURE | Не удалось получить ID для: {recipe_url}")
        return None

    # --- ПЛАН ПИТАНИЯ (MEAL PLAN) ---
    def create_meal_plan(self, recipe_id, date):
        """Создание плана питания (Задание №3)"""
        endpoint = "mealplan/"
        payload = {
            "recipe": int(recipe_id),
            "date": date,
            "slot": 1,
            "servings": 1
        }
        return self._make_request("POST", endpoint, data=payload)

    def get_meal_plans(self):
        """Получение всех планов (обязательный метод)"""
        return self._make_request("GET", "mealplan/")

    def delete_meal_plan(self, plan_id):
        """Удаление плана (обязательный метод)"""
        return self._make_request("DELETE", f"mealplan/{plan_id}/")

    # --- СПИСОК ПОКУПОК (SHOPPING LIST) ---
    def get_shopping_lists(self):
        """Проверка списка покупок (обязательный метод)"""
        return self._make_request("GET", "shopping/shoppinglist/")

    # --- ТЕСТ СОЕДИНЕНИЯ ---
    def test_connection(self):
        print("Testing API connection...")
        res = self.get_all_recipes()
        if res and res.status_code == 200:
            print("STATUS: SUCCESS")
        else:
            print(f"STATUS: FAILED (Code: {res.status_code if res else 'No response'})")


if __name__ == "__main__":
    client = TandoorAPIClient()
    client.test_connection()
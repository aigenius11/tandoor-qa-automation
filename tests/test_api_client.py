import pytest
import allure
from api.client import TandoorAPIClient

# Глобальная маркировка
pytestmark = [pytest.mark.api, allure.epic("API Tests"), allure.feature("Recipe Management")]

@pytest.mark.api
@allure.story("Get Recipes List")
@allure.title("Проверка базовой доступности списка рецептов")
def test_get_all_recipes_status(api_client):
    with allure.step("Запрос списка всех рецептов"):
        response = api_client.get_all_recipes()

    with allure.step("Проверка статус-кода 200"):
        assert response.status_code == 200, f"Ошибка! Статус: {response.status_code}"


@allure.story("Specific Recipe")
@allure.title("Проверка получения рецепта по конкретному ID")
def test_check_specific_recipe(api_client, recipe_id):
    endpoint = f"recipe/{recipe_id}/"

    with allure.step(f"Запрос рецепта с ID {recipe_id}"):
        response = api_client._make_request(method="GET", endpoint=endpoint)

    with allure.step("Проверка успешности ответа и соответствия ID"):
        assert response.status_code == 200, f"Рецепт с ID {recipe_id} не найден"
        data = response.json()
        assert data.get("id") == recipe_id, "ID в ответе не совпадает с запрошенным"


@allure.story("Security")
@allure.title("Проверка защиты API (Invalid Token)")
@pytest.mark.security
def test_api_unauthorized():
    with allure.step("Инициализация клиента с неверным токеном"):
        bad_client = TandoorAPIClient(token="invalid_token_123")

    with allure.step("Попытка запроса данных"):
        response = bad_client.get_all_recipes()

    with allure.step("Проверка получения ошибки доступа (401/403)"):
        assert response.status_code in [401, 403], f"Сервер не отклонил запрос: {response.status_code}"


@allure.story("Get Recipes List")
@allure.title("Проверка структуры данных списка рецептов")
def test_get_recipes_list_structure(api_client):
    with allure.step("Запрос списка рецептов"):
        response = api_client.get_all_recipes()

    with allure.step("Проверка наличия поля 'results' и типа данных"):
        data = response.json()
        assert "results" in data, "Поле 'results' отсутствует"
        assert isinstance(data["results"], list), "Результаты должны быть списком"


@allure.story("Recipe Creation")
@allure.title("Проверка импорта рецепта по внешней ссылке")
def test_create_recipe(api_client):
    recipe_url = "https://1000.menu/cooking/109088-pechene-v-aerogrile"

    with allure.step(f"Импорт рецепта по URL: {recipe_url}"):
        recipe_id = api_client.import_recipe(recipe_url)

    with allure.step("Проверка получения валидного ID после создания"):
        assert recipe_id is not None, "ID рецепта не получен"
        assert isinstance(recipe_id, int), "ID должен быть числом"


@allure.story("Recipe Deletion")
@allure.title("Проверка удаления рецепта")
def test_delete_recipe(api_client, recipe_id):
    with allure.step(f"Запрос на удаление рецепта с ID {recipe_id}"):
        response = api_client.delete_recipe(recipe_id)

    with allure.step("Проверка допустимых статус-кодов (200, 204, 403)"):
        allowed_status_codes = [200, 204, 403]
        assert response.status_code in allowed_status_codes
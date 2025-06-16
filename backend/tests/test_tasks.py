import pytest
from httpx import AsyncClient
from fastapi import status

pytestmark = pytest.mark.asyncio

async def get_auth_token(async_client: AsyncClient, email: str, password: str) -> str:
    response = await async_client.post(
        "/api/auth/token",
        data={"username": email, "password": password}
    )
    assert response.status_code == status.HTTP_200_OK, "Failed to get auth token"
    return response.json()["access_token"]

class TestTaskRoutesWithAuth:
    @pytest.fixture(scope="function", autouse=True)
    async def setup_users_and_token(self, async_client: AsyncClient):
        creator_email = "task_creator@example.com"
        creator_password = "password123"

        user_response = await async_client.post(
            "/api/users/",
            json={"email": creator_email, "first_name": "Создатель", "last_name": "Задач", "password": creator_password}
        )
        assert user_response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

        self.token = await get_auth_token(async_client, creator_email, creator_password)
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    async def test_create_task_unauthenticated(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/tasks/",
            json={"title": "Попытка без токена", "type": "testing"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_task_success(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/tasks/",
            headers=self.auth_headers,
            json={
                "title": "Очень важная задача",
                "description": "Сделать что-то очень важное",
                "type": "development",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Очень важная задача"
        assert data["creator"]["email"] == "task_creator@example.com"

    async def test_get_tasks_authenticated(self, async_client: AsyncClient):
        response = await async_client.get("/api/tasks/", headers=self.auth_headers)
        assert response.status_code == status.HTTP_200_OK

    async def test_get_and_delete_task(self, async_client: AsyncClient):
        create_response = await async_client.post(
            "/api/tasks/",
            headers=self.auth_headers,
            json={"title": "Задача на удаление", "type": "documentation"},
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        task_id = create_response.json()["id"]

        get_response = await async_client.get(f"/api/tasks/{task_id}", headers=self.auth_headers)
        assert get_response.status_code == status.HTTP_200_OK

        # ИСПРАВЛЕНО: Проверяем, что эндпоинт возвращает 204 No Content
        delete_response = await async_client.delete(f"/api/tasks/{task_id}", headers=self.auth_headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        get_after_delete_response = await async_client.get(f"/api/tasks/{task_id}", headers=self.auth_headers)
        assert get_after_delete_response.status_code == status.HTTP_404_NOT_FOUND
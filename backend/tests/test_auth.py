import pytest
from httpx import AsyncClient
from fastapi import status

# Пометка для pytest-asyncio, что все тесты в файле асинхронные
pytestmark = pytest.mark.asyncio


class TestAuthRoutes:
    """Тесты для эндпоинтов /users/ и /auth/token."""

    async def test_create_user_success(self, async_client: AsyncClient):
        """Тест успешного создания пользователя."""
        response = await async_client.post(
            "/api/users/",
            json={
                "email": "test@example.com",
                "first_name": "Тест",
                "last_name": "Тестов",
                "password": "a_strong_password",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "hashed_password" not in data

    async def test_create_user_duplicate_email(self, async_client: AsyncClient):
        """Тест ошибки при попытке создать пользователя с существующим email."""
        await async_client.post(
            "/api/users/",
            json={
                "email": "duplicate@example.com",
                "first_name": "Дубль",
                "last_name": "Один",
                "password": "password123",
            },
        )
        response = await async_client.post(
            "/api/users/",
            json={
                "email": "duplicate@example.com",
                "first_name": "Дубль",
                "last_name": "Два",
                "password": "password456",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    async def test_login_success(self, async_client: AsyncClient):
        """Тест успешного входа и получения JWT токена."""
        email = "login_test@example.com"
        password = "my_super_password"
        await async_client.post(
            "/api/users/",
            json={
                "email": email,
                "first_name": "Логин",
                "last_name": "Тест",
                "password": password,
            },
        )

        login_response = await async_client.post(
            "/api/auth/token",
            data={"username": email, "password": password},
        )
        assert login_response.status_code == status.HTTP_200_OK
        data = login_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.parametrize(
        "username, password, expected_status, expected_detail",
        [
            ("wrong@example.com", "any_password", status.HTTP_401_UNAUTHORIZED, "Incorrect email or password"),
            ("login_test@example.com", "wrong_password", status.HTTP_401_UNAUTHORIZED, "Incorrect email or password"),
        ],
    )
    async def test_login_failure(
        self, async_client: AsyncClient, username, password, expected_status, expected_detail
    ):
        """Тест неудачных попыток входа (неверный логин или пароль)."""
        await async_client.post(
            "/api/users/",
            json={
                "email": "login_test_for_fail@example.com", # Используем другой email, чтобы не конфликтовать с другими тестами
                "first_name": "Логин",
                "last_name": "Тест",
                "password": "my_super_password",
            },
        )

        response = await async_client.post(
            "/api/auth/token",
            data={"username": username, "password": password},
        )
        assert response.status_code == expected_status
        # ИСПРАВЛЕНО: Убрана лишняя часть 'import pytest'
        assert expected_detail in response.json()["detail"]
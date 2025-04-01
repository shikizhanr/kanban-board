import pytest
from fastapi import status
from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings

def test_register_user(client):
    """Тест регистрации нового пользователя"""
    # Сначала удалим пользователя, если он существует
    response = client.post("/auth/login", json={"username": "newuser", "password": "newpass123"})
    if response.status_code == 200:
        # Пользователь существует, удалим его
        db = next(client.app.dependency_overrides[get_db]())
        db.query(User).filter(User.username == "newuser").delete()
        db.commit()
    
    user_data = {
        "username": "newuser",
        "first_name": "New",
        "last_name": "User",
        "password": "newpass123"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
    assert response.json()["username"] == "newuser"

def test_register_existing_user(client, test_user):
    """Тест попытки регистрации существующего пользователя"""
    user_data = {
        "username": test_user["username"],
        "first_name": "Test",
        "last_name": "User",
        "password": "testpass123"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"]

def test_login_user(client, test_user):
    """Тест успешного входа"""
    response = client.post(
        "/auth/login",
        json={"username": test_user["username"], "password": "testpass123"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

def test_login_invalid_credentials(client, test_user):
    """Тест входа с неверными учетными данными"""
    # Неверный пароль
    response = client.post(
        "/auth/login",
        json={"username": test_user["username"], "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_refresh_token(auth_client, test_user):
    """Тест обновления токена"""
    response = auth_client.post(
        "/auth/refresh-token",
        json={"username": test_user["username"]}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

def test_change_password_success(auth_client, test_user, client):
    """Тест успешной смены пароля"""
    response = auth_client.put(
        "/auth/change-password",
        json={
            "username": test_user["username"],
            "current_password": "testpass123",
            "new_password": "newsecurepass123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Проверяем новый пароль
    login_response = client.post(
        "/auth/login",
        json={"username": test_user["username"], "password": "newsecurepass123"}
    )
    assert login_response.status_code == status.HTTP_200_OK

def test_expired_token(client, test_user):
    """Тест с просроченным токеном"""
    expired_token = jwt.encode(
        {"sub": test_user["username"], "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    response = client.put(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {expired_token}"},
        json={
            "username": test_user["username"],
            "current_password": "testpass123",
            "new_password": "newpass123"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
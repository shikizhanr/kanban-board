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

@pytest.mark.parametrize(
    "username, password, expected_status_code, error_detail_contains",
    [
        ("testuser", "wrongpassword", status.HTTP_401_UNAUTHORIZED, "Incorrect username or password"), # Assuming test_user fixture creates "testuser"
        ("nonexistentuser", "anypassword", status.HTTP_401_UNAUTHORIZED, "Incorrect username or password"),
        (None, "testpass123", status.HTTP_422_UNPROCESSABLE_ENTITY, None), # Missing username
        ("testuser", None, status.HTTP_422_UNPROCESSABLE_ENTITY, None), # Missing password
    ]
)
def test_login_various_scenarios(client, test_user, username, password, expected_status_code, error_detail_contains):
    # test_user fixture ensures "testuser" with "testpass123" exists
    payload = {}
    if username is not None:
        payload["username"] = username
    if password is not None:
        payload["password"] = password

    # If username in payload is None, use the actual test_user's username for other cases
    # This logic seems a bit off for the None case, let's adjust.
    # If username for the test case is None, it means we are testing missing username.
    # If username is "testuser", it refers to the one created by test_user fixture.

    actual_payload_username = test_user["username"] if username == "testuser" else username

    final_payload = {}
    if actual_payload_username is not None: # For missing username test, this will be None
        final_payload["username"] = actual_payload_username
    if password is not None:
        final_payload["password"] = password

    # Handle case where username itself is being tested as None (missing)
    if username is None and "username" in final_payload: # Should not happen if username is None
        del final_payload["username"]


    response = client.post("/auth/login", json=final_payload)
    assert response.status_code == expected_status_code
    if error_detail_contains:
        assert error_detail_contains in response.json()["detail"]
    elif expected_status_code == status.HTTP_422_UNPROCESSABLE_ENTITY: # For missing fields
        assert "detail" in response.json() # Check that there's some detail



# Parametrized test for registration validation
@pytest.mark.parametrize(
    "user_data_override, expected_status_code, error_detail_part",
    [
        ({"username": "u"}, status.HTTP_422_UNPROCESSABLE_ENTITY, "username"), # Username too short (hypothetical, depends on actual validation) - current schema pattern ^[a-zA-Z0-9_]+$
        ({"username": "user n@me"}, status.HTTP_422_UNPROCESSABLE_ENTITY, "username"), # Invalid username pattern
        ({"password": "short"}, status.HTTP_422_UNPROCESSABLE_ENTITY, "password"), # Password too short
        ({"first_name": "F"}, status.HTTP_422_UNPROCESSABLE_ENTITY, "first_name"), # First name too short
        ({"last_name": "L"}, status.HTTP_422_UNPROCESSABLE_ENTITY, "last_name"),   # Last name too short
        ({"username": None}, status.HTTP_422_UNPROCESSABLE_ENTITY, "username"), # Missing username
        ({"password": None}, status.HTTP_422_UNPROCESSABLE_ENTITY, "password"), # Missing password
        ({"first_name": None}, status.HTTP_422_UNPROCESSABLE_ENTITY, "first_name"), # Missing first_name
        ({"last_name": None}, status.HTTP_422_UNPROCESSABLE_ENTITY, "last_name"), # Missing last_name
    ]
)
def test_register_invalid_data(client, user_data_override, expected_status_code, error_detail_part):
    base_user_data = {
        "username": "validuserreg", # Needs to be unique for each parametrized run if not cleaned
        "first_name": "ValidFirst",
        "last_name": "ValidLast",
        "password": "validpassword123"
    }

    # Ensure username is unique for each test run to avoid "already registered" if previous run failed mid-way
    # or if this test is retried. A simple way is to append a unique suffix or use a counter.
    # For now, we assume each parameter set is distinct enough or tests are isolated.
    # If username is being overridden to an invalid one, use that.
    if "username" in user_data_override and user_data_override["username"] != "u" and user_data_override["username"] != "user n@me" and user_data_override["username"] is not None:
         base_user_data["username"] = f"{base_user_data['username']}_{user_data_override.get('username', 'param')}"


    invalid_data = base_user_data.copy()
    # Apply the override. If a value is None, it means we test its absence.
    for key, value in user_data_override.items():
        if value is None:
            if key in invalid_data: # Remove if testing missing field
                del invalid_data[key]
        else:
            invalid_data[key] = value # Override with specific invalid value

    response = client.post("/auth/register", json=invalid_data)
    assert response.status_code == expected_status_code

    if error_detail_part: # Check if the error message contains reference to the problematic field
        error_json = response.json()
        if isinstance(error_json.get("detail"), list): # Pydantic validation errors are lists of dicts
            assert any(error_detail_part in error.get("loc", [])[-1] for error in error_json["detail"]), \
                   f"Expected error detail to mention '{error_detail_part}', got: {error_json['detail']}"
        elif isinstance(error_json.get("detail"), str): # Simpler error string
             assert error_detail_part in error_json["detail"]



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
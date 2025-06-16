import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем корень проекта в PYTHONPATH
# project_root = Path(__file__).parent.parent.parent.parent # Assuming backend is already in PYTHONPATH or tests are run from root
# sys.path.append(str(project_root))
# Assuming 'app' is directly importable if tests are run correctly (e.g. with PYTHONPATH=.)
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.task import Task # For cleaning up tasks
from fastapi import status # For status codes

# Настройка тестовой БД SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для создания и удаления тестовой БД"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def db_session(setup_database):
    """Фикстура для работы с тестовой БД"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client(db_session):
    """Фикстура тестового клиента FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="module")
def test_user_data():
    """Данные тестового пользователя"""
    return {
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpass123"
    }

@pytest.fixture(scope="module")
def test_user(client, test_user_data, db_session):
    """Фикстура создания тестового пользователя"""
    # Очищаем таблицу пользователей перед тестами
    db_session.query(User).delete()
    db_session.commit()
    
    # Регистрируем пользователя
    response = client.post("/auth/register", json=test_user_data)
    
    # Если пользователь уже существует, логинимся
    if response.status_code != 200:
        response = client.post(
            "/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
    
    assert response.status_code == 200
    return response.json()

@pytest.fixture(scope="module")
def auth_client(client, test_user):
    """Фикстура авторизованного клиента"""
    # Логинимся чтобы получить токен
    login_data = {
        "username": test_user["username"],
        "password": "testpass123"
    }
    response = client.post("/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    # Создаем авторизованный клиент
    # client.headers.update({"Authorization": f"Bearer {token}"}) # Modifies client in-place, affecting other fixtures if not careful
    # Return a new client or a client wrapper to avoid shared state for headers
    authed_client = TestClient(app)
    authed_client.headers.update({"Authorization": f"Bearer {token}"})
    authed_client.app.dependency_overrides = client.app.dependency_overrides.copy()
    return authed_client

@pytest.fixture(scope="module")
def test_user2_data():
    return {
        "username": "testuser2",
        "first_name": "Test",
        "last_name": "UserTwo",
        "password": "testpass123"
    }

@pytest.fixture(scope="module")
def test_user2(client, test_user2_data, db_session):
    # Ensure a clean slate for this user if running tests multiple times
    existing_user = db_session.query(User).filter(User.username == test_user2_data["username"]).first()
    if existing_user:
        # For simplicity, if user exists, we assume they were created by a previous run of this fixture
        # and we can proceed to login for the auth_client_user2.
        # A more robust approach might involve deleting and recreating or ensuring idempotent creation.
        # Here, we'll try to fetch their details as if they were just registered.
        # This part is tricky because the original fixture returns response.json() which includes a token for registration.
        # Let's adjust to ensure the user exists and then auth_client_user2 handles login.
        # For this fixture, just ensure the user record exists.
        db_session.delete(existing_user) # Clean up to ensure fresh registration
        db_session.commit()


    response = client.post("/auth/register", json=test_user2_data)
    # This assertion was too strict before, registration gives 200 or 201 usually.
    # And login (if user existed) would be 200.
    # The original test_user fixture had mixed logic for register/login.
    # Let's simplify: this fixture *ensures* user2 is registered.
    if response.status_code == status.HTTP_400_BAD_REQUEST and "already registered" in response.json().get("detail", ""):
        # This case means user existed despite cleanup attempt or due to parallel test runs.
        # For this fixture, we'll consider it "ok" and auth_client_user2 will login.
        # Return the existing user's data.
        return db_session.query(User).filter(User.username == test_user2_data["username"]).first() # Return User model instance

    assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED], f"Failed to register test_user2: {response.text}"
    # Return the user data from the response (which might include token, etc., depending on /register endpoint)
    # Or fetch the user from DB to return a consistent User model instance
    user_model = db_session.query(User).filter(User.username == test_user2_data["username"]).first()
    assert user_model is not None, "User2 not found in DB after registration attempt."
    return user_model


@pytest.fixture(scope="module")
def auth_client_user2(client, test_user2_data, test_user2): # test_user2 fixture ensures user exists
    login_data = {
        "username": test_user2_data["username"],
        "password": test_user2_data["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK, f"Failed to log in test_user2 for auth_client_user2: {response.text}"
    token = response.json()["access_token"]

    authed_client = TestClient(app)
    authed_client.headers.update({"Authorization": f"Bearer {token}"})
    authed_client.app.dependency_overrides = client.app.dependency_overrides.copy()
    return authed_client


@pytest.fixture(scope="function")
def test_task(auth_client, db_session, test_user_data): # Added test_user_data for username
    user = db_session.query(User).filter(User.username == test_user_data["username"]).first()
    if not user:
        pytest.fail(f"Default test user '{test_user_data['username']}' not found for creating test_task.")

    # Clean tasks for this specific user to avoid interference between tests
    db_session.query(Task).filter(Task.author_id == user.id).delete()
    db_session.commit()

    task_data = {
        "title": "Test Task for Fixture",
        "description": "A task created by a fixture",
        "task_profile": "GENERAL",
        "status": "PLANNED"
    }
    response = auth_client.post("/tasks/", json=task_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Failed to create task for fixture: {response.text}"
    return response.json()
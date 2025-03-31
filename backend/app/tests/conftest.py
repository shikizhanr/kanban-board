import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models.user import User

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
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
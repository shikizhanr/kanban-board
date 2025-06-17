import pytest
import os # Added import
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# --- ВАЖНО: Загружаем переменные окружения из .env файла ---
# Это нужно сделать ДО импорта кода вашего приложения (app.main).
from dotenv import load_dotenv
load_dotenv()
# --- КОНЕЦ ВАЖНОЙ ЧАСТИ ---

# Используем SQLite в памяти для тестов
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL # Set DATABASE_URL for the app code

# Теперь, когда переменные загружены, импорт пройдет успешно
from app.main import app
from app.db.session import Base, get_db


engine = create_async_engine(TEST_DATABASE_URL, echo=True) # This engine is for test session management
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def override_get_db(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session
    return _override_get_db

@pytest.fixture(scope="function")
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app) 
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
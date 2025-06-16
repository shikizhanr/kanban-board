import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Загружаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем асинхронный "движок" для SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем фабрику сессий, которая будет создавать новые сессии для каждого запроса
# expire_on_commit=False - важно для асинхронного кода, чтобы объекты были доступны после коммита
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Базовый класс для всех ваших моделей SQLAlchemy
Base = declarative_base()

# Зависимость для FastAPI, которая предоставляет сессию в эндпоинты
async def get_db() -> AsyncSession:
    """
    Эта функция-генератор создает и предоставляет сессию базы данных для каждого запроса,
    а затем закрывает ее после выполнения запроса.
    """
    async with SessionLocal() as session:
        yield session
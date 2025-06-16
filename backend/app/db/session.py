import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)


SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    """
    Эта функция-генератор создает и предоставляет сессию базы данных для каждого запроса,
    а затем закрывает ее после выполнения запроса.
    """
    async with SessionLocal() as session:
        yield session
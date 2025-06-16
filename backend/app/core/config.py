from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    """
    Класс настроек приложения, загружающий переменные из .env файла.
    """
    PROJECT_NAME: str = "Task Management Backend"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str # Секретный ключ для JWT
    ALGORITHM: str = "HS256" # Алгоритм для JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 # Время жизни токена доступа в минутах
    DATABASE_URL: str # URL базы данных для основного приложения
    TEST_DATABASE_URL: str # URL базы данных для тестов

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Создаем экземпляр настроек
settings = Settings()
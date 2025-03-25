from pydantic import BaseSettings


class Settings(BaseSettings):
    # Настройки приложения
    APP_NAME: str = "Task Manager API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True  # Режим отладки

    # Настройки базы данных


    # JWT-аутентификация



settings = Settings()
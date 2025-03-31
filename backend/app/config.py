from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    jwt_secret_key: str = "default-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_user: str = "postgres"
    postgres_password: str = ""
    postgres_db: str = "myapp"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'

settings = Settings()
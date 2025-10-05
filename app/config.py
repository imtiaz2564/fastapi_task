import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME", "FastAPI Task App")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "True").lower() == "true"
    APP_PORT: int = int(os.getenv("APP_PORT", 8000))
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")

    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_NAME: str = os.getenv("DB_NAME")

    # Automatically detect if running locally (not in Docker)
    @property
    def DATABASE_URL(self) -> str:
        host = self.DB_HOST
        # if DB_HOST is "db" but there's no Docker env var, assume local
        if host == "db" and not os.path.exists("/.dockerenv"):
            host = "localhost"
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{host}:{self.DB_PORT}/{self.DB_NAME}"

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    STATIC_IMAGE_PATH: str = os.getenv("STATIC_IMAGE_PATH")
    GENERATED_PDF_DIR: str = os.getenv("GENERATED_PDF_DIR")

settings = Settings()

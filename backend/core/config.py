import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Car Import AI"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/car_import_ai")

    class Config:
        case_sensitive = True

settings = Settings()

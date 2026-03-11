import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Car Import AI"
    DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.fenlzmyffahriefuljom:TuateamAdmin12@aws-1-eu-west-2.pooler.supabase.com:5432/postgres"
)

    class Config:
        case_sensitive = True

settings = Settings()

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Car Import AI"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres.fenlzmyffahriefuljom:p6JmSE8wTDPZkkDS@aws-1-eu-west-2.pooler.supabase.com:6543/postgres"
    )
    
    # Auth Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "7aa2f8e1c6b5d4e3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week

    class Config:
        case_sensitive = True

settings = Settings()

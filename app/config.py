from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/punerakshak"
    openweather_api_key: Optional[str] = "demo"
    
    class Config:
        env_file = ".env"

settings = Settings()

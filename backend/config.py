from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Track Atlas"

    class Config:
        env_file = ".env"
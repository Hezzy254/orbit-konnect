from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Orbit Konnect"
    APP_VERSION: str = "0.1.0"

    DEBUG: bool = True

    SECRET_KEY: str = "change-this-secret-key"

    DATABASE_URL: str = "sqlite:///orbit_konnect.db"

    MIKROTIK_HOST: str = "192.168.88.1"
    MIKROTIK_USERNAME: str = "admin"
    MIKROTIK_PASSWORD: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
from datetime import timedelta

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from .env
    """

    # Application
    APP_NAME: str = "Orbit Konnect"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # MikroTik
    MIKROTIK_HOST: str
    MIKROTIK_USERNAME: str
    MIKROTIK_PASSWORD: str

    @property
    def ACCESS_TOKEN_EXPIRE(self) -> timedelta:
        return timedelta(
            minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
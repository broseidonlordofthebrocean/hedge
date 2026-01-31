from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "HEDGE API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://hedge:hedge_dev@localhost:5432/hedge"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Security
    secret_key: str = "dev-secret-change-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: str = "http://localhost:3000"

    # External APIs
    polygon_api_key: str = ""
    fred_api_key: str = ""
    sec_user_agent: str = "HEDGE contact@hedge.finance"

    # Clerk Auth
    clerk_secret_key: str = ""
    clerk_webhook_secret: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()

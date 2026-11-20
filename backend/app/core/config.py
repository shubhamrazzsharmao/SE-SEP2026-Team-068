from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase Postgres connection string (SQLAlchemy URL, psycopg driver)
    database_url: str = "sqlite:///./dev.db"

    # Supabase Auth: set SUPABASE_URL for projects using asymmetric JWT signing keys
    # (verified through the project's JWKS endpoint); set SUPABASE_JWT_SECRET for
    # projects still on the legacy shared secret (HS256).
    supabase_url: str = ""
    supabase_jwt_secret: str = ""

    llm_provider: str = "fake"  # fake | gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # DEBUG also logs /health checks; INFO logs requests, sign-ins and activity; WARNING only problems.
    log_level: str = "INFO"

    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    # Local SQLite development only. On Supabase the tables come from supabase/schema.sql.
    auto_create_tables: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()

from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _to_asyncpg_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    DATABASE_URL: str
    CAPASHINO_BASE_URL: str
    CAPASHINO_API_KEY: str

    @model_validator(mode="before")
    @classmethod
    def assemble_database_url(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        database_url = data.get("DATABASE_URL")
        if database_url:
            data["DATABASE_URL"] = _to_asyncpg_url(database_url)
            return data

        connection_string = data.get("POSTGRES_CONNECTION_STRING")
        if connection_string:
            data["DATABASE_URL"] = _to_asyncpg_url(connection_string)
            return data

        host = data.get("POSTGRES_HOST")
        username = data.get("POSTGRES_USERNAME")
        password = data.get("POSTGRES_PASSWORD")
        database_name = data.get("POSTGRES_DATABASE_NAME")
        if host and username and password and database_name:
            port = data.get("POSTGRES_PORT", 5432)
            data["DATABASE_URL"] = (
                f"postgresql+asyncpg://{quote_plus(username)}:{quote_plus(password)}"
                f"@{host}:{port}/{database_name}"
            )
            return data

        return data


settings = Settings()

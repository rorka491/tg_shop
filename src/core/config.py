from pathlib import Path

from pydantic import PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict


base_dir = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    upload_dir: Path = base_dir / "uploads" / "preview"

    service_password: str

    debug: bool = True

    telegram_token: str

    postgres_user: str = "rodion"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "tg_shop"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    _postgres_url: str | None = PrivateAttr(default=None)
    _redis_url: str | None = PrivateAttr(default=None)

    @property
    def postgres_url(self) -> str:
        if self._postgres_url is None:
            self._postgres_url = (
                f"postgresql+asyncpg://"
                f"{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}"
                f"/{self.postgres_db}"
            )

        return self._postgres_url

    @property
    def redis_url(self) -> str:
        if self._redis_url is None:
            self._redis_url = (
                f"redis://{self.redis_host}:"
                f"{self.redis_port}/{self.redis_db}"
            )

        return self._redis_url


settings = Settings() # type: ignore
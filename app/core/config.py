from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Image Auth Gallery API"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    mysql_user: str = "root"
    mysql_password: str = "root"
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str = "gallery_db"

    uploads_dir: str = "uploads"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

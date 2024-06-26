from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


class Settings(BaseSettings):
    postgres_url: PostgresDsn

    class Config:
        env_file = ".env"
        env_prefix = "env_"

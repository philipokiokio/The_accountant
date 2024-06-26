from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


class Settings(BaseSettings):
    postgres_url: PostgresDsn
    jwt_secret_key: str
    ref_jwt_secret_key: str
    second_signer_key: str

    class Config:
        env_file = ".env"
        env_prefix = "env_"

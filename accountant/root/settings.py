from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn


class Settings(BaseSettings):
    postgres_url: PostgresDsn
    redis_url: RedisDsn
    jwt_secret_key: str
    ref_jwt_secret_key: str
    second_signer_key: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: str
    mail_server: str
    mail_from_name: str

    class Config:
        env_file = ".env"
        env_prefix = "env_"

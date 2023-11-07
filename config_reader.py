from pydantic import SecretStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv('config.env')


class Settings(BaseSettings):
    client_id: SecretStr
    client_secret: SecretStr
    redirect_uri: SecretStr
    subdomain: SecretStr
    db_id: SecretStr
    enum_db_id: SecretStr
    secret: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()

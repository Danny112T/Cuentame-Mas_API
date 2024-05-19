from os import environ
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_TITLE: str = "Cuentame+ GraphQL API"
    PROJECT_VERSION: str = "0.0.1"
    MONGO_HOST: str = environ.get("DB_HOST")
    MONGO_PORT: str = environ.get("DB_PORT")
    MONGO_DB: str = environ.get("DB_DATABASE")
    MONGO_URI: str = environ.get("DB_URI", "mongodb://{MONGO_HOST}:{MONGO_PORT}")


settings = Settings()

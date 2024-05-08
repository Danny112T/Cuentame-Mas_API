import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_TITLE: str = "Cuentame+ GraphQL API"
    PROJECT_VERSION: str = "0.0.1"
    HOST: str = os.environ.get("HOST_URL")
    PORT: int = int(os.environ.get("HOST_PORT"))
    BASE_URL: str = HOST+":"+str(PORT)
    MONGO_HOST: str = os.environ.get("DB_HOST")
    MONGO_PORT: str = os.environ.get("DB_PORT")
    MONGO_DB: str = os.environ.get("DB_DATABASE")
    MONGO_URI: str = os.environ.get("DB_URI",'mongodb://{MONGO_HOST}:{MONGO_PORT}')
        
settings = Settings()
from fastapi_mail import ConnectionConfig
from pydantic import SecretStr
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

APP_NAME = config("APP_NAME", default="Cuentame+ GraphQL API")
APP_VERSION = config("APP_VERSION", default="0.0.1")
MONGO_HOST = config("MONGO_HOST", default="localhost")
MONGO_PORT = config("MONGO_PORT", default="27017")
MONGO_DB = config("DB_DATABASE", default="cuentamemas")

MONGO_URI = config("DB_URI", default=f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}")

JWT_SECRET: str = str(config("JWT_SECRET", cast=Secret))
ALGORITHM: str = str(config("ALGORITHM", default="HS256"))

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    config("ACCESS_TOKEN_EXPIRE_MINUTES", default="15000")
)
EMAIL_VAL: bool = bool(config("EMAIL_VALIDATION", default="False"))

email_conf = ConnectionConfig(
    MAIL_USERNAME=config("MAIL_USERNAME"),
    MAIL_PASSWORD=config("MAIL_PASSWORD", cast=SecretStr),
    MAIL_FROM=config("MAIL_FROM"),
    MAIL_PORT=config("MAIL_PORT", cast=int),
    MAIL_SERVER=config("MAIL_SERVER"),
    MAIL_FROM_NAME="Cuentame Más",
    MAIL_STARTTLS=config("MAIL_STARTTLS", cast=bool),
    MAIL_SSL_TLS=config("MAIL_SSL_TLS", cast=bool),
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

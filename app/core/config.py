from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

APP_NAME = config("APP_NAME", default="Cuentame+ GraphQL API")
APP_VERSION = config("APP_VERSION", default="0.0.1")
MONGO_HOST = config("MONGO_HOST", default="localhost")
MONGO_PORT = config("MONGO_PORT", default="27017")
MONGO_DB = config("DB_DATABASE", default="cuentamemas")

MONGO_URI = config("DB_URI", default=f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}")
# MONGO_URI = "mongodb+srv://iDannyT:dgrBNobBWy4vIXbR@clustersdmtp.g8faxeg.mongodb.net/?retryWrites=true&w=majority&appName=ClustersDMTP"

JWT_SECRET: str = str(config("JWT_SECRET", cast=Secret))
ALGORITHM: str = str(config("ALGORITHM", default="HS256"))

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    config("ACCESS_TOKEN_EXPIRE_MINUTES", default="15000")
)
EMAIL_VAL: bool = bool(config("EMAIL_VALIDATION", default="False"))

from pymongo import MongoClient
from app.core.config import MONGO_DB, MONGO_URI

name_db = MONGO_DB
mongo_uri = MONGO_URI
client = MongoClient(mongo_uri)
db = client[name_db]
try:
    client.admin.command("ping")
    print(
        f"You successfully connected to the database {name_db} in the uri {mongo_uri}"
    )
except Exception as e:
    print(e)

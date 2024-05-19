from pymongo import MongoClient
from app.config import settings

name_db = settings.MONGO_DB
mongo_uri = settings.MONGO_URI
client = MongoClient(settings.MONGO_URI)
db = client[name_db]
collection_name = db["users"]
try:
    client.admin.command("ping")
    print("You successfully connected to the database")
except Exception as e:
    print(e)

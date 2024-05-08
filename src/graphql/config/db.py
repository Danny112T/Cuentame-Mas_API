from pymongo import MongoClient
from src.graphql.config.core import settings

DB_NAME = settings.MONGO_DB

db = MongoClient(settings.MONGO_URI).DB_NAME

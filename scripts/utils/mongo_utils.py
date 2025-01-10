from pymongo import MongoClient
from config.settings import MONGO_CONFIG

def get_mongo_connection():
    client = MongoClient(
        host=MONGO_CONFIG["host"],
        port=MONGO_CONFIG["port"],
        username=MONGO_CONFIG["username"],
        password=MONGO_CONFIG["password"],
    )
    return client[MONGO_CONFIG["database"]]

def insert_document(collection_name, document):
    db = get_mongo_connection()
    collection = db[collection_name]
    collection.insert_one(document)

def fetch_documents(collection_name, query={}):
    db = get_mongo_connection()
    collection = db[collection_name]
    return list(collection.find(query))

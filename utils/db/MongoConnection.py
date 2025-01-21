from pymongo import MongoClient
from utils.config.settings import MONGO_CONFIG

class MongoConnection:
    _instance = None

    @staticmethod
    def get_instance():
        if MongoConnection._instance is None:
            MongoConnection._instance = MongoClient(
                host=MONGO_CONFIG["host"],
                port=MONGO_CONFIG["port"],
                username=MONGO_CONFIG["username"],
                password=MONGO_CONFIG["password"],
                maxPoolSize=10,
                replicaSet=MONGO_CONFIG.get("replicaSet")
            )
        return MongoConnection._instance[MONGO_CONFIG["database"]]

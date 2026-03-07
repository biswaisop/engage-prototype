from pymongo import MongoClient
from pymongo.collection import Collection
import os
from dotenv import load_dotenv

load_dotenv()



class MongoDB:
    _client: MongoClient = None

    @classmethod
    def get_client(cls) -> MongoClient:
        if cls._client is None:
            cls._client = MongoClient(os.getenv("MONGODB"))
        return cls._client

    @classmethod
    def get_collection(cls,  org_id: str, collection_name: str) -> Collection:
        client = cls.get_client()
        db = client[org_id]
        return db[collection_name]
    
    @classmethod
    def conversations(cls) -> Collection:
        return cls.get_collection("chats")
    
    @classmethod
    def leads(cls, org_id: str) -> Collection:
        return cls.get_collection(org_id,"leads")
    

# client = MongoClient(
#     os.getenv("MONGOURI"),
#     maxPoolSize=100,        # max concurrent connections
#     minPoolSize=5,          # keep 5 alive even when idle
#     serverSelectionTimeoutMS=5000  # fail fast if DB is unreachable
#     )



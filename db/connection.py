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
    def get_collection(cls, collection_name: str) -> Collection:
        client = cls.get_client()
        db = client[os.getenv("MONGODB-NAME", "hotel-chatbot")]
        return db[collection_name]
    
    @classmethod
    def conversations(cls) -> Collection:
        return cls.get_collection("chats")
    

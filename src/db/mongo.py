from pymongo import MongoClient
from src.config import MONGO_URI

_client = None


def get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client


def get_db():
    return get_client()["vetsalud"]


def close():
    global _client
    if _client:
        _client.close()
        _client = None

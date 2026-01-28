from pymongo import MongoClient
from config import MONGODB_URI, MONGODB_NAME

mongo_client = None
mongo_database = None

def connect_db():
    global mongo_client, mongo_database
    
    if mongo_client is None:
        mongo_client = MongoClient(MONGODB_URI)
        mongo_database = mongo_client[MONGODB_NAME]

    return mongo_database

def close_db():
    global mongo_client, mongo_database
    
    if mongo_client:
        mongo_client.close()
        mongo_client = None
        mongo_database = None

def init_db():
    db = connect_db()

    users = db["users"]
    users.create_index("username", unique=True)

import os
from pymongo import MongoClient
from utils.logger import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "analytixai")

try:
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    # Test connection
    client.server_info()
    logger.info("✅ MongoDB connected successfully")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {str(e)}")
    raise

# ✅ EXPOSE COLLECTIONS (THIS WAS MISSING)
users_collection = db["users"]
analysis_collection = db["analysis"]

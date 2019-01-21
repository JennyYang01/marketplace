# This module is to connect app with database.

from pymongo import MongoClient

# pymongo database client
pymongo_client = MongoClient("127.0.0.1", 27017)

# Access Marketplace database with markertplace_db
marketplace_db = pymongo_client["marketplace_db"]
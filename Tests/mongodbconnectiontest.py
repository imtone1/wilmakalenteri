# 
import os
from dotenv import load_dotenv

load_dotenv() # runs "export key=value" on all our key/value pairs in .env

# Tällä vaan testataan yhteyttä MongoDB:hen. Koodi on kopioitu MongoDB:n sivuilta.
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = os.environ["ATLAS_URI"]

def create_mongodb_connection(uri):
    
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return True

    except Exception as e:
        print(e)
        return False
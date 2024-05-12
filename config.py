from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
load_dotenv()
key=os.environ.get('mongodb_pass')
appName=os.environ.get('appName')
uri = f"mongodb+srv://jhachirag7:{key}@cluster0.rnfwq8t.mongodb.net/?retryWrites=true&w=majority&appName={appName}"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db=client.blog_db
collection=db['blog_data']
collection_user=db['blog_user']
collection_likes=db['blog_like']
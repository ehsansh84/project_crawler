from dotenv import load_dotenv
import os
load_dotenv()
# MONGO_URL = os.getenv('MONGO_URL')
# DB_NAME = os.getenv('DB_NAME')


def db():
    # print(f'MONGO_URL: {Settings.MONGO_URL}')
    from pymongo import MongoClient
    con = MongoClient(Settings.MONGO_URL)
    return con[Settings.DB_NAME]


def get_hash(string: str) -> str:
    import hashlib
    text_encoded = string.encode('utf-8')
    hashed_text = hashlib.sha256(text_encoded).hexdigest()
    return hashed_text


class Settings:
    MONGO_URL = os.environ.get('MONGO_URL')
    PROJECT_PATH = os.environ.get('PROJECT_PATH')
    UPLOAD_PATH = os.environ.get('UPLOAD_PATH')
    MEDIA_PATH = os.environ.get('MEDIA_PATH')
    DB_NAME = os.environ.get('DB_NAME')

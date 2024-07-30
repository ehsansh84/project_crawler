from dotenv import load_dotenv
import os
import hashlib
load_dotenv('.local_env')
load_dotenv()


def db():
    from tinydb import TinyDB, Query
    return TinyDB('db.json')


def mdb():
    from pymongo import MongoClient
    con = MongoClient(os.getenv('MONGO_URL'))
    return con[os.getenv('DB_NAME')]


def create_hash(s):
    hash_object = hashlib.sha256()
    hash_object.update(s.encode('utf-8'))
    return hash_object.hexdigest()


class Consts:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    TELEGRAM_USER_ID = os.getenv('TELEGRAM_USER_ID')

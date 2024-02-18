from dotenv import load_dotenv
load_dotenv()


def db():
    from tinydb import TinyDB, Query
    return TinyDB('db.json')

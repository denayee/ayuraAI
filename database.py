import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()


def get_db():
    conn = sqlite3.connect(os.getenv("SQLITE_DB_PATH"))
    conn.row_factory = sqlite3.Row
    return conn

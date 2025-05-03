#!C:/Users/kkari/AppData/Local/Programs/Python/Python312/python.exe
import sqlite3
import sys
import os
import json
from datetime import datetime

# Ensure stdout uses UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"C:\Apache24\htdocs\logs\flight_search.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return
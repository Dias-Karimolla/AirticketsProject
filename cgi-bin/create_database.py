import sqlite3
import os


db_path = r"C:\Apache24\htdocs\logs\flight_search.db"

if os.path.exists(db_path):
    os.remove(db_path)


conn = sqlite3.connect(db_path)
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        departure TEXT,
        destination TEXT,
        departure_date TEXT,
        return_date TEXT,
        passengers TEXT,
        class TEXT
    )
''')

# Commit changes and close
conn.commit()
conn.close()

print(f"Database created at {db_path} with only search_requests table")
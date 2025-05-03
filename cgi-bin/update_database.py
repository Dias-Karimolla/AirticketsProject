import sqlite3
import os


db_path = r"C:\Apache24\htdocs\logs\flight_search.db"


conn = sqlite3.connect(db_path)
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        departure TEXT NOT NULL,
        destination TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        arrival_time TEXT NOT NULL,
        airline TEXT NOT NULL,
        price INTEGER NOT NULL,
        class TEXT NOT NULL
    )
''')


cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT NOT NULL,
        rating INTEGER NOT NULL,
        price_per_night INTEGER NOT NULL,
        description TEXT
    )
''')


cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        city TEXT NOT NULL,
        price INTEGER NOT NULL,
        image_url TEXT
    )
''')


cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        preferences TEXT,
        created_at TEXT NOT NULL
    )
''')


cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_session_id TEXT,
        type TEXT NOT NULL,
        reference_id INTEGER NOT NULL,
        booking_date TEXT NOT NULL,
        details TEXT
    )
''')


cursor.executemany('''
    INSERT INTO flights (departure, destination, departure_time, arrival_time, airline, price, class)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', [
    ("Almaty", "Tbilisi", "2025-05-01 09:00", "2025-05-01 12:00", "Air Astana", 25000, "economy"),
    ("Almaty", "Tbilisi", "2025-05-01 14:00", "2025-05-01 17:00", "SCAT Airlines", 30000, "business"),
    ("Astana", "Paris", "2025-05-02 08:00", "2025-05-02 14:00", "Lufthansa", 95320, "business")
])

cursor.executemany('''
    INSERT INTO hotels (name, city, rating, price_per_night, description)
    VALUES (?, ?, ?, ?, ?)
''', [
    ("Hilton Tbilisi", "Tbilisi", 5, 8500, "Центр города, 5 звёзд"),
    ("Tbilisi Nights Hostel", "Tbilisi", 3, 2500, "Бюджетный вариант, 3 звезды"),
    ("Paris Plaza", "Paris", 4, 12000, "Рядом с Эйфелевой башней")
])


cursor.executemany('''
    INSERT INTO recommendations (title, description, city, price, image_url)
    VALUES (?, ?, ?, ?, ?)
''', [
    ("Назарбаев Центр", "Лучший комплекс зданий, построенный...", "Astana", 19225, "/static/images/nazarbaev.jpg"),
    ("Мечеть Айя-София", "Самое известное место Стамбула...", "Istanbul", 68141, "/static/images/ayasofya.jpg"),
    ("Эйфелева башня", "Романтика Парижа ждет вас...", "Paris", 95320, "/static/images/eiffel.jpg"),
    ("Большой Каньон", "Уникальное природное чудо...", "Arizona", 120450, "/static/images/canyon.jpg")
])


conn.commit()
conn.close()

print(f"Database updated at {db_path} with new tables and sample data")
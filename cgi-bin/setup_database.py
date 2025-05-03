import sqlite3
import os
from datetime import datetime

# Define database path
db_path = r"C:\Apache24\htdocs\logs\flight_search.db"

# Remove existing database to start fresh (optional, comment out if you want to keep existing data)
if os.path.exists(db_path):
    os.remove(db_path)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create search_requests table (existing)
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

# Create users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        created_at TEXT NOT NULL
    )
''')

# Create user_preferences table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        preferred_class TEXT,
        preferred_destinations TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Create flights table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        departure TEXT NOT NULL,
        destination TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        arrival_time TEXT NOT NULL,
        airline TEXT NOT NULL,
        price INTEGER NOT NULL,
        class TEXT NOT NULL,
        available_seats INTEGER NOT NULL
    )
''')

# Create flight_reviews table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS flight_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (flight_id) REFERENCES flights(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Create hotels table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT NOT NULL,
        rating INTEGER NOT NULL,
        price_per_night INTEGER NOT NULL,
        description TEXT,
        available_rooms INTEGER NOT NULL
    )
''')

# Create hotel_reviews table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotel_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hotel_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (hotel_id) REFERENCES hotels(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Create bookings table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        reference_id INTEGER NOT NULL,
        booking_date TEXT NOT NULL,
        details TEXT,
        status TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Create payments table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        payment_method TEXT NOT NULL,
        payment_date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (booking_id) REFERENCES bookings(id)
    )
''')

# Create destinations table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS destinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        country TEXT NOT NULL,
        description TEXT NOT NULL,
        image_url TEXT
    )
''')

# Create recommendations table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        destination_id INTEGER NOT NULL,
        flight_id INTEGER NOT NULL,
        price INTEGER NOT NULL,
        description TEXT,
        FOREIGN KEY (destination_id) REFERENCES destinations(id),
        FOREIGN KEY (flight_id) REFERENCES flights(id)
    )
''')

# Create travel_plans table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS travel_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        plan_name TEXT NOT NULL,
        budget INTEGER NOT NULL,
        days INTEGER NOT NULL,
        details TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Create notifications table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL,
        is_read INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Create promotions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS promotions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        reference_id INTEGER NOT NULL,
        discount_percentage INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL
    )
''')

# Create audit_logs table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')

# Insert sample data
# Users
cursor.executemany('''
    INSERT INTO users (email, password_hash, full_name, created_at)
    VALUES (?, ?, ?, ?)
''', [
    ("user1@example.com", "pass123", "John Doe", "2025-05-01 10:00:00"),
    ("user2@example.com", "pass456", "Jane Smith", "2025-05-01 11:00:00")
])

# User Preferences
cursor.executemany('''
    INSERT INTO user_preferences (user_id, preferred_class, preferred_destinations)
    VALUES (?, ?, ?)
''', [
    (1, "business", '["Tbilisi", "Paris"]'),
    (2, "economy", '["Astana", "Istanbul"]')
])

# Flights
cursor.executemany('''
    INSERT INTO flights (departure, destination, departure_time, arrival_time, airline, price, class, available_seats)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', [
    ("Almaty", "Tbilisi", "2025-05-01 09:00", "2025-05-01 12:00", "Air Astana", 25000, "economy", 50),
    ("Almaty", "Tbilisi", "2025-05-01 14:00", "2025-05-01 17:00", "SCAT Airlines", 30000, "business", 20),
    ("Astana", "Paris", "2025-05-02 08:00", "2025-05-02 14:00", "Lufthansa", 95320, "business", 30)
])

# Flight Reviews
cursor.executemany('''
    INSERT INTO flight_reviews (flight_id, user_id, rating, comment, created_at)
    VALUES (?, ?, ?, ?, ?)
''', [
    (1, 1, 4, "Great flight, but a bit delayed.", "2025-05-01 13:00:00"),
    (2, 2, 5, "Amazing service!", "2025-05-01 18:00:00")
])

# Hotels
cursor.executemany('''
    INSERT INTO hotels (name, city, rating, price_per_night, description, available_rooms)
    VALUES (?, ?, ?, ?, ?, ?)
''', [
    ("Hilton Tbilisi", "Tbilisi", 5, 8500, "Центр города, 5 звёзд", 10),
    ("Tbilisi Nights Hostel", "Tbilisi", 3, 2500, "Бюджетный вариант, 3 звезды", 20),
    ("Paris Plaza", "Paris", 4, 12000, "Рядом с Эйфелевой башней", 15)
])

# Hotel Reviews
cursor.executemany('''
    INSERT INTO hotel_reviews (hotel_id, user_id, rating, comment, created_at)
    VALUES (?, ?, ?, ?, ?)
''', [
    (1, 1, 5, "Luxurious stay!", "2025-05-01 14:00:00"),
    (2, 2, 3, "Good for the price.", "2025-05-01 15:00:00")
])

# Bookings
cursor.executemany('''
    INSERT INTO bookings (user_id, type, reference_id, booking_date, details, status)
    VALUES (?, ?, ?, ?, ?, ?)
''', [
    (1, "flight", 1, "2025-05-01 10:30:00", '{"passengers": 2}', "confirmed"),
    (2, "hotel", 1, "2025-05-01 11:30:00", '{"check_in": "2025-05-01", "check_out": "2025-05-03"}', "pending")
])

# Payments
cursor.executemany('''
    INSERT INTO payments (booking_id, amount, payment_method, payment_date, status)
    VALUES (?, ?, ?, ?, ?)
''', [
    (1, 50000, "credit_card", "2025-05-01 10:35:00", "completed"),
    (2, 17000, "paypal", "2025-05-01 11:35:00", "pending")
])

# Destinations
cursor.executemany('''
    INSERT INTO destinations (city, country, description, image_url)
    VALUES (?, ?, ?, ?)
''', [
    ("Tbilisi", "Georgia", "Historic city with rich culture", "/static/images/tbilisi.jpg"),
    ("Paris", "France", "City of romance and lights", "/static/images/paris.jpg"),
    ("Astana", "Kazakhstan", "Modern capital with stunning architecture", "/static/images/astana.jpg"),
    ("Istanbul", "Turkey", "Where East meets West", "/static/images/istanbul.jpg")
])

# Recommendations
cursor.executemany('''
    INSERT INTO recommendations (destination_id, flight_id, price, description)
    VALUES (?, ?, ?, ?)
''', [
    (1, 1, 25000, "Explore Tbilisi's old town"),
    (2, 3, 95320, "Visit the Eiffel Tower"),
    (3, 0, 19225, "Discover Nazarbayev Center"),
    (4, 0, 68141, "Experience Hagia Sophia")
])

# Travel Plans
cursor.executemany('''
    INSERT INTO travel_plans (user_id, plan_name, budget, days, details)
    VALUES (?, ?, ?, ?, ?)
''', [
    (1, "3 Days in Tbilisi", 50000, 3, '{"day1": "Old Town", "day2": "Mtskheta", "day3": "Market"}')
])

# Notifications
cursor.executemany('''
    INSERT INTO notifications (user_id, message, created_at, is_read)
    VALUES (?, ?, ?, ?)
''', [
    (1, "Your flight booking is confirmed!", "2025-05-01 10:40:00", 0),
    (2, "Hotel booking pending payment.", "2025-05-01 11:40:00", 0)
])

# Promotions
cursor.executemany('''
    INSERT INTO promotions (type, reference_id, discount_percentage, start_date, end_date)
    VALUES (?, ?, ?, ?, ?)
''', [
    ("flight", 1, 10, "2025-05-01", "2025-05-15"),
    ("hotel", 1, 15, "2025-05-01", "2025-05-10")
])

# Audit Logs
cursor.executemany('''
    INSERT INTO audit_logs (user_id, action, details, timestamp)
    VALUES (?, ?, ?, ?)
''', [
    (1, "login", '{"email": "user1@example.com"}', "2025-05-01 10:00:00"),
    (1, "booking", '{"booking_id": 1}', "2025-05-01 10:30:00")
])

# Commit changes and close
conn.commit()
conn.close()

print(f"Database setup complete at {db_path} with 14 tables and sample data")
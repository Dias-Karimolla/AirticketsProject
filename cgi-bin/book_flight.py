#!C:\Users\kkari\AppData\Local\Programs\Python\Python312\python.exe
import cgi
import sqlite3
from datetime import datetime
import json
import cgitb; cgitb.enable()  # Для отладки
import os

# Установка заголовков для ответа
print("Content-Type: application/json")
print()

# Получение данных формы
form = cgi.FieldStorage()
flight_id = form.getvalue('flight_id')
user_id = form.getvalue('user_id')
passengers = form.getvalue('passengers')
price = form.getvalue('price')
first_name = form.getvalue('first_name')
last_name = form.getvalue('last_name')
email = form.getvalue('email')

# Путь к базе данных
db_path = 'C:\\Apache24\\htdocs\\logs\\flight_search.db'
if not os.path.exists(db_path):
    print(json.dumps({"success": false, "error": f"Database file not found: {db_path}"}))
    exit()

# Подключение к базе данных
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Вставка бронирования
    booking_date = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO bookings (user_id, flight_id, passengers, price, booking_date, status, first_name, last_name, email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id if user_id else None, flight_id, passengers, price, booking_date, 'confirmed', first_name, last_name, email))

    # Получение ID бронирования
    booking_id = cursor.lastrowid

    # Подтверждение изменений
    conn.commit()

    response = {"success": True, "booking_id": booking_id, "message": "Booking successful"}

except Exception as e:
    response = {"success": False, "error": str(e)}
finally:
    conn.close()

# Отправка ответа в формате JSON
print(json.dumps(response))
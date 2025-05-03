#!C:/Users/kkari/AppData/Local/Programs/Python/Python312/python.exe
import cgi
import sqlite3
from datetime import datetime
import json

# Установка заголовков для ответа
print("Content-Type: application/json")
print()

# Получение данных формы
form = cgi.FieldStorage()
departure = form.getvalue('departure')
destination = form.getvalue('destination')
departure_date = form.getvalue('departure_date')
return_date = form.getvalue('return_date')
passengers = form.getvalue('passengers')
travel_class = form.getvalue('class')
user_id = form.getvalue('user_id')  # Может быть NULL, если пользователь не авторизован

# Подключение к базе данных
try:
    conn = sqlite3.connect('C:\\Apache24\\htdocs\\logs\\flight_search.db')
    cursor = conn.cursor()

    # Вставка данных в таблицу search_requests
    timestamp = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO search_requests (user_id, departure, destination, departure_date, return_date, passengers, travel_class, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id if user_id else None, departure, destination, departure_date, return_date, int(passengers), travel_class, timestamp))

    # Подтверждение изменений
    conn.commit()

    # Ответ об успешном сохранении
    response = {"success": True, "message": "Search request saved successfully"}
except Exception as e:
    response = {"success": False, "error": str(e)}
finally:
    conn.close()

# Отправка ответа в формате JSON
print(json.dumps(response))
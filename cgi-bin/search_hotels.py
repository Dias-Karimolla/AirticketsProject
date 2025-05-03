#!C:/Users/kkari/AppData/Local/Programs/Python/Python312/python.exe
import sqlite3
import sys
import os
from urllib.parse import parse_qs
from datetime import datetime

# Ensure stdout uses UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"C:\Apache24\htdocs\logs\flight_search.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_from_session():
    user_id = os.environ.get('HTTP_COOKIE', '').split('user_id=')[1].split(';')[0] if 'user_id=' in os.environ.get('HTTP_COOKIE', '') else None
    if user_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    return None

def main():
    print("Content-Type: text/html; charset=utf-8\r\n\r\n", end='')

    user = get_user_from_session()
    user_id = user['id'] if user else None

    if os.environ.get("REQUEST_METHOD") == "POST":
        content_length = int(os.environ.get("CONTENT_LENGTH", 0))
        form_data = sys.stdin.read(content_length)
        form = parse_qs(form_data, keep_blank_values=True)
        form = {k: v[0] for k, v in form.items()}

        city = form.get('city', '')
        check_in = form.get('check_in', '')
        check_out = form.get('check_out', '')
        guests = int(form.get('guests', 0))

        # Validate dates
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
            if check_in_date >= check_out_date:
                raise ValueError("Check-out date must be after check-in date.")
        except ValueError as e:
            print(f"""
            <script>
                alert('Ошибка: {str(e)}');
                window.location.href = '/static/Design3.1.html';
            </script>
            """)
            return

        # Query hotels
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hotels WHERE city = ? AND available_rooms > 0", (city,))
        hotels = cursor.fetchall()

        # Check promotions
        cursor.execute('''
            SELECT * FROM promotions 
            WHERE type = 'hotel' AND start_date <= ? AND end_date >= ?
        ''', (datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')))
        promotions = {p['reference_id']: p['discount_percentage'] for p in cursor.fetchall()}

        hotel_results = "<h3 class='text-lg font-semibold text-blue-600 mt-4'>Доступные отели:</h3><div class='space-y-2'>"
        if hotels:
            for hotel in hotels:
                discount = promotions.get(hotel['id'], 0)
                discounted_price = hotel['price_per_night'] * (1 - discount / 100) if discount else hotel['price_per_night']
                hotel_results += f"""
                <div class='bg-gray-50 p-4 rounded-lg shadow'>
                    <p><span class='font-medium'>Название:</span> {hotel['name']}</p>
                    <p><span class='font-medium'>Город:</span> {hotel['city']}</p>
                    <p><span class='font-medium'>Рейтинг:</span> {hotel['rating']} звёзд</p>
                    <p><span class='font-medium'>Цена за ночь:</span> {discounted_price} ₸"""
                if discount:
                    hotel_results += f" <span class='text-green-600'>(Скидка {discount}%)</span>"
                hotel_results += f"""
                    </p>
                    <p><span class='font-medium'>Описание:</span> {hotel['description']}</p>
                    <p><span class='font-medium'>Свободных номеров:</span> {hotel['available_rooms']}</p>
                    <button onclick="bookHotel({hotel['id']}, '{check_in}', '{check_out}', {guests}, {discounted_price})" class="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Забронировать</button>
                </div>
                """
        else:
            hotel_results += "<p class='text-gray-600'>Отели не найдены.</p>"
        hotel_results += "</div>"
        conn.close()

        # Response
        response = f"""
        <div class="bg-white p-6 rounded-lg shadow-lg">
            <h2 class="text-2xl font-semibold text-blue-600 mb-4">Результаты поиска отелей</h2>
            <div class="space-y-3">
                <p><span class="font-medium">Город:</span> <span class="ml-2">{city}</span></p>
                <p><span class="font-medium">Дата заезда:</span> <span class="ml-2">{check_in}</span></p>
                <p><span class="font-medium">Дата выезда:</span> <span class="ml-2">{check_out}</span></p>
                <p><span class="font-medium">Гостей:</span> <span class="ml-2">{guests}</span></p>
            </div>
            {hotel_results}
            <a href="/static/Design3.1.html" class="mt-4 inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition">Новый поиск</a>
        </div>
        """

        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Результат поиска отелей</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                body {{ background-color: #f0f4f8; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; font-family: 'Arial', sans-serif; }}
            </style>
            <script>
                function bookHotel(hotelId, checkIn, checkOut, guests, price) {{
                    if (!{user_id or 'null'}) {{
                        alert('Пожалуйста, войдите в систему, чтобы забронировать отель.');
                        window.location.href = '/static/Design3.1.html';
                        return;
                    }}
                    fetch('/cgi-bin/book_hotel.py', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                        body: `hotel_id=${{hotelId}}&user_id=${{ {user_id} }}&check_in=${{checkIn}}&check_out=${{checkOut}}&guests=${{guests}}&price=${{price}}`
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.success) {{
                            alert('Отель успешно забронирован!');
                            window.location.href = '/static/Design3.1.html';
                        }} else {{
                            alert('Ошибка при бронировании: ' + data.error);
                        }}
                    }});
                }}
            </script>
        </head>
        <body>
            {response}
        </body>
        </html>
        """
        print(html)

if __name__ == "__main__":
    main()
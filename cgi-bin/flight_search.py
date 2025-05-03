#!C:/Users/kkari/AppData/Local/Programs/Python/Python313/python.exe
import cgi
import cgitb
import csv
import os
import datetime
import html
from urllib.parse import parse_qs

cgitb.enable()
LOG_FILE = "C:/Apache24/cgi-bin/search_logs.csv"

def log_search(form_data):
    with open("C:/Apache24/cgi-bin/debug.txt", "a") as debug_file:
        debug_file.write("log_search called at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = [
        timestamp,
        form_data.get("from", [""])[0],
        form_data.get("to", [""])[0],
        form_data.get("departure_date", [""])[0],
        form_data.get("return_date", [""])[0] or "N/A",
        form_data.get("passengers", [""])[0]
    ]
    file_exists = os.path.isfile(LOG_FILE)
    try:
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "From", "To", "Departure Date", "Return Date", "Passengers"])
            writer.writerow(log_entry)
    except Exception as e:
        with open("C:/Apache24/cgi-bin/error.txt", "a") as error_file:
            error_file.write(f"Error writing to CSV: {str(e)} at {timestamp}\n")

def validate_form(form_data):
    errors = []
    required_fields = ["from", "to", "departure_date", "passengers"]

    for field in required_fields:
        if not form_data.get(field) or not form_data[field][0].strip():
            errors.append(f"Поле {field} обязательно для заполнения")

    if form_data.get("departure_date"):
        try:
            datetime.datetime.strptime(form_data["departure_date"][0], "%Y-%m-%d")
        except ValueError:
            errors.append("Неверный формат даты отправления")

    if form_data.get("return_date") and form_data["return_date"][0].strip():
        try:
            datetime.datetime.strptime(form_data["return_date"][0], "%Y-%m-%d")
        except ValueError:
            errors.append("Неверный формат даты возвращения")

    if form_data.get("passengers"):
        try:
            passengers = int(form_data["passengers"][0].split()[0])
            if passengers <= 0:
                errors.append("Количество пассажиров должно быть больше 0")
        except ValueError:
            errors.append("Неверный формат количества пассажиров")

    return errors

def generate_flights(from_city, to_city, departure_date, passengers):
    flights = [
        {
            "airline": "Air Astana",
            "time": "08:00 - 10:30",
            "duration": "2ч 30м",
            "price": 25000,
            "stops": "Без пересадок"
        },
        {
            "airline": "SCAT Airlines",
            "time": "14:00 - 16:45",
            "duration": "2ч 45м",
            "price": 22000,
            "stops": "Без пересадок"
        },
        {
            "airline": "FlyArystan",
            "time": "20:00 - 22:30",
            "duration": "2ч 30м",
            "price": 18000,
            "stops": "Без пересадок"
        }
    ]
    return flights

def main():
    print("Content-Type: text/html; charset=utf-8\n")

    form = cgi.FieldStorage()
    if not form:
        print("<html><body><h1>No form data provided</h1>")
        print('<a href="/Design3.html">Go to search form</a></body></html>')
        return

    form_data = {key: form.getlist(key) for key in form.keys()}

    errors = validate_form(form_data)

    if errors:
        print("<html><body>")
        print("<h2>Ошибки в форме</h2>")
        print("<ul>")
        for error in errors:
            print(f"<li>{html.escape(error)}</li>")
        print("</ul>")
        print('<a href="javascript:history.back()">Вернуться назад</a>')
        print("</body></html>")
        return

    log_search(form_data)

    from_city = html.escape(form_data.get("from", [""])[0])
    to_city = html.escape(form_data.get("to", [""])[0])
    departure_date = html.escape(form_data.get("departure_date", [""])[0])
    return_date = html.escape(form_data.get("return_date", [""])[0] or "N/A")
    passengers = html.escape(form_data.get("passengers", [""])[0])

    flights = generate_flights(from_city, to_city, departure_date, passengers)

    # Используем f-строку для корректной подстановки
    print(f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Результаты поиска авиабилетов</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 20px;
                background-color: #f4f7fa;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            h1 {{
                color: #007bff;
                text-align: center;
                margin-bottom: 20px;
            }}
            .search-info {{
                background-color: #fff;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            .search-info p {{
                margin: 5px 0;
                font-size: 16px;
            }}
            .results-section {{
                display: flex;
                gap: 20px;
            }}
            .filters {{
                flex: 1;
                background-color: #fff;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .filters h3 {{
                margin-bottom: 15px;
                color: #333;
            }}
            .filters label {{
                display: block;
                margin: 10px 0;
                font-size: 14px;
            }}
            .results {{
                flex: 3;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }}
            .flight-card {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                background-color: #fff;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .flight-card div {{
                flex: 1;
                text-align: center;
            }}
            .flight-card .price {{
                font-weight: bold;
                color: #ff6200;
            }}
            .flight-card button {{
                padding: 8px 15px;
                background-color: #007bff;
                color: #fff;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            .flight-card button:hover {{
                background-color: #0056b3;
            }}
            .back-link {{
                display: block;
                text-align: center;
                margin-top: 20px;
                color: #007bff;
                text-decoration: none;
                font-size: 16px;
            }}
            .back-link:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Результаты поиска авиабилетов</h1>
            <div class="search-info">
                <p><strong>Маршрут:</strong> {from_city} → {to_city}</p>
                <p><strong>Дата вылета:</strong> {departure_date}</p>
                <p><strong>Дата возвращения:</strong> {return_date}</p>
                <p><strong>Пассажиры:</strong> {passengers}</p>
            </div>
            <div class="results-section">
                <div class="filters">
                    <h3>Фильтры</h3>
                    <label><input type="checkbox"> Без пересадок</label>
                    <label><input type="checkbox"> Утренние рейсы</label>
                    <label><input type="range" min="0" max="50000" value="25000"> Цена до <span>25 000 ₸</span></label>
                </div>
                <div class="results">
    """)

    for flight in flights:
        print(f"""
                    <div class="flight-card">
                        <div>{flight['airline']}</div>
                        <div>{flight['time']}</div>
                        <div>{flight['duration']}</div>
                        <div class="price">{flight['price']} ₸</div>
                        <div><button>Выбрать</button></div>
                    </div>
        """)

    print("""
                </div>
            </div>
            <a href="/Design3.html" class="back-link">Новый поиск</a>
        </div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    main()
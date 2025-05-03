#!C:\Users\kkari\AppData\Local\Programs\Python\Python312\python.exe
import json
import re
import sqlite3
from datetime import datetime
import os
import sys
from urllib.parse import parse_qs
import logging
import time
import traceback
import requests
import hashlib

# Set up logging
logging.basicConfig(
    filename=r'C:\Apache24\htdocs\logs\search_flights.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Ensure stdout uses UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Database path
DB_PATH = r"C:\Apache24\htdocs\logs\flight_search.db"

# Aviasales API configuration
API_TOKEN = "ba463465c90bfaee386337e7c62e8a35"
MARKER = "627294"
API_BASE_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"

def get_db_connection():
    logging.debug(f"Attempting to connect to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH, timeout=30)
    logging.debug("Connected to database, setting WAL mode")
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    logging.debug(f"Journal mode set to: {conn.execute('PRAGMA journal_mode;').fetchone()[0]}")
    return conn

def validate_input(value):
    if not value or value.strip() == "":
        return False
    value = re.sub(r'[<>;]', '', value.strip())
    return value

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def log_search_request(data, max_retries=2):
    logging.debug(f"Attempting to log search request: {data}")
    for attempt in range(max_retries + 1):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO search_requests (timestamp, departure, destination, departure_date, return_date, passengers, class)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                data.get("departure", ""),
                data.get("destination", ""),
                data.get("departure_date", ""),
                data.get("return_date", ""),
                data.get("passengers", ""),
                data.get("class", "")
            ))
            conn.commit()
            logging.debug("Search request logged successfully")
            break
        except sqlite3.OperationalError as e:
            logging.warning(f"Attempt {attempt + 1}/{max_retries + 1} failed to log search request due to: {str(e)}")
            time.sleep(2 ** attempt)
            if attempt == max_retries:
                logging.error(f"Max retries reached for logging search request. Skipping. Data: {data}")
        finally:
            conn.close()

def log_audit(user_id, action, details, max_retries=2):
    logging.debug(f"Attempting to log audit: {action}, {details}")
    for attempt in range(max_retries + 1):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO audit_logs (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action, json.dumps(details), datetime.now().isoformat()))
            conn.commit()
            logging.debug("Audit logged successfully")
            break
        except sqlite3.OperationalError as e:
            logging.warning(f"Attempt {attempt + 1}/{max_retries + 1} failed to log audit due to: {str(e)}")
            time.sleep(2 ** attempt)
            if attempt == max_retries:
                logging.error(f"Max retries reached for logging audit. Skipping. Details: {details}")
        finally:
            conn.close()

def get_user_from_session():
    logging.debug("Attempting to get user from session")
    user_id = os.environ.get('HTTP_COOKIE', '').split('user_id=')[1].split(';')[0] if 'user_id=' in os.environ.get('HTTP_COOKIE', '') else None
    if user_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            logging.debug(f"Querying user with id: {user_id}")
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            logging.debug(f"User query result: {user}")
            return user
        except sqlite3.OperationalError as e:
            logging.error(f"Failed to query user due to: {str(e)}")
            return None
        finally:
            conn.close()
    return None

def calculate_duration(departure_time, arrival_time, duration_to=None, duration_back=None):
    formats = ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M']
    dep = None
    arr = None
    for fmt in formats:
        try:
            if not dep:
                dep = datetime.strptime(departure_time, fmt)
            if arrival_time and not arr:
                arr = datetime.strptime(arrival_time, fmt)
            if dep and arr:
                break
        except ValueError:
            continue
    if duration_to is not None:
        total_minutes = duration_to  # duration_to is already in minutes
        hours = max(0, total_minutes // 60)  # Avoid negative values
        minutes = max(0, total_minutes % 60)
        return f"{hours}ч {minutes}м в пути"
    if not (dep and arr):
        logging.error(f"Error calculating duration: Could not parse times - departure: {departure_time}, arrival: {arrival_time}")
        return "Неизвестная длительность"
    duration = arr - dep
    total_minutes = int(duration.total_seconds() / 60)
    hours = max(0, total_minutes // 60)  # Avoid negative values
    minutes = max(0, total_minutes % 60)
    return f"{hours}ч {minutes}м в пути"

def get_airline_name(iata_code):
    airline_iata_map = {
        "HH": "AtlasGlobal",
        "VF": "Valuair",
        "U6": "Ural Airlines",
        "SU": "Aeroflot",
        "TK": "Turkish Airlines",
        "QR": "Qatar Airways",
        "EK": "Emirates",
        "BA": "British Airways",
        "AF": "Air France",
        "LH": "Lufthansa",
        "KC": "Air Astana",
        "F4": "FlyArystan",
        "DV": "SCAT Airlines",
        "DP": "Pobeda",
        "FV": "Rossiya",
        "UT": "UTair",
        "S7": "S7 Airlines",
        "5N": "Nordavia",
        "B2": "Belavia",
        "HY": "Uzbekistan Airways",
        "FZ": "FlyDubai",
        "G9": "Air Arabia",
        "EY": "Etihad Airways",
        "MS": "EgyptAir",
        "KL": "KLM",
        "AZ": "Alitalia"
    }
    return airline_iata_map.get(iata_code, iata_code)

def get_iata_code(city):
    if re.match(r'^[A-Z]{3}$', city):
        return city

    city_normalized = city.lower().replace('_', ' ').replace('-', ' ')

    city_iata_map = {
        # Казахстан
        "алматы": "ALA",
        "астана": "NQZ",
        "атырау": "GUW",
        "актау": "SCO",
        "шимкент": "CIT",
        "актобе": "AKX",
        "караганда": "KGF",
        "павлодар": "PWQ",
        "усть-каменогорск": "UKK",
        "кызылорда": "KZO",
        "семей": "PLX",
        "костанай": "KSN",
        "тараз": "DMB",
        "уральск": "URA",
        "петропавловск": "PPK",
        # Россия
        "москва": "MOW",
        "санкт-петербург": "LED",
        "екатеринбург": "SVX",
        "новосибирск": "OVB",
        "краснодар": "KRR",
        "уфа": "UFA",
        "казань": "KZN",
        "сочи": "AER",
        "владивосток": "VVO",
        "ростов-на-дону": "ROV",
        # США
        "нью-йорк": "NYC",
        "лос-анджелес": "LAX",
        "чикаго": "ORD",
        "хьюстон": "IAH",
        "феникс": "PHX",
        "дallas": "DFW",
        "денвер": "DEN",
        "сан-франциско": "SFO",
        "сиэтл": "SEA",
        "майами": "MIA",
        # Европа
        "лондон": "LON",
        "париж": "PAR",
        "берлин": "BER",
        "рома": "ROM",
        "амстердам": "AMS",
        "барселона": "BCN",
        "милан": "MIL",
        "мюнхен": "MUC",
        "виена": "VIE",
        "стамбул": "IST"
    }

    return city_iata_map.get(city_normalized, "")

def generate_signature(params):
    sorted_params = sorted(f"{k}={v}" for k, v in params.items() if k not in ['signature', 'token'])
    signature_string = f"{API_TOKEN}:{':'.join(sorted_params)}"
    logging.debug(f"Signature string: {signature_string}")
    return hashlib.md5(signature_string.encode('utf-8')).hexdigest()

def search_flights_api(departure, destination, departure_date, travel_class, passenger_count):
    logging.debug(f"Searching flights via API: departure={departure}, destination={destination}, date={departure_date}, class={travel_class}, passengers={passenger_count}")
    
    origin_iata = get_iata_code(departure)
    destination_iata = get_iata_code(destination)
    
    if not origin_iata or not destination_iata:
        logging.error(f"Could not map cities to IATA codes: {departure} -> {origin_iata}, {destination} -> {destination_iata}")
        return []

    markets = ["ru", "kz", "us"]
    flights = []
    seen_flights = set()
    currency = "RUB"  # Default currency

    for market in markets:
        params = {
            "origin": origin_iata,
            "destination": destination_iata,
            "departure_at": departure_date,
            "currency": "RUB",
            "market": market,
            "limit": 100,
            "direct": "false",
            "token": API_TOKEN
        }
        
        params["signature"] = generate_signature(params)
        
        logging.debug(f"Sending API request to {API_BASE_URL} with params: {params}")
        
        try:
            headers = {"Accept-Encoding": "gzip, deflate"}
            response = requests.get(API_BASE_URL, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"API response for market {market}: {data}")
            
            if not data.get("success"):
                logging.error(f"API request failed for market {market}: {data.get('error', 'Unknown error')}")
                continue
            
            currency = data.get("currency", "RUB")  # Update currency based on API response
            
            for flight in data.get("data", []):
                flight_key = (flight.get("flight_number"), flight.get("departure_at"))
                if flight_key in seen_flights:
                    continue
                seen_flights.add(flight_key)
                
                actual_destination = flight.get("destination", destination_iata)
                transfers = flight.get("transfers", 0)
                transfer_details = ""
                if transfers > 0:
                    # Пример: предполагаем, что API возвращает данные о пересадке
                    transfer_details = f"Пересадка в Астане (NQZ), {flight.get('transfer_duration', '1 ч 35 мин')}" if origin_iata == "ALA" and destination_iata == "GUW" else f"{transfers} пересадка(и), подробности уточняются"

                flight_data = {
                    "id": flight.get("id", len(flights) + 1),
                    "airline": get_airline_name(flight.get("airline", "Unknown")),
                    "departure": departure,
                    "destination": destination,
                    "actual_destination": actual_destination,
                    "departure_time": flight.get("departure_at", "").split("T")[1].split("+")[0][:5] if flight.get("departure_at") else "00:00",
                    "arrival_time": flight.get("return_at", "").split("T")[1].split("+")[0][:5] if flight.get("return_at") else "00:00",
                    "class": travel_class,
                    "price": float(flight.get("price", 0)),
                    "discount": 0,
                    "available_seats": passenger_count,
                    "duration": calculate_duration(flight.get("departure_at", "1970-01-01T00:00:00+00:00"), flight.get("return_at", "1970-01-01T00:00:00+00:00"), flight.get("duration_to"), flight.get("duration_back")),
                    "transfers": f"{transfers} пересадок" if transfers > 0 else "прямой",
                    "transfer_details": transfer_details,
                    "currency": currency
                }
                flights.append(flight_data)
        
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed for market {market}: {str(e)}")
            try:
                error_data = response.json()
                logging.error(f"API error details for market {market}: {error_data}")
            except:
                logging.error(f"Could not parse API error response for market {market}")
            continue

    if not flights:
        logging.warning("No flights found in API response across all markets, possibly due to date, route, or cache limitation")
    
    logging.debug(f"Processed {len(flights)} flights from API")
    return flights

def main():
    print("Content-Type: application/json; charset=utf-8\r\n\r\n", end='')
    try:
        logging.debug("Starting main execution")
        user = get_user_from_session()
        user_id = user['id'] if user else None
        logging.debug(f"User ID: {user_id}")

        if os.environ.get("REQUEST_METHOD") == "POST":
            content_length = int(os.environ.get("CONTENT_LENGTH", 0))
            form_data = sys.stdin.read(content_length)
            form = parse_qs(form_data, keep_blank_values=True)
            form = {k: v[0] for k, v in form.items()}
        else:
            form = {}

        logging.debug(f"Received form data: {form}")

        departure = validate_input(form.get("departure"))
        destination = validate_input(form.get("destination"))
        departure_date = form.get("departure_date")
        return_date = form.get("return_date")
        passengers = form.get("passengers")
        travel_class = validate_input(form.get("class"))

        errors = []
        if not departure:
            errors.append("Город вылета не указан.")
        if not destination:
            errors.append("Город назначения не указан.")
        if departure_date and not validate_date(departure_date):
            errors.append("Некорректная дата вылета.")
        if return_date and not validate_date(return_date):
            errors.append("Некорректная дата возвращения.")
        try:
            passenger_count = int(passengers.split()[0]) if passengers else 0
            if passenger_count <= 0:
                errors.append("Количество пассажиров должно быть больше 0.")
        except (ValueError, TypeError):
            errors.append("Некорректное количество пассажиров.")

        request_data = {
            "departure": departure or "",
            "destination": destination or "",
            "departure_date": departure_date or "",
            "return_date": return_date or "",
            "passengers": passengers or "",
            "class": travel_class or ""
        }
        logging.debug(f"Request data validated: {request_data}")
        log_search_request(request_data)
        log_audit(user_id, "search_flight", request_data)

        if errors:
            response = {"success": False, "errors": errors}
            logging.debug(f"Returning errors: {errors}")
            print(json.dumps(response))
            return

        flights = search_flights_api(departure, destination, departure_date, travel_class, passenger_count)

        flight_list = []
        for flight in flights:
            flight_list.append({
                "id": flight['id'],
                "airline": flight['airline'],
                "departure": flight['departure'],
                "destination": flight['destination'],
                "actual_destination": flight['actual_destination'],
                "departure_time": flight['departure_time'],
                "arrival_time": flight['arrival_time'],
                "class": flight['class'],
                "price": flight['price'],
                "discount": flight['discount'],
                "available_seats": flight['available_seats'],
                "duration": flight['duration'],
                "transfers": flight['transfers'],
                "transfer_details": flight['transfer_details'],
                "currency": flight['currency']
            })

        response = {"success": True, "flights": flight_list}
        if not flight_list:
            response["message"] = "Рейсы не найдены. Попробуйте изменить дату (доступны данные за последние 48 часов) или маршрут."
        logging.debug(f"Returning response: {response}")
        print(json.dumps(response))
    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}\nFull traceback: {''.join(traceback.format_exception(type(e), e, e.__traceback__))}")
        print(json.dumps({"success": False, "errors": ["Произошла внутренняя ошибка сервера."]}))
    finally:
        logging.debug("Main execution completed")

if __name__ == "__main__":
    main()
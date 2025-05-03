#!C:\Users\kkari\AppData\Local\Programs\Python\Python312\python.exe
import json
import sqlite3
import sys
import logging
import hashlib
from urllib.parse import parse_qs
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    filename=r'C:\Apache24\htdocs\logs\register.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Путь к базе данных
DB_PATH = r"C:\Apache24\htdocs\logs\flight_search.db"

# Обеспечение вывода в UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def get_db_connection():
    logging.debug(f"Подключение к базе данных: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    logging.debug(f"Режим журнала установлен: {conn.execute('PRAGMA journal_mode;').fetchone()[0]}")
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def validate_input(value):
    if not value or value.strip() == "":
        return False
    return value.strip()

def main():
    print("Content-Type: application/json; charset=utf-8\r\n\r\n", end='')
    try:
        logging.debug("Начало выполнения register.py")

        # Получение данных из формы
        if os.environ.get("REQUEST_METHOD") == "POST":
            content_length = int(os.environ.get("CONTENT_LENGTH", 0))
            form_data = sys.stdin.read(content_length)
            form = parse_qs(form_data, keep_blank_values=True)
            form = {k: v[0] for k, v in form.items()}
        else:
            form = {}

        logging.debug(f"Полученные данные формы: {form}")

        # Валидация входных данных
        first_name = validate_input(form.get("first_name"))
        last_name = validate_input(form.get("last_name"))
        email = validate_input(form.get("email"))
        password = validate_input(form.get("password"))

        errors = []
        if not first_name:
            errors.append("Имя не указано.")
        if not last_name:
            errors.append("Фамилия не указана.")
        if not email or "@" not in email:
            errors.append("Некорректный email.")
        if not password or len(password) < 6:
            errors.append("Пароль должен быть не менее 6 символов.")

        if errors:
            response = {"success": False, "error": " ".join(errors)}
            logging.debug(f"Ошибки валидации: {errors}")
            print(json.dumps(response))
            return

        # Хеширование пароля
        password_hash = hash_password(password)

        # Сохранение пользователя в базе данных
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users2 (first_name, last_name, email, password_hash)
                VALUES (?, ?, ?, ?)
            ''', (first_name, last_name, email, password_hash))
            conn.commit()
            logging.info(f"Пользователь успешно зарегистрирован: {email}")
            response = {"success": True}
        except sqlite3.IntegrityError:
            logging.warning(f"Попытка регистрации с существующим email: {email}")
            response = {"success": False, "error": "Этот email уже зарегистрирован."}
        except sqlite3.Error as e:
            logging.error(f"Ошибка базы данных при регистрации: {str(e)}")
            response = {"success": False, "error": "Ошибка сервера при регистрации."}
        finally:
            conn.close()

        print(json.dumps(response))
    except Exception as e:
        logging.error(f"Исключение в register.py: {str(e)}")
        print(json.dumps({"success": False, "error": "Произошла внутренняя ошибка сервера."}))
    finally:
        logging.debug("Выполнение register.py завершено")

if __name__ == "__main__":
    main()
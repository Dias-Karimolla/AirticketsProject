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
    filename=r'C:\Apache24\htdocs\logs\login.log',
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
    # Установка заголовков
    print("Content-Type: application/json; charset=utf-8")
    try:
        logging.debug("Начало выполнения login.py")

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
        email = validate_input(form.get("email"))
        password = validate_input(form.get("password"))

        errors = []
        if not email or "@" not in email:
            errors.append("Некорректный email.")
        if not password:
            errors.append("Пароль не указан.")

        if errors:
            response = {"success": False, "error": " ".join(errors)}
            logging.debug(f"Ошибки валидации: {errors}")
            print("\r\n\r\n", end='')
            print(json.dumps(response))
            return

        # Хеширование пароля
        password_hash = hash_password(password)

        # Проверка пользователя в базе данных
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users2 WHERE email = ? AND password_hash = ?", (email, password_hash))
            user = cursor.fetchone()
            if user:
                # Установка cookie с user_id
                user_id = user['id']
                print(f"Set-Cookie: user_id={user_id}; Path=/; HttpOnly")
                logging.info(f"Успешный вход пользователя: {email}")
                response = {"success": True}
            else:
                logging.warning(f"Неудачная попытка входа: {email}")
                response = {"success": False, "error": "Неверный email или пароль."}
        except sqlite3.Error as e:
            logging.error(f"Ошибка базы данных при входе: {str(e)}")
            response = {"success": False, "error": "Ошибка сервера при входе."}
        finally:
            conn.close()

        print("\r\n\r\n", end='')
        print(json.dumps(response))
    except Exception as e:
        logging.error(f"Исключение в login.py: {str(e)}")
        print("\r\n\r\n", end='')
        print(json.dumps({"success": False, "error": "Произошла внутренняя ошибка сервера."}))
    finally:
        logging.debug("Выполнение login.py завершено")

if __name__ == "__main__":
    main()
#!C:\Users\kkari\AppData\Local\Programs\Python\Python312\python.exe
import json
import sqlite3
import sys
import logging
from urllib.parse import parse_qs

# Настройка логирования
logging.basicConfig(
    filename=r'C:\Apache24\htdocs\logs\get_user.log',
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
    return conn

def main():
    print("Content-Type: application/json; charset=utf-8\r\n\r\n", end='')
    try:
        logging.debug("Начало выполнения get_user.py")

        # Получение user_id из query string
        query_string = os.environ.get("QUERY_STRING", "")
        params = parse_qs(query_string)
        user_id = params.get("user_id", [None])[0]

        if not user_id:
            response = {"success": False, "error": "user_id не указан"}
            logging.debug("user_id не указан")
            print(json.dumps(response))
            return

        # Запрос данных пользователя
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT first_name, last_name, email FROM users2 WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user:
                response = {
                    "success": True,
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "email": user["email"]
                }
                logging.debug(f"Данные пользователя найдены: {response}")
            else:
                response = {"success": False, "error": "Пользователь не найден"}
                logging.debug(f"Пользователь с id {user_id} не найден")
        except sqlite3.Error as e:
            logging.error(f"Ошибка базы данных: {str(e)}")
            response = {"success": False, "error": "Ошибка сервера"}
        finally:
            conn.close()

        print(json.dumps(response))
    except Exception as e:
        logging.error(f"Исключение в get_user.py: {str(e)}")
        print(json.dumps({"success": False, "error": "Произошла внутренняя ошибка сервера"}))
    finally:
        logging.debug("Выполнение get_user.py завершено")

if __name__ == "__main__":
    main()
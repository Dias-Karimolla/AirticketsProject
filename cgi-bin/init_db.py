import sqlite3
import logging

# Настройка логирования
logging.basicConfig(
    filename=r'C:\Apache24\htdocs\logs\init_db.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Путь к базе данных
DB_PATH = r"C:\Apache24\htdocs\logs\flight_search.db"

def init_db():
    logging.debug(f"Инициализация базы данных: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
        conn.execute('PRAGMA journal_mode=WAL;')
        cursor = conn.cursor()

        # Создание таблицы users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Проверка существующих таблиц (для отладки)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        logging.debug(f"Таблицы в базе данных: {tables}")

        conn.commit()
        logging.info("База данных успешно инициализирована")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при инициализации базы данных: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
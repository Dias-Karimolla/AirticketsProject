#!C:\Users\kkari\AppData\Local\Programs\Python\Python312\python.exe
import json
import os
import sys
import logging

# Настройка логирования
logging.basicConfig(
    filename=r'C:\Apache24\htdocs\logs\check_session.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Обеспечение вывода в UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("Content-Type: application/json; charset=utf-8\r\n\r\n", end='')
    try:
        logging.debug("Начало выполнения check_session.py")
        user_id = os.environ.get('HTTP_COOKIE', '').split('user_id=')[1].split(';')[0] if 'user_id=' in os.environ.get('HTTP_COOKIE', '') else None
        response = {"user_id": user_id}
        logging.debug(f"Результат проверки сессии: {response}")
        print(json.dumps(response))
    except Exception as e:
        logging.error(f"Исключение в check_session.py: {str(e)}")
        print(json.dumps({"user_id": null}))
    finally:
        logging.debug("Выполнение check_session.py завершено")

if __name__ == "__main__":
    main()
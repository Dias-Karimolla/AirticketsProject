#!C:\Users\kkari\AppData\Local\Programs\Python\Python312\python.exe
import json
import sys
import logging

# Настройка логирования
logging.basicConfig(
    filename=r'C:\Apache24\htdocs\logs\logout.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Обеспечение вывода в UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("Content-Type: application/json; charset=utf-8")
    print("Set-Cookie: user_id=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
    print("\r\n\r\n", end='')
    try:
        logging.debug("Начало выполнения logout.py")
        response = {"success": True}
        logging.info("Пользователь успешно вышел из системы")
        print(json.dumps(response))
    except Exception as e:
        logging.error(f"Исключение в logout.py: {str(e)}")
        print(json.dumps({"success": False, "error": "Произошла ошибка при выходе"}))
    finally:
        logging.debug("Выполнение logout.py завершено")

if __name__ == "__main__":
    main()
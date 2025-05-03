#!C:\Users\kkari\AppData\Local\Programs\Python\Python312\python.exe
import cgi
import sqlite3
import subprocess
import os
import json

# Получение данных
form = cgi.FieldStorage()
booking_id = form.getvalue('booking_id')

# Путь к базе данных
db_path = 'C:\\Apache24\\htdocs\\logs\\flight_search.db'

# Подключение к базе данных
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получение информации о бронировании
    cursor.execute('''
        SELECT b.id, b.user_id, b.flight_id, b.passengers, b.price, b.booking_date, b.status, 
               b.first_name, b.last_name, b.email, f.airline, f.departure, f.destination, 
               f.departure_time, f.arrival_time, f.duration
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        WHERE b.id = ?
    ''', (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        print("Content-Type: application/json")
        print()
        print(json.dumps({"success": false, "error": "Booking not found"}))
        conn.close()
        exit()

    ticket_data = {
        "id": booking[0],
        "user_id": booking[1],
        "flight_id": booking[2],
        "passengers": booking[3],
        "price": booking[4],
        "booking_date": booking[5],
        "status": booking[6],
        "first_name": booking[7],
        "last_name": booking[8],
        "email": booking[9],
        "airline": booking[10],
        "departure": booking[11],
        "destination": booking[12],
        "departure_time": booking[13],
        "arrival_time": booking[14],
        "duration": booking[15]
    }

    # Генерация улучшенного LaTeX для билета
    latex_content = r'''
\documentclass[a4paper]{article}
\usepackage[russian]{babel}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\geometry{a4paper, margin=1in}
\usepackage{fancyhdr}
\usepackage{colortbl}
\usepackage{xcolor}
\usepackage{array}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

\usepackage{fontspec}
\setmainfont{Noto Serif}

\definecolor{headercolor}{RGB}{0, 102, 204}
\definecolor{tableheader}{RGB}{230, 240, 255}
\definecolor{tablerow}{RGB}{245, 245, 245}

\fancyhead[C]{\textcolor{headercolor}{\Huge\textbf{Airline Logo}} \\ \large Транспортная компания}
\fancyfoot[C]{\thepage}

\begin{document}

\begin{center}
  \textcolor{headercolor}{\Huge\textbf{Авиабилет}} \\
  \vspace{0.5cm}
  \large Номер билета: \textbf{\texttt{%d}}
\end{center}

\begin{tabular}{|>{\columncolor{tableheader}}p{3cm}|p{10cm}|}
  \hline
  \rowcolor{tableheader} \textbf{Поле} & \textbf{Значение} \\
  \hline
  \rowcolor{tablerow} Имя & %s \\
  \hline
  \rowcolor{tablerow} Фамилия & %s \\
  \hline
  \rowcolor{tablerow} Email & \texttt{%s} \\
  \hline
  \rowcolor{tablerow} Авиакомпания & \textbf{%s} \\
  \hline
  \rowcolor{tablerow} Откуда & \textbf{%s} \\
  \hline
  \rowcolor{tablerow} Куда & \textbf{%s} \\
  \hline
  \rowcolor{tablerow} Время вылета & %s \\
  \hline
  \rowcolor{tablerow} Время прибытия & %s \\
  \hline
  \rowcolor{tablerow} Длительность & %s \\
  \hline
  \rowcolor{tablerow} Количество пассажиров & %d \\
  \hline
  \rowcolor{tablerow} Цена & \textbf{%d\,RUB} \\
  \hline
  \rowcolor{tablerow} Дата бронирования & %s \\
  \hline
  \rowcolor{tablerow} Статус & \textcolor{green}{\textbf{%s}} \\
  \hline
\end{tabular}

\vspace{1cm}
\begin{center}
  \small
  Спасибо за выбор нашей авиакомпании! \\
  Для получения дополнительной информации свяжитесь с нами: support@airline.com
\end{center}

\end{document}
''' % (
        ticket_data["id"],
        ticket_data["first_name"],
        ticket_data["last_name"],
        ticket_data["email"],
        ticket_data["airline"],
        ticket_data["departure"],
        ticket_data["destination"],
        ticket_data["departure_time"],
        ticket_data["arrival_time"],
        ticket_data["duration"],
        ticket_data["passengers"],
        ticket_data["price"],
        ticket_data["booking_date"],
        ticket_data["status"]
    )

    # Сохранение LaTeX в файл
    latex_file = f'ticket_{booking_id}.tex'
    with open(latex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    # Компиляция в PDF с использованием latexmk
    subprocess.run(['latexmk', '-pdf', latex_file], check=True)

    # Чтение сгенерированного PDF
    pdf_file = f'ticket_{booking_id}.pdf'
    with open(pdf_file, 'rb') as f:
        pdf_content = f.read()

    # Установка заголовков для скачивания PDF
    print(f"Content-Type: application/pdf")
    print(f"Content-Disposition: attachment; filename=ticket_{booking_id}.pdf")
    print(f"Content-Length: {len(pdf_content)}")
    print()

    # Отправка PDF
    print(pdf_content.decode('latin1'), end='')

    # Удаление временных файлов
    for ext in ['.tex', '.aux', '.log', '.out', '.pdf']:
        file_path = f'ticket_{booking_id}{ext}'
        if os.path.exists(file_path):
            os.remove(file_path)

except Exception as e:
    print("Content-Type: application/json")
    print()
    print(json.dumps({"success": false, "error": str(e)}))
finally:
    conn.close()
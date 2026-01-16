
import os
import sqlite3 as sq
import smtplib , ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
import pandas as pd

host = "smtp.gmail.com"
port = 465

context = ssl.create_default_context()

# --- POBIERANIE DANYCH Z ENV ---
username = os.environ.get('EMAIL_USERNAME')  # np. 'app.tferenc@gmail.com'
password = os.environ.get('EMAIL_PASSWORD')  # Gmail App Password (16 znaków, bez spacji)
receiver = os.environ.get('EMAIL_RECEIVER')  # np. 'ferenc.tomasz007@gmail.com'
db_path = os.environ.get('DB_PATH', 'data/database.db')  # domyślnie jak u Ciebie

if not username or not password or not receiver:
    raise ValueError("Brak wymaganych ENV: EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_RECEIVER")

def send_email(task_list, receiver_email):
    message = MIMEMultipart()
    message['From'] = username
    message['To'] = receiver_email
    message['Subject'] = "ebis_tm_backup"

    body = "Oto lista zadań przypadających na dzisiaj:<br><br>"
    body += "<table border='1'><tr><th>Name</th><th>Story ID</th><th>Estimate Date</th></tr>"
    for task in task_list:
        body += f"<tr><td>{task['name']}</td><td>{task['story_id']}</td><td>{task['estimate_date']}</td></tr>"
    body += "</table>"

    message.attach(MIMEText(body, 'html'))
    text = message.as_string()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver_email, text)

def get_tasks_from_db():
    # today = date.today().strftime("%Y-%m-%d")  # zostawiam na przyszłość, jakbyś chciał filtrować po dacie
    conn = sq.connect(db_path)

    # Twoje kryteria
    query = "SELECT * FROM tasks WHERE is_completed = 'false' and story_id = 176;"
    db_tasks = pd.read_sql_query(query, conn, dtype=str)

    tasks = [
        {
            "id": row['id'],
            "name": row['name'],
            "story_id": row['story_id'],
            "estimate_date": row['estimate_date']
        }
        for _, row in db_tasks.iterrows()
    ]
    conn.close()
    return tasks

def main():
    tasks = get_tasks_from_db()
    if tasks:
        send_email(tasks, receiver)
    else:
        print("Brak zadań do wysłania.")

if __name__ == "__main__":
    main()


import os
import sqlite3 as sq
import smtplib , ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
import pandas as pd
import utils.db as db 
from utils.secrets import get_secret






host = "smtp.gmail.com"
port = 465

context = ssl.create_default_context()

# --- POBIERANIE DANYCH Z ENV ---
username = get_secret("EMAIL_USERNAME", section="em")
password = get_secret("EMAIL_PASSWORD", section="em")
receiver = get_secret("EMAIL_RECEIVER", section="em")

if not username or not password or not receiver:
    raise ValueError("Brak wymaganych ENV: EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_RECEIVER")

def send_email(task_list, receiver_email):
    message = MIMEMultipart()
    message['From'] = username
    message['To'] = receiver_email
    message['Subject'] = "Lista zadan na dzisiaj"

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
    conn = db.pg_conn()

    # Twoje kryteria

    query = f"""
        SELECT t.*
        FROM {db.schema()}.tasks AS t
        LEFT JOIN {db.schema()}.stories AS s ON t.story_id = s.id
        WHERE 1=1
          AND s.est_start_date >= CURRENT_DATE
          AND s.est_end_date   >= CURRENT_DATE
          AND t.is_completed = 'false'
    """

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
    return tasks

def main():
    tasks = get_tasks_from_db()
    if tasks:
        send_email(tasks, receiver)
    else:
        print("Brak zadań do wysłania.")

if __name__ == "__main__":
    main()

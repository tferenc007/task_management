import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import imaplib
import email
from email.header import decode_header
import os

host = "smtp.gmail.com"
port = 465

context = ssl.create_default_context()
username = 'app.tferenc@gmail.com'
password = 'iyix czki wixf cafu'
receiver = 'app.tferenc@gmail.com'
attachment_dir = 'data/'

def send_email_with_attachment(body, attachment_path):

    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Create a multipart message
    message = MIMEMultipart()
    message['From'] = username
    message['To'] = receiver
    message['Subject'] = f"{current_timestamp};ebis_tm_backup"

    # Add body to email
    message.attach(MIMEText(body, 'plain'))

    # Open the file in binary mode
    with open(attachment_path, 'rb') as attachment:
        # Add file as application/octet-stream
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        'Content-Disposition',
        f'attachment; filename= database.db',
    )

    # Attach the file to the message
    message.attach(part)

    # Convert the message to a string and send it
    text = message.as_string()
    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, text)
def find_latest_email_and_save_attachment():
    # Connect to the server
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mail.select("inbox")

    # Search for all emails
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    latest_email_id = None
    latest_timestamp = None

    # Iterate through all emails to find the one with the latest timestamp in the subject
    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        # Decode the email subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")

        # Extract the timestamp from the subject
        try:
            timestamp_str = subject.split(";")[0]
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue

        # Update the latest email if this one is newer
        if latest_timestamp is None or timestamp > latest_timestamp:
            latest_timestamp = timestamp
            latest_email_id = email_id

    # Fetch the latest email and save its attachment
    if latest_email_id:
        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            if filename:
                filepath = os.path.join(attachment_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))

    # Logout and close connection
    mail.logout()

# Usage
# find_latest_email_and_save_attachment()

import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

host = "smtp.gmail.com"
port = 465

context = ssl.create_default_context()

def send_email_with_attachment(body, attachment_path):
    username = 'app.tferenc@gmail.com'
    password = 'iyix czki wixf cafu'
    receiver = 'app.tferenc@gmail.com'

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

# Usage
send_email_with_attachment(
    body='Please find the attached file.',
    attachment_path='data/database.db'
)
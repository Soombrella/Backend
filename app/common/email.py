import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USERNAME")       # example@gmail.com
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # 앱 비밀번호


def send_email(to_email: str, subject: str, content: str):
    print("SMTP_USER =", repr(SMTP_USER))
    print("SMTP_PASSWORD =", repr(SMTP_PASSWORD))


    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(content, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

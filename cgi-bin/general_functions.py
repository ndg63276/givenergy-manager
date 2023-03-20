import os
import json
import smtplib
from email.mime.text import MIMEText


def read_json():
    with open(os.path.join(os.path.dirname(__file__), "user_input.json"), "r") as f:
        j = json.load(f)
    return j


def get_headers(apikey):
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return headers


def send_email(subject, body):
    j = read_json()
    if j["email_address"] == "":
        print(body)
        return
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = j["email_address"]
    msg['To'] = j["email_address"]
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(j["email_address"], j["email_password"])
    smtp_server.sendmail(j["email_address"], j["email_address"], msg.as_string())
    smtp_server.quit()

import smtplib
from email.mime.text import MIMEText
from user_input import email_address, email_password


def get_headers(apikey):
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return headers


def send_email(subject, body):
    if email_address == "":
        print(body)
        return
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = email_address
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(email_address, email_password)
    smtp_server.sendmail(email_address, email_address, msg.as_string())
    smtp_server.quit()

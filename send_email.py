from bottle import template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from icecream import ic
from password import password_em


def send_email(to_email, from_email, subject, email_body, email, password):
    try:
        message = MIMEMultipart()
        message["To"] = to_email
        message["From"] = from_email
        message["Subject"] = subject

        messageText = MIMEText(email_body, 'html')
        message.attach(messageText)

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo('Gmail')
        server.starttls()
        server.login(email, password)
        server.sendmail(from_email, to_email, message.as_string())
        server.quit()

        return "success"
    except Exception as ex:
        ic(ex)
        return "error"
    

    ################ sending email for signup #############
def send_signup_email(user_email, verification_code):
    try:
        inputted_email=user_email
        verification_code = verification_code
        email_body = template("__email_signup", verification_code=verification_code, email=inputted_email)
        result = send_email(
        to_email='mathildeengb@gmail.com',
        from_email='mathildeengb@gmail.com',
        subject='Please verify',
        email_body=email_body,
        email='mathildeengb@gmail.com',
        password=password_em)
        return result
    except Exception as ex:
        ic(ex)
        return "error sending signup mail"
    

def send_reset_email(user_email, reset_token):
    try:
        email_body = template("__email_reset_password", reset_token=reset_token, email=user_email)
        result = send_email(
        to_email='mathildeengb@gmail.com',
        from_email='mathildeengb@gmail.com',
        subject='Reset password',
        email_body=email_body,
        email='mathildeengb@gmail.com',
        password=password_em)
        return result
    except Exception as ex:
        ic(ex)
        return "error sending reset mail"
    

def send_deletion_email(user_name):
    try:
        user_name=user_name
        email_body = template("__email_user_deleted", user_name= user_name)
        result = send_email(
        to_email='mathildeengb@gmail.com',
        from_email='mathildeengb@gmail.com',
        subject='Deletion confirmed',
        email_body=email_body,
        email='mathildeengb@gmail.com',
        password=password_em)
        return result
    except Exception as ex:
        ic(ex)
        return "error sending signup mail"

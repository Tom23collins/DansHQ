from msal import ConfidentialClientApplication
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_access_token(app):
    authority = f"https://login.microsoftonline.com/{app.config['TENANT_ID']}"
    client_app = ConfidentialClientApplication(
        app.config['CLIENT_ID'],
        app.config['CLIENT_SECRET'],
        authority=authority
    )
    result = client_app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if 'access_token' not in result:
        raise Exception(f"Failed to acquire token: {result.get('error_description')}")
    return result['access_token']

def send_welcome_email(app, recipient_email, first_name):
    try:
        access_token = get_access_token(app)

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = app.config['MAIL_USERNAME']
        msg['To'] = recipient_email
        msg['Subject'] = "Welcome to Flask Azure Quickstart!"
        body = f"Hi {first_name},\n\nThank you for signing up. We're excited to have you!"
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server
        smtp = smtplib.SMTP('smtp.office365.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(app.config['MAIL_USERNAME'], access_token)
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        smtp.quit()

    except Exception as e:
        app.logger.error(f"Failed to send email to {recipient_email}: {e}")

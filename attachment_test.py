import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
import time

# Set log file for the email attachment.
e_send = open(r'error_log.txt', 'a')
formatted_time = time.strftime("  %d-%m-%Y"   "  %T" "\n")
formatted_time_log = time.strftime("  %d-%m-%Y"   "  %T ")
e_send.write("AGC Commander Log file.   Start Time: ")
e_send.write(str(formatted_time))
start_time = datetime.now()
e_send.close()

def email_send():
    # Private environment variables.
    email_sender = os.environ.get('EMAIL_SENDER')
    email_password = os.environ.get('EMAIL_PASSWORD')
    email_receiver_one = os.environ.get('EMAIL_ONE')
    email_receiver_two = os.environ.get('EMAIL_TWO')

    # Email body and subject etc.
    subject = 'Transmitter fault in Finland'
    body = """  
    Hello. there has been an error detected with one or more of the transmitters in finland.
    Please see the attachment for more details.
    Don't have a good day, have a great day.   
    """
    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_receiver_one
    em['Subject'] = subject
    em.attach(MIMEText(body, "plain"))

    filename = "error_log.txt"
    attachment = open(filename, "rb")
    attachment_package = MIMEBase("application", "octet-stream")
    attachment_package.set_payload(attachment.read())
    encoders.encode_base64(attachment_package)
    attachment_package.add_header("Content-Disposition", "attachment; filename= " + filename)
    em.attach(attachment_package)
    text = em.as_string()

    # Setup email address plus port and passwords etc.
    tie_server = smtplib.SMTP('smtp.gmail.com', 587)
    tie_server.starttls()
    tie_server.login(email_sender, email_password)

    tie_server.sendmail(email_sender, email_receiver_one, text)
    tie_server.quit()


email_send()

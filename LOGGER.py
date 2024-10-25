import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
import time
import pandas as pd
import serial
# Set log file for the email attachment.
e_send = open(r'/home/radar_test/AGC/AGC_email/error_log.txt', 'a')
formatted_time = time.strftime("  %d-%m-%Y"   "  %T" "\n")
formatted_time_log = time.strftime("  %d-%m-%Y"   "  %T ")
e_send.write("AGC Commander Log file.   Start Time: ")
e_send.write(str(formatted_time))
start_time = datetime.now()
e_send.close()
radar_position = pd.read_csv("/home/radar_test/AGC/AGC_email/antenna_positions.csv")
ser = serial.Serial("/dev/ttyUSB0")
#ser = serial.Serial("COM1")
ser.baudrate = 9600
ser.bytesize = 8
ser.parity = 'N'
ser.stopbits = 1
ser.timeout = 1

packet_to_send = bytearray([0x55, 0x01, 0x01, 0x01, 0x03])
logging_check = bytearray([0xff])
packet_to_log = bytearray([0x55, 0x01, 0x01, 0x01, 0x03])

def email_send():
    # Private environment variables.
    # Email_receiver_two = os.environ.get('EMAIL_TWO')
    email_sender = os.environ.get('SENDER')
    email_password = os.environ.get('SENDER_P')
    email_receiver_one = os.environ.get('RECIPIENT')
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

    filename = "/home/radar_test/AGC/error_log.txt"
    attachment = open(filename, "rb")
    attachment_package = MIMEBase("application", "octet-stream")
    attachment_package.set_payload(attachment.read())
    encoders.encode_base64(attachment_package)
    attachment_package.add_header("Content-Disposition", "attachment; filename= " + filename)
    em.attach(attachment_package)
    text = em.as_string()

    # Setup email address plus port and passwords etc.
    gmail_server = smtplib.SMTP('smtp.gmail.com', 587)
    gmail_server.starttls()
    gmail_server.login(email_sender, email_password)

    gmail_server.sendmail(email_sender, email_receiver_one, text)
    gmail_server.quit()



def logging_stuff():
    e_send = open(r'/home/radar_test/AGC/error_log.txt', 'a')
    fault_counter = 0
    attempt_counter = 0

    for i in range(1):

        attempt_counter = attempt_counter + 1
        for radar in range(16):
            true_radar_position = (radar_position.loc[radar].at['agc'])
            rad_value = int(true_radar_position, 16)
            time_now = datetime.now()
            formatted_time = time_now.strftime("%d-%m-%Y"   "  %T")
            packet_to_send[1] = rad_value
            packet_to_send[3] = 0x01
            packet_to_send[4] = (sum(packet_to_send[1:4]))
            ser.write(packet_to_send)
            data_received = ser.readall()
            expected_response = packet_to_send[0:1]
            logging_check_two = logging_check[0:1]
            data_received_conv = data_received.hex()
            # tx_read = (packet_to_send).hex()
            # rx = str(data_received_conv)
            # tx = str(tx_read)
            # readout_rx = [rx[i:i + 2] for i in range(0, len(rx), 2)]
            # readout_tx = [tx[i:i + 2] for i in range(0, len(tx), 2)]
            # print(data_received_conv)

            if data_received[0:1] == expected_response:
                e_send.write("ANTENNA: ")
                e_send.write(str(radar + 1))
                e_send.write(" Responded to Packet_sent ok. ")
                if data_received[14:15] == logging_check_two:
                    e_send.write("Recevied 0xFF so All ok ")
                    e_send.write(str(formatted_time))
                    e_send.write("\n")
                else:
                    fault_counter = fault_counter + 1
                    e_send.write("ANTENNA: ")
                    e_send.write(str(radar + 1))
                    e_send.write(" Check Status of Transmitter")
                    e_send.write(str(formatted_time))
                    e_send.write("\n")

            else:
                fault_counter = fault_counter + 1
                #print("No Response from AGC_TX")
                e_send.write(f"ANTENNA: ")
                e_send.write(str(radar + 1))
                e_send.write(" No Response from Transmitter ")
                e_send.write(str(formatted_time))
                e_send.write("\n")

        if fault_counter > 0:
            e_send.close()
            #print(fault_counter)
            #print(attempt_counter)
            email_send() #Hash this out if you dont want to get emails while fault finding.


logging_stuff()












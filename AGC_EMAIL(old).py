# AGC COMMANDER EMAIL MODULE
# CASSIE LAKIN
# 14_10_2022
# V1.1

# This module will run in the background whilst the radar is running and email any faults found.
# The module scans through and sends a status packet to each of the radar positions.
# It then records all packets received and checks for validity.
# The module crates a log file of each of the transmitters. any faults are emailed to a specified addresses to alert of
# possible faults.
# an email will only occur when there is a fault
# The email should contain an alert of which transmitter is acting up.

# Module imports
from datetime import datetime
import sys
import serial
import threading, time
from email.message import EmailMessage
import ssl
import smtplib
import os
import pandas as pd

ser = serial.Serial("/dev/ttyUSB0")
ser.baudrate = 9600
ser.bytesize = 8
ser.parity = 'N'
ser.stopbits = 1
ser.timeout = 1
radar_position = pd.read_csv("antenna_positions.csv")

# Main Data String Array in bytes.
# 0 "STX" byte is always 55(hex).
# 1 "addr" is target microcontroller address in the range 1-254 decimal.
# 2 "Len" is the length of the data field. This is always 1 for command packets.
# 3 "cmd" is the command number 1-13.
# 4 "bcc" is the block checksum. This is the least significant 8 bits of the sum of bytes 1-3.

# this is the main packet. It will change depending on commands.
packet_to_send = bytearray([0x55, 0x01, 0x01, 0x01, 0x03])
logging_check = bytearray([0xff])
packet_to_log = bytearray([0x55, 0x01, 0x01, 0x01, 0x03])

#opens log file and starts a title and start time and closes file.
log_file = open(r'log_file.txt', 'a')
formatted_time = time.strftime("  %d-%m-%Y"   "  %T" "\n")
formatted_time_log = time.strftime("  %d-%m-%Y"   "  %T ")
log_file.write("AGC Commander Log file.   Start Time: ")
log_file.write(str(formatted_time))
start_time = datetime.now()
log_file.close()

# As above but this log file is attached to email if a fault is discovered.
e_send = open(r'e_send.txt', 'a')
formatted_time = time.strftime("  %d-%m-%Y"   "  %T" "\n")
formatted_time_log = time.strftime("  %d-%m-%Y"   "  %T ")
e_send.write("AGC Commander Log file.   Start Time: ")
e_send.write(str(formatted_time))
start_time = datetime.now()
e_send.close()

log_file = open(r'log_file.txt', 'a')
e_send = open(r'e_send.txt', 'a')
email_sender = os.environ.get('EMAIL_SENDER')
email_password = os.environ.get('EMAIL_PASSWORD')
email_receiver_one = os.environ.get('EMAIL_ONE')
email_receiver_two = os.environ.get('EMAIL_TWO')
# Below will not be actual email or password, but environment variables that can be called.
def email_send():

        #email_sender = '' #environment variable in work comp
        #email_password = ''          #environment variable in work computer

        # Below is a list of the email addresses to send to. may also be environment variables.
        #email_receiver = ('')
        subject = 'TRANSMITTER FAULT!'
        body = """THERE APPEARS TO BE A PROBLEM WITH ONE OF THE TRANSMITTERS. check attachment"""
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver_one
        em['Subject'] = subject
        em.set_content(body)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver_one, em.as_string())


def logging_stuff():
    log_file = open(r'log_file.txt', 'a')
    e_send = open(r'e_send.txt', 'a')
    for radar in range(16):
        true_radar_position = (radar_position.loc[radar].at['agc'])
        rad_value = int(true_radar_position, 16)
        time_now = datetime.now()
        formatted_time = time_now.strftime("%d-%m-%Y"   "  %T")
        packet_to_send[1] = (rad_value)
        packet_to_send[3] = 0x01
        packet_to_send[4] = (sum(packet_to_send[1:4]))
        ser.write(packet_to_send)
        data_received = ser.readall()
        expected_response = packet_to_send[0:1]
        logging_check_two = logging_check[0:1]
        data_received_conv = (data_received).hex()
        tx_read = (packet_to_send).hex()
        rx = str(data_received_conv)
        tx = str(tx_read)
        readout_rx = [rx[i:i + 2] for i in range(0, len(rx), 2)]
        readout_tx = [tx[i:i + 2] for i in range(0, len(tx), 2)]
        print(data_received_conv)
        if data_received[0:1] == expected_response:
            log_file.write("AGC: ")
            log_file.write(str(radar))
            log_file.write(" Responded to Packet_sent ok. ")
            if data_received[14:15] == logging_check_two:
                log_file.write("Recevied 0xFF so All ok ")
                log_file.write(str(formatted_time))
                log_file.write("\n")
                e_send.write("AGC:")
                e_send.write(str(radar))
                e_send.write(" Working ok ")
                e_send.write(str(formatted_time))
                e_send.write("\n")

            else:
                log_file.write("AGC: ")
                log_file.write(str(radar))
                log_file.write(" Check Status of Transmitter")
                log_file.write(str(formatted_time))
                log_file.write("\n")

                e_send.write("AGC: ")
                e_send.write(str(radar))
                e_send.write(" Check Status of Transmitter")
                e_send.write(str(formatted_time))
                e_send.write("\n")
                #e_send.close()
                #email_send()

        else:
            print("No Response from AGC_TX")
            log_file.write("AGC: ")
            log_file.write(str(radar))
            log_file.write(" No Response from Transmitter ")
            log_file.write(str(formatted_time))
            log_file.write("\n")

            e_send.write("AGC: ")
            e_send.write(str(radar))
            e_send.write(" No Response from Transmitter ")
            e_send.write(str(formatted_time))
            e_send.write("\n")
            #e_send.close()
            #email_send()
    log_file.close()
    e_send.close()



logging_stuff()

email_send()

# still to do:
# actually attach the "e_send.txt" before sending.
# set up second email receiver for either julian or matt.
# set conditions for email alerts.
# does this log need to be deleted after so many days to prevent the hdd filling. Its only really needed for analytics?
# should it email a copy of this log every month and then create a new one and delete the old so i can keep a copy on my
# one drive?
# Use cron scheduler to run this once an hour.

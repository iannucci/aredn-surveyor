# AREDN Wardriving
#
# 2024-0815 (c) Bob Iannucci

import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import sqlite3
import time
import pynmea2
import io
import serial

nodeIP = '10.5.222.97'
username = "root"
password = "SurSocNet99"
databasePath = '/Users/bob/Documents/AREDN/AREDN Signal Strength.db'
gpsPort = '/dev/tty.usbmodem14201'
gpsBaudRate = 115200
antenna = 'Bullet'
mounting = '4Runner'

class Logger():
    def __init__ (self, databasePath):
        self.databasePath = databasePath
        self.connection = None
        self.cursor = None
        
    def connect(self):
        try:
            self.connection = sqlite3.connect(self.databasePath)
            self.cursor = self.connection.cursor()
        except Exception as e:
            print('connect() failed: %s' % e)
            self.disconnect()
        
    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = None
        self.cursor = None
        
    def log(self, nodeName, nodeMAC, nodeMode, ssid, snr, signal, channel, latitude, longitude, antenna, mounting):
        insertStatement = 'INSERT INTO Readings ('\
        'Node_Name, '\
        'Node_MAC_Address, '\
        'Node_Mode, '\
        'SSID, '\
        'SNR, '\
        'Signal, '\
        'Channel, '\
        'Receiver_Latitude, '\
        'Receiver_Longitude, '\
        'Receiver_Antenna, '\
        'Receiver_Mounting, '\
        'Time ) '\
        'VALUES ("%s", "%s", "%s", "%s", %d, %d, %d, %f, %f, "%s", "%s", %d)' % (nodeName, nodeMAC, nodeMode, ssid, snr, signal, channel, latitude, longitude, antenna, mounting, int(time.time()), )
        try:
            if self.connection is None:
                self.connect()
            self.cursor.execute(insertStatement)
            self.connection.commit()
        except Exception as e:
            print('log() failed: %s' % e)
            self.disconnect()

def fetch_wifi_survey(host):
    '''
    Accesses the node's WiFi survey page, scrapes it, and
    returns a dictionary of the surveyed stations
    '''
    url = 'http://%s/cgi-bin/scan' % (host,)
    html = requests.get(url, auth=(username, password))
    soup = BeautifulSoup(html.text, 'html.parser')
    tables = pd.read_html(StringIO(str(soup)))
    table = tables[0].transpose().to_dict()
    return table

def fetch_position():   
    ser = serial.Serial(gpsPort, gpsBaudRate, timeout=5.0)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

    while 1:
        try:
            line = sio.readline()
            if (line[:6] == "$GPGGA"):
                msg = pynmea2.parse(line)
                # print(msg.latitude)
                # print(msg.longitude)
                return msg
        except serial.SerialException as e:
            print('Device error: {}'.format(e))
            break
        except pynmea2.ParseError as e:
            print('Parse error: {}'.format(e))
            continue

try:
    logger = Logger(databasePath)
    while True:
        readings = fetch_wifi_survey(nodeIP)
        position = fetch_position()
        for index, r in readings.items():
            logger.log(r['Hostname'], r['MAC/BSSID'], r['802.11 Mode'], r['SSID'], r['SNR'], r['Signal'], r['Chan'], position.latitude, position.longitude, antenna, mounting)
except KeyboardInterrupt:
    logger.disconnect()
    print('\nDone')
except Exception as e:
    print('Abnormal termination: %s' % e)


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

class Logger():
    def __init__ (self, databasePath):
        self.databasePath = databasePath
        
    def connect(self):
        self.connection = sqlite3.connect(self.databasePath)
        self.cursor = self.connection.cursor()
        
    def disconnect(self):
        self.connection.close()
        
    def log(self, nodeName, nodeMAC, nodeMode, ssid, snr, signal, channel, latitude, longitude):
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
        'Time ) '\
        'VALUES ("%s", "%s", "%s", "%s", %d, %d, %d, %f, %f, %d)' % (nodeName, nodeMAC, nodeMode, ssid, snr, signal, channel, latitude, longitude, int(time.time()), )
        self.cursor.execute(insertStatement)
        self.connection.commit() 

def test_sqlite_insert(databasePath):
    logger = Logger(databasePath)
    logger.connect()
    logger.log('Test Node 2', '01:23:45:67:89:AB', 'Connected Ad-Hoc Station', 'AREDN-10-v3', 30, -60, 175, 37.0401, -122.1296)
    logger.disconnect()  

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
    # test_sqlite_insert(databasePath)
    logger = Logger(databasePath)
    logger.connect()
    while True:
        readings = fetch_wifi_survey(nodeIP)
        position = fetch_position()
        for index, r in readings.items():
            logger.log(r['Hostname'], r['MAC/BSSID'], r['802.11 Mode'], r['SSID'], r['SNR'], r['Signal'], r['Chan'], position.latitude, position.longitude)
except KeyboardInterrupt:
    logger.disconnect()
    print('\nDone')


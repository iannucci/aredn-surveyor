# Component of aredn_wardiving by Bob Iannucci
#
# See LICENSE.md for license information

import sqlite3
import time

class AREDNLogger():
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
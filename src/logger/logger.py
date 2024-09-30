# Component of aredn_wardiving by Bob Iannucci
#
# See LICENSE.md for license information

import sqlite3
import time
from src.debugger.debug_log import debugLog

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Logger():
    def __init__ (self, databasePath):
        self.databasePath = databasePath
        self.connection = None
        self.cursor = None
        
    # Should only be called internally
    def _connect(self):
        try:
            self.connection = sqlite3.connect(self.databasePath, check_same_thread=False)
            self.connection.row_factory = dict_factory
            self.cursor = self.connection.cursor()
        except Exception as e:
            debugLog('[logger] connect() failed: %s', (e,))
            self._disconnect()
        
    # Should only be called internally
    def _disconnect(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = None
        self.cursor = None
        
    # **FIXME** Need an input queue that provides access to this method
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
                self._connect()
            self.cursor.execute(insertStatement)
            self.connection.commit()
        except Exception as e:
            debugLog('[logger] log() failed: %s', (e,))
            self._disconnect()
         
    # **FIXME** Need an input queue that provides access to this method   
    def query(self, nodeName=None, nodeMAC=None, ssid=None, channel=None, startTime=None, stopTime=None):
        priorWhere = False
        selectStatement = 'SELECT * FROM Readings '
        if (nodeName is not None):
            selectStatement += ' WHERE Node_Name = "%s"' % (nodeName,)
            priorWhere = True
        if (nodeMAC is not None):
            if (priorWhere):
                selectStatement += ' AND Node_MAC_Address = "%s"' % (nodeMAC,)
            else:
                selectStatement += ' WHERE Node_MAC_Address = "%s"' % (nodeMAC,)
                priorWhere = True
        if (ssid is not None):
            if (priorWhere):
                selectStatement += ' AND SSID = "%s"' % (ssid,)
            else:
                selectStatement += ' WHERE SSID = "%s"' % (ssid,)
                priorWhere = True
        if (channel is not None):
            if (priorWhere):
                selectStatement += ' AND Channel = "%s"' % (channel,)
            else:
                selectStatement += ' WHERE Channel = "%s"' % (channel,)
                priorWhere = True
        if (startTime is not None) and (stopTime is not None):
            if (priorWhere):
                selectStatement += ' AND TIME >= %s AND TIME <= %s' % (startTime, stopTime,)
            else:
                selectStatement += ' WHERE TIME >= %s AND TIME <= %s' % (startTime, stopTime,)
        try:
            if self.connection is None:
                self._connect()
            self.cursor.execute(selectStatement)
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            debugLog('[logger] log() failed: %s', (e,))
            self._disconnect()
            
    def databaseToPoints(self, records):
        points = []
        for record in records:
            latitude = float(record['Receiver_Latitude'])
            longitude = float(record['Receiver_Longitude'])
            # pointString = 'new google.maps.LatLng(%s, %s)' % (latitude, longitude,)
            points.append( { 'lat': latitude, 'lng': longitude } )
        return points
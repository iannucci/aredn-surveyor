# Component of AREDN Survey by Bob Iannucci
#
# See LICENSE.md for license information

import pynmea2
import io
import serial
import math
import time
import threading
import configparser
import pathlib
from src.debugger.debug_log import debugLog, debugError

projectDir = pathlib.Path(__file__).parent.parent.resolve()
thisDir = pathlib.Path(__file__).parent.resolve()
configPath = '%s/config/config.ini' % projectDir
config = configparser.ConfigParser()
config.read(configPath)
maxGPSTries = 10

class GPS():
    # Save state information but do not create a thread
    def __init__(self, serialPort, baudRate):
        self.serialPort = serialPort
        self.baudRate = baudRate
        self.lastPosition = None
        self.lastPositionUTC = None
        self.pollingThread = None
        self.serialConnection = None
        self.serialIO = None
        self.staleReadingLogSeconds = 10
        
    # If no thread already, create one and start it
    def start(self):
        debugLog('[gps] Starting GPS')
        if (self.pollingThread is None):
            self.pollingThread = threading.Thread(target=self.pollingLoop, args=())
            self.pollingThread.start()
            return True
        else:
            return False
        
    # If thread exists, stop it
    def stop(self):
        debugLog('[gps] Stopping GPS')
        if (self.pollingThread is not None):
            self.pollingThread.join()
            self.pollingThread = None
            self.lastPosition = None
            self.lastPositionUTC = None
            return True
        else:
            return False
        
    # Returns (lastPosition, ageInSeconds) 
    def query(self):
        if (self.lastPosition is not None):
            return (self.lastPosition, time.time() - self.lastPositionUTC)
        else:
            return (None, None)
        
    def pollingLoop(self):
        def establishSerialIO():
            # Establish connection to the GPS module
            try:
                self.serialConnection = serial.Serial(self.serialPort, self.baudRate, timeout=float(config['gps']['gpsSerialTimeoutSeconds']))
                self.serialIO = io.TextIOWrapper(io.BufferedRWPair(self.serialConnection, self.serialConnection))
                time.sleep(5)
                self.serialConnection.reset_input_buffer()
                return True
            except Exception as e:
                debugLog('[gps] Serial error: %s', (e,))
                debugError(e)
                self.self.serialConnection = None
                self.serialIO = None
                return False
            
        def getPosition():
            # Might have to read a couple lines from the GPS before getting
            # a $GPGGA or $GPRMC NMEA message
            lines = []
            for i in range(maxGPSTries):
                try:
                    line = self.serialIO.readline()
                    # debugLog('[gps] GPS says %s', (line,))
                    lines.append(line)
                    if (line[:6] == "$GPGGA") or (line[:6] == "$GPRMC") or (line[:6] == "$GNGLL"):
                        position = pynmea2.parse(line)
                        self.lastPosition = position
                        self.lastPositionUTC = time.time()
                        # debugLog('[gps] Position: Lat: %f  Lon: %f', (position.latitude, position.longitude,))
                    return True
                except serial.SerialException as e:
                    debugLog('[gps] Device error: %s', (e,))
                    debugError(e)
                    return False
                except pynmea2.ParseError as e:
                    # debugLog('[gps] Parse error: %s', (e,))
                    # debugError(e)
                    return False
                except Exception as e:
                    debugLog('[gps] Other error: %s', (e,))
                    self.serialConnection.reset_input_buffer()
                    debugError(e)
                    return False
            if (time.time() - self.lastPositionUTC > 10):
                debugLog('[gps] No valid GPS readings in the last %d seconds', (self.staleReadingLogSeconds,))
            return False
        
        # Main loop -- repeat until the thread is stopped
        while True:
            try:
                # Open a serial connection
                while not establishSerialIO():
                    # Something went wrong -- wait a bit so as not to flood the log, then retry
                    time.sleep(int(config['gps']['gpsSleepOnErrorSeconds']))
                # With a valid serial connection, continually read position
                while getPosition():
                    pass
            except Exception as e:
                debugLog('[gps] GPS thread error, re-starting: %s', (e,))
                debugError(e)
            finally:
                # Before looping back, close the serial port so that it can be re-opened afresh
                self.serialConnection.close()
                self.serialConnection = None
                self.serialIO = None
                continue

    def distanceInMeters(self, position1, position2):
        lat1 = position1.latitude
        lon1 = position1.longitude
        lat2 = position2.latitude
        lon2 = position2.longitude
        
        dLat = (lat2 - lat1) * math.pi / 180.0
        dLon = (lon2 - lon1) * math.pi / 180.0
    
        # convert to radians
        lat1 = (lat1) * math.pi / 180.0
        lat2 = (lat2) * math.pi / 180.0
    
        # apply formulae
        a = (pow(math.sin(dLat / 2), 2) +
            pow(math.sin(dLon / 2), 2) *
                math.cos(lat1) * math.cos(lat2));
        rad = 6371
        c = 2 * math.asin(math.sqrt(a))
        return rad * c * 1000
# Component of aredn_wardiving by Bob Iannucci
#
# See LICENSE.md for license information

import pynmea2
import io
import serial
import math

class GPS():
    def __init__(self, serialPort, baudRate):
        self.serialPort = serialPort
        self.baudRate = baudRate
        
    def query(self):   
        ser = serial.Serial(self.serialPort, self.baudRate, timeout=5.0)
        sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

        while 1:
            try:
                line = sio.readline()
                if (line[:6] == "$GPGGA"):
                    msg = pynmea2.parse(line)
                    return msg
            except serial.SerialException as e:
                print('Device error: {}'.format(e))
                break
            except pynmea2.ParseError as e:
                print('Parse error: {}'.format(e))
                continue
            except e:
                print('Other error: {}'.format(e))
            
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
        return rad * c
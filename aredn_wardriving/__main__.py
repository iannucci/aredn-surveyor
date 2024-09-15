# Component of aredn_wardiving by Bob Iannucci
#
# See LICENSE.md for license information

import math
import time
import configparser
import pathlib
import threading
import aredn_wardriving.logger as l
import aredn_wardriving.surveyor as s
import aredn_wardriving.gps as g
import aredn_wardriving.webserver as w

thisDir = pathlib.Path(__file__).parent.resolve()
configPath = '%s/conf/config.ini' % thisDir
config = configparser.ConfigParser()
config.read(configPath)
logger = l.Logger(config['database']['databasePath'])
surveyor = s.Surveyor(config['aredn']['nodeIP'], config['aredn']['username'], config['aredn']['password'])
gps = g.GPS(config['gps']['gpsPort'], config['gps']['gpsBaudRate'])

def logging():
    positionOfLastLogEntry = None
    while True:
        readings = surveyor.query()
        position = gps.query()
        if (position.latitude == 0 and position.longitude == 0):
            continue
        if (positionOfLastLogEntry is None) or (gps.distanceInMeters(position, positionOfLastLogEntry) >= int(config['application']['minMetersToMove'])):
            for index, r in readings.items():
                if math.isnan(r['SNR']):
                    continue
                logger.log(r['Hostname'], r['MAC/BSSID'], r['802.11 Mode'], r['SSID'], r['SNR'], r['Signal'], r['Chan'], position.latitude, position.longitude, config['receiver']['antenna'], config['receiver']['mounting'])
            positionOfLastLogEntry = position
            time.sleep(int(config['application']['secondsToSleep']))

try:
    loggingThread = threading.Thread(target=logging, args=())
    wesbserverThread = threading.Thread(target=w.webserver, args=())
    loggingThread.start()
    wesbserverThread.start()
except KeyboardInterrupt:
    print('\nDone')
except Exception as e:
    print('Abnormal termination: %s' % e)
finally:
    loggingThread.join()
    wesbserverThread.join()
    logger.disconnect()

# Component of AREDN Survey by Bob Iannucci
#
# See LICENSE.md for license information

import math
import time
import configparser
import pathlib
import threading
from src.logger.logger import Logger
from src.collector.collector import Collector
from src.positioner.gps import GPS
from src.webserver.webserver import webserver
from src.debugger.debug_log import debugLog

projectDir = pathlib.Path(__file__).parent.parent.resolve()
thisDir = pathlib.Path(__file__).parent.resolve()
configPath = '%s/config/config.ini' % projectDir
config = configparser.ConfigParser()
config.read(configPath)
logger = Logger(config['database']['databasePath'])
surveyor = Collector(config['aredn']['nodeIP'], config['aredn']['username'], config['aredn']['password'])
gps = GPS(config['gps']['gpsPort'], config['gps']['gpsBaudRate'])

def logging():
    positionOfLastLogEntry = None
    while True:
        readings = surveyor.query()
        (position, ageInSeconds) = gps.query()
        #
        # **FIXME** Need to use ageInSeconds
        #
        if (position is None):
            debugLog('[main] GPS position is unknown -- skipping')
            sleepSeconds = float(config['application']['secondsToSleepNothingToLog'])
            time.sleep(sleepSeconds)
            continue
        if (position.latitude == 0 and position.longitude == 0):
            debugLog('[main] GPS position is invalid -- skipping')
            sleepSeconds = float(config['application']['secondsToSleepNothingToLog'])
            time.sleep(sleepSeconds)
            continue
        
        distanceInMeters = gps.distanceInMeters(position, positionOfLastLogEntry or position)
        
        if ((positionOfLastLogEntry is None) or 
            (distanceInMeters >= float(config['application']['minMetersToMove']))):
            if (positionOfLastLogEntry is None):
                debugLog('[main] Creating initial log entry')
            else:
                debugLog('[main] Creating log entry because we have moved %.1f meters', (distanceInMeters,))
            nReadings = len(readings)
            if nReadings == 0:
                debugLog('[main] No signal -- recording position only')
                logger.log('No signal', '', '', '', -100, -100, 0, position.latitude, position.longitude, config['receiver']['antenna'], config['receiver']['mounting'])
            else:
                debugLog('[main] %d readings', (nReadings,))
                for index, r in readings.items():
                    if math.isnan(r['SNR']):
                        debugLog('[main] SNR is invalid -- skipping')
                        continue
                    logger.log(r['Hostname'], r['MAC/BSSID'], r['802.11 Mode'], r['SSID'], r['SNR'], r['Signal'], r['Chan'], position.latitude, position.longitude, config['receiver']['antenna'], config['receiver']['mounting'])
            positionOfLastLogEntry = position
        sleepSeconds = float(config['application']['secondsToSleepAfterLogging'])
        time.sleep(sleepSeconds)
        
        
        
try:
    loggingThread = threading.Thread(target=logging, args=())
    wesbserverThread = threading.Thread(target=webserver, args=())
    #
    # Future: log reader in its own thread
    #         Create a time-stamped queue of readings from the log thread
    #         Periodically pop the queue and check the GPS
    #           * If no (or stale) position
    #               Discard the readings
    #               Remove our map pin
    #           * else 
    #               Move our map pin to our position
    #               If we have not moved enough since the last database entry, 
    #                 Discard the readings
    #                 Color our map pin red
    #               else 
    #                 Put the readings and position in the database
    #                 Color our map pin green
    #
    debugLog('[main] Starting logging thread')
    loggingThread.start()
    debugLog('[main] Starting webserver thread')
    wesbserverThread.start()
    debugLog('[main] Starting GPS thread')
    gps.start()
except KeyboardInterrupt:
    debugLog('[main] \nDone')
except Exception as e:
    debugLog('[main] Abnormal termination: %s', (e,))
    gps.stop()
    loggingThread.join()
    wesbserverThread.join()
    logger.disconnect()

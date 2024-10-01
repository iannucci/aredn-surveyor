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
from src.webserver.webserver import Webserver
from src.debugger.debug_log import debugLog

class Surveyor():
    def __init__(self):
        self.projectDir = pathlib.Path(__file__).parent.parent.resolve()
        self.thisDir = pathlib.Path(__file__).parent.resolve()
        self.configPath = '%s/config/config.ini' % self.projectDir
        self.config = configparser.ConfigParser()
        self.config.read(self.configPath)
        self.logger = Logger(self.config['database']['databasePath'])
        self.collector = Collector(self.config['aredn']['nodeIP'], self.config['aredn']['username'], self.config['aredn']['password'])
        self.gps = GPS(self.config['gps']['gpsPort'], self.config['gps']['gpsBaudRate'])
        self.webserver = Webserver(self)
        self.loggingThread = None
        self.wesbserverThread = None
        self.enabled = False
        
    def start(self):
        self.loggingThread = threading.Thread(target=self.loop, args=())
        self.wesbserverThread = threading.Thread(target=self.webserver.start, args=())
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
        self.loggingThread.start()
        debugLog('[main] Starting webserver thread')
        self.wesbserverThread.start()
        debugLog('[main] Starting GPS thread')
        self.gps.start()
    
    def stop(self):
        self.gps.stop()
        self.loggingThread.join()
        self.wesbserverThread.join()
        self.logger._disconnect()
        
    def startSession(self, sessionName):
        self.sessionName = sessionName
        self.logger.createSession(sessionName)
        self.enabled = True
        
    def stopSession(self):
        self.enabled = False
        
    def loop(self):
        positionOfLastLogEntry = None
        prefix = self.config['aredn']['ssidPrefix']
        while True:
            while self.enabled:
                readings = self.collector.query()
                (position, ageInSeconds) = self.gps.query()
                #
                # **FIXME** Need to use ageInSeconds
                #
                if (position is None):
                    debugLog('[main] GPS position is unknown -- skipping')
                    sleepSeconds = float(self.config['application']['secondsToSleepNothingToLog'])
                    time.sleep(sleepSeconds)
                    continue
                if (position.latitude == 0 and position.longitude == 0):
                    debugLog('[main] GPS position is invalid -- skipping')
                    sleepSeconds = float(self.config['application']['secondsToSleepNothingToLog'])
                    time.sleep(sleepSeconds)
                    continue
                
                distanceInMeters = self.gps.distanceInMeters(position, positionOfLastLogEntry or position)
                
                if ((positionOfLastLogEntry is None) or 
                    (distanceInMeters >= float(self.config['application']['minMetersToMove']))):
                    if (positionOfLastLogEntry is None):
                        debugLog('[main] Creating initial log entry')
                    else:
                        debugLog('[main] Creating log entry because we have moved %.1f meters', (distanceInMeters,))
                    nReadings = len(readings)
                    nReadingsLogged = 0
                    for index, r in readings.items():
                        if math.isnan(r['SNR']) or not isinstance(r['SSID'], str):
                            # debugLog('[main] Invalid reading -- skipping')
                            continue
                        if r['SSID'].startswith(prefix):
                            self.logger.log(r['Hostname'], r['MAC/BSSID'], r['802.11 Mode'], r['SSID'], r['SNR'], r['Signal'], r['Chan'], position.latitude, position.longitude, self.config['receiver']['antenna'], self.config['receiver']['mounting'])
                            nReadingsLogged += 1
                    if nReadingsLogged == 0:
                        debugLog("[main] No nodes that match '%s' -- recording position only", (prefix,))
                        self.logger.log('No signal', '', '', '', -100, -100, 0, position.latitude, position.longitude, self.config['receiver']['antenna'], self.config['receiver']['mounting'])
                    else:
                        debugLog("[main] Logged %d reading(s) matching '%s'", (nReadingsLogged, prefix,))
                    positionOfLastLogEntry = position
                    # **FIXME** Update the session table stop time
                    self.logger.updateSessionStopTime(time.time())
                sleepSeconds = float(self.config['application']['secondsToSleepAfterLogging'])
                time.sleep(sleepSeconds)
            else:
                self.sessionName = None
            sleepSeconds = float(self.config['application']['secondsToSleepWhileDisabled'])
            time.sleep(sleepSeconds)

try:
    surveyor = Surveyor()
    surveyor.start()
except KeyboardInterrupt:
    debugLog('[main] \nDone')
except Exception as e:
    debugLog('[main] Abnormal termination: %s', (e,))
finally:
    surveyor.stop()

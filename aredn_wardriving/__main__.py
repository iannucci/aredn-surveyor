# Component of aredn_wardiving by Bob Iannucci
#
# See LICENSE.md for license information

import time
import configparser
import pathlib
import aredn_wardriving.aredn_logger as Logger
import aredn_wardriving.aredn_neighbor_surveyor as Surveyor
import aredn_wardriving.usb_gps as GPS

thisDir = pathlib.Path(__file__).parent.resolve()
configPath = '%s/conf/config.ini' % thisDir
config = configparser.ConfigParser()
config.read(configPath)
logger = Logger.AREDNLogger(config['database']['databasePath'])
surveyor = Surveyor.AREDNNeighborSurveyor(config['aredn']['nodeIP'], config['aredn']['username'], config['aredn']['password'])
gps = GPS.USBGPS(config['gps']['gpsPort'], config['gps']['gpsBaudRate'])

try:
    positionOfLastLogEntry = None
    while True:
        readings = surveyor.query()
        position = gps.query()
        if (positionOfLastLogEntry is None) or (gps.distanceInMeters(position, positionOfLastLogEntry) >= int(config['application']['minMetersToMove'])):
            for index, r in readings.items():
                logger.log(r['Hostname'], r['MAC/BSSID'], r['802.11 Mode'], r['SSID'], r['SNR'], r['Signal'], r['Chan'], position.latitude, position.longitude, config['receiver']['antenna'], config['receiver']['mounting'])
            positionOfLastLogEntry = position
            time.sleep(int(config['application']['secondsToSleep']))
except KeyboardInterrupt:
    print('\nDone')
except Exception as e:
    print('Abnormal termination: %s' % e)
finally:
    logger.disconnect()

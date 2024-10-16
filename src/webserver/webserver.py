# Component of AREDN Survey by Bob Iannucci
#
# See LICENSE.md for license information

from flask import Flask, send_from_directory, request
import configparser as c
import pathlib
import sys
import os

projectDir = pathlib.Path(__file__).parent.parent.resolve()
moduleDir = '%s/src' % projectDir
configFilePath = '%s/config/config.ini' % projectDir
sys.path.append(os.fspath(projectDir))
surveyor = None
sessionName = ''

config = c.ConfigParser()
config.read(configFilePath)

import logger.logger as l
import webserver.map_helper as m
from src.debugger.debug_log import debugLog

app = Flask(__name__)

config = c.ConfigParser()
config.read(configFilePath)
logger = l.Logger(config['database']['databasePath'])
mapHelper = m.MapHelper()

@app.route("/")
def surveyor():
    return send_from_directory('www', 'surveyor.html')

@app.route('/logging', methods=['POST'])
def logging():
    global surveyor
    global sessionName
    dataDict = request.json
    # We make two passes over the dataDict:
    #   the first pass only checks for validity
    #   the second pass, if the first is successful, makes the changes
    invalid = not surveyor
    for key, value in dataDict.items():
        match key:
            case 'logging':
                pass
            case _:
                invalid = True
                
    if invalid: 
        return { 'valid': False }
    else:
        for key, value in dataDict.items():
            match key:
                case 'logging':
                    match value:
                        case 'stop':
                            loggingEnabled = False
                            surveyor.stopSession()
                            sessionName = ''
                            return { 'valid': True }
                        case 'query':
                            return { 'valid': True,
                                    'sessionName': sessionName }
                        case _:
                            # Maybe 'start' case -- look for sessionName
                            if ('sessionName' in value):
                                loggingEnabled = True
                                sessionName = value['sessionName']
                                surveyor.startSession(sessionName)
                                return { 'valid': True }
                            else:
                                return { 'valid': False }
                case _:
                    return { 'valid': False }

@app.route('/point-data', methods=['POST'])
def pointData():
    validStart = False
    validStop = False
    dataDict = request.json
    for key, value in dataDict.items():
        match key:
            case 'startTime':
                if validUTC(value):
                    startTime = value
                    validStart = True
            case 'stopTime':
                if validUTC(value):
                    stopTime = value
                    validStop = True
    if (not validStart) or (not validStop) or (startTime > stopTime):
        return { 'valid': False }
    result = logger.query(startTime = startTime, stopTime = stopTime)
    if (result == []):
        debugLog('[webserver] No points in the database match the query.')
        points = []
        latitude = float(config['map']['defaultCenterLatitude'])
        longitude = float(config['map']['defaultCenterLongitude'])
        zoomLevel = int(config['map']['defaultZoomLevel'])
        center = { 'lat': latitude, 'lng': longitude }
        serverResponse = { 'center': center, 'zoom': zoomLevel, 'points': points }
    else:
        points = logger.databaseToPoints(result)
        bounds = mapHelper.boundingRectangle(points)
        mapDimPixels = { 'height': 1000, 'width': 800 }
        mapSettings = mapHelper.boundsToCenterZoom(bounds, mapDimPixels)
        serverResponse = { 'center': mapSettings['center'], 'zoom': mapSettings['zoom'] , 'points': points }
    debugLog('[webserver] Responding to /point-data request with %d point(s)', (len(points),))
    return serverResponse

# css and js files, among others, are served via this rule
@app.route("/www/<filename>")
def static_content(filename):
    return send_from_directory('www', filename)

# Returns a valid UTC else False
def validUTC(time):
    return isinstance(time, int)

class Webserver():
    def __init__(self, main):
        global surveyor 
        self.surveyor = main
        surveyor = main
    
    def start(self):
        # Avoid using privileged ports like 80 -- Use something above 1024 instead
        app.run(host='0.0.0.0', port=config['application']['port'])

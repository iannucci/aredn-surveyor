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
def heatmap():
    return send_from_directory('www', 'dynamic-heatmap.html')

@app.route('/logging', methods=['POST'])
def logging():
    global surveyor
    dataDict = request.json
    loggingEnabled = dataDict['logging']
    
    if loggingEnabled:
        debugLog('[webserver] Logging: %s  to: %s', (str(loggingEnabled),dataDict['logName'],))
        if surveyor:
            surveyor.enabled = True
    else:
        debugLog('[webserver] Logging: %s', (str(loggingEnabled),))
        if surveyor:
            surveyor.enabled = False
    serverResponse = { 'response': True }
    return serverResponse

@app.route('/heatmap-data')
def heatmapData():
    # result = logger.query(nodeName=nodeName, nodeMAC=nodeMAC, ssid=ssid, channel=channel, startTime=startTime, stopTime=stopTime)
    result = logger.query(startTime=1727560368, stopTime=1727560484)  #channel=175)
    if (result == []):
        debugLog('[webserver] No points in the database match the query. Exiting.')
        return None
    else:
        points = logger.databaseToPoints(result)
        bounds = mapHelper.boundingRectangle(points)
        mapDimPixels = { 'height': 1000, 'width': 800 }
        mapSettings = mapHelper.boundsToCenterZoom(bounds, mapDimPixels)
        serverResponse = { 'center': mapSettings['center'], 'zoom': mapSettings['zoom'] , 'points': points }
    # debugLog('[webserver] Replying to client with %s', (serverResponse,))
    return serverResponse

# css and js files, among others, are served via this rule
@app.route("/www/<filename>")
def static_content(filename):
    return send_from_directory('www', filename)

# def webserver():
class Webserver():
    def __init__(self, main):
        global surveyor 
        self.surveyor = main
        surveyor = main
    
    def start(self):
        # Avoid using privileged ports like 80 -- Use something above 1024 instead
        app.run(host='0.0.0.0', port=config['application']['port'])

from flask import Flask, send_from_directory
import configparser as c
import pathlib
import sys
import os

projectDir = pathlib.Path(__file__).parent.parent.resolve()
moduleDir = '%s/aredn_wardriving' % projectDir
configFilePath = '%s/conf/config.ini' % moduleDir
sys.path.append(os.fspath(projectDir))

import aredn_wardriving.logger as l
import aredn_wardriving.map_helper as m

app = Flask(__name__)

# @app.route("/")
# def map():
#     return send_from_directory('www', 'map.html')



config = c.ConfigParser()
config.read(configFilePath)
logger = l.Logger(config['database']['databasePath'])
mapHelper = m.MapHelper()

@app.route("/")
def heatmap():
    return send_from_directory('www', 'dynamic-heatmap.html')

@app.route('/heatmap-data')
def heatmapData():
    # result = logger.query(nodeName=nodeName, nodeMAC=nodeMAC, ssid=ssid, channel=channel, startTime=startTime, stopTime=stopTime)
    result = logger.query(channel=175)
    if (result == []):
        print('No points in the database match the query. Exiting.')
        return None
    else:
        points = logger.databaseToPoints(result)
        bounds = mapHelper.boundingRectangle(points)
        mapDimPixels = { 'height': 1000, 'width': 800 }
        mapSettings = mapHelper.boundsToCenterZoom(bounds, mapDimPixels)
        serverResponse = { 'center': mapSettings['center'], 'zoom': mapSettings['zoom'] , 'points': points }
    print('[heatmap-data] Replying to client with %s' % (serverResponse,))
    return serverResponse

# css and js files, among others, are served via this rule
@app.route("/www/<filename>")
def static_content(filename):
    return send_from_directory('www', filename)

app.run(host='0.0.0.0', port=81)

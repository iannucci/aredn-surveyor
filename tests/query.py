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

def queryBoundsAndZoom(mapDimPixels, nodeName=None, nodeMAC=None, ssid=None, channel=None, startTime=None, stopTime=None):
    config = c.ConfigParser()
    config.read(configFilePath)
    logger = l.Logger(config['database']['databasePath'])
    mapHelper = m.MapHelper()
    result = logger.query(nodeName=nodeName, nodeMAC=nodeMAC, ssid=ssid, channel=channel, startTime=startTime, stopTime=stopTime)
    if (result == []):
        print('No points in the database match the query. Exiting.')
        return None
    else:
        points = logger.databaseToPoints(result)
        # print(mapHelper.pointsToGoogleLatLng(points))
        bounds = mapHelper.boundingRectangle(points)
        mapSettings = mapHelper.boundsToCenterZoom(bounds, mapDimPixels)
        return { 'center': mapSettings['center'], 'zoom': mapSettings['zoom'] }
    
print(queryBoundsAndZoom({ 'height': 1000, 'width': 800 }, channel=175))
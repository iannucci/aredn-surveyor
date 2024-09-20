import configparser as c
import pathlib
import sys
import os

projectDir = pathlib.Path(__file__).parent.parent.resolve()
moduleDir = '%s/src' % projectDir
configFilePath = '%s/config/config.ini' % moduleDir
sys.path.append(os.fspath(projectDir))

import src.logger.logger as l
import src.webserver.map_helper as m
from src.debugger.debug_log import debugLog

def queryBoundsAndZoom(mapDimPixels, nodeName=None, nodeMAC=None, ssid=None, channel=None, startTime=None, stopTime=None):
    config = c.ConfigParser()
    config.read(configFilePath)
    logger = l.Logger(config['database']['databasePath'])
    mapHelper = m.MapHelper()
    result = logger.query(nodeName=nodeName, nodeMAC=nodeMAC, ssid=ssid, channel=channel, startTime=startTime, stopTime=stopTime)
    if (result == []) or (result is None):
        debugLog('No points in the database match the query. Exiting.')
        return None
    else:
        points = logger.databaseToPoints(result)
        # debugLog(mapHelper.pointsToGoogleLatLng(points))
        bounds = mapHelper.boundingRectangle(points)
        mapSettings = mapHelper.boundsToCenterZoom(bounds, mapDimPixels)
        return { 'center': mapSettings['center'], 'zoom': mapSettings['zoom'] }

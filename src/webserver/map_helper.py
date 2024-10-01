# Component of AREDN Survey by Bob Iannucci
#
# See LICENSE.md for license information

import math

ZOOM_MAX = 16

# Helper functions for dealing with Google Maps
class MapHelper():
    def boundingRectangle(self, points):
        minLat = 90
        maxLat = -90
        minlng = 180
        maxlng = -180
        for point in points:
            lat = point['lat']
            lng = point['lng']
            minLat = min(minLat, lat)
            maxLat = max(maxLat, lat)
            minlng = min(minlng, lng)
            maxlng = max(maxlng, lng)
        northEast = { 'lat': maxLat, 'lng': maxlng }
        southWest = { 'lat': minLat, 'lng': minlng }
        return { 'ne': northEast, 'sw': southWest }

    def boundsToCenterZoom(self, bounds, mapDim):
        WORLD_DIM = { 'height': 256, 'width': 256 }
        ZOOM_MAX = 16

        def latRad(lat):
            sin = math.sin(lat * math.pi / 180)
            radX2 = math.log((1 + sin) / (1 - sin)) / 2
            return max(min(radX2, math.pi), -math.pi) / 2

        def zoom(mapPx, worldPx, fraction):
            if (worldPx == 0) or (fraction == 0):
                return  ZOOM_MAX
            else:
                return math.floor(math.log(mapPx / worldPx / fraction) / math.log(2))

        ne = bounds['ne']
        sw = bounds['sw']

        latFraction = (latRad(ne['lat']) - latRad(sw['lat'])) / math.pi

        lngDiff = ne['lng'] - sw['lng']
        lngFraction = ((lngDiff + 360) if (lngDiff < 0) else lngDiff) / 360

        latZoom = zoom(mapDim['height'], WORLD_DIM['height'], latFraction)
        lngZoom = zoom(mapDim['width'], WORLD_DIM['width'], lngFraction)
        
        centerLat = sw['lat'] + ((ne['lat'] - sw['lat']) / 2.0)
        centerlng = sw['lng'] + ((ne['lng'] - sw['lng']) / 2.0)
        center = { 'lat': centerLat, 'lng': centerlng }

        return { 'center': center, 'zoom': min(latZoom, lngZoom, ZOOM_MAX) }

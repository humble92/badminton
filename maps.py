from dis import dis
import googlemaps
import os
from haversine import haversine


class Maps:
    def __init__(self):
        self.gmaps = googlemaps.Client(key=os.getenv('google_map_api_key'))

    # address to (lat, lon) 
    def geocoder(self, address):
        geocode_result = self.gmaps.geocode(address)
        return geocode_result[0]["geometry"]["location"]

    # calculate distance between 2 addresses
    def calc_distance(self, origin, dest):
        coordinate1 = self.geocoder(origin).values()
        coordinate2 = self.geocoder(dest).values()
        distance = haversine(tuple(coordinate1), tuple(coordinate2))
        # print(distance)
        return distance


# Simple test
g = Maps()
# g.geocoder("M4E 3L8")
g.calc_distance("M4E 3L8", "1501 ALBION RD Toronto")
g.calc_distance("M4E 3L8", "M4E 3L8")
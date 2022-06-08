import googlemaps
from haversine import haversine
import json

class Maps:
    def __init__(self):
        self.gmaps = googlemaps.Client(key='AIzaSyCrRlb_3B-tHPfgPhWHGp-xNtS4CBts6I0')

    # address to (lat, lon) 
    def geocoder(self, address):
        geocode_result = self.gmaps.geocode(address)
        write_json(geocode_result, "humble")
        return geocode_result[0]["geometry"]["location"]

    # calculate distance between 2 addresses
    def calc_distance(self, origin, dest):
        coordinate1 = self.geocoder(origin).values()
        coordinate2 = self.geocoder(dest).values()
        return haversine(tuple(coordinate1), tuple(coordinate2))



# function to add to JSON
def write_json(python_obj, filename="JSON_FILE", mode='w', indent=4):
    with open(filename, mode) as f:
        json.dump(python_obj, f, indent=indent)

g = Maps()
# g.geocoder("M4E 3L8")
g.calc_distance("M4E 3L8", "M5R 1X8")
g.calc_distance("M4E 3L8", "M4E 3L8")
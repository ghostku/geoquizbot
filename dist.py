import math
from haversine import haversine, Unit

def main():
    lat1 = 50.517097
    lon1 = 30.464360
    lat2 = 50.471747
    lon2 = 30.518106
    print(distance_im_meters_between_earth_coordinates(lat1, lon1, lat2, lon2))

    place1 = (50.517097, 30.464360)
    place2 = (50.471747, 30.518106)
    print(haversine(place1, place2, Unit.METERS))
def degrees_to_radians(degrees):
    return degrees * math.pi / 180

def distance_im_meters_between_earth_coordinates(lat1, lon1, lat2, lon2):
    EARTH_RADIUS_M = 6371000

    d_lat = degrees_to_radians(lat2 - lat1)
    d_lon = degrees_to_radians(lon2 - lon1)

    lat1 = degrees_to_radians(lat1)
    lat2 = degrees_to_radians(lat2)

    a = math.sin(d_lat/2) * math.sin(d_lat/2) + math.sin(d_lon/2) * math.sin(d_lon/2) * math.cos(lat1) * math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return c * EARTH_RADIUS_M

if __name__ == "__main__":
    main()

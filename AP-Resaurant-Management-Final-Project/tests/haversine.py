# import math

# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371  # Radius of the Earth in kilometers

#     dlat = math.radians(lat2 - lat1)
#     dlon = math.radians(lon2 - lon1)
#     a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
#     distance = R * c

#     return distance

# # Given coordinate
# lat1 = 48.8584
# lon1 = 2.2945

# lat2 = 48.8584
# lon2 = 2.2545

# # Maximum distance in kilometers
# max_distance = 5
# print(haversine(lat1, lon1, lat2, lon2))

from math import radians, sin, cos, acos
 
print("Input coordinates of two points:")
mlat = radians(float(input("Location 1 latitude: ")))
mlon = radians(float(input("Location 2 longitude: ")))
plat = radians(float(input("Location 1latitude: ")))
plon = radians(float(input("Location 2 longitude: ")))
 
dist = 6371.01 * acos(sin(mlat)*sin(plat) + cos(mlat)*cos(plat)*cos(mlon - plon))
print("The distance is %.2fkm." % dist)
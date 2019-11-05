import csv
from collections import namedtuple
from classes.package import *


def load_data(distance_csv, package_csv):
    '''Populate packages list, distances 2D list, Locations namedtuple list.
    Called in/by: main.py ~13

    Things it should do (remember, one function per task):
        read/clean/validate package csv
        create Package objects and return a list referencing all of them
        read/clean/validate distances csv
        populate list of Locations

    Data definitions:
    A Location is a namedtuple of location-number, landmark, street address.
    '''
    packages, distances, Locations = [], [], []
    Location = namedtuple('Locations', ['num', 'landmark', 'address'])
    Locations.append(Location(1, 'Hub', '4001 S 700 E 84107'))
    return packages, distances, Locations

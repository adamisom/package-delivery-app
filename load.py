import csv
from classes.package import *


def load_data(distance_csv, package_csv):
    '''Populate packages list, distances 2D list, and Locations Enum.
    Called in/by: main.py ~13
    Things it should do (remember, one function per task):
        read/clean/validate package csv
        create Package objects and return a list referencing all of them
        read/clean/validate distances csv
        Locations = Enum(k/v pairs of landmark/loc#)
    '''
    packages, distances, Locations = [], [], []
    return packages, distances, Locations

import csv
from collections import namedtuple
from classes.package import *
'''
 DONE   1. tentative function-name and multi-line comment
    2. sentence(s) on what it's supposed to, especially in terms of data
    3. data definitions/context--what kind of data, and what it represents
    4. parameters and return statement
    5. one-line purpose
    6. improve function name
    7. delete sentence(s) from step 2
    6. generate examples as given:/expect:
    7. convert simpler examples to test(s)
    8. develop the function
    9. pass those test(s)
    10. convert more examples into tests
    11. develop the function
    12. pass those tests
    13. move the tests into a testing file and rerun them there
    14. clean up the function
'''


def read_distance_csv(csv):
    '''.'''


def clean_distance_data():
    '''.'''


def fill_distance_data():
    '''.'''


def validate_distance_data():
    '''.'''


def clean_address_data():
    '''.'''


def read_package_csv(csv):
    '''.'''


def clean_package_data():
    '''.'''


def validate_package_address_data():
    '''.'''


def load_data(distance_csv, package_csv):
    '''Populate packages list, distances 2D list, Locations namedtuple list.
    Called in/by: main.py ~13

    Things it should do (remember, one function per task):
        read/clean_dist/clean_addr/fill/validate distances csv
        populate list of Locations
        read/clean/validate package csv
        create Package objects and return a list referencing all of them

    Data definitions:
    A Location is a namedtuple of location-number, landmark, street address.
    '''
    distances, Locations, packages = [], [], []

    Location = namedtuple('Locations', ['num', 'landmark', 'address'])
    Locations.append(Location(1, 'Hub', '4001 S 700 E 84107'))
    return distances, Locations, packages

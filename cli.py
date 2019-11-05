from classes.time_custom import *
from classes.truck import *
from classes.package import *


def snapshot(time_custom, packages, Locations):
    '''Display historical status of each/every package at a provided time.
    Called in/by: main.py ~55

    This should be able to loop through a list of packages, and for each:
        - fetch its status at that time
            - by inspecting the package's history attribute
        - fetch other properties of the package
        - store a user-friendly listing of the package's properties
    Finally it should print all of the package statuses in a readable way.

    Data definitions:
    A Location is a namedtuple of location-number, landmark, street address.
    '''
    print(f'Locations: {Locations}')

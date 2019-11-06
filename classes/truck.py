import random
from .time_custom import *
from .package import *


class Truck():
    id_counter = 1
    max_packages = 16
    first_delivery_time = Time_Custom(8, 00, 00)

    def __init__(self):
        '''Create Truck object.
        Called in/by: main.py ~15

        Assumes trucks start at the hub.
        '''
        self.props = Hash(ID=Truck.id_counter,
                          location=1,  # location 1 is the hub
                          time=Truck.first_delivery_time,
                          packages=[])

        Truck.id_counter += 1

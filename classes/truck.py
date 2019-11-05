import random
from .time_custom import *
from .package import *


class Truck():
    id_counter = 1
    max_packages = 16
    first_delivery_time = Time_Custom(8, 00, 00)

    def __init__(self):
        '''Create Truck object.
        Called in/by: main.py ~15'''
        self.ID = Truck.id_counter
        Truck.id_counter += 1
        self.location = 1  # Locations['HUB']
        self.time = Truck.first_delivery_time
        self.packages = []

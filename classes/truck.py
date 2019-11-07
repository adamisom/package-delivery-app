import random
from .time_custom import *
from .package import *


class Truck():
    id_counter = 1
    max_packages = 16
    average_speed = 18
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

    def update_late_packages(self, all_packages):
        '''Update all late-arriving packages that are now at the hub.

        TODO: have last_arrival_time passed in and use it.'''
        for pkg in all_packages:
            pkg.update_late_package()

    def update_corrected_packages(self, all_packages):
        '''Update all packages that had a known wrong-destination at start of day
        but which have now been corrected, i.e., which can now be delivered.

        TODO: have last_correction_time passed in and use it.'''
        for pkg in all_packages:
            pkg.update_corrected_package()

    def discover_packages_at_hub(self, last_arrival_time, last_correction_time,
                                 all_packages):
        '''Return list of packages at hub.

        TODO: call the two helpers above this method.'''
        return [pkg for pkg in all_packages
                if pkg.props['state'].name == 'AT_HUB']

    def load(self):
        '''Load truck with packages.

        What it should do:
        - change truck's packages property
        '''
        pass

    def deliver(self):
        '''Deliver packages on truck.

        What it should do:
        - update EACH package's state and history properties
        - update truck's packages and location properties
        '''
        pass

    def __str__(self):
        '''Return string representation of Truck object.'''
        package_list = '\n\t'.join([str(pkg) for pkg in self.packages])
        return f'Truck with ID: {self.ID}, is at location {self.location}, '\
               f'at {str(self.time)}, with these packages: \n\t{package_list}'

    @classmethod
    def speed_function(cls, location1, location2):
        '''Return average speed between two locations in miles per hour.

        For now, this program assumes trucks' average speed is always 18 mph
        between any two locations, starting/stopping time notwithstanding.
        '''
        return 18

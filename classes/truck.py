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

        NOTE that 'location' actually refers to a location.num
        Assumes trucks start at the hub.
        '''
        self.props = Hash(ID=Truck.id_counter,
                          location=1,  # location 1 is the hub
                          time=Truck.first_delivery_time,
                          packages=[])

        Truck.id_counter += 1

    def update_late_packages(self, all_packages):
        '''Update all late-arriving packages that are now at the hub.'''
        late_arrivals = [pkg for pkg in all_packages
                         if pkg.props['special_note']['late_arrival']
                         is not None]

        for pkg in late_arrivals:
            anticipated_arrival = pkg.props['special_note']['late_arrival']

            if (self.props['time'] > anticipated_arrival and
                    pkg.props['state'].name == 'LATE_ARRIVAL'):
                pkg.update_late_as_arrived()

    def update_corrected_packages(self, all_packages, destination_corrections):
        '''Update all packages that had a known wrong-destination at start of day
        but which have now been corrected, i.e., which can now be delivered.'''
        wrong_destinations = [pkg for pkg in all_packages
                              if pkg.props['special_note']['wrong_destination']
                              is True]

        for pkg in wrong_destinations:
            index = [correction.id for correction in
                     destination_corrections].index(pkg.props['ID'])

            updated_destination = destination_corrections[index]

            if updated_destination.location is not None:
                pkg.update_package_destination(updated_destination)

                if pkg.props['state'].name == 'WRONG_DESTINATION':  # need if?
                    pkg.update_wrong_destination_as_corrected()

    def get_deliverable_packages(self, all_packages, destination_corrections):
        '''Return list of packages at hub and update late or wrong-destination
        packages that have (respectively) arrived or been corrected.'''
        self.update_late_packages(all_packages)
        self.update_corrected_packages(all_packages, destination_corrections)
        return [pkg for pkg in all_packages
                if pkg.props['state'].name == 'AT_HUB']

    def load(self, pkg_load):
        '''Load truck with packages.

        What it should do:
        - change truck's packages property
        '''
        self.packages = pkg_load

    def deliver(self, route):
        '''Deliver packages on truck.

        Data definition: A 'Stop' on a 'Route' is a list, containing:
            - location*
            - packages: list of packages to drop off at this location
            - distance_?
            - projected_arrival? (time_custom)
        A Route is then simply a list of Stops.

        *A Location is a namedtuple of num, landmark, address.

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

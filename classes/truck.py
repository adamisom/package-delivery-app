import random
from .time_custom import *
from .package import *


class Truck():
    id_counter = 1
    max_packages = 16
    average_speed = 18
    starting_location = 1  # location 1 is the hub
    first_delivery_time = Time_Custom(8, 00, 00)

    def __init__(self):
        '''Create Truck object.
        Called in/by: main.py ~15

        NOTE that 'location' actually refers to a location.num
        Assumes trucks start at the hub.
        '''
        self.props = Hash(ID=Truck.id_counter,
                          location=Truck.starting_location,
                          time=Truck.first_delivery_time,
                          packages=[],
                          mileage_for_day=0)

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

    def get_available_packages(self, all_packages, destination_corrections):
        '''Return list of packages at hub and update late or wrong-destination
        packages that have (respectively) arrived or been corrected.'''
        self.update_late_packages(all_packages)
        self.update_corrected_packages(all_packages, destination_corrections)
        at_hub = [pkg for pkg in all_packages
                  if pkg.props['state'].name == 'AT_HUB']
        ID = self.props['ID']
        can_go = [pkg for pkg in all_packages
                  if (pkg.props['special_note']['truck_number'] is None or
                      pkg.props['special_note']['truck_number'] == ID)]
        return [pkg for pkg in all_packages
                if pkg in at_hub and pkg in can_go]

    def load(self, pkg_load):
        '''Load truck with packages.'''
        self.packages = pkg_load

    def get_mileage_for_day(self):
        '''Find and return actual mileage truck has traveled today.

        This function currently just returns the distance passed in, but it
        could be easily extended in the future to account for "real life",
        for example if a truck was forced to take a detour.
        '''
        return self.props['mileage_for_day']

    def deliver(self, route):
        '''Deliver packages on truck.

        Note: this whole program implicitly assumes that trucks are able to
        deliver each package precisely on schedule.

        What it should do:
        - update EACH package's state and history properties
        - update truck's packages and location properties

        Data definition (see algorithms.py for more):
        A 'Stop' on a 'Route' is a namedtuple, comprising:
            - location: location of the stop
            - packages: list of packages to drop off at this location
            - distance_from_prev: distance from previous stop
            - projected_arrival: a Time_Custom object
        '''

        # TEMPORARY--this is helpful, put in test?
        pretty_route = '\n\t'.join([str(stop) for stop in route])
        # print(f'\nin truck.deliver, route is: {pretty_route}')

        for stop in route:
            self.props['location'] = stop.location
            self.props['time'] = stop.projected_arrival
            self.props['packages'] = list(
                set(self.props['packages']) - set(stop.packages))
            self.props['mileage_for_day'] += stop.distance_from_prev

            for pkg in stop.packages:
                pkg.set_state('DELIVERED')
                pkg.add_to_history('DELIVERED', self.props['time'])

    def __str__(self):
        '''Return string representation of Truck object.'''
        package_list = '\n\t'.join([str(pk) for pk in self.props['packages']])
        return (f"Truck with ID: {self.props['ID']}; location: "
                f"{self.props['location']}; time: {str(self.props['time'])};"
                f" with these packages: \n\t{package_list}")

    @classmethod
    def speed_function(cls, location1, location2):
        '''Return average speed between two locations in miles per hour.

        For now, this program assumes trucks' average speed is always 18 mph
        between any two locations, starting/stopping time notwithstanding.
        '''
        return cls.average_speed

from .time_custom import *
from .package import *


class Truck():
    '''This class creates Truck objects.

    Class Attributes:
     - id_counter: to ensure Trucks have unique IDs, starting at 1
     - max_packages: all trucks carry a maximum of 16 packages at once
     - average_speed: all trucks always go at 18mph (including stops)
     - first_delivery_time: all trucks initially leave the hub at 8:00 AM

    Attributes (Instance variables):
     - ID: ID
     - location: a namedtuple of num, landmark, address
     - time: current time of truck
        This only updates when trucks arrive somewhere, not every minute.
     - packages: list of packages currently on the truck
     - mileage_for_day: mileage for the day

    Trucks, when they are at the hub, are capable of seeing whether any
    late-arrival packages have arrived and updating such packages, and they
    are also capable (or rather, you can suppose their drivers are capable) of
    updating wrong-destination packages (if the correct destination is known).
    '''

    id_counter = 1
    max_packages = 16
    average_speed = 18
    starting_location = 1  # location 1 is the hub
    first_delivery_time = Time_Custom(8, 00, 00)

    def __init__(self):
        '''Create Truck object.'''
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
                # anticipated_arrival will be used in the new History_Record,
                # which means we implicitly assume late arrivals arrive
                # precisely when we were told they would (and not even later!)
                pkg.update_late_as_arrived(anticipated_arrival)

    def update_corrected_packages(self, all_packages, destination_corrections):
        '''Update all packages that had a known wrong-destination at start of day
        but which have now been corrected, i.e., which can now be delivered.'''
        wrong_destinations = [p for p in all_packages
                              if p.props['state'].name == 'WRONG_DESTINATION']

        for pkg in wrong_destinations:
            if pkg.props['ID'] in [c.pkg_id for c in destination_corrections]:
                updated_destination, = [c for c in destination_corrections
                                        if c.pkg_id == pkg.props['ID']]

                if updated_destination.location is not None:
                    pkg.update_package_destination(
                        updated_destination.location)
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
        self.props['packages'] = pkg_load

    def get_mileage_for_day(self):
        '''Find and return actual mileage truck has traveled today.

        This function currently just returns the instance prop mileage_for_day
        but could easily be extended in the future to account for "real life",
        for example if a truck was forced to take a detour.
        '''
        return self.props['mileage_for_day']

    def deliver(self, route):
        '''Deliver packages on truck.

        Note: this whole program implicitly assumes that trucks are able to
        deliver each package precisely on schedule.

        A 'Stop' on a 'Route' is a namedtuple, comprising:
            - loc: location of the stop
            - pkgs: list of packages to drop off at this location
            - dist: distance from previous stop
            - arrival: a Time_Custom object (projected arrival, not actual)
        '''
        for stop in route:
            self.props['location'] = stop.loc
            self.props['time'] = stop.arrival
            self.props['packages'] = list(
                set(self.props['packages']) - set(stop.pkgs))
            self.props['mileage_for_day'] += stop.dist

            for pkg in stop.pkgs:
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

        This function currently just returns the class prop average_speed
        but could easily be extended in the future to account for 'real life',
        for example some roads could be faster than others.
        '''
        return cls.average_speed

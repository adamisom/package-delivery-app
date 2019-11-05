import algorithms as algo
import cli
import load
from classes.time_custom import *
from classes.hash import *
from classes.package import *
from classes.truck import *
from tests.general_tests import *

distance_csv = '/Users/adamisom/Desktop/WGUPS Distance Table.csv'
package_csv = '/Users/adamisom/Desktop/WGUPS Package File.csv'

packages, distances, Locations = load.load_data(distance_csv, package_csv)
# known_destination_correction_times = [Time_Custom(10, 20, 00)]
truck_one, truck_two = Truck(), Truck()
trucks = [truck_one, truck_two]


def all_packages_delivered():
    '''Return whether all packages are delivered. UNTESTED.'''
    return True
    # return all([pkg.status == Status(Status['DELIVERED']
    #             for pkg in packages)])


def last_arrival_time():
    '''Return the time by which all packages will have arrived at the hub.'''
    return None
    # return max([pkg.special_note['late_arrival']
    #             for pkg in all_packages
    #             if pkg.special_note['late_arrival'] is not None])


def last_correction_time():
    '''Return the time by which all destination corrections will be known.'''
    return None
    # if any([pkg.special_note['wrong_destination']
    #         for pkg in all_packages]):
    #     return max(known_destination_correction_times)
    # return None

number_of_loops = 0
while not all_packages_delivered() and number_of_loops < 100:
    number_of_loops += 1

    for truck in trucks:
        pass
        # if truck.location == destinations['WGU']:
        #     last_arrival_time = last_arrival_time()
        #     last_correction_time = last_correction_time()

        # pkgs_at_hub = truck.discover_packages_at_hub(la, lc)
        # pkg_load = algo.pick_load(pkgs_at_hub)
        # truck.load(pkg_load)
        # route = algo.build_route(pkg_load)
        # truck.deliver(route)

# cli.snapshot(Time_Custom(9, 00, 00))
# cli.snapshot(Time_Custom(10, 00, 00))
# cli.snapshot(Time_Custom(13, 00, 00))

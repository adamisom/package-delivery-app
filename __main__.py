from .algorithms import *
from .cli import snapshot, handle_input
from .load import load_data
from .classes.time_custom import Time_Custom
from .classes.hash import Hash
from .classes.package import Package
from .classes.truck import Truck
from .tests.general_tests import *

distance_csv = '/Users/adamisom/Desktop/WGUPS Distance Table.csv'
package_csv = '/Users/adamisom/Desktop/WGUPS Package File.csv'


def all_packages_delivered(packages):
    '''Return whether all packages are delivered.

    TODO: test this'''
    return all([pkg.props['state'].name == 'DELIVERED'
                for pkg in packages])


def last_arrival_time(packages):
    '''Return the time by which all packages will have arrived at the hub.
    TODO: make it so this isn't called every time. In fact, I'll most likely
    get rid of the function (see notes.txt)
    '''
    return (max([pkg.props['special_note']['late_arrival']
                for pkg in packages
                if pkg.props['special_note']['late_arrival'] is not None])
            if len(packages) > 0
            else None)


def last_correction_time(packages, known_destination_correction_times):
    '''Return the time by which all destination corrections will be known.
    TODO: make it so this isn't called every time. In fact, I'll most likely
    get rid of the function (see notes.txt)
    '''
    if any([pkg.props['special_note']['wrong_destination']
            for pkg in packages]):
        return max(known_destination_correction_times)
    return None


def run_program():
    distances, Locations, packages = load_data(distance_csv, package_csv)
    known_destination_correction_times = [Time_Custom(10, 20, 00)]
    truck_one, truck_two = Truck(), Truck()
    trucks = [truck_one, truck_two]

    number_of_loops = 0
    while not all_packages_delivered(packages) and number_of_loops < 100:
        number_of_loops += 1

        for truck in trucks:
            if truck.props['location'] == 1:
                last_arrival = last_arrival_time(packages)
                last_correction = last_correction_time(
                    packages, known_destination_correction_times)
                la, lc = last_arrival, last_correction

                pkgs_at_hub = truck.discover_packages_at_hub(la, lc, packages)
                pkg_load = pick_load(pkgs_at_hub, distances)
                truck.load(pkg_load)
                route = build_route(pkg_load, distances)
                truck.deliver(route)

    snapshot(Time_Custom(9, 00, 00), packages)
    # snapshot(Time_Custom(10, 00, 00), packages)
    # snapshot(Time_Custom(13, 00, 00), packages)

    # handle_input(packages)

if __name__ == '__main__':
    run_program()

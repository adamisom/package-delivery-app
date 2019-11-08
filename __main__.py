from .algorithms import pick_load, build_route
from .cli import (say_hello, make_snapshot, handle_snapshot_request,
                  get_destination_corrections_from_user)
from .load import load_data
from .classes.time_custom import Time_Custom
from .classes.hash import Hash
from .classes.package import Package
from .classes.truck import Truck
from .tests.general import test


def all_packages_delivered(packages):
    '''Return whether all packages are delivered.'''
    return all([pkg.props['state'].name == 'DELIVERED'
                for pkg in packages])


def run_program(distance_csv, package_csv):
    say_hello()

    distances, Locations, packages = load_data(distance_csv, package_csv)

    Destination_Corrections = get_destination_corrections_from_user(Locations)

    truck_one, truck_two = Truck(), Truck()
    trucks = [truck_one, truck_two]

    number_of_loops = 0
    while not all_packages_delivered(packages) and number_of_loops < 3:
        number_of_loops += 1

        for truck in trucks:  # um, right now this calls contents 2x per loop
            if truck.props['location'] == 1:
                pkgs_at_hub = truck.get_deliverable_packages(
                    packages, Destination_Corrections)
                pkg_load = pick_load(pkgs_at_hub, distances)
                truck.load(pkg_load)
                route = build_route(pkg_load, distances)
                truck.deliver(route)

    make_snapshot(Time_Custom(9, 00, 00), packages)
    # make_snapshot(Time_Custom(10, 00, 00), packages)
    # make_snapshot(Time_Custom(13, 00, 00), packages)

    # handle_snapshot_request(packages)

    test()

if __name__ == '__main__':
    run_program('/Users/adamisom/Desktop/WGUPS Distance Table.csv',
                '/Users/adamisom/Desktop/WGUPS Package File.csv')

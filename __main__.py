# Adam Isom, Student ID #000906109
from .algorithms import pick_load, build_route
from .cli import (say_hello, make_snapshot, handle_snapshot_request,
                  get_destination_corrections_from_user)
from .load import load_data
from .classes.time_custom import Time_Custom
from .classes.hash import Hash
from .classes.package import Package
from .classes.truck import Truck
from .tests.general import test


def is_package_delivered_and_on_time(package):
    '''Return whether the given package was delivered at all if it had no
    deadline, and whether it was delivered on time if it did have one.'''

    # # These print statements are useful, I may save them in tests
    # print(f"Package ID: {package.props['ID']}")
    # print(f"Deadline?\t{package.props['deadline']}")
    # print(f"Package History:\n{package.display_history()}\n")

    for record in package.props['history']:
        if (record.state.name == 'DELIVERED' and
                package.props['deadline'] is None):
            return True

        if (record.state.name == 'DELIVERED' and
                record.time <= package.props['deadline']):
            return True

    return False


def display_number_delivered_on_time(packages):
    '''Calculate and display the number (it should be all of them) of packages
    that were delivered on time.'''
    on_time_count = 0
    for pkg in packages:
        if is_package_delivered_and_on_time(pkg):
            on_time_count += 1

    print(f'\n{on_time_count} out of {len(packages)} packages '
          'were delivered on time.')


def all_packages_delivered(packages):
    '''Return whether all packages are delivered.'''
    return all([pkg.props['state'].name == 'DELIVERED'
                for pkg in packages])


def display_distances(distances):
    '''Print distance 2D-list as a readable table.

    For development use only (take out before promoting to production).'''
    string = ''
    for row in distances:
        string += '\n'
        for item in row:
            string += str(item).rjust(5, ' ')
    string = string.replace('DISTANCE BETWEEN HUBS IN MILES', '    ')
    string = 'DISTANCES' + string
    print(string)


def run_program(distance_csv, package_csv):
    say_hello()

    distances, Locations, packages = load_data(distance_csv, package_csv)

    # for development only--save in tests?
    # display_distances(distances)

    Destination_Corrections = get_destination_corrections_from_user(Locations)

    number_of_trucks = 3
    number_of_drivers = 2
    trucks = []
    for i in range(number_of_trucks):
        trucks.append(Truck())

    initial_leave = Time_Custom(8, 00, 00)  # trucks first leave hub at 8 AM

    # Initial departure of all trucks, if there's a driver for that truck.
    # The last truck to leave is responsible for ensuring all packages meet
    # their deadline. In the future, if one truck isn't enough, the last two
    # or three could be responsible, or another solution could be found.
    last_truck_to_leave_in_morning = trucks[number_of_drivers-1]
    for truck in trucks:
        pkgs_at_hub = truck.get_deliverable_packages(
            packages, Destination_Corrections)

        if truck is last_truck_to_leave_in_morning:
            pkg_load = pick_load(pkgs_at_hub, packages, distances,
                                 True, truck.props['ID'])
        else:
            pkg_load = pick_load(pkgs_at_hub, packages, distances,
                                 False, truck.props['ID'])
        truck.load(pkg_load)

        route = build_route(pkg_load, distances, Locations,
                            Truck.speed_function, initial_leave)
        truck.deliver(route)

        if truck is last_truck_to_leave_in_morning:
            break

    # for development only--save in tests?
    display_number_delivered_on_time(packages)

    count = 0
    while not all_packages_delivered(packages) and count < 5:
        count += 1

    # make_snapshot(Time_Custom(9, 00, 00), packages)
    # make_snapshot(Time_Custom(10, 00, 00), packages)
    # make_snapshot(Time_Custom(13, 00, 00), packages)

    # handle_snapshot_request(packages)

    # test()  # take out this line before promoting to production

    # TODO: from Rubric: "The verification includes the total miles added to
    # all trucks, and it states that all packages were delivered on time."


if __name__ == '__main__':
    run_program('/Users/adamisom/Desktop/WGUPS Distance Table.csv',
                '/Users/adamisom/Desktop/WGUPS Package File.csv')

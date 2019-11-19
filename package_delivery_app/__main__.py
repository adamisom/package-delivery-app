# Adam Isom, Student ID #000906109
import sys
from .cli import (say_hello, make_snapshot, handle_snapshot_request,
                  get_destination_corrections_from_user)
from .load import load_data
from .classes.time_custom import Time_Custom
from .classes.hash import Hash
from .classes.package import Package
from .classes.truck import Truck
from .classes.route_builder import RouteBuilder
from .tests.general import test


def all_packages_delivered(packages):
    '''Return whether all packages are delivered.'''
    return all([pkg.props['state'].name == 'DELIVERED'
                for pkg in packages])


def display_packages_with_history(packages):
    '''Display each delivered package and their delivery-status histories.'''
    delivered = '\n'.join([str(pkg) + '\n' + pkg.display_history()
                           for pkg in packages
                           if pkg.props['state'].name == 'DELIVERED'])
    print(f'DELIVERED: {delivered}')


def display_distance_traveled(total_distance):
    '''Display distance (in miles) traveled to deliver all packages.'''
    print(f'\nTotal travel distance today was {total_distance:.2f} miles.')


def is_package_delivered_and_on_time(package):
    '''Return whether the given package was delivered at all if it had no
    deadline, and whether it was delivered on time if it did have one.'''
    for record in package.props['history']:
        if record.state.name == 'DELIVERED':
            if package.props['deadline'] is None:
                return True
            if record.time <= package.props['deadline']:
                return True
    return False


def display_number_delivered_on_time(packages):
    '''Calculate and display the number (it should be all of them) of packages
    that were delivered on time.'''
    on_time_count = sum([1 for pkg in packages
                         if is_package_delivered_and_on_time(pkg)])
    print(f'\n{on_time_count} out of {len(packages)} packages '
          'were delivered on time.')


def display_distances(distances):
    '''Print distance 2D-list as a readable table.'''
    string = '\n'.join(''.join([str(item).rjust(5, ' ')
                                for item in row])
                       for row in distances)
    string = string.replace('DISTANCE BETWEEN HUBS IN MILES', '    ')
    print('DISTANCES\n', string)


def run_program(distance_csv, package_csv):
    '''Run the program!'''
    say_hello()

    distances, Locations, packages = load_data(distance_csv, package_csv)

    # Note: one destination-correction is hardcoded so that I don't have to
    # enter it each time I run this program. The assignment that this program
    # was built for specified this destination-correction as known in advance.
    # If you use this code you will probably want to remove it (cli.py ln ~320)
    Destination_Corrections = get_destination_corrections_from_user(Locations)

    number_of_trucks = 3
    number_of_drivers = 2
    trucks = []
    for i in range(number_of_drivers):  # trucks can't be sent without drivers
        trucks.append(Truck())

    count = 0
    while count < 5 and not all_packages_delivered(packages):
        count += 1
        for truck in trucks:

            packages_ready = truck.get_available_packages(
                packages, Destination_Corrections)

            route_parameters = Hash(
                ['available_packages', packages_ready],
                ['distances', distances],
                ['max_load', Truck.max_packages],
                ['truck_number', truck.props['ID']],
                ['Locations', Locations],
                ['speed_function', Truck.speed_function],
                ['starting_location', Truck.starting_location],
                ['initial_leave_time', Truck.first_delivery_time])
            route_builder = RouteBuilder(route_parameters)
            route = route_builder.build_route()

            truck.load(route_builder.get_packages())
            truck.deliver(route)

    total_distance = sum([truck.props['mileage_for_day']
                          for truck in trucks])
    display_distance_traveled(total_distance)
    display_number_delivered_on_time(packages)

    # make_snapshot(Time_Custom(9, 00, 00), packages)
    # handle_snapshot_request(packages)
    test()


if __name__ == '__main__':
    try:
        dist_csv = sys.argv[1]
        pkg_csv = sys.argv[2]
    except IndexError:
        raise IndexError('You didn\'t provide both required csv files')

    run_program(dist_csv, pkg_csv)

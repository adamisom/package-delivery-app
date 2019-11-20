# Adam Isom, Student ID #000906109
import sys
from .cli import (say_hello, ask_if_snapshot_wanted, handle_snapshot_request,
                  ask_if_package_histories_wanted, ask_if_route_display_wanted,
                  get_destination_corrections)
from .load import load_data
from .classes.time_custom import Time_Custom
from .classes.hash import Hash
from .classes.package import Package
from .classes.truck import Truck
from .classes.route_builder import RouteBuilder
from .tests.general import test


'''
Note: the number 79 is hardcoded 5 times in "display" functions and methods
    to print out a line 79 characters long (2 times here in __main__, 2 times
    in cli, and 1 time in route_builder), so if a user's console is less than
    79 characters, the print-outs won't be pretty.
'''


def all_packages_delivered(packages):
    '''Return whether all packages are delivered.'''
    return all([pkg.props['state'].name == 'DELIVERED'
                for pkg in packages])


def number_delivered(packages):
    '''Return count of number delivered.'''
    return sum([1 for pkg in packages
                if pkg.props['state'].name == 'DELIVERED'])


def display_packages_with_history(packages):
    '''Display each package and its delivery-status histories.'''
    sorted_pkgs_with_history = '\n'.join(
        [(str(p).replace('PkgState.', '') + '\n\t' + p.history_string('\t'))
         for p in sorted(packages, key=lambda p: p.props['ID'])])

    print(f'Packages and their histories:\n{sorted_pkgs_with_history}\n')
    print('*' * 79, '\n')


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
    distances, Locations, packages = load_data(distance_csv, package_csv)

    say_hello()
    # Destination_Corrections = []
    Destination_Corrections = get_destination_corrections(Locations)
    # route_display_wanted = ask_if_route_display_wanted()
    # snapshot_wanted = ask_if_snapshot_wanted()
    # package_histories_wanted = ask_if_package_histories_wanted()
    print('*' * 79, '\n')

    number_of_trucks = 3
    number_of_drivers = 2
    trucks = []
    for i in range(number_of_drivers):  # trucks can't be sent without drivers
        trucks.append(Truck())

    while not all_packages_delivered(packages):
        number_delivered_before_loop = number_delivered(packages)

        # for truck in trucks:

        # send out whichever truck arrives to the hub first, or the lower-ID
        # truck if they are ready to leave at the same time (e.g. 8 AM)
        truck = sorted(trucks,
                       key=lambda t: (t.props['time'], t.props['ID']))[0]

        packages_ready = truck.get_available_packages(
            packages, Destination_Corrections)

        if len(packages_ready) == 0:
            # advance current truck's clock to latest destination-correction
            latest_correction = max([c.time for c in Destination_Corrections])
            if truck.props['time'] < latest_correction:
                truck.props['time'] = latest_correction

                # try again
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
            ['leaving_hub_at', truck.props['time']])
        route_builder = RouteBuilder(route_parameters)
        route = route_builder.build_route()

        # if route_display_wanted and route != []:
        if route != []:
            route_builder.display_route()

        truck.load(route_builder.get_packages())
        truck.deliver(route)

        number_delivered_after_loop = number_delivered(packages)
        if not number_delivered_after_loop > number_delivered_before_loop:
            break

    total_distance = sum([truck.props['mileage_for_day']
                          for truck in trucks])
    display_distance_traveled(total_distance)
    display_number_delivered_on_time(packages)
    print('\n')
    print('*' * 79)

    # if snapshot_wanted:
    #     handle_snapshot_request(packages)

    # if package_histories_wanted:
    #     display_packages_with_history(packages)


if __name__ == '__main__':
    try:
        dist_csv = sys.argv[1]
        pkg_csv = sys.argv[2]
    except IndexError:
        raise IndexError('You didn\'t provide both required csv files')

    run_program(dist_csv, pkg_csv)

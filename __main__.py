# Adam Isom, Student ID #000906109
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


def display_distance_traveled(total_distance):
    '''Display distance (in miles) traveled to deliver all packages.'''
    print(f'\nTotal travel distance today was {total_distance:.2f} miles.')


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

    # display_distances(distances)

    Destination_Corrections = get_destination_corrections_from_user(Locations)

    number_of_trucks = 3
    number_of_drivers = 2
    trucks = []
    for i in range(number_of_trucks):
        trucks.append(Truck())

    for truck in trucks:
        # TEMPORARY TEST STUFF BELOW
        if truck.props['ID'] != 1:
            continue
        for pkg in packages:
            pass
            # pkg.props['special_note']['truck_number'] = [1]
            # if pkg.props['ID'] != 15:
            #     pkg.props['deadline'] = Time_Custom(10, 30, 00)

        # TODO: see why this is returning all 40,
        # given that several have late arrival it should be <40
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

    count = 0
    while not all_packages_delivered(packages) and count < 5:
        count += 1

    total_distance = sum([truck.props['mileage_for_day']
                          for truck in trucks])
    display_distance_traveled(total_distance)
    display_number_delivered_on_time(packages)

    # make_snapshot(Time_Custom(9, 00, 00), packages)
    # make_snapshot(Time_Custom(10, 00, 00), packages)
    # make_snapshot(Time_Custom(13, 00, 00), packages)

    # handle_snapshot_request(packages)

    # test()  # take out this line before promoting to production


if __name__ == '__main__':
    run_program('/Users/adamisom/Desktop/WGUPS Distance Table.csv',
                '/Users/adamisom/Desktop/WGUPS Package File.csv')

import random
from copy import deepcopy
from collections import namedtuple
from .classes.time_custom import Time_Custom


Stop = namedtuple('Stop', ['location', 'packages',
                           'distance_from_prev', 'projected_arrival'])


def get_nearest_neighbor(starting_from, destination_numbers, distances):
    '''Return the package-destination's location-number nearest to a provided
    location-number.

    Inputs:
    - starting_from: a Location's num property. Locations are namedtuples
    of num, landmark, address.
    - destination_numbers: list of all location_numbers that need to be
    visited to drop off all packages on the simulated route.
    - distances: a 2D list wherein both column and row indices happen to be a
    location_number (due to how the Locations list of Location namedtuples was
    set up in load.py)
    '''

    # fetch the row holding distance information for provided location_number
    row_index = [row[0] for row in distances].index(starting_from)
    distances_from_start = distances[row_index]

    # make 2D list of location-number (column 1) and distance (column 2),
    # where the distance in column 2 is distance FROM provided location_number
    # TO a different destination (namely the one with col 1's location_number)
    transposed = list(zip(distances[0], distances_from_start))

    # only check neighbors we actually have to visit
    eligible_neighbors = [location_distance for location_distance in transposed
                          if location_distance[0] in destination_numbers and
                          location_distance[1] > 0]

    nearest = min(eligible_neighbors, key=lambda neighbor: neighbor[1])

    return nearest


def nearest_neighbors_total_distance(destination_numbers, distances):
    '''Return total distance traveled in a simulated route.

    This function assumes trucks start at the hub (initial location 1).
    '''
    distance_traveled = 0
    location = 1

    while len(destination_numbers) > 0:
        nearest_neighbor = get_nearest_neighbor(
            location, destination_numbers, distances)

        location = nearest_neighbor[0]
        destination_numbers.remove(location)

        distance_traveled += nearest_neighbor[1]

    return distance_traveled


def get_location_nums(pkgs):
    '''Return set of location numbers a route must visit to drop off all
    its packages.'''
    set_of_location_nums = set([pkg.props['location'].num for pkg in pkgs])
    return list(set_of_location_nums)


def pick_load(pkgs_at_hub, distances):
    '''Return list of package IDs that performed the best from a simulation of
    many package selections and deliveries.

    Inputs:
    - pkgs_at_hub: list of packages (references to Package objects)
    - distances: 2D list. distances[i][j] gives dist between locations i, j
    '''
    number_of_simulated_loads = 20
    simulated_load_package_IDs = []
    simulated_load_distances = []

    for i in range(number_of_simulated_loads):
        # if <16 items at hub, program crashes
        hypothetical_package_load = random.sample(pkgs_at_hub, 16)
        destination_numbers = get_location_nums(hypothetical_package_load)

        simulated_load_package_IDs.append(hypothetical_package_load)
        simulated_load_distances.append(
            nearest_neighbors_total_distance(destination_numbers, distances))

    # By the way, since Python's index stops at the first occurence in a list,
    # if two routes tied on distance, the first one simulated is returned
    index_of_min_distance = simulated_load_distances.index(
        min(simulated_load_distances))
    return simulated_load_package_IDs[index_of_min_distance]


def get_stop_projected_arrival(speed_function, dist_from_prev, stop_A, stop_B):
    '''Return projected arrival time for a stop on a route.'''
    avg_speed = speed_function(stop_A.location, stop_B.location)
    minutes = 60 * (dist_from_prev / avg_speed)
    projected_arrival = Time_Custom.clone(stop_A.projected_arrival)
    projected_arrival.add_time(minutes)
    return projected_arrival


def get_stop_packages(location_num, packages):
    '''Return list of package-IDs to be dropped off at a given location.'''
    return [pkg.props['ID'] for pkg in packages
            if pkg.props['location'].num == location_num]


def compute_route_distance(route):
    '''Return total distance a route covers.'''
    return sum([stop.distance_from_prev for stop in route])


def build_route(pkg_load, distances, Locations, truck_speed, initial_leave):
    '''Return delivery route (list of stops) for a provided package-load.

    Data definition: A 'Stop' on a 'Route' is a list, containing:
        - location*
        - packages: list of packages (IDs??) to drop off at this location
        - distance_?
        - projected_arrival? (time_custom)
    A Route is then simply a list of Stops.

    *A Location is a namedtuple of num, landmark, address.

    This function assumes that routes should start at the hub.
    '''
    route = []
    destination_numbers = get_location_nums(pkg_load)

    location_num = 1  # routes start at the hub (location #1)

    for pkg in pkg_load:

        # dummy values
        distance_from_previous = 5
        packages_at_stop = []
        projected_arrival = Time_Custom(12, 00, 00)

        stop = Stop(location_num, packages_at_stop,
                    distance_from_previous, projected_arrival)

        route.append(stop)
    return route

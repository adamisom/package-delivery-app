import random
from copy import deepcopy
from collections import namedtuple
from .classes.time_custom import Time_Custom


Stop = namedtuple('Stop', ['location', 'packages',
                           'distance_from_prev', 'projected_arrival_time'])


def get_nearest_neighbor(location_number, destination_numbers, distances):
    '''Return the package-destination's location-number nearest to a provided
    location-number.

    Inputs:
    - location_number: a Location's num property. Locations are namedtuples
    of num, landmark, address.
    - destination_numbers: list of all location_numbers that need to be
    visited to drop off all packages on the simulated route. As a reminder,
    this function is ultimately called by pick_load, so it's part of the load
    phase, not the deliver phase.
    - distances: a 2D list wherein both column and row indices happen to be a
    location_number (due to how the Locations list of Location namedtuples was
    set up in load.py)
    '''

    # fetch the row holding distance information for provided location_number
    row_index = [row[0] for row in distances].index(location_number)
    distances_from_location = distances[row_index]

    # make 2D list of location-number (column 1) and distance (column 2),
    # where the distance in column 2 is distance FROM provided location_number
    # TO a different destination (namely the one with col 1's location_number)
    transposed = list(zip(distances[0], distances_from_location))

    # only check neighbors we actually have to visit--and exclude itself!
    eligible_neighbors = [location_distance for location_distance in transposed
                          if location_distance[0] in destination_numbers and
                          location_distance[1] > 0]

    nearest = min(eligible_neighbors, key=lambda neighbor: neighbor[1])

    return nearest


def nearest_neighbors_route(pkg_load, destination_numbers, distances):
    '''Return total distance traveled in a simulated route in which the route
    is built up from greedy nearest-neighbor selection.

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
            nearest_neighbors_route(
                hypothetical_package_load, destination_numbers, distances))

    # By the way, since Python's index stops at the first occurence in a list,
    # if two routes tied on distance, the first one simulated is returned
    index_of_min_distance = simulated_load_distances.index(
        min(simulated_load_distances))
    return simulated_load_package_IDs[index_of_min_distance]


'''In main, I call algorithms.py code like this:
    pkg_load = pick_load(pkgs_at_hub, distances), then truck load,
    then route = build_route(pkg_load, distances, Locations)

FUNCTION DESIGN RECIPE
    1. tentative function-name and multi-line comment
    2. sentence(s) on what it's supposed to, especially in terms of data
    3. data definitions/context--what kind of data, and what it represents
    4. parameters and return statement
    5. one-line purpose
    6. improve function name
    7. delete sentence(s) from step 2
    6. generate examples as given:/expect:
    7. convert simpler examples to test(s)
    8. develop the function
    9. pass those test(s)
    10. convert more examples into tests
    11. develop the function
    12. pass those tests
    13. move the tests into a testing file and rerun them there
    14. clean up the function
'''


def dijkstras_route(pkg_load, distances):
    ''''Return an optimal delivery route (a simple ordered list of package IDs_
    using Dijkstra's algorithm.'''
    route_order = []
    return route_order


def build_stop(location, distance_from_prev):  # do I need distances here?
    '''Return a Stop on a route.

    A Stop has these attributes:
        -
        -
        -
        -
    '''
    pkg_count = 1
    stop = Stop(location, [pkg_count], distance_from_prev, '')
    pkg_count += 1
    return stop


def build_route(pkg_load, distances, Locations):
    '''Return delivery route (list of stops) for a provided package-load.

    Data definition: A 'Stop' on a 'Route' is a list, containing:
        - location*
        - packages: list of packages to drop off at this location
        - distance_?
        - projected_arrival? (time_custom)
    A Route is then simply a list of Stops.

    *A Location is a namedtuple of num, landmark, address.
    '''
    route = []

    location = random.choice(Locations)

    for pkg in pkg_load:
        distance_from_prev = 5
        route.append(build_stop(location, distance_from_prev))
    return route

import random
from copy import deepcopy


def update_nn_distances(location, pkg_load_distances):
    '''Update the 2D list of distances used by nearest_neighbors_route to mark
    one location as already picked (so it isn't picked again).'''
    pass  # no return


def get_nearest_neighbor(location, pkg_load_distances):
    '''Return the location nearest to a provided location.'''
    location_num = 1  # the hub: a dummy value for now
    return location_num


def nearest_neighbors_route(pkg_load, pkg_load_distances):
    '''Return total distance traveled in a simulated route in which the route
    is built up from greedy nearest-neighbor selection.'''
    distance_traveled = 0
    return distance_traveled


def pick_load(pkgs_at_hub, distances):
    '''Return list of package IDs that performed the best from a simulation of
    many package selections and deliveries.'''
    pkg_load = random.sample(pkgs_at_hub, 16)  # if <16 at hub, program crashes
    return pkg_load


def dijkstras_route(pkg_load, distances):
    ''''Return an optimal delivery route (a simple ordered list of package IDs_
    using Dijkstra's algorithm.'''
    route_order = []
    return route_order


def build_stop(location, distances):
    '''Return a Stop on a route.

    A Stop has these attributes:
        -
        -
        -
        -
    '''
    stop = []
    return stop


def build_route(pkg_load, distances):
    '''Return delivery route (list of stops) for a provided package-load.'''
    route = []
    return route

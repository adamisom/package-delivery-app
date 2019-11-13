import random
from copy import deepcopy
from collections import namedtuple
from .time_custom import Time_Custom
from .hash import Hash


class RouteBuilder:
    '''On data structures and so forth used:

    A 'Neighbor' is a namedtuple, comprising:
        - location*
        - distance_from_prev: distance from previous stop

    A 'Stop' on a 'Route' is a namedtuple, comprising:
        - location*
        - distance_from_prev: distance from previous stop
        - packages: list of packages to drop off at this location
      ( - projected_arrival: a Time_Custom object )
    A Route is then simply a list of Stops.
    A 'Stop' is upgraded to a 'StopPlus' in build_stops_for_routes.

    * A Location is itself a namedtuple of num, landmark, address.
    '''
    Neighbor = namedtuple(
        'Neighbor', ['location', 'distance_from_prev'])
    Stop = namedtuple(
        'Stop', ['location', 'distance_from_prev', 'packages'])
    StopPlus = namedtuple(
        'StopPlus', ['location', 'distance_from_prev', 'packages',
                     'projected_arrival'])

    def __init__(self, route_parameters):
        self.available_packages = route_parameters['available_packages'],
        self.distances = route_parameters['distances']
        self.max_load = route_parameters['max_load']
        self.truck_number = route_parameters['truck_number']
        # the following parameters are needed only by build_stops_for_route:
        self.Locations = route_parameters['Locations']
        self.speed_function = route_parameters['speed_function']
        self.starting_location = route_parameters['starting_location']
        self.initial_leave_time = route_parameters['initial_leave_time']

        self.package_load = []
        self.route = []
        self.candidate_stops = self.candidate_stops()  # a list

        # use below in comprehension (to get ALL locs for pkg list)
        self.pkgs_to_locations = dict()  # [pkgs_to_locations for x in pkgidss]
        self.route_distance = 0

    def candidate_stops(self):
        '''Create list of stops not yet in route which contain
        available_packages.

        Uses available_packages.'''
        pass

    def find_nearest(self, starting_location):
        '''Return nearest neighbor to starting_location.

        Uses distances, candidate_stops.'''
        pass

    def pick_packages_for_deliver_with_constraints(self):
        '''Augment package_load with any other packages that must be delivered
        with those currently in package_load.

        If unable to meet deliver-with constraints (because max_load would be
        exceeded), return tuple of negative one plus list of packages to be
        removed from package_load. Calling methods will recognize the -1.

        SIDE NOTE: It is okay to adjust for the off-by-one error in the csv.
        Called by each of the five main ones.

        Uses available_packages.'''
        pass

    def pick_packages_requiring_this_truck(self):
        '''Augment package_load with packages that must go on this truck.
        Do not exceed a package_load size of max_load.

        Uses available_packages, max_load, package_load,
        route, truck_number.'''
        pass

    def pick_packages_with_deadlines(self):
        '''Augment package_load with packages that have deadlines, in order of
        deadline time (earliest first).
        Do not exceed a package_load size of max_load.

        I think I'll have it only pick up up to half of all packages that
        have deadlines, on the assumptions that (1) at least two trucks drive
        out at 8, (2) they'll have plenty of time, and I want to try this at
        all because (3) I assume not being so restricted on the first truck's
        route will lead to better average mileage for truck 1 + truck 2.

        Specifically--I really want to pick up packages on the way. That's
        where most of my mileage savings will be.

        Uses available_packages, max_load, package_load, route.'''
        pass

    def pick_packages_on_the_way(self):
        '''Augment package_load with packages that are going to the same
        destinations as packages already in package_load.
        Do not exceed a package_load size of max_load.

        Uses available_packages, max_load, package_load,
         route, candidate_stops, pkgs_to_locations.'''
        pass

    def add_nearby_neighbors(self):
        '''
        Do not exceed a package_load size of max_load.

        Uses available_packages, distances, max_load,
        package_load, route, candidate_stops.'''
        pass

    def add_stops_at_end(self):
        '''
        Do not exceed a package_load size of max_load.

        Uses available_packages, distances, max_load,
        package_load, route, candidate_stops.'''
        pass

    def optimize_route(self):
        '''Repeatedly reorder segments (or subroutes) of route until
        a shorter overall distance cannot be found.

        Uses distances, route.  Purpose: swap segments.'''
        pass

    def get_projected_arrival(self):
        '''Return projected arrival time for a stop on a route.

        Uses speed_function, route, route! (for previous stop).'''
        pass

    def add_projected_arrival_times(self):
        '''Replace each Stop in route with a StopPlus having projected arrival.

        Uses Locations, speed_function, starting_location, initial_leave_time,
        package_load, route! (route is used to get a previous_stop).'''
        pass

    def build_route(self):
        '''Return a delivery route (list of stops).
        Notes:
        1. The following functions mutate package_load, route,
        and candidate_stops.
        2. If package_load is size max_load after any one of these calls,
        subsequent calls won't add any more to the load or the route.
        3. Each function does its own check for deliver-with constraints.
        '''
        self.pick_packages_requiring_this_truck()
        self.pick_packages_with_deadlines()
        self.pick_packages_on_the_way()
        self.add_nearby_neighbors()
        self.add_stops_at_end()
        self.optimize_route()
        self.add_projected_arrival_times()

        return self.route, self.package_load

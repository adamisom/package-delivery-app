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
        - projected_arrival: a Time_Custom object
    A Route is then simply a list of Stops.

    * A Location is itself a namedtuple of num, landmark, address.
    '''
    Neighbor = namedtuple(
        'Neighbor', ['location', 'distance_from_prev'])
    Stop = namedtuple(
        'Stop', ['location', 'distance_from_prev',
                 'packages', 'projected_arrival'])

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
        self.simple_route = []
        self.candidate_stops = self.candidate_stops()  # a list

        # use below in comprehension (to get all locs for pkg list)
        self.pkgs_to_locations = dict()  # [pkgs_to_locations for x in pkgidss]

        self.route = []
        self.route_distance = 0

    def candidate_stops(self):
        '''Uses available_packages.'''
        pass

    def find_nearest(self, starting_location):
        '''Uses distances, candidate_stops.'''
        pass

    def pick_packages_for_deliver_with_constraints(self):
        '''Called by each of the five main ones.'''
        pass

    def pick_packages_requiring_this_truck(self):
        '''Uses available_packages, max_load, package_load,
        simple_route, truck_number.'''
        pass

    def pick_packages_with_deadlines(self):
        '''Uses available_packages, max_load, package_load,
        simple_route.'''
        pass

    def pick_packages_on_the_way(self):
        '''Uses available_packages, max_load, package_load,
         simple_route, candidate_stops, pkgs_to_locations.'''
        pass

    def add_nearby_neighbors(self):
        '''Uses available_packages, distances, max_load,
        package_load, simple_route, candidate_stops.'''
        pass

    def add_stops_at_end(self):
        '''Uses available_packages, distances, max_load,
        package_load, simple_route, candidate_stops.'''
        pass

    def optimize_route(self):
        '''Uses distances, simple_route.  Purpose: swap segments.'''
        pass

    def get_projected_arrival(self):
        '''Uses speed_function, simple_route, route! (for previous stop).'''
        pass

    def build_stops_for_route(self):
        '''Uses Locations, speed_function, starting_location,
        initial_leave_time, package_load, simple_route, pkgs_to_locations.'''
        pass

    def build_route(self):
        '''Return a delivery route (list of stops).
        Notes:
        1. The following functions mutate package_load, simple_route,
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
        self.build_stops_for_route()

        return self.route, self.package_load

import random
from collections import namedtuple
from .route_builder import improve_route
from .time_custom import Time_Custom
from .hash import Hash

class RouteBuilder():
    '''On namedtuples used:
    A 'Neighbor' is a namedtuple, comprising:
        - loc: a Location*'s num property
        - dist: distance from previous stop
    A 'Stop' on a 'Route' is a namedtuple, comprising:
        - loc: a Location*'s num property
        - dist: distance from previous stop
        - pkgs: list of packages to drop off at this location
    A Route is then simply a list of Stops.
    A 'Stop' is upgraded to a 'StopPlus' at the end.
    A StopPlus has a location* instead of just a location number, plus it has
        - arrival: a proejcted arrival time (Time_Custom objec)
    * A Location is itself a namedtuple of num, landmark, address.

    I use the namedutple _replace method to create new ones. Per the docs*,
    since namedtuples are accessed via dot notation, "To prevent conflicts
    with field names, the method and attribute names start with an underscore."
    In other words the _ does not indicate _replace is supposed to be private.
    * https://docs.python.org/3/library/collections.html#collections.namedtuple
    '''
    Neighbor = namedtuple('Neighbor', ['loc', 'dist'])
    Stop = namedtuple('Stop', ['loc', 'dist', 'pkgs'])
    StopPlus = namedtuple('StopPlus', ['loc', 'dist', 'pkgs', 'arrival'])

    def __init__(self, route_parameters):
        self.available_pkgs = route_parameters['available_packages']
        self.distances = route_parameters['distances']
        self.max_load = route_parameters['max_load']
        self.truck_number = route_parameters['truck_number']
        self.Locations = route_parameters['Locations']
        self.speed_function = route_parameters['speed_function']
        self.starting_location = route_parameters['starting_location']
        self.initial_leave_time = route_parameters['initial_leave_time']

        self.route = []

    def display_stop(self, stop):
        '''Display one stop.'''
        pkgs = ''.join(['\tPkg '+p.props['ID']+'/'+p.props['location'].address
                        for p in stop.pkgs.sort(key=lambda p: p.props['ID'])])
        print(f'Stop. At: {stop.location}, +{stop.dist}mi, w/{pkgs}')

    def display_route(self, called_by):
        '''Display route.'''
        stops = '\n'.join([display_stop(stop) for stop in self.route])
        print(f'{called_by}, Route is {self.compute_route()}mi, with {stops}')
        print(f'\n\nLoad has {len(self.get_packages())} pkgs, including: '
              f'{[str(pkg) for pkg in self.get_packages()]}', '-' * 79)

    def get_locations(self):
        '''Return list of location-numbers/locations currently in route.'''
        return [stop.location for stop in self.route]

    def get_packages(self):
        '''Return list of all packages currently in route.'''
        return [stop.packages for stop in self.route]

    def compute_route(self):
        '''Return total distance of route.'''
        return sum([stop.distance_from_prev for stop in self.route])

    def Location_from_number(self, num):
        '''Return a Location from a location-number.'''
        return [L for L in self.Locations if L.num==num][0]

    def add_first_stop(self):
        '''Add first stop.'''
        self.route.append(RouteBuilder.Stop(self.starting_location, 0, []))

    def add_final_stop(self):
        '''Add final stop. (This must be done before route uses StopPluses.)'''
        dist = self.distances[self.route[-1].location][1]
        self.route.append(RouteBuilder.Stop(self.starting_location, dist, []))

    def unvisited_with_packages(self):
        '''Return list of unvisited location-numbers that have packages.'''
        stops_with_pkgs = list(set([
            pkg.props['location'].num for pkg in self.available_pkgs
            if pkg not in self.get_packages()]))
        # start at 2 because col 0 isn't distance data, and col 1 is the hub
        return [loc_num for loc_nu in self.distances[0][2:]
                if loc_num in stops_with_pkgs and
                loc_num not in self.get_locations()]

    def find_nearest(self, Stop, optional_list=None):
        '''Return nearest neighbor-with-packages to Stop passed in.'''
    starting_from = zip(self.distances[0], self.distances[Stop.location])
    eligible_neighbors = [RouteBuilder.Neighbor(loc_num, dist)
                          for (loc_num, dist) in starting_from
                          if loc_num in self.unvisited_with_packages()]
    return min(eligible_neighbors,
               key=lambda neighbor: neighbor.distance_from_prev)



    def build_route(self):
        '''Return a delivery route (list of stops).'''
        if len(self.available_packages) == 0:
            return []  # empty route

        self.route = improve_route(self.route, self.distances,
                                   RouteBuilder.Stop)

        pass

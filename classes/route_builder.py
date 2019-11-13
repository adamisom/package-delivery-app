import random
from copy import deepcopy
from collections import namedtuple
from itertools import permutations
from .time_custom import Time_Custom
from .hash import Hash


class RouteBuilder:
    '''On data structures and so forth used:

    A 'Neighbor' is a namedtuple, comprising:
        - location: a Location*'s num property
        - distance_from_prev: distance from previous stop

    A 'Stop' on a 'Route' is a namedtuple, comprising:
        - location: a Location*'s num property
        - distance_from_prev: distance from previous stop
        - packages: list of packages to drop off at this location
    A Route is then simply a list of Stops.

    A 'Stop' is upgraded to a 'StopPlus' in build_stops_for_routes.
    A StopPlus has a location* instead of just a location number, plus
        - projected_arrival: a Time_Custom object

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
        '''Create list of stops which contain available_packages.

        NOTE that candidate-stops is a PER-ROUTE variable.
        It is totally okay to remove stops from it, as __main__
        will make a new route-builder for each route of each truck.

        What is it supposed to do?
         - filter all stops (distances[0][1:]) to include only stops
         with packages in available_packages having that location ID
         I'M READY

        Uses available_packages.'''
        pass

    def find_nearest(self, starting_location):
        '''Return nearest neighbor to starting_location.

        What is it supposed to do?
         - find nearest candidate_stop to provided starting_location
            - get distance-row for starting location
            - among eligible neighbors (must be 'in' candidate_stops),
            pick nearest, via min(.., key=lambda thing: the distance)
         - return Neighbor object (location, distance_from_prev tuple)
         I'M READY

        Uses distances, candidate_stops.'''
        pass

    def get_deliver_with_packages(self, packages_to_check):
        '''Return list of all packages that need to be delivered with any
        package from packages_to_check.

        What is it supposed to do?
         - get IDs from any deliver-with constraints from any package to check
         - return list of packages having those IDs
        I'M READY

        SIDE NOTE: It is okay to adjust for the off-by-one error in the csv.
        Called by each of the five main ones.

        Uses available_packages.'''
        pass

    def pick_packages_requiring_this_truck(self):
        '''Augment package_load with packages that must go on this truck.
        Do not exceed a package_load size of max_load.

        What is it supposed to do?
         * Note: DO NOT remove any stops from self.candidate_stops
         - get packages having truck-constraint
         - get set-of-locations for those pkgs
         - loop while len(route) <= max_load and len(set-of-locations) > 0
            - call self.find_nearest, passing in the set-of-locations
            - check for other packages there not already in package_load
            and then add to that any resulting from deliver_with constraint
            - if room
                - create a Stop and add packages from those with constraint
                - append Stop to route
            - remove location from set-of-locations
        I'M READY

        Uses available_packages, max_load, package_load,
        route, truck_number.'''
        pass

    def pick_packages_with_deadlines(self):
        '''Augment package_load with packages that have deadlines, in order of
        deadline time (earliest first).
        Do not exceed a package_load size of max_load.

        What is it supposed to do?
         * Note: DO NOT remove any stops from self.candidate_stops
         - get (some?*) packages having a deadline*
         - get set-of-locations for those pkgs
         - loop while len(route) <= max_load and len(set-of-locations) > 0
            - call self.find_nearest, passing in the set-of-locations
            - check for other packages there not already in package_load
            and then add to that any resulting from deliver_with constraint
            - if room
                - create a Stop and add packages from those with constraint
                - append Stop to route
            - remove location from set-of-locations
        I'M READY

        *I think I'll have it only pick up up to half of all packages that
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

        What is it supposed to do?
         - get all location numbers currently in route (from deadline/truck)
         - loop while len(route) <= max_load and len(candidate_stops) > 0
         - loop location numbers for packages currently in package_load
            - check for other packages there not already in package_load
            and then add to that any resulting from deliver_with constraint
            - if room, update Stop's package list
            - remove that stop from self.candidate_stops
        I'M READY

        Uses available_packages, max_load, package_load,
        route, candidate_stops, pkgs_to_locations (MAYBE).
        Note/TODO: If nothing else uses pkgs_to_locations, delete it.'''
        pass

    def add_nearby_neighbors(self):
        '''Add more stops to route, interleaved throughout current route, when
        doing so would not make route much longer, until either max_load is
        reached or candidate_stops is exhausted.

        Say we're looking at stop i and stop j. This method would see if there
        exists a stop k (with packages) such that going from i to k to j does
        not take more than twice (2x) as long as going from i to j.

        What is it supposed to do?
         - loop while len(route) <= max_load and len(candidate_stops) > 0
         and also not yet reached the end of the route (do not add to end)
            - return if current stop/index is last in route-so-far
            - get current stop/index-in-route and call find_nearest with it
            - check for other packages there not already in package_load
            and then add to that any resulting from deliver_with constraint
            - if room, add pkgs to self.package_load
                - and create a Stop
                - and append Stop to route
            - remove that stop from self.candidate_stops
            - increment current stop/index
        I'M READY

        Uses available_packages, distances, max_load,
        package_load, route, candidate_stops.'''
        pass

    def add_stops_at_end(self):
        '''Add more stops to route at the end, until either max_load is
        reached or candidate_stops is exhausted.

        What is it supposed to do?
         - loop while len(route) <= max_load and len(candidate_stops) > 0
            - get current route-end and call self.find_nearest with it
            - check the # of packages there, after calling deliver_with
            - if room, add pkgs to self.package_load
                - and create a Stop
                - and append Stop to route
            - remove that stop from self.candidate_stops
        I'M READY

        Uses available_packages, distances, max_load,
        package_load, route, candidate_stops.'''
        pass

    def get_subroute_distance(self, ordering):
        '''Return distance of a subroute (helper to optimize_route).

        What is it supposed to do?
         - loop subroute and accumulate distance, then return it
        I'M READY

        Uses distances.
        '''
        pass

    def optimize_route(self):
        '''Reorder the ordering of stops in segments (or subroutes) of size 7
        whenever a shorter segment distance can be found by reordering.

        Why 7? Please read on. (tl;dr to balance runtime and optimality).
        * For a segment of size n, check every possible permutation of
        stop-orders to find the one with the shortest distance.
        * If we did this for the entire route, we'd have a guaranteed shortest
        distance--but the runtime would be O(n!)
        * However.. O(n!) is not so bad if we limit n. I know--this seems TOO
        easy/simple. But hey--why NOT check if subroutes can be reordered to
        make a shorter overall route?
        * For a given segment, I keep the start and end fixed and permute the
        order of stops in between. This means (n-2)! orderings are checked per
        segment. This means (m-n+1) * (n-2)! total permutations are checked,
        where m = total route length (+1 because do wrap-around to end at hub)
        * For n=7, (n-2)! = 5! = 120, which is not so bad. It's very fast to
        compute one route distance and computing 120 isn't so bad either.

        What is it supposed to do?
        - ooh! one thing it needs to do is check the wrap-around to see if the
        last segment/leg that returns to hub benefits from swapping
        - so first I need to temporarily append the ending point if the other
        methods haven't added it to the end, and likewise prepend to front
        - needs to keep track of whether it shortened route because it should
        return True/False based off that. just grab length at beginning and
        compare at end, that is straightforward and readable.
        - loop the route (len(route) - 7 + 1 iterations)
            - generate permutations of the innards of the segment (5 long)
            - augment permutations to have 2-lists instead, [1] for distance
            - loop the segment's permutations
                - append get_subroute distance to the [1] of that item
                    - make sure to pass in start and end(total length 7 not 5)
            - replace contents of route at that slice(e.g.route[0:n]) w/ min()
                orderings = permutations(list_slice)
                augmented = [[list(ordering)] for ordering in orderings]
                ...you can now append dist, due to the list-in-list-in-list
                finally, replace with min(augmented, key=lambda o: o[1])
        I'M READY
            Except for one thing: need to know if route at the point this is
            called will start at the hub, as well as if it already ends at hub

        Uses distances, route.  Purpose: swap segments, using swap_ helper.'''
        n = 7
        pass

    def get_projected_arrival(self):
        '''Return projected arrival time for a stop on a route.

        What is it supposed to do?
         - from a previous stop location and proj arrival compute proj arrival
         for the calling stop, using speed_function and distance_from_prev
         - makes a time_custom object
         1. I'll want to do one print statement to verify it's working-that
         the previous stop had proj_arrival, and that this one is time_custom
        I'M READY

        Uses speed_function, route, route! (for previous stop).'''
        pass

    def add_projected_arrival_times_and_Locations(self):
        '''Replace each Stop in route with a StopPlus--add projected arrival,
        and replace location number with reference to a Location.

        What is it supposed to do?
         - take in a route using Stops and return a route using StopPluses
         - for each stop
            - get_projected_arrival
            - get Location
            - build StopPlus
        I'M READY

        Uses Locations, speed_function, starting_location, initial_leave_time,
        package_load, route! (route is used to get a previous_stop).'''
        pass

    def build_route(self):
        '''Return a delivery route (list of stops).

        What is it supposed to do?
         - pick a good package load, and have a route built up along the way
         - augment with projected arrivals and return... that is it.
         1. call each function
            I will want to write print statements after each call
            to examine what load is up to that point.
            a. how to pretty print packages from a load
                pretty_pkgs = '\n'.join([str(pkg) for pkg
                                         in __])
                print(f'All Packages/IDs: {pretty_pkgs}')
            b. where to put it: once after each self._ call
                and print truck num too:
                print(f'Truck number {self.truck_number} now has load:')
        I'M READY

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
        self.add_projected_arrival_times_and_Locations()

        return self.route, self.package_load

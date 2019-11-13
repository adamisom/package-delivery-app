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
        self.available_packages = route_parameters['available_packages']
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
        self.candidate_stops = []

        # use below in comprehension (to get ALL locs for pkg list)
        self.pkgs_to_locations = dict()  # [pkgs_to_locations for x in pkgidss]
        self.route_distance = 0

    def get_candidate_stops(self):
        '''Create list of stops which contain available_packages.

        NOTE that candidate-stops is a PER-ROUTE variable.
        It is totally okay to remove stops from it, as __main__
        will make a new route-builder for each route of each truck.

        What is it supposed to do?
         - filter all stops (distances[0][1:]) to include only stops
         with packages in available_packages having that location ID
        I'M DONE

        Uses available_packages.'''
        all_stops = [Location.num for Location in self.Locations]
        stops_from_packages = [pkg.props['location'].num for pkg
                               in self.available_packages]
        return list(set(stops_with_packages))

    def find_nearest(self, Stop, optional_list=None):
        '''Return nearest neighbor to location of Stop passed in.

        find_nearest relies on self.candidate_stops being updated every time
        a new stop is added to the route, so that nearest doesn't (uselessly)
        return a stop already in the route.
        Likewise, if optional_list is passed in, it relies on that list not
        including any stops already in the route.

        It also relies on the fact that load.py sets Location numbers
        to be the same as row and column indices on distances.

        What is it supposed to do?
         - find nearest candidate_stop to provided starting_location
            - get distance-row for starting location
            - among eligible neighbors (must be 'in' candidate_stops),
            pick nearest, via min(.., key=lambda thing: the distance)
         - return Neighbor object (location, distance_from_prev tuple)
         I'M DONE

        Uses distances, candidate_stops.'''
        starting_location = Stop.location
        from_start = zip(self.distances[0], self.distances[starting_location])
        neighbors_from_start = [Neighbor(loc_num, dist)
                                for (loc_num, dist) in from_start]
        neighbors_from_start = neighbors_from_start[1:]  # [0] isn't dist data
        eligible_destinations = optional_list or self.candidate_stops
        eligible_neighbors = [neighbor for neighbor in neighbors_from_start
                              if neighbor.location in eligible_destinations]

        return min(eligible_neighbors,
                   key=lambda neighbor: neighbor.distance_from_prev)

    def get_deliver_with_packages(self, packages_to_check):
        '''Return list of all packages that need to be delivered with any
        package from packages_to_check--which is a single stop's packages.

        What is it supposed to do?
         - get IDs from any deliver-with constraints from any package to check
         - return list of packages having those IDs
        I'M DONE

        SIDE NOTE: It is okay to adjust for the off-by-one error in the csv.
        Called by each of the five main ones.

        Uses available_packages.'''
        from_deliver_constraints = []
        for pkg in packages_to_check:
            deliver_with = pkg.props['special_note']['deliver_with']
            if deliver_with:
                from_deliver_constraints += [ID for ID in deliver_with]
        return [pkg for pkg in self.available_packages
                if pkg.props['ID'] in from_deliver_constraints and
                pkg not in self.package_load]

    def pick_packages_requiring_this_truck(self):
        '''Augment package_load with packages that must go on this truck.
        Do not exceed a package_load size of max_load.
        Do not remove a stop from candidate_stops--pick_packages_on_the_way
        needs to be able to check it again.

        What is it supposed to do?
         * Note: DO NOT remove any stops from self.candidate_stops
         - get list of the packages having truck-constraint
         - get set-of-locations for those pkgs
         - loop while (len(self.package_load) <= self.max_load and
         len(set-of-locations) > 0):
            - call self.find_nearest, passing in the set-of-locations
            - see what would need to be delivered-with
            - if room
                - create a Stop and add packages from those with constraint
                - append Stop to route
            - remove location from set-of-locations

        I'M NOT DONE, BECAUSE:
            I HAVE TO take into account deadlines at stops ALREADY in route
            Right now code assumes all deadline-pkgs will be at NEW stops
            This will involve making sure new_locations only has.. NEW locs!

        Uses available_packages, max_load, package_load,
        route, truck_number.'''
        having_truck_constraint = []
        for pkg in self.available_packages:
            truck_num = pkg.props['special_note']['truck_number']
            if truck_num and truck_num == self.truck_number:
                if pkg not in self.package_load:
                    having_truck_constraint.append(pkg)
        new_locations = list(set([pkg.props['location'].num
                                  for pkg in having_truck_constraint]))

        while (len(self.package_load) <= self.max_load and
                len(new_locations) > 0):
            # THIS WILL THROW ERROR IF ROUTES AREN'T INITIALIZED WITH 1/HUB
            nearest = self.find_nearest(route[-1], new_locations)
            for_here = [pkg for pkg in having_truck_constraint
                        if pkg.props['location'].num == nearest.location]
            goes_with = self.get_deliver_with_packages(for_here)
            if len(self.package_load + for_here + goes_with) <= self.max_load:
                route.append(Stop(nearest.location,
                                  nearest.distance_from_prev,
                                  for_here + goes_with))

            new_locations.remove(nearest.location)

    def pick_packages_with_deadlines(self):
        '''Augment package_load with packages that have deadlines, in order of
        deadline time (earliest first).
        Do not exceed a package_load size of max_load.
        Do not remove a stop from candidate_stops--pick_packages_on_the_way
        needs to be able to check it again.

        What is it supposed to do?
         * Note: DO NOT remove any stops from self.candidate_stops
         - get (some?*) packages having a deadline*
         - get set-of-locations for those pkgs
         - loop while (len(self.package_load) <= self.max_load and
         len(set-of-locations) > 0):
            - call self.find_nearest, passing in the set-of-locations
            - see what would need to be delivered-with
            - if room
                - create a Stop and add packages from those with constraint
                - append Stop to route
            - remove location from set-of-locations

        I'M NOT DONE, BECAUSE:
            I HAVE TO take into account deadlines at stops ALREADY in route
            Right now code assumes all deadline-pkgs will be at NEW stops
            This will involve making sure new_locations only has.. NEW locs!

        Uses available_packages, max_load, package_load, route.'''
        having_deadlines = []
        for pkg in self.available_packages:
            deadline = pkg.props['deadline']
            if deadline:
                having_deadlines.append(pkg)
        # If the truck would be over half full just from deadline-packages,
        # let the next truck grab some. This code isn't 'smart' about which
        # ones it keeps, so it could grab only one of a few that are heading
        # to the same place, but pick_packages_on_the_way oughta fix that.
        deadlines_selection = having_deadlines[:(self.max_load/2)]

        new_locations = list(set([pkg.props['location'].num
                                  for pkg in deadlines_selection]))

        while (len(self.package_load) <= self.max_load and
                len(new_locations) > 0):
            # THIS WILL THROW ERROR IF ROUTES AREN'T INITIALIZED WITH 1/HUB
            nearest = self.find_nearest(route[-1], new_locations)
            for_here = [pkg for pkg in deadlines_selection
                        if pkg.props['location'].num == nearest.location]
            goes_with = self.get_deliver_with_packages(for_here)
            if len(self.package_load + for_here + goes_with) <= self.max_load:
                route.append(Stop(nearest.location,
                                  nearest.distance_from_prev,
                                  for_here + goes_with))

            new_locations.remove(nearest.location)

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
        I'M DONE

        Uses available_packages, max_load, package_load,
        route, candidate_stops, pkgs_to_locations (MAYBE).
        Note/TODO: If nothing else uses pkgs_to_locations, delete it.'''
        for stop in route:
            if self.package_load == self.max_load:
                break
            more_at_stop = [pkg for pkg in self.available_packages
                            if pkg.props['location'].num == stop.location and
                            pkg not in self.package_load]
            if len(self.package_load + more_at_stop) <= self.max_load:
                stop.packages += more_at_stop

            self.candidate_stops.remove(stop.location)

    def add_nearby_neighbors(self, acceptable_increase):
        '''For each pair of stops in route, see if there is a nearby neighbor
        that can be inserted between them.

        Neighbor will not be inserted if the would-be sub-route of three stops
        is more than acceptable_increase times as long as the sub-route of two
        stops is without it.
        Method stops when the first of these conditions is fulfilled:
        - max_load is reached
        - candidate_stops are exhausted
        - end of the route

        What is it supposed to do?
         - loop while (len(self.package_load) <= self.max_load and
         len(self.candidate_stops) > 0):
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
        I'M DONE

        Uses available_packages, distances, max_load,
        package_load, route, candidate_stops.'''
        for index, stop in enumerate(route):
            # TODO: modify ==0 to ==1 once I have routes initialized with hub
            if len(self.package_load) == self.max_load:
                break
            if len(self.candidate_stops) == 0:
                break
            if len(route) == 0 or stop == route[-1]:
                break

            nearest = find_nearest(stop)  # is Neighbor, not Stop (that's ok)
            current_next = route[index + 1]

            subroute = [stop, nearest, current_next]

            if (get_subroute_distance(subroute) <=
                    acceptable_increase *
                    distances[stop.location][current_next.location]):

                pkgs_at = [pkg for pkg in self.available_packages
                           if pkg.props['location'].num == nearest.location]

                route.insert(index,
                             Stop(nearest.location,
                                  nearest.distance_from_prev,
                                  pkgs_at))

            self.candidate_stops.remove(stop.location)

    def add_stops_at_end(self):
        '''Add more stops to route at the end, until either max_load is
        reached or candidate_stops is exhausted.

        What is it supposed to do?
         - loop (len(self.package_load) <= self.max_load and
         len(self.candidate_stops) > 0):
            - get current route-end and call self.find_nearest with it
            - check the # of packages there, after calling deliver_with
            - if room, add pkgs to self.package_load
                - and create a Stop
                - and append Stop to route
            - remove that stop from self.candidate_stops
        I'M DONE

        Uses available_packages, distances, max_load,
        package_load, route, candidate_stops.'''
        while (len(self.package_load) <= self.max_load and
                len(self.candidate_stops) > 0):
            # THIS WILL THROW ERROR IF ROUTES AREN'T INITIALIZED WITH 1/HUB
            nearest = self.find_nearest(route[-1])
            for_here = [pkg for pkg in self.available_packages
                        if pkg.props['location'].num == nearest.location]
            goes_with = self.get_deliver_with_packages(for_here)
            if len(self.package_load + for_here + goes_with) <= self.max_load:
                route.append(Stop(nearest.location,
                                  nearest.distance_from_prev,
                                  for_here + goes_with))

            self.candidate_stops.remove(stop.location)

    def get_subroute_distance(self, subroute):
        '''Return distance of a subroute (helper to optimize_route).

        Items in subroute are only required to have a location number.

        What is it supposed to do?
         - loop subroute and accumulate distance, then return it
        I'M DONE

        Uses distances.
        '''
        distance = 0
        for index, stop in enumerate(subroute):
            if stop == subroute[-1]:
                break
            start, end = stop, subroute[index+1]
            distance += distances[start][end]
        return distance

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
        I'M DONE
            Except for one thing: need to know if route at the point this is
            called will start at the hub, as well as if it already ends at hub

        Uses distances, route.  Purpose: swap segments, using swap_ helper.'''
        n = 7
        # CODE WILL THROW ERROR IF ROUTE DOES NOT ALREADY END IN THE HUB
        for index_into_route in range(len(route) - n):
            start, end = index_into_route, index_into_route + n
            subroutes = list(permutations(self.route[start:end]))
            with_distances = [(subroute, get_subroute_distance(subroute))
                              for subroute in subroutes]
            shortest = min(with_distances, key=lambda subr: subr[1])

            self.route = self.route[:start] + shortest[0] + self.route[end:]

    def get_projected_arrival(self, stop):
        '''Return projected arrival time for a stop on a route.

        What is it supposed to do?
         - from a previous stop location and proj arrival compute proj arrival
         for the calling stop, using speed_function and distance_from_prev
         - makes a time_custom object
         1. I'll want to do one print statement to verify it's working-that
         the previous stop had proj_arrival, and that this one is time_custom
        I'M DONE

        Uses speed_function, route, route! (for previous stop).'''
        index = self.route.index(stop)

        if index == 0:
            return self.initial_leave_time

        previous = route[index - 1]

        avg_speed = speed_function(previous.location, stop.location)
        minutes = 60 * (stop.distance_from_prev / avg_speed)
        projected_arrival = Time_Custom.clone(previous.projected_arrival)
        projected_arrival.add_time(minutes)

        return projected_arrival

    def add_projected_arrival_times_and_Locations(self):
        '''Replace each Stop in route with a StopPlus--add projected arrival,
        and replace location number with reference to a Location.

        What is it supposed to do?
         - take in a route using Stops and return a route using StopPluses
         - for each stop
            - get_projected_arrival, passing in stop
            - get Location
            - build StopPlus
        I'M DONE

        Uses Locations, speed_function, starting_location, initial_leave_time,
        package_load, route! (route is used to get a previous_stop).'''
        upgraded = []

        for stop in self.route:
            Location = [Loc for Loc in Locations if Loc.num == stop.location]
            projected_arrival = get_projected_arrival(stop)
            upgraded.append(StopPlus(Location,
                                     stop.distance_from_prev,
                                     stop.packages,
                                     projected_arrival))

        self.route = upgraded

    def display_route_params_and_candidate_stops(self):
        '''.
        '''
        pass

    def display_load(self):
        '''.
        '''
        pretty_pkgs = ''
        # pretty_pkgs = '\n'.join([str(pkg) for pkg
        #                          in self.package_load])
        # print(f'All Packages/IDs: {pretty_pkgs}')
        pass

    def display_route(self):
        '''.
        '''
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
        if len(self.available_packages) == 0:
            return self.route, self.package_load  # both were empty-initialized

        self.get_candidate_stops()
        self.display_route_params_and_candidate_stops()

        self.pick_packages_requiring_this_truck()
        self.display_load()
        self.pick_packages_with_deadlines()
        self.display_load()
        self.pick_packages_on_the_way()
        self.display_load()
        self.add_nearby_neighbors(1.75)  # experiment with acceptable_increase
        self.display_load()
        self.add_stops_at_end()
        self.display_load()

        self.display_route()
        self.optimize_route()
        self.display_route()
        self.add_projected_arrival_times_and_Locations()
        self.display_route()

        return self.route, self.package_load

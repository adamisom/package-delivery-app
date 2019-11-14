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
        self.ready_pkgs = route_parameters['available_packages']
        self.distances = route_parameters['distances']
        self.max_load = route_parameters['max_load']
        self.truck_num = route_parameters['truck_number']
        self.Locations = route_parameters['Locations']
        self.speed_function = route_parameters['speed_function']
        self.starting_location = route_parameters['starting_location']
        self.initial_leave_time = route_parameters['initial_leave_time']

        self.route = []

    def get_locations(self):
        '''Return list of location-numbers/locations currently in route.'''
        return [stop.location for stop in self.route]

    def get_packages(self):
        '''Return list of all packages currently in route.'''
        return [stop.packages for stop in self.route]

    def display_stop(self, stop):
        '''Display one stop.'''
        pkgs = ''.join(['\tPkg '+p.props['ID']+'/'+p.props['location'].address
                        for p in stop.pkgs.sort(key=lambda p: p.props['ID'])])
        print(f'Stop. At: {stop.location}, +{stop.dist}mi, w/{pkgs}')

    def compute_dist(self):
        '''Return total distance of route.'''
        return sum([stop.distance_from_prev for stop in self.route])

    def display_route(self, called_by):
        '''Display route.'''
        stops = '\n'.join([display_stop(stop) for stop in self.route])
        print(f'{called_by}, Route is {self.compute_dist()}mi, with {stops}')
        print(f'\n\nLoad has {len(self.get_packages())} pkgs, including: '
              f'{[str(pkg) for pkg in self.get_packages()]}', '-' * 79)

    def grouped_deliver_with_constraints(self):
        '''Return list of lists of available-packages' IDs where each list
        comprises IDs of packages that must be delivered together.'''
        deliver_withs = [pkg for pkg in self.available_pkgs
                         if pkg.props['special_note']['deliver_with']]
        sets = []
        for pkg in deliver_withs:
            IDs = pkg.props['ID'] + pkg.props['special_note']['deliver_with']
            IDs = set(IDs)
            # if this is a subset of a set in sets, skip
            if any(IDs.issubset(set_) for set_ in sets):
                continue
            # if a strict subset of this exists in sets, delete that, add this
            IDs_subsets = [set_ for set_ in sets if IDs.issuperset(set_)]
            sets = [set_ for set_ in sets if set_ not in IDs_subsets]
            sets.append(IDs)
            # if this overlaps with a set in sets, merge into this and replace
            # if there are no overlaps, neither IDs nor sets will be changed
            overlaps = [set_ for set_ in sets if not IDs.isdisjoint(set_)]
            sets = [set_ for set_ in sets if set_ not in overlaps]
            IDs = IDs.union(*overlaps)
            sets.append(IDs)
        return [list(set_) for set_ in sets]

    def unvisited_with_packages(self):
        '''Return list of unvisited locations with ready unpicked packages.'''
        stops_with_pkgs = list(set([
            pkg.props['location'].num for pkg in self.packages_left()]))
        # start at 2 because col 0 isn't distance data, and col 1 is the hub
        return [loc_num for loc_nu in self.distances[0][2:]
                if loc_num in stops_with_pkgs and
                loc_num not in self.get_locations()]

    def get_packages_left(self):
        '''Return list of packages ready to go not already in route.'''
        return list(set(self.ready_pkgs) - set(self.get_packages()))

    def find_nearest(self, Stop, optional_list=None):
        '''Return nearest neighbor-with-packages to Stop passed in.'''
        starting_from = zip(self.distances[0], self.distances[Stop.location])
        eligible_neighbors = [RouteBuilder.Neighbor(loc_num, dist)
                              for (loc_num, dist) in starting_from
                              if loc_num in self.unvisited_with_packages()]
        return min(eligible_neighbors,
                   key=lambda neighbor: neighbor.distance_from_prev)

    def get_truck_constraint_packages(self):
        '''Return list of packages left that must go on this truck.'''
        return [pkg for pkg in self.packages_left()
                if pkg.props['special_note']['truck_number'] and
                pkg.props['special_note']['truck_number'] == self.truck_num]

    def get_most_urgent_packages(self):
        '''Return list of packages left with deadline before 10:00 AM.'''
        return [pkg for pkg in self.packages_left()
                if pkg.props['deadline'] and
                pkg.props['deadline'] <= Time_Custom(10, 00, 00)]  # <= not <

    def get_packages_on_the_way(self):
        '''Return list of packages left for stops already on the route.'''
        return [pkg for pkg in self.packages_left()
                if pkg.props['location'].num in self.get_locations()]

    def get_other_deadline_packages(self):
        '''Return list of packages left with deadline after 10:00 AM.'''
        return [pkg for pkg in self.packages_left()
                if pkg.props['deadline'] and
                pkg.props['deadline'] > Time_Custom(10, 00, 00)]

    def add_first_stop(self):
        '''Add first stop.'''
        self.route.append(RouteBuilder.Stop(self.starting_location, 0, []))

    def add_final_stop(self):
        '''Add final stop.'''
        dist = self.distances[self.route[-1].location][1]
        self.route.append(RouteBuilder.Stop(self.starting_location, dist, []))

    def Location_from_number(self, num):
        '''Return a Location from a location-number.'''
        return [L for L in self.Locations if L.num == num][0]

    def get_projected_arrival(self, stop):
        '''Return projected arrival time for a stop on a route.'''
        index = self.route.index(stop)
        if index == 0:
            return self.initial_leave_time
        previous = self.route[index - 1]
        avg_speed = self.speed_function(previous.loc, stop.loc)
        minutes = 60 * (stop.dist / avg_speed)
        projected_arrival = Time_Custom.clone(previous.arrival)
        try:  # TODO: take out this try/except when I know my app works
            projected_arrival.add_time(minutes)
        except ValueError:
            print(f'\n\tUH OH! Tried adding {minutes} minutes\n')
        return projected_arrival

    def convert_to_stopplus(self):
        '''Replace each Stop in route with a StopPlus--add projected arrival,
        and replace location number with reference to a Location.'''
        for index, stop in enumerate(self.route):
            Location = self.Location_from_number(stop.loc)
            projected_arrival = self.get_projected_arrival(stop)
            self.route[index] = RouteBuilder.StopPlus(
                Location, stop.dist, stop.pkgs, projected_arrival)

    def build_route(self):
        '''Return a delivery route (list of stops).
        NOTES:
            - Do NOT add ANY deliver-with package unless you can add ALL.
            - POSSIBLE LOGIC BUG: anything that treats all stops as equal
            when the hub (start and end) need to be treated differently.
            - LOGIC AMBIGUITY/POSSIBLE BUG--noticed in unvisited_with_packages
            stops_with_pkgs assumes pick up packages on way ALREADY HAPPENED
            because if it didn't before this was called, this function would
            select some "partially" visited locations
        '''
        if len(self.available_pkgs) == 0:
            return []  # empty route
        self.add_first_stop()
        # cool stuff after this line
        ############################
        dummy = 0
        while len(self.get_packages() < self.max_load) and dummy < 100:

            dummy += 1

        ############################
        # cool stuff above this line
        self.add_final_stop()  # must be done before next two lines
        self.route = improve_route(self.route, self.distances,
                                   RouteBuilder.Stop)
        self.convert_to_stopplus()
        return self.route

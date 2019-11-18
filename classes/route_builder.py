import random
from collections import namedtuple
from .route_helpers import improve_route
from .time_custom import Time_Custom
from .hash import Hash
import pdb  # TEMPORARY


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
        - arrival: a projected arrival time (Time_Custom objec)
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
        self.initial_leave = route_parameters['initial_leave_time']

        self.route = []

    def get_locations(self):
        '''Return list of location-numbers/locations currently in route.'''
        return [stop.loc for stop in self.route]

    def get_packages(self):
        '''Return list of all packages currently in route.'''
        return [pkg for stop in self.route for pkg in stop.pkgs]

    def sort_by_hub_closeness(self, pkgs=None):
        '''Return packages sorted by closeness to hub.'''
        return sorted(
            pkgs if pkgs else self.get_packages(),
            key=lambda pkg: self.distances[1][pkg.props['location'].num])

    def compute_dist(self):
        '''Return total distance of route.'''
        return round(sum([stop.dist for stop in self.route]), 2)

    def display_packages(self, pkgs):
        '''Pretty-print list of packages passed in.'''
        print('\n'.join([str(pkg) for pkg in pkgs]))

    def display_stop(self, stop):
        '''Display one stop.'''
        pkgs = ''.join(
            [f"\n\tPkg {str(p.props['ID']).rjust(2)}, to go to location "
             f"{p.props['location'].num} /\t{p.props['location'].address}"
             for p in sorted(stop.pkgs, key=lambda p: p.props['ID'])])
        print(f'This Stop is number {self.route.index(stop)+1} on the route, '
              f'to go location #{stop.loc}, which is {stop.dist} miles from '
              f'the last stop, and has these packages:{pkgs}')

    # def route_to_file(self, filename):
    #     '''TEMPORARY, display_route but to a file.'''
    #     with open(filename, 'w') as f:
    #         print(f'ROUTE is {self.compute_dist()}mi, with stops', file=f)
    #         for stop in self.route:
    #             pkgs = ''.join(
    #                 [f"\n\tPkg {str(p.props['ID']).rjust(2)}, to go to location "
    #                  f"{p.props['location'].num} /\t{p.props['location'].address}"
    #                  for p in sorted(stop.pkgs, key=lambda p: p.props['ID'])])
    #             overall = (f'This Stop is number {self.route.index(stop)+1} on the route, '
    #                        f'to go location #{stop.loc}, which is {stop.dist} miles from '
    #                        f'the last stop, and has these packages:{pkgs}')
    #             print(overall, file=f)
    #         print(f'Load has {len(self.get_packages())} pkgs:', file=f)
    #         for pkg in self.get_packages():
    #             print(str(pkg), file=f)
    #         print('-' * 79, file=f)

    def display_route(self, called_by=''):
        '''Display route.'''
        print(f'{called_by}/ ROUTE is {self.compute_dist()}mi, with stops:')
        for stop in self.route:
            self.display_stop(stop)
        print(f'Load has {len(self.get_packages())} pkgs, including:')
        for pkg in self.get_packages():
            print(str(pkg))
        print('-' * 79)

    def grouped_deliver_with_constraints(self):
        '''Return list of lists of ready packages, sorted smaller first,
        each list comprising packages that must be delivered together.'''
        deliver_withs = [pkg for pkg in self.ready_pkgs
                         if pkg.props['special_note']['deliver_with']]
        sets = []
        for pkg in deliver_withs:
            IDs = [pkg.props['ID']] + pkg.props['special_note']['deliver_with']
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

        pkgs_from_IDs = [[pkg for pkg in self.ready_pkgs
                          if pkg.props['ID'] in set_]
                         for set_ in sets]
        return sorted(pkgs_from_IDs, key=lambda lst: len(lst))

    def get_most_urgent_packages(self):
        '''Return list of packages left with deadline before 10:00 AM.'''
        return [pkg for pkg in self.packages_left()  # TODO: just do ready_pkgs
                if pkg.props['deadline'] and
                pkg.props['deadline'] <= Time_Custom(10, 00, 00)]  # <= not <

    def get_truck_constraint_packages(self):
        '''Return list of packages left that must go on this truck.'''
        return [pkg for pkg in self.packages_left()  # TODO: just do ready_pkgs
                if pkg.props['special_note']['truck_number'] and
                pkg.props['special_note']['truck_number'] == self.truck_num]

    def get_other_deadline_packages(self):
        '''Return list of packages left with deadline after 10:00 AM.'''
        return [pkg for pkg in self.packages_left()  # TODO: just do ready_pkgs
                if pkg.props['deadline'] and
                pkg.props['deadline'] > Time_Custom(10, 00, 00)]

    def get_packages_on_the_way(self, pkg_load):
        '''Return list of packages destined for same place as any package in
        passed-in list (called before any packages are added to route).'''
        locations_for_pkg_load = list(set([pkg.props['location'].num
                                           for pkg in pkg_load]))
        return [pkg for pkg in list(set(self.ready_pkgs) - set(pkg_load))
                if pkg.props['location'].num in locations_for_pkg_load]

    def forbid_overfilling_load(self, so_far, more):
        '''Return package-list whose size does not exceed self.max_load, and
        which combines lists so_far and more (note: so_far could be empty).'''
        if len(so_far) + len(more) > self.max_load:
            closer_first = self.sort_by_hub_closeness(more)
            max_minus_current = self.max_load - len(so_far)
            more = closer_first[:max_minus_current]
        return list(set(so_far).union(set(more)))

    def forbid_partial_deliver_groups(self, groups, pkgs_to_load):
        '''Return package-list having no partial deliver-with groups.'''
        updated = pkgs_to_load[:]
        for pkg in pkgs_to_load:
            for deliver_group in groups:
                if pkg in deliver_group:
                    together = list(set(updated).union(set(deliver_group)))
                    if len(together) <= self.max_load:
                        updated = together
                    else:
                        updated.remove(pkg)
        return updated

    def packages_left(self):
        '''Return list of packages ready to go not already in route.'''
        return list(set(self.ready_pkgs) - set(self.get_packages()))

    def unvisited_stops_with_packages(self):
        '''Return list of unvisited locations at which at least one ready,
        unpicked package needs to be dropped off.'''
        stops_with_pkgs = list(set([
            pkg.props['location'].num for pkg in self.packages_left()]))
        # start at 2 because col 0 isn't distance data, and col 1 is the hub
        return [loc_num for loc_num in self.distances[0][2:]
                if loc_num in stops_with_pkgs and
                loc_num not in self.get_locations()]

    def find_nearest(self, Stop, location_list=None):
        '''Return nearest neighbor-with-packages to Stop passed in.'''
        starting_from = zip(self.distances[0], self.distances[Stop.loc])
        eligible_location_nums = (location_list if location_list
                                  else self.unvisited_stops_with_packages())
        eligible_neighbors = [RouteBuilder.Neighbor(loc_num, dist)
                              for (loc_num, dist) in starting_from
                              if loc_num in eligible_location_nums]
        return min(eligible_neighbors,
                   key=lambda neighbor: neighbor.dist)

    def add_first_stop(self):
        '''Add first stop.'''
        self.route.append(RouteBuilder.Stop(self.starting_location, 0, []))

    def add_final_stop(self):
        '''Add final stop.'''
        dist = self.distances[self.route[-1].loc][1]  # from previous to hub
        self.route.append(RouteBuilder.Stop(self.starting_location, dist, []))

    def get_earliest_deadline_for_stop(self, stop):
        '''Return earliest deadline, if any, for a given stop in the route.'''
        deadlines = [pkg.props['deadline'] for pkg in stop.pkgs
                     if pkg.props['deadline']]
        return min(deadlines) if len(deadlines) > 0 else None

    def Location_from_number(self, num):
        '''Return a Location from a location-number.'''
        return [L for L in self.Locations if L.num == num][0]

    def get_projected_arrival(self, stop):
        '''Return projected arrival time for a stop on a route.'''
        index = self.route.index(stop)
        if index == 0:
            return self.initial_leave
        previous = self.route[index - 1]
        avg_speed = self.speed_function(previous.loc, stop.loc)
        minutes = 60 * (stop.dist / avg_speed)
        projected_arrival = Time_Custom.clone(previous.arrival)
        projected_arrival.add_time(minutes)
        return projected_arrival

    def convert_to_stopplus(self):
        '''Replace each Stop in route with a StopPlus--add projected arrival,
        and replace location number with reference to a Location.'''
        for index, stop in enumerate(self.route):
            Location = self.Location_from_number(stop.loc)
            projected_arrival = self.get_projected_arrival(stop)
            self.route[index] = RouteBuilder.StopPlus(
                Location, stop.dist, stop.pkgs, projected_arrival)

    # # TEMPORARY
    # def display_all_package_locations(self):
    #     pkgs = ''.join(
    #         [f"\n\tPkg {str(p.props['ID']).rjust(2)}, to go to location "
    #          f"{p.props['location'].num} /\t{p.props['location'].address}"
    #          for p in sorted(self.ready_pkgs,
    #                          key=lambda p: p.props['location'].num)])
    #     # key=lambda p: p.props['ID'])])
    #     print('\nALL ready packages\' locations:', pkgs)
    #     print('-' * 79)

    def add_nearby_neighbors(self, acceptable_increase):
        '''Add nearby neighbors found throughout the route-so-far if doing so
        wouldn't increase distance much (determined by acceptable_increase).'''
        stop_index = 0

        while (len(self.get_packages()) < self.max_load and
               len(self.unvisited_stops_with_packages()) > 0):

            stop = self.route[stop_index]
            if stop == self.route[-1]:
                break

            nearest = self.find_nearest(stop)
            cur_next = self.route[stop_index + 1]
            if nearest == cur_next:
                continue

            distance_with_nearest = (self.distances[stop.loc][nearest.loc] +
                                     self.distances[nearest.loc][cur_next.loc])

            if distance_with_nearest <= acceptable_increase * cur_next.dist:
                for_here = [pkg for pkg in self.packages_left()
                            if pkg.props['location'].num == nearest.loc]
                excess_removed = self.forbid_overfilling_load(
                    self.get_packages(), for_here)
                for_here = list(set(excess_removed) - set(self.get_packages()))

                if len(for_here) > 0:
                    self.route.insert(stop_index + 1, (RouteBuilder.Stop(
                        nearest.loc, nearest.dist, for_here)))

            stop_index += 1

    def build_route(self):
        '''Return a delivery route (list of stops).
        TEMPORARY NOTES:
            - How To:
                (*) update a stop's packages, if need be:
                stop = stop._replace(pkgs=new_list)
                (*) print a list of pkgs
                print('\nAFTER:'); self.display_packages(pkgs_to_load)
        '''
        if len(self.ready_pkgs) == 0:
            return []

        # TEMPORARY
        # self.display_all_package_locations()

        self.add_first_stop()

        groups = self.grouped_deliver_with_constraints()

        #    I.    Add urgent packages and truck-constraint packages first.
        # If truck is leaving at or after 9am, get packages with non-urgent
        # deadlines too. Also add any that must be delivered with those.
        # Note that no Stops for the route are being created yet.
        pkgs_to_load = self.get_most_urgent_packages()
        pkgs_to_load = self.forbid_overfilling_load([], pkgs_to_load)
        # print('\nAFTER most urgent:'); self.display_packages(pkgs_to_load)

        more_to_load = self.get_truck_constraint_packages()
        if self.initial_leave > Time_Custom(8, 00, 00):
            more_to_load += self.get_other_deadline_packages()
        pkgs_to_load = self.forbid_overfilling_load(pkgs_to_load, more_to_load)

        pkgs_to_load = self.forbid_partial_deliver_groups(groups, pkgs_to_load)

        #    II.   Get other packages that would be 'on the way'.
        # Also get any that must be delivered with those.
        more_to_load = self.get_packages_on_the_way(pkgs_to_load)
        pkgs_to_load = self.forbid_overfilling_load(pkgs_to_load, more_to_load)
        pkgs_to_load = self.forbid_partial_deliver_groups(groups, pkgs_to_load)

        #    III.  Add other deliver-with groups that will fit, smallest-first,
        # and remove packages in remaining groups from consideration.
        # The idea for the first part of that is to get deliver-with packages
        # out of the way as soon as possible, and the idea for the second part
        # is to not have to worry about partial groups again while route-
        # building.
        # NOTE: it is likely the first route of the day will be longer than
        # successive trips, as it is mostly driven by package constraints,
        # rather than nearest-neighbors / distance.
        for group in groups:  # deliver-with method sorted them smallest-first
            new_list = list(set(pkgs_to_load).union(set(group)))
            if len(new_list) <= self.max_load:
                pkgs_to_load = new_list
                groups.remove(group)

        delivwith_pkgs_left = [pkg for group in groups for pkg in group]
        self.ready_pkgs = list(set(self.ready_pkgs) - set(delivwith_pkgs_left))

        #    IV.   Construct stops from pkgs_to_load and add to route.
        locs = list(set([pkg.props['location'].num for pkg in pkgs_to_load]))
        while len(locs) > 0:
            nearest = self.find_nearest(self.route[-1], locs)
            pkgs_for_stop = [pkg for pkg in pkgs_to_load
                             if pkg.props['location'].num == nearest.loc]
            self.route.append(RouteBuilder.Stop(
                nearest.loc, nearest.dist, pkgs_for_stop))
            locs.remove(nearest.loc)

        #    V.    Look for nearby neighbors between each stop-pair on route
        # PLEASE NOTE: ~1.6 is simply the parameter that performed well for me
        # with my sample data. It may need to be changed if given more data!
        acceptable_increase = 1.6
        self.add_nearby_neighbors(acceptable_increase)

        #    VI.   Add more stops near the end of the route
        while (len(self.get_packages()) < self.max_load and
               len(self.unvisited_stops_with_packages()) > 0):

            nearest = self.find_nearest(self.route[-1])

            more = [pkg for pkg in self.packages_left()
                    if pkg.props['location'].num == nearest.loc]
            all_pkgs = self.forbid_overfilling_load(self.get_packages(), more)
            at_this_stop = list(set(all_pkgs) - set(self.get_packages()))

            self.route.append(RouteBuilder.Stop(
                nearest.loc, nearest.dist, at_this_stop))

        #    VII.  Re-order stops on route to get shorter total distance,
        # so long as deadlines wouldn't be missed. Note that the code up to
        # now doesn't itself guarantee deadlines will be missed--that's a nice
        # double-duty that improve_route is doing for us. Natural place, b/c ..
        self.add_final_stop()
        # curr = self.route
        # temp = improve_route(self.route, self.distances,
                             # RouteBuilder.Stop)
        # self.route = temp
        # print(f'Route after improve_route would be:')
        # self.route_to_file('with_improve.txt')
        # print(f'Whereas otherwise it is:')
        # self.route_to_file('without_improve.txt')
        # self.display_route()
        # print(f'\n')
        stop_deadlines = [(stop.loc, self.get_earliest_deadline_for_stop(stop))
                          for stop in self.route]
        stop_deadlines = [sd for sd in stop_deadlines if sd[1]]  # remove Nones

        self.route = improve_route(self.route, self.distances, stop_deadlines,
                                   self.speed_function, self.initial_leave,
                                   RouteBuilder.Stop)
        # TEMPORARY:
        # self.display_route()

        #    VIII. Convert Stops on route to StopPluses and return route
        self.convert_to_stopplus()
        return self.route

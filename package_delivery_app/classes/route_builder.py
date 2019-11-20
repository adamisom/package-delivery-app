from collections import namedtuple
from .route_helpers import improve_route
from .time_custom import Time_Custom
from .hash import Hash


class RouteBuilder():
    '''Class to build a single route, from hub to hub, for a truck.

    The entire "API" is the build_route method. All other methods are helpers.

    Notes on namedtuples used
    -------------------------
    A 'Neighbor' is a namedtuple, comprising:
        - loc: a Location*'s num property
        - dist: distance from previous stop

    A 'Stop' on a 'Route' is a namedtuple, comprising:
        - loc: a Location*'s num property
        - dist: distance from previous stop
        - pkgs: list of packages to drop off at this location
    A Route is then simply a list of Stops.

    # # TEMPORARY / considering
    # A 'MaybeStop' is used near the beginning and is a 'Stop' plus a
    #     - deadline: earliest deadline for this maybe-stop
    # MaybeStops are used to ensure that all packages-with-deadlines selected
    # in the first step of route-building can definitely be delivered on time.

    A 'Stop' is upgraded to a 'StopPlus' at the end.
    A StopPlus has a Location* instead of just a location number, plus it has
        - arrival: a projected arrival time (Time_Custom objec)

    * A Location is itself a namedtuple of num, landmark, address.
    '''
    Neighbor = namedtuple('Neighbor', ['loc', 'dist'])
    # Stop = namedtuple('Stop', ['loc', 'dist', 'pkgs'])
    # # TEMPORARY
    # MaybeStop = namedtuple('MaybeStop', ['loc', 'dist', 'pkgs', 'deadline'])
    StopPlus = namedtuple('StopPlus', ['loc', 'dist', 'pkgs', 'arrival'])

    def __init__(self, route_parameters):
        self.ready_pkgs = route_parameters['available_packages']
        self.distances = route_parameters['distances']
        self.max_load = route_parameters['max_load']
        self.truck_num = route_parameters['truck_number']
        self.Locations = route_parameters['Locations']
        self.speed_function = route_parameters['speed_function']
        self.starting_location = route_parameters['starting_location']
        self.leaving_hub_at = route_parameters['leaving_hub_at']

        self.route = []

    def get_locations(self):
        '''Return list of location-numbers/locations currently in route.'''
        return [stop.loc for stop in self.route]

    def get_packages(self):
        '''Return list of all packages currently in route.'''
        return [pkg for stop in self.route for pkg in stop.pkgs]

    def sort_pkgs_by_hub_closeness(self, pkgs=None):
        '''Return packages sorted by closeness to hub.'''
        return sorted(
            pkgs if pkgs else self.get_packages(),
            key=lambda pkg: self.distances[1][pkg.props['location'].num])

    def sort_locs_by_hub_closeness(self, location_nums=None):
        '''Return location-numbers list sorted by closeness to hub.'''
        return sorted(
            location_nums if location_nums else self.get_locations(),
            key=lambda loc_num: self.distances[1][loc_num])

    def compute_dist(self):
        '''Return total distance of route.'''
        return round(sum([stop.dist for stop in self.route]), 2)

    def display_packages(self, pkgs):
        '''Pretty-print list of packages passed in.'''
        print('\n'.join([str(pkg) for pkg in pkgs]))

    def display_stop(self, stop):
        '''Display one stop.'''
        pkgs = ',\t'.join(['Package #' + str(p.props['ID']) for p in
                           sorted(stop.pkgs, key=lambda p: p.props['ID'])])
        print(f'Stop {self.route.index(stop)+1}: truck is projected to arrive '
              f'by {str(stop.arrival)} to {stop.loc}, which is {stop.dist} '
              f'miles from the last stop, and has these packages:\n\t{pkgs}')

    def display_route(self, called_by='', show_load=False):
        '''Display route.'''
        if called_by:
            print(f'{called_by}')

        print('{:-^79}'.format(f' This Route is {self.compute_dist()}miles '))

        for stop in self.route:
            self.display_stop(stop)

        if show_load:
            print(f'Load has {len(self.get_packages())} pkgs, including:')
            for pkg in self.get_packages():
                print(str(pkg))

        print('*' * 79, '\n')

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
        '''Return list of packages left with deadline in 2 hours or less.'''
        two_hours_from_now = Time_Custom.clone(self.leaving_hub_at)
        two_hours_from_now.add_time(120)
        return [pkg for pkg in self.ready_pkgs
                if pkg.props['deadline'] and
                pkg.props['deadline'] <= two_hours_from_now]

    def get_truck_constraint_packages(self):
        '''Return list of packages left that must go on this truck.'''
        return [pkg for pkg in self.ready_pkgs
                if pkg.props['special_note']['truck_number'] and
                pkg.props['special_note']['truck_number'] == self.truck_num]

    def get_other_deadline_packages(self):
        '''Return list of packages left with deadline over 2 hours from now.'''
        two_hours_from_now = Time_Custom.clone(self.leaving_hub_at)
        two_hours_from_now.add_time(120)
        return [pkg for pkg in self.ready_pkgs
                if pkg.props['deadline'] and
                pkg.props['deadline'] > two_hours_from_now]

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
            closer_first = self.sort_pkgs_by_hub_closeness(more)
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
            return self.leaving_hub_at
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

    def add_more_deliverwith_groups(self, pkgs_to_load, groups):
        '''Add more deliver-with groups that will fit, smallest first.'''
        for group in groups:  # deliver-with method sorted them smallest-first
            new_list = list(set(pkgs_to_load).union(set(group)))
            if len(new_list) <= self.max_load:
                pkgs_to_load = new_list

        delivwith_pkgs_left = [pkg for group in groups for pkg in group]
        self.ready_pkgs = list(set(self.ready_pkgs) - set(delivwith_pkgs_left))

        return pkgs_to_load

    def construct_stops(self, pkgs_to_load):
        '''Construct stops for packages, in nearest-neighbor order, and append
        them to the route.'''
        locs = list(set([pkg.props['location'].num for pkg in pkgs_to_load]))
        while len(locs) > 0:
            nearest = self.find_nearest(self.route[-1], locs)
            pkgs_for_stop = [pkg for pkg in pkgs_to_load
                             if pkg.props['location'].num == nearest.loc]
            self.route.append(RouteBuilder.Stop(
                nearest.loc, nearest.dist, pkgs_for_stop))
            locs.remove(nearest.loc)

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

    def add_stops_at_end(self):
        '''Add stops at end using nearest-neighbors until load is full or
        no more destination stops exist.'''
        while (len(self.get_packages()) < self.max_load and
               len(self.unvisited_stops_with_packages()) > 0):

            nearest = self.find_nearest(self.route[-1])

            more = [pkg for pkg in self.packages_left()
                    if pkg.props['location'].num == nearest.loc]
            all_pkgs = self.forbid_overfilling_load(self.get_packages(), more)
            at_this_stop = list(set(all_pkgs) - set(self.get_packages()))

            if len(at_this_stop) > 0:
                self.route.append(RouteBuilder.Stop(
                    nearest.loc, nearest.dist, at_this_stop))

    def deadline_packages_guaranteed_ontime(self, maybe_stops):
        '''FILL ME IN/Clarify proj = projected. I MAY NOT NEED THIS.(Worth?)'''
        #     8. loop NN route and if any stop arrival > deadline, return False
        #     9. else return True
        for maybe_stop in maybe_stops:
            # if potential_stop.arrival > potential_stop.deadline:
            if maybe_stop[4] > maybe_stop[3]:  # 4=arrival 3=deadline
                return False
        return True

    def construct_maybe_stops(self, locs, maybe_stops):
        '''FILL ME IN.'''
        # first location is the hub (1); no deadline and arrival=leaving_at_hub
        nn_route = [(1, [], None, self.leaving_at_hub)]
        maybe_stops_copy = maybe_stops[:]
        distance_so_far = 0

        while len(maybe_stops_copy) > 0
            nearest = self.find_nearest(locs)
            distance_so_far += nearest.dist
            maybe_stop, = [maybe_stop for maybe_stop in maybe_stops
                           if maybe_stop[0] == nearest.loc]

            avg_speed = 18  # self.speed_function(...)
            cumulative_minutes = 60 * (distance_so_far / avg_speed)
            projected_arrival = Time_Custom.clone(leaving_at_hub)
            projected_arrival.add_time(cumulative_minutes)

            nn_route.append(*maybe_stop, projected_arrival)
            maybe_stops_copy.remove(maybe_stops_copy.index(maybe_stop))

        return nn_route

    def forbid_impossible_deadline_combinations(self, deadline_pkgs):
        '''Return package-list which is sure to meet all deadlines;
        if it was already sure to be possible, no changes will be made.

        As input it takes a list of only packages that have deadlines.

        The reason that considering only deadline packages can guarantee that
        they still all get delivered on time when more stops and packages are
        added later is because there is at least one route that improve_route
        will find in all its permutations that meets deadlines: the one where
        all deadline stops are visited first before any others.

        Note that the naive nearest-neighbors check used by this method is only
        a quick-n-dirty way to assess whether all deadlines could be met early
        on in the route-building process--before a proper route is made at
        all, let alone before it's handed over to improve_route.

        FURTHER NOTE that this function does not use the Truck's speed-function
        flexibility as it was not deemed worth the effort. An assumption of
        this program is the truck is always going 18mph, stops included; I made
        it more flexible in places, but not here...
        '''
        # 1. get stop loc#s for deadline pkgs, AND PREPEND with stop 1/hub
        locs = list(set([pkg.props['location'].num for pkg in deadline_pkgs]))
        maybe_stops = [(loc, [pkg for pkg in deadline_pkgs
                              if pkg.props['location'].num == loc])
                       for loc in locs]

        # 2. get earliest deads for those stop loc#s
        maybe_stops = [(ms[0], ms[1],
                        min([pkg.props['deadline'] for pkg in deadline_pkgs
                             if pkg.props['location'].num == ms[0]]))
                       for ms in maybe_stops]

        # 3. construct NN route (IT NEED NOT go back to hub-lol! why would it!)
        # 4. compute times for each stop
        nn_route = self.construct_maybe_stops(locs, maybe_stops)

        # 5. while helper deadlines_met is false and length > 0
        while (not deadline_packages_guaranteed_ontime(maybe_stops) and
               len(maybe_stops) > 0):
        #     6. remove PACKAGES furthest from hub (and loop)
            furthest = self.sort_locs_by_hub_closeness(locs)[-1]
            pkgs_there = [pkg for pkg in deadline_pkgs
                          if pkg.props['location'].num == furthest]

            locs.remove(furthest)
            maybe_stop, = [ms for ms in maybe_stops if ms[0] == furthest]
            maybe_stops.remove(maybe_stop)

            # KEY (subtract furthest pkgs from deadline_pkgs):
            deadline_pkgs = list(set(deadline_pkgs) - set(pkgs_there))

        #     7. re-compute times for each stop (replacing MaybeStop)
            nn_route = self.construct_maybe_stops(locs, maybe_stops)

        # 10. return new list that may have some pkgs excluded
        return deadline_pkgs

    def build_route(self):
        '''Return a delivery route (list of stops).'''
        if len(self.ready_pkgs) == 0:
            return []

        self.add_first_stop()

        groups = self.grouped_deliver_with_constraints()

        #    I.    Add urgent packages first[, and those on the way.]?
        # If truck is leaving after its initial run, get non-urgent packages
        # with deadlines too. Also add any that must be delivered with those.
        # Note that 8:00am is the initial run for a truck, and this is an
        # assumption also made by the Truck class.
        # Also--unrelated--note that no Stops for the route are created yet.
        pkgs_to_load = self.get_most_urgent_packages()
        pkgs_to_load = self.forbid_overfilling_load([], pkgs_to_load)

        more_to_load = self.get_truck_constraint_packages()
        if self.leaving_hub_at > Time_Custom(8, 00, 00):
            more_to_load += self.get_other_deadline_packages()
        pkgs_to_load = self.forbid_overfilling_load(pkgs_to_load, more_to_load)

        pkgs_to_load = self.forbid_partial_deliver_groups(groups, pkgs_to_load)

        #    II.   Get other packages that would be 'on the way'.
        # Also get any that must be delivered with those.
        more_to_load = self.get_packages_on_the_way(pkgs_to_load)
        pkgs_to_load = self.forbid_overfilling_load(pkgs_to_load, more_to_load)
        pkgs_to_load = self.forbid_partial_deliver_groups(groups, pkgs_to_load)

        #    III.  Check whether it is possible to deliver all of the deadline
        # packages in pkgs_to_load on time, and if not, remove one at a time
        # (starting with those furthest from the hub) until it is possible.

        # TODO: split out/separate truck-constraint from step I
        self.forbid_impossible_deadline_combinations(pkgs_to_load)
        # ALSO TODO: forbid partial deliver groups again after the above, but
        # not quite: just plain remove any partial deliver goroups since if any
        # partials remain after forbid_impossib, they CAN'T all be deliv ontime

        #    IV.   Add truck-constraint packages, plus those that would be 'on
        # the way' and any that must be delivered-with.

        #    IV.   Add other deliver-with groups that will fit, smallest-first,
        # then remove packages in remaining groups from consideration. The idea
        # for the first part of that is to get deliver-with packages out of the
        # way as soon as possible, and the idea for the second part is to not
        # have to worry about partial groups again while route-building.
        #
        # Note: it is likely the first route of the day will be longer than
        # successive trips, as it is mostly driven by package constraints,
        # rather than nearest-neighbors / distance.
        pkgs_to_load = self.add_more_deliverwith_groups(pkgs_to_load, groups)

        #    V.    Construct stops from pkgs_to_load and add to route.
        self.construct_stops(pkgs_to_load)

        #    VI.   Look for nearby neighbors between each stop-pair on route
        # Note: ~1.6 is simply the parameter that performed well for me with
        # my sample data. It may need to be changed if given more data.
        acceptable_increase = 1.6
        self.add_nearby_neighbors(acceptable_increase)

        #    VII.  Add more stops near the end of the route
        self.add_stops_at_end()

        #    VIII. Re-order stops on route to get shorter total distance,
        # so long as deadlines wouldn't be missed.
        self.add_final_stop()

        stop_deadlines = [(stop.loc, self.get_earliest_deadline_for_stop(stop))
                          for stop in self.route]
        stop_deadlines = [sd for sd in stop_deadlines if sd[1]]  # remove Nones

        self.route = improve_route(self.route, self.distances, stop_deadlines,
                                   self.speed_function, self.leaving_hub_at,
                                   RouteBuilder.Stop)

        #    IX.   Convert Stops on route to StopPluses and return route
        self.convert_to_stopplus()
        return self.route

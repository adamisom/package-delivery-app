def get_deliver_with_packages(self, packages_to_check):
    '''Return list of all packages that need to be delivered with any
    package from packages_to_check--which is a single stop's packages.'''
    from_deliver_constraints = []
    for pkg in packages_to_check:
        deliver_with = pkg.props['special_note']['deliver_with']
        if deliver_with:
            from_deliver_constraints += [ID for ID in deliver_with]
    return [pkg for pkg in self.available_packages
            if pkg.props['ID'] in from_deliver_constraints and
            pkg not in self.package_load and
            pkg not in packages_to_check]

def pick_packages_requiring_this_truck(self):
    '''Augment package_load with packages that must go on this truck.
    Do not exceed a package_load size of max_load. Do not remove a stop
    from candidate_stops: pick_packages_on_the_way needs to check it again.
    '''
    having_truck_constraint = []
    for pkg in self.available_packages:
        truck_num = pkg.props['special_note']['truck_number']
        if truck_num and truck_num == self.truck_number:
            if pkg not in self.package_load:
                having_truck_constraint.append(pkg)

    new_locations = list(set([pkg.props['location'].num
                              for pkg in having_truck_constraint
                              if pkg.props['location'].num not in
                              self.get_route_locations()]))

    # packages going to locations already in route
    for stop in self.route:

        for_here = [pkg for pkg in having_truck_constraint
                    if pkg.props['location'].num == stop.location]

        if len(self.package_load) + len(for_here) <= self.max_load:
            stop = stop._replace(packages=stop.packages + for_here)
            self.package_load += for_here

    # packages going to locations not yet in route
    while (len(self.package_load) <= self.max_load and
            len(new_locations) > 0):
        nearest = self.find_nearest(self.route[-1], new_locations)
        for_here = [pkg for pkg in having_truck_constraint
                    if pkg.props['location'].num == nearest.location and
                    pkg not in self.package_load]
        goes_with = self.get_deliver_with_packages(for_here)

        if len(self.package_load + for_here + goes_with) <= self.max_load:
            self.package_load += for_here + goes_with
            self.route.append(RouteBuilder.Stop(nearest.location,
                                                nearest.distance_from_prev,
                                                for_here + goes_with))

        new_locations.remove(nearest.location)

def pick_packages_with_deadlines(self):
    '''Augment package_load with packages that have deadlines, in order of
    deadline time (earliest first).
    Do not exceed a package_load size of max_load. Do not remove a stop
    from candidate_stops: pick_packages_on_the_way needs to check it again.
    '''
    print('MADE it in pick_with_deadlines--which starts with route:', end='')
    self.display_route()

    having_deadlines = []
    for pkg in self.available_packages:
        deadline = pkg.props['deadline']
        if deadline:
            having_deadlines.append(pkg)

    # If the truck would be over half full just from deadline-packages,
    # let the next truck grab some. This code isn't 'smart' about which
    # ones it keeps, so it could grab only one of a few that are heading
    # to the same place, but pick_packages_on_the_way oughta fix that.
    up_to = int(self.max_load/2)
    # DEVELOPMENT note: for the first load, this function causes pkg 39
    # to be skipped-loc 7, like pkg 13-but packages_on_way picks up 39!
    deadlines_selection = having_deadlines[:up_to]

    new_locations = list(set([pkg.props['location'].num
                              for pkg in deadlines_selection
                              if pkg.props['location'].num not in
                              self.get_route_locations()]))
    print(f'INSIDE with_deadlines, new_locations is {new_locations}')

    # packages going to locations already in route
    for stop in self.route:
        for_here = [pkg for pkg in deadlines_selection
                    if pkg.props['location'].num == stop.location]
        if len(self.package_load) + len(for_here) <= self.max_load:
            stop = stop._replace(packages=stop.packages + for_here)
            self.package_load += for_here

    # packages going to locations not yet in route
    while (len(self.package_load) <= self.max_load and
            len(new_locations) > 0):
        nearest = self.find_nearest(self.route[-1], new_locations)
        for_here = [pkg for pkg in deadlines_selection
                    if pkg.props['location'].num == nearest.location and
                    pkg not in self.package_load]
        goes_with = self.get_deliver_with_packages(for_here)
        if len(self.package_load + for_here + goes_with) <= self.max_load:

            # temporary
            print(f'\nIn with-deadlines, AT STOP# {nearest.location},'
                  f'which has address {self.loc_by_num(nearest.location).address}')
            print(f'\tcurrent load is: {self.pretty_pkgs()}')
            print(f'\tfor_here is: {self.pretty_pkgs(for_here)}')
            print(f'\tgoes with is: {self.pretty_pkgs(goes_with)}')
            # self.package_load += for_here
            self.package_load += for_here + goes_with
            self.route.append(RouteBuilder.Stop(nearest.location,
                                                nearest.distance_from_prev,
                                                for_here + goes_with))

            print(f'INSIDE with_deadlines, new stop added, route is now', end='')
            self.display_route()

        new_locations.remove(nearest.location)

def pick_packages_on_the_way(self):
    '''Augment package_load with packages that are going to the same
    destinations as packages already in package_load.
    Do not exceed a package_load size of max_load.
    '''
    print('MADE it in pick_on_way--which starts with route:', end='')
    self.display_route()

    for stop in self.route:
        if self.package_load == self.max_load:
            break
        more_at_stop = [pkg for pkg in self.available_packages
                        if pkg.props['location'].num == stop.location and
                        pkg not in self.package_load]
        goes_with = self.get_deliver_with_packages(more_at_stop)
        if (len(self.package_load + more_at_stop + goes_with) <=
                self.max_load):
            self.package_load += more_at_stop + goes_with
            stop = stop._replace(packages=stop.packages +
                                 more_at_stop +
                                 goes_with)

        if stop.location != 1:  # the hub / 1 won't be in candidate stops
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
    '''
    print('MADE it in add nearby neighbors--which starts with route:', end='')
    self.display_route()

    for index, stop in enumerate(self.route):
        if len(self.package_load) == self.max_load:
            break
        if len(self.candidate_stops) == 0:
            break
        if stop == self.route[-1]:
            break

        nearest = self.find_nearest(stop)
        current_next = self.route[index + 1]

        subroute = [stop, nearest, current_next]

        if (self.get_subroute_distance(subroute) <=
                acceptable_increase *
                self.distances[stop.location][current_next.location]):

            for_here = [pkg for pkg in self.available_packages
                        if pkg.props['location'].num ==
                        nearest.location and
                        pkg not in self.package_load]
            goes_with = self.get_deliver_with_packages(for_here)

            if (len(self.package_load + for_here + goes_with) <=
                    self.max_load):
                self.package_load += for_here + goes_with

                self.route.insert(index + 1,
                                  RouteBuilder.Stop(
                                    nearest.location,
                                    nearest.distance_from_prev,
                                    for_here + goes_with))

        self.candidate_stops.remove(nearest.location)

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
    '''
    print(f'\nMADE IT inside add_stops_at_end...')
    print('Where route right now is:', end='')
    self.display_route()
    print(f'In add_stops_at_end candidate_stops is {self.candidate_stops}')

    while (len(self.package_load) <= self.max_load and
            len(self.candidate_stops) > 0):

        nearest = self.find_nearest(self.route[-1])

        print(f'nearest is: {nearest}')

        for_here = [pkg for pkg in self.available_packages
                    if pkg.props['location'].num == nearest.location and
                    pkg not in self.package_load]
        goes_with = self.get_deliver_with_packages(for_here)

        if (len(self.package_load + for_here + goes_with) <=
                self.max_load and len(for_here) > 0):
            self.package_load += for_here + goes_with

            self.route.append(RouteBuilder.Stop(nearest.location,
                                                nearest.distance_from_prev,
                                                for_here + goes_with))

        self.candidate_stops.remove(nearest.location)

def get_subroute_distance(self, subroute):
    '''Return distance of a subroute (helper to optimize_route).

    Items in subroute are required to have a location (number) property.
    '''
    distance = 0
    for index, stop in enumerate(subroute):
        if stop == subroute[-1]:
            break
        start, end = stop.location, subroute[index+1].location
        distance += self.distances[start][end]
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

    TODO: update each of the freaking stops' distances to change.
    Right now if I run display_route calling compute_distance() it doesn't
    chagne, and of course not, I never change it in the stop.
    A helper might be called for that takes route and makes new stops
    based on the (new) order they're in.

    TODO: don't let this method switch the first or last stops! (HUB!)
    Right now it is...

    UPDATE: both todos actually need fixing before I stop the time error :/
    '''
    n = 7

    for index_into_route in range(len(self.route) - n):
        start, end = index_into_route, index_into_route + n
        subroutes = list(permutations(self.route[start:end]))
        with_distances = [(subroute, self.get_subroute_distance(subroute))
                          for subroute in subroutes]
        shortest = min(with_distances, key=lambda subr: subr[1])

        # permutations creates tuples, this recreates the Stop namedtuples
        subroute_of_namedtuples = []
        for stop_tuple in shortest[0]:
            subroute_of_namedtuples.append(RouteBuilder.Stop(*stop_tuple))

        self.route = (self.route[:start] +
                      subroute_of_namedtuples +
                      self.route[end:])

def get_projected_arrival(self, stop):
    '''Return projected arrival time for a stop on a route.'''
    index = self.route.index(stop)

    if index == 0:
        return self.initial_leave_time

    previous = self.route[index - 1]

    print('\nTHIS stop and PREVIOUS stop are:')
    print(f'\t{stop}, \n\t{previous}')
    print('AND just locations...')
    # print(f'\t{stop.location}, \n\t{previous.location.num}')

    avg_speed = self.speed_function(previous.location, stop.location)
    print(f'\tspeed_function invoked is {self.speed_function(None,None)}')
    minutes = 60 * (stop.distance_from_prev / avg_speed)
    print(f'\tminutes is {minutes}')
    projected_arrival = Time_Custom.clone(previous.projected_arrival)

    # this shouldn't be happening..but I got a 2-length route, dist 0
    if len(self.route) == 2:
        minutes = 42

    print(f'\tcloned time is {str(projected_arrival)}')
    projected_arrival.add_time(minutes)

    return projected_arrival

def add_projected_arrival_times_and_Locations(self):
    '''Replace each Stop in route with a StopPlus--add projected arrival,
    and replace location number with reference to a Location.'''
    for index, stop in enumerate(self.route):
        Location = self.loc_by_num(stop.location)

        projected_arrival = self.get_projected_arrival(stop)

        self.route[index] = RouteBuilder.StopPlus(Location,
                                                  stop.distance_from_prev,
                                                  stop.packages,
                                                  projected_arrival)


def build_route(self):
    self.add_first_stop()  # starts at hub
    self.display_route('after add_first_stop')
    self.get_candidate_stops()

    self.pick_packages_requiring_this_truck()
    self.display_load('pick_packages_requiring_this_truck')
    self.pick_packages_with_deadlines()
    self.display_load('pick_packages_with_deadlines')
    self.pick_packages_on_the_way()
    self.display_load('pick_packages_on_the_way')
    self.add_nearby_neighbors(1.75)  # TODO: experiment with this number
    self.display_load('add_nearby_neighbors')
    self.add_stops_at_end()
    self.display_load('add_stops_at_end')

    self.add_final_stop()
    self.display_route()
    self.optimize_route()

    self.add_projected_arrival_times_and_Locations()
    self.display_route()

    return self.route, self.package_load

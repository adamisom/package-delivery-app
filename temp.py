''' TESTING SNIPPETS
(*) to test sget_other_deadline_packages
if self.initial_leave_time > Time_Custom(9, 00, 00):
            temp += self.get_other_deadline_packages()
(*)
'''


# # If the truck would be over half full just from deadline-packages,
# # let the next truck grab some. This code isn't 'smart' about which
# # ones it keeps, so it could grab only one of a few that are heading
# # to the same place, but pick_packages_on_the_way oughta fix that.
# up_to = int(self.max_load/2)
# # DEVELOPMENT note: for the first load, this function causes pkg 39
# # to be skipped-loc 7, like pkg 13-but packages_on_way picks up 39!
# deadlines_selection = having_deadlines[:up_to]

# # canonical stuff:
# nearest = self.find_nearest(self.route[-1]
# if len(self.package_load + for_here + goes_with) <= self.max_load:
# self.route.append(RouteBuilder.Stop(...))


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
    while (len(self.package_load) <= self.max_load and
            len(self.candidate_stops) > 0):
        nearest = self.find_nearest(self.route[-1])
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

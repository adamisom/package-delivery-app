''' TESTING SNIPPETS
(*) to test sget_other_deadline_packages
if self.initial_leave_time > Time_Custom(9, 00, 00):
            temp += self.get_other_deadline_packages()
(*) to test d-w groups get added for truck/deadline pkgs:
# put these 2 lines in main for truck/trucks
if 1 <= pkg.props['ID'] <= 21:  # go back and forth with 20/21
    pkg.props['special_note']['deliver_with'] = [15]
# put in route_builder
# add any packages that must be delivered with the above
updated = pkgs_to_load[:]  # TODO: try converting this to listcomp
for pkg in pkgs_to_load:
    for deliver_with in groups:
        if pkg in deliver_with:
            together = list(set(updated).union(set(deliver_with)))
            if len(together) <= self.max_load:
                updated += deliver_with
            else:
                updated.remove(pkg)
pkgs_to_load = updated
(*) to test d-w groups do get added smallest-first AFTER (next section)
for pkg in packages:  # inside main / for truck in trucks
    # pass
    if 1 <= pkg.props['ID'] <= 22:
        pkg.props['special_note']['deliver_with'] = [4]
    elif 23 <= pkg.props['ID'] <= 28:
        pkg.props['special_note']['deliver_with'] = [26]
    elif 29 <= pkg.props['ID'] <= 37:
        pkg.props['special_note']['deliver_with'] = [33]
    else:  # for pkg IDs 38-40
        pkg.props['special_note']['deliver_with'] = [39]
groups = self.grouped_deliver_with_constraints()
print_ = '\n*\n'.join(['\n'.join([str(p) for p in g]) for g in groups])
print(f'DELIVER-WITH GROUPS: {print_}\n')
for group in groups:
    new_list = list(set(pkgs_to_load).union(set(group)))
if len(new_list) <= self.max_load:
        pkgs_to_load += group
self.display_route()
(*) to view deliver-with groups
# prt_ = '\n*\n'.join(['\n'.join([str(p) for p in g]) for g in groups])
# print(f'DELIVER-WITH GROUPS: {prt_}\n')
'''

# # canonical stuff from older code:
# nearest = self.find_nearest(self.route[-1]
# if len(self.package_load + for_here + goes_with) <= self.max_load:
# self.route.append(RouteBuilder.Stop(...))

''' MISCELLANEOUS OR LOW_PRIORITY TODOS:
convert this(*1) into a listcomp(*2), and in case I change the code,
this is the section that checks for deliver-withs, specifically after
truck/deadline constraints are added, at the beginning of build_route
(*1) updated = pkgs_to_load[:]
for pkg in pkgs_to_load:
    for deliver_with in groups:
        if pkg in deliver_with:
            together = list(set(updated).union(set(deliver_with)))
            if len(together) <= self.max_load:
                updated += deliver_with
            else:
                updated.remove(pkg)
(*2) idea: start from deliver-with groups, not pkgs_to_load, like this:
for deliver_with_group in groups:
            if any([])
... I'm thinking the listcomp for the any will have to be nested somehow.

'''


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

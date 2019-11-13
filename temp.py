def get_nearest_neighbor(starting_from, destination_numbers, distances):
    '''Return the location-number nearest to a provided location-number.

    Inputs:
    - starting_from: a Location's num property. Locations are namedtuples
    of num, landmark, address.
    - destination_numbers: list of all location_numbers that need to be
    visited to drop off all packages on the simulated route.
    - distances: a 2D list wherein both column and row indices happen to be a
    location_number (due to how the Locations list of Location namedtuples was
    set up in load.py)
    '''

    # fetch the row holding distance information for provided location_number
    row_index = [row[0] for row in distances].index(starting_from)
    distances_from_start = distances[row_index]

    # make 2D list of location-number (column 1) and distance (column 2),
    # where the distance in column 2 is distance FROM provided location_number
    # TO a different destination (namely the one with col 1's location_number)
    transposed = list(zip(distances[0], distances_from_start))

    # only check neighbors we actually have to visit
    eligible_neighbors = [location_distance for location_distance in transposed
                          if location_distance[0] in destination_numbers and
                          location_distance[1] > 0]

    nearest = min(eligible_neighbors, key=lambda neighbor: neighbor[1])

    return nearest


def nearest_neighbors_route(destination_numbers, distances, max_load):
    '''Return an ordered route as well as total distance traveled for a
    given set of destinations (Locations) to visit, up to max_load locations.

    This function assumes trucks start at the hub (initial location 1).
    '''
    distance_traveled = 0
    location = 1
    route_order = []

    while (len(destination_numbers) > 0 and len(route_order) <= max_load):
        nearest_neighbor = get_nearest_neighbor(
            location, destination_numbers, distances)

        location = nearest_neighbor[0]
        route_order.append(location)
        destination_numbers.remove(location)

        distance_traveled += nearest_neighbor[1]

    return route_order, distance_traveled


def get_location_nums(pkgs):
    '''Return set of location numbers a route must visit to drop off all
    its packages.'''
    set_of_location_nums = set([pkg.props['location'].num for pkg in pkgs])
    return list(set_of_location_nums)


def pick_to_meet_deadlines(pkg_load, pkgs_at_hub):
    '''Return list of packages with a deadline before noon that are still at
    the hub (not loaded) if this truck is the last one to leave.

    Assumptions (two):
    - This function assumes that if a deadline is after 12:00 noon there will
    be plenty of time to deliver it on a truck's second run.
    - It also...assumes all trucks initially leave the hub at 8:00am.........
    '''
    return [pkg for pkg in pkgs_at_hub
            if pkg.props['deadline'] and
            pkg.props['deadline'] < Time_Custom(12, 00, 00) and
            pkg not in pkg_load]


def pick_to_satisfy_truck_constraints(pkg_load, pkgs_at_hub, truck_num):
    '''Return list of packages that need to go on the given truck-number.'''
    return [pkg for pkg in pkgs_at_hub
            if pkg.props['special_note']['truck_number'] == truck_num and
            pkg not in pkg_load]


def pick_same_destination_packages(pkg_load, pkgs_at_hub):
    '''Return list of all packages going to the same destinations as any
    package in the current package-load.'''
    set_of_location_nums = get_location_nums(pkg_load)
    return [pkg for pkg in pkgs_at_hub
            if pkg.props['location'].num in set_of_location_nums and
            pkg not in pkg_load]


def pick_to_satisfy_deliver_constraints(pkg_load, pkgs_at_hub):
    '''Return list of packages that must be delivered simultaneously with any
    packages currently in pkg_load, and in that list, include................

    This function assumes (in the append) that package IDs are unique.
    '''
    deliver_with = []
    for pkg in pkg_load:
        if pkg.props['special_note']['deliver_with']:
            for ID in pkg.props['special_note']['deliver_with']:
                deliver_with += [pkg for pkg in pkgs_at_hub
                                 if pkg.props['ID'] == ID]

    return [pkg for pkg in deliver_with if pkg not in pkg_load]


def add_up_to_max_load(pkg_load, candidates_to_add, max_load):
    '''Return list of packages with some to all of candidates_to_add
    added, up to max_load.
    TODO: raise error if pkg_load already > 16? '''
    while (len(pkg_load) <= max_load and
           len(candidates_to_add) > 0):
        pkg_load.append(candidates_to_add.pop())
    return pkg_load


def make_initial_selection(pkgs_at_hub, max_load, is_last, truck_num):
    '''Generate a partial selection of packages for loading based off of
    deadline, truck-number, same-destination, and deliver-with.'''
    load = []

    if is_last:
        candidates = pick_to_meet_deadlines(load, pkgs_at_hub)
        load = add_up_to_max_load(load, candidates, max_load)
    if len(load) == max_load:
        return load
    # print(f'after pick for deadlines (truck num {truck_num}, load is {load}, len-load is {len(load)}')

    candidates = pick_to_satisfy_truck_constraints(load, pkgs_at_hub,
                                                   truck_num)
    load = add_up_to_max_load(load, candidates, max_load)
    if len(load) == max_load:
        return load
    # print(f'after pick for truck.. (truck num {truck_num}, load is {load}, len-load is {len(load)}')

    candidates = pick_same_destination_packages(load, pkgs_at_hub)
    load = add_up_to_max_load(load, candidates, max_load)
    if len(load) == max_load:
        return load
    # if len(load) != 0:
    #     print(f'after pick for destination.. (truck num {truck_num}, load is {load}, len-load is {len(load)}')

    candidates = pick_to_satisfy_deliver_constraints(load, pkgs_at_hub)
    load = add_up_to_max_load(load, candidates, max_load)
    if len(load) == max_load:
        return load
    # if len(load) != 0:
    #     print(f'after pick for deliver-with.. (truck num {truck_num}, load is {load}, len-load is {len(load)}')

    return load


def add_throughout(load, order, candidate_locations,
                   pkgs_at_hub, distances, max_load):
    '''.'''
    new_route_order = order

    for index, location_num in enumerate(order):
        # immediately return if max_load has been reached
        if len(load) == max_load:
            return load

        # exit the loop one item early, due to the index + 1 look-ahead below
        if location_num == order[-1]:
            return load

        # nearest[0] is location, nearest[1] is distance-away
        nearest = get_nearest_neighbor(
            location_num, candidate_locations, distances)

        current_next = order[index + 1]
        possible_next = nearest[0]

        if possible_next != current_next:
            # if it wouldn't take twice as long or more, go to 'nearest' right
            # after this location, before going to current_next
            if (distances[location_num][possible_next] +
                    distances[possible_next][current_next] <
                    2 * distances[location_num][current_next]):
                new_route_order = (new_route_order[:index] + [possible_next] +
                                   new_route_order[index:])

    return new_route_order


def add_to_end(load, order, candidate_locations,
               pkgs_at_hub, distances, max_load):
    '''.'''
    distance_traveled = 0
    location = 1
    route_order = []

    while (len(destination_numbers) > 0 and len(route_order) <= max_load):
        nearest_neighbor = get_nearest_neighbor(
            location, destination_numbers, distances)

        location = nearest_neighbor[0]
        route_order.append(location)
        destination_numbers.remove(location)

        distance_traveled += nearest_neighbor[1]

    return route_order, distance_traveled


def make_load_selection(pkgs_at_hub, distances, max_load, is_last, truck_num):
    '''Generate one possible selection of packages for loading.'''

    # NEW IDEA:
    candidate_locations = get_location_nums(pkgs_at_hub)

    load = make_initial_selection(pkgs_at_hub, max_load, is_last, truck_num)
    order = []

    if len(load) > 0 and len(load) < max_load:
        destination_numbers = get_location_nums(load)
        candidate_locations = list(
            set(candidate_locations) - set(destination_numbers))

        nn_route = nearest_neighbors_route(
            destination_numbers, distances, max_load)
        order = nn_route[0]
        load = add_throughout(load, order, candidate_locations,
                              pkgs_at_hub, distances, max_load)

    load = add_to_end(load, order, candidate_locations,
                      pkgs_at_hub, distances, max_load)

    # get nearest-neighbor, but only for locations with any packages

    # call same_dest helper and add to load

    # call deliver_with helper and add to load

    # call helper to drop some(all, droppable) if I have too many

    # TODO: return an 'order'/distance tuple
    return random.sample(pkgs_at_hub, max_load)


def pick_load(pkgs_at_hub, distances, is_last, truck_num):
    '''Return list of package IDs that performed the best from a simulation of
    many package selections and deliveries.

    TO DO: update this so it no longer does a simulation.
    It's just not necessary, or helpful.
    Because make_load_selection will just be totally deterministic (and do NN)
    I can/should empirically test this by printing all simulated load dists,
    and if I'm in for a surprise (if they differ), I'll take a closer look!

    Inputs:
    - pkgs_at_hub: list of packages (references to Package objects)
    - distances: 2D list. distances[i][j] gives dist between locations i, j
    '''
    # this should probably be passed in from main which'd get it from Truck
    max_load = 16

    number_of_simulated_loads = 100
    simulated_load_package_IDs = []
    simulated_load_distances = []

    for i in range(number_of_simulated_loads):

        # if <16 items at hub, program crashes (random.sample) :< need to fix!
        eligible_pkgs = [p for p in pkgs_at_hub
                         if p.props['special_note']['truck_number'] is None or
                         p.props['special_note']['truck_number'] == truck_num]
        hypothetical_package_load = make_load_selection(eligible_pkgs,
                                                        distances,
                                                        16,
                                                        is_last,
                                                        truck_num)

        destination_numbers = get_location_nums(hypothetical_package_load)

        simulated_load_package_IDs.append(hypothetical_package_load)
        # this call should not be necessary--I'll be removing a bunch of stuff
        nn_route = nearest_neighbors_route(
            destination_numbers, distances, max_load)
        distance = nn_route[1]
        simulated_load_distances.append(distance)

    # By the way, since Python's index stops at the first occurence in a list,
    # if two routes tied on distance, the first one simulated is returned
    index_of_min_distance = simulated_load_distances.index(
        min(simulated_load_distances))

    # Pretty printing:
    pretty_pkgs = [str(pkg) for pkg
                   in simulated_load_package_IDs[index_of_min_distance]]
    pretty_pkgs = '\n'.join(pretty_pkgs)
    print(f'All IDs: {pretty_pkgs}')

    return simulated_load_package_IDs[index_of_min_distance]


def get_projected_arrival(speed_function, dist_from_prev, stop_A, location_B):
    '''Return projected arrival time for a stop on a route.'''
    avg_speed = speed_function(stop_A.location, location_B)
    minutes = 60 * (dist_from_prev / avg_speed)
    projected_arrival = Time_Custom.clone(stop_A.projected_arrival)
    projected_arrival.add_time(minutes)
    return projected_arrival


def build_route(pkg_load, distances, Locations, truck_speed, initial_leave):
    '''Return delivery route (list of stops) for a provided package-load.'''
    route = []
    destination_numbers = get_location_nums(pkg_load)

    location_num = 1

    while len(destination_numbers) > 0:
        nearest_neighbor = get_nearest_neighbor(
            location_num, destination_numbers, distances)

        location_num, distance_from_previous = nearest_neighbor

        destination_numbers.remove(location_num)

        packages_for_stop = get_stop_packages(location_num, pkg_load)

        if len(route) == 0:
            previous_stop = None
            projected_arrival = initial_leave
        else:
            previous_stop = route[-1]
            projected_arrival = get_projected_arrival(
                truck_speed, distance_from_previous,
                previous_stop, location_num)

        stop = Stop(location_num,
                    packages_for_stop,
                    distance_from_previous,
                    projected_arrival)
        route.append(stop)

    # add final stop--go back to the hub (location #1)
    distance_from_previous = distances[location_num][1]
    projected_arrival = get_projected_arrival(
        truck_speed, distance_from_previous, previous_stop, 1)
    route.append(Stop(1,
                      [],
                      distance_from_previous,
                      projected_arrival))

    return route
# per notes.txt, each item has:
# meaningful name - signature - purpose stmt


# build_route needs to...
destination_numbers = get_location_nums(pkg_load)
nearest_neighbor = get_nearest_neighbor(
    location, destination_numbers, distances)
location_num, distance_from_previous = nearest_neighbor
destination_numbers.remove(location_num)


# TEMP:
def get_nearest_neighbor2(starting_from, destination_numbers, distances):
    '''.'''
    row_index = [row[0] for row in distances].index(starting_from)
    distances_from_start = distances[row_index]

    transposed = list(zip(distances[0], distances_from_start))

    eligible_neighbors = [location_distance for location_distance in transposed
                          if location_distance[0] in destination_numbers and
                          location_distance[1] > 0]

    print(f'\ninside nn2, starting_from is {starting_from}, '
          f'destination-#s is {destination_numbers}, distances is '
          f'(NVM-TOO LONG) and eligible neighbors is: {eligible_neighbors}')
    try:
        nearest = min(eligible_neighbors, key=lambda neighbor: neighbor[1])
    except ValueError:
        nearest = None

    return nearest

# INSIDE BUILD_ROUTE:
# this call is problematic rn
# well no shit. it's two different concerns
# # of packages is not equal to # of drop-off locations
# but get_nearest_neighbor requires... oh god.
# ... I could...
# - test if pkg location is the same
# - if it is not, then call nn, up thru packages_for_stop
nearest_neighbor = get_nearest_neighbor2(
    location_num, destination_numbers, distances)
if nearest_neighbor is None:
    return

location_num, distance_from_previous = nearest_neighbor
destination_numbers.remove(location_num)

packages_for_stop = get_stop_packages(location_num, pkg_load)

# Hmm--this SHOULD throw an error, since I define stop
# but also pass it in as last param to get_stop_projected_arrival
stop = Stop(location_num,
            packages_for_stop,
            distance_from_previous,
            (initial_leave if len(route) == 0
             else get_stop_projected_arrival(
                truck_speed, distance_from_previous,
                route[-1], stop)))  # -1: prev stop

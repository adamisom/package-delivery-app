from itertools import permutations
from .time_custom import Time_Custom


class ImproveRoute_Min_ValueError(BaseException):
    pass


def update_subroute_distances(subroute, distances):
    '''Update a subroute to have correct distances.

    Receives subroute as list of tuples in which each tuple's indices are
        0 = location-number     1 = distance-from-previous  2 = package-list
    We are updating the [1] index, distance-from-previous.
    '''
    for index, stop in enumerate(subroute):
        if index == 0:
            continue
        prev, curr = subroute[index-1][0], stop[0]
        dist = distances[prev][curr]
        subroute[index] = stop[0], dist, stop[2]
    return subroute


def meets_deadlines(partial_route, distances, deadlines, speed, leave_time):
    '''Return whether a given partial-route meets all package deadlines.

    NOTE: I override speed with 18 (see below).
    The requirements for which this project built specify that the average
    speed of a truck is always 18mph, no matter what, and including stops.
    I built other parts of this program to be flexible via accommodating an
    actual speed function in the future. However, I did not deem it worth
    the effort to make this particular function flexible wrt a speed function.
    '''
    if deadlines == []:
        return True

    speed = 18

    distance_so_far = 0

    for stop in partial_route:
        distance_so_far += stop[1]  # stop[1] is distance-from-previous-stop

        # stop[0] and d[0] are both location-numbers
        if stop[0] in [d[0] for d in deadlines]:
            minutes_to_get_there = 60 * (distance_so_far / speed)
            projected_arrival = Time_Custom.clone(leave_time)
            projected_arrival.add_time(minutes_to_get_there)

            deadline, = [d[1] for d in deadlines if stop[0] == d[0]]
            if projected_arrival > deadline:
                return False

    return True


def recreate_namedtuples(route, Stop_namedtuple):
    '''Recreate namedtuples (permutations downcasts to regular tuples).'''
    return [Stop_namedtuple(*stop_tuple)
            if not isinstance(stop_tuple, Stop_namedtuple)
            else stop_tuple
            for stop_tuple in route]


def improve_route(route, distances, deadlines, speed, leave, Stop_namedtuple):
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
    segment. This means (m-n) * (n-2)! total permutations are checked,
    where m = total route length.
    * For n=7, (n-2)! = 5! = 120, which is not so bad. It's very fast to
    compute one route distance and computing 120 isn't so bad either.
    '''
    if len(route) <= 3:
        return route

    n = 7

    # Why "- n + 1?" Example: a route of size n+1 has two subroutes of size n
    for index in range(len(route) - n + 1):
        end = min(index + n - 1, len(route) - 1)  # route size can be < n

        # note that 'end' is used, not end-1, because slice-ends are exclusive
        new_orderings = list(permutations(route[index+1:end]))

        # a full subroute for distance calculation must include start and end
        subroutes = [[route[index], *ordering, route[end]]
                     for ordering in new_orderings]

        with_updated_distances = [update_subroute_distances(
                                    subroute, distances)
                                  for subroute in subroutes]

        with_none_late = [subroute for subroute in with_updated_distances
                          if meets_deadlines(route[:index] + list(subroute),
                                             distances, deadlines,
                                             speed, leave)]

        with_distance_sums = [(subroute, sum([x[1] for x in subroute]))
                              for subroute in with_none_late]

        try:
            shortest = min(with_distance_sums,
                           key=lambda candidate_route: candidate_route[1])
        except ValueError:  # probably min() was given an empty list
            raise ImproveRoute_Min_ValueError('No route exists that would '
                                              'meet all remaining deadlines.')

        route = route[:index] + list(shortest[0]) + route[end+1:]

    return recreate_namedtuples(route, Stop_namedtuple)

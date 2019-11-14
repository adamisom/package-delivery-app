from itertools import permutations


def update_subroute_distances(subroute, distances):
    '''Update a subroute to have correct distances.'''
    for index, stop in enumerate(subroute):
        if stop == subroute[-1]:
            continue
        start, end = stop[1], subroute[index+1][1]
        dist = distances[start][end]
        subroute[index] = stop[0] + (dist,) + stop[2]
    return subroute


def recreate_namedtuples(route, Stop_namedtuple):
    '''Recreate namedtuples (permutations downcasts to regular tuples).'''
    return [Stop_namedtuple(*stop_tuple)
            if not isinstance(stop_tuple, Stop_namedtuple)
            else stop_tuple
            for stop_tuple in route]


def improve_route(route, distances, Stop_namedtuple):
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
    '''
    n = 7

    # Why - n + 1? Example: a route of size n+1 has two subroutes of size n
    for index in range(len(route) - n + 1):
        end = index + n - 1
        reorder_start, reorder_end = index + 1, end - 1
        new_orderings = list(permutations(route[reorder_start:reorder_end]))
        subroutes = [[route[index]] + ordering + [route[end]]
                     for ordering in new_orderings]
        with_updated_distances = [update_subroute_distances(subroute)
                                  for subroute in subroutes]
        with_distance_sums = [(subroute, sum([x[1] for x in subroute]))
                              for subroute in with_updated_distances]
        shortest = min(with_distance_sums, key=lambda ordering: ordering[1])
        route = route[:index] + [with_distance_sums[0]] + route[end:]

    return recreate_namedtuples(route, Stop_namedtuple)

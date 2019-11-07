# per notes.txt, each item has:
# meaningful name - signature - purpose stmt

'''Four truck functions + 1 truck class var.'''
Truck.speed_function(cls, point1, point2):
    '''Return average speed between two points.'''
    return Truck.avg_speed  # Truck.avg_speed class var


def load(self):
    '''Load truck with packages.'''
    pass


def deliver(self):
    '''Deliver packages on truck.'''
    pass


def __str__(self):
    '''Return string representation of Truck object.
    TODO: clean it up a bit and make sure all props are listed.'''
    return f'Truck with ID: {self.ID}, at location {self.location}, '\
           f'time {self.time}, with these packages: \n\t{package_list}'


''' Five functions (3 truck 2 package) to update late/wrong-dest pkgs.'''


def update_late_package(self):
    '''Update a late-arriving package to indicate it is now at the hub.

    Package class.'''
    if self.props['state'] == PkgState['LATE_ARRIVAL']:
        self.set_state('AT_HUB')


def update_corrected_package(self):
    '''Update a wrong-destination package to indicate destination is now known
    i.e. it can be delivered.

    Package class.'''
    if self.props['state'] == PkgState['WRONG_DESTINATION']:
        self.set_state('AT_HUB')


def update_late_packages(self, all_packages):
    '''Update all late-arriving packages that are now at the hub.

    Truck class.
    TODO: have last_arrival_time passed in and use it.'''
    for pkg in all_packages:
        pkg.update_late_package()


def update_corrected_packages(self, all_packages):
    '''Update all packages that had a known wrong-destination at start of day
    but which have now been corrected, i.e., which can now be delivered.

    Truck class.
    TODO: have last_correction_time passed in and use it.'''
    for pkg in all_packages:
        pkg.update_corrected_package()


def discover_packages_at_hub(self, last_arrival_time, last_correction_time,
                             all_packages):
    '''Return list of packages at hub.

    Truck class.    Calls helpers to update . '''
    return [pkg for pkg in all_packages
            if pkg.props['state'].name == 'AT_HUB']


''' Algorithm module: 7 functions, 4 for load 3 for deliver, like this:
(load)
pick_load
    calls nearest_neighbor_route
        calls get_nearest_neighbor
            calls update_nn_distances

(deliver)
build_route
    calls dijkstras_route
    loops per stop, and calls build_stop
'''


def update_nn_distances(location, pkg_load_distances):
    '''Update the 2D list of distances used by nearest_neighbors_route to mark
    one location as already picked (so it isn't picked again).'''
    pass  # no return


def get_nearest_neighbor(location, pkg_load_distances):
    '''Return the location nearest to a provided location.'''
    location_num = 1  # the hub: a dummy value for now
    return location_num


def nearest_neighbors_route(pkg_load, pkg_load_distances):
    '''Return total distance traveled in a simulated route in which the route
    is built up from greedy nearest-neighbor selection.'''
    distance_traveled = 0s
    return distance_traveled


def pick_load(pkgs_at_hub, distances):
    '''Return list of package IDs that performed the best from a simulation of
    many package selections and deliveries.'''
    pkg_load = random.sample(pkgs_at_hub, 16)  # if <16 at hub, program crashes
    return


def dijkstras_route(pkg_load, distances):
    ''''Return an optimal delivery route (a simple ordered list of package IDs_
    using Dijkstra's algorithm.'''
    route_order = []
    return route_order


def build_stop(location, distances):
    '''Return a Stop on a route.

    A Stop has these attributes:
        -
        -
        -
        -
    '''
    stop = []
    return stop


def build_route(pkg_load, distances):
    '''Return delivery route (list of stops) for a provided package-load.'''
    route = []
    return route

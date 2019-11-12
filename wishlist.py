# per notes.txt, each item has:
# meaningful name - signature - purpose stmt


def is_package_on_time(package):
    '''Return whether the given package was delivered on time.'''
    if not package.props['deadline']:
        return True  # if a package had no deadline, it was 'on time'

    for record in package.props['history']:
        if (record.state == 'DELIVERED' and
                record.time <= package.props['deadline']):
            return True

    # A package was not on time if it failed the loop above, meaning
    # either (1) it was never delivered, or (2) it missed its deadline
    return False


def display_on_time_delivery_rate(packages):
    '''Calculate and display the number (it should be all of them) of packages
    that were delivered on time.'''
    on_time_count = 0
    for pkg in packages:
        if is_package_on_time(pkg):
            on_time_count += 1

    print(f'\n{on_time_count} out of {len(packages)} packages'
          'were delivered on time.')


# IN MAIN, right after getting route, write route_distance = compute..(route)
# IN MAIN, make a new total_dist var and increment this in for truck/trucks
# TRUCK CLASS
def get_mileage_for_one_route(self, route_distance):
    '''Calculate and return total distance traveled for one route (from hub,
    back to hub).

    This function currently just returns the route-distance passed in, but it
    could be easily extended in the future to account for "real life",
    for example if a truck was forced to take a detour.
    '''
    return route_distance


def display_distance_traveled(total_distance):
    '''Display distance (in miles) traveled to deliver all packages.'''
    print(f'Total travel distance was: {total_distance} miles.')


'''Now, I'm envisioning deadlines + truck-num as happening BEFORE
the random selection, and the random selection in the loop ONLY being
on what is left.

    For deadline, here's what I could do:
truck - add prop is_last_leaving_hub which defaults to False
algos - pass is_last to pick_load (main)->alter_load->pick_to_meet_deadlines
main - create num_trucks arg to run_program--and num_drivers while I'm at it,
pass into the if __main__ run_program call, then iterate and create a Trucks
array but create initial # of trucks limited by num_drivers (not num_trucks)
THEN enumerate the for truck in trucks call, and if truck is last one,
set its truck property but also make an is_last var and pass to pick_load.
THE END.

and for truck-num, I similarly have to pass a variable "truck_num":
from run_program->pick_load->alter_load->satisfy_truck_num_constraints
THE END.

Oh! Oh! I have to make sure the random choice in pick_load EXCLUDES
any packages that have a truck number other than current truck number!
I definitely don't want to do a 'subtraction', that's ugly I'd rather
just filter the list of packages being randomly sampled to exclude some...
'''


def pick_to_satisfy_truck_constraints(pkgs_at_hub, truck_num):
    '''Return list of packages that need to go on the given truck-number.'''
    return [pkg for pkg in pkgs_at_hub
            if pkg.props['special_note']['truck_number'] == truck_num]


# WAIT! I think I will not pass is_last_truck in, and instead
# I will conditionally call THIS function IF is_last_truck, WITHIN pick_load
def pick_to_meet_deadlines(pkgs_at_hub, is_last_truck):
    '''Return list of packages with a deadline before noon that are still at
    the hub (not loaded) if this truck is the last one to leave.

    Assumptions (two):
    - This function assumes that if a deadline is after 12:00 noon there will
    be plenty of time to deliver it on a truck's second run.
    - It also assumes all trucks initially leave the hub at 8:00am.
    '''
    if not is_last_truck:
        return []
    # else this is the last truck leaving in the morning!
    return [pkg for pkg in pkgs_at_hub
            if pkg.props['deadline'] and
            pkg.props['deadline'] < Time_Custom(12, 00, 00)]


def pick_same_destination_packages(pkg_load, pkgs_at_hub):
    '''Return list of packages going to the same destinations as any package
    in the current package-load, so long as those packages do not have any
    special-note constraints of their own.

    Note that the list returned does include packages already in pkg_load,
    namely those which are going to destinations that other packages are also
    going to. It is necessary to include those packages in this return list
    as well as new ones from pkgs_at_hub, so that they do not get removed
    when augment_load calls reduce_load. (It wouldn't make much sense to look
    at pkg_load, see package #5 is going to location #2, say, 'hey, package
    #27 is also going there', and add package #27, only for package #5 to be
    removed from pkg_load later.)'''
    set_of_location_nums = get_location_nums(pkg_load)
    # set([pkg.props['location'].num for pkg in pkgs])

    return [pkg for pkg in pkgs_at_hub
            if pkg.props['location'].num in set_of_location_nums]


def pick_to_satisfy_deliver_constraints(pkg_load, pkgs_at_hub):
    '''Return list of packages that must be delivered simultaneously with any
    packages currently in pkg_load, and in that list, include...

    Note that the list returned does include packages already in pkg_load,
    namely those with a deliver-with constraint. It is necessary to include
    the deliver-with's already in pkg_load so that they don't get removed
    later. The same thing applies in pick_same_destination_packages.
    '''
    deliver_with_in_pkg_load = [pkg for pkg in pkg_load
                                if pkg.props['special_note']['deliver_with']]
    deliver_with_in_all = []
    # Note the distinction between pkg which is from deliver_with_in_pkg_load,
    # and any_pkg which is from pkgs_at_hub
    for pkg in deliver_with_in_pkg_load:
        deliver_with_in_all += [any_pkg for any_pkg in pkgs_at_hub
                                if any_pkg.props['ID']
                                in pkg.props['special_note']['deliver_with']]

    return list(set(deliver_with_in_all))


def reduce_load(pkg_load, leave_alone, max_load=16):
    '''Return a smaller list of packages that have some randomly subtracted,
    where leave_alone indicates which packages should not be subtracted.

    This function assumes max load is 16 packages if no value is passed in.

    This function also assumes leave_alone is not larger than pkg_load minus
    leave_alone (which is eligible_for_removal). If this is not true, then
    all of leave_alone is removed instead.
    If this situation happened in production--more than rarely--then packages
    are more constrained / interrelated than the sample data seemed to
    suggest. And in that case, the whole approach to selecting a package-load
    should probably be updated.
    '''
    number_to_remove = len(pkg_load) - max_load
    eligible_for_removal = list(set(pkg_load) - set(leave_alone))

    if number_to_remove > eligible_for_removal:
        return list(set(pkg_load) - set(leave_alone))

    remove_these = random.sample(eligible_for_removal, number_to_remove)
    return list(set(pkg_load) - set(remove_these))


def augment_load(pkg_load, ackages, is_last_truck, truck_num):
    '''Return augmented package load that takes into account deliver-with
    constraints and packages with the same destinations.
    '''
    augmented = pkg_load

    deliver_with = pick_to_satisfy_deliver_constraints(augmented, packages)
    augmented = reduce_load(augmented + deliver_with, deliver_with)

    same_dest = pick_same_destination_packages(augmented, packages)
    augmented = reduce_load(augmented + same_dest, same_dest)

    return augmented

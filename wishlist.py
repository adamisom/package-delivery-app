# per notes.txt, each item has:
# meaningful name - signature - purpose stmt

def display_on_time_delivery_rate(packages):
    '''Calculate and display the number (it should be all of them) of packages
    that were delivered on time.'''
    on_time_count = 0
    for pkg in packages:
        pass
        # immediately increment on_time_count if package had no deadline
        # if deadline
            # iterate history (does package have a helper?)
                # find time when delivered
                # if delivered on or before deadline, increment on_time..
                # else do not!
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


'''Now I'm envisioning deadlines + truck-num as happening BEFORE
the random selection, and the random selection in the loop ONLY being
on what is left.

Then, deliver-with and same-destination will be augments, but it's
slightly tricky because when the pkg-load sheds packags to make up for it,
it has to know both about what was added by those two functions as well as
the 'buddy' packages for which both those functions returned more on behalf
of--wouldn't do much good to get another package going to location 2, if the
shed phase then got rid of that first 'locatio 2' package...
'''
''' for deadline, here's what I could do:
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

def pick_to_satisfy_truck_constraints(pkg_load, all_packages, truck_num):
    '''Return list of packages that need to go on the given truck-number.'''
    truck_num_packages = []
    return truck_num_packages


def pick_to_meet_deadlines(all_packages, is_last_truck):
    '''Return list of packages with a deadline before noon that are still at
    the hub (not loaded) if this truck is the last one to leave.

    Assumptions(2):
    - This function assumes that if a deadline is after 12:00 noon there will
    be plenty of time to deliver it on a truck's second run.
    - It also assumes all trucks initially leave the hub at 8:00am.
    '''
    deadline_packages = []
    return deadline_packages


def pick_to_satisfy_deliver_constraints(pkg_load, all_packages):
    '''Return list of packages that must be delivered simultaneously with any
    packages currently in pkg_load, and in that list, include...
    '''
    deliver_with_packages = []
    return deliver_with_packages


def pick_same_destination_packages(pkg_load, all_packages):
    '''Return list of packages going to the same destinations as any package
    in the current package-load, so long as those packages do not have any
    special-note constraints of their own.

    This pick_ function's return list does include ...'''
    same_destination_packages = []
    # only include same-destination packages that do not have constraints

    return same_destination_packages


# THESE SHOULD BE DONE:
def reduce_load(pkg_load, leave_alone):
    '''Return a smaller list of packages that have some randomly subtracted.

    This is to compensate for the functions pick_to_satisfy_deliver_constraints
    and pick_same_destination_packages, which add packages.

    leave_alone should be a sublist of pkg_load and indicates which packages
    should not be removed from pkg_load.

    This function assumes leave_alone is not larger than pkg_load.
    '''
    remove_these = random.sample(list(set(pkg_load) - set(leave_alone)))
    return list(set(pkg_load) - set(remove_these))


def augment_load(pkg_load, ackages, is_last_truck, truck_num):
    '''Return augmented package load that takes into account deliver-with
    constraints and packages with the same destinations.
    '''
    augmented = pkg_load

    deliver_with = pick_to_satisfy_deliver_constraints(augmented, packages)
    augmented += deliver_with
    pkg_load = reduce_load(augmented, deliver_with)

    same_dest = pick_same_destination_packages(augmented, packages)
    augmented += same_dest
    augmented = reduce_load(augmented, same_dest)

    return augmented

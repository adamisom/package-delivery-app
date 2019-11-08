import re
from collections import namedtuple
from .classes.time_custom import Time_Custom
from .classes.package import Package


def say_hello():
    '''Say hello when the program starts.'''
    print('Hello!\nThis application simulates package delivery via truck.\n')


def give_user_snapshot_instructions():
    '''Advise the user to enter a time for a snapshot.'''
    print('If you\'d like to see the status of each package at a given time, '
          'please enter the time on the next line.\nMake sure to enter a '
          '\'military\' time, for example 14:00 for 2:00pm. Seconds are '
          'optional, but make sure to use two digits for the hour.\n'
          'Examples: 08:35, 10:00, 12:01:30 (this would be just after noon)')


def validate_length(time_string):
    '''Validate that the user-requested time-string is a correct length.'''
    return len(time_string.strip()) == 5 or len(time_string.strip()) == 7


def get_time_parts_from_string(time_string):
    '''Extract and return hh, mm, ss from a string of form hh:mm or hh:mm:ss.

    hh refers to two-digit hour, mm : two-digit minute, ss : two-digit second
    '''
    hour = int(time_string[0:2])
    minute = int(time_string[3:5])
    second = (int(time_string[6:8])
              if len(time_string.strip()) == 7
              else 0)
    return hour, minute, second


def validate_values(time_parts):
    '''Validate user-provided time for snapshot has a valid number of hours,
    minutes and seconds.'''
    hour, minute, second = time_parts
    return (hour >= 0 and hour < 24 and
            minute >= 0 and minute < 60 and
            second >= 0 and second < 60)


def handle_snapshot_request(packages):
    '''Listen for user input and generate snapshot when input is valid.

    TODO: Rename this. Also rename the get_destin... function name.
    '''
    give_user_snapshot_instructions()

    user_requested_time = input('Whenever you\'re ready...  ')
    while not validate_length(user_requested_time):
        print('\nPlease try again. Please enter two-digit hour, colon, '
              'two-digit minute.')
        user_requested_time = input('Whenever you\'re ready...  ')

    time_parts = get_time_parts_from_string(user_requested_time)
    while not validate_values(time_parts):
        print('\nPlease try again. Please enter an hour from 0 to 23, minute '
              'from 0 to 59, and second (if entered) also from 0 to 59.')
        user_requested_time = input('Whenever you\'re ready...  ')

    print(f'Alright! You asked for a snapshot at time {user_requested_time}')
    make_snapshot(Time_Custom(*time_parts), packages)


def package_status_at_time(package, time_custom):
    '''Return the status of a package at a given time.'''
    # if time_custom is before 7:59am, use the initial state
    if time_custom < Time_Custom(7, 59, 00):
        return package.props['history'][0].state
    if len(package.props['history']) == 1:
        return package.props['history'][0].state
    for index, record in enumerate(package.props['history']):
        if record.time > time_custom:
            # go back one record
            return package.props['history'][index - 1].state


def package_snapshot(package, time_custom):
    '''Display historical status of a given package at a given time.'''
    package_str = str(package)
    # remove current delivery state of package
    cut_start = package_str.index('delivery status')
    cut_end = package_str.index('destination')
    print(package_str[0:cut_start] + package_str[cut_end:])

    status = package_status_at_time(package, time_custom).name
    print(f'\tFinally, delivery status at {time_custom} was {status}')


def make_snapshot(time_custom, packages):
    '''Display historical status of each/every package at a provided time.

    Called in/by: main.py ~55
    '''
    print(f'\nSNAPSHOT OF ALL PACKAGES AT {str(time_custom)}:')
    for package in packages:
        package_snapshot(package, time_custom)


def get_destination_corrections_from_user(Locations):
    '''Purpose of function goes here.

    Data definition:
    A Destination_Correction is a namedtuple of
        id:         Package ID
        time:       Time by which we will know the correct destination
        location:   Location* of the correct destination

    *Location is itself a namedtuple of num, landmark, address (see load.py).

    Notes on destination corrections:
        Purpose: Separating 'when it will be known' from the destination itself
    lets us handle when a sender initially gave us the wrong address (and tells
    us so), but when they need some time to find out the right address or
    otherwise get it to us. It also lets us handle when we know we got it
    wrong but know that we'll have the right information later.

        Usage: the list of destination corrections returned by this function is
    intended to be checked by truck drivers at the hub. If the time listed for
    a correction has passed, the truck is responsible for updating the package.
    If the location property of a correction is still None, despite the time
    being past the time-of-correction, the package will not be updated.
    '''
    Destination_Corrections = []

    Destination_Correction = namedtuple('Destination_Correction',
                                        ['id', 'time', 'location'])

    return Destination_Corrections

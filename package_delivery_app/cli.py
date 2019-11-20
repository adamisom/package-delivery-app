import re
from os import path
from collections import namedtuple
from .classes.time_custom import Time_Custom
from .classes.package import Package


def say_hello():
    '''Say hello when the program starts and advise the user they will be asked
    what information, if any, they would like displayed.'''
    print('Hello!\nThis application simulates package delivery via truck.')
    print('\nPlease note: A "route" is a single trip, starting at the hub\n'
          'and ending at the hub; multiple delivery routes may be needed\n'
          'to deliver all your packages.\n')
    print('This program is about to ask you a few things, in this order:\n'
          '\twhether you have any destination-correction information to enter,'
          '\n\twhether you want to display each route\'s path (with packages),'
          '\n\twhether you would like to get a snapshot at the end, showing'
          '\n\tthe delivery status of each package at some time that you '
          'provide,\n\tand finally, whether you want see the history '
          'of each package at the very end.\n')


def ask_if_route_display_wanted():
    '''Return whether user wants to view each route and its stops.'''
    user_says = input('Would you like to see each route that is calculated?\n')
    return user_says.lower().strip() in ('y', 'yes')


def ask_if_snapshot_wanted():
    '''Return whether user wants a snapshot.'''
    says = input('Would you like to generate a snapshot at the end?\n'
                 'If so, then once the routes are calculated (and '
                 'displayed, if you wanted that),\nyou\'ll be '
                 'asked to provide a time for the snapshot.\nThat snapshot '
                 'will appear in the console here, and will also be stored '
                 'in\na new file "package_snapshot.txt" in the directory '
                 'you are running this from.\nIf you would '
                 'like a snapshot later, press "y" or "yes", then Enter.\n'
                 'Otherwise, press any other key, like Enter or "n".\n')
    return says.lower().strip() in ('y', 'yes')


def ask_if_package_histories_wanted():
    '''Return whether user wants to view all package histories.'''
    user_says = input('Would you like to see all packages and their histories '
                      'at the end?\n(This will appear after a snapshot, if '
                      'you asked for one.)\n')
    return user_says.lower().strip() in ('y', 'yes')


def give_user_snapshot_instructions():
    '''Advise the user to enter a time for a snapshot.'''
    print('\nAlright, time for that snapshot you asked about.\n'
          'Please enter the time on the next line.\nMake sure to enter a '
          '\'military\' time, for example 14:00 for 2:00pm.\nSeconds are '
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
    '''Listen for user input and generate snapshot when input is valid.'''
    give_user_snapshot_instructions()

    user_requested_time = input('Whenever you\'re ready, enter a time\n')
    while not validate_length(user_requested_time):
        print('\nPlease try again. Please enter two-digit hour, colon, '
              'two-digit minute.')
        user_requested_time = input('Whenever you\'re ready...  ')

    time_parts = get_time_parts_from_string(user_requested_time)
    while not validate_values(time_parts):
        print('\nPlease try again. Please enter an hour from 0 to 23, minute '
              'from 0 to 59, and second (if entered) also from 0 to 59.')
        user_requested_time = input('Whenever you\'re ready, enter a time\n')

    print(f'Alright! You asked for a snapshot at time {user_requested_time}')
    make_snapshot(Time_Custom(*time_parts), packages)

    print('*' * 79, '\n')


def package_status_at_time(package, time_custom):
    '''Return the status of a package at a given time.'''
    # if time_custom is before 7:59am, use the initial state
    if time_custom < Time_Custom(7, 59, 00):
        return package.props['history'][0].state
    if len(package.props['history']) == 1:
        return package.props['history'][0].state
    # case: package had at least one History_Record after time_custom
    for index, record in enumerate(package.props['history']):
        if record.time > time_custom:
            # go back one record
            return package.props['history'][index - 1].state
    # case: package no History_Records after time_custom
    return package.props['history'][-1].state


def package_snapshot_file(package, time_custom):
    '''Write historical status of given package at given time to text file.'''
    filename = 'package_snapshot.txt'
    append_or_write = 'a' if path.exists(filename) else 'w'
    with open(filename, append_or_write) as f:
        package_str = str(package)

        # do not include current delivery-state of package in snapshot string
        cut_start = package_str.index('delivery status')
        cut_end = package_str.index('destination')
        print(package_str[0:cut_start] + package_str[cut_end:], file=f)

        status = package_status_at_time(package, time_custom).name
        print(f'\tFinally, delivery status at {time_custom} was {status}',
              file=f)


def package_snapshot(package, time_custom):
    '''Display historical status of a given package at a given time.'''
    package_str = str(package)

    # do not include current delivery-state of package in snapshot string
    cut_start = package_str.index('delivery status')
    cut_end = package_str.index('destination')
    print(package_str[0:cut_start] + package_str[cut_end:])

    status = package_status_at_time(package, time_custom).name
    print(f'\tFinally, delivery status at {time_custom} was {status}')


def make_snapshot(time_custom, packages):
    '''Display historical status of each/every package at a provided time.'''
    print(f'\nSNAPSHOT OF ALL PACKAGES AT {str(time_custom)}:')
    for package in packages:
        package_snapshot(package, time_custom)
        package_snapshot_file(package, time_custom)


def ask_user_if_they_have_correction_information():
    '''Ask user if they have destination-correction information.'''
    print('If you have any destination-corrections for packages, you are in '
          'the right place.\nIf you don\'t have any corrections, no problem--'
          'just type "q" or "quit" and hit Enter.\nIf you do have information,'
          ' type any other key--like the Enter key.\n'
          'Just keep in mind that if your distance file indicates that any '
          'packages\nare known to have the wrong destination, but you do not '
          'supply a correction,\nthose packages will not get delivered. '
          'Remember--to exit this optional step, \njust press "q" or "quit", '
          ' then Enter, to skip it.')
    ask_user = input('')
    return ask_user.lower().strip() not in ('q', 'quit')


def give_user_correction_instructions():
    '''Give the user instructions for supplying valid destination-correction
    information.'''
    print('\tIf you just want to update a package\'s destination '
          'right away,\nfirst type the package ID, then comma and '
          'space, then either the landmark\nor street address.'
          '\n\tIf you are entering information about a destination '
          'correction that\nwill be known later, enter it in this '
          'format: first the package ID, and then\nthe time by which '
          'the true destination will be known.'
          '\n\tIf you are updating an existing correction item, '
          'enter it in this \nformat: first the package ID, and then '
          'either the landmark or the street\naddress (yes, this is '
          'the same as in the first case).'
          '\n\n\tHere are some examples of input that will be accepted:'
          '\n3, 09:30\t\t<= this says that package with ID 3 has the wrong '
          '\n\t\t\tdestination location, but it will be corrected'
          '\n\t\t\tby 9:30am today'
          '\n5, 13:30\t\t<= similarly, this says package 5 will'
          '\n\t\t\thave the correct destination by 1:30pm today'
          '\n6, Sugar House Park\t<= this says that package ID 6 needs to go '
          'to\n\t\t\tSugar House Park instead of whatever the previous '
          '\n\t\t\tdestination was'
          '\n\n\tA couple of things worth keeping in mind:'
          '\n1. If you enter a time, it must be in this format'
          '\n\th:mm or hh:mm\n\tExamples: 3:55, 12:30, 14:00'
          '\n2. If you enter a time, it must be "military time".'
          '\n3. That means "AM" and "PM" are ignored.'
          '\n4. If you enter a location, then whether that is a '
          'landmark or street address, it must match exactly what '
          'the package csv file had for that package. The exception is '
          'that the (five-digit) zip code is optional.\n')


def validate_user_correction_information(input_string, Locations):
    '''Validate user-supplied destination-correction information.

    Note the -6: This lops off the 5 zip digits plus the preceding space.
    '''
    user_input = input_string.split(',')
    if len(user_input) != 2:
        return False

    package_id, time_or_location = user_input
    package_id = package_id.strip()
    time_or_location = time_or_location.strip()

    digit_regex = re.search("(\d{1,2}):(\d{2})", time_or_location)

    landmarks = [loc.landmark for loc in Locations]
    street_addresses = [loc.address for loc in Locations]
    street_addresses_no_zip = [loc.address[:-6] for loc in Locations]

    return (user_input[0].isdigit() and   # first part an integer
            (digit_regex or               # second part a time
             time_or_location in landmarks or     # or second part a location
             time_or_location in street_addresses or
             time_or_location in street_addresses_no_zip))


def get_valid_correction_item_or_quit(Locations):
    '''Get valid destination-correction information from user.'''
    prompt = ('\nPlease enter the destination-correction information '
              'on the next line, then hit the Enter key:\n')
    sorry = ('\nSorry, that doesn\'t look like valid correction information '
             'to me.\nIf you don\'t want to enter information after all, '
             'type "q" or "quit" to exit.\nOtherwise, please try again.')

    user_input = input(prompt)
    while not validate_user_correction_information(user_input, Locations):
        print(sorry)
        user_input = input(prompt)
        if user_input.lower().strip() in ('q', 'quit', 'quit()'):
            return 'quit'

    return user_input


def get_valid_package_id_from_string(package_id_string):
    '''Validate and return package ID from string.

    This function assumes that the company's package ID numbers
    will always be less than 1000. This assumption is shared by a
    Package class method (validate_package_ID_list method).
    '''
    ID = int(package_id_string.strip())

    if not ID > 0:
        raise ValueError('Package ID found in special note too small')
    if not ID < 1000:
        raise ValueError('Package ID found in special note too large')

    return ID


def get_time_or_location_from_string(time_or_location, Locations):
    '''Extract the time or the location supplied by user for a correction;
    if user supplies both (unexpected), only the address is extracted.

    Note the -6: This lops off the 5 zip digits plus the preceding space.
    '''
    time_or_location = time_or_location.strip()

    landmarks = [loc.landmark for loc in Locations]
    if time_or_location in landmarks:
        index_of_match = landmarks.index(time_or_location)
        # this trick works because list comprehensions retain order
        return Locations[index_of_match]

    street_addresses = [loc.address for loc in Locations]
    if time_or_location in street_addresses:
        index_of_match = street_addresses.index(time_or_location)
        # this trick works because list comprehensions retain order
        return Locations[index_of_match]

    street_addresses_no_zip = [loc.address[:-6] for loc in Locations]
    if time_or_location in street_addresses_no_zip:
        index_of_match = street_addresses_no_zip.index(time_or_location)
        # this trick works because list comprehensions retain order
        return Locations[index_of_match]

    digit_regex = re.search("(\d{1,2}):(\d{2})", time_or_location)
    if digit_regex:
        hour, minute = digit_regex.groups()
        hour, minute = int(hour), int(minute)
        return Time_Custom(hour, minute, 0)


def get_one_destination_correction(Locations):
    '''Get one destination-correction from user.'''
    item_or_quit = get_valid_correction_item_or_quit(Locations)
    if item_or_quit == 'quit':
        return 'quit'

    correction_item_list = [None] * 3

    user_input = item_or_quit.split(',')

    package_id = get_valid_package_id_from_string(user_input[0])
    correction_item_list[0] = package_id

    time_or_location = get_time_or_location_from_string(
        user_input[1], Locations)
    if isinstance(time_or_location, Time_Custom):
        correction_item_list[1] = time_or_location  # time
    else:
        correction_item_list[2] = time_or_location  # location

    return correction_item_list


def get_destination_corrections(Locations):
    '''Get one or more destination-corrections from user; calls many helpers.

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
                                        ['pkg_id', 'time', 'location'])

    user_has_information = ask_user_if_they_have_correction_information()

    if not user_has_information:
        return Destination_Corrections

    give_user_correction_instructions()

    while user_has_information:
        item_or_quit = get_one_destination_correction(Locations)

        if item_or_quit == 'quit':
            break
        else:
            match = [c for c in Destination_Corrections
                     if item_or_quit[0] == c.pkg_id]
            # merge or overwrite existing correction for that package if exists
            if len(match) > 0:
                match = match[0]
                index = Destination_Corrections.index(match)
                updated = (match.pkg_id,
                           (item_or_quit[1] or match.time),
                           (item_or_quit[2] or match.location))
                Destination_Corrections[index] = (
                  Destination_Correction(*updated))
            else:  # add new correction
                Destination_Corrections.append(
                  Destination_Correction(*item_or_quit))

        ask_for_more = input('\nWould you like to add another? Type "y" '
                             'or "yes" if so.\nOtherwise, hit Enter.\n')
        user_has_information = ask_for_more.lower().strip() in ('y', 'yes')

    print('*' * 79, '\n')

    return Destination_Corrections

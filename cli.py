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


def ask_user_if_they_have_correction_information():
    '''FILL ME IN.'''
    print('If you know of a package with the wrong destination, you are in '
          'the right place. If you don\'t have this information right now, '
          'no problem--just type "q" or "quit" and hit Enter.\nIf you do, '
          'have information, type any other key--like the Enter key.')
    ask_user = input('')
    return ask_user.lower().strip() not in ('q', 'quit')


def give_user_correction_instructions():
    '''FILL ME IN.'''
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
          'the package csv file had for that package.\n')


def validate_user_correction_information(input_string, Locations):
    user_input = input_string.split(',')
    if len(user_input) != 2:
        return False

    package_id, time_or_location = user_input
    package_id = package_id.strip()
    time_or_location = time_or_location.strip()

    one_digit_hour = re.search('\d{1}:\d{2}', time_or_location, re.IGNORECASE)
    two_digit_hour = re.search('\d{2}:\d{2}', time_or_location, re.IGNORECASE)

    landmarks = [loc.landmark for loc in Locations]
    street_addresses = [loc.address for loc in Locations]

    return (user_input[0].isdigit() and   # first part an integer
            (one_digit_hour or two_digit_hour or  # second part a time
             time_or_location in landmarks or     # or a location
             time_or_location in street_adresses))


def get_valid_correction_item_or_quit(Locations):
    '''.'''
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


def get_package_id_from_string(package_id_string):
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
    '''.'''
    time_or_location = time_or_location.strip()
    one_digit_hour = re.search('\d{1}:\d{2}', time_or_location, re.IGNORECASE)
    two_digit_hour = re.search('\d{2}:\d{2}', time_or_location, re.IGNORECASE)

    if one_digit_hour or two_digit_hour:
        if one_digit_hour:
            hour = int(one_digit_hour.group(0)[0:1])
            minute = int(one_digit_hour.group(0)[2:4])
            return Time_Custom(hour, minute, 0)
        elif two_digit_hour:
            hour = int(two_digit_hour.group(0)[0:2])
            minute = int(two_digit_hour.group(0)[3:5])
            return Time_Custom(hour, minute, 0)

    landmarks = [loc.landmark for loc in Locations]
    if time_or_location in landmarks:
        index_of_match = landmarks.index(time_or_location)
        # this trick works because list comprehensions retain order
        return Locations[index_of_match]

    street_addresses = [loc.address for loc in Locations]
    if time_or_location in street_adresses:
        index_of_match = street_addresses.index(time_or_location)
        # this trick works because list comprehensions retain order
        return Locations[index_of_match]


def get_one_destination_correction(Locations):
    '''FILL ME IN.'''
    item_or_quit = get_valid_correction_item_or_quit(Locations)
    if item_or_quit == 'quit':
        return 'quit'

    correction_item_list = [None] * 3

    user_input = input_string.split(',')
    package_id = get_package_id_from_string(package_id_string)
    orrection_item_list[0] = package_id
    time_or_location = get_time_or_location_from_string(
        time_or_location, Locations)
    if isinstance(time_or_location, Time_Custom):
        correction_item_list[1] = time_or_location  # time
    else:
        correction_item_list[2] = time_or_location  # location

    return correction_item_list


def get_destination_corrections_from_user(Locations):
    '''FILL ME IN.

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

    # NOTE the below line is a manual add (I am not a fan!)
    Destination_Corrections.append(
        Destination_Correction(9, Time_Custom(10, 20, 00), None))

    # temporary return
    return Destination_Corrections

    user_has_information = ask_user_if_they_have_correction_information()
    if not user_has_information:
        return Destination_Corrections

    give_user_correction_instructions()

    while user_has_information:
        # THE LINE BELOW IS WHERE I NEED MORE WORK
        parsed_input = get_one_destination_correction(Locations)
        print(f'\nparsed input: {parsed_input}\n')

        if parsed_input == 'quit':
            return Destination_Corrections

        ask_for_more = input('Would you like to add another correction? Type '
                             '"y" or "yes" if so.\nOtherwise, hit Enter.\n')
        user_has_information = ask_for_more.lower().strip() in ('y', 'yes')

    return Destination_Corrections

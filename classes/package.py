import re
from enum import Enum
from .time_custom import *


class PkgState(Enum):
    '''Enumerate possible package states.'''
    AT_HUB = 1
    IN_TRANSIT = 2
    DELIVERED = 3
    LATE_ARRIVAL = 4
    WRONG_DESTINATION = 5


class Package():
    id_counter = 1

    def __init__(self, d, w, sn, location):
        '''Create Package object.

        Called in/by: load.py ~191
        Things it should do (remember, one function per task):
            add all passed-in properties
                notably including location(in place of address+city+state+zip)
            parse special note and then set initial status
            add state property
            add history property

        Data definitions:
        Special note: a property of a package that itself has four properties:
            - truck_number
            - deliver_with
            - late_arrival
            - wrong_destination
        The first two of these sub-properties are used to set initial state.

        Location: a namedtuple of location-number, landmark, street address.
        '''
        self.ID = Package.id_counter
        Package.id_counter += 1

        self.deadline = d
        self.weight = w
        self.location = location

        self.special_note = sn
        self.mark_package_special(self.parse_special_note(sn))
        self.state = None
        self.set_initial_state()

        self.history = [(self.state, Time_Custom(8, 00, 00))]

    def set_state(self, state_string):
        '''Update state of a package.'''
        self.state = PkgState(PkgState[state_string])

    def set_initial_state(self):
        '''Set initial state of package to hub, late, or wrong-destination.'''
        if self.special_note['late_arrival']:
            self.set_state('LATE_ARRIVAL')
        elif self.special_note['wrong_destination']:
            self.set_state('WRONG_DESTINATION')
        else:
            self.set_state('AT_HUB')

    def parse_special_note(self, special_note):
        '''Parse the special note (if any) attached to a package.

        The meaning of a special note is determined by its match to one of the
        following (caps-insensitive) patterns:
            1. 'only', followed by 'truck', followed by an integer
                If matched, ...
            2. 'delivered with', followed by an integer or comma-separated
            list of integers
                If matched, ...
            3. 'delayed', followed by a time of the form 'h:mm (am|pm)'
            or 'hh:mm (am|pm)'
                If matched, ...
            4. 'wrong address'
                If matched, ...
        Assumption: only one pattern will be matched for any given package.
        If more than one did match, the constraint actually assigned to
        the package is dictated by the order in which they are checked.
        '''
        truck_number_constraint = truck_regex_match(special_note)
        co_delivery_constraint = delivery_regex_match(special_note)
        late_arrival_constraint = arrival_regex_match(special_note)
        wrong_destination_constraint = destination_regex_match(special_note)

        if truck_number_constraint:
            truck = get_truck_number(special_note)
            return dict(truck_number=truck)
        if co_delivery_constraint:
            package_list = get_packages_to_deliver_with(special_note)
            return dict(deliver_with=package_list)
        if late_arrival_constraint:
            when = Time_Custom(*get_arrival_time(special_note))
            return dict(late_arrival=when)
        if wrong_destination_constraint:
            return dict(wrong_destination=True)

        assert (special_note == '')
        return None

    def mark_package_special(self, parsed_note):
        '''Update package props based off result of parsing special_note.

        Sets four new properties on self.special_note, initialized to None,
        then updates the zero or one properties passed in as parsed_note.
        '''
        self.special_note = dict.fromkeys(['truck_number', 'deliver_with',
                                          'late_arrival', 'wrong_destination'])
        if isinstance(parsed_note, dict):
            self.special_note.update(parsed_note)
        # # a simple test:
        # if parsed_note is not None:
        #     print("package special note is now: ", self.special_note)


'''
    The following regex functions are not part of the Package class because
    they do not need to be--they neither consume nor produce Package objects.
'''


def truck_regex_match(note):
    '''Return regex match for a truck-number constraint in a special note.'''
    return re.search("(only)(.*?)(truck) \d", note, re.IGNORECASE)


def delivery_regex_match(note):
    '''Return regex match for a delivery constraint in a special note.'''
    return re.search("(delivered with \d+[, \d+]*)", note, re.IGNORECASE)


def arrival_regex_match(note):
    '''Return regex match for a late-arrival constraint in a special note.'''
    return re.search("(delayed)(.*?)\d\d?:\d\d (am|pm)", note, re.IGNORECASE)


def destination_regex_match(note):
    '''Return regex match for wrong-destination constraint in special note.'''
    return re.search("wrong address", note, re.IGNORECASE)


def get_truck_number(note):
    '''Parse and return truck number from a package special note.'''
    integers_found = [int(num) for num in filter(str.isdigit, note)]
    assert(validate_truck_number(integers_found))
    truck_num = integers_found[0]
    return truck_num


def get_packages_to_deliver_with(note):
    '''Parse and return list of package IDs from a package special note.'''
    index_of_first_integer = re.search("\d", note, re.IGNORECASE).start()
    substring = note[index_of_first_integer:]
    integers_found = [int(num) for num in substring.split(', ')]
    if len(integers_found) == 0:  # try split by ',' instead of ', '
        integers_found = [int(num) for num in substring.split(',')]

    assert(validate_package_ID_list(integers_found))

    package_IDs = integers_found
    return package_IDs


def get_arrival_time(note):
    '''Parse and return late-arrival time from a package special note.'''
    one_digit_hour = re.search("\d{1}:\d{2} (am|pm)", note, re.IGNORECASE)
    two_digit_hour = re.search("\d{2}:\d{2} (am|pm)", note, re.IGNORECASE)

    assert(one_digit_hour or two_digit_hour)

    if one_digit_hour:
        hour = int(one_digit_hour.group(0)[0:1])
        minute = int(one_digit_hour.group(0)[2:4])
        am_pm = one_digit_hour.group(0)[5:7]
    elif two_digit_hour:
        hour = int(two_digit_hour.group(0)[0:2])
        minute = int(two_digit_hour.group(0)[3:5])
        am_pm = two_digit_hour.group(0)[6:8]

    assert(validate_arrival_time(hour, minute, am_pm))

    if am_pm == 'pm':
        hour += 12

    arriving_at_tuple = (hour, minute, 0)
    return arriving_at_tuple


def validate_truck_number(integers_found):
    '''Validate truck number found in package special note.

    This function assumes that the company's truck-number labels
    will always be less than 50.
    '''
    return len(integers_found) == 1 and integers_found[0] < 100


def validate_package_ID_list(integers_found):
    '''Validate co-delivery package IDs found in package special note.

    This function assumes that the company's package ID numbers
    will always be less than 1000.
    '''
    return all([i > 0 and i < 1000 for i in integers_found])


def validate_arrival_time(hour, minute, am_pm):
    '''Validate late-arrival time found in package special note.

    This function assumes the note will not have a military time.
    That is, hour will be from 0 to 12, and if hour is 0, it will be AM.

    This function makes no assumptions about what hours of the day
    a truck delivers.
    '''
    return ((hour >= 0 and hour <= 12) and (minute >= 0 and minute < 60) and
            not (hour == 0 and am_pm in ('pm', 'PM')))

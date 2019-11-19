import re
from collections import namedtuple
from enum import Enum
from .time_custom import *
from .hash import *


class PackageSpecialNote_ValueError(BaseException):
    pass


class PkgState(Enum):
    '''Enumerate possible package states.'''
    AT_HUB = 1
    IN_TRANSIT = 2
    DELIVERED = 3
    LATE_ARRIVAL = 4
    WRONG_DESTINATION = 5


class Package():
    '''The Package class provides Package objects.

    Attributes (Instance variables):
     - ID: ID
     - deadline: when a package must be delivered by
     - weight: in kilograms.
        Note: no aspect of this entire program currently cares about weight.
    - location: a namedtuple of num, landmark, address
    - special note: a property of a package that itself has 4 properties:
        - truck_number
        - deliver_with
        - late_arrival
        - wrong_destination
        The first two of these subproperties are used to set initial state.
    '''

    History_Record = namedtuple('History_Record', ['state', 'time'])

    def __init__(self, pkg_id, d, w, sn, location):
        '''Create Package object.'''
        self.props = Hash(ID=int(pkg_id),
                          deadline=d,
                          weight=w,
                          location=location)

        self.props['special_note'] = Hash('truck_number',
                                          'deliver_with',
                                          'late_arrival',
                                          'wrong_destination')
        self.mark_package_special(self.parse_special_note(sn))

        self.props['state'] = None
        self.set_initial_state()

        self.props['history'] = []
        self.set_initial_history()

    def set_state(self, state_string):
        '''Update state of a package.'''
        self.props['state'] = PkgState(PkgState[state_string])

    def set_initial_state(self):
        '''Set initial state of package to hub, late, or wrong-destination.'''
        if self.props['special_note']['late_arrival']:
            self.set_state('LATE_ARRIVAL')
        elif self.props['special_note']['wrong_destination']:
            self.set_state('WRONG_DESTINATION')
        else:
            self.set_state('AT_HUB')

    def set_initial_history(self):
        '''Set initial history of a package as at-hub at 7:59am.'''
        self.props['history'].append(
            Package.History_Record(self.props['state'],
                                   Time_Custom(7, 59, 00)))

    def add_to_history(self, state_string, time):
        '''Add to history of a package object.'''
        self.props['history'].append(
            Package.History_Record(PkgState(PkgState[state_string]), time))

    def history_string(self, delimiter=None):
        '''Return print-statement-friendly history of package.'''
        return f'\n{delimiter}'.join([' at:\t'.join((record.state.name,
                                                     str(record.time)))
                          for record in self.props['history']])

    def update_late_as_arrived(self, time):
        '''Update a late-arriving package to indicate it is now at the hub.'''
        self.set_state('AT_HUB')
        self.props['history'].append(
            Package.History_Record(PkgState(PkgState['AT_HUB']), time))

    def update_wrong_destination_as_corrected(self):
        '''Update a wrong-destination package to indicate destination is now
        known. In other words, it can be delivered.'''
        self.set_state('AT_HUB')

    def update_package_destination(self, updated_destination):
        '''Update location property of package object.'''
        self.props['location'] = updated_destination

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
            truck_num = get_truck_number(special_note)
            return 'truck_number', truck_num
        if co_delivery_constraint:
            package_list = get_packages_to_deliver_with(special_note)
            return 'deliver_with', package_list
        if late_arrival_constraint:
            if not Time_Custom.is_valid_AM_PM_time(special_note):
                raise PackageSpecialNote_ValueError(
                    'Time-like value not parseable as an AM/PM time')
            when = Time_Custom.make_time_from_string(special_note)
            return 'late_arrival', when
        if wrong_destination_constraint:
            return 'wrong_destination', True

        if special_note != '':
            raise PackageSpecialNote_ValueError(
                'Special note could not be parsed as a package constraint')
        return None

    def mark_package_special(self, parsed_note):
        '''Update package props based off result of parsing special_note.

        Sets four new properties on self.special_note, initialized to None,
        then updates the zero or one properties passed in as parsed_note.
        '''
        if parsed_note is not None:
            parsed_note_key, parsed_note_value = parsed_note
            self.props['special_note'][parsed_note_key] = parsed_note_value

    def __str__(self):
        '''Return string representation of a Package object.'''
        return '\n\t'.join([f"Package ID: {self.props['ID']}",
                            f"delivery status: {self.props['state']}",
                            f"destination: {self.props['location'].address}",
                            f"deadline: {self.props['deadline']}",
                            f"weight: {self.props['weight']}"])


'''
    The following regex functions are not part of the Package class because
    they do not need to be--they neither consume nor produce Package objects.
'''
truck_pattern = re.compile("(only)(.*?)(truck) \d", re.IGNORECASE)
delivery_pattern = re.compile("(delivered with \d+[, \d+]*)", re.IGNORECASE)
arrival_pattern = re.compile("(delayed)(.*?)\d\d?:\d\d (am|pm)", re.IGNORECASE)
destination_pattern = re.compile("wrong address", re.IGNORECASE)


def truck_regex_match(note):
    '''Return regex match for a truck-number constraint in a special note.'''
    return truck_pattern.search(note)


def delivery_regex_match(note):
    '''Return regex match for a delivery constraint in a special note.'''
    return delivery_pattern.search(note)


def arrival_regex_match(note):
    '''Return regex match for a late-arrival constraint in a special note.'''
    return arrival_pattern.search(note)


def destination_regex_match(note):
    '''Return regex match for wrong-destination constraint in special note.'''
    return destination_pattern.search(note)


def validate_truck_number(integers_found):
    '''Validate truck number found in package special note.

    This function assumes that the company's truck-number labels
    will always be less than 100.
    '''
    return len(integers_found) == 1 and integers_found[0] < 100


def get_truck_number(note):
    '''Parse and return truck number from a package special note.'''
    integers_found = [int(num) for num in filter(str.isdigit, note)]
    if not validate_truck_number(integers_found):
        raise PackageSpecialNote_ValueError(
            'Truck-number error in special note: either more than one '
            'number was found, or it was too high to be a truck number')

    truck_num = integers_found[0]
    return truck_num


def validate_package_ID_list(integers_found):
    '''Validate co-delivery package IDs found in package special note.

    This function assumes that the company's package ID numbers
    will always be less than 1000. This assumption is shared by a
    cli module function (get_package_id_from_string).
    '''
    return all([i > 0 and i < 1000 for i in integers_found])


def get_packages_to_deliver_with(note):
    '''Parse and return list of package IDs from a package special note.'''
    index_of_first_integer = re.search("\d", note, re.IGNORECASE).start()
    substring = note[index_of_first_integer:]
    integers_found = [int(num) for num in substring.split(', ')]
    if len(integers_found) == 0:  # try split by ',' instead of ', '
        integers_found = [int(num) for num in substring.split(',')]

    if not validate_package_ID_list(integers_found):
        raise PackageSpecialNote_ValueError(
            'Package-ID error in a deliver-with special note: one or more '
            'IDs found was either below zero or too high to be a package ID')

    package_IDs = integers_found
    return package_IDs

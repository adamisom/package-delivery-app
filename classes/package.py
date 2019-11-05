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
        Called in/by: load.py ~??

        Things it should do (remember, one function per task):
            set_initial_status(self.mark_pkg(self.parse_special_note(sn))))
            NOTE: these would go on the wish list but I'll just copy/paste them
            add all passed-in properties
                notably including location (in place of address+city+state+zip)
            add status property
            add history property

        Data definitions:
        Location: a namedtuple of location-number, landmark, street address.
        '''
        self.ID = Package.id_counter
        Package.id_counter += 1

        self.deadline = d
        self.weight = w
        self.location = location

        self.special_note = sn
        self.status = None
        # call special note parsing right here

        self.history = [(self.status, Time_Custom(8, 00, 00))]

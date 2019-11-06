class Time_Custom:
    '''Time objects represent a truck's clock. Minutes can be added to them.

    Objects are military time (no AM/PM) and do not have fractional seconds.
    Example usage:
        given:  Time_Custom(13,15,27)
        add:    33.5 minutes
        result: Time_Custom(13,48,57)
    '''

    def __init__(self, hour, minute, second):
        '''Create Time_Custom object.'''
        self.hour = hour
        self.minute = minute
        self.second = second

    def advance_clock(self, minutes):
        '''Advance the "clock" of a Time_Custom object by adding minutes.

        Input is restricted to a (positive number of) minutes.

        This function assumes only that the travel time between any two
        destinations does not exceed 16 hours.
        '''
        if minutes < 1 or minutes > 960:
            raise ValueError('Ineligible number of minutes passed')
        else:
            h, m, s = Time_Custom.decompose(minutes)
            h, m, s = (h + self.hour), (m + self.minute), (s + self.second)
            m, s = Time_Custom.adjust_seconds(m, s)
            h, m = Time_Custom.adjust_minutes(h, m)
            self.hour, self.minute, self.second = h, m, s

    @staticmethod
    def decompose(minutes_to_add):
        '''Break down minutes-to-add into hours, minutes and seconds.'''
        h = int(minutes_to_add / 60)
        m = int(minutes_to_add - 60 * h)
        s = round(60 * (minutes_to_add % 1))
        return h, m, s

    @staticmethod
    def adjust_minutes(h, m):
        '''Adjust any number of seconds > 60 by rolling over into minutes.'''
        hours_overflow = int((m - (m % 60)) / 60)
        return h + hours_overflow, m - 60 * hours_overflow

    @staticmethod
    def adjust_seconds(m, s):
        '''Adjust any number of minutes > 60 by rolling over into hours.'''
        minutes_overflow = int((s - (s % 60)) / 60)
        return m + minutes_overflow, s - 60 * minutes_overflow

    def __str__(self):
        '''Return string representation of a Time_Custom object.'''
        return f'{self.hour:02}:{self.minute:02}:{self.second:02}'

    def __eq__(self, other):
        '''Return whether one time is == another. Assumes inputs are times.'''
        if not isinstance(other, Time_Custom):
            raise ValueError('Right-hand side of == not a Time_Custom object')
        elif (self.hour == other.hour and
              self.minute == other.minute and
              self.second == other.second):
            return True
        else:
            return False

    def __ne__(self, other):
        '''Return whether one time is != another. Assumes inputs are times.'''
        return not self == other

    def __lt__(self, other):
        '''Return whether one time is < another. Assumes inputs are times.'''
        if not isinstance(other, Time_Custom):
            raise ValueError('Right-hand side of < not a Time_Custom object')
        else:
            if self.hour < other.hour:
                return True
            elif (self.hour == other.hour and
                  self.minute < other.minute):
                return True
            elif (self.minute == other.minute and
                  self.second < other.second):
                return True
            else:
                return False

    def __gt__(self, other):
        '''Return whether one time is > another. Assumes inputs are times.'''
        if not isinstance(other, Time_Custom):
            raise ValueError('Right-hand side of > not a Time_Custom object')
        else:
            if self.hour > other.hour:
                return True
            elif (self.hour == other.hour and
                  self.minute > other.minute):
                return True
            elif (self.minute == other.minute and
                  self.second > other.second):
                return True
            else:
                return False

    def __le__(self, other):
        '''Return whether one time is <= another. Assumes inputs are times.'''
        return self == other or self < other

    def __ge__(self, other):
        '''Return whether one time is >= another. Assumes inputs are times.'''
        return self == other or self > other

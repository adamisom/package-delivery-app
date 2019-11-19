class Hash():
    '''The Hash class provides hash-table objects.

    Public API / Examples of Usage, in Ten Lines:
        example = Hash()  # initialize
        example['hello'] = 5
        example['hello']  # returns 5
        str(example)  # returns { hello: 5 }  (but {} on separate lines)
        example['hey']  # raises KeyError
        example2 = Hash(3)  # raises TypeError (keys must be strings)
        example3 = Hash('hi')  # adds a key of 'hi' and default value of None
        example4 = Hash(['hi', 3])  # adds a key of 'hi' with value 3
        example5 = Hash(('hi', 6))  # adds a key of 'hi' with value 6
        example6 = Hash(a_kwarg=45)  # adds a key of 'a_kwarg' with value 45

    Note on hash collision: the chaining approach is used.
      If multiple values have the same hashed index, there will be a list of
      key-value lists at that index.
      For the more common case of no collision for a given index, there will be
      only a single key-value list at an index.

    Further notes:
      - Under the hood, hashed keys and their values are stored as nested lists
      - Hash objects are doubled and rehashed when # items >60% of __props size
      - The internal _hash method is basic and should not be regarded as secure
    '''

    def __init__(self, *args, **kwargs):
        '''Create hash object.

        Attributes:
          - hash_size: all Hash objects start with 50 buckets/slots
          - props: this stores the hashed values. Initialized with Nones.
        '''
        self._hash_size = 50
        self._props = [None] * self._hash_size
        self._count = 0

        for k, v in kwargs.items():
            self[k] = v

        for arg in args:
            if isinstance(arg, (list, tuple)) and len(arg) == 2:
                key_string, value = arg[0], arg[1]
                self[key_string] = value
            else:
                self[arg] = None

    def get(self, key_string, default=None):
        '''Return property of hash object or default value if key not found.

        This is identical to __getitem__ except "raise KeyError.." is replaced
        with "return default".
        '''
        if not isinstance(key_string, str):
            raise TypeError(f'Key {key_string} is not a string')

        index = self._hash(key_string)
        prop = self._props[index]

        # case: None was at that index
        if prop is None:
            return default

        # case: a list of key-value lists was at that index
        if isinstance(prop[0], list):
            for sub_list in prop:
                if sub_list[0] == key_string:
                    return sub_list[1]
            return default

        # case: a single key-value list was at that index
        if prop[0] == key_string:
            return prop[1]
        else:
            return default

    def _flatten(self):
        '''Flatten props. This method exists to be called by __repr__.'''
        flat = []

        for prop in self._props:
            if prop is None:
                continue

            if isinstance(prop[0], list):
                for sub_list in prop:
                    key_string, value = sub_list[0], sub_list[1]
                    flat.append([key_string, value])

            else:
                key_string, value = prop[0], prop[1]
                flat.append([key_string, value])

        return flat

    def _hash(self, key_string, str_size_min=10):
        '''Hash a key and return index.'''
        padded = key_string.rjust(str_size_min, key_string[0])
        return sum([(ord(ch)) ** ((idx % 30) + 5) + 43
                   for idx, ch in enumerate(padded)]
                   ) % self._hash_size

    def _rehash(self):
        '''Re-hash all items (called when self._props needs to double).'''
        copy = self._double()
        self._count = 0

        for prop in copy:
            if prop is None:
                continue

            if isinstance(prop[0], list):
                for sub_list in prop:
                    key_string, value = sub_list[0], sub_list[1]
                    self[key_string] = value

            else:
                key_string, value = prop[0], prop[1]
                self[key_string] = value

    def _double(self):
        '''Double hash object props size and re-hash all keys.

        The disregard of the copy module's deepcopy method is intentional,
        in order to keep this class free of imports.
        '''
        copy = Hash._deepcopy(self._props)

        self._hash_size *= 2
        self._props = [None] * self._hash_size

        return copy

    def _debug_str(self):
        '''Return string representation of hash object useful for debugging.

        Whereas str prints self._props as if the underlying data structure
        were (itself) a hash, debug_str shows what Hash objects truly are:
        nested lists.
        '''
        return f"\nprops: {','.join([str(prop) for prop in self._props])}\n"

    def __getitem__(self, key_string):
        '''Get property of hash object via [] notation.'''
        if not isinstance(key_string, str):
            raise TypeError(f'Key {key_string} is not a string')

        index = self._hash(key_string)
        prop = self._props[index]

        # case: None was at that index
        if prop is None:
            raise KeyError(f'Key {key_string} does not exist in the hash')

        # case: a list of key-value lists was at that index
        if isinstance(prop[0], list):
            for sub_list in prop:
                if sub_list[0] == key_string:
                    return sub_list[1]
            raise KeyError(f'Key {key_string} does not exist in the hash')

        # case: a single key-value list was at that index
        if prop[0] == key_string:
            return prop[1]
        else:
            raise KeyError(f'Key {key_string} does not exist in the hash')

    def __setitem__(self, key_string, value):
        '''Set property of hash object via [] notation.'''
        if not isinstance(key_string, str):
            raise TypeError(f'Key {key_string} is not a string')

        index = self._hash(key_string)
        prop = self._props[index]

        # case: None was at that index
        if prop is None:
            self._props[index] = [key_string, value]
            self._count += 1

        # case: a list of key-value lists was at that index
        elif isinstance(prop[0], list):
            for sub_list in prop:
                if sub_list[0] == key_string:
                    sub_list[1] = value
            # if not found:
            self._props[index].append([key_string, value])
            self._count += 1

        # case: a single key-value list was at that index
        # note: at this point, isinstance(prop, list) must be True
        else:
            if prop[0] == key_string:
                self._props[index][1] = value
            else:  # if not found, wrap existing item in a list and append
                current_resident = self._props[index]
                self._props[index] = [current_resident]
                self._props[index].append([key_string, value])
                self._count += 1

        # rehash if self._props is getting too full
        if self._count / self._hash_size >= 0.6:
            self._rehash()

    def __str__(self):
        '''Return string representation of hash object.'''
        prop_strings = []

        for prop in self._props:
            if prop is None:
                continue

            if isinstance(prop[0], list):
                props_from_subl = []

                for sub_l in prop:
                    # avoid infinite recursion if a value happens to be 'self'
                    if sub_l[1] is self:
                        props_from_subl.append(f'\n\t\t{repr(sub_l[0])}: '
                                               '"self"')
                    else:
                        props_from_subl.append(f'\n\t\t{repr(sub_l[0])}: '
                                               f'{repr(sub_l[1])}')

                prop_strings.append(
                  '\n\t{' + ','.join(props_from_subl) + '\n\t}')

            else:
                # avoid infinite recursion if a value happens to be 'self'
                if prop[1] is self:
                    prop_strings.append(f'\n\t{repr(prop[0])}: "self"')
                else:
                    prop_strings.append(f'\n\t{repr(prop[0])}: '
                                        f'{repr(prop[1])}')

        return '{' + ','.join(prop_strings) + '\n}'

    def __repr__(self):
        '''Return string representation of hash object.'''
        unpacked = ', '.join(str(x) for x in self._flatten())
        return f'Hash({unpacked})'

    def __eq__(self, other):
        '''Compare two hash objects to check if they are equal.

        Two hash objects are equal if they have the same (non-None) props.
        '''
        return self._props == other._props

    @staticmethod
    def _deepcopy(lst):
        '''Create a deep copy of a list.

        This method was created intentionally to cut out an unneeded import,
        namely deepcopy from copy.
        '''
        result = []

        for item in lst:
            if not isinstance(item, list):
                result.append(item)

            else:
                result.append(Hash._deepcopy(item))

        return result

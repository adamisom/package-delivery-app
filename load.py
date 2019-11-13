import csv
import re
from collections import namedtuple
from .classes.package import Package
from .classes.time_custom import Time_Custom


class DistanceCsv_ValueError(BaseException):
    pass


class PackageCsv_ValueError(BaseException):
    pass


def read_distance_csv(csv_file):
    '''Return list-of-lists representation of the contents of passed-in csv.

    Remarks on csv: This whole program expects the passed-in csv to contain a
    (skippable) header. It expects the list of locations appearing in the
    first column to be identical to the list of locations in the first row.
    It expects there to be a second column with location data, but this column
    contains only street-addresses and zip-codes, not landmark names (like the
    first row and column have). Finally, it expects that zip codes will
    consistently appear only in this second column, and they will be wrapped
    in parentheses.
    None of these expectations should be read as an endorsement of the format
    of the input csv. This is simply the format that the user provides.
    '''
    csv_data = []
    with open(csv_file) as csvFile:
        csvReader = csv.reader(csvFile)
        for row in csvReader:
            if row[0] != '':
                csv_data.append(row)
    return csv_data


def clean_address_data(column_one, column_two):
    '''Return tuple of cleaned landmark and street address.'''

    # In column one of csv, street-address is on a newline after landmark name
    landmark = column_one.split('\n')[0].strip()

    # In column two the format is 'address\n(zip)'--I prefer 'address zip'
    # and that is the format to which package addresess will be matched
    street_address = column_two.replace('\n(', ' ').rstrip(')').strip()

    # Package addresses will have the same standard for direction abbreviation
    # so that the two sets of addresses are consistent and therefore matchable
    street_address = (street_address
                      .replace('South', 'S')
                      .replace('North', 'N')
                      .replace('East', 'E')
                      .replace('West', 'W'))

    return landmark, street_address


def get_location_data(csv_data):
    '''Return list of tuples of index, landmarks, and street addresses.'''
    locations = []
    for index, row in enumerate(csv_data):
        if index != 0:
            landmark, street_address = clean_address_data(row[0], row[1])
            locations.append((index, landmark, street_address))
    return locations


def populate_locations(location_data, Location_constructor):
    '''Return list of location named-tuples from location data.'''
    Locations = []
    for location_datum in location_data:
        Locations.append(Location_constructor(*location_datum))
    return Locations


def clean_distance_data(csv_data):
    '''Remove redundant column, use location numbers instead of names,
    and convert distance data (a mix of integer and string) to floats.
    '''
    for row_index, row in enumerate(csv_data):
        del row[1]

        for col_index, datum in enumerate(row):
            if row_index != 0 and col_index != 0:
                if datum != '':
                    csv_data[row_index][col_index] = float(datum)

        # row_index will be used for location numbers
        if row_index != 0:
            row[0] = row_index

    # col_index will be used for location numbers
    # Note that col_index coincides with (is the same value as) row_index.
    for col_index, _ in enumerate(csv_data[0]):
        if col_index != 0:
            csv_data[0][col_index] = col_index


def fill_distance_data(data):
    '''Fill in distance data where the missing pieces of data can be inferred.

    If cell at [i,j] is missing, but [j,i] is known, fill [i,j] with [j,i],
    and vice versa. Skip when neither or both are empty.
    '''
    for row_index, row in enumerate(data):
        for col_index, distance in enumerate(row):
            ij = data[row_index][col_index]
            ji = data[col_index][row_index]

            if ij == '' and ji != '':
                data[row_index][col_index] = data[col_index][row_index]

            elif ji == '' and ij != '':
                data[col_index][row_index] = data[row_index][col_index]


def validate_distance_data(data):
    '''Validate distance data is both present and non-contradicting.'''
    for row_index, row in enumerate(data):
        for col_index, distance in enumerate(row):
            ij = data[row_index][col_index]
            ji = data[col_index][row_index]

            if ij is None and ji is None:
                return False
            if ij != ji:
                return False

    return True


def read_package_csv(csv_file):
    '''Return list-of-lists representation of the contents of passed-in csv.

    Remarks on csv: This whole program expects the passed-in csv to contain
    a list of package attributes in the following order:
        - Package ID
        - Address
        - City
        - State
        - Zip
        - Delivery Deadline (a time-of-day)
        - Mass (weight in kg)
        - Special Notes
            Note: The plural is a misnomor--only one special note is permitted
    '''
    csv_data = []
    with open(csv_file) as csvFile:
        csvReader = csv.reader(csvFile)
        for row in csvReader:
            if row[0].isdigit():
                csv_data.append(row)
    return csv_data


def clean_package_data(csv_data):
    '''Clean package data preliminarily to initializing package objects.'''
    for row in csv_data:
        # if deadline is 'EOD' or end of day, it can be ignored
        if row[5] == 'EOD':
            row[5] = None

        # Distance addresses have the same standard for direction abbreviation
        # so that the two sets of addresses are consistent and thus matchable
        row[1] = (row[1]
                  .replace('South', 'S')
                  .replace('North', 'N')
                  .replace('East', 'E')
                  .replace('West', 'W'))

        # only the first eight columns have data
        del row[8:]


def validate_package_address_data(package_data, location_namedtuples):
    '''Validate all package address data matches a location address.'''
    location_addresses = [loc[2] for loc in location_namedtuples]
    for row in package_data:
        package_address = f'{row[1]} {row[4]}'  # street address plus zip code
        if package_address not in location_addresses:
            return False
    return True


def get_one_package_destination(pkg_row, location_namedtuples):
    '''Return the location named-tuple matching a package's destination.'''
    package_address = f'{pkg_row[1]} {pkg_row[4]}'  # street address plus zip
    location_addresses = [loc[2] for loc in location_namedtuples]
    return location_namedtuples[location_addresses.index(package_address)]


def validate_package_deadline_times(package_data):
    '''Validate that all package deadlines can be converted to Time_Custom.'''
    for row in package_data:
        deadline = row[5]
        if deadline is None:
            continue

        if not Time_Custom.is_valid_AM_PM_time(deadline):
            return False

    return True


def populate_packages(package_data, location_namedtuples):
    '''Return list of Package objects based on package data from the csv.'''
    all_packages = []
    for package_row in package_data:
        destination = get_one_package_destination(package_row,
                                                  location_namedtuples)
        deadline = package_row[5]
        if deadline is not None:
            deadline = Time_Custom.make_time_from_string(package_row[5])

        data_to_use = [package_row[0], deadline] + package_row[6:8]
        new_package = Package(*data_to_use, destination)
        all_packages.append(new_package)
    return all_packages


def load_data(distance_csv, package_csv):
    '''Populate packages list, distances 2D list, Locations namedtuple list.

    Data definition:
    A Location is a namedtuple of location-number, landmark, street address.
    '''
    distances, Locations, packages = [], [], []

    Location = namedtuple('Location', ['num', 'landmark', 'address'])

    distances = read_distance_csv(distance_csv)

    # Locations populated first because clean_distance_data removes addresses
    location_data = get_location_data(distances)
    Locations = populate_locations(location_data, Location)
    clean_distance_data(distances)
    fill_distance_data(distances)

    if not validate_distance_data(distances):
        raise DistanceCsv_ValueError('One or more distance values are absent '
                                     'or contradict other values in the file')

    package_data = read_package_csv(package_csv)
    clean_package_data(package_data)

    if not validate_package_address_data(package_data, Locations):
        raise PackageCsv_ValueError('One or more package addresses does not '
                                    'match any location from distances csv')
    if not validate_package_deadline_times(package_data):
        raise PackageCsv_ValueError('One or more package deadlines could not '
                                    'be parsed as a valid AM/PM time')

    packages = populate_packages(package_data, Locations)

    return distances, Locations, packages

import re


def test_regexes():
    '''
    Functions to test:
    truck_regex_match
    delivery_regex_match
    arrival_regex_match
    destination_regex_match

    get_truck_number
    get_packages_to_deliver_with
    get_arrival_time

    validate_truck_number
    validate_package_ID_list
    validate_arrival_time
    '''
    pass

# Test strings and expected pass/fails:
# s = 'Can only be on truck 2'  # expect: pass
# s = 'Can only be on truck2'  # fail
# s = 'can oNlY be on trUcK 2'  # pass
# s = 'Can only be on truck 22'  # fail
# s = 'Can only be on truck 0'  # fail
# s = 'Can only be on truck 4'  # fail
# s = 'Can only be on truck -1'  # fail
# s = 'Can only be on truck'  # fail
# s = 'Delayed on flight---will not arrive to depot until 9:05 am'  # pass
# s = 'Delay--will not arrive until 9:05 am'  # pass
# s = 'Delay--will arrive 9:05 am'  # pass
# s = 'Delay--will arrive 9:05am'  # uh oh, currently won't pass--but should
# s = 'Delay--will arrive 19:00am'  # pass (yes, user shouldn't have said am!)
# s = 'Delay--will arrive 24:00pm'  # fail
# s = 'Delay--will arrive 19:65am'  # fail
# s = 'Delay--will arrive 6am'  # fail
# s = 'Delay--will arrive 9am'  # uh oh, currently won't pass--but should
# s = 'Must be delivered with 15, 19'  # pass
# s = 'Must be delivered with 15,19'  # pass
# s = 'Must be delivered with 5, 19'  # pass
# s = 'Must be delivered with 5, 3, and 19'  # fail (users must be trained!)
# s = 'Wrong address listed'  # pass
# s = 'wrong address'  # pass
# s = 'incorrect address'  # fail (users must be trained to write 'wrong'!)

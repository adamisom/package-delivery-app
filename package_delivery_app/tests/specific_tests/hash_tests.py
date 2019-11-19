from ...classes.hash import *


def test_hashes():
    # 1 PASS
    # initialize a Hash with two values and print the hash. This will
    hash_one = Hash('bob', 'joe')
    # print("I expect to see a list of 48 Nones and "
    # "two key-value lists of form [value, None]")
    # print(hash_one._debug_str())

    # GET TESTS
    # 2 PASS
    # Key not found, test 1: None is found at the index
    # print("I expect hash_one['sarah'] to raise a KeyError")
    # print(hash_one['sarah'])

    # 3 PASS
    # Key not found, test 2: a key-value list is found at the index,
    # but the key does not match the key being requested
    # print("I expect hash_one['cnb'] to raise a KeyError")
    # print(hash_one['cnb'])

    # 4 PASS
    # Key not found, test 3: a list of key-value lists is found at the index,
    # but none of the keys in the key-value lists match the requested key
    # hash_one['cnb'] = 55  # creating a list of key-value lists at that index
    # print("I expect hash_one['dmb'] to raise a KeyError")
    # print(hash_one['dmb'])

    # 5 PASS
    # Get from a single key-value list
    # In the 'bob' case below, I expect the default value to be None
    # This situation will occur when a new Hash is initialized with arguments.
    # hash_one['new_key'] = 42
    # print("I expect hash_one['new_key'] to return 42")
    # print(hash_one['new_key'])
    # print("I expect hash_one['bob'] to return None")
    # print(hash_one['bob'])

    # 6 PASS
    # NOTE: this is when my hashing algorithm was weaker. I could find it
    # by searching my git commits if need be. Back then, bob=cnb
    # Get from a list of key-value lists
    # hash_one['cnb'] = 55
    # print(f"Showing there is a list of lists now: {hash_one._debug_str()}")
    # print("I expect hash_one['bob'] to return None")
    # print(hash_one['bob'])

    # SET TESTS
    # 7 PASS
    # assign to an index currently holding None
    # this should replace None with [key, value]
    # NOTE: this is the case that the vast majority of hashes should fall into
    # hash_one['dork'] = 30
    # print("I expect hash_one['dork'] to return 30")
    # print(hash_one['dork'])

    # 8 PASS
    # reassign an existing key
    # (no hash collision, i.e., only one key-value list is at that index)
    # hash_one['bob'] = 7
    # print("I expect hash_one['bob'] to return 7")
    # print(hash_one['bob'])

    # 9 PASS
    # NOTE: this is when my hashing algorithm was weaker. I could find it
    # by searching my git commits if need be. Back then, bob=cnb
    # hash collision case 1: one key-value list exists at that index already
    # but the key living there is not the key being inserted
    # this should wrap the existing key-value list in a list,
    # and then append to the outer list
    # hash_one['cnb'] = 55
    # print(f"Showing there is a list of lists now: {hash_one._debug_str()}")

    # 10 PASS
    # hash collision case 2: multiple key-value lists exist there already
    # and the key being updated already exists in that list
    # in this case, reassign the existing key
    # hash_one['cnb'] = 55
    # print("I expect hash_one['cnb'] to return 55")
    # print(hash_one['cnb'])
    # hash_one['cnb'] = 37
    # print("I expect hash_one['cnb'] to return 37")
    # print(hash_one['cnb'])

    # 11 PASS
    # hash collision case 3: multiple key-value lists exist there already
    # and the key in question does not yet exist among the list
    # in this case, append to the existing list of key-value lists
    # hash_one['cnb'] = 55
    # hash_one['dmb'] = 44
    # print("I expect hash_one['dmb'] to return 44")
    # print(hash_one['dmb'])

    # TESTS ADDED LATER
    # 12 PASS
    # initialize Hash object with key-value lists
    # hash_two = Hash(['hello', 4], ['world', 5])
    # print("I expect to see [hello,4] and [world,5] in hash_two")
    # print(hash_two._debug_str())

    # 13 PASS
    # initialize Hash object with a mix of key-strings and key-value tuples
    # hash_three = Hash('hello', ('world', 5))
    # print("I expect to see [hello,None] and [world,5] in hash_two")
    # print(hash_three._debug_str())

    # 14 PASS
    # as soon as 60% or more of buckets/slots are filled,
    # hash_size (buckets/slots) is doubled
    # hash_four = Hash(*[c for c in 'abcdefghijklmnopqrstuvwxyz0123'])
    # print("I expect there to be 50 slots")
    # print('length: ', len(hash_four._props))
    # hash_four['%'] = 8
    # print("I expect there to be 100 slots")
    # print('length: ', len(hash_four._props))
    # print(hash_four._debug_str())

    # 15 PASS
    # as soon as 60% or more of buckets/slots are filled, all keys are
    # re-hashed. NOTE: nested lists count once per sublist.
    # hash_five = Hash(*[c for c in 'abcdefghijklmnopqrstuvwxyz0123'])
    # print("I expect the ordering of items to be different between 1 and 2.")
    # print("len(1)", len(hash_five._props), " and 1:", hash_five._debug_str())
    # hash_five['%'] = 8
    # print("len(2)", len(hash_five._props), " and 2:", hash_five._debug_str())

    # 16 PASS
    # NOTE: this is when my hashing algorithm was weaker. I could find it
    # by searching my git commits if need be. Back then, bob=cnb
    # str method correctly formats hashes with sublists and excludes all Nones
    # hash_six = Hash('bob', 'cnb')  # bob and cnb hash to same index
    # print(str(hash_six))
    # hash_six_point_one = Hash('bob')
    # print(str(hash_six_point_one))
    # hash_six_point_two = Hash()
    # print(str(hash_six_point_two))

    # 17 PASS
    # getitem raises an error if not given a string
    # print("I expect to see a TypeError with hash_six[4]")
    # hash_six[4]

    # 18 PASS
    # setitem raises an error if not given a string
    # print("I expect to see a TypeError with hash_six[4] = 6")
    # hash_six[4] = 6

    # 19
    # str method does not break if a hashed value equals itself
    # hash_seven = Hash('hi','world')
    # hash_seven['recursion!'] = hash_seven
    # print("I expect to see..")
    # print(str(hash_seven))

    # # 20 PASS
    # # _debug_str method represents props as what they are--nested lists
    # hash_eight = Hash(('hey', 4))
    # print(hash_eight._debug_str())

    # 21 PASS
    # deepcopy method works
    # b = [[[3,4],[5],6],[7,[8,9]],10]
    # b_ = Hash._deepcopy(b)
    # print(b)
    # print(b_)
    # print('This should fail: id b_ == id b:', id(b_)==id(b))

    # 22 PASS
    # initializing Hash with None throws KeyError (because None not a string)
    # hash_nine = Hash(None)
    # print("I expect to see a KeyError")
    # print(hash_nine._debug_str())

    # 23 PASS
    # hash_ten, hash_eleven = Hash(['hello', 5]), Hash()
    # print("Before adding prop to hash_eleven I expect False for == test")
    # print(hash_ten == hash_eleven)
    # print("After adding prop to hash_eleven I expect True for == test")
    # hash_eleven['hello'] = 5
    # print(hash_ten == hash_eleven)

    # 24 PASS
    # hash_twelve = Hash(['world', 5])
    # print("I expect get to behave the same as [] when a value has been set")
    # print(f"Expecting 5: {hash_twelve.get('world')}")
    # print("I expect get to supply a default value if no value has been set")
    # print(f"Expecting None: {hash_twelve.get('hello')}")
    # print("I expect get to use a passed-in default value")
    # print(f"Expecting 'not found!': {hash_twelve.get('hello','not found!')}")

    # 25 PASS
    # eval(repr(obj) should == obj
    # hash_13 = Hash('hey', ['yo', 5])
    # print("I expect this to be True: hash_13 == eval(repr(hash_13))")
    # print(hash_13 == eval(repr(hash_13)))

    # 26 PASS
    # passing kwargs into Hash() adds them
    # hash_14 = Hash(a_kwarg=45)
    # print("I expect to see a Hash with k-v pair [a_kwarg, 45]")
    # print(hash_14._debug_str())

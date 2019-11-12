# per notes.txt, each item has:
# meaningful name - signature - purpose stmt


def add_up_to_max_load(pkg_load, candidates_to_add, max_load):
    '''Return list of packages with some to all of candidates_to_add
    added, up to max_load.
    TODO: raise error if pkg_load already > 16? '''
    while len(pkg_load) <= max_load:
        pkg_load.append(candidates_to_add.pop())
    return pkg_load

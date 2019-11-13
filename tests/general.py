from ..classes.time_custom import *
from ..classes.package import *
from ..classes.truck import *
from ..classes.route_builder import *
from .specific_tests.algorithms_tests import test_algorithms
from .specific_tests.hash_tests import test_hashes
from .specific_tests.regex_tests import test_regexes


def test():
    test_algorithms()
    test_hashes()
    test_regexes()

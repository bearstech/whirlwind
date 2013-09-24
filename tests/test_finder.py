import unittest

from whirlwind.mock import MockFinder, MockNoiseReader
from whirlwind.storage import FindQuery


class FinderTest(unittest.TestCase):

    def test_mock(self):
        r = MockNoiseReader()
        m = MockFinder({'mock.a.b.c': r})
        f = FindQuery('mock.a.*', None, None)
        for node in m.find_nodes(f):
            assert node.path == 'mock.a.b.c'

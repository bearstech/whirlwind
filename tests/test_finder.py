import time
import unittest

from whirlwind.mock import MockFinder, MockNoiseReader
from whirlwind.storage import FindQuery


class FinderTest(unittest.TestCase):

    def test_mock(self):
        r = MockNoiseReader()
        m = MockFinder({'mock.a.b.c': r})
        f = FindQuery('mock.a.*', None, None)
        now = int(time.time())
        for node in m.find_nodes(f):
            assert node.path == 'mock.a.b.c'
            timeInfo, values = node.fetch(now - 300, now)
            startTime, endTime, step = timeInfo
            assert startTime == now - 300
            assert endTime == now
            assert step == 30  # Default value
            assert len(values) == (endTime - startTime) / step

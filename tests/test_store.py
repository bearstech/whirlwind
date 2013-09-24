import unittest

from whirlwind.mock import MockFinder, MockNoiseReader
from whirlwind.storage import Store


class TestStore(unittest.TestCase):

    def test_mock(self):
        r = MockNoiseReader()
        m = MockFinder({'mock.a.b.c': r})
        store = Store([m])
        f = list(store.find('mock.a.*'))
        assert len(f) == 1
        f = store.find('a.*')
        assert list(f) == []

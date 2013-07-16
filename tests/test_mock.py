import unittest
from whirlwind import mock


class MockTest(unittest.TestCase):
    def test_get(self):
        m = mock.MockStoreNoise()
        a = m.fetch('test', '-12hours')
        assert len(a[0]) == 1440

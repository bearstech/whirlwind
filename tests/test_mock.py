import unittest
from whirlwind import mock


class MockTest(unittest.TestCase):
    def test_get(self):
        m = mock.MockStore()
        a = m.fetch('test', '-12hours')
        print a

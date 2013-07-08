import unittest
from whirlwind import mock


class MockTest(unittest.TestCase):
    def test_get(self):
        a = mock.whisper_get('-12hours')
        print a

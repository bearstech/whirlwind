import unittest
from whirlwind import evaluator
from whirlwind.mock import MockStoreStatic


class EvaluatorTest(unittest.TestCase):
    def test_tokens(self):
        store = MockStoreStatic()
        tokens = 'averageSeries(a.b.1, d.e.3)'
        context = {
            'startTime': '-2days',
            'endTime': 'now',
        }
        values = evaluator.evaluateTarget(store, context, tokens)
        for v in values[0]:
            assert v == 2.0

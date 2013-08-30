import unittest
from whirlwind import evaluator
from whirlwind.mock import MockStoreStatic, MockStore


class EvaluatorTest(unittest.TestCase):

    def _evaluator(self, tokens):
        store = MockStoreStatic()
        context = {
            'startTime': '-2days',
            'endTime': 'now',
        }
        return evaluator.evaluateTarget(store, context, tokens)

    def test_average(self):
        values = self._evaluator('averageSeries(a.b.1, d.e.3)')
        for v in values[0]:
            assert v == 2.0

    def test_sum(self):
        values = self._evaluator('sumSeries(a.b.1, d.e.3)')
        for v in values[0]:
            assert v == 4.0

    def test_diff(self):
        values = self._evaluator('diffSeries(a.b.5, d.e.1)')
        for v in values[0]:
            assert v == 4.0
        # Doesn't work in the graphite project too
        #values = self._evaluator('diffSeries(a.b.5,3)')
        #for v in values[0]:
            #assert v == 2.0

    def test_min_max(self):
        store = MockStore({'a.b.c': [1, 2, 3, 4, 1, 5],
                           'd.e.f': [2, 1, 3, 0, 6, 7]
                           })
        context = {
            'startTime': '-2days',
            'endTime': 'now',
        }
        tokens = 'minSeries(a.b.c, d.e.f)'
        values = evaluator.evaluateTarget(store, context, tokens)
        vv = [v for v in values[0] if v is not None]
        assert vv == [1, 1, 3, 0, 1, 5]

        tokens = 'maxSeries(a.b.c, d.e.f)'
        values = evaluator.evaluateTarget(store, context, tokens)
        vv = [v for v in values[0] if v is not None]
        assert vv == [2, 2, 3, 4, 6, 7]

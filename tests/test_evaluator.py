import unittest
from whirlwind import evaluator
from whirlwind.mock import MockStaticReader, MockFinder
from whirlwind.storage import Store
from whirlwind.attime import parseATTime


class EvaluatorTest(unittest.TestCase):
    def setUp(self):
        mock_reader = MockStaticReader()
        finder = MockFinder({
            'one': MockStaticReader(1),
            'three': MockStaticReader(3),
            'five': MockStaticReader(5)
        })
        self.store = Store([finder], hosts=None)

    def _evaluator(self, tokens):
        context = {
            'startTime': parseATTime('-2days'),
            'endTime': parseATTime('now'),
            'localOnly': True
        }
        return evaluator.evaluateTarget(self.store, context, tokens)

    def test_average(self):
        values = self._evaluator('averageSeries(one, three)')
        for v in values[0]:
            assert v == 2.0

    def test_sum(self):
        values = self._evaluator('sumSeries(one, three)')
        for v in values[0]:
            assert v == 4.0

    def test_diff(self):
        values = self._evaluator('diffSeries(five, one)')
        for v in values[0]:
            assert v == 4.0
        # Doesn't work in the graphite project too
        #values = self._evaluator('diffSeries(a.b.5,3)')
        #for v in values[0]:
            #assert v == 2.0

    # FIXME
    #def test_min_max(self):
        #store = MockStore({'a.b.c': [1, 2, 3, 4, 1, 5],
                           #'d.e.f': [2, 1, 3, 0, 6, 7]
                           #})
        #context = {
            #'startTime': '-2days',
            #'endTime': 'now',
        #}
        #tokens = 'minSeries(a.b.c, d.e.f)'
        #values = evaluator.evaluateTarget(store, context, tokens)
        #vv = [v for v in values[0] if v is not None]
        #assert vv == [1, 1, 3, 0, 1, 5]

        #tokens = 'maxSeries(a.b.c, d.e.f)'
        #values = evaluator.evaluateTarget(store, context, tokens)
        #vv = [v for v in values[0] if v is not None]
        #assert vv == [2, 2, 3, 4, 6, 7]

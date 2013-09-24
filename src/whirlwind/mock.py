import time
from datetime import datetime
from fnmatch import fnmatch

from attime import parseATTime
from perlin import SimplexNoise
from store import AbstractStore
from datalib import TimeSeries
from node import LeafNode
from intervals import Interval, IntervalSet


def magic_time(stuff):
    if type(stuff) == datetime:
        return time.mktime(stuff.timetuple())
    elif type(stuff) == str:
        return time.mktime(parseATTime(stuff).timetuple())
    elif type(stuff) == int:
        return stuff
    raise Exception("Bad argument type")


class MockFinder(object):

    def __init__(self, datas):
        self.datas = datas

    def find_nodes(self, query):
        for path, data in self.datas.items():
            if fnmatch(path, query.pattern):
                yield LeafNode(path, data)


class MockReader(object):

    def __init__(self, step=30):
        self.step = step

    def get_intervals(self):
        start = 0
        end = int(time.time())
        return IntervalSet([Interval(start, end)])

    def fetch(self, startTime, endTime):
        # timeInfos = start, end, step
        # return timeInfos, values
        pass


class MockNoiseReader(MockReader):

    def fetch(self, startTime, endTime=None):
        now = int(time.time())
        if endTime is None:
            endTime = now
        else:
            endTime = magic_time(endTime)
        startTime = magic_time(startTime)
        delta = int(endTime) - int(startTime)

        tick = delta / self.step
        noise = SimplexNoise(1024)
        noise.randomize()
        timeInfos = startTime, endTime, self.step
        return timeInfos, [noise.noise2(1, a) for a in range(tick)]


class MockStoreNoise(AbstractStore):

    def fetch(self, pathExpr, startTime, endTime=None, step=30):
        now = int(time.time())
        if endTime is None:
            endTime = now
        else:
            endTime = magic_time(endTime)
        startTime = magic_time(startTime)
        delta = int(endTime) - int(startTime)

        tick = delta / step
        noise = SimplexNoise(1024)
        noise.randomize()
        series = TimeSeries(pathExpr,
                          startTime, endTime,
                          step,
                          [noise.noise2(1, a) for a in range(tick)])
        series.pathExpression = pathExpr  # hack to pass expressions through to render functions
        return [series]


class MockStoreStatic(AbstractStore):
    """ Last part of the pathExpr is the returned value.
    """

    def fetch(self, pathExpr, startTime, endTime=None, step=30):
        now = int(time.time())
        if endTime is None:
            endTime = now
        else:
            endTime = time.mktime(parseATTime(endTime).timetuple())
        startTime = time.mktime(parseATTime(startTime).timetuple())
        delta = int(endTime) - int(startTime)

        tick = delta / step
        v = float(pathExpr.split('.')[-1])
        series = TimeSeries(pathExpr,
                          startTime, endTime,
                          step,
                          [v for a in range(tick)])
        series.pathExpression = pathExpr  # hack to pass expressions through to render functions
        return [series]


class MockStore(AbstractStore):

    def __init__(self, store):
        self.store = store

    def fetch(self, pathExpr, startTime, endTime=None, step=30):
        now = int(time.time())
        if endTime is None:
            endTime = now
        else:
            endTime = time.mktime(parseATTime(endTime).timetuple())
        startTime = time.mktime(parseATTime(startTime).timetuple())
        delta = int(endTime) - int(startTime)

        tick = delta / step
        s = self.store[pathExpr]
        v = s + [None for a in range(tick - len(s))]
        series = TimeSeries(pathExpr,
                          startTime, endTime,
                          step,
                          v)
        series.pathExpression = pathExpr  # hack to pass expressions through to render functions
        return [series]


if __name__ == '__main__':
    m = MockStore()
    print(m.fetch('test', '-1day', 'now', 30))

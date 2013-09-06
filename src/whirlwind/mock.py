import time
from datetime import datetime

from attime import parseATTime
from perlin import SimplexNoise
from store import AbstractStore
from datalib import TimeSeries


def magic_time(stuff):
    if type(stuff) == datetime:
        return time.mktime(stuff.timetuple())
    elif type(stuff) == str:
        return time.mktime(parseATTime(stuff).timetuple())
    elif type(stuff) == int:
        return stuff
    raise Exception("Bad argument type")


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

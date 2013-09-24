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
    elif type(stuff) == float:
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

class MockStaticReader(MockReader):

    def __init__(self, value=1, step=30):
        self.step = step
        self.value = value

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
        return timeInfos, [self.value for i in range(tick)]


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


if __name__ == '__main__':
    m = MockStore()
    print(m.fetch('test', '-1day', 'now', 30))

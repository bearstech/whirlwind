import time
from datetime import datetime

from attime import parseATTime
from perlin import SimplexNoise
from store import AbstractStore


class MockStore(AbstractStore):

    def fetch(self, _, startTime, endTime=None, step=30):
        now = int(time.time())
        if endTime is None:
            endTime = now
        else:
            endTime = time.mktime(parseATTime(endTime).timetuple())
        startTime = time.mktime(parseATTime(startTime).timetuple())
        delta = int(endTime) - int(startTime)

        tick = delta / step
        noise = SimplexNoise(1024)
        noise.randomize()
        return ((startTime, endTime, step),
                [noise.noise2(1, a) for a in range(tick)])


if __name__ == '__main__':
    m = MockStore()
    print(m.fetch('test', '-1day', 'now', 30))

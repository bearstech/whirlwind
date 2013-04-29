import time
import struct
import os.path
import os

import whisper
from redis import StrictRedis as Redis

from whirlwind import target_to_path

METRICS = 'metrics'
PERIOD = 30
METRIC_WRITE = 'carbon.write'
METRIC_POINTS = 'carbon.points'


class Persist(object):
    """ Sequential writer for Carbon server.
    The story is simple, fetch data from redis, write them, wait, loop.
    This code is supervised by Carbon daemon.
    """

    def __init__(self, path="/tmp/"):
        self.redis = Redis()
        self.path = path
        self.dirs = set()
        self.redis.sadd(METRICS, METRIC_POINTS, METRIC_WRITE)

    def metric(self, name, value):
        "Add some metrics : make your own dogfood, just before lunch."
        timestamp = time.time()
        serialized = struct.pack('!ff', timestamp, value)
        pipe = self.redis.pipeline()
        pipe.zadd(name, timestamp, serialized)
        pipe.publish(name, serialized)
        pipe.execute()

    def run(self):
        while True:
            before = time.time()
            self.handle()
            after = time.time()
            self.metric(METRIC_WRITE, (after - before) * 1000)
            time.sleep(PERIOD - int(before) + int(after))

    def handle(self):
        points = 0
        for metric in self.redis.smembers(METRICS):
            values = self.redis.zrange(metric, 0, -1)
            points += len(values)
            f = target_to_path(self.path, metric)
            d = os.path.dirname(f)
            if d not in self.dirs:
                if not os.path.isdir(d):
                    os.makedirs(d)
                self.dirs.add(d)
            if not os.path.exists(f):
                whisper.create(f, [(10, 1000)])  # [FIXME] hardcoded values
            whisper.update_many(f, [struct.unpack('!ff', a) for a in values])
            if len(values):
                self.redis.zrem(metric, *values)
        self.metric(METRIC_POINTS, points)

if __name__ == "__main__":
    p = Persist()
    p.run()

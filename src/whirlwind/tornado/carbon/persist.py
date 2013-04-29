import time
import struct
import os.path
import os

import whisper
from redis import Redis

from whirlwind import target_to_path

METRICS = 'metrics'
PERIOD = 30


class Persist(object):

    def __init__(self, path="/tmp/"):
        self.redis = Redis()
        self.path = path
        self.dirs = set()

    def run(self):
        while True:
            tick = int(time.time())
            self.handle()
            time.sleep(PERIOD - tick + int(time.time()))

    def handle(self):
        for metric in self.redis.smembers(METRICS):
            values = self.redis.zrange(metric, 0, -1)
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

if __name__ == "__main__":
    p = Persist()
    p.run()

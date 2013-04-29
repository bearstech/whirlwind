import time

import whisper
from redis import Redis

METRICS = 'metrics'
PERIOD = 30


class Persist(object):

    def __init__(self):
        self.redis = Redis()

    def run(self):
        while True:
            tick = int(time.time())
            self.handle()
            time.sleep(PERIOD - tick + int(time.time()))

    def handle(self):
        for metric in self.redis.smembers(METRICS):
            values = self.redis.zrange(metric, 0, -1)
            print metric, values  # persist here
            if len(values):
                self.redis.zrem(metric, *values)

if __name__ == "__main__":
    p = Persist()
    p.run()

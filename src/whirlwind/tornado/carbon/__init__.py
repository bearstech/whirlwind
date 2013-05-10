import struct

from tornado.tcpserver import TCPServer
from tornado.gen import coroutine, Task
from tornado.process import Subprocess
import tornadoredis


def parse(line):
    metric, value, timestamp = line.strip().split()
    return metric, float(timestamp), float(value)


class Carbon(TCPServer):
    """Carbon daemon.
    Listen the simple socket carbon protocol and feed the redis,
    later, some writes will happens.
    """

    def __init__(self, persist=True):
        super(Carbon, self).__init__()
        self.metrics = set()
        self.redis = tornadoredis.Client()  # Maybe some parameters
        self.redis.connect()
        if persist:
            self.persist = Subprocess(["python", "-m",
                                       "whirlwind.tornado.carbon.persist"])
            # [TODO] handle crash and restarting.

    @coroutine
    def handle_stream(self, stream, address):
        while True:
            line = yield Task(stream.read_until, "\n")
            try:
                metric, timestamp, value = parse(line)
            except Exception:
                stream.close()
            serialized = struct.pack('!ff', timestamp, value)
            pipe = self.redis.pipeline()
            if metric not in self.metrics:
                pipe.sadd('metrics', metric)
                self.metrics.add(metric)
            pipe.zadd(metric, timestamp, serialized)
            pipe.publish(metric, serialized)
            yield Task(pipe.execute)

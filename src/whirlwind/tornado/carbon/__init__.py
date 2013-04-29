import struct

from tornado.tcpserver import TCPServer
from tornado.gen import coroutine, Task
import tornadoredis


def parse(line):
    metric, value, timestamp = line.strip().split()
    return metric, float(timestamp), float(value)


class Carbon(TCPServer):

    def __init__(self):
        super(Carbon, self).__init__()
        self.redis = tornadoredis.Client()  # Mayebe some parameters
        self.redis.connect()

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
            pipe.zadd(metric, timestamp, serialized)
            pipe.publish(metric, serialized)
            yield Task(pipe.execute)
            print "hop"


if __name__ == "__main__":
    from tornado.ioloop import IOLoop
    server = Carbon()
    server.listen(8888)
    IOLoop.instance().start()

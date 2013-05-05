import os
from os.path import splitext
from tornado.gen import coroutine, Return, Task

from __init__ import Whisper
from ..metrics import AbstractMetric


class Metrics(AbstractMetric):
    "A folder full of whisper files."

    def __init__(self, path, redis):
        self.path = path
        self.redis = redis

    @coroutine
    def keys(self):
        already = yield Task(self.redis.exists, 'metrics')
        if already:
            members = yield Task(self.redis.smembers, 'metrics')
            raise Return(members)
        keys = []
        for root, dirs, files in os.walk(self.path):
            key = '.'.join(root[len(self.path) + 1:].split('/'))
            for name in files:
                db, ext = splitext(name)
                if ext == ".wsp":
                    kk = '%s.%s' % (key, db)
                    yield Task(self.redis.sadd, 'metrics', kk)
                    keys.append(kk)
        raise Return(keys)

    def get(self, key):
        return Whisper("%s/%s.wsp" % (self.path, "/".join(key.split('.'))))

if __name__ == "__main__":
    from tornado.ioloop import IOLoop
    from tornado.gen import Callback, WaitAll
    import tornadoredis

    @coroutine
    def all_header():
        redis = tornadoredis.Client()  # Maybe some parameters
        redis.connect()
        m = Metrics('/tmp/whisper', redis)
        keys = yield m.keys()
        for k in keys:
            m.get(k)._build_header(callback=(yield Callback(k)))
        w = yield WaitAll(keys)
        print w, len(w)

    @coroutine
    def pattern():
        redis = tornadoredis.Client()  # Maybe some parameters
        redis.connect()
        m = Metrics('/tmp/whisper', redis)
        match = yield m.fetch('servers.*')
        print match
        match = yield m.fetch('*.agents.*')
        print match

    IOLoop.instance().run_sync(pattern)

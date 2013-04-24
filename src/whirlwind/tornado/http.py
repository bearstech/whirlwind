from tornado.web import (
    asynchronous, RequestHandler, Application
)
from tornado.gen import coroutine
from __init__ import Whisper


class RenderHandler(RequestHandler):

    def initialize(self, path):
        self.path = path

    @coroutine
    @asynchronous
    def get(self):
        target = self.get_argument('target')
        path = "%s%s.wsp" % (self.path, "/".join(target.split(".")))
        w = Whisper(path)
        time_info, values = yield w.fetch()
        self.set_status(200)
        self.set_header("Content-Type", "application/json")
        self.set_header("Cache-Control", "no-cache")
        self.write("[")
        for value in values:
            if value is None:
                self.write('0,')
        self.write("]")
        self.finish()
        w.close()


if __name__ == "__main__":
    import tornado.ioloop
    import sys
    path = sys.argv[1]
    application = Application([
        (r"/render", RenderHandler, dict(path=path)),
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

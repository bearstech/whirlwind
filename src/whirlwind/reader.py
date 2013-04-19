import os
from tornado.iostream import BaseIOStream


class ReadOnlyFileStream(BaseIOStream):
    def __init__(self, path):
        super(ReadOnlyFileStream, self).__init__()
        self.file = open(path, 'r')

    def fileno(self):
        return self.file.fileno()

    def close_fd(self):
        self.file.close()

    def read_from_fd(self):
        try:
            chunk = os.read(self.fileno(), self.read_chunk_size)
        except (IOError, OSError):
            return None
        return chunk


if __name__ == "__main__":
    from tornado.ioloop import IOLoop
    from tornado.gen import coroutine, Task

    @coroutine
    def main():
        f = ReadOnlyFileStream('./README.md')
        first = yield Task(f.read_until, "\n")
        deuz = yield Task(f.read_until, "\n")
        f.close()
        print first, deuz

    IOLoop.instance().run_sync(main)

import os
from os.path import splitext


class Metrics(object):
    "A folder full of whisper files."

    def __init__(self, path):
        self.path = path

    def keys(self):
        for root, dirs, files in os.walk(self.path):
            key = '.'.join(root[len(self.path) + 1:].split('/'))
            for name in files:
                db, ext = splitext(name)
                if ext == ".wsp":
                        yield '%s.%s' % (key, db)


if __name__ == "__main__":
    m = Metrics('/tmp/whisper')
    print list(m.keys())

import struct
import functools
from whisper import (
    metadataSize, archiveInfoSize, pointSize,
    archiveInfoFormat, metadataFormat,
    aggregationTypeToMethod,
    CorruptWhisperFile
)
from tornado.gen import coroutine, Task

from reader import ReadOnlyFileStream


class Whisper(ReadOnlyFileStream):
    _header = None

    def header(self, callback=None):
        if not self._header:
            self._build_header(callback=functools.partial(callback, self._header))
        else:
            IOLoop.instance().add_callback(functools.partial(callback, self._header))

    @coroutine
    def _build_header(self):
        packedMetadata = yield Task(self.read_bytes, metadataSize)

        try:
            (aggregationType, maxRetention, xff, archiveCount) = struct.unpack(metadataFormat, packedMetadata)
        except:
            raise CorruptWhisperFile("Unable to read header", self.name)

        archives = []

        for i in xrange(archiveCount):
            packedArchiveInfo = yield Task(self.read_bytes, archiveInfoSize)
            try:
                (offset, secondsPerPoint, points) = struct.unpack(archiveInfoFormat, packedArchiveInfo)
            except:
                raise CorruptWhisperFile(
                    "Unable to read archive%d metadata" % i, self.name)

            archiveInfo = {
                'offset': offset,
                'secondsPerPoint': secondsPerPoint,
                'points': points,
                'retention': secondsPerPoint * points,
                'size': points * pointSize,
            }
            archives.append(archiveInfo)

        self._header = {
            'aggregationMethod': aggregationTypeToMethod.get(
                aggregationType, 'average'),
            'maxRetention': maxRetention,
            'xFilesFactor': xff,
            'archives': archives,
        }


#def fetch(path, fromTime, untilTime=None):
    #w = Whisper(path)
    #w.header()


if __name__ == "__main__":
    import sys
    from tornado.ioloop import IOLoop

    @coroutine
    def main():
        w = Whisper(sys.argv[1])
        yield w._build_header()
        print w._header

    IOLoop.instance().run_sync(main)

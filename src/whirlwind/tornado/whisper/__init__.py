"""
Large part of this code came from whisper.
"""
import struct
import time
from whisper import (
    metadataSize, archiveInfoSize, pointSize,
    archiveInfoFormat, metadataFormat,
    aggregationTypeToMethod,
    CorruptWhisperFile,
    pointFormat,
    InvalidTimeInterval
)
from tornado.gen import coroutine, Task, Return

from ..reader import ReadOnlyFileStream


class Whisper(ReadOnlyFileStream):
    _header = None

    @coroutine
    def _build_header(self):
        if self._header is None:
            packedMetadata = yield Task(self.read_bytes, metadataSize)

            try:
                (aggregationType, maxRetention, xff, archiveCount) = struct.unpack(
                    metadataFormat, packedMetadata)
            except:
                raise CorruptWhisperFile("Unable to read header", self.name)

            archives = []

            for i in xrange(archiveCount):
                packedArchiveInfo = yield Task(self.read_bytes, archiveInfoSize)
                try:
                    (offset, secondsPerPoint, points) = struct.unpack(
                        archiveInfoFormat, packedArchiveInfo)
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
        raise Return(self._header)

    @coroutine
    def fetch(self, fromTime=0, untilTime=None):
        header = yield self._build_header()
        now = int(time.time())
        if untilTime is None:
            untilTime = now
        fromTime = int(fromTime)
        untilTime = int(untilTime)

        # Here we try and be flexible and return as much data as we can.
        # If the range of data is from too far in the past or fully
        # in the future, we return nothing
        if (fromTime > untilTime):
            raise InvalidTimeInterval("Invalid time interval: from time '%s' is after until time '%s'" % (fromTime, untilTime))

        oldestTime = now - header['maxRetention']
        # Range is in the future
        if fromTime > now:
            raise Return(None)
        # Range is beyond retention
        if untilTime < oldestTime:
            raise Return(None)
        # Range requested is partially beyond retention, adjust
        if fromTime < oldestTime:
            fromTime = oldestTime
        # Range is partially in the future, adjust
        if untilTime > now:
            untilTime = now

        diff = now - fromTime
        for archive in header['archives']:
            if archive['retention'] >= diff:
                break

        data = yield self._archive(archive, fromTime, untilTime)
        raise Return(data)

    @coroutine
    def _archive(self, archive, fromTime, untilTime):
        """
        Fetch data from a single archive. Note that checks for validity of
        the time period requested happen above this level so it's possible
        to wrap around the archive on a read and request data older than
        the archive's retention
        """
        fromInterval = int(fromTime - (fromTime % archive['secondsPerPoint'])) + archive['secondsPerPoint']
        untilInterval = int(untilTime - (untilTime % archive['secondsPerPoint'])) + archive['secondsPerPoint']
        yield Task(self.seek, archive['offset'])
        packedPoint = yield Task(self.read_bytes, pointSize)
        (baseInterval, baseValue) = struct.unpack(pointFormat, packedPoint)

        if baseInterval == 0:
            step = archive['secondsPerPoint']
            points = (untilInterval - fromInterval) / step
            timeInfo = (fromInterval, untilInterval, step)
            valueList = [None] * points
            raise Return((timeInfo, valueList))

        #Determine fromOffset
        timeDistance = fromInterval - baseInterval
        pointDistance = timeDistance / archive['secondsPerPoint']
        byteDistance = pointDistance * pointSize
        fromOffset = archive['offset'] + (byteDistance % archive['size'])

        #Determine untilOffset
        timeDistance = untilInterval - baseInterval
        pointDistance = timeDistance / archive['secondsPerPoint']
        byteDistance = pointDistance * pointSize
        untilOffset = archive['offset'] + (byteDistance % archive['size'])

        #Read all the points in the interval
        yield Task(self.seek, fromOffset)
        if fromOffset < untilOffset:  # If we don't wrap around the archive
            seriesString = yield Task(self.read_bytes,
                                      untilOffset - fromOffset)
        else:  # We do wrap around the archive, so we need two reads
            archiveEnd = archive['offset'] + archive['size']
            seriesString = yield Task(self.read_bytes, archiveEnd - fromOffset)
            yield Task(self.seek, archive['offset'])
            seriesString += yield Task(self.read_bytes,
                                       untilOffset - archive['offset'])

        # Now we unpack the series data we just read
        # (anything faster than unpack?)
        byteOrder, pointTypes = pointFormat[0], pointFormat[1:]
        points = len(seriesString) / pointSize
        seriesFormat = byteOrder + (pointTypes * points)
        unpackedSeries = struct.unpack(seriesFormat, seriesString)

        #And finally we construct a list of values (optimize this!)
        valueList = [None] * points  # pre-allocate entire list for speed
        currentInterval = fromInterval
        step = archive['secondsPerPoint']

        for i in xrange(0, len(unpackedSeries), 2):
            pointTime = unpackedSeries[i]
            if pointTime == currentInterval:
                pointValue = unpackedSeries[i + 1]
                # in-place reassignment is faster than append()
                valueList[i / 2] = pointValue
                currentInterval += step

        self.close()
        timeInfo = (fromInterval, untilInterval, step)
        raise Return((timeInfo, valueList))


if __name__ == "__main__":
    import sys
    from tornado.ioloop import IOLoop

    @coroutine
    def main():
        w = Whisper(sys.argv[1])
        a = yield w.fetch()
        print a

    IOLoop.instance().run_sync(main)

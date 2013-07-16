"""Copyright 2008 Orbitz WorldWide

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

import time

from logger import log


class TimeSeries(list):
    def __init__(self, name, start, end, step, values, consolidate='average'):
        self.name = name
        self.start = start
        self.end = end
        self.step = step
        list.__init__(self, values)
        self.consolidationFunc = consolidate
        self.valuesPerPoint = 1
        self.options = {}

    def __iter__(self):
        if self.valuesPerPoint > 1:
            return self.__consolidatingGenerator(list.__iter__(self))
        else:
            return list.__iter__(self)

    def consolidate(self, valuesPerPoint):
        self.valuesPerPoint = int(valuesPerPoint)

    def __consolidatingGenerator(self, gen):
        buf = []
        for x in gen:
            buf.append(x)
            if len(buf) == self.valuesPerPoint:
                while None in buf:
                    buf.remove(None)
                if buf:
                    yield self.__consolidate(buf)
                    buf = []
                else:
                    yield None
        while None in buf:
            buf.remove(None)
        if buf:
            yield self.__consolidate(buf)
        else:
            yield None
        raise StopIteration

    def __consolidate(self, values):
        usable = [v for v in values if v is not None]
        if not usable:
            return None
        if self.consolidationFunc == 'sum':
            return sum(usable)
        if self.consolidationFunc == 'average':
            return float(sum(usable)) / len(usable)
        raise Exception, "Invalid consolidation function!"

    def __repr__(self):
        return 'TimeSeries(name=%s, start=%s, end=%s, step=%s)' % (
            self.name, self.start, self.end, self.step)

    def getInfo(self):
        """Pickle-friendly representation of the series"""
        return {
            'name': self.name,
            'start': self.start,
            'end': self.end,
            'step': self.step,
            'values': list(self),
        }


# Utilities

def recv_exactly(conn, num_bytes):
    buf = ''
    while len(buf) < num_bytes:
        data = conn.recv(num_bytes - len(buf))
        if not data:
            raise Exception("Connection lost")
        buf += data

    return buf


# Data retrieval API
def fetchData(requestContext, pathExpr):
    seriesList = []
    startTime = requestContext['startTime']
    endTime = requestContext['endTime']

    if requestContext['localOnly']:
        store = LOCAL_STORE
    else:
        store = STORE

    for dbFile in store.find(pathExpr):
        log.metric_access(dbFile.metric_path)
        dbResults = dbFile.fetch( timestamp(startTime), timestamp(endTime) )
        try:
            cachedResults = CarbonLink.query(dbFile.real_metric)
            results = mergeResults(dbResults, cachedResults)
        except:
            log.exception()
            results = dbResults

        if not results:
            continue

        (timeInfo, values) = results
        (start, end, step) = timeInfo
        series = TimeSeries(dbFile.metric_path, start, end, step, values)
        series.pathExpression = pathExpr  # hack to pass expressions through to render functions
        seriesList.append(series)

    return seriesList


def mergeResults(dbResults, cacheResults):
    cacheResults = list(cacheResults)

    if not dbResults:
        return cacheResults
    elif not cacheResults:
        return dbResults

    (timeInfo, values) = dbResults
    (start, end, step) = timeInfo

    for (timestamp, value) in cacheResults:
        interval = timestamp - (timestamp % step)

        try:
            i = int(interval - start) / step
            values[i] = value
        except:
            pass

    return (timeInfo, values)


def timestamp(datetime):
    "Convert a datetime object into epoch time"
    return time.mktime(datetime.timetuple())

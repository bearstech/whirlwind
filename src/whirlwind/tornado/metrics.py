import fnmatch
import time

from tornado.gen import coroutine, Return, Callback, WaitAll

from ..grammar import grammar
from ..attime import parseATTime


def _deduplicate(entries):
    yielded = set()
    for entry in entries:
        if entry not in yielded:
            yielded.add(entry)
            yield entry


def match_entries(entries, pattern):
    # First we check for pattern variants (ie. {foo,bar}baz = foobaz or barbaz)
    v1, v2 = pattern.find('{'), pattern.find('}')

    if v1 > -1 and v2 > v1:
        variations = pattern[v1 + 1:v2].split(',')
        variants = [pattern[:v1] + v + pattern[v2 + 1:] for v in variations]
        matching = []

        for variant in variants:
            matching.extend(fnmatch.filter(entries, variant))

        return list(_deduplicate(matching))  # remove dupes without changing order

    else:
        matching = fnmatch.filter(entries, pattern)
        matching.sort()
        return matching


def timestamp(datetime):
    "Convert a datetime object into epoch time"
    return time.mktime(datetime.timetuple())


class AbstractMetric(object):

    def keys(self):
        raise NotImplementedError()

    def get(self, key):
        raise NotImplementedError()

    @coroutine
    def filter_keys(self, pattern):
        tokens = grammar.parseString(pattern)[0]
        if not tokens.pathExpression:
            raise NotImplementedError()
        keys = yield self.keys()
        entries = match_entries(keys, tokens.pathExpression)
        raise Return(entries)

    @coroutine
    def fetch(self, pattern, from_='-1d', until='now'):
        keys = yield self.filter_keys(pattern)
        for key in keys:
            mesure = self.get(key)
            mesure.fetch(timestamp(parseATTime(from_)),
                         timestamp(parseATTime(until)),
                         callback=(yield Callback(key)))
        values = yield WaitAll(keys)
        raise Return(values)

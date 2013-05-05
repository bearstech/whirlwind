import fnmatch

from tornado.gen import coroutine, Return, Task

from ..grammar import grammar


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


class AbstractMetric(object):

    def keys(self):
        raise NotImplementedError()

    @coroutine
    def fetch(self, pattern):
        tokens = grammar.parseString(pattern)[0]
        if not tokens.pathExpression:
            raise NotImplementedError()
        keys = yield self.keys()
        m = match_entries(keys, tokens.pathExpression)
        raise Return(m)

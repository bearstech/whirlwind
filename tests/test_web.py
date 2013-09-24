from webtest import TestApp

from whirlwind import web
from whirlwind.mock import MockFinder, MockNoiseReader
from whirlwind.storage import Store


def test_simple():
    mock_reader = MockNoiseReader()
    finder = MockFinder({
        'a.b.c': mock_reader,
        'd.e.f': mock_reader
    })
    store = Store([finder], hosts=None)
    web.app.config.update({
        'store': store
    })
    app = TestApp(web.app)
    resp = app.get('/render?target=a.b.c&target=d.e.f&from=-1day')
    assert resp.status_int == 200
    series = resp.json
    assert len(series) == 2
    for serie in series:
        assert 'target' in serie
        assert 'datapoints' in serie
        assert len(serie['datapoints']) == 2880

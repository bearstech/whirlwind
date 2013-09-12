from webtest import TestApp

from whirlwind import web


def test_simple():
    web.app.config.update({
        'store': 'mock.noise'
    })
    app = TestApp(web.app)
    resp = app.get('/render?target=a.b.c&target=d.e.f&from=-1day')
    print resp.status
    assert resp.status_int == 200
    series = resp.json
    assert len(series) == 2
    for serie in series:
        assert 'target' in serie
        assert 'datapoints' in serie
        assert len(serie['datapoints']) == 2880

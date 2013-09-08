import json

import whisper
from bottle import route, run, request, default_app, Response, get

from __init__ import target_to_path
from attime import parseATTime
from evaluator import evaluateTarget

from whirlwind.mock import MockStore, MockStoreNoise

folder = '/tmp/whisper/'  # sys.argv[1]



@get("/render")
def render():
    if 'from' in request.query:
        fromTime = parseATTime(request.query['from'])
    else:
        fromTime = parseATTime('-1d')
    if 'until' in request.query:
        untilTime = parseATTime(request.query.until)
    else:
        untilTime = parseATTime('now')

    targets = request.query.getall('target')

    if 'format' in request.query:
        format_ = request.query.format
    else:
        format_ = 'json'

    store_name = app.config['store']

    if store_name == 'mock.noise':
        store = MockStoreNoise()

    requestContext = {'startTime': fromTime,
                      'endTime': untilTime,
                      'data': []
                      }

    series = []
    for target in targets:
        series.extend(evaluateTarget(store, requestContext, target))

    if format_ == 'json':
        r = []
        for serie in series:
            r.append({
                "target": serie.name,
                "datapoints": list(serie)
            })
        return json.dumps(r)

app = default_app()

if __name__ == "__main__":
    app.config.update({
        'store': 'mock.noise'
    })
    run(host='localhost', port=5000,
        reloader=True, server="wsgiref", quiet=True)

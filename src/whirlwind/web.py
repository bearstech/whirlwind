import json

from bottle import route, run, request, default_app, response, get

from __init__ import target_to_path
from attime import parseATTime
from evaluator import evaluateTarget
from storage import Store

from whirlwind.mock import MockFinder, MockNoiseReader

folder = '/tmp/whisper/'  # sys.argv[1]


def format_raw(datas):
    pass


def format_json(datas):
    pass


def format_csv(datas):
    pass


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

    store = app.config['store']

    requestContext = {'startTime': fromTime,
                      'endTime': untilTime,
                      'data': [],
                      'localOnly': True
                      }

    data = []
    for target in targets:
        if not target.strip():
            continue
        data.extend(evaluateTarget(store, requestContext, target))

    if format_ == 'json':
        series_data = []
        for series in data:
            timestamps = range(int(series.start),
                               int(series.end), int(series.step))
            datapoints = zip(series, timestamps)
            series_data.append(dict(target=series.name, datapoints=datapoints))
        response.content_type = "application/json"
        return json.dumps(series_data)

app = default_app()

if __name__ == "__main__":
    mock_reader = MockNoiseReader()
    finder = MockFinder({'a.b.c': mock_reader})
    store = Store([finder], hosts=None)
    app.config.update({
        'store': store
    })
    run(host='localhost', port=5000,
        reloader=True, server="wsgiref", quiet=True)

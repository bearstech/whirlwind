import sys

import whisper
from bottle import route, run, request, default_app

from __init__ import target_to_path
from attime import parseATTime
from mock import whisper_get

folder = '/tmp/whisper/'  # sys.argv[1]


@route("/render")
def render():
    if 'from' in request.query:
        fromTime = parseATTime(request.query['from'])
    else:
        fromTime = parseATTime('-1d')
    if 'until' in request.query:
        untilTime = parseATTime(request.query.until)
    else:
        untilTime = parseATTime('now')


    target = request.query.target
    if target.split('.')[0] == 'mock':
        timeinfo, values = whisper_get(fromTime, untilTime, 30)
    else:
        path = target_to_path(folder, target)
        timeinfo, values = whisper.fetch(path, fromTime, untilTime)

    return dict(values=values)

app = default_app()

if __name__ == "__main__":
    run(host='localhost', port=5000, reloader=True, server="wsgiref", quiet=True)

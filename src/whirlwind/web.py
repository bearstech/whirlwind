import sys

import whisper
from bottle import route, run, request

from __init__ import target_to_path

folder = '/tmp/whisper/'  # sys.argv[1]


@route("/render")
def hello():
    target = request.query.target
    path = target_to_path(folder, target)
    timeinfo, values = whisper.fetch(path, 0, None)

    return dict(values=values)

app = bottle.default_app()

if __name__ == "__main__":
    run(host='localhost', port=5000, reloader=True, server="wsgiref", quiet=True)

import time
from datetime import datetime

from attime import parseATTime
from perlin import SimplexNoise


def whisper_get(fromTime, untilTime=None, step=30):
    now = int(time.time())
    if untilTime is None:
        untilTime = now
    else:
        untilTime = time.mktime(parseATTime(untilTime).timetuple())
    fromTime = time.mktime(parseATTime(fromTime).timetuple())
    delta = int(untilTime) - int(fromTime)

    tick = delta / step
    noise = SimplexNoise(1024)
    noise.randomize()
    return ((fromTime, untilTime, step),
            [noise.noise2(1, a) for a in range(tick)])


if __name__ == '__main__':
    now = int(time.time())
    age = 3600 * 24  # one day
    print(whisper_get(now - age, now, 30))

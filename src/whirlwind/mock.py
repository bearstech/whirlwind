import time

from perlin import SimplexNoise


def whisper_get(fromTime, untilTime=None, step=30):
    now = int(time.time())
    if untilTime is None:
        untilTime = now
    delta = untilTime - fromTime
    tick = delta / step
    noise = SimplexNoise()
    noise.randomize()
    return ((fromTime, untilTime, step),
            [noise.noise2(1, a) for a in range(tick)])


if __name__ == '__main__':
    print(whisper_get(0, 3600, 30))

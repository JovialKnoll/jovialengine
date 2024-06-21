import random
import math
from datetime import datetime


def clamp(number, minimum, maximum):
    return max(minimum, min(maximum, number))


def get_int_movement(tracking, vel, dt):
    tracking += vel * dt
    tracking_int = int(tracking)
    tracking -= tracking_int
    return tracking, tracking_int


def reduce_number(number, divisor):
    result = number // divisor
    mod = number % divisor
    if random.random() < (mod / divisor):
        result += 1
    return result


def sin_curve(number: float | int):
    return math.sin(number * math.pi / 2)


def cos_curve(number: float | int):
    if number == 1:
        return 0
    return math.cos(number * math.pi / 2)


def binary(start, end, mix):
    if mix < 1.0:
        return start
    return end


def lerp(start, end, mix):
    return start + (end - start)*mix


def inc_speed_lerp(start, end, mix):
    return lerp(start, end, mix**2)


def dec_speed_lerp(start, end, mix):
    return lerp(start, end, 1 - (1 - mix)**2)


def inc_dec_speed_lerp(start, end, mix):
    midpoint = lerp(start, end, 0.5)
    if mix < 0.5:
        return inc_speed_lerp(start, midpoint, mix * 2)
    else:
        return dec_speed_lerp(midpoint, end, (mix - 0.5) * 2)


def dec_inc_speed_lerp(start, end, mix):
    midpoint = lerp(start, end, 0.5)
    if mix < 0.5:
        return dec_speed_lerp(start, midpoint, mix * 2)
    else:
        return inc_speed_lerp(midpoint, end, (mix - 0.5) * 2)


def get_datetime_file_name():
    return datetime.utcnow().isoformat().replace(':', '')

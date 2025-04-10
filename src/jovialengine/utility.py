import random
import math
import datetime

import pygame


def get_int_movement(tracking: float, vel: float, dt: int):
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


def sin_curve(number: float):
    return math.sin(number * math.pi / 2)


def cos_curve(number: float):
    if number == 1:
        return 0
    return math.cos(number * math.pi / 2)


def get_positional_channel_mix(pos: pygame.typing.Point, camera: pygame.FRect):
    lr_pos = pygame.math.clamp((pos[0] - camera.left) / camera.width, 0, 1)
    # currently doesn't start to get quieter as sprites get further off-screen to left or right (or up or down)
    # possibly should
    channel_l = _bound_channel_volume(cos_curve(lr_pos))
    channel_r = _bound_channel_volume(sin_curve(lr_pos))
    return channel_l, channel_r


def _bound_channel_volume(volume: float):
    return .2 + (volume * .8)


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
    return datetime.datetime.now(datetime.UTC).isoformat().replace(':', '')

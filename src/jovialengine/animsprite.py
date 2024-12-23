from collections import deque
from collections.abc import Callable

import pygame

from .saveable import Saveable
from .gamesprite import GameSprite
from . import utility


class Anim(Saveable):
    __slots__ = (
        'func',
        'time',
        'pos',
        'sound',
        'positional_sound',
        'callback',
    )

    def __init__(self, func: str, time: int, pos: pygame.typing.Point,
                 sound: pygame.mixer.Sound = None, positional_sound: bool = False,
                 callback: Callable[[], None] = None):
        self.func = func
        self.time = time
        self.pos = pygame.math.Vector2(pos)
        self.sound = sound
        self.positional_sound = positional_sound
        self.callback = callback

    def save(self):
        # no sound right now, sorry
        # if we need it, either start passing sounds as paths
        # or don't save when there are pending Anims
        return self.func, self.time, self.pos

    @classmethod
    def load(cls, save_data):
        return Anim(*save_data)


class AnimSprite(GameSprite):
    BINARY = 'Binary'
    LERP = 'LERP'
    INC_SPEED = 'INC'
    DEC_SPEED = 'DEC'
    INC_DEC_SPEED = 'INC_DEC'
    DEC_INC_SPEED = 'DEC_INC'
    _FUNCTIONS = {
        BINARY: utility.binary,
        LERP: utility.lerp,
        INC_SPEED: utility.inc_speed_lerp,
        DEC_SPEED: utility.dec_speed_lerp,
        INC_DEC_SPEED: utility.inc_dec_speed_lerp,
        DEC_INC_SPEED: utility.dec_inc_speed_lerp,
    }

    @classmethod
    def to_func(cls, func):
        return cls._FUNCTIONS.get(func, utility.lerp)

    __slots__ = (
        'anims',
        'last_pos',
        'time',
        'positional_sound',
        'sound_channel',
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anims = deque()
        self.last_pos = None
        self.time = 0
        self.positional_sound = False
        self.sound_channel = None

    def save(self):
        return {
            'rect_topleft': self.rect.topleft,
            'seq': self.seq,
            'mask_seq': self.mask_seq,
            'anims': self.anims,
            'last_pos': self.last_pos,
            'time': self.time,
        }

    @classmethod
    def load(cls, save_data):
        new_obj = AnimSprite(topleft=save_data['rect_topleft'])
        if new_obj.seq is not None:
            new_obj.seq = save_data['seq']
        if new_obj.mask_seq is not None:
            new_obj.mask_seq = save_data['mask_seq']
        new_obj.anims = save_data['anims']
        new_obj.last_pos = save_data['last_pos']
        new_obj.time = save_data['time']
        return new_obj

    def still_animating(self):
        if self.anims:
            return True
        return False

    def update(self, dt: int, camera: pygame.FRect):
        if self.last_pos is None:
            self.last_pos = self.rect.center
        # adding dt
        self.time += dt
        while self.anims and self.time >= self.anims[0].time:
            done_anim = self.anims.popleft()
            self.time -= done_anim.time
            self.rect.center = done_anim.pos
            self.last_pos = self.rect.center
            if done_anim.sound:
                self.positional_sound = done_anim.positional_sound
                channel = done_anim.sound.play()
                if self.positional_sound:
                    self.sound_channel = channel
            if done_anim.callback:
                done_anim.callback()
        if self.anims:
            current_anim = self.anims[0]
            func = self.to_func(current_anim.func)
            self.rect.center = func(
                self.last_pos,
                current_anim.pos,
                self.time / current_anim.time
            )
        else:
            self.last_pos = None
            self.time = 0
        if self.positional_sound:
            if self.sound_channel.get_busy():
                channel_l, channel_r = utility.get_positional_channel_mix(self.rect.center, camera)
                self.sound_channel.set_volume(channel_l, channel_r)
            else:
                self.positional_sound = False
                self.sound_channel = None

    def add_pos_abs(self, func: str, time: int, pos: pygame.typing.Point,
                    sound: pygame.mixer.Sound = None, positional_sound: bool = False,
                    callback: Callable[[], None] = None):
        self.anims.append(
            Anim(func, time, pos, sound, positional_sound, callback)
        )

    def add_pos_rel(self, func: str, time: int, pos: pygame.typing.Point,
                    sound: pygame.mixer.Sound = None, positional_sound: bool = False,
                    callback: Callable[[], None] = None):
        new_pos = pygame.math.Vector2(pos)
        if self.anims:
            new_pos += self.anims[-1].pos
        else:
            new_pos += self.rect.center
        self.add_pos_abs(func, time, new_pos, sound=sound, positional_sound=positional_sound, callback=callback)

    def add_wait(self, time: int,
                 sound: pygame.mixer.Sound = None, positional_sound: bool = False,
                 callback: Callable[[], None] = None):
        self.add_pos_rel(AnimSprite.BINARY, time, (0, 0), sound, positional_sound, callback)

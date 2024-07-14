import abc
from typing import final, Sequence

import pygame

from . import load
from . import game
from .saveable import Saveable
from .modebase import ModeBase


class GameSprite(pygame.sprite.DirtySprite, Saveable, abc.ABC):
    """Base class for many game objects.
    Subclasses should set up image, rect, and optionally source_rect.
    (will maybe make a standard way of handling source_rect animation stuff, later)
    """
    _IMAGE_LOCATION: str = None
    _ALPHA_OR_COLORKEY = False

    __slots__ = (
        'pos',
    )

    def __init__(self, pos: Sequence[float] = (0, 0)):
        if not self._IMAGE_LOCATION:
            raise NotImplementedError(
                "_IMAGE_LOCATION must be overridden in children of GameSprite"
            )
        super().__init__()
        self.dirty = 2  # always draw
        self.pos = pygame.math.Vector2(pos)
        self.image = load.image(self._IMAGE_LOCATION, self._ALPHA_OR_COLORKEY)
        self.rect = self.image.get_rect()

    def save(self):
        return {
            'rect_topleft': self.rect.topleft,
            'source_rect': self.source_rect,
            'pos': (self.pos.x, self.pos.y),
        }

    @classmethod
    def load(cls, save_data):
        new_obj = cls()
        new_obj.rect.topleft = save_data['rect_topleft']
        new_obj.source_rect = save_data['source_rect']
        new_obj.pos = pygame.math.Vector2(save_data['pos'])
        return new_obj

    def start(self, mode: ModeBase | None = None):
        """Function to start processing the GameSprite as part of running the game.
        Should usually be called after creating the GameSprite.
        Adds the sprite to appropriate groups in the current game mode or the mode indicated.
        Sprites created within a mode's __init__ should probably have that mode passed into this method.
        """
        if mode is None:
            mode = game.get_game().current_mode
        sprite_groups = mode.get_sprite_groups()
        sprite_groups["all"].add(self)
        return self

    @final
    def update(self, *args):
        self._update(args[0])
        self.rect.center = self.pos

    def _update(self, dt: int):
        pass

from typing import final

import pygame

from . import game
from .saveable import Saveable
from .modebase import ModeBase


class GameSprite(pygame.sprite.DirtySprite, Saveable):
    """Base class for many game objects.
    Subclasses should set up image, rect, and optionally source_rect.
    (will maybe make a standard way of handling source_rect animation stuff, later)
    """
    __slots__ = (
        'pos',
    )

    def __init__(self):
        super().__init__()
        self.dirty = 2  # always draw
        self.pos = pygame.math.Vector2()

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
        mode.start_sprite(self)
        return self

    @final
    def update(self, *args):
        self._update(args[0])
        self.rect.center = self.pos

    def _update(self, dt: int):
        pass

import abc
from typing import final, Sequence

import pygame

from . import load
from . import game
from .saveable import Saveable
from .modebase import ModeBase


class GameSprite(pygame.sprite.DirtySprite, Saveable, abc.ABC):
    """Base class for many game objects.
    Subclasses should set:
    required: _IMAGE_LOCATION, location of image file
    required: _ALPHA_OR_COLORKEY, used for loading image
    optional: _IMAGE_SECTION_SIZE, used if only displaying subset of image for sprite animation
    """
    _IMAGE_LOCATION: str = None
    _ALPHA_OR_COLORKEY: bool | tuple[int, int, int] = None
    _IMAGE_SECTION_SIZE: tuple[int, int] = None

    __slots__ = (
        'pos',
        '_seq',
        '_image_count_x',
        '_image_count_y',
    )

    def __init__(self, pos: Sequence[float] = (0, 0)):
        if not self._IMAGE_LOCATION:
            raise NotImplementedError(
                "_IMAGE_LOCATION must be overridden in children of GameSprite"
            )
        if not self._ALPHA_OR_COLORKEY:
            raise NotImplementedError(
                "_ALPHA_OR_COLORKEY must be overridden in children of GameSprite"
            )
        super().__init__()
        self.dirty = 2  # always draw
        self.pos = pygame.math.Vector2(pos)
        self.image = load.image(self._IMAGE_LOCATION, self._ALPHA_OR_COLORKEY)
        if self._IMAGE_SECTION_SIZE:
            self.source_rect = pygame.rect.Rect((0, 0), self._IMAGE_SECTION_SIZE)
            self.rect = pygame.rect.Rect((0, 0), self._IMAGE_SECTION_SIZE)
            self._seq: int | None = 0
            image_size = self.image.get_size()
            self._image_count_x = image_size[0] // self._IMAGE_SECTION_SIZE[0]
            self._image_count_y = image_size[1] // self._IMAGE_SECTION_SIZE[1]
        else:
            self.rect = self.image.get_rect()
            self._seq: int | None = None
        self.rect.center = self.pos

    def save(self):
        return {
            'rect_center': self.rect.center,
            'source_rect': self.source_rect,
            'pos': (self.pos.x, self.pos.y),
            '_seq': self._seq,
        }

    @classmethod
    def load(cls, save_data):
        new_obj = cls()
        new_obj.rect.topleft = save_data['rect_topleft']
        new_obj.source_rect = save_data['source_rect']
        new_obj.pos = pygame.math.Vector2(save_data['pos'])
        new_obj._seq = save_data['_seq']
        return new_obj

    @final
    @property
    def seq(self):
        """Get the sprite sequence.
        Set this value to change to a different part of the sprite sheet."""
        return self._seq

    @final
    @seq.setter
    def seq(self, value: int):
        if self._seq is None:
            raise RuntimeError("error: setting seq for GameSprite not using a sprite sheet")
        self._seq = value % (self._image_count_x * self._image_count_y)
        self.source_rect.x = (self._seq % self._image_count_x) * self._IMAGE_SECTION_SIZE[0]
        self.source_rect.y = (self._seq // self._image_count_x) * self._IMAGE_SECTION_SIZE[1]

    @final
    def start(self, mode: ModeBase | None = None):
        """Function to start processing the GameSprite as part of running the game.
        Should usually be called after creating the GameSprite.
        Adds the sprite to appropriate groups in the current game mode or the mode indicated.
        Sprites created within a mode's __init__ should probably have that mode passed into this method.
        """
        if mode is None:
            mode = game.get_current_mode()
        mode.sprite_groups["all"].add(self)
        self._create()
        return self

    @final
    def update(self, *args):
        self._update(args[0])
        self.rect.center = self.pos

    def _create(self):
        """Called when a GameSprite is started."""
        pass

    def _update(self, dt: int):
        """Called to apply time updates to a GameSprite"""
        pass

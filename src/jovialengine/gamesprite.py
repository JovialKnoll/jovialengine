import abc
from functools import cache
from typing import final, Sequence, Self

import pygame

from . import load
from . import game
from .saveable import Saveable
from .modebase import ModeBase
from .inputframe import InputFrame, StateChange


class GameSprite(pygame.sprite.DirtySprite, Saveable, abc.ABC):
    """Base class for many game objects.
    Subclasses should set:
    required: _IMAGE_LOCATION, location of image file
    required: _ALPHA_OR_COLORKEY, used for loading image
    optional: _IMAGE_SECTION_SIZE, used if only displaying subset of image for sprite animation
    optional: _COLLISION_RADIUS, set this if a circle collision is appropriate for this sprite
    optional: _COLLISION_MASK_LOCATION, location of image file for generating a collision mask
    optional: _COLLISION_MASK_ALPHA_OR_COLORKEY, alpha_or_colorkey for generating a collision mask
    optional: _GETS_INPUT, set this true to force this sprite to receive input

    To hook in to collision checking, create a function like so:
    def collide_OtherGameSpriteClassName(self, other: OtherGameSpriteClassName):
        do_something()
    collide_OtherGameSpriteClassName will be called whenever there is a collision with a OtherGameSpriteClassName
    Other will be the GameSprite collided with.
    """
    _IMAGE_LOCATION: str = None
    _ALPHA_OR_COLORKEY: bool | tuple[int, int, int] = None
    _IMAGE_SECTION_SIZE: tuple[int, int] | None = None
    _COLLISION_RADIUS: float | None = None
    _COLLISION_MASK_LOCATION: str | None = None
    _COLLISION_MASK_ALPHA_OR_COLORKEY: bool | tuple[int, int, int] | None = None
    _GETS_INPUT: bool = False

    __slots__ = (
        '_input_frame',
        '_image_count_x',
        '_image_count_y',
        '_seq',
        '_mask_source_rect',
        '_mask_image_count_x',
        '_mask_image_count_y',
        '_mask_seq',
        '_pos',
    )

    def __init__(self, pos: Sequence[float] = (0, 0)):
        if not self._IMAGE_LOCATION:
            raise RuntimeError(
                "_IMAGE_LOCATION must be overridden in children of GameSprite"
            )
        if not self._ALPHA_OR_COLORKEY:
            raise RuntimeError(
                "_ALPHA_OR_COLORKEY must be overridden in children of GameSprite"
            )
        if self._COLLISION_MASK_LOCATION and not self._COLLISION_MASK_ALPHA_OR_COLORKEY:
            raise RuntimeError(
                "if _COLLISION_MASK_LOCATION is overridden, _COLLISION_MASK_ALPHA_OR_COLORKEY must also be overridden"
            )
        super().__init__()
        self._input_frame: InputFrame | None = None
        self._seq: int | None = None
        self.dirty = 2  # always draw
        self.image = load.image(self._IMAGE_LOCATION, self._ALPHA_OR_COLORKEY)
        self._image_count_x: int | None = None
        self._image_count_y: int | None = None
        if self._IMAGE_SECTION_SIZE:
            self.rect = pygame.rect.Rect((0, 0), self._IMAGE_SECTION_SIZE)
            self.source_rect = pygame.rect.Rect((0, 0), self._IMAGE_SECTION_SIZE)
            self._seq = 0
            image_size = self.image.get_size()
            self._image_count_x = image_size[0] // self._IMAGE_SECTION_SIZE[0]
            self._image_count_y = image_size[1] // self._IMAGE_SECTION_SIZE[1]
        else:
            self.rect = self.image.get_rect()
        self.radius: float | None = None
        self.mask = load.mask_filled(self.rect.size)
        self._mask_source_rect: pygame.Rect | None = None
        self._mask_seq: int | None = None
        self._mask_image_count_x: int | None = None
        self._mask_image_count_y: int | None = None
        if self._COLLISION_RADIUS:
            self.radius = self._COLLISION_RADIUS
            self.mask = load.mask_circle(self.rect.size, self.radius)
        if self._COLLISION_MASK_LOCATION:
            self._mask_image = load.image(self._COLLISION_MASK_LOCATION, self._COLLISION_MASK_ALPHA_OR_COLORKEY)
            if self.rect.size != self._mask_image.get_size():
                self._mask_source_rect = pygame.rect.Rect((0, 0), self.rect.size)
                self._mask_seq = 0
                mask_image_size = self._mask_image.get_size()
                self._mask_image_count_x = mask_image_size[0] // self.rect.size[0]
                self._mask_image_count_y = mask_image_size[1] // self.rect.size[1]
            self.mask = load.mask_surface(
                self._mask_image,
                self._mask_source_rect and self._mask_source_rect.topleft,
                self._mask_source_rect and self._mask_source_rect.size
            )
        self.pos = pos

    def save(self):
        return {
            '_pos': self._pos,
            '_seq': self._seq,
            '_mask_seq': self._mask_seq,
        }

    @classmethod
    def load(cls, save_data):
        new_obj = cls(save_data['_pos'])
        if new_obj.seq is not None:
            new_obj.seq = save_data['_seq']
        if new_obj.mask_seq is not None:
            new_obj.mask_seq = save_data['_mask_seq']
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
    @property
    def mask_seq(self):
        """Get the sprite sequence.
        Set this value to change to a different part of the sprite sheet."""
        return self._mask_seq

    @final
    @mask_seq.setter
    def mask_seq(self, value: int):
        if self._mask_seq is None:
            raise RuntimeError("error: setting mask_seq for GameSprite not using a sprite sheet")
        self._mask_seq = value % (self._image_count_x * self._image_count_y)
        self._mask_source_rect.x = (self._mask_seq % self._mask_image_count_x) * self.rect.size[0]
        self._mask_source_rect.y = (self._mask_seq // self._mask_image_count_y) * self.rect.size[1]
        self.mask = load.mask_surface(
            self._mask_image,
            self._mask_source_rect and self._mask_source_rect.topleft,
            self._mask_source_rect and self._mask_source_rect.size
        )

    @final
    @property
    def pos(self):
        """Get the sprite position.
        Setting this value updates the rect center, but this can hold floats."""
        return self._pos

    @final
    @pos.setter
    def pos(self, value: Sequence[float]):
        self._pos = pygame.math.Vector2(value)
        self.rect.center = self._pos

    @classmethod
    @final
    @cache
    def get_collision_labels(cls):
        labels = [
            t.__name__
            for t in cls.mro()
            if t not in GameSprite.mro()
        ]
        labels.append('GameSprite')
        return frozenset(labels)

    @classmethod
    @final
    @cache
    def get_collides_with(cls):
        return frozenset([
            e.removeprefix('collide_')
            for e in dir(cls)
            if e.startswith('collide_')
        ])

    @final
    def does_collide(self, other: Self):
        if self.radius and other.radius:
            return pygame.sprite.collide_circle(self, other)
        elif not self.radius and not other.radius \
                and not self._COLLISION_MASK_LOCATION and not other._COLLISION_MASK_LOCATION:
            return pygame.sprite.collide_rect(self, other)
        return pygame.sprite.collide_mask(self, other)

    @final
    def start(self, mode: ModeBase | None = None):
        """Function to start processing the GameSprite as part of running the game.
        Should usually be called after creating the GameSprite.
        Adds the sprite to appropriate groups in the current game mode or the mode indicated.
        Sprites created within a mode's __init__ should probably have that mode passed into this method.
        """
        if mode is None:
            mode = game.get_current_mode()
        mode.sprite_groups['all'].add(self)
        mode.sprite_groups['collide'].add(self)
        if self._GETS_INPUT or self._take_state_change is not GameSprite._take_state_change:
            mode.sprite_groups['input'].add(self)
        self._create(mode)
        return self

    @final
    def input(self, input_frame: InputFrame):
        """Called to pass the current InputFrame to a GameSprite."""
        for state_change in input_frame.state_changes:
            self._take_state_change(state_change)
        self._input_frame = input_frame

    def update(self, dt: int):
        """Called to apply time updates to a GameSprite."""
        pass

    def _create(self, mode: ModeBase):
        """Called when a GameSprite is started."""
        pass

    def _take_state_change(self, state_change: StateChange):
        """Handle input state change (this is called on all state changes if this GameSprite receives input)
        During this method call self._input_frame still holds the old input_frame.
        Overriding this method ensures that the child class will receive input."""
        pass

import abc
from functools import cache
from typing import final, Self

import pygame

from . import load
from . import gamebuilder
from .saveable import Saveable
from .modebase import ModeBase
from .inputframe import InputFrame, StateChange


class GameSprite(pygame.sprite.Sprite, Saveable, abc.ABC):
    """Base class for many game objects.
    Subclasses should set:
    optional: _IMAGE_LOCATION, location of image file (if not set subclass must set image and rect)
    optional: _ALPHA_OR_COLORKEY, used for loading image, required if _IMAGE_LOCATION is set
    optional: _IMAGE_SECTION_SIZE, used if only displaying subset of image for sprite animation
    optional: _COLLISION_RADIUS, set this if a circle collision is appropriate for this sprite
    optional: _COLLISION_MASK_LOCATION, location of image file for generating a collision mask
    optional: _COLLISION_MASK_ALPHA_OR_COLORKEY, used for loading image, required if _COLLISION_MASK_LOCATION is set
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
        '_base_image',
        '_source_rect',
        '_image_count_x',
        '_image_count_y',
        '_seq',
        '_mask_image',
        '_mask_source_rect',
        '_mask_image_count_x',
        '_mask_image_count_y',
        '_mask_seq',
    )

    def __init__(self, **kwargs):
        if self._IMAGE_LOCATION and not self._ALPHA_OR_COLORKEY:
            raise RuntimeError(
                "if _IMAGE_LOCATION is set, _ALPHA_OR_COLORKEY must be set"
            )
        if self._COLLISION_MASK_LOCATION and not self._COLLISION_MASK_ALPHA_OR_COLORKEY:
            raise RuntimeError(
                "if _COLLISION_MASK_LOCATION is set, _COLLISION_MASK_ALPHA_OR_COLORKEY must be set"
            )
        super().__init__()
        self.image = None
        self.rect = None
        self._input_frame: InputFrame | None = None
        self._base_image: pygame.Surface | None = None
        self._image_count_x: int | None = None
        self._image_count_y: int | None = None
        self._seq: int | None = None
        self._source_rect: pygame.Rect | None = None
        if self._IMAGE_LOCATION:
            self._base_image = load.image(self._IMAGE_LOCATION, self._ALPHA_OR_COLORKEY)
            self.image = self._base_image
            if self._IMAGE_SECTION_SIZE:
                image_size = self._base_image.get_size()
                self._image_count_x = image_size[0] // self._IMAGE_SECTION_SIZE[0]
                self._image_count_y = image_size[1] // self._IMAGE_SECTION_SIZE[1]
                self._seq = 0
                self._source_rect = pygame.Rect((0, 0), self._IMAGE_SECTION_SIZE)
                self.image = load.subsurface(self._base_image, tuple(self._source_rect))
            self.rect = self.image.get_frect(**kwargs)
        self.radius: float | None = None
        self._mask_image: pygame.Surface | None = None
        self._mask_image_count_x: int | None = None
        self._mask_image_count_y: int | None = None
        self._mask_seq: int | None = None
        self._mask_source_rect: pygame.Rect | None = None
        if self.image:
            size = self.image.get_size()
            self.mask = load.mask_filled(size)
            if self._COLLISION_RADIUS:
                self.radius = self._COLLISION_RADIUS
                self.mask = load.mask_circle(size, self.radius)
            if self._COLLISION_MASK_LOCATION:
                self._mask_image = load.image(self._COLLISION_MASK_LOCATION, self._COLLISION_MASK_ALPHA_OR_COLORKEY)
                mask_image_size = self._mask_image.get_size()
                if size != mask_image_size:
                    self._mask_image_count_x = mask_image_size[0] // size[0]
                    self._mask_image_count_y = mask_image_size[1] // size[1]
                    self._mask_seq = 0
                    self._mask_source_rect = pygame.Rect((0, 0), size)
                self.mask = load.mask_surface(self._mask_image, self._mask_source_rect and tuple(self._mask_source_rect))

    def save(self):
        return {
            'rect_topleft': self.rect.topleft,
            '_seq': self._seq,
            '_mask_seq': self._mask_seq,
        }

    @classmethod
    def load(cls, save_data):
        new_obj = GameSprite(topleft=save_data['rect_topleft'])
        if new_obj.seq is not None:
            new_obj.seq = save_data['_seq']
        if new_obj.mask_seq is not None:
            new_obj.mask_seq = save_data['_mask_seq']
        return new_obj

    @final
    @property
    def seq(self):
        """Get the image sequence.
        Set this value to change to a different part of the image sheet."""
        return self._seq

    @final
    @seq.setter
    def seq(self, value: int):
        if self._seq is None:
            raise RuntimeError("error: setting seq for GameSprite not using a sprite sheet")
        self._seq = value % (self._image_count_x * self._image_count_y)
        self._source_rect.x = (self._seq % self._image_count_x) * self._IMAGE_SECTION_SIZE[0]
        self._source_rect.y = (self._seq // self._image_count_x) * self._IMAGE_SECTION_SIZE[1]
        self.image = load.subsurface(self._base_image, tuple(self._source_rect))

    @final
    @property
    def mask_seq(self):
        """Get the mask sequence.
        Set this value to change to a different part of the mask sheet."""
        return self._mask_seq

    @final
    @mask_seq.setter
    def mask_seq(self, value: int):
        if self._mask_seq is None:
            raise RuntimeError("error: setting mask_seq for GameSprite not using a sprite sheet")
        size = self.image.get_size()
        self._mask_seq = value % (self._mask_image_count_x * self._mask_image_count_y)
        self._mask_source_rect.x = (self._mask_seq % self._mask_image_count_x) * size[0]
        self._mask_source_rect.y = (self._mask_seq // self._mask_image_count_x) * size[1]
        self.mask = load.mask_surface(self._mask_image, tuple(self._mask_source_rect))

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
            # no rounding since circle collisions doesn't match exact pixels anyway
            dx = self.rect.centerx - other.rect.centerx
            dy = self.rect.centery - other.rect.centery
            ds = dx**2 + dy**2
            return ds <= (self.radius + other.radius)**2
        elif self.radius or other.radius or self._COLLISION_MASK_LOCATION or other._COLLISION_MASK_LOCATION:
            # rounding so that mask collisions reflect apparent (drawn) position of sprites
            dx = round(other.rect.x) - round(self.rect.x)
            dy = round(other.rect.y) - round(self.rect.y)
            return self.mask.overlap(other.mask, (dx, dy))
        else:
            # rounding so that rect collisions reflect apparent (drawn) positions of sprites
            self_rect = self.rect.move_to(topleft=(round(self.rect.x), round(self.rect.y)))
            other_rect = other.rect.move_to(topleft=(round(other.rect.x), round(other.rect.y)))
            return self_rect.colliderect(other_rect)

    @final
    def start(self, mode: ModeBase | None = None):
        """Function to start processing the GameSprite as part of running the game.
        Should usually be called after creating the GameSprite.
        Adds the sprite to appropriate groups in the current game mode or the mode indicated.
        Sprites created within a mode's __init__ should probably have that mode passed into this method.
        """
        if mode is None:
            mode = gamebuilder.get_current_mode()
        mode.sprites_all.add(self)
        mode.sprites_game.add(self)
        if self._GETS_INPUT or self._take_state_change is not GameSprite._take_state_change:
            mode.sprites_input.add(self)
        self._start(mode)
        return self

    @final
    def input(self, input_frame: InputFrame):
        """Called to pass the current InputFrame to a GameSprite."""
        for state_change in input_frame.state_changes:
            self._take_state_change(state_change)
        self._input_frame = input_frame

    def update(self, dt: int, camera: pygame.FRect):
        """Called to apply time updates to a GameSprite."""
        pass

    def draw_dynamic(self, screen: pygame.Surface, offset: pygame.typing.IntPoint):
        """Called to apply dynamic drawing from a GameSprite after normal drawing."""
        pass

    def _start(self, mode: ModeBase):
        """Called when a GameSprite is started."""
        pass

    def _take_state_change(self, state_change: StateChange):
        """Handle input state change (this is called on all state changes if this GameSprite receives input)
        During this method call self._input_frame still holds the old input_frame.
        Overriding this method ensures that the child class will receive input."""
        pass

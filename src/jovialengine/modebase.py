import abc
from typing import final, Sequence
from collections.abc import Iterable

import pygame

from . import display
from .inputframe import InputFrame


class ModeBase(abc.ABC):
    """Base class for all game modes.
    Subclasses should set:
    optional: _SPACE_SIZE, size of the space inside this mode, if not supplied will assume display.screen_size
    optional: _CAMERA_SIZE, size of the camera inside this mode, if not supplied will assume display.screen_size
    optional: _CAMERA_OFFSET, offset for drawing camera view onto screen

    When a subclass wants to pass on to another mode, set self.next_mode.
    Don't create another mode unless you are immediately assigning it to self.next_mode.
    """
    _SPACE_SIZE: tuple[int, int] | None = None
    _CAMERA_SIZE: tuple[int, int] | None = None
    _CAMERA_OFFSET: tuple[int, int] = (0, 0)

    __slots__ = (
        '_space',
        '_background',
        'sprite_groups',
        '_sprite_collisions',
        '_camera',
        '_camera_pos',
        '_input_frame',
        'next_mode',
    )

    def __init__(self):
        self._space = pygame.Surface(self._SPACE_SIZE or display.screen_size).convert()
        self._background = pygame.Surface(self._SPACE_SIZE or display.screen_size).convert()
        self._background.fill((255, 255, 255))
        self.sprite_groups = {
            'all': pygame.sprite.LayeredDirty(),
            'input': pygame.sprite.Group(),
            'collide': pygame.sprite.Group(),
        }
        self._sprite_collisions = dict()
        self._camera = pygame.rect.Rect((0, 0), self._CAMERA_SIZE or display.screen_size)
        self._camera_pos = pygame.math.Vector2(self._camera.center)
        self._input_frame: InputFrame | None = None
        self.next_mode: ModeBase | None = None

    @final
    @property
    def camera_pos(self):
        """Get the camera position.
        Setting this value updates the camera center, but this can hold floats."""
        return self._camera_pos

    @final
    @camera_pos.setter
    def camera_pos(self, value: Sequence[float]):
        self._camera_pos = pygame.math.Vector2(value)
        self._camera.center = self._camera_pos

    @final
    def input(self, events: Iterable[pygame.event.Event], input_frame: InputFrame):
        """All game modes can take in input."""
        for event in events:
            self._take_event(event)
        self._take_frame(input_frame)
        for sprite in self.sprite_groups['input'].sprites():
            sprite.input(input_frame)
        self._input_frame = input_frame

    @final
    def update(self, dt: int):
        """All game modes can update."""
        self._update_pre_sprites(dt)
        for sprite in self.sprite_groups['all'].sprites():
            sprite.update(dt)
        self._sprite_collisions = dict()
        for sprite in self.sprite_groups['collide'].sprites():
            for collide_label in sprite.get_collide_labels():
                if collide_label[0] not in self.sprite_groups:
                    continue
                for other in self.sprite_groups[collide_label[0]].sprites():
                    if self.__does_collide:
                        getattr(sprite, collide_label[1])(other)
        self._update_post_sprites(dt)

    def __does_collide(self, sprite, other):
        sprites = frozenset((sprite, other))
        does_collide = self._sprite_collisions.get(sprites)
        if does_collide is None:
            does_collide = sprite.does_collide(other)
            self._sprite_collisions[sprites] = does_collide
        return does_collide

    @final
    def draw(self, screen: pygame.surface.Surface):
        """All game modes can draw to the screen"""
        self._update_pre_draw(screen)
        self._space.blit(self._background, (0, 0))
        self._draw_pre_sprites(self._space)
        self.sprite_groups['all'].draw(self._space)
        self._draw_post_sprites(self._space)
        screen.blit(self._space, self._CAMERA_OFFSET, self._camera)
        self._draw_post_camera(screen)

    @final
    def cleanup(self):
        """All sprite groups we have in this mode should be emptied here.
        We can't just kill the sprites since we might be reusing them between modes."""
        for sprite_group in self.sprite_groups.values():
            sprite_group.empty()
        self._cleanup()

    def _take_event(self, event: pygame.event.Event):
        """Handle any input that requires looking at pygame events directly, like typing."""
        pass

    def _take_frame(self, input_frame: InputFrame):
        """Handle all other input.
        During this method call self._input_frame still holds the old input_frame."""
        pass

    def _update_pre_sprites(self, dt: int):
        pass

    def _update_post_sprites(self, dt: int):
        pass

    def _update_pre_draw(self, screen: pygame.surface.Surface):
        pass

    def _draw_pre_sprites(self, screen: pygame.surface.Surface):
        pass

    def _draw_post_sprites(self, screen: pygame.surface.Surface):
        pass

    def _draw_post_camera(self, screen: pygame.surface.Surface):
        pass

    def _cleanup(self):
        pass

    @staticmethod
    def _stop_mixer():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.stop()

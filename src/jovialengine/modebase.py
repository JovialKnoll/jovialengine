import abc
from typing import final
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
        'sprites_all',
        'sprites_collide',
        'sprites_input',
        '_camera',
        '_camera_pos',
        '_input_frame',
        'next_mode',
    )

    def __init__(self):
        self._space = pygame.Surface(self._SPACE_SIZE or display.screen_size).convert()
        self._background = pygame.Surface(self._SPACE_SIZE or display.screen_size).convert()
        self._background.fill((0, 0, 0))
        self.sprites_all = pygame.sprite.LayeredUpdates()
        self.sprites_collide = pygame.sprite.Group()
        self.sprites_input = pygame.sprite.Group()
        self._camera = pygame.Rect((0, 0), self._CAMERA_SIZE or display.screen_size)
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
    def camera_pos(self, value: pygame.typing.Point):
        self._camera_pos = pygame.math.Vector2(value)
        self._camera.center = self._camera_pos

    @final
    def input(self, events: Iterable[pygame.event.Event], input_frame: InputFrame):
        """All game modes can take in input."""
        for event in events:
            self._take_event(event)
        self._take_frame(input_frame)
        for sprite in self.sprites_input.sprites():
            sprite.input(input_frame)
        self._input_frame = input_frame

    @final
    def update(self, dt: int):
        """All game modes can update."""
        self._update_pre_sprites(dt)
        for sprite in self.sprites_all.sprites():
            sprite.update(dt, self._camera)
        self.__handle_collisions()
        self._update_post_sprites(dt)

    def __handle_collisions(self):
        collide_events = []
        collide_sprites = self.sprites_collide.sprites()
        for i, sprite0 in enumerate(collide_sprites):
            for j in range(i + 1, len(collide_sprites)):
                sprite1 = collide_sprites[j]
                sprite0_collides = sprite0.get_collides_with() & sprite1.get_collision_labels()
                sprite1_collides = sprite1.get_collides_with() & sprite0.get_collision_labels()
                if (sprite0_collides or sprite1_collides) and sprite0.does_collide(sprite1):
                    for sprite0_collide in sprite0_collides:
                        collide_events.append((getattr(sprite0, 'collide_' + sprite0_collide), sprite1,))
                    for sprite1_collide in sprite1_collides:
                        collide_events.append((getattr(sprite1, 'collide_' + sprite1_collide), sprite0,))
        for collide_event in collide_events:
            collide_event[0](collide_event[1])

    @final
    def draw(self, screen: pygame.Surface):
        """All game modes can draw to the screen"""
        self._update_pre_draw()
        self._space.set_clip(self._camera)
        self._space.blit(self._background, (0, 0))
        self._draw_pre_sprites(self._space)
        self.sprites_all.draw(self._space)
        self._draw_post_sprites(self._space)
        screen.blit(self._space, self._CAMERA_OFFSET, self._camera)
        self._draw_post_camera(screen)

    @final
    def cleanup(self):
        """All sprite groups we have in this mode should be emptied here.
        We can't just kill the sprites since we might be reusing them between modes."""
        for sprites in (self.sprites_all, self.sprites_collide, self.sprites_input):
            sprites.empty()
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

    def _update_pre_draw(self):
        """Handle anything that only needs to happen right before drawing, like updating the camera position."""
        pass

    def _draw_pre_sprites(self, screen: pygame.Surface):
        pass

    def _draw_post_sprites(self, screen: pygame.Surface):
        pass

    def _draw_post_camera(self, screen: pygame.Surface):
        pass

    def _cleanup(self):
        pass

    @staticmethod
    def _stop_mixer():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.stop()

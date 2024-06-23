import abc
from typing import final
from collections.abc import Iterable

import pygame

from .inputframe import InputFrame


class ModeBase(abc.ABC):
    """This is an abstract object for game modes.
    """
    __slots__ = (
        '_space',
        '_background',
        '_all_sprites',
        '_camera',
        '_input_frame',
        'next_mode',
    )

    @abc.abstractmethod
    def __init__(self):
        """Implementation must contain a call to _init passing in the space size before all else."""
        raise NotImplementedError(
            type(self).__name__ + ".__init__(self)"
        )

    def _init(self, space_size: tuple[int, int]):
        self._space = pygame.Surface(space_size).convert()
        self._background = pygame.Surface(space_size).convert()
        self._background.fill((255, 255, 255))
        self._all_sprites = pygame.sprite.LayeredDirty()
        self._camera = pygame.rect.Rect((0, 0), space_size)
        self._input_frame: InputFrame | None = None
        """All game modes must set the next mode when they are done.
        Don't create another mode unless you are immediately assigning it to self.next_mode
        """
        self.next_mode: ModeBase | None = None

    def cleanup(self):
        self._all_sprites.empty()

    def _take_event(self, event: pygame.event.Event):
        """Handle any input that requires looking at pygame events directly, like typing."""
        pass

    def _take_frame(self, input_frame: InputFrame):
        """Handle all other input."""
        pass

    @final
    def input(self, events: Iterable[pygame.event.Event], input_frame: InputFrame):
        """All game modes can take in input."""
        for event in events:
            self._take_event(event)
        self._take_frame(input_frame)
        self._input_frame = input_frame

    def _update(self, dt: int):
        pass

    @final
    def update(self, dt: int):
        """All game modes can update."""
        self._update(dt)
        self._all_sprites.update(dt)

    def _update_pre_draw(self, screen: pygame.surface.Surface):
        pass

    def _draw_pre_sprites(self, screen: pygame.surface.Surface):
        pass

    def _draw_post_sprites(self, screen: pygame.surface.Surface):
        pass

    def _draw_post_camera(self, screen: pygame.surface.Surface):
        pass

    @final
    def draw(self, screen: pygame.surface.Surface):
        """All game modes can draw to the screen"""
        self._update_pre_draw(screen)
        self._space.blit(self._background, (0, 0))
        self._draw_pre_sprites(self._space)
        self._all_sprites.draw(self._space)
        self._draw_post_sprites(self._space)
        screen.blit(self._space, (0, 0), self._camera)
        self._draw_post_camera(screen)

    @staticmethod
    def _stop_mixer():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.stop()

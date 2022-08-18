import abc
from typing import final
from collections.abc import Iterable

import pygame

from .input import Action


class ModeBase(abc.ABC):
    """This is an abstract object for game modes.
    """
    __slots__ = (
        '_space',
        '_background',
        '_all_sprites',
        '_camera',
        'next_mode',
    )

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
        """All game modes must set the next mode when they are done.
        Don't create another mode unless you are immediately assigning it to self.next_mode
        """
        self.next_mode: ModeBase | None = None

    def cleanup(self):
        self._all_sprites.empty()

    @abc.abstractmethod
    def _input(self, action: Action):
        raise NotImplementedError(
            type(self).__name__ + "._input(self, action)"
        )

    def _postInput(self):
        """Handle any input that's checked directly, like joysticks etc."""
        pass

    @final
    def inputActions(self, actions: Iterable[Action]):
        """All game modes can take in actions."""
        for action in actions:
            self._input(action)
        self._postInput()

    def _update(self, dt: int):
        pass

    @final
    def update(self, dt: int):
        """All game modes can update."""
        self._update(dt)
        self._all_sprites.update(dt)

    def _updatePreDraw(self, screen: pygame.surface.Surface):
        pass

    def _drawPreSprites(self, screen: pygame.surface.Surface):
        pass

    def _drawPostSprites(self, screen: pygame.surface.Surface):
        pass

    def _drawPostCamera(self, screen: pygame.surface.Surface):
        pass

    @final
    def draw(self, screen: pygame.surface.Surface):
        """All game modes can draw to the screen"""
        self._updatePreDraw(screen)
        self._space.blit(self._background, (0, 0))
        self._drawPreSprites(self._space)
        self._all_sprites.draw(self._space)
        self._drawPostSprites(self._space)
        screen.blit(self._space, (0, 0), self._camera)
        self._drawPostCamera(screen)

    @staticmethod
    def _stopMixer():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.stop()

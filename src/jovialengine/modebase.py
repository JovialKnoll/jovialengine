import abc
import typing

import pygame

import jovialengine

import constants


class ModeBase(abc.ABC):
    """This is an abstract object for game modes.
    """
    __slots__ = (
        '__pressed_mouse_buttons',
        '_space',
        '_background',
        '_all_sprites',
        '_camera',
        'next_mode',
    )

    def __init__(self):
        """If you want a mode's space to not share dimension with the screen size, call out to init yourself."""
        self.init(constants.SCREEN_SIZE)

    def init(self, space_size: tuple[int, int]):
        self.__pressed_mouse_buttons = dict()
        self._space = pygame.Surface(space_size).convert(jovialengine.shared.display.screen)
        self._background = pygame.Surface(space_size).convert(self._space)
        self._background.fill((255, 255, 255))
        self._all_sprites = pygame.sprite.LayeredDirty()
        self._camera = pygame.rect.Rect((0, 0), constants.SCREEN_SIZE)
        """All game modes must set the next mode when they are done.
        Don't create another mode unless you are immediately assigning it to self.next_mode
        """
        self.next_mode = None

    def cleanup(self):
        self._all_sprites.empty()

    def __trackMouseButton(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.__pressed_mouse_buttons[event.button] = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in self.__pressed_mouse_buttons:
                del self.__pressed_mouse_buttons[event.button]

    def _mouseButtonStatus(self, button: int):
        if button not in self.__pressed_mouse_buttons:
            return False
        return self.__pressed_mouse_buttons[button]

    @abc.abstractmethod
    def _input(self, event: pygame.event.Event):
        raise NotImplementedError(
            type(self).__name__ + "._input(self, event)"
        )

    @typing.final
    def input_events(self, events: typing.Iterable[pygame.event.Event]):
        """All game modes can take in events."""
        for event in events:
            self._input(event)
            self.__trackMouseButton(event)

    def _update(self, dt: int):
        pass

    @typing.final
    def update(self, dt: int):
        """All game modes can update."""
        self._update(dt)
        self._all_sprites.update(dt)

    def _updatePreDraw(self):
        pass

    def _drawPreSprites(self, screen: pygame.surface.Surface):
        pass

    def _drawPostSprites(self, screen: pygame.surface.Surface):
        pass

    @typing.final
    def draw(self, screen: pygame.surface.Surface):
        """All game modes can draw to the screen"""
        self._updatePreDraw()
        self._space.blit(self._background, (0, 0))
        self._drawPreSprites(self._space)
        self._all_sprites.draw(self._space)
        self._drawPostSprites(self._space)
        screen.blit(self._space, (0, 0), self._camera)

    @staticmethod
    def _stopMixer():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.stop()

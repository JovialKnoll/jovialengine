import os
import typing
import functools

import pygame
pygame.init()

from .display import Display
from .fontwrap import FontWrap
from .modebase import ModeBase
from .modegamemenu import ModeGameMenu
from .modegamemenu import ModeGameMenuTop
from . import config

import constants
import state


class _Game(object):
    __slots__ = (
        'game_running',
        'start_mode_cls',
        'display',
        'font_wrap',
        'state',
        '_current_mode',
        '_is_first_loop',
        '_max_framerate',
        '_clock',
        '_joysticks',
    )

    def __init__(self):
        self.game_running = False
        self.display: Display
        self.font_wrap: FontWrap
        if constants.FONT:
            font = pygame.font.Font(constants.FONT, constants.FONT_SIZE)
        else:
            font = pygame.font.SysFont(None, constants.FONT_SIZE)
        self.font_wrap = FontWrap(font, constants.FONT_HEIGHT, constants.FONT_ANTIALIAS)
        self.state = state.State()
        self.start_mode_cls: typing.Type[ModeBase]
        self._current_mode: ModeBase
        self._is_first_loop = True
        self._max_framerate = config.get(config.MAX_FRAMERATE)
        self._clock = pygame.time.Clock()
        self._joysticks = [
            pygame.joystick.Joystick(i)
            for i
            in range(pygame.joystick.get_count())
        ]

    def load(self,
             start_mode_cls: typing.Type[ModeBase],
             src_directory: str,
             title: str,
             window_icon: str | None
             ):
        self.start_mode_cls = start_mode_cls
        config.init(
            os.path.join(src_directory, 'config.ini')
        )
        self.display = Display(
            os.path.join(src_directory, 'screenshots'),
            title,
            window_icon
        )
        self._current_mode = self.start_mode_cls()
        self.game_running = True

    def run(self):
        """Run the game, and check if the game needs to end."""
        if not self._current_mode:
            raise RuntimeError("error: no current mode")
        events = self._filterInput(pygame.event.get())
        self._current_mode.inputEvents(events)
        for i in range(self._getTime()):
            self._current_mode.update(1)
        self._current_mode.draw(self.display.screen)
        self.display.scaleDraw()
        if self._current_mode.next_mode is not None:
            if isinstance(self._current_mode, ModeGameMenu) \
                    and not isinstance(self._current_mode.next_mode, ModeGameMenu):
                pygame.mixer.music.unpause()
                pygame.mixer.unpause()
            self._current_mode.cleanup()
            self._current_mode = self._current_mode.next_mode
        if not self.game_running:
            config.save()
        self._is_first_loop = False
        return self.game_running

    def _filterInput(self, events: typing.Iterable[pygame.event.Event]):
        """Take care of input that game modes should not take care of."""
        events = map(self.display.scaleMouseInput, events)
        events = filter(self._stillNeedsHandling, events)
        return list(events)

    def _stillNeedsHandling(self, event: pygame.event.Event):
        """If event should be handled before all others, handle it and return False, otherwise return True.
        As an example, game-ending or display-changing events should be handled before all others.
        Also filter out bad mouse events here.
        """
        match event.type:
            case pygame.QUIT | pygame.WINDOWFOCUSLOST | pygame.WINDOWMINIMIZED:
                return self._handlePauseMenu()
            case pygame.WINDOWMOVED:
                if not self._is_first_loop:
                    return self._handlePauseMenu()
            case pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return self._handlePauseMenu()
                elif event.key == pygame.K_F12:
                    self.display.takeScreenshot()
                    return False
            case pygame.MOUSEMOTION | pygame.MOUSEBUTTONUP | pygame.MOUSEBUTTONDOWN:
                if (
                    event.pos[0] < 0
                    or event.pos[1] < 0
                    or event.pos[0] >= constants.SCREEN_SIZE[0]
                    or event.pos[1] >= constants.SCREEN_SIZE[1]
                ):
                    return False
            case pygame.JOYDEVICEREMOVED:
                self._joysticks = [
                    joystick
                    for joystick
                    in self._joysticks
                    if joystick.get_instance_id() != event.instance_id
                ]
                return False
            case pygame.JOYDEVICEADDED:
                self._joysticks = [
                    pygame.joystick.Joystick(i)
                    for i
                    in range(pygame.joystick.get_count())
                ]
                return False
        return True

    def _handlePauseMenu(self):
        # pass quit events forward to ModeGameMenu, but not to other modes
        if isinstance(self._current_mode, ModeGameMenu):
            return True
        self._current_mode = ModeGameMenuTop(self._current_mode)
        pygame.mixer.music.pause()
        pygame.mixer.pause()
        return False

    def _getTime(self):
        return self._clock.tick(self._max_framerate)


@functools.cache
def getGame():
    return _Game()

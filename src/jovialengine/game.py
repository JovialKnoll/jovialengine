import typing
import os
from datetime import datetime

import pygame

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
        'display',
        'font_wrap',
        'state',
        'start_mode_cls',
        '_current_mode',
        '_is_first_loop',
        '_max_framerate',
        '_clock',
        '_joysticks',
    )

    def __init__(self):
        self.game_running = False
        self.display = Display()
        if constants.FONT:
            font = pygame.font.Font(constants.FONT, constants.FONT_SIZE)
        else:
            font = pygame.font.SysFont(None, constants.FONT_SIZE)
        self.font_wrap = FontWrap(font, constants.FONT_HEIGHT, constants.FONT_ANTIALIAS)
        self.state = state.State()
        self.start_mode_cls: typing.Type[ModeBase]
        self._current_mode: ModeBase
        self._is_first_loop = True
        self._max_framerate = config.config.getint(config.CONFIG_SECTION, config.CONFIG_MAX_FRAMERATE)
        self._clock = pygame.time.Clock()
        self._joysticks = [
            pygame.joystick.Joystick(i)
            for i
            in range(pygame.joystick.get_count())
        ]

    def load(self, start_mode_cls: typing.Type[ModeBase]):
        self.game_running = True
        self.start_mode_cls = start_mode_cls
        self._current_mode: ModeBase = self.start_mode_cls()

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
            config.saveConfig()
        self._is_first_loop = False
        return self.game_running

    def _filterInput(self, events: typing.Iterable[pygame.event.Event]):
        """Take care of input that game modes should not take care of."""
        return list(
            filter(
                self._stillNeedsHandling,
                map(
                    self.display.scaleMouseInput,
                    events
                )
            )
        )

    def _stillNeedsHandling(self, event: pygame.event.Event):
        """If event should be handled before all others, handle it and return False, otherwise return True.
        As an example, game-ending or display-changing events should be handled before all others.
        Also filter out bad mouse events here.
        """
        if event.type in (pygame.QUIT, pygame.WINDOWFOCUSLOST, pygame.WINDOWMINIMIZED):
            return self._handlePauseMenu()
        elif event.type == pygame.WINDOWMOVED and not self._is_first_loop:
            return self._handlePauseMenu()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return self._handlePauseMenu()
            elif event.key == pygame.K_F12:
                try:
                    os.mkdir(constants.SCREENSHOT_DIRECTORY)
                except FileExistsError:
                    pass
                file_name = f"{datetime.utcnow().isoformat().replace(':', '')}.png"
                file_path = os.path.join(constants.SCREENSHOT_DIRECTORY, file_name)
                pygame.image.save(self.display.screen, file_path)
                return False
        elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN) \
            and (
                event.pos[0] < 0
                or event.pos[1] < 0
                or event.pos[0] >= constants.SCREEN_SIZE[0]
                or event.pos[1] >= constants.SCREEN_SIZE[1]
        ):
            return False
        elif event.type == pygame.JOYDEVICEREMOVED:
            self._joysticks = [
                joystick
                for joystick
                in self._joysticks
                if joystick.get_instance_id() != event.instance_id
            ]
            return False
        elif event.type == pygame.JOYDEVICEADDED:
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


_game_instance: _Game | None = None


def getInstance():
    global _game_instance
    if _game_instance is None:
        _game_instance = _Game()
    return _game_instance

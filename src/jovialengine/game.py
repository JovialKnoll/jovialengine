import typing
import os
from datetime import datetime

import pygame

import jovialengine
from .modegamemenu import ModeGameMenu
from .modegamemenu import ModeGameMenuTop
from .display import Display
from . import config

import constants
import state


class Game(object):
    __slots__ = (
        '_max_framerate',
        '_clock',
        '_current_mode',
        '_is_first_loop',
    )

    def __init__(self, start_mode_cls: typing.Type[jovialengine.ModeBase]):
        # init shared objects
        jovialengine.shared.display = Display()
        jovialengine.shared.font_wrap = jovialengine.fontwrap.FontWrap(constants.FONT, constants.FONT_SIZE)
        jovialengine.shared.state = state.State()
        jovialengine.shared.start_mode_cls = start_mode_cls
        jovialengine.shared.game_running = True
        # init game properties
        self._max_framerate = jovialengine.shared.config.getint(config.CONFIG_SECTION, config.CONFIG_MAX_FRAMERATE)
        self._clock = pygame.time.Clock()
        self._current_mode = jovialengine.shared.start_mode_cls()
        self._is_first_loop = True

    def run(self):
        """Run the game, and check if the game needs to end."""
        if not self._current_mode:
            raise RuntimeError("error: no current mode")
        self._current_mode.input_events(
            self._filterInput(pygame.event.get())
        )
        for i in range(self._getTime()):
            self._current_mode.update(1)
        self._current_mode.draw(jovialengine.shared.display.screen)
        jovialengine.shared.display.scaleDraw()
        if self._current_mode.next_mode is not None:
            if isinstance(self._current_mode, ModeGameMenu) \
                    and not isinstance(self._current_mode.next_mode, ModeGameMenu):
                pygame.mixer.music.unpause()
                pygame.mixer.unpause()
            self._current_mode.cleanup()
            self._current_mode = self._current_mode.next_mode
        if not jovialengine.shared.game_running:
            jovialengine.shared.saveConfig()
        self._is_first_loop = False
        return jovialengine.shared.game_running

    def _filterInput(self, events: typing.Iterable[pygame.event.Event]):
        """Take care of input that game modes should not take care of."""
        return filter(self._stillNeedsHandling, map(jovialengine.shared.display.scaleMouseInput, events))

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
                pygame.image.save(jovialengine.shared.display.screen, file_path)
                return False
        elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN) \
            and (
                event.pos[0] < 0
                or event.pos[1] < 0
                or event.pos[0] >= constants.SCREEN_SIZE[0]
                or event.pos[1] >= constants.SCREEN_SIZE[1]
        ):
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

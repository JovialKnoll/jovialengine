import os
from types import ModuleType
from collections.abc import Iterable

import pygame
pygame.init()

from . import display
from . import input
from . import fontwrap
from .modebase import ModeBase
from .modegamemenu import ModeGameMenu
from .modegamemenu import ModeGameMenuTop
from .saveable import Saveable
from . import config
from . import save


class _Game(object):
    __slots__ = (
        'start_mode_cls',
        'state_cls',
        '_clock',
        '_max_framerate',
        '_joysticks',
        '_is_first_loop',
        '_current_mode',
        'state',
        'running',
    )

    def __init__(
        self,
        mode_module: ModuleType,
        start_mode_cls: type[ModeBase],
        state_cls: type[Saveable],
        src_directory: str,
        screen_size: tuple[int, int],
        title: str,
        window_icon: str | None,
        max_players: int,
        event_names: tuple[str],
        input_defaults: tuple[input.InputDefault],
        font_location: str | None,
        font_size: int,
        font_height: int,
        font_antialias: bool
    ):
        self.start_mode_cls = start_mode_cls
        self.state_cls = state_cls
        config.init(
            os.path.join(src_directory, 'config.ini')
        )
        save.init(
            os.path.join(src_directory, 'saves'),
            mode_module
        )
        display.init(
            os.path.join(src_directory, 'screenshots'),
            screen_size,
            title,
            window_icon
        )
        input.init(
            os.path.join(src_directory, 'input.cfg'),
            max_players,
            event_names,
            input_defaults
        )
        if font_location:
            font = pygame.font.Font(font_location, font_size)
        else:
            font = pygame.font.SysFont(None, font_size)
        fontwrap.init(font, font_height, font_antialias)
        self._clock = pygame.time.Clock()
        self._max_framerate = config.get(config.MAX_FRAMERATE)
        self._joysticks = [
            pygame.joystick.Joystick(i)
            for i
            in range(pygame.joystick.get_count())
        ]
        self._is_first_loop = True
        self._current_mode: ModeBase | None = None
        self.state: Saveable | None = None
        self.running = False

    def start(self):
        """Start the game, must be called before run()."""
        self._current_mode = self.start_mode_cls()
        self.state = self.state_cls()
        self.running = True

    def run(self):
        """Run the game, and check if the game needs to end."""
        if not self._current_mode:
            raise RuntimeError("error: self._current_mode is not set")
        events = self._filterInput(pygame.event.get())
        events = input.takeEvents(events)
        input_frame = input.getInputFrame()
        if input_frame.wasPlayerInputPressed(0, input.TYPE_SCREENSHOT):
            display.takeScreenshot()
        if any(map(self._isPauseEvent, events)) or input_frame.wasInputPressed(input.TYPE_PAUSE):
            # if already in pause menu no need to do this stuff
            if not isinstance(self._current_mode, ModeGameMenu):
                self._current_mode = ModeGameMenuTop(self._current_mode)
                input.startNewMode()
                input_frame = input.getInputFrame()
                pygame.mixer.music.pause()
                pygame.mixer.pause()
                events = []
        self._current_mode.input(events, input_frame)
        for i in range(self._getTime()):
            self._current_mode.update(1)
        self._current_mode.draw(display.screen)
        display.scaleDraw()
        if self._current_mode.next_mode is not None:
            if isinstance(self._current_mode, ModeGameMenu) \
                    and not isinstance(self._current_mode.next_mode, ModeGameMenu):
                pygame.mixer.music.unpause()
                pygame.mixer.unpause()
            self._current_mode.cleanup()
            self._current_mode = self._current_mode.next_mode
            input.startNewMode()
        self._is_first_loop = False
        if not self.running:
            config.save()
            input.save()
            self._current_mode = None
            self.state = None
            pygame.quit()
        return self.running

    def _filterInput(self, events: Iterable[pygame.event.Event]):
        """Take care of input that game modes should not take care of."""
        events = map(display.scaleMouseInput, events)
        events = filter(self._filterEvent, events)
        return list(events)

    def _filterEvent(self, event: pygame.event.Event):
        """If event should be handled before all others, handle it and return False, otherwise return True.
        As an example, game-ending or display-changing events should be handled before all others.
        Also filter out bad mouse events here.
        """
        match event.type:
            case pygame.MOUSEMOTION | pygame.MOUSEBUTTONUP | pygame.MOUSEBUTTONDOWN:
                return display.isInScreen(event.pos)
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

    def _isPauseEvent(self, event: pygame.event.Event):
        return event.type in (pygame.QUIT, pygame.WINDOWFOCUSLOST, pygame.WINDOWMINIMIZED) \
            or (event.type == pygame.WINDOWMOVED and not self._is_first_loop)

    def _getTime(self):
        return self._clock.tick(self._max_framerate)


_game: _Game | None = None


def initGame(
    mode_module: ModuleType,
    start_mode_cls: type[ModeBase],
    state_cls: type[Saveable],
    src_directory: str,
    screen_size: tuple[int, int],
    title: str,
    window_icon: str | None,
    max_players: int,
    event_names: tuple[str],
    input_defaults: tuple[input.InputDefault],
    font_location: str | None,
    font_size: int,
    font_height: int,
    font_antialias: bool
):
    """Loads up the game and prepares it for running.
    Arguments:
    mode_module - the module holding all modes for your game
    start_mode_cls - the class for the first mode
    state_cls - the class for holding general game state
    src_directory - directory of the program
    screen_size - size of the virtual screen
    title - title of the game (for titlebar)
    window_icon - location of icon of the game (for titlebar)
    max_players - maximum number of players the game supports
    event_names - names for virtual inputs that button / axis inputs map to
    input_defaults - default input mappings
    font_location - location of default font for the game
    font_size - default font size
    font_height - default font height
    font_antialias - default font antialias
    """
    global _game
    if _game:
        raise RuntimeError("error: _game is already set")
    _game = _Game(
        mode_module,
        start_mode_cls,
        state_cls,
        src_directory,
        screen_size,
        title,
        window_icon,
        max_players,
        event_names,
        input_defaults,
        font_location,
        font_size,
        font_height,
        font_antialias
    )
    _game.start()
    return _game


def getGame():
    return _game

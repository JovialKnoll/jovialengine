import os
from types import ModuleType
from collections.abc import Iterable

import pygame
pygame.init()

from . import display
from . import gameinput
from . import fontwrap
from .modebase import ModeBase
from .modegamemenu import ModeGameMenu
from .modegamemenu import ModeGameMenuTop
from .saveable import Saveable
from . import config
from . import save


class _Game(object):
    __slots__ = (
        'mode_module',
        'start_mode_cls',
        'restart_mode_cls',
        'state_cls',
        'src_directory',
        'screen_size',
        'title',
        'window_icon',
        'max_players',
        'event_names',
        'input_defaults',
        'font_location',
        'font_size',
        'font_height',
        'font_antialias',
        'max_dt',

        '_joysticks',
        'state',
        'current_mode',
        '_running',
        '_is_first_loop',
        '_clock',
    )

    def __init__(self):
        self.mode_module: ModuleType | None = None
        self.start_mode_cls: type[ModeBase] | None = None
        self.restart_mode_cls: type[ModeBase] | None = None
        self.state_cls: type[Saveable] | None = None
        self.src_directory: str | None = None
        self.screen_size: tuple[int, int] | None = None
        self.title: str = ""
        self.window_icon: str | None = None
        self.max_players: int = 1
        self.event_names: tuple[str] | None = None
        self.input_defaults: tuple[gameinput.InputDefault] | None = None
        self.font_location: str | None = None
        self.font_size: int | None = None
        self.font_height: int | None = None
        self.font_antialias: bool | None = None
        self.max_dt: int = 5

        self._joysticks: list[pygame.joystick.Joystick] = []
        self.state: Saveable | None = None
        self.current_mode: ModeBase | None = None
        self._running: bool = False
        self._is_first_loop: bool = False
        self._clock: pygame.time.Clock | None = None

    def start(self):
        """Start the game, must be called before run()."""
        if not self.mode_module:
            raise RuntimeError("error: self.mode_module is not set")
        if not self.start_mode_cls:
            raise RuntimeError("error: self.start_mode_cls is not set")
        if not self.state_cls:
            raise RuntimeError("error: self.state_cls is not set")
        if not self.src_directory:
            raise RuntimeError("error: self.src_directory is not set")
        if not self.screen_size:
            raise RuntimeError("error: self.screen_size is not set")
        if not self.event_names:
            raise RuntimeError("error: self.event_names is not set")
        if not self.input_defaults:
            raise RuntimeError("error: self.input_defaults is not set")
        if not self.font_size:
            raise RuntimeError("error: self.font_size is not set")
        if not self.font_height:
            raise RuntimeError("error: self.font_height is not set")
        if self.font_antialias is None:
            raise RuntimeError("error: self.font_antialias is not set")
        config.init(
            os.path.join(self.src_directory, 'config.ini')
        )
        save.init(
            os.path.join(self.src_directory, 'saves'),
            self.mode_module
        )
        display.init(
            os.path.join(self.src_directory, 'screenshots'),
            self.screen_size,
            self.title,
            self.window_icon
        )
        gameinput.init(
            os.path.join(self.src_directory, 'input.cfg'),
            self.max_players,
            self.event_names,
            self.input_defaults
        )
        if self.font_location:
            font = pygame.font.Font(self.font_location, self.font_size)
        else:
            font = pygame.font.SysFont(None, self.font_size)
        fontwrap.init(font, self.font_height, self.font_antialias)

        self._joysticks = [
            pygame.joystick.Joystick(i)
            for i
            in range(pygame.joystick.get_count())
        ]
        self.set_state()
        self.current_mode = self.start_mode_cls()
        self._running = True
        self._is_first_loop = True
        self._clock = pygame.time.Clock()

    def set_state(self, save_data=None):
        if save_data:
            self.state = self.state_cls.load(save_data)
        else:
            self.state = self.state_cls()

    def stop(self):
        self._running = False

    def run(self):
        """Run the game, and check if the game needs to end."""
        if not self.current_mode:
            raise RuntimeError("error: self.current_mode is not set")
        events = self._filter_input(pygame.event.get())
        events = gameinput.take_events(events)
        input_frame = gameinput.get_input_frame()
        if input_frame.was_player_input_pressed(0, gameinput.TYPE_SCREENSHOT):
            display.take_screenshot()
        if any(map(self._is_pause_event, events)) or input_frame.was_input_pressed(gameinput.TYPE_PAUSE):
            # if already in pause menu no need to do this stuff
            if not isinstance(self.current_mode, ModeGameMenu):
                self.current_mode = ModeGameMenuTop(self.current_mode)
                gameinput.start_new_mode()
                input_frame = gameinput.get_input_frame()
                pygame.mixer.music.pause()
                pygame.mixer.pause()
                events = []
        self.current_mode.input(events, input_frame)
        dt = self._clock.tick_busy_loop(display.max_framerate)
        while dt > self.max_dt:
            dt -= self.max_dt
            self.current_mode.update(self.max_dt)
        self.current_mode.update(dt)
        self.current_mode.draw(display.screen)
        display.scale_draw()
        if self.current_mode.next_mode is not None:
            if isinstance(self.current_mode, ModeGameMenu) \
                    and not isinstance(self.current_mode.next_mode, ModeGameMenu):
                pygame.mixer.music.unpause()
                pygame.mixer.unpause()
            self.current_mode.cleanup()
            self.current_mode = self.current_mode.next_mode
            gameinput.start_new_mode()
        self._is_first_loop = False
        if not self._running:
            config.save()
            gameinput.save()
            self.current_mode = None
            self.state = None
            pygame.quit()
        return self._running

    def _filter_input(self, events: Iterable[pygame.event.Event]):
        """Take care of input that game modes should not take care of."""
        events = map(display.scale_mouse_input, events)
        events = filter(self._filter_event, events)
        return list(events)

    def _filter_event(self, event: pygame.event.Event):
        """If event should be handled before all others, handle it and return False, otherwise return True.
        As an example, game-ending or display-changing events should be handled before all others.
        Also filter out irrelevant mouse events here.
        """
        match event.type:
            case pygame.MOUSEMOTION | pygame.MOUSEBUTTONUP | pygame.MOUSEBUTTONDOWN:
                return display.is_in_screen(event.pos)
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

    def _is_pause_event(self, event: pygame.event.Event):
        return event.type in {pygame.QUIT, pygame.WINDOWFOCUSLOST, pygame.WINDOWMINIMIZED} \
            or (event.type == pygame.WINDOWMOVED and not self._is_first_loop)


_game: _Game | None = None


class GameBuilder(object):
    __slots__ = (
        '_game',
    )
    def __init__(self):
        self._game = _Game()

    def set_mode_module(self, mode_module: ModuleType):
        """required: Sets the module that holds all modes."""
        self._game.mode_module = mode_module
        return self

    def set_start_mode_cls(self, start_mode_cls: type[ModeBase]):
        """required: Sets the class for the game start mode."""
        self._game.start_mode_cls = start_mode_cls
        return self

    def set_restart_mode_cls(self, restart_mode_cls: type[ModeBase]):
        """optional: Sets the class for the game restart mode."""
        self._game.restart_mode_cls = restart_mode_cls
        return self

    def set_state_cls(self, state_cls: type[Saveable]):
        """required: Sets the class for holding general game state."""
        self._game.state_cls = state_cls
        return self

    def set_src_directory(self, src_directory: str):
        """required: Sets the directory of the program (for config, input, saves, screenshots)."""
        self._game.src_directory = src_directory
        return self

    def set_screen_size(self, screen_size: tuple[int, int]):
        """required: Sets the size of the virtual screen."""
        if screen_size[0] < 1 or screen_size[1] < 1:
            raise ValueError("error: screen_size must have a positive non-zero length for each dimension")
        self._game.screen_size = screen_size
        return self

    def set_title(self, title: str):
        """optional: Sets the title of the game window."""
        self._game.title = title
        return self

    def set_window_icon(self, window_icon: str):
        """optional: Sets the location of icon of the game window."""
        self._game.window_icon = window_icon
        return self

    def set_max_players(self, max_players: int):
        """optional: Sets the maximum number of players the game supports."""
        if max_players < 1:
            raise ValueError("error: max_players must not be less than 1")
        self._game.max_players = max_players
        return self

    def set_event_names(self, event_names: tuple[str]):
        """required: Sets the names for the virtual input events."""
        self._game.event_names = event_names
        return self

    def set_input_defaults(self, input_defaults: tuple[gameinput.InputDefault]):
        """required: Sets the default input mappings."""
        self._game.input_defaults = input_defaults
        return self

    def set_font_location(self, font_location: str):
        """optional: Sets the location of the default font."""
        self._game.font_location = font_location
        return self

    def set_font_size(self, font_size: int):
        """required: Sets the size of the default font."""
        self._game.font_size = font_size
        return self

    def set_font_height(self, font_height: int):
        """required: Sets the height of the default font."""
        self._game.font_height = font_height
        return self

    def set_font_antialias(self, font_antialias: bool):
        """required: Sets the antialias type of the default font."""
        self._game.font_antialias = font_antialias
        return self

    def set_max_dt(self, max_dt: int):
        """optional: Sets the maximum dt for updates.
        If dt is over this amount instead the game runs updates and collision checks multiple times.
        Default is 5."""
        self._game.max_dt = max_dt
        return self

    def build(self):
        global _game
        if _game:
            raise RuntimeError("error: _game is already set")
        _game = self._game
        _game.start()
        return _game


def stop():
    _game.stop()


def get_state():
    return _game.state


def set_state(save_data=None):
    _game.set_state(save_data)


def get_start_mode_cls():
    return _game.start_mode_cls


def get_restart_mode_cls():
    return _game.restart_mode_cls or _game.start_mode_cls


def get_current_mode():
    return _game.current_mode

from types import ModuleType

from .game import Game
from .modebase import ModeBase
from .saveable import Saveable
from . import gameinput


_game: Game | None = None


class GameBuilder(object):
    __slots__ = (
        '_game',
    )
    def __init__(self):
        self._game = Game()

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

    def set_auto_save(self):
        """optional: Sets the game to automatically save and load. (opposite of default behavior)"""
        self._game.auto_save = True
        return self

    def set_restart_without_state(self):
        """optional: Sets the game to not reset the shared state when restarted. (opposite of default behavior)"""
        self._game.restart_affects_state = False
        return self

    def set_mouse_invisible(self):
        """optional: Sets the game to not reset the shared state when restarted. (opposite of default behavior)"""
        self._game.mouse_visible = False
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


def get_auto_save():
    return _game.auto_save


def get_restart_affects_state():
    return _game.restart_affects_state

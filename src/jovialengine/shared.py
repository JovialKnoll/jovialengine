import typing

import pygame

from .display import Display
from .fontwrap import FontWrap
from .modebase import ModeBase

import state


display: Display
font_wrap: FontWrap
state: state.State
start_mode_cls: typing.Type[ModeBase]
joysticks: typing.Iterable[pygame.joystick.Joystick]
game_running: False

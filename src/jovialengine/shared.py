import typing

from .display import Display
from .fontwrap import FontWrap
from .modebase import ModeBase

import state


display: Display
font_wrap: FontWrap
state: state.State
start_mode_cls: typing.Type[ModeBase]
game_running: False

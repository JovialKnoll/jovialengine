import os
import copy
import enum
from collections.abc import Iterable

import pygame

from .inputframe import ControllerStateChange, InputFrame


class InputType(enum.Enum):
    KEYBOARD = enum.auto()
    MOUSE = enum.auto()
    CON_BUTTON = enum.auto()
    CON_HAT = enum.auto()
    CON_AXIS = enum.auto()


TYPE_NONE = -1
TYPE_PAUSE = 0
TYPE_SCREENSHOT = 1
INPUT_TYPE_START_POS = 2
_input_file: str | None = None
_max_players: int
_num_inputs: int
_controller_states: list[list[float | int]]
_controller_states_prev: list[list[float | int]]
_controller_state_changes: list[ControllerStateChange]


def init(input_file: str, max_players: int, num_inputs: int):
    global _input_file
    global _num_inputs
    global _max_players
    if _input_file:
        raise RuntimeError("error: _input_file is already set")
    _input_file = input_file
    if os.path.exists(_input_file):
        _parseFile()
    # load in input mapping from config
    # make objects to hold onto current virtual gamepad states
    _max_players = max_players
    _num_inputs = num_inputs
    startNewMode()


def startNewMode():
    global _controller_states
    global _controller_states_prev
    global _controller_state_changes
    _controller_states = [[0] * _num_inputs for x in range(_max_players)]
    _controller_states_prev = [[0] * _num_inputs for x in range(_max_players)]
    _controller_state_changes = []


def _parseFile():
    with open(_input_file, 'r') as file:
        # read in custom file format here
        # save into dictionary / dictionaries for fast comparisons
        pass


def save():
    # save on confirming changes to key mappings
    with open(_input_file, 'w') as file:
        # write in custom file format here
        pass


def takeEvents(events: Iterable[pygame.event.Event]):
    global _controller_states_prev
    global _controller_state_changes
    _controller_states_prev = copy.deepcopy(_controller_states)
    _controller_state_changes = []
    for event in events:
        match event.type:
            case pygame.KEYUP | pygame.KEYDOWN:
                player_id, event_type = _mapEvent(InputType.KEYBOARD, event.key)
                _logEvent(player_id, event_type, 1 if event.type == pygame.KEYDOWN else 0)
            case pygame.MOUSEBUTTONUP | pygame.MOUSEBUTTONDOWN:
                player_id, event_type = _mapEvent(InputType.MOUSE, event.button)
                _logEvent(player_id, event_type, 1 if event.type == pygame.MOUSEBUTTONDOWN else 0)
            case pygame.JOYBUTTONUP | pygame.JOYBUTTONDOWN:
                player_id, event_type = _mapEvent(InputType.CON_BUTTON, event.button, event.instance_id)
                _logEvent(player_id, event_type, 1 if event.type == pygame.JOYBUTTONDOWN else 0)
            case pygame.JOYHATMOTION:
                hat_value_left_right_up_down = (
                    1 if event.value[0] == -1 else 0,
                    1 if event.value[0] == 1 else 0,
                    1 if event.value[1] == 1 else 0,
                    1 if event.value[1] == -1 else 0,
                )
                for i, event_value in enumerate(hat_value_left_right_up_down):
                    player_id, event_type = _mapEvent(InputType.CON_HAT, event.hat * 4 + i, event.instance_id)
                    _logEvent(player_id, event_type, event_value)
            case pygame.JOYAXISMOTION:
                axis_value_back_forth = (
                    event.value * -1 if event.value < 0 else 0,
                    event.value if event.value > 0 else 0,
                )
                for i, event_value in enumerate(axis_value_back_forth):
                    player_id, event_type = _mapEvent(InputType.CON_AXIS, event.axis * 2 + i, event.instance_id)
                    _logEvent(player_id, event_type, event_value)
                # event.value
                pass


def _mapEvent(input_type: InputType, input_id: int, controller_id: int = 0):
    # fill out these based on mapping
    player_id = 0
    event_type = TYPE_NONE
    # replace the below with proper mapping later
    if input_type == InputType.KEYBOARD:
        if input_id == pygame.K_ESCAPE:
            event_type = TYPE_PAUSE
        elif input_id == pygame.K_F12:
            event_type = TYPE_SCREENSHOT
    return player_id, event_type


def _logEvent(player_id: int, event_type: int, event_value: float | int):
    if _controller_states[player_id][event_type] != event_value:
        _controller_state_changes.append(
            ControllerStateChange(player_id, event_type, event_value)
        )
        _controller_states[player_id][event_type] = event_value


def getInputFrame():
    return InputFrame(_controller_states, _controller_states_prev, _controller_state_changes)

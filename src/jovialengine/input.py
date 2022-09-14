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


class InputDefault(object):
    __slots__ = (
        'player_id',
        'event_type',
        'input_type',
        'input_id',
        'controller_id',
    )

    def __init__(
        self,
        player_id: int,
        event_type: int,
        input_type: InputType,
        input_id: int,
        controller_id: int = 0
    ):
        self.player_id = player_id
        self.event_type = event_type
        self.input_type = input_type
        self.input_id = input_id
        self.controller_id = controller_id

    def getMapKey(self):
        return _getMapKey(
            self.input_type,
            self.input_id,
            self.controller_id
        )

    def getMapValue(self):
        return (
            self.player_id,
            self.event_type,
        )


TYPE_NONE = -1
TYPE_PAUSE = 0
TYPE_SCREENSHOT = 1
EVENT_TYPE_START_POS = 2
_input_file: str | None = None
_max_players: int
_event_names: tuple[str]
_num_inputs: int
_controller_states: list[list[float | int]]
_controller_states_prev: list[list[float | int]]
_controller_state_changes: list[ControllerStateChange]
_input_mapping: dict[tuple[InputType, int, int], tuple[int, int]]


def init(input_file: str, max_players: int, event_names: tuple[str], input_defaults: tuple[InputDefault]):
    global _input_file
    global _max_players
    global _event_names
    global _num_inputs
    if _input_file:
        raise RuntimeError("error: _input_file is already set")
    _input_file = input_file
    if os.path.exists(_input_file):
        with open(_input_file, 'r') as file:
            # read in custom file format here
            # save into dictionary / dictionaries for fast comparisons
            pass
    else:
        for input_default in input_defaults:
            _input_mapping[input_default.getMapKey()] = input_default.getMapValue()
    _max_players = max_players
    _event_names = event_names
    _num_inputs = EVENT_TYPE_START_POS + len(event_names)
    startNewMode()


def startNewMode():
    global _controller_states
    global _controller_states_prev
    global _controller_state_changes
    _controller_states = [[0] * _num_inputs for x in range(_max_players)]
    _controller_states_prev = [[0] * _num_inputs for x in range(_max_players)]
    _controller_state_changes = []


def save():
    # save on confirming changes to key mappings
    with open(_input_file, 'w') as file:
        # write in custom file format here
        # player_id;event_name:input_type.name-controller_id-input_id
        # player_id;event_name:input_type.name-controller_id-input_id,input_type-name-controller_id-input_id
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


def _getMapKey(input_type: InputType, input_id: int, controller_id: int):
    return (
        input_type,
        input_id,
        controller_id,
    )


def _mapEvent(input_type: InputType, input_id: int, controller_id: int = 0):
    # replace the below with proper mapping later
    if input_type == InputType.KEYBOARD:
        if input_id == pygame.K_ESCAPE:
            return 0, TYPE_PAUSE
        elif input_id == pygame.K_F12:
            return 0, TYPE_SCREENSHOT
    return _input_mapping.get(
        _getMapKey(input_type, input_id, controller_id),
        (0, TYPE_NONE,)
    )


def _logEvent(player_id: int, event_type: int, event_value: float | int):
    if event_type != TYPE_NONE and _controller_states[player_id][event_type] != event_value:
        _controller_state_changes.append(
            ControllerStateChange(player_id, event_type, event_value)
        )
        _controller_states[player_id][event_type] = event_value


def getInputFrame():
    return InputFrame(_controller_states, _controller_states_prev, _controller_state_changes)

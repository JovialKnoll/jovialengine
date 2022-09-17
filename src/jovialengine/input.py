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
ENGINE_INPUT_DEFAULTS = (
    InputDefault(0, TYPE_PAUSE, InputType.KEYBOARD, pygame.K_ESCAPE),
    InputDefault(0, TYPE_SCREENSHOT, InputType.KEYBOARD, pygame.K_F12),
)
_input_file: str | None = None
_max_players: int
_event_names: tuple[str]
_num_inputs: int
_input_defaults: tuple[InputDefault]
_input_mapping: dict[tuple[InputType, int, int], tuple[int, int]]
_controller_states: list[list[float | int]]
_controller_states_prev: list[list[float | int]]
_controller_state_changes: list[ControllerStateChange]


def init(input_file: str, max_players: int, event_names: tuple[str], input_defaults: tuple[InputDefault]):
    global _input_file
    global _max_players
    global _event_names
    global _num_inputs
    global _input_defaults
    if _input_file:
        raise RuntimeError("error: _input_file is already set")
    _input_file = input_file
    _max_players = max_players
    _event_names = event_names
    _num_inputs = EVENT_TYPE_START_POS + len(event_names)
    _input_defaults = input_defaults
    if os.path.exists(_input_file):
        _load()
    else:
        resetDefaultMapping()
    startNewMode()


def startNewMode():
    global _controller_states
    global _controller_states_prev
    global _controller_state_changes
    _controller_states = [[0] * _num_inputs for x in range(_max_players)]
    _controller_states_prev = [[0] * _num_inputs for x in range(_max_players)]
    _controller_state_changes = []


def resetDefaultMapping():
    global _input_mapping
    _input_mapping = dict()
    for input_default in ENGINE_INPUT_DEFAULTS:
        _input_mapping[input_default.getMapKey()] = input_default.getMapValue()
    for input_default in _input_defaults:
        _input_mapping[input_default.getMapKey()] = input_default.getMapValue()


def _load():
    global _input_mapping
    with open(_input_file, 'r') as file:
        # read in custom file format here
        # save into dictionary / dictionaries for fast comparisons
        pass


def _getSaveInput(input_type: InputType, input_id: int, controller_id: int):
    result = f'{input_type.name}-'
    if input_type == InputType.KEYBOARD:
        result += pygame.key.name(input_id)
    else:
        result += str(input_id)
    if input_type in (InputType.CON_BUTTON, InputType.CON_HAT, InputType.CON_AXIS):
        result += f'-{controller_id}'
    return result


def save():
    mapping_to_write: dict[tuple[int, int], list[tuple[InputType, int, int]]] = dict()
    for key, value in _input_mapping.items():
        if value not in mapping_to_write:
            mapping_to_write[value] = []
        mapping_to_write[value].append(key)
    with open(_input_file, 'w') as file:
        for write_key, write_value in mapping_to_write.items():
            inputs = ','.join(
                [
                    _getSaveInput(item[0], item[1], item[2])
                    for item
                    in write_value
                ]
            )
            line = '{};{}:{}'.format(
                write_key[0],
                _event_names[write_key[1] - EVENT_TYPE_START_POS],
                inputs
            )
            print(line, file=file)
        # player_id;event_name:input_type.name-input_id-controller_id
        # player_id;event_name:input_type.name-input_id-controller_id,input_type-name-input_id-controller_id


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

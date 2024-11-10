import os
import copy
import enum
from collections.abc import Iterable

import pygame

from .inputframe import StateChange, InputFrame


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

    def get_map_key(self):
        return _get_map_key(
            self.input_type,
            self.input_id,
            self.controller_id
        )

    def get_map_value(self):
        return (
            self.player_id,
            self.event_type,
        )


_HAT_BUTTON_NAMES = (
    "L",
    "R",
    "U",
    "D",
)
TYPE_NONE = -1
TYPE_PAUSE = 0
TYPE_SCREENSHOT = 1
_ENGINE_INPUT_NAMES = (
    "Pause",
    "Screenshot",
)
_ENGINE_INPUT_DEFAULTS = (
    InputDefault(0, TYPE_PAUSE, InputType.KEYBOARD, pygame.K_ESCAPE),
    InputDefault(0, TYPE_SCREENSHOT, InputType.KEYBOARD, pygame.K_F12),
)
_CONTROLLER_PAUSE_BUTTON = 7
EVENT_TYPE_START_POS = len(_ENGINE_INPUT_NAMES)
_input_file: str | None = None
max_players: int
_event_names: tuple[str]
num_inputs: int
_input_defaults: tuple[InputDefault]
_input_mapping: dict[tuple[InputType, int, int], tuple[int, int]]
_controller_states: list[list[float | int]]
_controller_states_prev: list[list[float | int]]
_controller_state_changes: list[StateChange]


def init(input_file: str, max_players_in: int, event_names: tuple[str], input_defaults: tuple[InputDefault]):
    global _input_file
    global max_players
    global _event_names
    global num_inputs
    global _input_defaults
    if _input_file:
        raise RuntimeError("error: _input_file is already set")
    if max_players_in < 1:
        raise ValueError("error: max_players_in must be at least 1")
    _input_file = input_file
    max_players = max_players_in
    _event_names = _ENGINE_INPUT_NAMES + event_names
    num_inputs = len(_event_names)
    _input_defaults = input_defaults
    if os.path.exists(_input_file):
        _load()
    else:
        reset_default_mapping()
    start_new_mode()


def start_new_mode():
    global _controller_states
    global _controller_states_prev
    global _controller_state_changes
    _controller_states = [[0] * num_inputs for _ in range(max_players)]
    _controller_states_prev = [[0] * num_inputs for _ in range(max_players)]
    _controller_state_changes = []


def _set_input_mapping(input_default: InputDefault):
    _input_mapping[input_default.get_map_key()] = input_default.get_map_value()


def reset_default_mapping():
    global _input_mapping
    _input_mapping = dict()
    controller_pause = tuple(
        InputDefault(i, TYPE_PAUSE, InputType.CON_BUTTON, _CONTROLLER_PAUSE_BUTTON, i)
        for i in range(max_players)
    )
    for input_default in _ENGINE_INPUT_DEFAULTS + controller_pause + _input_defaults:
        _set_input_mapping(input_default)


def _get_hat_values(event: pygame.event.Event) -> tuple[int, int, int, int]:
    return (
        1 if event.value[0] == -1 else 0,
        1 if event.value[0] == 1 else 0,
        1 if event.value[1] == 1 else 0,
        1 if event.value[1] == -1 else 0,
    )


def set_input_mapping(player_id: int, event_type: int, event: pygame.event.Event) -> bool:
    match event.type:
        case pygame.KEYDOWN:
            input_default = InputDefault(
                player_id,
                event_type,
                InputType.KEYBOARD,
                event.key
            )
        case pygame.MOUSEBUTTONDOWN:
            input_default = InputDefault(
                player_id,
                event_type,
                InputType.MOUSE,
                event.button
            )
        case pygame.JOYBUTTONDOWN:
            input_default = InputDefault(
                player_id,
                event_type,
                InputType.CON_BUTTON,
                event.button,
                event.instance_id
            )
        case pygame.JOYHATMOTION:
            input_id = None
            for i, event_value in enumerate(_get_hat_values(event)):
                if event_value == 1:
                    input_id = event.hat * 4 + i
            input_default = InputDefault(
                player_id,
                event_type,
                InputType.CON_HAT,
                input_id,
                event.instance_id
            )
        case _:
            return False
    _set_input_mapping(input_default)
    return True


def _get_input_id_display(input_type: InputType, input_id: int) -> str:
    match input_type:
        case InputType.KEYBOARD:
            return pygame.key.name(input_id)
        case InputType.CON_HAT:
            return f'{input_id // 4}{_HAT_BUTTON_NAMES[input_id % 4]}'
        case _:
            return str(input_id)


def _get_display_input(input_type: InputType, input_id: int, controller_id: int) -> str:
    match input_type:
        case InputType.KEYBOARD:
            result = f'KEY-'
        case InputType.MOUSE:
            result = f'MOUSE-'
        case InputType.CON_BUTTON:
            result = f'CON{controller_id}-BT-'
        case InputType.CON_HAT:
            result = f'CON{controller_id}-HT-'
        case InputType.CON_AXIS:
            result = f'CON{controller_id}-AX-'
        case _:
            raise ValueError("error: input_type must be a supported InputType")
    result += _get_input_id_display(input_type, input_id)
    return result


def get_event_with_controls(player_id: int, event_type: int) -> str:
    inputs = [
        _get_display_input(*key)
        for key, value in _input_mapping.items()
        if value == (player_id, event_type)
    ]
    return f"{_event_names[event_type]}: {','.join(inputs)}"


def get_event_name(event_type: int) -> str:
    return _event_names[event_type]


_PLAYER_SEP = '|'
_EVENT_SEP = ':'
_INPUT_SEP = '&'
_PART_SEP = '+'


def _load():
    global _input_mapping
    _input_mapping = dict()
    with open(_input_file, 'r') as file:
        for line in file:
            line_parts = line.strip().split(_PLAYER_SEP)
            player_id = int(line_parts[0].strip())
            line_parts = line_parts[1].strip().split(_EVENT_SEP)
            event_name = line_parts[0].strip()
            event_type = _event_names.index(event_name)
            input_sections = line_parts[1].strip().split(_INPUT_SEP)
            for input_section in input_sections:
                if not input_section:
                    continue
                input_parts = input_section.strip().split(_PART_SEP)
                input_type_name = input_parts[0]
                input_type = InputType[input_type_name]
                input_id_or_name = input_parts[1]
                input_id: int
                match input_type:
                    case InputType.KEYBOARD:
                        input_id = pygame.key.key_code(input_id_or_name)
                    case InputType.CON_HAT:
                        hat_number = int(input_id_or_name[:-1])
                        hat_direction = input_id_or_name[-1]
                        input_id = hat_number * 4 + _HAT_BUTTON_NAMES.index(hat_direction)
                    case _:
                        input_id = int(input_id_or_name)
                controller_id = 0
                if len(input_parts) == 3:
                    controller_id = int(input_parts[2])
                _input_mapping[_get_map_key(input_type, input_id, controller_id)] = (player_id, event_type)


def _get_save_input(input_type: InputType, input_id: int, controller_id: int):
    result = f'{input_type.name}{_PART_SEP}'
    result += _get_input_id_display(input_type, input_id)
    if input_type in {InputType.CON_BUTTON, InputType.CON_HAT, InputType.CON_AXIS}:
        result += f'{_PART_SEP}{controller_id}'
    return result


def save():
    mapping_to_write: dict[tuple[int, int], list[tuple[InputType, int, int]]] = dict()
    for key, value in _input_mapping.items():
        if value not in mapping_to_write:
            mapping_to_write[value] = []
        mapping_to_write[value].append(key)
    with open(_input_file, 'w') as file:
        for write_key, write_value in mapping_to_write.items():
            inputs = _INPUT_SEP.join(
                [
                    _get_save_input(item[0], item[1], item[2])
                    for item
                    in write_value
                ]
            )
            line = ('{}' + _PLAYER_SEP + '{}' + _EVENT_SEP + '{}').format(
                write_key[0],
                _event_names[write_key[1]],
                inputs
            )
            print(line, file=file)


def _take_event(event: pygame.event.Event):
    match event.type:
        case pygame.KEYUP | pygame.KEYDOWN:
            player_id, event_type = _map_event(InputType.KEYBOARD, event.key)
            return _log_event(player_id, event_type, 1 if event.type == pygame.KEYDOWN else 0)
        case pygame.MOUSEBUTTONUP | pygame.MOUSEBUTTONDOWN:
            player_id, event_type = _map_event(InputType.MOUSE, event.button)
            return _log_event(player_id, event_type, 1 if event.type == pygame.MOUSEBUTTONDOWN else 0)
        case pygame.JOYBUTTONUP | pygame.JOYBUTTONDOWN:
            player_id, event_type = _map_event(InputType.CON_BUTTON, event.button, event.instance_id)
            return _log_event(player_id, event_type, 1 if event.type == pygame.JOYBUTTONDOWN else 0)
        case pygame.JOYHATMOTION:
            for i, event_value in enumerate(_get_hat_values(event)):
                player_id, event_type = _map_event(InputType.CON_HAT, event.hat * 4 + i, event.instance_id)
                _log_event(player_id, event_type, event_value)
        case pygame.JOYAXISMOTION:
            axis_value_back_forth = (
                event.value * -1 if event.value < 0 else 0,
                event.value if event.value > 0 else 0,
            )
            for i, event_value in enumerate(axis_value_back_forth):
                player_id, event_type = _map_event(InputType.CON_AXIS, event.axis * 2 + i, event.instance_id)
                _log_event(player_id, event_type, event_value)
    return True


def take_events(events: Iterable[pygame.event.Event]):
    global _controller_states_prev
    global _controller_state_changes
    _controller_states_prev = copy.deepcopy(_controller_states)
    _controller_state_changes = []
    events = filter(_take_event, events)
    return list(events)


def _get_map_key(input_type: InputType, input_id: int, controller_id: int):
    return (
        input_type,
        input_id,
        controller_id,
    )


def _map_event(input_type: InputType, input_id: int, controller_id: int = 0):
    return _input_mapping.get(
        _get_map_key(input_type, input_id, controller_id),
        (0, TYPE_NONE,)
    )


def _log_event(player_id: int, event_type: int, event_value: float | int):
    if event_type != TYPE_NONE and _controller_states[player_id][event_type] != event_value:
        _controller_state_changes.append(
            StateChange(player_id, event_type, event_value)
        )
        _controller_states[player_id][event_type] = event_value
    return event_type != TYPE_SCREENSHOT


def get_input_frame():
    return InputFrame(_controller_states, _controller_states_prev, _controller_state_changes)

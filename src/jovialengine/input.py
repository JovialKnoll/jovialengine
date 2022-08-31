import os
import copy
from collections.abc import Iterable

import pygame

from .inputframe import ControllerStateChange, InputFrame


TYPE_NONE = -1
TYPE_MOUSE = -2
TYPE_PAUSE = 0
TYPE_SCREENSHOT = 1
_input_file: str | None = None
_max_players: int
_num_inputs: int
_controller_states: list[list[float | int]]
_controller_states_prev: list[list[float | int]]
_controller_state_changes: list[ControllerStateChange]
_pressed_mouse_buttons: dict[int, tuple[int, int]]


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
    global _pressed_mouse_buttons
    _controller_states = [[0] * _num_inputs for x in range(_max_players)]
    _controller_states_prev = [[0] * _num_inputs for x in range(_max_players)]
    _controller_state_changes = []
    _pressed_mouse_buttons = dict()


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
        if event.type == pygame.MOUSEBUTTONDOWN:
            _pressed_mouse_buttons[event.button] = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in _pressed_mouse_buttons:
                del _pressed_mouse_buttons[event.button]
        # do actual mapping
        # if mapping results in setting a value in controller state that is already set
        # for [player_id][event_type] then set event_type = TYPE_NONE
        player_id = 0
        event_type = TYPE_NONE
        event_value = None
        key = getattr(event, 'key', None)
        instance_id = getattr(event, 'instance_id', None)
        button = getattr(event, 'button', None)
        axis = getattr(event, 'axis', None)
        # replace the below with proper mapping later
        if key == pygame.K_ESCAPE:
            event_type = TYPE_PAUSE
        elif key == pygame.K_F12:
            event_type = TYPE_SCREENSHOT

        match event.type:
            case pygame.KEYUP | pygame.JOYBUTTONUP:
                event_value = 0
            case pygame.KEYDOWN | pygame.JOYBUTTONDOWN:
                event_value = 1
            case pygame.JOYAXISMOTION:
                event_value = event.value
                pass
            case pygame.JOYHATMOTION:
                # instance_id, hat, value
                # event_value = 1
                pass
        if _controller_states[player_id][event_type] != event_value:
            _controller_state_changes.append(
                ControllerStateChange(player_id, event_type, event_value)
            )
            _controller_states[player_id][event_type] = event_value


def getInputFrame():
    return InputFrame(_controller_states, _controller_states_prev, _controller_state_changes)

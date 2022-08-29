import os
import copy

import pygame


TYPE_NONE = -1
TYPE_MOUSE = -2
TYPE_PAUSE = 0
TYPE_SCREENSHOT = 1
_input_file: str | None = None
_max_players: int
_num_inputs: int
_controller_states: list[list[float | int]]
_controller_states_prev: list[list[float | int]]
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
    global _pressed_mouse_buttons
    _controller_states = [[0] * _num_inputs for x in range(_max_players)]
    _pressed_mouse_buttons = dict()
    copyToPrev()


def copyToPrev():
    global _controller_states_prev
    _controller_states_prev = copy.deepcopy(_controller_states)


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


def getInputStatus(player_id: int, action_type: int):
    return _controller_states[player_id][action_type]


def getMouseButtonStatus(button: int):
    if button not in _pressed_mouse_buttons:
        return False
    return _pressed_mouse_buttons[button]


def wasInputPressed(player_id: int, action_type: int):
    return _controller_states[player_id][action_type] == 1 \
        and _controller_states_prev[player_id][action_type] == 0


def getInputState():
    return "new class with state and helpful functions, probably"


def takeEvent(event: pygame.event.Event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        _pressed_mouse_buttons[event.button] = event.pos
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button in _pressed_mouse_buttons:
            del _pressed_mouse_buttons[event.button]
    # do actual mapping
    # if mapping results in setting a value in controller state that is already set
    # for [player_id][action_type] then set action_type = Action.TYPE_NONE
    player_id = 0
    action_type = TYPE_NONE
    action_value = None
    match event.type:
        case pygame.KEYUP:
            # key, mod, unicode, scancode
            action_value = 0
        case pygame.KEYDOWN:
            # key, mod, unicode, scancode
            action_value = 1
            # replace the below with proper mapping later
            if event.key == pygame.K_ESCAPE:
                action_type = TYPE_PAUSE
            elif event.key == pygame.K_F12:
                action_type = TYPE_SCREENSHOT
        case pygame.JOYBUTTONUP:
            # instance_id, button
            action_value = 0
        case pygame.JOYBUTTONDOWN:
            # instance_id, button
            action_value = 1
        case pygame.JOYHATMOTION:
            # instance_id, hat, value
            # action_value = 1
            pass
        case pygame.JOYAXISMOTION:
            # instance_id, axis, value
            # action_value = 1
            pass
    _controller_states[player_id][action_type] = action_value

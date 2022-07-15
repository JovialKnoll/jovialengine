import pygame

from . import config

import constants


class Action(object):
    ACTION_ID_NONE = -1
    ACTION_ID_MOUSE = -2
    __slots__ = (
        'player_id',
        'action_id',
        'action_value',
        'type',
        '__dict__',
    )

    def __init__(self, player_id: int, action_id: int, action_value: float | int, event: pygame.event.Event):
        self.player_id = player_id
        self.action_id = action_id
        self.action_value = action_value
        self.type = event.type
        self.__dict__ = event.__dict__


class Input(object):
    __slots__ = (
        '__pressed_mouse_buttons',
        'controller_states',
    )

    def __init__(self, max_players: int, num_inputs: int):
        # load in input mapping from config
        # make objects to hold onto current virtual gamepad states
        self.__pressed_mouse_buttons = dict()
        controller_states = [[0] * num_inputs for x in range(max_players)]

    def _getAction(self, event: pygame.event.Event):
        # do actual mapping
        # if mapping results in setting a value in controller state that is already set
        # for [player_id][action_id] then set action_id = Action.ACTION_ID_NONE
        return Action(0, 0, 0, event)

    def map(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.__pressed_mouse_buttons[event.button] = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in self.__pressed_mouse_buttons:
                del self.__pressed_mouse_buttons[event.button]
        action = self._getAction(event)
        self.controller_states[action.player_id][action.action_id] = action.action_value
        return action

    def mouseButtonStatus(self, button: int):
        if button not in self.__pressed_mouse_buttons:
            return False
        return self.__pressed_mouse_buttons[button]

    def clearMouseButtonStatus(self):
        self.__pressed_mouse_buttons = dict()

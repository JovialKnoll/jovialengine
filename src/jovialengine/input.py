import pygame


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

    def __init__(self, player_id: int, action_id: int, action_value: float | int | None, event: pygame.event.Event):
        self.player_id = player_id
        self.action_id = action_id
        self.action_value = action_value
        self.type = event.type
        self.__dict__ = event.__dict__


_pressed_mouse_buttons: dict[int, tuple[int, int]] = dict()
_controller_states: list[list[float | int]] | None = None


def init(max_players: int, num_inputs: int):
    global _controller_states
    # load in input mapping from config
    # make objects to hold onto current virtual gamepad states
    _controller_states = [[0] * num_inputs for x in range(max_players)]


def _getAction(event: pygame.event.Event):
    # do actual mapping
    # if mapping results in setting a value in controller state that is already set
    # for [player_id][action_id] then set action_id = Action.ACTION_ID_NONE
    player_id = 0
    action_id = Action.ACTION_ID_NONE
    action_value = None
    match event.type:
        case pygame.KEYUP:
            # key, mod, unicode, scancode
            action_value = 0
        case pygame.KEYDOWN:
            # key, mod, unicode, scancode
            action_value = 1
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
    return Action(player_id, action_id, action_value, event)


def mapEvent(event: pygame.event.Event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        _pressed_mouse_buttons[event.button] = event.pos
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button in _pressed_mouse_buttons:
            del _pressed_mouse_buttons[event.button]
    action = _getAction(event)
    _controller_states[action.player_id][action.action_id] = action.action_value
    return action


def getInputStatus(player_id: int, action_id: int):
    return _controller_states[player_id][action_id]


def getMouseButtonStatus(button: int):
    if button not in _pressed_mouse_buttons:
        return False
    return _pressed_mouse_buttons[button]


def clearMouseButtonStatus():
    global _pressed_mouse_buttons
    _pressed_mouse_buttons = dict()

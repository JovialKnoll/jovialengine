from collections.abc import Collection


class ControllerStateChange(object):
    __slots__ = (
        'player_id',
        'event_type',
        'new_value',
    )

    def __init__(self, player_id: int, event_type: int, new_value: float | int):
        self.player_id = player_id
        self.event_type = event_type
        self.new_value = new_value


class InputFrame(object):
    __slots__ = (
        '_controller_states',
        '_controller_states_prev',
        '_controller_state_changes',
    )

    def __init__(
        self,
        controller_states: list[list[float | int]],
        controller_states_prev: list[list[float | int]],
        controller_state_changes: list[ControllerStateChange]
    ):
        self._controller_states = controller_states
        self._controller_states_prev = controller_states_prev
        self._controller_state_changes = controller_state_changes

    def get_input_state(self, player_id: int, event_type: int):
        return self._controller_states[player_id][event_type]

    def was_player_input_pressed(self, player_id: int, event_type: int):
        for state_change in self._controller_state_changes:
            if state_change.new_value == 1 \
                    and state_change.event_type == event_type \
                    and state_change.player_id == player_id:
                return True
        return False

    def was_input_pressed(self, event_type: int):
        for state_change in self._controller_state_changes:
            if state_change.new_value == 1 \
                    and state_change.event_type == event_type:
                return True
        return False

    def was_any_player_input_pressed(self, player_id: int, event_types: Collection[int]):
        for state_change in self._controller_state_changes:
            if state_change.new_value == 1 \
                    and state_change.event_type in event_types \
                    and state_change.player_id == player_id:
                return True
        return False

    def was_any_input_pressed(self, event_types: Collection[int]):
        for state_change in self._controller_state_changes:
            if state_change.new_value == 1 \
                    and state_change.event_type in event_types:
                return True
        return False

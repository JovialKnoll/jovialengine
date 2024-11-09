from collections.abc import Collection


class StateChange(object):
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
        '_states',
        '_states_prev',
        'state_changes',
    )

    def __init__(
        self,
        states: list[list[float | int]],
        states_prev: list[list[float | int]],
        state_changes: list[StateChange]
    ):
        self._states = states
        self._states_prev = states_prev
        self.state_changes = state_changes

    def get_input_state(self, player_id: int, event_type: int):
        return self._states[player_id][event_type]

    def was_player_input_pressed(self, player_id: int, event_type: int):
        for state_change in self.state_changes:
            if state_change.new_value == 1 \
                    and state_change.event_type == event_type \
                    and state_change.player_id == player_id:
                return True
        return False

    def was_input_pressed(self, event_type: int):
        for state_change in self.state_changes:
            if state_change.new_value == 1 \
                    and state_change.event_type == event_type:
                return True
        return False

    def was_any_player_input_pressed(self, player_id: int, event_types: Collection[int]):
        for state_change in self.state_changes:
            if state_change.new_value == 1 \
                    and state_change.event_type in event_types \
                    and state_change.player_id == player_id:
                return True
        return False

    def was_any_input_pressed(self, event_types: Collection[int]):
        for state_change in self.state_changes:
            if state_change.new_value == 1 \
                    and state_change.event_type in event_types:
                return True
        return False

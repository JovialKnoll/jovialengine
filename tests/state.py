from jovialengine.saveable import Saveable


class State(Saveable):
    __slots__ = (
        'value',
    )

    def __init__(self, value):
        self.value = value

    def save(self):
        return self.value

    @classmethod
    def load(cls, save_data):
        value = save_data
        new_obj = cls(value)
        return new_obj

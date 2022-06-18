from jovialengine.modebase import ModeBase
from jovialengine.saveable import Saveable


class ModeGameMenu(ModeBase, Saveable):
    __slots__ = (
        'test_value',
    )

    def __init__(self):
        super().__init__()
        self.test_value = 1

    def save(self):
        return self.test_value

    @classmethod
    def load(cls, save_data):
        test_value = save_data
        new_obj = cls()
        new_obj.test_value = test_value
        return new_obj

    def _input(self, event):
        pass

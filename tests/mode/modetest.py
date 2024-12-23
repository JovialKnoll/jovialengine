import pygame

from jovialengine.modebase import ModeBase
from jovialengine.saveable import Saveable


class ModeTest(ModeBase, Saveable):
    _SPACE_SIZE = (8, 8)
    _CAMERA_SIZE = (4, 4)
    _CAMERA_OFFSET = (1, 1)

    __slots__ = (
        'test_value',
    )

    def __init__(self, sprite_pos: pygame.typing.Point=(0,0)):
        super().__init__()
        self._background.fill(pygame.Color('red'))
        self._background.set_at((2, 5), pygame.Color('black'))
        test_sprite = pygame.sprite.Sprite()
        test_sprite.image = pygame.Surface((1, 1))
        test_sprite.image.fill(pygame.Color('green'))
        test_sprite.rect = test_sprite.image.get_frect(topleft=sprite_pos)
        self.sprites_all.add(test_sprite)
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

    def _draw_post_camera(self, screen: pygame.Surface):
        screen.set_at((5, 0), pygame.Color('blue'))
        screen.set_at((5, 5), pygame.Color('blue'))

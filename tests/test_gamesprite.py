import unittest

import pygame

from jovialengine.gamesprite import GameSprite
import jovialengine.load as load


class TestSpriteA(GameSprite):
    pass

class TestSpriteB(TestSpriteA):
    pass

class TestSpriteC(GameSprite):
    def collide_TestSpriteA(self, other):
        pass

class GameSpriteLoading(GameSprite):
    def __init__(self, pos = (0, 0)):
        if not self._IMAGE_LOCATION:
            raise RuntimeError(
                "_IMAGE_LOCATION must be overridden in children of GameSprite"
            )
        if not self._ALPHA_OR_COLORKEY:
            raise RuntimeError(
                "_ALPHA_OR_COLORKEY must be overridden in children of GameSprite"
            )
        if self._COLLISION_MASK_LOCATION and not self._COLLISION_MASK_ALPHA_OR_COLORKEY:
            raise RuntimeError(
                "if _COLLISION_MASK_LOCATION if overridden, _COLLISION_MASK_ALPHA_OR_COLORKEY must also be overridden"
            )
        pygame.sprite.DirtySprite.__init__(self)
        self._input_frame = None
        self._seq: int | None = None
        self.dirty = 2  # always draw
        self.image = pygame.image.load(self._IMAGE_LOCATION)
        if self._ALPHA_OR_COLORKEY is not True and self._ALPHA_OR_COLORKEY is not False:
            self.image.set_colorkey(self._ALPHA_OR_COLORKEY)
        if self._IMAGE_SECTION_SIZE:
            self.source_rect = pygame.rect.Rect((0, 0), self._IMAGE_SECTION_SIZE)
            self.rect = pygame.rect.Rect((0, 0), self._IMAGE_SECTION_SIZE)
            self._seq = 0
            image_size = self.image.get_size()
            self._image_count_x = image_size[0] // self._IMAGE_SECTION_SIZE[0]
            self._image_count_y = image_size[1] // self._IMAGE_SECTION_SIZE[1]
        else:
            self.rect = self.image.get_rect()
        self.radius = None
        if self._COLLISION_RADIUS:
            self.radius = self._COLLISION_RADIUS
            self.mask = load.mask_circle(self.rect.size, self.radius)
        if self._COLLISION_MASK_LOCATION:
            surface = pygame.image.load(self._IMAGE_LOCATION)
            if self._ALPHA_OR_COLORKEY is not True and self._ALPHA_OR_COLORKEY is not False:
                surface.set_colorkey(self._ALPHA_OR_COLORKEY)
            self.mask = pygame.mask.from_surface(surface)
        if not self._COLLISION_RADIUS and not self._COLLISION_MASK_LOCATION:
            self.mask = load.mask_filled(self.rect.size)
        self.pos = pos

class TestSpriteCircle(GameSpriteLoading):
    _IMAGE_LOCATION = './assets/gfx/4x4_image.png'
    _ALPHA_OR_COLORKEY = (255, 0, 255)
    _COLLISION_RADIUS = 1.5

class TestSpriteRect(GameSpriteLoading):
    _IMAGE_LOCATION = './assets/gfx/4x4_image.png'
    _ALPHA_OR_COLORKEY = (255, 0, 255)

class TestSpriteMask(GameSpriteLoading):
    _IMAGE_LOCATION = './assets/gfx/4x4_image.png'
    _ALPHA_OR_COLORKEY = (255, 0, 255)
    _COLLISION_MASK_LOCATION = './assets/gfx/4x4_image.png'
    _COLLISION_MASK_ALPHA_OR_COLORKEY = (255, 0, 255)

class TestInput(unittest.TestCase):
    def test__get_labels_GameSprite(self):
        # Assert
        self.assertEqual(GameSprite._get_labels(), ('all',))

    def test__get_labels_TestSpriteA(self):
        # Assert
        self.assertEqual(TestSpriteA._get_labels(), ('TestSpriteA','all',))

    def test__get_labels_TestSpriteB(self):
        # Assert
        self.assertEqual(TestSpriteB._get_labels(), ('TestSpriteB','TestSpriteA','all',))

    def test_get_collide_labels_TestSpriteA(self):
        # Assert
        self.assertEqual(TestSpriteA.get_collide_labels(), ())

    def test_get_collide_labels_TestSpriteC(self):
        # Assert
        self.assertEqual(TestSpriteC.get_collide_labels(), (('TestSpriteA','collide_TestSpriteA',),))

    def test_does_collide_circles_false(self):
        # Arrange
        left = TestSpriteCircle((2.5, 3))
        right = TestSpriteCircle((8.5, 4))
        # Act
        does_collide = left.does_collide(right)
        # Assert
        self.assertFalse(does_collide)

    def test_does_collide_circles_true(self):
        # Arrange
        left = TestSpriteCircle((2.5, 3))
        right = TestSpriteCircle((3.99, 3))
        # Act
        does_collide = left.does_collide(right)
        # Assert
        self.assertTrue(does_collide)

    def test_does_collide_rects_false(self):
        # Arrange
        left = TestSpriteRect((2.5, 3))
        right = TestSpriteRect((8.5, 4))
        # Act
        does_collide = left.does_collide(right)
        # Assert
        self.assertFalse(does_collide)

    def test_does_collide_rects_true(self):
        # Arrange
        left = TestSpriteRect((2, 3))
        right = TestSpriteRect((5, 6))
        # Act
        does_collide = left.does_collide(right)
        # Assert
        self.assertTrue(does_collide)

    def test_does_collide_mask_false0(self):
        # Arrange
        left = TestSpriteMask((2, 3))
        right = TestSpriteMask((5, 3))
        # Act
        does_collide = left.does_collide(right)
        # Assert
        self.assertFalse(does_collide)

    def test_does_collide_mask_false1(self):
        # Arrange
        left = TestSpriteMask((3, 3))
        right = TestSpriteMask((6, 6))
        # Act
        does_collide = left.does_collide(right)
        # Assert
        self.assertFalse(does_collide)

    def test_does_collide_mask_true(self):
        # Arrange
        left = TestSpriteMask((4, 4))
        right = TestSpriteMask((6, 2))
        # Act
        does_collide = left.does_collide(right)
        # Assert
        self.assertTrue(does_collide)

    def test_does_collide_self_false(self):
        # Arrange
        left = TestSpriteMask((4, 4))
        right = left
        # Act
        does_collide = left.does_collide(right)
        # Assert
        self.assertFalse(does_collide)


if __name__ == '__main__':
    unittest.main()

import unittest

import pygame

from jovialengine.gamesprite import GameSprite
import jovialengine.load as load


def image(filename, alpha_or_colorkey=False):
    result = pygame.image.load(filename)
    if alpha_or_colorkey is not True and alpha_or_colorkey is not False:
        result.set_colorkey(alpha_or_colorkey)
    return result
load.image = image

class TestSpriteA(GameSprite):
    pass

class TestSpriteB(TestSpriteA):
    pass

class TestSpriteC(GameSprite):
    _GETS_INPUT = True
    def collide_TestSpriteA(self, other):
        pass

class TestSpriteD(GameSprite):
    def _take_state_change(self, state_change):
        print(state_change)

class TestSpriteCircle(GameSprite):
    _IMAGE_LOCATION = './assets/gfx/4x4_image.png'
    _ALPHA_OR_COLORKEY = (255, 0, 255)
    _COLLISION_RADIUS = 1.5

class TestSpriteRect(GameSprite):
    _IMAGE_LOCATION = './assets/gfx/4x4_image.png'
    _ALPHA_OR_COLORKEY = (255, 0, 255)

class TestSpriteMask(GameSprite):
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

    def test__get_labels_TestSpriteC(self):
        # Assert
        self.assertEqual(TestSpriteC._get_labels(), ('TestSpriteC','all','input','collide',))

    def test__get_labels_TestSpriteD(self):
        # Assert
        self.assertEqual(TestSpriteD._get_labels(), ('TestSpriteD','all','input',))

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
        right = TestSpriteMask((5, 5))
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

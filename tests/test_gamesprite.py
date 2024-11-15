import unittest

import pygame

from jovialengine.gamesprite import GameSprite


class TestSpriteA(GameSprite):
    pass

class TestSpriteB(TestSpriteA):
    pass

class TestSpriteC(GameSprite):
    def collide_TestSpriteA(self, other):
        pass

class TestSpriteCircle(GameSprite):
    _IMAGE_LOCATION = './assets/gfx/4x4_image.png'
    _ALPHA_OR_COLORKEY = (255, 0, 255)
    _COLLISION_RADIUS: 2.5

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
        try:
            left = TestSpriteCircle((2.5, 3))
        except pygame.error:
            pass
        try:
            right = TestSpriteCircle((8.5, 4))
        except pygame.error:
            pass
        # Act
        does_collide = left.does_collide(right)
        # Assert
        self.assertFalse(does_collide)


if __name__ == '__main__':
    unittest.main()

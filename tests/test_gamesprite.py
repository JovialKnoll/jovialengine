import unittest

import pygame

from jovialengine.gamesprite import GameSprite


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

class TestSpriteSheet(GameSprite):
    _IMAGE_LOCATION = './assets/gfx/6x4_sheet_tests.png'
    _ALPHA_OR_COLORKEY = (255, 0, 255)
    _IMAGE_SECTION_SIZE = (2, 2)
    _COLLISION_MASK_LOCATION = './assets/gfx/6x4_mask_tests.png'
    _COLLISION_MASK_ALPHA_OR_COLORKEY = (255, 0, 255)

class TestGameSprite(unittest.TestCase):
    IMAGE_POINTS = (
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
    )

    @classmethod
    def setUpClass(cls):
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def test_get_collision_labels_GameSprite(self):
        # Assert
        self.assertEqual(GameSprite.get_collision_labels(), frozenset(('GameSprite',)))

    def test_get_collision_labels_TestSpriteA(self):
        # Assert
        self.assertEqual(TestSpriteA.get_collision_labels(), frozenset(('TestSpriteA','GameSprite',)))

    def test_get_collision_labels_TestSpriteB(self):
        # Assert
        self.assertEqual(TestSpriteB.get_collision_labels(), frozenset(('TestSpriteB','TestSpriteA','GameSprite',)))

    def test_get_collision_labels_TestSpriteC(self):
        # Assert
        self.assertEqual(TestSpriteC.get_collision_labels(), frozenset(('TestSpriteC','GameSprite',)))

    def test_get_collision_labels_TestSpriteD(self):
        # Assert
        self.assertEqual(TestSpriteD.get_collision_labels(), frozenset(('TestSpriteD','GameSprite',)))

    def test_get_collides_with_TestSpriteA(self):
        # Assert
        self.assertEqual(TestSpriteA.get_collides_with(), frozenset(()))

    def test_get_collides_with_TestSpriteC(self):
        # Assert
        self.assertEqual(TestSpriteC.get_collides_with(), frozenset(('TestSpriteA',)))

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

    def test_does_collide_rects_round_false(self):
        # Arrange
        left = TestSpriteRect()
        left.rect.topleft = (0.00, 0.0)
        right = TestSpriteRect()
        right.rect.topleft = (4.0, 0.0)
        # Act
        does_collide = left.does_collide(right)
        # Assert
        self.assertFalse(does_collide)

    def test_does_collide_rects_round_true(self):
        # Arrange
        left = TestSpriteRect()
        left.rect.topleft = (0.01, 0.0)
        right = TestSpriteRect()
        right.rect.topleft = (4.0, 0.0)
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

    def test_does_collide_mask_round_false_0(self):
        # Arrange
        left = TestSpriteSheet()
        left.mask_seq = 4
        left.rect.topleft = (0.49, 0.0)
        right = TestSpriteSheet()
        right.mask_seq = 4
        right.rect.topleft = (2.0, 0.0)
        # Act
        does_collide = left.does_collide(right)
        # Assert
        self.assertFalse(does_collide)

    def test_does_collide_mask_round_false_1(self):
        # Arrange
        left = TestSpriteSheet()
        left.mask_seq = 4
        left.rect.topleft = (0.49, 0.0)
        right = TestSpriteSheet()
        right.mask_seq = 4
        right.rect.topleft = (2.0, 0.0)
        # Act
        does_collide = right.does_collide(left)
        # Assert
        self.assertFalse(does_collide)

    def test_does_collide_mask_round_true_0(self):
        # Arrange
        left = TestSpriteSheet()
        left.mask_seq = 4
        left.rect.topleft = (0.5, 0.0)
        right = TestSpriteSheet()
        right.mask_seq = 4
        right.rect.topleft = (2.0, 0.0)
        # Act
        does_collide = left.does_collide(right)
        # Assert
        self.assertTrue(does_collide)

    def test_does_collide_mask_round_true_1(self):
        # Arrange
        left = TestSpriteSheet()
        left.mask_seq = 4
        left.rect.topleft = (0.5, 0.0)
        right = TestSpriteSheet()
        right.mask_seq = 4
        right.rect.topleft = (2.0, 0.0)
        # Act
        does_collide = right.does_collide(left)
        # Assert
        self.assertTrue(does_collide)

    def test_seq(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.seq = 6
        # Assert
        self.assertEqual(sprite.seq, 0)

    def test_seq_image_0(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.seq = 0
        # Assert
        self.assertEqual(sprite.image.size, (2, 2))
        for pos in self.IMAGE_POINTS:
            self.assertEqual(sprite.image.get_at(pos), pygame.Color('red'))

    def test_seq_image_1(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.seq = 1
        # Assert
        self.assertEqual(sprite.image.size, (2, 2))
        for pos in self.IMAGE_POINTS:
            self.assertEqual(sprite.image.get_at(pos), pygame.Color('green'))

    def test_seq_image_2(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.seq = 2
        # Assert
        self.assertEqual(sprite.image.size, (2, 2))
        for pos in self.IMAGE_POINTS:
            self.assertEqual(sprite.image.get_at(pos), pygame.Color('blue'))

    def test_seq_image_3(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.seq = 3
        # Assert
        self.assertEqual(sprite.image.size, (2, 2))
        for pos in self.IMAGE_POINTS:
            self.assertEqual(sprite.image.get_at(pos), pygame.Color('black'))

    def test_seq_image_4(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.seq = 4
        # Assert
        self.assertEqual(sprite.image.size, (2, 2))
        for pos in self.IMAGE_POINTS:
            self.assertEqual(sprite.image.get_at(pos), pygame.Color('white'))

    def test_seq_image_5(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.seq = 5
        # Assert
        self.assertEqual(sprite.image.size, (2, 2))
        for pos in self.IMAGE_POINTS:
            self.assertEqual(sprite.image.get_at(pos), pygame.Color('black'))

    def test_mask_seq(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.mask_seq = 6
        # Assert
        self.assertEqual(sprite.mask_seq, 0)

    def test_mask_seq_mask_0(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.mask_seq = 0
        # Assert
        self.assertEqual(sprite.mask.get_size(), (2, 2))
        self.assertEqual(sprite.mask.get_at((0, 0)), 0)
        self.assertEqual(sprite.mask.get_at((1, 0)), 1)
        self.assertEqual(sprite.mask.get_at((0, 1)), 1)
        self.assertEqual(sprite.mask.get_at((1, 1)), 1)

    def test_mask_seq_mask_1(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.mask_seq = 1
        # Assert
        self.assertEqual(sprite.mask.get_size(), (2, 2))
        self.assertEqual(sprite.mask.get_at((0, 0)), 1)
        self.assertEqual(sprite.mask.get_at((1, 0)), 0)
        self.assertEqual(sprite.mask.get_at((0, 1)), 1)
        self.assertEqual(sprite.mask.get_at((1, 1)), 1)

    def test_mask_seq_mask_2(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.mask_seq = 2
        # Assert
        self.assertEqual(sprite.mask.get_size(), (2, 2))
        self.assertEqual(sprite.mask.get_at((0, 0)), 1)
        self.assertEqual(sprite.mask.get_at((1, 0)), 1)
        self.assertEqual(sprite.mask.get_at((0, 1)), 0)
        self.assertEqual(sprite.mask.get_at((1, 1)), 1)

    def test_mask_seq_mask_3(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.mask_seq = 3
        # Assert
        self.assertEqual(sprite.mask.get_size(), (2, 2))
        self.assertEqual(sprite.mask.get_at((0, 0)), 1)
        self.assertEqual(sprite.mask.get_at((1, 0)), 1)
        self.assertEqual(sprite.mask.get_at((0, 1)), 1)
        self.assertEqual(sprite.mask.get_at((1, 1)), 0)

    def test_mask_seq_mask_4(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.mask_seq = 4
        # Assert
        self.assertEqual(sprite.mask.get_size(), (2, 2))
        self.assertEqual(sprite.mask.get_at((0, 0)), 1)
        self.assertEqual(sprite.mask.get_at((1, 0)), 1)
        self.assertEqual(sprite.mask.get_at((0, 1)), 1)
        self.assertEqual(sprite.mask.get_at((1, 1)), 1)

    def test_mask_seq_mask_5(self):
        # Arrange
        sprite = TestSpriteSheet()
        # Act
        sprite.mask_seq = 5
        # Assert
        self.assertEqual(sprite.mask.get_size(), (2, 2))
        self.assertEqual(sprite.mask.get_at((0, 0)), 0)
        self.assertEqual(sprite.mask.get_at((1, 0)), 0)
        self.assertEqual(sprite.mask.get_at((0, 1)), 0)
        self.assertEqual(sprite.mask.get_at((1, 1)), 0)


if __name__ == '__main__':
    unittest.main()

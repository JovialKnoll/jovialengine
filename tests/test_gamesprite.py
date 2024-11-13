import unittest

from jovialengine.gamesprite import GameSprite


class TestSpriteA(GameSprite):
    pass

class TestSpriteB(TestSpriteA):
    pass

class TestSpriteC(GameSprite):
    def collide_TestSpriteA(self, other):
        pass

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


if __name__ == '__main__':
    unittest.main()

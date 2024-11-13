import unittest

from jovialengine.gamesprite import GameSprite


class TestInput(unittest.TestCase):
    def test__get_labels_GameSprite(self):
        # Assert
        self.assertEqual(GameSprite._get_labels(), ['all'])


if __name__ == '__main__':
    unittest.main()

import unittest
import os

import pygame

from mode import ModeTest


class TestModeBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def test_draw(self):
        # Arrange
        screen = pygame.Surface((6, 6))
        screen.fill(pygame.Color('white'))
        mode = ModeTest()
        # Act
        mode.draw(screen)
        # Assert
        got = ""
        for y in range(6):
            for x in range(6):
                color = screen.get_at((x, y))
                if color == pygame.Color('white'):
                    got += "W"
                elif color == pygame.Color('red'):
                    got += "r"
                elif color == pygame.Color('green'):
                    got += "g"
                elif color == pygame.Color('blue'):
                    got += "b"
                elif color == pygame.Color('black'):
                    got += "B"
            got += os.linesep
        expected = "WWWWWb" + os.linesep \
            + "WrrrrW" + os.linesep \
            + "WrrgrW" + os.linesep \
            + "WrrrrW" + os.linesep \
            + "WrBrrW" + os.linesep \
            + "WWWWWb" + os.linesep
        self.assertEqual(got, expected)

    def test_cleanup(self):
        # Arrange
        mode = ModeTest()
        # Act
        mode.cleanup()
        # Assert
        self.assertEqual(len(mode.sprites_all), 0)


if __name__ == '__main__':
    unittest.main()

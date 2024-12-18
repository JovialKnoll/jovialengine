import unittest
import os

import pygame

from mode import ModeTest


class TestModeBase(unittest.TestCase):
    DRAW_EXPECTED = "WWWWWb" + os.linesep \
                   + "WrrrrW" + os.linesep \
                   + "WrrgrW" + os.linesep \
                   + "WrrrrW" + os.linesep \
                   + "WrBrrW" + os.linesep \
                   + "WWWWWb" + os.linesep

    @staticmethod
    def get_surface_string(surface: pygame.Surface):
        result = ""
        for y in range(surface.height):
            for x in range(surface.width):
                color = surface.get_at((x, y))
                if color == pygame.Color('white'):
                    result += "W"
                elif color == pygame.Color('red'):
                    result += "r"
                elif color == pygame.Color('green'):
                    result += "g"
                elif color == pygame.Color('blue'):
                    result += "b"
                elif color == pygame.Color('black'):
                    result += "B"
            result += os.linesep
        return result

    @classmethod
    def setUpClass(cls):
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    def test_draw(self):
        # Arrange
        screen = pygame.Surface((6, 6))
        screen.fill(pygame.Color('white'))
        mode = ModeTest((3, 3))
        mode._camera.topleft = (1, 2)
        # Act
        mode.draw(screen)
        # Assert
        draw_result = self.get_surface_string(screen)
        self.assertEqual(draw_result, self.DRAW_EXPECTED)

    def test_draw_rounding_camera(self):
        # Arrange
        screen = pygame.Surface((6, 6))
        screen.fill(pygame.Color('white'))
        mode = ModeTest((3, 3))
        mode._camera.topleft = (0.9, 1.9)
        # Act
        mode.draw(screen)
        # Assert
        draw_result = self.get_surface_string(screen)
        self.assertEqual(draw_result, self.DRAW_EXPECTED)

    def test_draw_rounding_sprite(self):
        # Arrange
        screen = pygame.Surface((6, 6))
        screen.fill(pygame.Color('white'))
        mode = ModeTest((2.9, 2.9))
        mode._camera.topleft = (1, 2)
        # Act
        mode.draw(screen)
        # Assert
        draw_result = self.get_surface_string(screen)
        self.assertEqual(draw_result, self.DRAW_EXPECTED)

    def test_draw_rounding_both(self):
        # Arrange
        screen = pygame.Surface((6, 6))
        screen.fill(pygame.Color('white'))
        mode = ModeTest((2.9, 2.9))
        mode._camera.topleft = (0.9, 1.9)
        # Act
        mode.draw(screen)
        # Assert
        draw_result = self.get_surface_string(screen)
        self.assertEqual(draw_result, self.DRAW_EXPECTED)

    def test_cleanup(self):
        # Arrange
        mode = ModeTest()
        # Act
        mode.cleanup()
        # Assert
        self.assertEqual(len(mode.sprites_all), 0)


if __name__ == '__main__':
    unittest.main()

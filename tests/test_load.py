import unittest
import os

import pygame

import jovialengine.load as load


class TestLoad(unittest.TestCase):
    @staticmethod
    def get_mask_string(mask: pygame.Mask):
        size = mask.get_size()
        result = ""
        for y in range(size[1]):
            for x in range(size[0]):
                bit = surface.get_at((x, y))
                result += str(bit)
            result += os.linesep
        return result

    def test_mask_circle_even(self):
        # Arrange
        size = (32, 32)
        radius = 16
        # Act
        mask = load.mask_circle(size, radius)
        # Assert
        mask_result = self.get_mask_string(mask)
        print(mask_result)

    def test_mask_circle_odd(self):
        # Arrange
        size = (31, 31)
        radius = 15.5
        # Act
        mask = load.mask_circle(size, radius)
        # Assert
        mask_result = self.get_mask_string(mask)
        print(mask_result)


if __name__ == '__main__':
    unittest.main()

import unittest
import os

import jovialengine.load as load


class TestLoad(unittest.TestCase):
    def test_mask_circle_even(self):
        # Arrange
        size = (32, 32)
        radius = 16
        # Act
        mask = load.mask_circle(size, radius)
        # Assert

    def test_mask_circle_odd(self):
        # Arrange
        size = (31, 31)
        radius = 15.5
        # Act
        mask = load.mask_circle(size, radius)
        # Assert


if __name__ == '__main__':
    unittest.main()

import unittest

import pygame

import jovialengine.utility as utility


class TestUtility(unittest.TestCase):
    def test_clamp(self):
        # Assert
        self.assertEqual(
            utility.clamp(123, 5, 10),
            10
        )
        self.assertEqual(
            utility.clamp(-123, 5, 10),
            5
        )
        self.assertEqual(
            utility.clamp(12, 3, 33),
            12
        )

    def test_get_int_movement(self):
        # Arrange
        tracking = 0.6
        # Act
        tracking, tracking_int = utility.get_int_movement(tracking, 3.75, 10)
        # Assert
        self.assertEqual(tracking_int, 38)
        self.assertTrue(0.0999999999 < tracking < 0.1000000001)

    def test_get_positional_channel_mix(self):
        # Arrange
        pos = (100, 100)
        camera = pygame.Rect(10, 0, 320, 240)
        # Act
        result = utility.get_positional_channel_mix(pos, camera)
        # Assert
        self.assertEqual(result, (0.9231914344987546, 0.5420440747442257))

    def test_binary(self):
        # Assert
        self.assertEqual(
            utility.binary(1.0, 2.0, 0.0),
            1
        )
        self.assertEqual(
            utility.binary(1.0, 2.0, 0.99999),
            1
        )
        self.assertEqual(
            utility.binary(1.0, 2.0, 1.0),
            2
        )
        self.assertEqual(
            utility.binary(1.0, 2.0, 1),
            2
        )

    def test_lerp(self):
        # Assert
        self.assertEqual(
            utility.lerp(1.0, 2.0, 0.0),
            1
        )
        self.assertEqual(
            utility.lerp(1.0, 2.0, 0.25),
            1.25
        )
        self.assertEqual(
            utility.lerp(1.0, 2.0, 0.75),
            1.75
        )
        self.assertEqual(
            utility.lerp(1.0, 2.0, 1.0),
            2
        )

    def test_inc_speed_lerp(self):
        # Assert
        self.assertEqual(
            utility.inc_speed_lerp(1.0, 2.0, 0.0),
            1
        )
        self.assertEqual(
            utility.inc_speed_lerp(1.0, 2.0, 0.25),
            1.0625
        )
        self.assertEqual(
            utility.inc_speed_lerp(1.0, 2.0, 0.75),
            1.5625
        )
        self.assertEqual(
            utility.inc_speed_lerp(1.0, 2.0, 1.0),
            2
        )

    def test_dec_speed_lerp(self):
        # Assert
        self.assertEqual(
            utility.dec_speed_lerp(1.0, 2.0, 0.0),
            1
        )
        self.assertEqual(
            utility.dec_speed_lerp(1.0, 2.0, 0.25),
            1.4375
        )
        self.assertEqual(
            utility.dec_speed_lerp(1.0, 2.0, 0.75),
            1.9375
        )
        self.assertEqual(
            utility.dec_speed_lerp(1.0, 2.0, 1.0),
            2
        )

    def test_inc_dec_speed_lerp(self):
        # Assert
        self.assertEqual(
            utility.inc_dec_speed_lerp(1.0, 2.0, 0.0),
            1
        )
        self.assertEqual(
            utility.inc_dec_speed_lerp(1.0, 2.0, 0.25),
            1.125
        )
        self.assertEqual(
            utility.inc_dec_speed_lerp(1.0, 2.0, 0.75),
            1.875
        )
        self.assertEqual(
            utility.inc_dec_speed_lerp(1.0, 2.0, 1.0),
            2
        )

    def test_dec_inc_speed_lerp(self):
        # Assert
        self.assertEqual(
            utility.dec_inc_speed_lerp(1.0, 2.0, 0.0),
            1
        )
        self.assertEqual(
            utility.dec_inc_speed_lerp(1.0, 2.0, 0.25),
            1.375
        )
        self.assertEqual(
            utility.dec_inc_speed_lerp(1.0, 2.0, 0.75),
            1.625
        )
        self.assertEqual(
            utility.dec_inc_speed_lerp(1.0, 2.0, 1.0),
            2
        )


if __name__ == '__main__':
    unittest.main()

import unittest

import jovialengine.utility as utility


class TestUtility(unittest.TestCase):
    def test_clamp(self):
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

    def test_getIntMovement(self):
        tracking = 0.6
        tracking_int = 0
        tracking, tracking_int = utility.getIntMovement(tracking, 3.75, 10)
        self.assertEqual(tracking_int, 38)
        self.assertTrue(tracking < 0.1000000001 and tracking > 0.0999999999)

    def test_binary(self):
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

    def test_incSpeedLerp(self):
        self.assertEqual(
            utility.incSpeedLerp(1.0, 2.0, 0.0),
            1
        )
        self.assertEqual(
            utility.incSpeedLerp(1.0, 2.0, 0.25),
            1.0625
        )
        self.assertEqual(
            utility.incSpeedLerp(1.0, 2.0, 0.75),
            1.5625
        )
        self.assertEqual(
            utility.incSpeedLerp(1.0, 2.0, 1.0),
            2
        )

    def test_decSpeedLerp(self):
        self.assertEqual(
            utility.decSpeedLerp(1.0, 2.0, 0.0),
            1
        )
        self.assertEqual(
            utility.decSpeedLerp(1.0, 2.0, 0.25),
            1.4375
        )
        self.assertEqual(
            utility.decSpeedLerp(1.0, 2.0, 0.75),
            1.9375
        )
        self.assertEqual(
            utility.decSpeedLerp(1.0, 2.0, 1.0),
            2
        )

    def test_incDecSpeedLerp(self):
        self.assertEqual(
            utility.incDecSpeedLerp(1.0, 2.0, 0.0),
            1
        )
        self.assertEqual(
            utility.incDecSpeedLerp(1.0, 2.0, 0.25),
            1.125
        )
        self.assertEqual(
            utility.incDecSpeedLerp(1.0, 2.0, 0.75),
            1.875
        )
        self.assertEqual(
            utility.incDecSpeedLerp(1.0, 2.0, 1.0),
            2
        )

    def test_decIncSpeedLerp(self):
        self.assertEqual(
            utility.decIncSpeedLerp(1.0, 2.0, 0.0),
            1
        )
        self.assertEqual(
            utility.decIncSpeedLerp(1.0, 2.0, 0.25),
            1.375
        )
        self.assertEqual(
            utility.decIncSpeedLerp(1.0, 2.0, 0.75),
            1.625
        )
        self.assertEqual(
            utility.decIncSpeedLerp(1.0, 2.0, 1.0),
            2
        )


if __name__ == '__main__':
    unittest.main()

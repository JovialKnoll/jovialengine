import unittest
import sys
import os
sys.path.append(
    os.path.dirname(os.path.realpath(__file__)) + "/../src/jovialengine"
)
import utility


class TestUtility(unittest.TestCase):
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

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

if __name__ == '__main__':
    unittest.main()

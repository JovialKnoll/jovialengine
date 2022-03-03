import unittest
import jovialengine.utility as utility


class TestUtility(unittest.TestCase):
    def test_binary(self):
        self.assertEqual(
            utility.binary(1, 2, 0.0),
            1
        )
        self.assertEqual(
            utility.binary(1, 2, 0.99999),
            1
        )
        self.assertEqual(
            utility.binary(1, 2, 1.0),
            2
        )
        self.assertEqual(
            utility.binary(1, 2, 1),
            2
        )

if __name__ == '__main__':
    unittest.main()

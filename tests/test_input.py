import unittest
import os

import jovialengine.input as input


class TestInput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        input.init(
            os.path.join('.', 'input.cfg'),
            1,
            (
                "Left",
                "Right",
                "Up",
                "Down",
                "Confirm",
                "Cancel",
            )
        )

    def test_init(self):
        # Assert
        self.assertEqual(len(input._controller_states), 1)
        self.assertEqual(len(input._controller_states[0]), 8)


if __name__ == '__main__':
    unittest.main()

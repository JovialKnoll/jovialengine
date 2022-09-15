import unittest
import os

import pygame

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
            ),
            (
                input.InputDefault(0, input.EVENT_TYPE_START_POS, input.InputType.KEYBOARD, pygame.K_a),
            )
        )

    def test_init(self):
        # Assert
        self.assertEqual(len(input._controller_states), 1)
        self.assertEqual(len(input._controller_states[0]), 8)


if __name__ == '__main__':
    unittest.main()

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
                input.InputDefault(0, input.EVENT_TYPE_START_POS + 0, input.InputType.KEYBOARD, pygame.K_a),
                input.InputDefault(0, input.EVENT_TYPE_START_POS + 1, input.InputType.KEYBOARD, pygame.K_d),
                input.InputDefault(0, input.EVENT_TYPE_START_POS + 2, input.InputType.KEYBOARD, pygame.K_w),
                input.InputDefault(0, input.EVENT_TYPE_START_POS + 3, input.InputType.KEYBOARD, pygame.K_s),
            )
        )

    def test__controller_states_init(self):
        # Assert
        self.assertEqual(len(input._controller_states), 1)
        self.assertEqual(len(input._controller_states[0]), 8)

    def test__controller_states_prev_init(self):
        # Assert
        self.assertEqual(len(input._controller_states_prev), 1)
        self.assertEqual(len(input._controller_states_prev[0]), 8)

    def test__input_mapping_init(self):
        # Arrange
        expected_input_mapping = {
            (input.InputType.KEYBOARD, pygame.K_ESCAPE, 0): (0, input.TYPE_PAUSE),
            (input.InputType.KEYBOARD, pygame.K_F12, 0): (0, input.TYPE_SCREENSHOT),
            (input.InputType.CON_BUTTON, input._CONTROLLER_PAUSE_BUTTON, 0): (0, input.TYPE_PAUSE),
            (input.InputType.KEYBOARD, pygame.K_a, 0): (0, input.EVENT_TYPE_START_POS + 0),
            (input.InputType.KEYBOARD, pygame.K_d, 0): (0, input.EVENT_TYPE_START_POS + 1),
            (input.InputType.KEYBOARD, pygame.K_w, 0): (0, input.EVENT_TYPE_START_POS + 2),
            (input.InputType.KEYBOARD, pygame.K_s, 0): (0, input.EVENT_TYPE_START_POS + 3),
        }
        # Assert
        self.assertEqual(input._input_mapping, expected_input_mapping)

    def test__getInputIdDisplay_keyboard(self):
        # Assert
        self.assertEqual(input._getInputIdDisplay(input.InputType.KEYBOARD, pygame.K_a), "a")

    def test__getInputIdDisplay_hat(self):
        # Assert
        self.assertEqual(input._getInputIdDisplay(input.InputType.CON_HAT, 2), "0U")

    def test_getEventWithControls(self):
        # Assert
        self.assertEqual(input.getEventWithControls(0, input.EVENT_TYPE_START_POS + 2), "Up: KEY-w")

    def test_getEventName(self):
        # Assert
        self.assertEqual(input.getEventName(input.EVENT_TYPE_START_POS + 3), "Down")

    def test_save_and_load(self):
        # Arrange
        expected = input._input_mapping
        # Act
        input.save()
        input._load()
        # Assert
        self.assertEqual(input._input_mapping, expected)

    def test_takeEvents(self):
        # Arrange
        events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_d}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_s}),
        ]
        # Act
        input.takeEvents(events)
        input_frame = input.getInputFrame()
        # Assert
        self.assertEqual(input_frame._controller_states, [[0, 0, 0, 1, 0, 1, 0, 0,]])


if __name__ == '__main__':
    unittest.main()

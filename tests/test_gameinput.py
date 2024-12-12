import unittest
import os

import pygame

import jovialengine.gameinput as gameinput


class TestGameInput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        gameinput.init(
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
                gameinput.InputDefault(0, gameinput.EVENT_TYPE_START_POS + 0, gameinput.InputType.KEYBOARD, pygame.K_a),
                gameinput.InputDefault(0, gameinput.EVENT_TYPE_START_POS + 1, gameinput.InputType.KEYBOARD, pygame.K_d),
                gameinput.InputDefault(0, gameinput.EVENT_TYPE_START_POS + 2, gameinput.InputType.KEYBOARD, pygame.K_w),
                gameinput.InputDefault(0, gameinput.EVENT_TYPE_START_POS + 3, gameinput.InputType.KEYBOARD, pygame.K_s),
            )
        )

    def test__controller_states_init(self):
        # Assert
        self.assertEqual(len(gameinput._controller_states), 1)
        self.assertEqual(len(gameinput._controller_states[0]), 8)

    def test__controller_states_prev_init(self):
        # Assert
        self.assertEqual(len(gameinput._controller_states_prev), 1)
        self.assertEqual(len(gameinput._controller_states_prev[0]), 8)

    def test__input_mapping_init(self):
        # Arrange
        expected_input_mapping = {
            (gameinput.InputType.KEYBOARD, pygame.K_ESCAPE, 0): (0, gameinput.TYPE_PAUSE),
            (gameinput.InputType.KEYBOARD, pygame.K_F12, 0): (0, gameinput.TYPE_SCREENSHOT),
            (gameinput.InputType.CON_BUTTON, gameinput._CONTROLLER_PAUSE_BUTTON, 0): (0, gameinput.TYPE_PAUSE),
            (gameinput.InputType.KEYBOARD, pygame.K_a, 0): (0, gameinput.EVENT_TYPE_START_POS + 0),
            (gameinput.InputType.KEYBOARD, pygame.K_d, 0): (0, gameinput.EVENT_TYPE_START_POS + 1),
            (gameinput.InputType.KEYBOARD, pygame.K_w, 0): (0, gameinput.EVENT_TYPE_START_POS + 2),
            (gameinput.InputType.KEYBOARD, pygame.K_s, 0): (0, gameinput.EVENT_TYPE_START_POS + 3),
        }
        # Assert
        self.assertEqual(gameinput._input_mapping, expected_input_mapping)

    def test__get_input_id_display_keyboard(self):
        # Assert
        self.assertEqual(gameinput._get_input_id_display(gameinput.InputType.KEYBOARD, pygame.K_a), "a")

    def test__get_input_id_display_hat(self):
        # Assert
        self.assertEqual(gameinput._get_input_id_display(gameinput.InputType.CON_HAT, 2), "0U")

    def test_get_event_with_controls(self):
        # Assert
        self.assertEqual(gameinput.get_event_with_controls(0, gameinput.EVENT_TYPE_START_POS + 2), "Up: KEY-w")

    def test_get_event_name(self):
        # Assert
        self.assertEqual(gameinput.get_event_name(gameinput.EVENT_TYPE_START_POS + 3), "Down")

    def test_save_and_load(self):
        # Arrange
        expected = gameinput._input_mapping
        # Act
        gameinput.save()
        gameinput._load()
        # Assert
        self.assertEqual(gameinput._input_mapping, expected)

    def test_take_events(self):
        # Arrange
        events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_d}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_s}),
        ]
        # Act
        gameinput.take_events(events)
        input_frame = gameinput.get_input_frame()
        # Assert
        self.assertEqual(input_frame._states, [[0, 0, 0, 1, 0, 1, 0, 0,]])
        self.assertTrue(input_frame.was_player_input_pressed(0, gameinput.EVENT_TYPE_START_POS + 1))
        self.assertTrue(input_frame.was_input_pressed(gameinput.EVENT_TYPE_START_POS + 3))


if __name__ == '__main__':
    unittest.main()

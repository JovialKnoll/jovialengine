import unittest

import pygame

import jovialengine.display as display


class TestDisplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        display.upscale = 3
        display.screen_size = (320, 240)

    @staticmethod
    def set_up_full_screen():
        display.is_fullscreen = True
        display._fullscreen_offset = [50, 100]

    @staticmethod
    def set_up_windowed():
        display.is_fullscreen = False
        display._fullscreen_offset = None

    def test_scale_mouse_input_fullscreen_button(self):
        # Arrange
        self.set_up_full_screen()
        event_dict = {
            'pos': (400, 800),
            'button': 1,
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        result_event = display.scale_mouse_input(event)
        # Assert
        self.assertEqual(result_event.pos, (116, 233))
        self.assertEqual(result_event.button, 1)

    def test_scale_mouse_input_fullscreen_motion(self):
        # Arrange
        self.set_up_full_screen()
        event_dict = {
            'pos': (400, 800),
            'rel': (100, 200),
            'buttons': (1,),
        }
        event = pygame.event.Event(pygame.MOUSEMOTION, event_dict)
        # Act
        result_event = display.scale_mouse_input(event)
        # Assert
        self.assertEqual(result_event.pos, (116, 233))
        self.assertEqual(result_event.rel, (33, 66))
        self.assertEqual(result_event.buttons, (1,))

    def test_scale_mouse_input_windowed_button(self):
        # Arrange
        self.set_up_windowed()
        event_dict = {
            'pos': (400, 800),
            'button': 1,
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        result_event = display.scale_mouse_input(event)
        # Assert
        self.assertEqual(result_event.pos, (133, 266))
        self.assertEqual(result_event.button, 1)

    def test_scale_mouse_input_windowed_motion(self):
        # Arrange
        self.set_up_windowed()
        event_dict = {
            'pos': (400, 800),
            'rel': (100, 200),
            'buttons': (1,),
        }
        event = pygame.event.Event(pygame.MOUSEMOTION, event_dict)
        # Act
        result_event = display.scale_mouse_input(event)
        # Assert
        self.assertEqual(result_event.pos, (133, 266))
        self.assertEqual(result_event.rel, (33, 66))
        self.assertEqual(result_event.buttons, (1,))

    def test_is_in_screen_true(self):
        # Arrange
        self.set_up_windowed()
        # Act
        result = display.is_in_screen((2, 3))
        # Assert
        self.assertTrue(result)

    def test_is_in_screen_false(self):
        # Arrange
        self.set_up_windowed()
        # Act
        result = display.is_in_screen((-2, 3))
        # Assert
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

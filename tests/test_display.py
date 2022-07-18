import unittest

import pygame

import jovialengine.display as display


class TestDisplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        display.upscale = 3
        display.screen_size = (320, 240)

    @staticmethod
    def setUpFullScreen():
        display.is_fullscreen = True
        display._fullscreen_offset = [50, 100]

    @staticmethod
    def setUpWindowed():
        display.is_fullscreen = False
        display._fullscreen_offset = None

    def test_scaleMouseInput_fullscreen_button(self):
        # Arrange
        self.setUpFullScreen()
        event_dict = {
            'pos': (400, 800),
            'button': 1,
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        result_event = display.scaleMouseInput(event)
        # Assert
        self.assertEqual(result_event.pos, (116, 233))
        self.assertEqual(result_event.button, 1)

    def test_scaleMouseInput_fullscreen_motion(self):
        # Arrange
        self.setUpFullScreen()
        event_dict = {
            'pos': (400, 800),
            'rel': (100, 200),
            'buttons': (1,),
        }
        event = pygame.event.Event(pygame.MOUSEMOTION, event_dict)
        # Act
        result_event = display.scaleMouseInput(event)
        # Assert
        self.assertEqual(result_event.pos, (116, 233))
        self.assertEqual(result_event.rel, (33, 66))
        self.assertEqual(result_event.buttons, (1,))

    def test_scaleMouseInput_windowed_button(self):
        # Arrange
        self.setUpWindowed()
        event_dict = {
            'pos': (400, 800),
            'button': 1,
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        result_event = display.scaleMouseInput(event)
        # Assert
        self.assertEqual(result_event.pos, (133, 266))
        self.assertEqual(result_event.button, 1)

    def test_scaleMouseInput_windowed_motion(self):
        # Arrange
        self.setUpWindowed()
        event_dict = {
            'pos': (400, 800),
            'rel': (100, 200),
            'buttons': (1,),
        }
        event = pygame.event.Event(pygame.MOUSEMOTION, event_dict)
        # Act
        result_event = display.scaleMouseInput(event)
        # Assert
        self.assertEqual(result_event.pos, (133, 266))
        self.assertEqual(result_event.rel, (33, 66))
        self.assertEqual(result_event.buttons, (1,))

    def test_isInScreen_true(self):
        # Arrange
        self.setUpWindowed()
        # Act
        result = display.isInScreen((2, 3))
        # Assert
        self.assertTrue(result)

    def test_isInScreen_false(self):
        # Arrange
        self.setUpWindowed()
        # Act
        result = display.isInScreen((-2, 3))
        # Assert
        self.assertFalse(result)

    def test_getPositionalChannelMix(self):
        # Arrange
        self.setUpWindowed()
        # Act
        result = display.getPositionalChannelMix(90)
        # Assert
        self.assertEqual(result, (0.9231914344987546, 0.5420440747442257))


if __name__ == '__main__':
    unittest.main()

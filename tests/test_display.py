import unittest

import pygame

import jovialengine.display as display


class DisplayForTestFullscreen(display.Display):
    def __init__(self):
        self.is_fullscreen = True
        self._fullscreen_offset = [50, 100]
        self.upscale = 2


class DisplayForTestWindowed(display.Display):
    def __init__(self):
        self.is_fullscreen = False
        self._fullscreen_offset = None
        self.upscale = 3


class TestDisplay(unittest.TestCase):
    def test_scaleMouseInput_fullscreen_button(self):
        # Arrange
        disp = DisplayForTestFullscreen()
        event_dict = {
            'pos': (400, 800),
            'button': 1,
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        result_event = disp.scaleMouseInput(event)
        # Assert
        self.assertEqual(result_event.pos, (175, 350))
        self.assertEqual(result_event.button, 1)

    def test_scaleMouseInput_fullscreen_motion(self):
        # Arrange
        disp = DisplayForTestFullscreen()
        event_dict = {
            'pos': (400, 800),
            'rel': (100, 200),
            'buttons': (1),
        }
        event = pygame.event.Event(pygame.MOUSEMOTION, event_dict)
        # Act
        result_event = disp.scaleMouseInput(event)
        # Assert
        self.assertEqual(result_event.pos, (175, 350))
        self.assertEqual(result_event.rel, (50, 100))
        self.assertEqual(result_event.buttons, (1))

    def test_scaleMouseInput_windowed_button(self):
        # Arrange
        disp = DisplayForTestWindowed()
        event_dict = {
            'pos': (400, 800),
            'button': 1,
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        result_event = disp.scaleMouseInput(event)
        # Assert
        self.assertEqual(result_event.pos, (200, 400))
        self.assertEqual(result_event.button, 1)

    def test_scaleMouseInput_windowed_motion(self):
        # Arrange
        disp = DisplayForTestWindowed()
        event_dict = {
            'pos': (400, 800),
            'rel': (100, 200),
            'buttons': (1),
        }
        event = pygame.event.Event(pygame.MOUSEMOTION, event_dict)
        # Act
        result_event = disp.scaleMouseInput(event)
        # Assert
        self.assertEqual(result_event.pos, (200, 400))
        self.assertEqual(result_event.rel, (50, 100))
        self.assertEqual(result_event.buttons, (1))


if __name__ == '__main__':
    unittest.main()

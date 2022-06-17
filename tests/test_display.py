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
    def test_scaleMouseInput(self):
        disp = DisplayForTestFullscreen()
        event_dict = {
            'pos': (400, 800),
            'button': 1,
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        
        result_event = disp.scaleMouseInput(event)
        
        self.assertEqual(result_event.pos, (175, 350))
        self.assertEqual(result_event.button, 1)


if __name__ == '__main__':
    unittest.main()

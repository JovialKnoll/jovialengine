import unittest

import pygame

import jovialengine.display as display


class DisplayForTest(display.Display):
    def __init__(self):
        self._fullscreen_offset = [50, 100]
        self.upscale = 2


class TestDisplay(unittest.TestCase):
    def test_scaleMouseInput(self):
        disp = DisplayForTest()
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

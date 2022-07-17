import unittest

import pygame

import jovialengine.display as display
import jovialengine.game as game


class DisplayForTest(display.Display):
    def __init__(self):
        self.is_fullscreen = False
        self._fullscreen_offset = None
        self.upscale = 3
        self.screen_size = (320, 240)


class GameForTest(game._Game):
    def __init__(self):
        self.game_running = False
        self._is_first_loop = False
        self._joysticks = []
        self.display = DisplayForTest()

    def _handlePauseMenu(self):
        return False


class TestGame(unittest.TestCase):
    gameForTest: game._Game = None

    @classmethod
    def setUpClass(cls):
        cls.gameForTest = GameForTest()

    def test__stillNeedsHandling_QUIT(self):
        # Arrange
        event_dict = {
        }
        event = pygame.event.Event(pygame.QUIT, event_dict)
        # Act
        result = self.gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertFalse(result)

    def test__stillNeedsHandling_WINDOWFOCUSLOST(self):
        # Arrange
        event_dict = {
        }
        event = pygame.event.Event(pygame.WINDOWFOCUSLOST, event_dict)
        # Act
        result = self.gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertFalse(result)

    def test__stillNeedsHandling_WINDOWMINIMIZED(self):
        # Arrange
        event_dict = {
        }
        event = pygame.event.Event(pygame.WINDOWMINIMIZED, event_dict)
        # Act
        result = self.gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertFalse(result)

    def test__stillNeedsHandling_WINDOWMOVED(self):
        # Arrange
        event_dict = {
        }
        event = pygame.event.Event(pygame.WINDOWMOVED, event_dict)
        # Act
        result = self.gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertFalse(result)

    def test__stillNeedsHandling_KEYDOWN_ESCAPE(self):
        # Arrange
        event_dict = {
            'key': pygame.K_ESCAPE,
        }
        event = pygame.event.Event(pygame.KEYDOWN, event_dict)
        # Act
        result = self.gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertFalse(result)

    def test__stillNeedsHandling_KEYDOWN_a(self):
        # Arrange
        event_dict = {
            'key': pygame.K_a,
        }
        event = pygame.event.Event(pygame.KEYDOWN, event_dict)
        # Act
        result = self.gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertTrue(result)

    def test__stillNeedsHandling_MOUSEBUTTONDOWN_IN(self):
        # Arrange
        event_dict = {
            'pos': (1, 1),
            'button': 1
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        result = self.gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertTrue(result)

    def test__stillNeedsHandling_MOUSEBUTTONDOWN_OUT(self):
        # Arrange
        event_dict = {
            'pos': (-1, -1),
            'button': 1
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        result = self.gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

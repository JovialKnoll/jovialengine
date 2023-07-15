import unittest

import pygame

import jovialengine.display as display
import jovialengine.game as game


class GameForTest(game._Game):
    def __init__(self):
        self.running = False
        self._is_first_loop = False
        self._joysticks = []

    def _handlePauseMenu(self):
        return False


class TestGame(unittest.TestCase):
    game_for_test: game._Game = None

    @classmethod
    def setUpClass(cls):
        cls.game_for_test = GameForTest()
        display.is_fullscreen = False
        display._fullscreen_offset = None
        display.upscale = 3
        display.screen_size = (320, 240)

    def test__isPauseEvent_QUIT(self):
        # Arrange
        event_dict = {
        }
        event = pygame.event.Event(pygame.QUIT, event_dict)
        # Act
        result = self.game_for_test._isPauseEvent(event)
        # Assert
        self.assertTrue(result)

    def test__isPauseEvent_WINDOWFOCUSLOST(self):
        # Arrange
        event_dict = {
        }
        event = pygame.event.Event(pygame.WINDOWFOCUSLOST, event_dict)
        # Act
        result = self.game_for_test._isPauseEvent(event)
        # Assert
        self.assertTrue(result)

    def test__isPauseEvent_WINDOWMINIMIZED(self):
        # Arrange
        event_dict = {
        }
        event = pygame.event.Event(pygame.WINDOWMINIMIZED, event_dict)
        # Act
        result = self.game_for_test._isPauseEvent(event)
        # Assert
        self.assertTrue(result)

    def test__isPauseEvent_WINDOWMOVED(self):
        # Arrange
        event_dict = {
        }
        event = pygame.event.Event(pygame.WINDOWMOVED, event_dict)
        # Act
        result = self.game_for_test._isPauseEvent(event)
        # Assert
        self.assertTrue(result)

    def test__filterEvent_KEYDOWN_a(self):
        # Arrange
        event_dict = {
            'key': pygame.K_a,
        }
        event = pygame.event.Event(pygame.KEYDOWN, event_dict)
        # Act
        result = self.game_for_test._filterEvent(event)
        # Assert
        self.assertTrue(result)

    def test__filterEvent_MOUSEBUTTONDOWN_IN(self):
        # Arrange
        event_dict = {
            'pos': (1, 1),
            'button': 1
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        result = self.game_for_test._filterEvent(event)
        # Assert
        self.assertTrue(result)

    def test__filterEvent_MOUSEBUTTONDOWN_OUT(self):
        # Arrange
        event_dict = {
            'pos': (-1, -1),
            'button': 1
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        result = self.game_for_test._filterEvent(event)
        # Assert
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

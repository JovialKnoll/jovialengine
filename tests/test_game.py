import unittest

import pygame

import jovialengine.game as game


class GameForTest(game._Game):
    def __init__(self):
        self.game_running = False
        self._is_first_loop = False
        self._joysticks = []

    def _handlePauseMenu(self):
        return False


class TestGame(unittest.TestCase):
    def test__stillNeedsHandling_QUIT(self):
        # Arrange
        gameForTest = GameForTest()
        event_dict = {
        }
        event = pygame.event.Event(pygame.QUIT, event_dict)
        # Act
        result = gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertFalse(result)

    def test__stillNeedsHandling_WINDOWFOCUSLOST(self):
        # Arrange
        gameForTest = GameForTest()
        event_dict = {
        }
        event = pygame.event.Event(pygame.WINDOWFOCUSLOST, event_dict)
        # Act
        result = gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertFalse(result)

    def test__stillNeedsHandling_WINDOWMINIMIZED(self):
        # Arrange
        gameForTest = GameForTest()
        event_dict = {
        }
        event = pygame.event.Event(pygame.WINDOWMINIMIZED, event_dict)
        # Act
        result = gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertFalse(result)

    def test__stillNeedsHandling_WINDOWMOVED(self):
        # Arrange
        gameForTest = GameForTest()
        event_dict = {
        }
        event = pygame.event.Event(pygame.WINDOWMOVED, event_dict)
        # Act
        result = gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertFalse(result)

    def test__stillNeedsHandling_KEYDOWN_ESCAPE(self):
        # Arrange
        gameForTest = GameForTest()
        event_dict = {
            'key': pygame.K_ESCAPE,
        }
        event = pygame.event.Event(pygame.KEYDOWN, event_dict)
        # Act
        result = gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertFalse(result)

    def test__stillNeedsHandling_KEYDOWN_a(self):
        # Arrange
        gameForTest = GameForTest()
        event_dict = {
            'key': pygame.K_a,
        }
        event = pygame.event.Event(pygame.KEYDOWN, event_dict)
        # Act
        result = gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertTrue(result)

    def test__stillNeedsHandling_MOUSEBUTTONDOWN_IN(self):
        # Arrange
        gameForTest = GameForTest()
        event_dict = {
            'pos': (1, 1),
            'button': 1
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        result = gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertTrue(result)

    def test__stillNeedsHandling_MOUSEBUTTONDOWN_OUT(self):
        # Arrange
        gameForTest = GameForTest()
        event_dict = {
            'pos': (-1, -1),
            'button': 1
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        result = gameForTest._stillNeedsHandling(event)
        # Assert
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()

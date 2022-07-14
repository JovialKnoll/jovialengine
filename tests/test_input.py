import unittest

import pygame

import jovialengine.input as input


class TestInput(unittest.TestCase):
    def test_Action_init(self):
        # Arrange
        event_dict = {
            'pos': (1, 1),
            'button': 1,
        }
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_dict)
        # Act
        action = input.Action(event)
        # Assert
        self.assertEqual(action.pos, event.pos)
        self.assertEqual(action.button, event.button)
        self.assertEqual(action.type, event.type)


if __name__ == '__main__':
    unittest.main()

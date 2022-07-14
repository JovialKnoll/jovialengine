import pygame

from . import config

import constants


class Action(pygame.event.EventType):
    def __init__(self, event: pygame.event.Event):
        self.__dict__.update(event.__dict__)


class Input(object):
    __slots__ = (
    )

    def __init__(self):
        # load in input mapping from config
        # make objects to hold onto current virtual gamepad states
        pass

    def map(self, event: pygame.event.Event):
        # map based on input mapping, update current virtual gamepad states
        return event

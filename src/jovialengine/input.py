import pygame

from . import config

import constants


class Action(object):
    __slots__ = (
        '__dict__',
        'type',
    )

    def __init__(self, event: pygame.event.Event):
        self.__dict__ = event.__dict__
        self.type = event.type


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

import functools

import pygame


@functools.cache
def load(filename, alpha_or_colorkey=False):
    image = pygame.image.load(filename)
    if alpha_or_colorkey is True:
        image = image.convert_alpha()
    else:
        image = image.convert()
        if alpha_or_colorkey is not False:
            image.set_colorkey(alpha_or_colorkey)
    return image

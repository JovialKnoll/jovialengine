import functools

import pygame


@functools.cache
def image(filename, alpha_or_colorkey=False):
    """Loads an image, converts, and sets colorkey as needed.
    The results are cached so don't alter them."""
    result = pygame.image.load(filename)
    if alpha_or_colorkey is True:
        result = result.convert_alpha()
    else:
        result = result.convert()
        if alpha_or_colorkey is not False:
            result.set_colorkey(alpha_or_colorkey)
    return result


@functools.cache
def mask(filename, alpha_or_colorkey=False):
    """Loads an image and uses this to construct a mask.
    The results are cached so don't alter them."""
    pass


@functools.cache
def sound(filename):
    """Loads a sound.
    The results are cached so don't alter them."""
    return pygame.mixer.Sound(filename)

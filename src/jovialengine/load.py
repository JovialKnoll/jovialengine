import functools

import pygame


@functools.cache
def image(filename, alpha_or_colorkey=False):
    """Loads images, converts, and sets colorkey as needed.
    The results are cached, so don't blit to them."""
    result = pygame.image.load(filename)
    if alpha_or_colorkey is True:
        result = result.convert_alpha()
    else:
        result = result.convert()
        if alpha_or_colorkey is not False:
            result.set_colorkey(alpha_or_colorkey)
    return result


@functools.cache
def sound(filename):
    """Loads sounds.
    The results are cached, so don't set volume on them."""
    return pygame.mixer.Sound(filename)

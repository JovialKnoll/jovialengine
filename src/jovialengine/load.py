from functools import cache

import pygame


@cache
def image(filename: str, alpha_or_colorkey: bool | pygame.typing.ColorLike=False):
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


@cache
def subsurface(surface: pygame.Surface, rect: tuple[int, int, int, int]):
    """Gets a subsurface from a surface.
    The results are cached so don't alter them."""
    return surface.subsurface(rect)


@cache
def flip(surface: pygame.Surface, flip_x: bool, flip_y: bool):
    """Gets a flipped surface from a surface.
    The results are cached so don't alter them."""
    return pygame.transform.flip(surface, flip_x, flip_y)


@cache
def mask_surface(surface: pygame.Surface, rect: tuple[int, int, int, int] | None=None):
    """Constructs a mask from a surface.
    The results are cached so don't alter them."""
    if rect:
        surface = subsurface(surface, rect)
    return pygame.mask.from_surface(surface)


@cache
def mask_filled(size: tuple[int, int]):
    """Constructs a filled mask.
    The results are cached so don't alter them."""
    return pygame.mask.Mask(size, True)


@cache
def mask_circle(size: tuple[int, int], radius: float):
    """Constructs a mask with a filled circle centered in the size at the given radius.
    The results are cached so don't alter them."""
    surface = pygame.Surface(size)
    surface.fill((0, 0, 0))
    pygame.draw.circle(surface, (255, 0, 0), (size[0] / 2, size[1] / 2), radius)
    surface.set_colorkey((0, 0, 0))
    return pygame.mask.from_surface(surface)


@cache
def sound(filename: str):
    """Loads a sound.
    The results are cached so don't alter them."""
    return pygame.mixer.Sound(filename)

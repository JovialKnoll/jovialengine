import pygame

from . import utility


class OffsetGroup(pygame.sprite.LayeredUpdates):
    """A sprite group for drawing sprites, in layers, offset by some amount.
    For best results, sprite.rect should be an FRect."""
    def draw(self, surface: pygame.Surface, offset: pygame.typing.Point=(0,0)):
        sprite_sequence = [
            (sprite.image, utility.round_point(sprite.rect.move(offset)))
            for sprite
            in self.sprites()
        ]
        surface.fblits(sprite_sequence)
        self.lostsprites = []
        return self.lostsprites

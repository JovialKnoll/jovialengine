import pygame


class OffsetGroup(pygame.sprite.LayeredUpdates):
    """A sprite group for drawing sprites, in layers, offset by some amount."""
    def draw(self, surface: pygame.Surface, offset: pygame.typing.IntPoint=(0,0)):
        sprite_sequence = [
            (
                sprite.image,
                (
                    round(sprite.rect.x) + offset[0],
                    round(sprite.rect.y) + offset[1],
                )
            )
            for sprite
            in self.sprites()
        ]
        surface.fblits(sprite_sequence)
        self.lostsprites = []
        return self.lostsprites

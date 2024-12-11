import pygame


class OffsetGroup(pygame.sprite.LayeredUpdates):
    def draw(self, surface: pygame.Surface, offset: tuple[int, int] | None=None):
        # using a list comprehension for now instead of a generator, haven't tested difference
        if offset:
            sprite_sequence = [(sprite.image, sprite.rect.move(offset)) for sprite in self.sprites()]
        else:
            sprite_sequence = [(sprite.image, sprite.rect) for sprite in self.sprites()]
        surface.fblits(sprite_sequence)
        self.lostsprites = []
        dirty = self.lostsprites
        return dirty

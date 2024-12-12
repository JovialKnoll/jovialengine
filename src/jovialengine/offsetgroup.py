import pygame


class OffsetGroup(pygame.sprite.LayeredUpdates):
    def draw(self, surface):
        # using a list comprehension for now instead of a generator, haven't tested difference
        sprite_sequence = [(sprite.image, sprite.rect) for sprite in self.sprites()]
        surface.fblits(sprite_sequence)
        self.lostsprites = []
        dirty = self.lostsprites
        return dirty

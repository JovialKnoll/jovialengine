import pygame


class OffsetGroup(pygame.sprite.LayeredUpdates):
    def draw(self, surface):
        sprite_sequence = [(sprite.image, sprite.rect) for sprite in self.sprites()]
        surface.fblits(sprite_sequence)
        self.lostsprites = []
        return self.lostsprites

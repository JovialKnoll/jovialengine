import pygame


class OffsetGroup(pygame.sprite.LayeredUpdates):
    def draw(self, surface: pygame.Surface, offset: pygame.typing.Point=(0,0)):
        sprite_sequence = [(sprite.image, sprite.rect.move(offset)) for sprite in self.sprites()]
        surface.fblits(sprite_sequence)
        self.lostsprites = []
        return self.lostsprites

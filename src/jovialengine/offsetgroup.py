import pygame


class OffsetGroup(pygame.sprite.LayeredUpdates):
    def draw(self, surface: pygame.Surface, offset: tuple[int, int] | None=None):
        if offset:
            sprite_sequence = [(sprite.image, sprite.rect.move(offset)) for sprite in self.sprites()]
        else:
            sprite_sequence = [(sprite.image, sprite.rect) for sprite in self.sprites()]
        surface.fblits(sprite_sequence)
        self.lostsprites = []
        return self.lostsprites

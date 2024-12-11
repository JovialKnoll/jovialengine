import pygame


class CameraGroup(pygame.sprite.LayeredUpdates):
    def draw(self, surface: pygame.Surface, camera: pygame.typing.RectLike | None=None):
        # using a list comprehension for now instead of a generator, haven't tested difference
        if camera:
            #todo: check sprite.rect.move vs constructing tuple from xs and ys
            sprite_sequence = [(sprite.image, sprite.rect) for sprite in self.sprites()]
        else:
            sprite_sequence = [(sprite.image, sprite.rect) for sprite in self.sprites()]
        surface.fblits(sprite_sequence)
        self.lostsprites = []
        dirty = self.lostsprites
        return dirty

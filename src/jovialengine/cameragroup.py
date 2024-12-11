import pygame


class CameraGroup(pygame.sprite.LayeredUpdates):
    def draw(self, surface: pygame.Surface, camera: pygame.Rect | None=None):
        # using a list comprehension for now instead of a generator, haven't tested difference
        if camera:
            sprite_sequence = [(sprite.image, sprite.rect.move(-camera.x, -camera.y)) for sprite in self.sprites()]
        else:
            sprite_sequence = [(sprite.image, sprite.rect) for sprite in self.sprites()]
        surface.fblits(sprite_sequence)
        self.lostsprites = []
        dirty = self.lostsprites
        return dirty

import pygame


class CameraGroup(pygame.sprite.LayeredUpdates):
    def draw(self, surface):
        sprites = self.sprites()
        # using a generator for now, later can check if a list comprehension is faster
        surface.fblits((sprite.image, sprite.rect) for sprite in sprites)
        self.lostsprites = []
        dirty = self.lostsprites
        return dirty

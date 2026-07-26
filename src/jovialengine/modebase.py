import abc
from typing import final, TYPE_CHECKING
from collections.abc import Iterable

import pygame

from . import load
from . import display
from .offsetgroup import OffsetGroup
from .inputframe import InputFrame
if TYPE_CHECKING:
    from .gamesprite import GameSprite


class ModeBase(abc.ABC):
    """Base class for all game modes.
    Subclasses should set:
    optional: _SPACE_SIZE, size of the space inside this mode, if not supplied will assume display.screen_size
    optional: _CAMERA_SIZE, size of the camera inside this mode, if not supplied will assume display.screen_size
    optional: _CAMERA_OFFSET, offset for drawing camera view onto screen
    optional: _STATIC_COLLISION_MASK_INFOS, iterable of setup information for collision masks for colliding with static
        background elements
        (LABEL, COLLISION_MASK, _COLLISION_MASK_ALPHA_OR_COLORKEY)

    When a subclass wants to pass on to another mode, set self.next_mode.
    Don't create another mode unless you are immediately assigning it to self.next_mode.
    """
    _SPACE_SIZE: tuple[int, int] | None = None
    _CAMERA_SIZE: tuple[int, int] | None = None
    _CAMERA_OFFSET: tuple[int, int] = (0, 0)
    _STATIC_COLLISION_MASK_INFOS: Iterable[tuple[str, str, bool | tuple[int, int, int]]]

    __slots__ = (
        '_background',
        'sprites_all',
        'sprites_game',
        'sprites_input',
        'map_sprites_static_collide',
        '_camera',
        '_input_frame',
        'next_mode',
    )

    def __init__(self):
        self._background = pygame.Surface(self.get_space_size()).convert()
        self._background.fill((0, 0, 0))
        self.sprites_all = OffsetGroup()
        self.sprites_game: pygame.sprite.Group[GameSprite] = pygame.sprite.Group()
        self.sprites_input: pygame.sprite.Group[GameSprite] = pygame.sprite.Group()
        self.map_sprites_static_collide: dict[str, pygame.sprite.Group[GameSprite]] = dict()
        self._static_collision_masks: Iterable[tuple[str, pygame.mask.Mask]] = []
        for static_collision_mask_info in _STATIC_COLLISION_MASK_INFOS:
            mask_image = load.image(static_collision_mask_info[1], static_collision_mask_info[2])
            mask = load.mask_surface(self._mask_image)
            self._static_collision_masks.append((static_collision_mask_info[0], mask))
        self._camera = pygame.FRect((0, 0), self._CAMERA_SIZE or display.screen_size)
        self._input_frame: InputFrame | None = None
        self.next_mode: ModeBase | None = None

    @final
    def add_sprite_static_collide(self, sprite: GameSprite):
        for sprite_collides_with in sprite.get_static_collides_with():
            if sprite_collides_with not in self.map_sprites_static_collide:
                self.map_sprites_static_collide[sprite_collides_with] = pygame.sprite.Group()
            self.map_sprites_static_collide[sprite_collides_with].add(sprite)

    @final
    def input(self, events: Iterable[pygame.event.Event], input_frame: InputFrame):
        """All game modes can take in input."""
        for event in events:
            self._take_event(event)
        self._take_frame(input_frame)
        for sprite in self.sprites_input.sprites():
            sprite.input(input_frame)
        self._input_frame = input_frame

    @final
    def update(self, dt: int):
        """All game modes can update."""
        self._update_pre_sprites(dt)
        for sprite in self.sprites_all.sprites():
            sprite.update(dt, self._camera)
        self._update_post_sprites(dt)
        self.__handle_static_collisions()
        self.__handle_collisions()

    @final
    def __handle_static_collisions(self):
        collide_sprites = self.sprites_game.sprites()
        for sprite in collide_sprites:
            for sprite_collides_with in sprite.get_static_collides_with():
                #check if sprite_collides_with is in set of possible background elements for this mode
                #then if so check whether sprite collides with that one
                #then if so call getattr(sprite, 'static_collide_' + sprite_collides_with)()
                pass

    @final
    def __handle_collisions(self):
        collide_events = []
        collide_sprites = self.sprites_game.sprites()
        for i, sprite0 in enumerate(collide_sprites):
            for j in range(i + 1, len(collide_sprites)):
                sprite1 = collide_sprites[j]
                sprite0_collides = sprite0.get_collides_with() & sprite1.get_collision_labels()
                sprite1_collides = sprite1.get_collides_with() & sprite0.get_collision_labels()
                if (sprite0_collides or sprite1_collides) and sprite0.does_collide(sprite1):
                    for sprite0_collide in sprite0_collides:
                        collide_events.append((getattr(sprite0, 'collide_' + sprite0_collide), sprite1,))
                    for sprite1_collide in sprite1_collides:
                        collide_events.append((getattr(sprite1, 'collide_' + sprite1_collide), sprite0,))
        for collide_event in collide_events:
            collide_event[0](collide_event[1])

    @final
    def draw(self, screen: pygame.Surface):
        """All game modes can draw to the screen"""
        self._update_pre_draw()
        screen.set_clip((self._CAMERA_OFFSET, self._CAMERA_SIZE or display.screen_size))
        offset = (
            self._CAMERA_OFFSET[0] - round(self._camera.x),
            self._CAMERA_OFFSET[1] - round(self._camera.y),
        )
        screen.blit(self._background, offset)
        self._draw_pre_sprites(screen, offset)
        self.sprites_all.draw_offset(screen, offset)
        for sprite in self.sprites_game.sprites():
            sprite.draw_dynamic(screen, offset)
        self._draw_post_sprites(screen, offset)
        screen.set_clip(None)
        self._draw_post_camera(screen)

    @final
    def cleanup(self):
        for sprites in (self.sprites_all, self.sprites_game, self.sprites_input):
            # we can't just kill the sprites since we might be reusing them between modes
            sprites.empty()
        self._cleanup()

    def _take_event(self, event: pygame.event.Event):
        """Handle any input that requires looking at pygame events directly, like typing."""
        pass

    def _take_frame(self, input_frame: InputFrame):
        """Handle all other input.
        During this method call self._input_frame still holds the old input_frame."""
        pass

    def _update_pre_sprites(self, dt: int):
        """Handle mode updates before sprites."""
        pass

    def _update_post_sprites(self, dt: int):
        """Handle mode updates after sprites (before collision handling)."""
        pass

    def _update_pre_draw(self):
        """Handle updates that only need to happen right before drawing, like updating the camera position."""
        pass

    def _draw_pre_sprites(self, screen: pygame.Surface, offset: pygame.typing.IntPoint):
        """Handle dynamic drawing after the background and before sprites."""
        pass

    def _draw_post_sprites(self, screen: pygame.Surface, offset: pygame.typing.IntPoint):
        """Handle dynamic drawing after the sprites."""
        pass

    def _draw_post_camera(self, screen: pygame.Surface):
        """Handle drawing onto screen after camera-aware drawing is done."""
        pass

    def _cleanup(self):
        """Handle any additional cleanup this mode will need when it's ended."""
        pass

    @staticmethod
    def _stop_mixer():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.stop()

    def get_space_size(self):
        return self._SPACE_SIZE or display.screen_size

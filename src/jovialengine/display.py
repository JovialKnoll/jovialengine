import typing
import sys
import os
import math
from datetime import datetime

import pygame

from . import config
from .modebase import ModeBase
from . import utility


class Display(object):
    __slots__ = (
        '_screenshot_directory',
        'screen_size',
        '_title',
        '_window_icon',
        '_monitor_res',
        '_upscale_max',
        '_windowed_flags',
        '_fullscreen_flags',
        'is_fullscreen',
        'upscale',
        '_disp_res',
        'screen',
        '_fullscreen_offset',
        '_full_screen',
        '_disp_screen',
    )

    def __init__(self,
                 screenshot_directory: str,
                 screen_size: typing.Tuple[int, int],
                 title: str,
                 window_icon: str | None):
        self._screenshot_directory = screenshot_directory
        self.screen_size = screen_size
        self._title = title
        self._window_icon = None
        if window_icon:
            self._window_icon = pygame.image.load(window_icon)
        self._setupDisplay()
        self.is_fullscreen = config.get(config.FULLSCREEN)
        self.upscale = config.get(config.SCREEN_SCALE)
        if self.upscale == 0:
            self.upscale = math.ceil(self._upscale_max / 2)
        self.upscale = max(min(self.upscale, self._upscale_max), 0)
        self._scaleDisp()
        self.screen: pygame.Surface = pygame.Surface(self.screen_size)
        self._fullscreen_offset = None
        self._full_screen = None
        if self.is_fullscreen:
            self._setFullscreen()
        else:
            self._setWindowed()
        self.screen = self.screen.convert()
        config.update(config.SCREEN_SCALE, self.upscale)

    def _setupDisplay(self):
        pygame.display.set_caption(self._title)
        if self._window_icon:
            pygame.display.set_icon(self._window_icon)
        display_info = pygame.display.Info()
        self._monitor_res = (
            display_info.current_w,
            display_info.current_h,
        )
        self._upscale_max = min(
            self._monitor_res[0] // self.screen_size[0],
            self._monitor_res[1] // self.screen_size[1]
        )
        max_disp_res = (
            self.screen_size[0] * self._upscale_max,
            self.screen_size[1] * self._upscale_max,
        )
        self._windowed_flags = 0
        if pygame.display.mode_ok(max_disp_res, pygame.DOUBLEBUF):
            self._windowed_flags = pygame.DOUBLEBUF
        self._fullscreen_flags = 0
        if sys.platform != "win32":
            self._fullscreen_flags = pygame.NOFRAME
        elif pygame.display.mode_ok(self._monitor_res, pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE):
            self._fullscreen_flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
        elif pygame.display.mode_ok(self._monitor_res, pygame.FULLSCREEN | pygame.DOUBLEBUF):
            self._fullscreen_flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
        elif pygame.display.mode_ok(self._monitor_res, pygame.FULLSCREEN):
            self._fullscreen_flags = pygame.FULLSCREEN

    def changeScale(self, scale_change: int):
        new_scale = self.upscale + scale_change
        if new_scale < 1 or new_scale > self._upscale_max:
            return
        self._alterScale(new_scale)

    def setScale(self, target_scale: int):
        new_scale = min(target_scale, self._upscale_max)
        if new_scale == self.upscale:
            return
        self._alterScale(new_scale)

    def _alterScale(self, new_scale: int):
        self.upscale = new_scale
        self._scaleDisp()
        if self.is_fullscreen:
            self._setFullscreen()
        else:
            pygame.display.quit()
            pygame.display.init()
            self._setupDisplay()
            self._setWindowed()
        self.screen = self.screen.convert()
        config.update(config.SCREEN_SCALE, self.upscale)

    def _scaleDisp(self):
        self._disp_res = (
            self.screen_size[0] * self.upscale,
            self.screen_size[1] * self.upscale,
        )

    def toggleFullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        pygame.display.quit()
        pygame.display.init()
        self._setupDisplay()
        if self.is_fullscreen:
            self._setFullscreen()
        else:
            self._setWindowed()
        self.screen = self.screen.convert()
        config.update(config.FULLSCREEN, self.is_fullscreen)

    def _setWindowed(self):
        # center window
        os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(
            (self._monitor_res[0] - self._disp_res[0]) // 2,
            (self._monitor_res[1] - self._disp_res[1]) // 2
        )
        self._fullscreen_offset = None
        self._full_screen = None
        self._disp_screen = pygame.display.set_mode(
            self._disp_res,
            self._windowed_flags
        )

    def _setFullscreen(self):
        self._fullscreen_offset = (
            (self._monitor_res[0] - self._disp_res[0]) // 2,
            (self._monitor_res[1] - self._disp_res[1]) // 2,
        )
        if self._full_screen is None:
            os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(0, 0)
            self._full_screen = pygame.display.set_mode(
                self._monitor_res,
                self._fullscreen_flags
            )
        else:
            self._full_screen.fill((0, 0, 0))
        self._disp_screen = pygame.Surface(self._disp_res).convert()

    def scaleDraw(self):
        """Scale screen onto display surface, then flip the display."""
        pygame.transform.scale(self.screen, self._disp_res, self._disp_screen)
        if self.is_fullscreen:
            self._full_screen.blit(self._disp_screen, self._fullscreen_offset)
        pygame.display.flip()

    def scaleMouseInput(self, event: pygame.event.Event):
        """Scale mouse position for events in terms of the screen (as opposed to the display surface)."""
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
            if self.is_fullscreen:
                event_dict = {
                    'pos': (
                        (event.pos[0] - self._fullscreen_offset[0]) // self.upscale,
                        (event.pos[1] - self._fullscreen_offset[1]) // self.upscale,
                    )
                }
            else:
                event_dict = {
                    'pos': (
                        event.pos[0] // self.upscale,
                        event.pos[1] // self.upscale,
                    )
                }
            if event.type == pygame.MOUSEMOTION:
                event_dict['rel'] = (
                    event.rel[0] // self.upscale,
                    event.rel[1] // self.upscale,
                )
                event_dict['buttons'] = event.buttons
            else:
                event_dict['button'] = event.button
            return pygame.event.Event(event.type, event_dict)
        return event

    def isInScreen(self, pos: typing.Tuple[int, int]):
        return (
            0 <= pos[0] < self.screen_size[0]
            and 0 <= pos[1] < self.screen_size[1]
        )

    def getBlurredScreen(self, mode: ModeBase):
        screen = pygame.Surface(self.screen_size).convert()
        mode.draw(screen)
        screen = pygame.transform.smoothscale(
            screen,
            (self.screen_size[0] * 4 // 5, self.screen_size[1] * 4 // 5)
        )
        screen = pygame.transform.smoothscale(
            screen,
            self.screen_size
        )
        return screen

    def getPositionalChannelMix(self, x: int | float):
        pos = min(max(x / self.screen_size[0], 0), 1)
        channel_l = self._boundChannelVolume(utility.cosCurve(pos))
        channel_r = self._boundChannelVolume(utility.sinCurve(pos))
        return channel_l, channel_r

    @staticmethod
    def _boundChannelVolume(volume: float):
        return .2 + (volume * .8)

    def takeScreenshot(self):
        try:
            os.mkdir(self._screenshot_directory)
        except FileExistsError:
            pass
        file_name = f"{datetime.utcnow().isoformat().replace(':', '')}.png"
        file_path = os.path.join(self._screenshot_directory, file_name)
        pygame.image.save(self.screen, file_path)
